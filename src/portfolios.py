"""Station 3 portfolio construction and walk-forward backtests.

The functions in this module form long-only, fully-invested systematic funds and
measure their out-of-sample performance. Each rebalance estimates weights using
only returns observed before the live month, then earns the next month's returns
at those weights.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
import pandas as pd
from scipy.optimize import minimize


METHOD_LABELS = {
    "equal_weight": "Equal Weight",
    "min_variance": "Minimum Variance",
    "max_sharpe": "Maximum Sharpe",
    "risk_parity": "Risk Parity",
}


@dataclass(frozen=True)
class BacktestConfig:
    """Configuration for a walk-forward fund backtest."""

    universe: str
    method: str
    periods_per_year: int = 252
    initial_window: int = 252
    risk_free_rate: float = 0.0


def method_label(method: str) -> str:
    """Return a readable method name."""
    return METHOD_LABELS.get(method, method.replace("_", " ").title())


def fund_name(universe: str, method: str) -> str:
    """Return the investable fund name shown in tables and the app."""
    return f"{universe} - {method_label(method)}"


def prepare_wide_returns(returns: pd.DataFrame, value_col: str = "daily_return") -> pd.DataFrame:
    """Convert long returns into a clean date x ticker matrix.

    Rows with any missing asset return are removed. This is deliberate for the
    combined universe: it removes dates where only crypto traded before equity
    returns are available, so a single weight vector is applied to all assets.
    """
    if {"date", "ticker", value_col}.issubset(returns.columns):
        frame = returns.copy()
        frame["date"] = pd.to_datetime(frame["date"])
        wide = frame.pivot_table(index="date", columns="ticker", values=value_col, aggfunc="mean")
    else:
        wide = returns.copy()
        wide.index = pd.to_datetime(wide.index)

    wide = wide.sort_index().apply(pd.to_numeric, errors="coerce")
    wide = wide.replace([np.inf, -np.inf], np.nan)
    wide = wide.dropna(axis=1, how="all").dropna(axis=0, how="any")
    if wide.empty:
        raise ValueError("returns matrix is empty after cleaning")
    return wide


def performance_metrics(daily_returns: pd.Series, periods_per_year: int = 252) -> dict:
    """Compute standard fund fact-sheet metrics from OOS daily returns."""
    r = pd.Series(daily_returns, dtype="float64").replace([np.inf, -np.inf], np.nan).dropna()
    if r.empty:
        raise ValueError("daily_returns is empty")

    growth = (1.0 + r).cumprod()
    running_max = growth.cummax()
    drawdown = growth / running_max - 1.0

    final_growth = float(growth.iloc[-1])
    if final_growth > 0:
        annualised_return = final_growth ** (periods_per_year / len(r)) - 1.0
    else:
        annualised_return = r.mean() * periods_per_year

    annualised_volatility = float(r.std(ddof=1) * math.sqrt(periods_per_year))
    sharpe = annualised_return / annualised_volatility if annualised_volatility > 0 else np.nan

    return {
        "observations": int(len(r)),
        "annualisation_factor": int(periods_per_year),
        "annualised_return": float(annualised_return),
        "annualised_volatility": float(annualised_volatility),
        "sharpe_ratio": float(sharpe) if pd.notna(sharpe) else np.nan,
        "max_drawdown": float(drawdown.min()),
        "final_growth_of_1": final_growth,
        "mean_daily_return": float(r.mean()),
        "daily_volatility": float(r.std(ddof=1)),
    }


def _normalise_weights(weights: np.ndarray) -> np.ndarray:
    """Clip tiny numerical noise and renormalise a weight vector."""
    w = np.asarray(weights, dtype="float64")
    w = np.nan_to_num(w, nan=0.0, posinf=0.0, neginf=0.0)
    w = np.clip(w, 0.0, None)
    total = w.sum()
    if total <= 0:
        return np.repeat(1.0 / len(w), len(w))
    return w / total


def _regularised_inputs(train: pd.DataFrame, periods_per_year: int) -> tuple[np.ndarray, np.ndarray]:
    """Return annualised mean and regularised covariance inputs."""
    clean = train.replace([np.inf, -np.inf], np.nan).dropna(axis=0, how="any")
    mu = clean.mean().to_numpy(dtype="float64") * periods_per_year
    cov = clean.cov().to_numpy(dtype="float64") * periods_per_year
    cov = np.nan_to_num(cov, nan=0.0, posinf=0.0, neginf=0.0)

    diag = np.diag(cov)
    avg_var = float(np.nanmean(diag)) if len(diag) else 0.0
    ridge = max(avg_var * 1e-6, 1e-8)
    cov = cov + np.eye(cov.shape[0]) * ridge
    return mu, cov


def _inverse_vol_weights(cov: np.ndarray) -> np.ndarray:
    vol = np.sqrt(np.clip(np.diag(cov), 1e-12, None))
    inv = 1.0 / vol
    return _normalise_weights(inv)


def optimise_weights(
    train: pd.DataFrame,
    method: str,
    periods_per_year: int = 252,
    risk_free_rate: float = 0.0,
) -> tuple[pd.Series, str]:
    """Estimate long-only fully-invested weights from the training window."""
    if train.shape[1] < 2:
        raise ValueError("at least two assets are required for portfolio optimisation")

    method = method.lower()
    tickers = train.columns
    n_assets = len(tickers)

    if method == "equal_weight":
        return pd.Series(np.repeat(1.0 / n_assets, n_assets), index=tickers), "equal_weight"

    mu, cov = _regularised_inputs(train, periods_per_year)
    bounds = [(0.0, 1.0)] * n_assets
    constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1.0}
    x0 = _inverse_vol_weights(cov)

    if method == "min_variance":
        objective = lambda w: float(w @ cov @ w)
        fallback = x0
    elif method == "max_sharpe":
        excess = mu - risk_free_rate

        def objective(w: np.ndarray) -> float:
            variance = float(w @ cov @ w)
            if variance <= 0:
                return 1e6
            return -float(w @ excess) / math.sqrt(variance)

        fallback = np.repeat(1.0 / n_assets, n_assets)
    elif method == "risk_parity":
        target = np.repeat(1.0 / n_assets, n_assets)

        def objective(w: np.ndarray) -> float:
            cov_w = cov @ w
            total_risk = float(w @ cov_w)
            if total_risk <= 0:
                return 1e6
            risk_contrib = w * cov_w / total_risk
            return float(((risk_contrib - target) ** 2).sum())

        fallback = x0
    else:
        raise ValueError(f"unknown portfolio method: {method}")

    result = minimize(
        objective,
        x0=x0,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 300, "ftol": 1e-10, "disp": False},
    )

    if result.success and np.isfinite(result.x).all():
        weights = _normalise_weights(result.x)
        status = "ok"
    else:
        weights = _normalise_weights(fallback)
        status = f"fallback: {result.message}"

    return pd.Series(weights, index=tickers), status


def _monthly_live_periods(index: pd.DatetimeIndex, first_live_pos: int) -> list[pd.Period]:
    live_index = index[first_live_pos:]
    return list(pd.Series(live_index.to_period("M")).drop_duplicates())


def oos_backtest(
    returns: pd.DataFrame,
    method: str = "min_variance",
    universe: str = "Combined",
    periods_per_year: int = 252,
    initial_window: int = 252,
    risk_free_rate: float = 0.0,
) -> dict[str, pd.DataFrame | dict]:
    """Run a monthly expanding-window out-of-sample backtest.

    For each live month, weights are estimated from returns strictly before the
    first live date of that month. Those weights are then held through that month.
    """
    wide = prepare_wide_returns(returns)
    if len(wide) <= initial_window:
        raise ValueError(
            f"not enough observations for initial_window={initial_window}; got {len(wide)}"
        )

    config = BacktestConfig(
        universe=universe,
        method=method.lower(),
        periods_per_year=periods_per_year,
        initial_window=initial_window,
        risk_free_rate=risk_free_rate,
    )
    name = fund_name(config.universe, config.method)

    return_parts = []
    weight_rows = []
    previous_weights: pd.Series | None = None
    first_live_date = wide.index[initial_window]

    for live_month in _monthly_live_periods(wide.index, initial_window):
        month_dates = wide.index[wide.index.to_period("M") == live_month]
        live_dates = month_dates[month_dates >= first_live_date]
        if len(live_dates) == 0:
            continue

        live_start = live_dates[0]
        live_end = live_dates[-1]
        train = wide.loc[wide.index < live_start]
        if len(train) < initial_window:
            continue

        weights, status = optimise_weights(
            train,
            method=config.method,
            periods_per_year=config.periods_per_year,
            risk_free_rate=config.risk_free_rate,
        )
        live_returns = wide.loc[live_dates].dot(weights)

        if previous_weights is None:
            turnover = np.nan
        else:
            aligned_prev = previous_weights.reindex(weights.index).fillna(0.0)
            turnover = float(0.5 * np.abs(weights - aligned_prev).sum())
        previous_weights = weights

        return_parts.append(
            pd.DataFrame(
                {
                    "date": live_returns.index,
                    "fund_id": name,
                    "universe": config.universe,
                    "method": config.method,
                    "method_label": method_label(config.method),
                    "daily_return": live_returns.to_numpy(dtype="float64"),
                    "rebalance_date": train.index[-1],
                    "live_start_date": live_start,
                    "live_end_date": live_end,
                    "training_observations": int(len(train)),
                    "periods_per_year": int(config.periods_per_year),
                }
            )
        )

        for ticker, weight in weights.items():
            weight_rows.append(
                {
                    "rebalance_date": train.index[-1],
                    "live_start_date": live_start,
                    "live_end_date": live_end,
                    "fund_id": name,
                    "universe": config.universe,
                    "method": config.method,
                    "method_label": method_label(config.method),
                    "ticker": ticker,
                    "weight": float(weight),
                    "training_observations": int(len(train)),
                    "turnover": turnover,
                    "optimizer_status": status,
                }
            )

    if not return_parts:
        raise ValueError(f"no live returns produced for {name}")

    fund_returns = pd.concat(return_parts, ignore_index=True).sort_values("date")
    fund_returns["growth_of_1"] = (1.0 + fund_returns["daily_return"]).cumprod()
    fund_returns["drawdown"] = fund_returns["growth_of_1"] / fund_returns["growth_of_1"].cummax() - 1.0

    weights_df = pd.DataFrame(weight_rows).sort_values(["live_start_date", "ticker"])
    metrics = performance_metrics(fund_returns["daily_return"], periods_per_year=config.periods_per_year)
    metrics.update(
        {
            "fund_id": name,
            "universe": config.universe,
            "method": config.method,
            "method_label": method_label(config.method),
            "first_live_date": fund_returns["date"].min(),
            "last_live_date": fund_returns["date"].max(),
            "initial_window": int(config.initial_window),
            "rebalance_frequency": "monthly",
            "risk_free_rate": float(config.risk_free_rate),
            "average_turnover": float(weights_df["turnover"].dropna().mean())
            if "turnover" in weights_df
            else np.nan,
        }
    )

    return {"returns": fund_returns, "weights": weights_df, "metrics": metrics}
