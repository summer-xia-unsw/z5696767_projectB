"""Station 3 sentiment model and sector index from news headlines.

The model scores each headline with VADER plus a small documented finance lexicon
extension. It then aggregates headline scores to ticker-days and equal-weights
those ticker-days into sector sentiment indices. Trading signals are lagged so a
day-t decision can only use day t-1 sentiment or earlier.
"""
from __future__ import annotations

import math
from typing import Iterable

import numpy as np
import pandas as pd


MODEL_NAME = "nltk_vader_finance_lexicon_v1"

# A deliberately small finance extension inspired by the Week08 finance-lexicon
# lecture. Accounting category words such as debt, tax, cost, and liability are
# not changed because the lecture warns that they are often descriptive rather
# than sentiment-bearing in financial text.
FINANCE_LEXICON = {
    "beat": 2.4,
    "beats": 2.4,
    "outperform": 2.1,
    "outperforms": 2.1,
    "upgrade": 2.0,
    "upgrades": 2.0,
    "surge": 2.2,
    "surges": 2.2,
    "rally": 1.8,
    "rallies": 1.8,
    "buyback": 1.7,
    "record": 1.5,
    "tailwind": 1.4,
    "dovish": 1.0,
    "miss": -2.2,
    "misses": -2.2,
    "downgrade": -2.3,
    "downgrades": -2.3,
    "plunge": -2.6,
    "plunges": -2.6,
    "slump": -2.2,
    "slumps": -2.2,
    "impairment": -2.0,
    "insolvency": -3.6,
    "headwind": -1.5,
    "hawkish": -1.0,
    "lawsuit": -1.8,
    "probe": -1.4,
    "warning": -2.0,
}


def ensure_vader_lexicon() -> None:
    """Ensure NLTK's VADER lexicon is available for the build step."""
    import nltk

    try:
        nltk.data.find("sentiment/vader_lexicon.zip")
    except LookupError:
        nltk.download("vader_lexicon", quiet=True)


def build_analyzer():
    """Build the VADER analyzer with the finance lexicon extension installed."""
    ensure_vader_lexicon()
    from nltk.sentiment import SentimentIntensityAnalyzer

    analyzer = SentimentIntensityAnalyzer()
    analyzer.lexicon.update(FINANCE_LEXICON)
    return analyzer


def to_score_100(compound: float | pd.Series) -> float | pd.Series:
    """Map VADER compound scores from [-1, 1] to a 0-100 fear/greed scale."""
    return (compound + 1.0) / 2.0 * 100.0


def split_headlines(text: object) -> list[str]:
    """Split the assembled ticker-day text back into individual headlines."""
    if pd.isna(text):
        return []
    return [part.strip() for part in str(text).split(" | ") if part.strip()]


def _score_titles(titles: Iterable[str], analyzer) -> dict[str, float | int]:
    compounds = []
    pos_scores = []
    neu_scores = []
    neg_scores = []
    for title in titles:
        score = analyzer.polarity_scores(title)
        compounds.append(float(score["compound"]))
        pos_scores.append(float(score["pos"]))
        neu_scores.append(float(score["neu"]))
        neg_scores.append(float(score["neg"]))

    if not compounds:
        return {
            "scored_headlines": 0,
            "compound": np.nan,
            "positive_component": np.nan,
            "neutral_component": np.nan,
            "negative_component": np.nan,
            "share_positive_headlines": np.nan,
            "share_neutral_headlines": np.nan,
            "share_negative_headlines": np.nan,
        }

    values = pd.Series(compounds, dtype="float64")
    return {
        "scored_headlines": int(len(values)),
        "compound": float(values.mean()),
        "positive_component": float(np.mean(pos_scores)),
        "neutral_component": float(np.mean(neu_scores)),
        "negative_component": float(np.mean(neg_scores)),
        "share_positive_headlines": float((values > 0.05).mean()),
        "share_neutral_headlines": float((values.abs() <= 0.05).mean()),
        "share_negative_headlines": float((values < -0.05).mean()),
    }


def score_headlines(panel: pd.DataFrame) -> pd.DataFrame:
    """Score the assembled headline panel at ticker-day level.

    Input rows are expected to contain `headline_text`, where multiple raw
    headlines are separated by ` | `. Each raw headline is scored separately and
    then averaged, avoiding the length bias that would come from scoring a long
    concatenated document as one text.
    """
    required = {"date", "ticker", "sector", "headline_count", "headline_text"}
    missing = required.difference(panel.columns)
    if missing:
        raise ValueError(f"headline panel is missing required columns: {sorted(missing)}")

    analyzer = build_analyzer()
    rows = []
    for row in panel.itertuples(index=False):
        titles = split_headlines(getattr(row, "headline_text"))
        scores = _score_titles(titles, analyzer)
        rows.append(
            {
                "date": pd.to_datetime(getattr(row, "date")),
                "ticker": getattr(row, "ticker"),
                "sector": getattr(row, "sector"),
                "headline_count": int(getattr(row, "headline_count")),
                **scores,
                "model": MODEL_NAME,
            }
        )

    scored = pd.DataFrame(rows)
    scored = scored[scored["scored_headlines"] > 0].copy()
    scored["score_100"] = to_score_100(scored["compound"])
    return scored.sort_values(["date", "ticker"]).reset_index(drop=True)


def _expanding_live_zscore(values: pd.Series, min_periods: int = 20) -> pd.Series:
    """Compute a z-score using only history before each current observation."""
    mean_prior = values.expanding(min_periods=min_periods).mean().shift(1)
    sd_prior = values.expanding(min_periods=min_periods).std(ddof=1).shift(1)
    z = (values - mean_prior) / sd_prior.replace(0, np.nan)
    return z.replace([np.inf, -np.inf], np.nan)


def sector_sentiment_index(scores: pd.DataFrame) -> pd.DataFrame:
    """Build a daily sector sentiment index, equal-weighting ticker-days.

    Ticker-days with no headlines are dropped from the sector average. Coverage
    columns show how many of the five sector names had news on each date. Lagged
    columns are for trading and shift the signal by one sector observation.
    """
    required = {"date", "ticker", "sector", "headline_count", "compound", "score_100"}
    missing = required.difference(scores.columns)
    if missing:
        raise ValueError(f"scores is missing required columns: {sorted(missing)}")

    data = scores.copy()
    data["date"] = pd.to_datetime(data["date"])

    sector = (
        data.groupby(["date", "sector"], as_index=False)
        .agg(
            ticker_days_with_news=("ticker", "nunique"),
            total_headlines=("headline_count", "sum"),
            compound=("compound", "mean"),
            score_100=("score_100", "mean"),
            share_positive_headlines=("share_positive_headlines", "mean"),
            share_neutral_headlines=("share_neutral_headlines", "mean"),
            share_negative_headlines=("share_negative_headlines", "mean"),
        )
        .sort_values(["sector", "date"])
        .reset_index(drop=True)
    )
    sector["sector_ticker_count"] = 5
    sector["ticker_coverage_rate"] = sector["ticker_days_with_news"] / sector["sector_ticker_count"]

    sector["sector_z_full_sample"] = sector.groupby("sector")["score_100"].transform(
        lambda x: (x - x.mean()) / x.std(ddof=1) if x.std(ddof=1) > 0 else 0.0
    )
    sector["sector_z_live"] = sector.groupby("sector", group_keys=False)["score_100"].apply(
        _expanding_live_zscore
    )
    sector["lagged_compound"] = sector.groupby("sector")["compound"].shift(1)
    sector["lagged_score_100"] = sector.groupby("sector")["score_100"].shift(1)
    sector["lagged_sector_z"] = sector.groupby("sector")["sector_z_live"].shift(1)
    sector["lagged_signal_date"] = sector.groupby("sector")["date"].shift(1)

    cols = [
        "date",
        "sector",
        "ticker_days_with_news",
        "sector_ticker_count",
        "ticker_coverage_rate",
        "total_headlines",
        "compound",
        "score_100",
        "sector_z_full_sample",
        "sector_z_live",
        "lagged_signal_date",
        "lagged_compound",
        "lagged_score_100",
        "lagged_sector_z",
        "share_positive_headlines",
        "share_neutral_headlines",
        "share_negative_headlines",
    ]
    return sector[cols].sort_values(["date", "sector"]).reset_index(drop=True)


def sentiment_coverage_summary(scores: pd.DataFrame) -> pd.DataFrame:
    """Summarise headline coverage and sentiment classification by sector."""
    data = scores.copy()
    data["date"] = pd.to_datetime(data["date"])
    return (
        data.groupby("sector", as_index=False)
        .agg(
            ticker_days_with_news=("ticker", "size"),
            total_headlines=("headline_count", "sum"),
            first_date=("date", "min"),
            last_date=("date", "max"),
            mean_score_100=("score_100", "mean"),
            mean_compound=("compound", "mean"),
            neutral_headline_share=("share_neutral_headlines", "mean"),
        )
        .sort_values("total_headlines", ascending=False)
        .reset_index(drop=True)
    )


def sector_sentiment_summary(index: pd.DataFrame) -> pd.DataFrame:
    """Summarise the sector sentiment index for tables and reporting."""
    data = index.copy()
    data["date"] = pd.to_datetime(data["date"])
    return (
        data.groupby("sector", as_index=False)
        .agg(
            observations=("date", "size"),
            mean_score_100=("score_100", "mean"),
            min_score_100=("score_100", "min"),
            max_score_100=("score_100", "max"),
            mean_ticker_coverage=("ticker_coverage_rate", "mean"),
            total_headlines=("total_headlines", "sum"),
        )
        .sort_values("mean_score_100", ascending=False)
        .reset_index(drop=True)
    )


def market_fear_greed_index(index: pd.DataFrame) -> pd.DataFrame:
    """Average sectors into a market-level fear/greed index for app/report use."""
    data = index.copy()
    data["date"] = pd.to_datetime(data["date"])
    market = (
        data.groupby("date", as_index=False)
        .agg(
            score_100=("score_100", "mean"),
            total_headlines=("total_headlines", "sum"),
            average_sector_coverage=("ticker_coverage_rate", "mean"),
        )
        .sort_values("date")
        .reset_index(drop=True)
    )
    sd = market["score_100"].std(ddof=1)
    market["market_z_full_sample"] = (
        (market["score_100"] - market["score_100"].mean()) / sd if sd > 0 else 0.0
    )
    return market
