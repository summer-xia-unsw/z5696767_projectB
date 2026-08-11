"""Reproduce the Project B results. Run from the project root:

    python scripts/run_part_b.py

The script prepares the data foundation, builds out-of-sample funds, scores news
sentiment into sector indices, and tests a look-ahead-safe sentiment tilt.
"""
from __future__ import annotations

import sys
import pathlib
import shutil

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from src import etl, features, fusion, portfolios, sentiment  # noqa: E402


ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "results" / "data"
TABLE_DIR = ROOT / "results" / "tables"
FIGURE_DIR = ROOT / "results" / "figures"
NUMBERED_DIR_NAMES = {
    "data": "Number_data",
    "tables": "Number_tables",
    "figures": "Number_figures",
}

PORTFOLIO_METHODS = ["equal_weight", "min_variance", "max_sharpe", "risk_parity"]
BASE_FUSION_FUND = "Equity - Minimum Variance"
TILTED_FUSION_FUND = "Equity - Minimum Variance Sentiment Tilt"

STAGE_ALIASES = {
    "results/data/equity_returns.csv": "01_equity_returns.csv",
    "results/data/crypto_returns_aligned.csv": "01_crypto_returns_aligned.csv",
    "results/data/combined_returns_panel.csv": "01_combined_returns_panel.csv",
    "results/data/headline_daily_panel.csv": "01_headline_daily_panel.csv",
    "results/data/fund_returns.csv": "02_fund_returns.csv",
    "results/data/fund_weights.csv": "02_fund_weights.csv",
    "results/tables/performance_metrics.csv": "02_performance_metrics.csv",
    "results/tables/latest_holdings.csv": "02_latest_holdings.csv",
    "results/figures/fund_growth_of_1.png": "02_fund_growth_of_1.png",
    "results/figures/combined_fund_drawdowns.png": "02_combined_fund_drawdowns.png",
    "results/figures/combined_risk_parity_weights.png": "02_combined_risk_parity_weights.png",
    "results/figures/fund_sharpe_barplot.png": "02_fund_sharpe_barplot.png",
    "results/figures/fund_risk_return_scatter.png": "02_fund_risk_return_scatter.png",
    "results/data/ticker_sentiment_scores.csv": "03_ticker_sentiment_scores.csv",
    "results/data/sector_sentiment_index.csv": "03_sector_sentiment_index.csv",
    "results/data/market_fear_greed_index.csv": "03_market_fear_greed_index.csv",
    "results/data/fusion_fund_returns.csv": "03_fusion_fund_returns.csv",
    "results/data/fusion_fund_weights.csv": "03_fusion_fund_weights.csv",
    "results/tables/sentiment_coverage_summary.csv": "03_sentiment_coverage_summary.csv",
    "results/tables/sector_sentiment_summary.csv": "03_sector_sentiment_summary.csv",
    "results/tables/fusion_comparison.csv": "03_fusion_comparison.csv",
    "results/tables/fusion_metrics.csv": "03_fusion_metrics.csv",
    "results/tables/fusion_diagnostics.csv": "03_fusion_diagnostics.csv",
    "results/figures/sector_sentiment_index.png": "03_sector_sentiment_index.png",
    "results/figures/sector_sentiment_ranking.png": "03_sector_sentiment_ranking.png",
    "results/figures/market_fear_greed_index.png": "03_market_fear_greed_index.png",
    "results/figures/fusion_growth_comparison.png": "03_fusion_growth_comparison.png",
    "results/figures/fusion_drawdown_comparison.png": "03_fusion_drawdown_comparison.png",
}

def ensure_dirs() -> None:
    for path in [DATA_DIR, TABLE_DIR, FIGURE_DIR]:
        path.mkdir(parents=True, exist_ok=True)
    for parent_name, numbered_name in NUMBERED_DIR_NAMES.items():
        (ROOT / "results" / parent_name / numbered_name).mkdir(parents=True, exist_ok=True)


def save_csv(df: pd.DataFrame, path: pathlib.Path) -> None:
    df.to_csv(path, index=False, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)} ({len(df):,} rows)")


def save_figure(path: pathlib.Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=180, bbox_inches="tight")
    plt.close()
    print(f"wrote {path.relative_to(ROOT)}")


def copy_stage_aliases() -> None:
    """Create numbered copies for easier reading without breaking required names."""
    for rel, alias in STAGE_ALIASES.items():
        src = ROOT / rel
        if not src.exists():
            continue
        numbered_dir = src.parent / NUMBERED_DIR_NAMES.get(src.parent.name, "")
        numbered_dir.mkdir(parents=True, exist_ok=True)
        dst = numbered_dir / alias
        shutil.copy2(src, dst)
        print(f"wrote {dst.relative_to(ROOT)}")


def write_output_index() -> None:
    """Write a compact index explaining stage-prefixed output files."""
    text = """# Results Output Index

This folder keeps the course-required filenames and also provides numbered
copies for reading. Numbered copies are now collected under `Number_data`,
`Number_tables`, and `Number_figures` folders.

Do not delete the unnumbered files. `scripts/check_handin.py` and the Streamlit
app rely on exact names such as `fund_returns.csv`, `fund_weights.csv`,
`sector_sentiment_index.csv`, and `performance_metrics.csv`.

## 00 - Output Guides

- `results/data/Number_data/00_data_output_guide.docx`
- `results/tables/Number_tables/00_tables_output_guide.docx`
- `results/figures/Number_figures/00_figures_output_guide.docx`

Purpose: Chinese quick-reference guides for understanding numbered outputs.

## 01 - Data Foundation

- `results/data/Number_data/01_equity_returns.csv`
- `results/data/Number_data/01_crypto_returns_aligned.csv`
- `results/data/Number_data/01_combined_returns_panel.csv`
- `results/data/Number_data/01_headline_daily_panel.csv`

Purpose: cleaned return and headline-panel inputs for Part B modelling.

## 02 - Portfolios And OOS Backtest

- `results/data/Number_data/02_fund_returns.csv`
- `results/data/Number_data/02_fund_weights.csv`
- `results/tables/Number_tables/02_performance_metrics.csv`
- `results/tables/Number_tables/02_latest_holdings.csv`
- `results/figures/Number_figures/02_fund_growth_of_1.png`
- `results/figures/Number_figures/02_combined_fund_drawdowns.png`
- `results/figures/Number_figures/02_combined_risk_parity_weights.png`
- `results/figures/Number_figures/02_fund_sharpe_barplot.png`
- `results/figures/Number_figures/02_fund_risk_return_scatter.png`

Purpose: investable funds, monthly walk-forward out-of-sample performance,
weights, metrics, and fact-sheet inputs.

## 03 - Sentiment And Fusion

- `results/data/Number_data/03_ticker_sentiment_scores.csv`
- `results/data/Number_data/03_sector_sentiment_index.csv`
- `results/data/Number_data/03_market_fear_greed_index.csv`
- `results/data/Number_data/03_fusion_fund_returns.csv`
- `results/data/Number_data/03_fusion_fund_weights.csv`
- `results/tables/Number_tables/03_sentiment_coverage_summary.csv`
- `results/tables/Number_tables/03_sector_sentiment_summary.csv`
- `results/tables/Number_tables/03_fusion_comparison.csv`
- `results/tables/Number_tables/03_fusion_metrics.csv`
- `results/tables/Number_tables/03_fusion_diagnostics.csv`
- `results/figures/Number_figures/03_sector_sentiment_index.png`
- `results/figures/Number_figures/03_sector_sentiment_ranking.png`
- `results/figures/Number_figures/03_market_fear_greed_index.png`
- `results/figures/Number_figures/03_fusion_growth_comparison.png`
- `results/figures/Number_figures/03_fusion_drawdown_comparison.png`

Purpose: finance-extended VADER sentiment, sector fear/greed analytics, and
base-vs-sentiment-tilt fusion results.

## 04 - App Consumption Layer

- `results/data/app_data_manifest.csv`
- `results/tables/app_table_manifest.csv`
- `results/figures/app_page_data_map.png`
- `results/data/Number_data/04_app_data_manifest.csv`
- `results/tables/Number_tables/04_app_table_manifest.csv`
- `results/figures/Number_figures/04_app_page_data_map.png`

Purpose: documents which canonical `results/` artifacts are read by
`streamlit_app.py`. Stage 04 does not create new model data; it consumes
precomputed files from stages 02 and 03 so the app stays light and does not
rerun VADER or backtests at runtime. The unnumbered files are canonical; the
`04_` files under `Number_*` are matching stage-labelled copies.

## 05 - Report And Submission Support

- `results/figures/report_combined_asset_class_weights.png`
- `results/figures/report_projectb_workflow_data_flow.png`
- `results/data/report_data_manifest.csv`
- `results/tables/report_table_manifest.csv`
- `results/tables/numbered_file_integrity_audit.csv`
- `results/data/Number_data/05_report_data_manifest.csv`
- `results/tables/Number_tables/05_report_table_manifest.csv`
- `results/tables/Number_tables/05_numbered_file_integrity_audit.csv`
- `results/figures/Number_figures/05_report_combined_asset_class_weights.png`
- `results/figures/Number_figures/05_report_projectb_workflow_data_flow.png`

Purpose: report-supporting exhibits. `report_combined_asset_class_weights.png`
compares Combined fund Equity/Crypto weights over time across the four portfolio
methods, making the course-required portfolio-weights-over-time exhibit clearer.
`report_projectb_workflow_data_flow.png` explains how raw market/news inputs,
ETL/features, funds, sentiment, fusion, canonical results, the Streamlit app,
the Word report, and AI workflow checks connect. The `05_` files are report-stage
copies or manifests to make final report evidence easy to identify.
`numbered_file_integrity_audit.csv` records the latest content-hash check
between numbered files and their unnumbered canonical counterparts.

A copy of `report_projectb_workflow_data_flow.png` is also saved under
`report/report_projectb_workflow_data_flow.png` so it is easy to find while
editing the Word report.
"""
    path = ROOT / "results" / "OUTPUT_INDEX.md"
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")

def build_foundation_outputs() -> dict[str, pd.DataFrame]:
    """Build return and headline-panel outputs needed by later Part B models."""
    clean_equity = etl.load_clean_equities()
    clean_crypto = etl.load_clean_crypto()
    clean_news = etl.load_clean_headlines()

    equity_returns = features.daily_returns(clean_equity).assign(asset_class="Equity")
    crypto_returns = features.daily_returns(clean_crypto).assign(
        asset_class="Crypto",
        sector="Crypto",
    )

    equity_calendar = clean_equity["date"].drop_duplicates().sort_values()
    crypto_returns_aligned = features.align_crypto_returns_to_equity_calendar(
        crypto_returns,
        equity_calendar,
    ).assign(asset_class="Crypto")

    combined_returns = pd.concat(
        [
            equity_returns[["date", "ticker", "sector", "asset_class", "daily_return"]],
            crypto_returns_aligned[["date", "ticker", "sector", "asset_class", "daily_return"]],
        ],
        ignore_index=True,
    ).sort_values(["date", "asset_class", "ticker"])

    headline_panel = features.assemble_headline_panel(clean_news, equity_calendar)

    return {
        "equity_returns": equity_returns,
        "crypto_returns_full": crypto_returns,
        "crypto_returns_aligned": crypto_returns_aligned,
        "combined_returns_panel": combined_returns,
        "headline_daily_panel": headline_panel,
    }


def asset_metadata(outputs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Return one metadata row per ticker for labelling holdings."""
    meta = pd.concat(
        [
            outputs["equity_returns"][["ticker", "sector", "asset_class"]],
            outputs["crypto_returns_full"][["ticker", "sector", "asset_class"]],
        ],
        ignore_index=True,
    )
    return meta.drop_duplicates(subset=["ticker"]).reset_index(drop=True)


def build_portfolio_outputs(outputs: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Build OOS fund returns, weights, and performance metrics."""
    configs = [
        {
            "universe": "Equity",
            "returns": outputs["equity_returns"],
            "periods_per_year": 252,
            "initial_window": 252,
        },
        {
            "universe": "Crypto",
            "returns": outputs["crypto_returns_full"],
            "periods_per_year": 365,
            "initial_window": 365,
        },
        {
            "universe": "Combined",
            "returns": outputs["combined_returns_panel"],
            "periods_per_year": 252,
            "initial_window": 252,
        },
    ]

    all_returns = []
    all_weights = []
    all_metrics = []
    meta = asset_metadata(outputs)

    for config in configs:
        for method in PORTFOLIO_METHODS:
            print(f"backtesting {config['universe']} / {portfolios.method_label(method)}")
            result = portfolios.oos_backtest(
                config["returns"],
                method=method,
                universe=config["universe"],
                periods_per_year=config["periods_per_year"],
                initial_window=config["initial_window"],
                risk_free_rate=0.0,
            )
            all_returns.append(result["returns"])
            all_weights.append(result["weights"])
            all_metrics.append(result["metrics"])

    fund_returns = pd.concat(all_returns, ignore_index=True)
    fund_weights = pd.concat(all_weights, ignore_index=True).merge(meta, on="ticker", how="left")
    metrics = pd.DataFrame(all_metrics)

    ordered_cols = [
        "fund_id",
        "universe",
        "method",
        "method_label",
        "first_live_date",
        "last_live_date",
        "observations",
        "annualisation_factor",
        "annualised_return",
        "annualised_volatility",
        "sharpe_ratio",
        "max_drawdown",
        "final_growth_of_1",
        "average_turnover",
        "initial_window",
        "rebalance_frequency",
        "risk_free_rate",
        "mean_daily_return",
        "daily_volatility",
    ]
    metrics = metrics[ordered_cols].sort_values(["universe", "method"])
    return fund_returns, fund_weights, metrics


def latest_holdings_table(fund_weights: pd.DataFrame) -> pd.DataFrame:
    """Extract latest rebalance holdings for fact sheets."""
    weights = fund_weights.copy()
    weights["live_start_date"] = pd.to_datetime(weights["live_start_date"])
    latest_dates = weights.groupby("fund_id", as_index=False)["live_start_date"].max()
    latest = weights.merge(latest_dates, on=["fund_id", "live_start_date"], how="inner")
    latest = latest[latest["weight"] > 0.001].copy()
    return latest.sort_values(["fund_id", "weight"], ascending=[True, False])[
        [
            "fund_id",
            "universe",
            "method",
            "method_label",
            "live_start_date",
            "ticker",
            "sector",
            "asset_class",
            "weight",
        ]
    ]


def build_sentiment_outputs(outputs: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    print("scoring headline sentiment with finance-extended VADER")
    scores = sentiment.score_headlines(outputs["headline_daily_panel"])
    sector_index = sentiment.sector_sentiment_index(scores)
    coverage = sentiment.sentiment_coverage_summary(scores)
    sector_summary = sentiment.sector_sentiment_summary(sector_index)
    market_index = sentiment.market_fear_greed_index(sector_index)
    return {
        "ticker_sentiment_scores": scores,
        "sector_sentiment_index": sector_index,
        "sentiment_coverage_summary": coverage,
        "sector_sentiment_summary": sector_summary,
        "market_fear_greed_index": market_index,
    }


def build_fusion_outputs(
    outputs: dict[str, pd.DataFrame],
    fund_returns: pd.DataFrame,
    fund_weights: pd.DataFrame,
    sector_index: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    print("building sentiment tilt fusion for Equity Minimum Variance")
    result = fusion.apply_sentiment(
        fund_weights,
        sector_index,
        outputs["equity_returns"],
        base_fund_id=BASE_FUSION_FUND,
        output_fund_id=TILTED_FUSION_FUND,
        tilt_strength=0.15,
    )
    comparison = fusion.fusion_comparison(
        fund_returns,
        result["returns"],
        base_fund_id=BASE_FUSION_FUND,
        tilted_fund_id=TILTED_FUSION_FUND,
        periods_per_year=252,
    )
    return {
        "fusion_fund_returns": result["returns"],
        "fusion_fund_weights": result["weights"],
        "fusion_metrics": result["metrics"],
        "fusion_diagnostics": result["diagnostics"],
        "fusion_comparison": comparison,
    }


def plot_growth(fund_returns: pd.DataFrame, path: pathlib.Path) -> None:
    data = fund_returns.copy()
    data["date"] = pd.to_datetime(data["date"])
    pivot = data.pivot_table(index="date", columns="fund_id", values="growth_of_1", aggfunc="last")

    plt.figure(figsize=(11.5, 7.0))
    for col in pivot.columns:
        plt.plot(pivot.index, pivot[col], linewidth=1.2, label=col)
    plt.title("Growth of $1 by out-of-sample fund")
    plt.xlabel("Date")
    plt.ylabel("Growth of $1")
    plt.legend(fontsize=7, ncol=2)
    save_figure(path)


def plot_combined_drawdowns(fund_returns: pd.DataFrame, path: pathlib.Path) -> None:
    data = fund_returns[fund_returns["universe"] == "Combined"].copy()
    data["date"] = pd.to_datetime(data["date"])
    pivot = data.pivot_table(index="date", columns="method_label", values="drawdown", aggfunc="last")

    plt.figure(figsize=(10.5, 6.0))
    for col in pivot.columns:
        plt.plot(pivot.index, pivot[col], linewidth=1.5, label=col)
    plt.title("Combined funds drawdown, out of sample")
    plt.xlabel("Date")
    plt.ylabel("Drawdown")
    plt.legend(fontsize=8)
    save_figure(path)


def plot_combined_weights(fund_weights: pd.DataFrame, path: pathlib.Path) -> None:
    data = fund_weights[
        (fund_weights["universe"] == "Combined") & (fund_weights["method"] == "risk_parity")
    ].copy()
    data["live_start_date"] = pd.to_datetime(data["live_start_date"])
    sector_weights = (
        data.groupby(["live_start_date", "sector"], as_index=False)["weight"].sum()
        .pivot(index="live_start_date", columns="sector", values="weight")
        .fillna(0.0)
        .sort_index()
    )

    plt.figure(figsize=(11.0, 6.2))
    plt.stackplot(
        sector_weights.index,
        [sector_weights[col] for col in sector_weights.columns],
        labels=sector_weights.columns,
        alpha=0.9,
    )
    plt.title("Combined Risk Parity fund weights by sector/asset class")
    plt.xlabel("Live month")
    plt.ylabel("Portfolio weight")
    plt.ylim(0, 1)
    plt.legend(fontsize=7, ncol=3, loc="upper left")
    save_figure(path)


def plot_sharpe_bar(metrics: pd.DataFrame, path: pathlib.Path) -> None:
    data = metrics.sort_values("sharpe_ratio")
    labels = data["fund_id"]
    colors = data["universe"].map({"Equity": "#376795", "Crypto": "#f28e2b", "Combined": "#59a14f"})

    plt.figure(figsize=(10.5, 7.0))
    plt.barh(labels, data["sharpe_ratio"], color=colors)
    plt.title("Out-of-sample Sharpe ratio by fund")
    plt.xlabel("Sharpe ratio")
    plt.ylabel("Fund")
    save_figure(path)


def plot_risk_return(metrics: pd.DataFrame, path: pathlib.Path) -> None:
    data = metrics.copy()
    colors = data["universe"].map({"Equity": "#376795", "Crypto": "#f28e2b", "Combined": "#59a14f"})

    plt.figure(figsize=(8.8, 6.4))
    plt.scatter(data["annualised_volatility"], data["annualised_return"], s=80, c=colors)
    for _, row in data.iterrows():
        plt.annotate(
            f"{row['universe']}\n{row['method_label']}",
            (row["annualised_volatility"], row["annualised_return"]),
            fontsize=7,
            xytext=(4, 4),
            textcoords="offset points",
        )
    plt.title("Out-of-sample annualised return versus volatility")
    plt.xlabel("Annualised volatility")
    plt.ylabel("Annualised return")
    save_figure(path)


def plot_sector_sentiment_index(sector_index: pd.DataFrame, path: pathlib.Path) -> None:
    data = sector_index.copy()
    data["date"] = pd.to_datetime(data["date"])
    pivot = data.pivot_table(index="date", columns="sector", values="score_100", aggfunc="mean").sort_index()
    smoothed = pivot.rolling(21, min_periods=5).mean()

    plt.figure(figsize=(11.5, 7.0))
    for col in smoothed.columns:
        plt.plot(smoothed.index, smoothed[col], linewidth=1.2, label=col)
    plt.axhline(50, color="#555555", linewidth=0.8, linestyle="--")
    plt.title("Sector news sentiment index, 21-day rolling average")
    plt.xlabel("Date")
    plt.ylabel("Fear/greed score, 0-100")
    plt.legend(fontsize=7, ncol=2)
    save_figure(path)


def plot_sector_sentiment_ranking(summary: pd.DataFrame, path: pathlib.Path) -> None:
    data = summary.sort_values("mean_score_100")
    plt.figure(figsize=(9.2, 6.2))
    plt.barh(data["sector"], data["mean_score_100"], color="#4e79a7")
    plt.axvline(50, color="#555555", linewidth=0.8, linestyle="--")
    plt.title("Average sector fear/greed score")
    plt.xlabel("Mean sentiment score, 0-100")
    plt.ylabel("Sector")
    save_figure(path)


def plot_market_fear_greed(market_index: pd.DataFrame, path: pathlib.Path) -> None:
    data = market_index.copy()
    data["date"] = pd.to_datetime(data["date"])
    data["rolling_score_100"] = data["score_100"].rolling(21, min_periods=5).mean()

    plt.figure(figsize=(10.8, 5.8))
    plt.plot(data["date"], data["rolling_score_100"], color="#9c755f", linewidth=1.7)
    plt.axhline(50, color="#555555", linewidth=0.8, linestyle="--")
    plt.title("Market news fear/greed index, 21-day rolling average")
    plt.xlabel("Date")
    plt.ylabel("Fear/greed score, 0-100")
    save_figure(path)


def plot_fusion_growth(fund_returns: pd.DataFrame, fusion_returns: pd.DataFrame, path: pathlib.Path) -> None:
    base = fund_returns[fund_returns["fund_id"] == BASE_FUSION_FUND][["date", "growth_of_1"]].copy()
    tilted = fusion_returns[["date", "growth_of_1"]].copy()
    base["date"] = pd.to_datetime(base["date"])
    tilted["date"] = pd.to_datetime(tilted["date"])

    plt.figure(figsize=(10.2, 5.8))
    plt.plot(base["date"], base["growth_of_1"], label="Base Minimum Variance", linewidth=1.8)
    plt.plot(tilted["date"], tilted["growth_of_1"], label="Sentiment Tilt", linewidth=1.8)
    plt.title("Fusion extension: growth of $1 before and after sentiment tilt")
    plt.xlabel("Date")
    plt.ylabel("Growth of $1")
    plt.legend()
    save_figure(path)


def plot_fusion_drawdown(fund_returns: pd.DataFrame, fusion_returns: pd.DataFrame, path: pathlib.Path) -> None:
    base = fund_returns[fund_returns["fund_id"] == BASE_FUSION_FUND][["date", "drawdown"]].copy()
    tilted = fusion_returns[["date", "drawdown"]].copy()
    base["date"] = pd.to_datetime(base["date"])
    tilted["date"] = pd.to_datetime(tilted["date"])

    plt.figure(figsize=(10.2, 5.8))
    plt.plot(base["date"], base["drawdown"], label="Base Minimum Variance", linewidth=1.8)
    plt.plot(tilted["date"], tilted["drawdown"], label="Sentiment Tilt", linewidth=1.8)
    plt.title("Fusion extension: drawdown before and after sentiment tilt")
    plt.xlabel("Date")
    plt.ylabel("Drawdown")
    plt.legend()
    save_figure(path)


def main() -> None:
    ensure_dirs()

    outputs = build_foundation_outputs()
    save_csv(outputs["equity_returns"], DATA_DIR / "equity_returns.csv")
    save_csv(outputs["crypto_returns_aligned"], DATA_DIR / "crypto_returns_aligned.csv")
    save_csv(outputs["combined_returns_panel"], DATA_DIR / "combined_returns_panel.csv")
    save_csv(outputs["headline_daily_panel"], DATA_DIR / "headline_daily_panel.csv")

    fund_returns, fund_weights, metrics = build_portfolio_outputs(outputs)
    save_csv(fund_returns, DATA_DIR / "fund_returns.csv")
    save_csv(fund_weights, DATA_DIR / "fund_weights.csv")
    save_csv(metrics, TABLE_DIR / "performance_metrics.csv")
    save_csv(latest_holdings_table(fund_weights), TABLE_DIR / "latest_holdings.csv")

    plot_growth(fund_returns, FIGURE_DIR / "fund_growth_of_1.png")
    plot_combined_drawdowns(fund_returns, FIGURE_DIR / "combined_fund_drawdowns.png")
    plot_combined_weights(fund_weights, FIGURE_DIR / "combined_risk_parity_weights.png")
    plot_sharpe_bar(metrics, FIGURE_DIR / "fund_sharpe_barplot.png")
    plot_risk_return(metrics, FIGURE_DIR / "fund_risk_return_scatter.png")

    sentiment_outputs = build_sentiment_outputs(outputs)
    save_csv(sentiment_outputs["ticker_sentiment_scores"], DATA_DIR / "ticker_sentiment_scores.csv")
    save_csv(sentiment_outputs["sector_sentiment_index"], DATA_DIR / "sector_sentiment_index.csv")
    save_csv(sentiment_outputs["market_fear_greed_index"], DATA_DIR / "market_fear_greed_index.csv")
    save_csv(sentiment_outputs["sentiment_coverage_summary"], TABLE_DIR / "sentiment_coverage_summary.csv")
    save_csv(sentiment_outputs["sector_sentiment_summary"], TABLE_DIR / "sector_sentiment_summary.csv")

    plot_sector_sentiment_index(
        sentiment_outputs["sector_sentiment_index"],
        FIGURE_DIR / "sector_sentiment_index.png",
    )
    plot_sector_sentiment_ranking(
        sentiment_outputs["sector_sentiment_summary"],
        FIGURE_DIR / "sector_sentiment_ranking.png",
    )
    plot_market_fear_greed(
        sentiment_outputs["market_fear_greed_index"],
        FIGURE_DIR / "market_fear_greed_index.png",
    )

    fusion_outputs = build_fusion_outputs(
        outputs,
        fund_returns,
        fund_weights,
        sentiment_outputs["sector_sentiment_index"],
    )
    save_csv(fusion_outputs["fusion_fund_returns"], DATA_DIR / "fusion_fund_returns.csv")
    save_csv(fusion_outputs["fusion_fund_weights"], DATA_DIR / "fusion_fund_weights.csv")
    save_csv(fusion_outputs["fusion_comparison"], TABLE_DIR / "fusion_comparison.csv")
    save_csv(fusion_outputs["fusion_metrics"], TABLE_DIR / "fusion_metrics.csv")
    save_csv(fusion_outputs["fusion_diagnostics"], TABLE_DIR / "fusion_diagnostics.csv")

    plot_fusion_growth(
        fund_returns,
        fusion_outputs["fusion_fund_returns"],
        FIGURE_DIR / "fusion_growth_comparison.png",
    )
    plot_fusion_drawdown(
        fund_returns,
        fusion_outputs["fusion_fund_returns"],
        FIGURE_DIR / "fusion_drawdown_comparison.png",
    )

    copy_stage_aliases()
    write_output_index()

    print("\nSentiment and fusion outputs are ready for Part B reporting and app work.")
    print("Next steps: update the Streamlit app and draft the report.")


if __name__ == "__main__":
    main()
