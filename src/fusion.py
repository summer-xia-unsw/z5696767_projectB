"""Station 3 extension: fuse sector sentiment into equity fund weights.

The fusion rule is intentionally simple and auditable. It starts from a base
equity fund's monthly weights and nudges sector weights using lagged sector
sentiment z-scores. The signal is fixed ex ante, clipped, long-only, and
renormalised, so the comparison is a disciplined extension rather than a tuned
in-sample search.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src import portfolios


def _wide_returns(returns: pd.DataFrame) -> pd.DataFrame:
    wide = returns.copy()
    wide["date"] = pd.to_datetime(wide["date"])
    return wide.pivot_table(index="date", columns="ticker", values="daily_return", aggfunc="mean").sort_index()


def apply_sentiment(
    weights: pd.DataFrame,
    sentiment: pd.DataFrame,
    equity_returns: pd.DataFrame,
    base_fund_id: str = "Equity - Minimum Variance",
    output_fund_id: str = "Equity - Minimum Variance Sentiment Tilt",
    tilt_strength: float = 0.15,
    z_col: str = "lagged_sector_z",
    z_clip: float = 2.0,
    periods_per_year: int = 252,
) -> dict[str, pd.DataFrame]:
    """Apply a lagged sector-sentiment tilt to one equity fund.

    Parameters
    ----------
    weights:
        Monthly fund weights from `results/data/fund_weights.csv`.
    sentiment:
        Sector sentiment index with a lagged z-score column. The lag makes the
        signal available before the live date decision.
    equity_returns:
        Long equity returns used to earn out-of-sample returns.
    base_fund_id:
        Existing equity fund to tilt.
    tilt_strength:
        Fixed multiplier. A positive value is momentum: more weight to sectors
        with better-than-usual lagged news.
    """
    required_weights = {"fund_id", "live_start_date", "live_end_date", "rebalance_date", "ticker", "sector", "weight"}
    missing_weights = required_weights.difference(weights.columns)
    if missing_weights:
        raise ValueError(f"weights is missing required columns: {sorted(missing_weights)}")

    required_sentiment = {"date", "sector", z_col, "lagged_signal_date"}
    missing_sentiment = required_sentiment.difference(sentiment.columns)
    if missing_sentiment:
        raise ValueError(f"sentiment is missing required columns: {sorted(missing_sentiment)}")

    base = weights[weights["fund_id"] == base_fund_id].copy()
    if base.empty:
        raise ValueError(f"base_fund_id not found in weights: {base_fund_id}")

    base["live_start_date"] = pd.to_datetime(base["live_start_date"])
    base["live_end_date"] = pd.to_datetime(base["live_end_date"])
    base["rebalance_date"] = pd.to_datetime(base["rebalance_date"])

    sig = sentiment[["date", "sector", z_col, "lagged_signal_date"]].copy()
    sig["date"] = pd.to_datetime(sig["date"])
    sig["lagged_signal_date"] = pd.to_datetime(sig["lagged_signal_date"])
    sig = sig.rename(columns={"date": "live_start_date", z_col: "sentiment_z"})

    tilted = base.merge(sig, on=["live_start_date", "sector"], how="left")
    tilted["sentiment_z"] = tilted["sentiment_z"].fillna(0.0).clip(-z_clip, z_clip)
    tilted["tilt_multiplier"] = (1.0 + tilt_strength * tilted["sentiment_z"]).clip(lower=0.0)
    tilted["raw_tilted_weight"] = tilted["weight"] * tilted["tilt_multiplier"]

    group_cols = ["live_start_date", "fund_id"]
    totals = tilted.groupby(group_cols)["raw_tilted_weight"].transform("sum")
    tilted["tilted_weight"] = np.where(totals > 0, tilted["raw_tilted_weight"] / totals, tilted["weight"])

    tilted_weights = tilted.copy()
    tilted_weights["base_fund_id"] = base_fund_id
    tilted_weights["fund_id"] = output_fund_id
    tilted_weights["method"] = "sentiment_tilt"
    tilted_weights["method_label"] = "Sentiment Tilt"
    tilted_weights["base_weight"] = tilted_weights["weight"]
    tilted_weights["weight"] = tilted_weights["tilted_weight"]
    tilted_weights["tilt_strength"] = tilt_strength

    keep_cols = [
        "rebalance_date",
        "live_start_date",
        "live_end_date",
        "base_fund_id",
        "fund_id",
        "universe",
        "method",
        "method_label",
        "ticker",
        "sector",
        "asset_class",
        "base_weight",
        "weight",
        "sentiment_z",
        "tilt_multiplier",
        "tilt_strength",
        "lagged_signal_date",
    ]
    tilted_weights = tilted_weights[keep_cols].sort_values(["live_start_date", "ticker"])

    wide = _wide_returns(equity_returns)
    return_rows = []
    for live_start, group in tilted_weights.groupby("live_start_date", sort=True):
        live_end = group["live_end_date"].iloc[0]
        live_dates = wide.index[(wide.index >= live_start) & (wide.index <= live_end)]
        if len(live_dates) == 0:
            continue
        w = group.set_index("ticker")["weight"].reindex(wide.columns).fillna(0.0)
        daily = wide.loc[live_dates].dot(w)
        return_rows.append(
            pd.DataFrame(
                {
                    "date": daily.index,
                    "fund_id": output_fund_id,
                    "base_fund_id": base_fund_id,
                    "universe": "Equity",
                    "method": "sentiment_tilt",
                    "method_label": "Sentiment Tilt",
                    "daily_return": daily.to_numpy(dtype="float64"),
                    "rebalance_date": group["rebalance_date"].iloc[0],
                    "live_start_date": live_start,
                    "live_end_date": live_end,
                    "periods_per_year": periods_per_year,
                    "tilt_strength": tilt_strength,
                }
            )
        )

    if not return_rows:
        raise ValueError("sentiment tilt produced no live returns")

    tilted_returns = pd.concat(return_rows, ignore_index=True).sort_values("date")
    tilted_returns["growth_of_1"] = (1.0 + tilted_returns["daily_return"]).cumprod()
    tilted_returns["drawdown"] = (
        tilted_returns["growth_of_1"] / tilted_returns["growth_of_1"].cummax() - 1.0
    )

    metrics = portfolios.performance_metrics(tilted_returns["daily_return"], periods_per_year=periods_per_year)
    metrics.update(
        {
            "fund_id": output_fund_id,
            "base_fund_id": base_fund_id,
            "universe": "Equity",
            "method": "sentiment_tilt",
            "method_label": "Sentiment Tilt",
            "first_live_date": tilted_returns["date"].min(),
            "last_live_date": tilted_returns["date"].max(),
            "tilt_strength": tilt_strength,
            "signal_column": z_col,
            "signal_lag": "at least one sector observation",
        }
    )

    lag_violations = tilted_weights[
        tilted_weights["lagged_signal_date"].notna()
        & (tilted_weights["lagged_signal_date"] >= tilted_weights["live_start_date"])
    ]
    diagnostics = pd.DataFrame(
        [
            {
                "base_fund_id": base_fund_id,
                "tilted_fund_id": output_fund_id,
                "tilt_strength": tilt_strength,
                "weight_sum_max_abs_error": float(
                    (tilted_weights.groupby("live_start_date")["weight"].sum() - 1.0).abs().max()
                ),
                "lag_violations": int(len(lag_violations)),
                "mean_abs_weight_change": float(
                    (tilted_weights["weight"] - tilted_weights["base_weight"]).abs().mean()
                ),
                "max_abs_weight_change": float(
                    (tilted_weights["weight"] - tilted_weights["base_weight"]).abs().max()
                ),
            }
        ]
    )

    return {
        "returns": tilted_returns,
        "weights": tilted_weights,
        "metrics": pd.DataFrame([metrics]),
        "diagnostics": diagnostics,
    }


def fusion_comparison(
    base_returns: pd.DataFrame,
    tilted_returns: pd.DataFrame,
    base_fund_id: str,
    tilted_fund_id: str,
    periods_per_year: int = 252,
) -> pd.DataFrame:
    """Build a before-vs-after comparison table for the fusion extension."""
    base = base_returns[base_returns["fund_id"] == base_fund_id].copy()
    tilted = tilted_returns[tilted_returns["fund_id"] == tilted_fund_id].copy()
    if base.empty or tilted.empty:
        raise ValueError("base or tilted return series is empty")

    base["date"] = pd.to_datetime(base["date"])
    tilted["date"] = pd.to_datetime(tilted["date"])
    common_dates = base["date"].isin(tilted["date"])
    base = base[common_dates]

    rows = []
    for label, frame in [("Base", base), ("Sentiment Tilt", tilted)]:
        metrics = portfolios.performance_metrics(frame["daily_return"], periods_per_year=periods_per_year)
        metrics.update(
            {
                "model": label,
                "fund_id": base_fund_id if label == "Base" else tilted_fund_id,
            }
        )
        rows.append(metrics)

    out = pd.DataFrame(rows)
    base_row = out[out["model"] == "Base"].iloc[0]
    for col in ["annualised_return", "annualised_volatility", "sharpe_ratio", "max_drawdown", "final_growth_of_1"]:
        out[f"delta_{col}_vs_base"] = out[col] - base_row[col]
    return out[
        [
            "model",
            "fund_id",
            "observations",
            "annualised_return",
            "annualised_volatility",
            "sharpe_ratio",
            "max_drawdown",
            "final_growth_of_1",
            "delta_annualised_return_vs_base",
            "delta_annualised_volatility_vs_base",
            "delta_sharpe_ratio_vs_base",
            "delta_max_drawdown_vs_base",
            "delta_final_growth_of_1_vs_base",
        ]
    ]
