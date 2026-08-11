"""Station 2 feature helpers reused as the Part B modelling input layer.

These functions build return features and assemble text panels only. Sentiment
scoring, portfolio optimisation, and backtesting are handled in separate Part B
modules.
"""
from __future__ import annotations

import pandas as pd


def daily_returns(prices: pd.DataFrame, price_col: str = "adjClose") -> pd.DataFrame:
    """Compute simple daily returns per ticker from adjusted close prices."""
    required = {"ticker", "date", price_col}
    missing = required.difference(prices.columns)
    if missing:
        raise ValueError(f"prices is missing required columns: {sorted(missing)}")

    df = prices.sort_values(["ticker", "date"]).copy()
    df["daily_return"] = df.groupby("ticker", sort=False)[price_col].pct_change()

    cols = ["date", "ticker", "daily_return"]
    if "sector" in df.columns:
        cols.append("sector")

    return df.loc[df["daily_return"].notna(), cols].reset_index(drop=True)


def align_crypto_returns_to_equity_calendar(
    crypto_returns: pd.DataFrame,
    equity_calendar: pd.Series,
) -> pd.DataFrame:
    """Left-align crypto returns onto the equity trading calendar."""
    dates = pd.Index(pd.to_datetime(equity_calendar).drop_duplicates().sort_values())
    tickers = sorted(crypto_returns["ticker"].dropna().unique())
    calendar = pd.MultiIndex.from_product(
        [dates, tickers],
        names=["date", "ticker"],
    ).to_frame(index=False)

    aligned = calendar.merge(
        crypto_returns[["date", "ticker", "daily_return"]],
        on=["date", "ticker"],
        how="left",
    )
    aligned["sector"] = "Crypto"
    return aligned


def assemble_headline_panel(
    headlines: pd.DataFrame,
    equity_calendar: pd.Series | None = None,
) -> pd.DataFrame:
    """Assemble headlines into a daily ticker-sector text panel.

    If an equity calendar is supplied, each headline date is mapped to the same
    trading day or the next available trading day.
    """
    required = {"date", "ticker", "sector", "title"}
    missing = required.difference(headlines.columns)
    if missing:
        raise ValueError(f"headlines is missing required columns: {sorted(missing)}")

    df = headlines.copy()
    df["date"] = (
        pd.to_datetime(df["date"], utc=True, errors="coerce")
        .dt.tz_convert(None)
        .dt.normalize()
        .astype("datetime64[ns]")
    )
    df["title"] = df["title"].fillna("").astype(str).str.strip()
    df["publisher"] = df.get("publisher", "").fillna("").astype(str).str.strip()
    df = df.drop_duplicates(subset=["ticker", "date", "title"])

    if equity_calendar is not None:
        trading_days = pd.DataFrame(
            {
                "trading_date": pd.to_datetime(equity_calendar)
                .drop_duplicates()
                .sort_values()
                .reset_index(drop=True)
                .astype("datetime64[ns]")
            }
        )
        df = df.sort_values("date")
        df = pd.merge_asof(
            df,
            trading_days,
            left_on="date",
            right_on="trading_date",
            direction="forward",
        )
        df = df[df["trading_date"].notna()].copy()
    else:
        df["trading_date"] = df["date"]

    grouped = (
        df.groupby(["trading_date", "ticker", "sector"], as_index=False)
        .agg(
            headline_count=("title", "size"),
            unique_publishers=("publisher", lambda x: int(x.replace("", pd.NA).dropna().nunique())),
            headline_text=("title", lambda x: " | ".join(x)),
        )
        .rename(columns={"trading_date": "date"})
        .sort_values(["date", "ticker"])
        .reset_index(drop=True)
    )
    return grouped
