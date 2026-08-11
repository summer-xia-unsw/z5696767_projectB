"""Station 1 ETL helpers reused as the Part B data foundation.

All raw data is loaded through ``src.data_access``. This module standardises
dates, applies the project-specific cleaning rules, and exposes small audit
helpers used before the Part B portfolio and sentiment models run.
"""
from __future__ import annotations

import pandas as pd

from src import data_access


CRYPTO_END_DATE = pd.Timestamp("2023-12-31")


def normalise_date_column(df: pd.DataFrame, column: str = "date") -> pd.DataFrame:
    """Return a copy with a timezone-naive midnight datetime column."""
    out = df.copy()
    out[column] = (
        pd.to_datetime(out[column], utc=True, errors="coerce")
        .dt.tz_convert(None)
        .dt.normalize()
        .astype("datetime64[ns]")
    )
    return out


def load_clean_equities() -> pd.DataFrame:
    """Load equity prices and remove exact ticker-date duplicates if present."""
    df = normalise_date_column(data_access.load_equity_prices())
    df = df.drop_duplicates(subset=["ticker", "date"], keep="first")
    return df.sort_values(["ticker", "date"]).reset_index(drop=True)


def load_clean_crypto() -> pd.DataFrame:
    """Load crypto prices, cap the sample at 2023-12-31, and deduplicate."""
    df = normalise_date_column(data_access.load_crypto_prices())
    df = df[df["date"] <= CRYPTO_END_DATE].copy()
    df = df.drop_duplicates(subset=["ticker", "date"], keep="first")
    return df.sort_values(["ticker", "date"]).reset_index(drop=True)


def load_clean_headlines() -> pd.DataFrame:
    """Load headlines, normalise dates, and remove exact duplicate headlines."""
    df = normalise_date_column(data_access.load_news_headlines())
    df["title"] = df["title"].fillna("").astype(str).str.strip()
    df["publisher"] = df["publisher"].fillna("").astype(str).str.strip()
    df = df.drop_duplicates(subset=["ticker", "date", "title"], keep="first")
    return df.sort_values(["ticker", "date", "title"]).reset_index(drop=True)


def duplicate_count(df: pd.DataFrame, keys: list[str]) -> int:
    """Count duplicate rows by a key set."""
    return int(df.duplicated(subset=keys).sum())


def price_calendar_audit(df: pd.DataFrame, dataset: str) -> pd.DataFrame:
    """Count missing observations per ticker against the dataset's own calendar."""
    calendar = pd.Index(sorted(df["date"].dropna().unique()))
    rows = []
    for ticker, group in df.groupby("ticker", sort=True):
        observed = pd.Index(sorted(group["date"].dropna().unique()))
        missing = calendar.difference(observed)
        rows.append(
            {
                "dataset": dataset,
                "ticker": ticker,
                "expected_dates": len(calendar),
                "observed_dates": len(observed),
                "missing_dates": len(missing),
                "first_missing_date": (
                    pd.Timestamp(missing[0]).date().isoformat()
                    if len(missing)
                    else ""
                ),
            }
        )
    return pd.DataFrame(rows)


def price_consistency_summary(df: pd.DataFrame, dataset: str) -> pd.DataFrame:
    """Summarise basic OHLCV consistency checks."""
    checks = {
        "negative_volume_rows": (df["volume"] < 0).sum(),
        "nonpositive_adjclose_rows": (df["adjClose"] <= 0).sum(),
        "high_below_low_rows": (df["high"] < df["low"]).sum(),
        "open_outside_high_low_rows": ((df["open"] > df["high"]) | (df["open"] < df["low"])).sum(),
        "close_outside_high_low_rows": ((df["close"] > df["high"]) | (df["close"] < df["low"])).sum(),
    }
    return pd.DataFrame(
        [{"dataset": dataset, "check": key, "rows": int(value)} for key, value in checks.items()]
    )


def dataset_inventory(raw: dict[str, pd.DataFrame], clean: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Build a compact inventory table for the report."""
    metadata = {
        "equity_prices": "50 US equities, OHLCV + adjusted close + sector",
        "crypto_prices": "10 cryptocurrencies, OHLCV + adjusted close",
        "news_headlines": "Equity news headlines, ticker, sector, URL, publisher",
    }
    frequency = {
        "equity_prices": "US equity trading days",
        "crypto_prices": "Daily crypto calendar capped at 2023-12-31",
        "news_headlines": "Headline event dates aligned later to equity trading days",
    }
    rows = []
    for name, df in clean.items():
        date_min = df["date"].min()
        date_max = df["date"].max()
        rows.append(
            {
                "dataset": name,
                "raw_rows": len(raw[name]),
                "clean_rows": len(df),
                "start_date": date_min.date().isoformat(),
                "end_date": date_max.date().isoformat(),
                "unique_tickers": df["ticker"].nunique() if "ticker" in df.columns else "",
                "unique_sectors": df["sector"].nunique() if "sector" in df.columns else "",
                "frequency": frequency[name],
                "coverage": metadata[name],
                "source": "Course-hosted project data ZIP via src/data_access.py",
            }
        )
    return pd.DataFrame(rows)
