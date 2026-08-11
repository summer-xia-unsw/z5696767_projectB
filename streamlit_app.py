"""NovaAlloc Streamlit dashboard for FINS5545 Project B.

The app is deliberately light: it reads precomputed CSV artifacts from
results/ and does not recompute portfolio optimisation or VADER sentiment.
"""

from __future__ import annotations

import pathlib

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = pathlib.Path(__file__).resolve().parent
DATA_DIR = ROOT / "results" / "data"
TABLE_DIR = ROOT / "results" / "tables"
FIGURE_DIR = ROOT / "results" / "figures" / "Redesign" / "png"
PDF_FIGURE_DIR = ROOT / "results" / "figures" / "Redesign" / "pdf"

REQUIRED_FILES = {
    "fund_returns": DATA_DIR / "fund_returns.csv",
    "fund_weights": DATA_DIR / "fund_weights.csv",
    "sector_sentiment": DATA_DIR / "sector_sentiment_index.csv",
    "performance": TABLE_DIR / "performance_metrics.csv",
}

OPTIONAL_FILES = {
    "latest_holdings": TABLE_DIR / "latest_holdings.csv",
    "market_sentiment": DATA_DIR / "market_fear_greed_index.csv",
    "sector_summary": TABLE_DIR / "sector_sentiment_summary.csv",
    "sentiment_coverage": TABLE_DIR / "sentiment_coverage_summary.csv",
    "fusion_returns": DATA_DIR / "fusion_fund_returns.csv",
    "fusion_comparison": TABLE_DIR / "fusion_comparison.csv",
    "fusion_diagnostics": TABLE_DIR / "fusion_diagnostics.csv",
}

REPORT_FIGURES = [
    {
        "stage": "02 Portfolios",
        "title": "Fund growth of USD 1",
        "png_file": "02_fund_growth_of_1.png",
        "pdf_file": "02_fund_growth_of_1.pdf",
        "role": "Compares the live wealth path of the 12 systematic funds.",
    },
    {
        "stage": "02 Portfolios",
        "title": "Risk-return map",
        "png_file": "02_fund_risk_return_scatter.png",
        "pdf_file": "02_fund_risk_return_scatter.pdf",
        "role": "Connects annualised return, volatility, universe, and method choice.",
    },
    {
        "stage": "02 Portfolios",
        "title": "Sharpe ratio ranking",
        "png_file": "02_fund_sharpe_barplot.png",
        "pdf_file": "02_fund_sharpe_barplot.pdf",
        "role": "Ranks funds by risk-adjusted performance for the report discussion.",
    },
    {
        "stage": "02 Portfolios",
        "title": "Combined fund drawdowns",
        "png_file": "02_combined_fund_drawdowns.png",
        "pdf_file": "02_combined_fund_drawdowns.pdf",
        "role": "Shows downside risk for Combined universe funds.",
    },
    {
        "stage": "02 Portfolios",
        "title": "Combined risk parity weights",
        "png_file": "02_combined_risk_parity_weights.png",
        "pdf_file": "02_combined_risk_parity_weights.pdf",
        "role": "Explains the time-varying allocation mechanism behind the product.",
    },
    {
        "stage": "03 Sentiment/Fusion",
        "title": "Sector sentiment index",
        "png_file": "03_sector_sentiment_index.png",
        "pdf_file": "03_sector_sentiment_index.pdf",
        "role": "Shows the VADER-based sector fear-greed signal through time.",
    },
    {
        "stage": "03 Sentiment/Fusion",
        "title": "Sector sentiment ranking",
        "png_file": "03_sector_sentiment_ranking.png",
        "pdf_file": "03_sector_sentiment_ranking.pdf",
        "role": "Summarises which sectors were relatively optimistic or cautious.",
    },
    {
        "stage": "03 Sentiment/Fusion",
        "title": "Market fear-greed index",
        "png_file": "03_market_fear_greed_index.png",
        "pdf_file": "03_market_fear_greed_index.pdf",
        "role": "Summarises broad headline tone on a 0-100 market index.",
    },
    {
        "stage": "03 Sentiment/Fusion",
        "title": "Fusion growth comparison",
        "png_file": "03_fusion_growth_comparison.png",
        "pdf_file": "03_fusion_growth_comparison.pdf",
        "role": "Compares base fund growth with the lagged sentiment tilt.",
    },
    {
        "stage": "03 Sentiment/Fusion",
        "title": "Fusion drawdown comparison",
        "png_file": "03_fusion_drawdown_comparison.png",
        "pdf_file": "03_fusion_drawdown_comparison.pdf",
        "role": "Shows whether the sentiment tilt improved downside control.",
    },
    {
        "stage": "04 App",
        "title": "App page-data map",
        "png_file": "04_app_page_data_map.png",
        "pdf_file": "04_app_page_data_map.pdf",
        "role": "Documents which app page reads which precomputed artifact.",
    },
    {
        "stage": "05 Report",
        "title": "Report asset-class weights",
        "png_file": "05_report_combined_asset_class_weights.png",
        "pdf_file": "05_report_combined_asset_class_weights.pdf",
        "role": "Supports the report explanation of Combined fund exposure.",
    },
    {
        "stage": "05 Report",
        "title": "Workflow and data-flow map",
        "png_file": "05_report_projectb_workflow_data_flow.png",
        "pdf_file": "05_report_projectb_workflow_data_flow.pdf",
        "role": "Shows how ETL, portfolios, sentiment, fusion, app, and report link together.",
    },
]

PALETTE = {
    "Equity": "#24536B",
    "Crypto": "#D0843D",
    "Combined": "#557A46",
    "Sentiment Tilt": "#8A5A44",
}

PAGES = ["Overview", "Funds", "Allocation", "Sentiment", "Fusion", "Method & Data Checks"]

DISPLAY_LABELS = {
    "artifact": "Artifact",
    "path": "Source path",
    "loaded": "Loaded",
    "rows": "Rows",
    "columns": "Columns",
    "fund_id": "Fund",
    "universe": "Universe",
    "method_label": "Method",
    "annualised_return": "Annualised return",
    "annualised_volatility": "Annualised volatility",
    "sharpe_ratio": "Sharpe ratio",
    "max_drawdown": "Max drawdown",
    "final_growth_of_1": "Final growth of $1",
    "average_turnover": "Average turnover",
    "ticker": "Ticker",
    "sector": "Sector",
    "asset_class": "Asset class",
    "weight": "Weight",
    "dollar_allocation": "Dollar allocation",
    "observations": "Observations",
    "mean_score_100": "Mean score (0-100)",
    "min_score_100": "Minimum score (0-100)",
    "max_score_100": "Maximum score (0-100)",
    "mean_ticker_coverage": "Mean ticker coverage",
    "ticker_days_with_news": "Ticker-days with news",
    "total_headlines": "Total headlines",
    "neutral_headline_share": "Neutral headline share",
    "model": "Model",
    "delta_annualised_return_vs_base": "Annualised return vs base",
    "delta_annualised_volatility_vs_base": "Volatility vs base",
    "delta_max_drawdown_vs_base": "Max drawdown vs base",
    "delta_sharpe_ratio_vs_base": "Sharpe ratio vs base",
    "delta_final_growth_of_1_vs_base": "Final growth vs base",
    "stage": "Stage",
    "title": "Figure",
    "png_exists": "PNG ready",
    "pdf_exists": "PDF ready",
    "png_path": "PNG path",
}

st.set_page_config(
    page_title="NovaAlloc | Systematic Funds",
    page_icon="NA",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.4rem; padding-bottom: 2.4rem;}
    .nova-hero {
        border: 1px solid #d9ded7;
        border-radius: 18px;
        padding: 1.2rem 1.35rem;
        background: linear-gradient(135deg, #f6f1e8 0%, #eef4ed 58%, #e7eff4 100%);
        margin-bottom: 1rem;
    }
    .nova-hero h1 {margin: 0; color: #183642; letter-spacing: -0.03em;}
    .nova-hero p {margin: 0.35rem 0 0 0; color: #46545a; font-size: 1.02rem;}
    .small-note {color: #657176; font-size: 0.86rem;}
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.85rem;
        margin: 1rem 0 1.2rem 0;
    }
    .kpi-card {
        background-color: #fbfaf6;
        border: 1px solid #e4dfd2;
        border-radius: 14px;
        padding: 0.85rem 0.95rem;
        min-height: 92px;
    }
    .kpi-label {
        color: #40464f;
        font-size: 0.92rem;
        margin-bottom: 0.55rem;
    }
    .kpi-value {
        color: #2f3440;
        font-size: 1.75rem;
        line-height: 1.12;
        letter-spacing: -0.03em;
        overflow-wrap: anywhere;
    }
    .kpi-sub {
        display: inline-block;
        margin-top: 0.48rem;
        padding: 0.18rem 0.5rem;
        border-radius: 999px;
        background: #e1f3e6;
        color: #10843d;
        font-size: 0.86rem;
    }
    .figure-note {
        border-left: 4px solid #24536B;
        background: #fbfaf6;
        padding: 0.75rem 0.9rem;
        color: #38484f;
        margin: 0.4rem 0 1rem 0;
    }
    .journey-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.85rem;
        margin: 0.75rem 0 1.2rem 0;
    }
    .journey-card {
        background: #ffffff;
        border: 1px solid #d9ded7;
        border-radius: 14px;
        padding: 0.9rem 0.95rem;
        min-height: 118px;
        box-shadow: 0 1px 0 rgba(24, 54, 66, 0.04);
    }
    .journey-step {
        color: #8A5A44;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    .journey-card h4 {
        margin: 0.35rem 0 0.35rem 0;
        color: #183642;
        font-size: 1.02rem;
    }
    .journey-card p {
        margin: 0;
        color: #526166;
        font-size: 0.9rem;
        line-height: 1.35;
    }
    .sidebar-note {
        color: #526166;
        font-size: 0.86rem;
        line-height: 1.35;
    }
    div[data-testid="stMetric"] {
        background-color: #fbfaf6;
        border: 1px solid #e4dfd2;
        border-radius: 14px;
        padding: 0.75rem 0.8rem;
    }
    @media (max-width: 1200px) {
        .kpi-grid {grid-template-columns: repeat(2, minmax(0, 1fr));}
        .journey-grid {grid-template-columns: repeat(2, minmax(0, 1fr));}
    }
    @media (max-width: 720px) {
        .kpi-grid {grid-template-columns: 1fr;}
        .journey-grid {grid-template-columns: 1fr;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=86_400, show_spinner="Loading precomputed NovaAlloc results...")
def load_results() -> dict[str, pd.DataFrame]:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required app artifacts: " + ", ".join(missing))

    frames: dict[str, pd.DataFrame] = {}
    for key, path in REQUIRED_FILES.items():
        frames[key] = pd.read_csv(path)
    for key, path in OPTIONAL_FILES.items():
        frames[key] = pd.read_csv(path) if path.exists() else pd.DataFrame()

    date_columns = [
        "date",
        "rebalance_date",
        "live_start_date",
        "live_end_date",
        "first_live_date",
        "last_live_date",
        "lagged_signal_date",
    ]
    for frame in frames.values():
        for col in date_columns:
            if col in frame.columns:
                frame[col] = pd.to_datetime(frame[col], errors="coerce")
    return frames


def pct(x: float | int | None, digits: int = 1) -> str:
    if x is None or pd.isna(x):
        return "n/a"
    return f"{x * 100:.{digits}f}%"


def num(x: float | int | None, digits: int = 2) -> str:
    if x is None or pd.isna(x):
        return "n/a"
    return f"{x:.{digits}f}"


def money(x: float | int | None) -> str:
    if x is None or pd.isna(x):
        return "n/a"
    return f"${x:,.0f}"


def compact_table(
    df: pd.DataFrame, percent_cols: list[str] | None = None, number_cols: list[str] | None = None
) -> pd.DataFrame:
    out = df.copy()
    percent_cols = percent_cols or []
    number_cols = number_cols or []
    for col in percent_cols:
        if col in out:
            out[col] = out[col].map(lambda v: pct(v, 1))
    for col in number_cols:
        if col in out:
            out[col] = out[col].map(lambda v: num(v, 2))
    return out


def display_label(column: str) -> str:
    return DISPLAY_LABELS.get(column, column.replace("_", " ").title())


def financial_display(
    df: pd.DataFrame,
    percent_cols: list[str] | None = None,
    number_cols: list[str] | None = None,
    money_cols: list[str] | None = None,
    integer_cols: list[str] | None = None,
) -> tuple[pd.DataFrame, dict[str, object]]:
    out = df.copy()
    percent_cols = percent_cols or []
    number_cols = number_cols or []
    money_cols = money_cols or []
    integer_cols = integer_cols or []
    column_config: dict[str, object] = {}

    for col in percent_cols:
        if col in out:
            out[col] = pd.to_numeric(out[col], errors="coerce") * 100
            label = display_label(col)
            column_config[label] = st.column_config.NumberColumn(label, format="%.1f%%")
    for col in number_cols:
        if col in out:
            out[col] = pd.to_numeric(out[col], errors="coerce")
            label = display_label(col)
            column_config[label] = st.column_config.NumberColumn(label, format="%.2f")
    for col in money_cols:
        if col in out:
            out[col] = pd.to_numeric(out[col], errors="coerce")
            label = display_label(col)
            column_config[label] = st.column_config.NumberColumn(label, format="$%.0f")
    for col in integer_cols:
        if col in out:
            out[col] = pd.to_numeric(out[col], errors="coerce")
            label = display_label(col)
            column_config[label] = st.column_config.NumberColumn(label, format="%d")

    out = out.rename(columns={col: display_label(col) for col in out.columns})
    return out, column_config


def render_financial_table(
    df: pd.DataFrame,
    percent_cols: list[str] | None = None,
    number_cols: list[str] | None = None,
    money_cols: list[str] | None = None,
    integer_cols: list[str] | None = None,
    hide_index: bool = True,
) -> None:
    table, column_config = financial_display(
        df,
        percent_cols=percent_cols,
        number_cols=number_cols,
        money_cols=money_cols,
        integer_cols=integer_cols,
    )
    st.dataframe(table, width="stretch", hide_index=hide_index, column_config=column_config)


def add_download(label: str, df: pd.DataFrame, file_name: str) -> None:
    st.download_button(
        label=label,
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=file_name,
        mime="text/csv",
    )


def relpath(path: pathlib.Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def report_figure_frame() -> pd.DataFrame:
    rows = []
    for figure in REPORT_FIGURES:
        png_path = FIGURE_DIR / figure["png_file"]
        pdf_path = PDF_FIGURE_DIR / figure["pdf_file"]
        rows.append(
            {
                **figure,
                "png_path": relpath(png_path),
                "pdf_path": relpath(pdf_path),
                "png_exists": png_path.exists(),
                "pdf_exists": pdf_path.exists(),
                "png_size_kb": round(png_path.stat().st_size / 1024, 1)
                if png_path.exists()
                else np.nan,
                "pdf_size_kb": round(pdf_path.stat().st_size / 1024, 1)
                if pdf_path.exists()
                else np.nan,
            }
        )
    return pd.DataFrame(rows)


def render_report_figure(figure: pd.Series, key_prefix: str) -> None:
    png_path = FIGURE_DIR / str(figure["png_file"])
    pdf_path = PDF_FIGURE_DIR / str(figure["pdf_file"])

    st.markdown(f"#### {figure['title']}")
    st.caption(f"{figure['stage']} | {figure['role']}")
    if png_path.exists():
        st.image(str(png_path), caption=str(figure["png_path"]), width="stretch")
    else:
        st.error(f"Missing PNG: {figure['png_path']}")

    c1, c2 = st.columns(2)
    if png_path.exists():
        c1.download_button(
            "Download PNG",
            data=png_path.read_bytes(),
            file_name=png_path.name,
            mime="image/png",
            key=f"{key_prefix}_png_{png_path.stem}",
        )
    if pdf_path.exists():
        c2.download_button(
            "Download PDF",
            data=pdf_path.read_bytes(),
            file_name=pdf_path.name,
            mime="application/pdf",
            key=f"{key_prefix}_pdf_{pdf_path.stem}",
        )


def metric_row(metrics: pd.DataFrame) -> None:
    fund_count = metrics["fund_id"].nunique()
    best_sharpe = metrics.loc[metrics["sharpe_ratio"].idxmax()]
    best_growth = metrics.loc[metrics["final_growth_of_1"].idxmax()]
    sample_start = pd.to_datetime(metrics["first_live_date"]).min().date()
    sample_end = pd.to_datetime(metrics["last_live_date"]).max().date()

    cards = [
        ("Investable funds", f"{fund_count}", ""),
        ("Best Sharpe ratio", num(best_sharpe["sharpe_ratio"], 2), str(best_sharpe["fund_id"])),
        (
            "Best final growth",
            f"{best_growth['final_growth_of_1']:.2f}x",
            str(best_growth["fund_id"]),
        ),
        ("OOS test window", f"{sample_start} to {sample_end}", "precomputed live sample"),
    ]
    html = ['<div class="kpi-grid">']
    for label, value, sub in cards:
        html.append('<div class="kpi-card">')
        html.append(f'<div class="kpi-label">{label}</div>')
        html.append(f'<div class="kpi-value">{value}</div>')
        if sub:
            html.append(f'<div class="kpi-sub">{sub}</div>')
        html.append("</div>")
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def growth_chart(fund_returns: pd.DataFrame, funds: list[str], title: str) -> go.Figure:
    data = fund_returns[fund_returns["fund_id"].isin(funds)].sort_values(["fund_id", "date"])
    fig = px.line(
        data,
        x="date",
        y="growth_of_1",
        color="fund_id",
        line_group="fund_id",
        title=title,
        labels={"date": "Date", "growth_of_1": "Growth of $1", "fund_id": "Fund"},
    )
    fig.update_layout(
        hovermode="x unified", legend_title_text="Fund", margin=dict(l=20, r=20, t=55, b=20)
    )
    return fig


def drawdown_chart(fund_returns: pd.DataFrame, funds: list[str], title: str) -> go.Figure:
    data = fund_returns[fund_returns["fund_id"].isin(funds)].sort_values(["fund_id", "date"])
    fig = px.line(
        data,
        x="date",
        y="drawdown",
        color="fund_id",
        line_group="fund_id",
        title=title,
        labels={"date": "Date", "drawdown": "Drawdown", "fund_id": "Fund"},
    )
    fig.update_layout(
        hovermode="x unified", yaxis_tickformat=".0%", margin=dict(l=20, r=20, t=55, b=20)
    )
    return fig


def risk_return_chart(metrics: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        metrics,
        x="annualised_volatility",
        y="annualised_return",
        color="universe",
        size="final_growth_of_1",
        hover_name="fund_id",
        text="method_label",
        color_discrete_map=PALETTE,
        labels={
            "annualised_volatility": "Annualised volatility",
            "annualised_return": "Annualised return",
            "universe": "Universe",
            "method_label": "Method",
        },
        title="Risk-return map for out-of-sample funds",
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(
        xaxis_tickformat=".0%",
        yaxis_tickformat=".0%",
        legend_title_text="Universe",
        margin=dict(l=20, r=20, t=55, b=20),
    )
    return fig


def holdings_chart(holdings: pd.DataFrame, fund_id: str) -> go.Figure:
    data = holdings[holdings["fund_id"] == fund_id].copy()
    data = data.sort_values("weight", ascending=False).head(15)
    fig = px.bar(
        data.sort_values("weight"),
        x="weight",
        y="ticker",
        color="asset_class",
        orientation="h",
        color_discrete_map=PALETTE,
        title="Top current holdings",
        labels={"weight": "Portfolio weight", "ticker": "Ticker", "asset_class": "Asset class"},
        hover_data=["sector"],
    )
    fig.update_layout(xaxis_tickformat=".0%", margin=dict(l=20, r=20, t=55, b=20))
    return fig


def allocation_series(fund_returns: pd.DataFrame, weights: dict[str, float]) -> pd.DataFrame:
    selected = list(weights.keys())
    pivot = fund_returns[fund_returns["fund_id"].isin(selected)].pivot_table(
        index="date", columns="fund_id", values="daily_return", aggfunc="mean"
    )
    pivot = pivot.dropna(how="any")
    if pivot.empty:
        return pd.DataFrame()
    w = pd.Series(weights).reindex(pivot.columns).fillna(0.0)
    daily = pivot.mul(w, axis=1).sum(axis=1)
    out = pd.DataFrame({"date": daily.index, "daily_return": daily.values})
    out["growth_of_1"] = (1.0 + out["daily_return"]).cumprod()
    out["drawdown"] = out["growth_of_1"] / out["growth_of_1"].cummax() - 1.0
    return out


def allocation_metrics(series: pd.DataFrame) -> dict[str, float]:
    if series.empty:
        return {}
    r = series["daily_return"].dropna()
    final_growth = float(series["growth_of_1"].iloc[-1])
    ann_return = final_growth ** (252 / len(r)) - 1.0 if len(r) > 0 and final_growth > 0 else np.nan
    ann_vol = float(r.std(ddof=1) * np.sqrt(252)) if len(r) > 1 else np.nan
    sharpe = ann_return / ann_vol if ann_vol and ann_vol > 0 else np.nan
    return {
        "annualised_return": ann_return,
        "annualised_volatility": ann_vol,
        "sharpe_ratio": sharpe,
        "max_drawdown": float(series["drawdown"].min()),
        "final_growth_of_1": final_growth,
    }


def sentiment_line(sector_sentiment: pd.DataFrame, sectors: list[str], rolling: int) -> go.Figure:
    data = sector_sentiment[sector_sentiment["sector"].isin(sectors)].copy()
    data = data.sort_values(["sector", "date"])
    data["rolling_score"] = data.groupby("sector")["score_100"].transform(
        lambda s: s.rolling(rolling, min_periods=max(3, rolling // 4)).mean()
    )
    fig = px.line(
        data,
        x="date",
        y="rolling_score",
        color="sector",
        title=f"Sector sentiment index, {rolling}-day rolling average",
        labels={"date": "Date", "rolling_score": "Fear/greed score (0-100)", "sector": "Sector"},
    )
    fig.add_hline(y=50, line_dash="dash", line_color="#6f777b", annotation_text="Neutral")
    fig.update_layout(hovermode="x unified", margin=dict(l=20, r=20, t=55, b=20))
    return fig


def market_sentiment_chart(market: pd.DataFrame, rolling: int) -> go.Figure:
    data = market.sort_values("date").copy()
    data["rolling_score"] = (
        data["score_100"].rolling(rolling, min_periods=max(3, rolling // 4)).mean()
    )
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=data["date"],
            y=data["score_100"],
            name="Daily score",
            line=dict(color="#c8b89f", width=1),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=data["date"],
            y=data["rolling_score"],
            name=f"{rolling}-day average",
            line=dict(color="#8A5A44", width=2.5),
        )
    )
    fig.add_hline(y=50, line_dash="dash", line_color="#6f777b", annotation_text="Neutral")
    fig.update_layout(
        title="Market news fear/greed index",
        xaxis_title="Date",
        yaxis_title="Fear/greed score (0-100)",
        hovermode="x unified",
        margin=dict(l=20, r=20, t=55, b=20),
    )
    return fig


def show_overview(frames: dict[str, pd.DataFrame]) -> None:
    metrics = frames["performance"]
    fund_returns = frames["fund_returns"]
    sector_sentiment = frames["sector_sentiment"]

    st.markdown(
        """
        <div class="nova-hero">
          <h1>NovaAlloc</h1>
          <p>
            A systematic multi-asset allocation prototype that connects fund performance,
            portfolio construction, and news sentiment evidence.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    metric_row(metrics)

    st.subheader("Start here")
    st.markdown(
        """
        <div class="journey-grid">
          <div class="journey-card">
            <div class="journey-step">Step 1</div>
            <h4>Compare funds</h4>
            <p>
              Rank the 12 systematic funds by return, risk, Sharpe ratio,
              drawdown, and holdings.
            </p>
          </div>
          <div class="journey-card">
            <div class="journey-step">Step 2</div>
            <h4>Build allocation</h4>
            <p>
              Combine selected funds and inspect the historical value path
              of a hypothetical portfolio.
            </p>
          </div>
          <div class="journey-card">
            <div class="journey-step">Step 3</div>
            <h4>Read sentiment</h4>
            <p>
              Use sector and market headline sentiment as context for risk discussion,
              not as a return guarantee.
            </p>
          </div>
          <div class="journey-card">
            <div class="journey-step">Step 4</div>
            <h4>Check evidence</h4>
            <p>
              Review whether a lagged sentiment tilt improved the base fund before
              treating it as product logic.
            </p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    b1, b2, b3, b4 = st.columns(4)
    if b1.button("Open fund comparison", use_container_width=True):
        st.session_state["pending_page"] = "Funds"
        st.rerun()
    if b2.button("Build allocation", use_container_width=True):
        st.session_state["pending_page"] = "Allocation"
        st.rerun()
    if b3.button("Read sentiment", use_container_width=True):
        st.session_state["pending_page"] = "Sentiment"
        st.rerun()
    if b4.button("Review fusion test", use_container_width=True):
        st.session_state["pending_page"] = "Fusion"
        st.rerun()

    left, right = st.columns([1.25, 1])
    with left:
        top_funds = metrics.sort_values("sharpe_ratio", ascending=False).head(6)["fund_id"].tolist()
        st.plotly_chart(
            growth_chart(fund_returns, top_funds, "Top funds by Sharpe: growth of $1"),
            width="stretch",
        )
    with right:
        st.plotly_chart(risk_return_chart(metrics), width="stretch")

    st.subheader("How to read the product")
    c1, c2, c3 = st.columns(3)
    c1.info("Compare funds by return, risk, Sharpe, drawdown, and holdings before choosing a fund.")
    c2.info("Use the allocation lab to combine funds and inspect the combined historical path.")
    c3.info(
        "Use sentiment analytics as context; the fusion test measures whether "
        "a simple sentiment tilt helped."
    )

    latest_sentiment_date = sector_sentiment["date"].max().date()
    st.caption(
        f"Latest sector sentiment observation: {latest_sentiment_date}. "
        "Portfolio results are based on the saved out-of-sample evidence set."
    )


def show_funds(frames: dict[str, pd.DataFrame]) -> None:
    metrics = frames["performance"].copy()
    fund_returns = frames["fund_returns"].copy()
    holdings = frames["latest_holdings"].copy()

    st.subheader("Fund comparison")
    st.caption("All performance is out of sample. Weights are estimated before each live month.")

    universes = sorted(metrics["universe"].unique())
    methods = sorted(metrics["method_label"].unique())
    c1, c2 = st.columns(2)
    selected_universes = c1.multiselect("Universe", universes, default=universes)
    selected_methods = c2.multiselect("Method", methods, default=methods)
    filtered = metrics[
        metrics["universe"].isin(selected_universes)
        & metrics["method_label"].isin(selected_methods)
    ].copy()

    if filtered.empty:
        st.warning("No funds match the selected filters.")
        return

    display_cols = [
        "fund_id",
        "universe",
        "method_label",
        "annualised_return",
        "annualised_volatility",
        "sharpe_ratio",
        "max_drawdown",
        "final_growth_of_1",
        "average_turnover",
    ]
    table = filtered[display_cols].sort_values("sharpe_ratio", ascending=False)
    render_financial_table(
        table,
        percent_cols=[
            "annualised_return",
            "annualised_volatility",
            "max_drawdown",
            "average_turnover",
        ],
        number_cols=["sharpe_ratio", "final_growth_of_1"],
    )
    add_download("Download filtered metrics", table, "novaalloc_filtered_metrics.csv")

    selected_funds = filtered["fund_id"].tolist()
    st.plotly_chart(
        growth_chart(fund_returns, selected_funds, "Filtered funds: growth of $1"), width="stretch"
    )
    st.plotly_chart(
        drawdown_chart(fund_returns, selected_funds, "Filtered funds: drawdown"), width="stretch"
    )

    st.subheader("Fund fact sheet")
    default_idx = int(filtered["sharpe_ratio"].idxmax())
    default_fund = metrics.loc[default_idx, "fund_id"]
    fund_id = st.selectbox(
        "Select a fund",
        filtered["fund_id"].tolist(),
        index=filtered["fund_id"].tolist().index(default_fund),
    )
    fund_metric = metrics[metrics["fund_id"] == fund_id].iloc[0]
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Annualised return", pct(fund_metric["annualised_return"], 1))
    m2.metric("Annualised volatility", pct(fund_metric["annualised_volatility"], 1))
    m3.metric("Sharpe ratio", num(fund_metric["sharpe_ratio"], 2))
    m4.metric("Max drawdown", pct(fund_metric["max_drawdown"], 1))
    m5.metric("Final growth", f"{fund_metric['final_growth_of_1']:.2f}x")

    left, right = st.columns([1.1, 0.9])
    with left:
        st.plotly_chart(
            growth_chart(fund_returns, [fund_id], f"{fund_id}: growth of $1"), width="stretch"
        )
        st.plotly_chart(
            drawdown_chart(fund_returns, [fund_id], f"{fund_id}: drawdown"), width="stretch"
        )
    with right:
        if not holdings.empty:
            st.plotly_chart(holdings_chart(holdings, fund_id), width="stretch")
            latest = (
                holdings[holdings["fund_id"] == fund_id]
                .sort_values("weight", ascending=False)
                .head(12)
            )
            render_financial_table(
                latest[["ticker", "sector", "asset_class", "weight"]], percent_cols=["weight"]
            )
        else:
            st.info("Latest holdings table is not available.")


def show_allocation(frames: dict[str, pd.DataFrame]) -> None:
    metrics = frames["performance"].copy()
    fund_returns = frames["fund_returns"].copy()

    st.subheader("Allocation lab")
    st.caption(
        "Build a hypothetical allocation across NovaAlloc funds using "
        "precomputed out-of-sample fund returns."
    )

    candidate_funds = metrics.sort_values("sharpe_ratio", ascending=False)["fund_id"].tolist()
    default_funds = candidate_funds[:3]
    selected = st.multiselect("Choose funds to combine", candidate_funds, default=default_funds)
    if not selected:
        st.warning("Select at least one fund.")
        return

    if st.button("Reset to equal starting weights", use_container_width=False):
        for fund in selected:
            st.session_state[f"alloc_weight_{fund}"] = int(100 / len(selected))
        st.rerun()

    raw_weights = {}
    with st.form("allocation_form"):
        total_capital = st.number_input(
            "Initial investment amount ($)",
            min_value=1000,
            max_value=10_000_000,
            value=100_000,
            step=5000,
        )
        st.write("Allocation weights")
        cols = st.columns(min(3, len(selected)))
        for i, fund in enumerate(selected):
            raw_weights[fund] = cols[i % len(cols)].slider(
                fund,
                0,
                100,
                int(100 / len(selected)),
                1,
                key=f"alloc_weight_{fund}",
            )
        submitted = st.form_submit_button("Apply allocation", use_container_width=True)

    total_weight = sum(raw_weights.values())
    if total_weight <= 0:
        st.warning("Total allocation weight must be greater than zero.")
        return
    if submitted:
        st.success("Allocation applied.")
    if total_weight != 100:
        st.info(
            f"Input weights total {total_weight}%. NovaAlloc normalises them "
            "to 100% for the portfolio test."
        )
    weights = {fund: value / total_weight for fund, value in raw_weights.items()}

    allocation = allocation_series(fund_returns, weights)
    if allocation.empty:
        st.warning("Selected funds do not share a common return window.")
        return
    stats = allocation_metrics(allocation)
    a1, a2, a3, a4, a5 = st.columns(5)
    a1.metric("Normalised weight total", "100%")
    a2.metric("Annualised return", pct(stats.get("annualised_return"), 1))
    a3.metric("Annualised volatility", pct(stats.get("annualised_volatility"), 1))
    a4.metric("Sharpe ratio", num(stats.get("sharpe_ratio"), 2))
    a5.metric("Max drawdown", pct(stats.get("max_drawdown"), 1))

    allocation["portfolio_value"] = allocation["growth_of_1"] * total_capital
    fig = px.line(
        allocation,
        x="date",
        y="portfolio_value",
        title="Hypothetical allocation value",
        labels={"date": "Date", "portfolio_value": "Portfolio value ($)"},
    )
    fig.update_layout(hovermode="x unified", margin=dict(l=20, r=20, t=55, b=20))
    st.plotly_chart(fig, width="stretch")

    weight_table = pd.DataFrame(
        {
            "fund_id": list(weights.keys()),
            "weight": list(weights.values()),
            "dollar_allocation": [w * total_capital for w in weights.values()],
        }
    )
    render_financial_table(
        weight_table,
        percent_cols=["weight"],
        money_cols=["dollar_allocation"],
    )
    add_download("Download allocation path", allocation, "novaalloc_allocation_path.csv")


def show_sentiment(frames: dict[str, pd.DataFrame]) -> None:
    sector_sentiment = frames["sector_sentiment"].copy()
    market = frames["market_sentiment"].copy()
    sector_summary = frames["sector_summary"].copy()
    coverage = frames["sentiment_coverage"].copy()

    st.subheader("News sentiment analytics")
    st.caption(
        "Historical headline sentiment is used as market context. "
        "It is not a guarantee of future return."
    )

    latest = sector_sentiment.sort_values("date").groupby("sector", as_index=False).tail(1)
    latest_date = sector_sentiment["date"].max().date()
    avg_score = latest["score_100"].mean()
    total_headlines = int(sector_sentiment["total_headlines"].sum())
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Latest sector date", str(latest_date))
    s2.metric("Latest average score", num(avg_score, 1))
    s3.metric("Total scored headlines", f"{total_headlines:,}")
    s4.metric("Covered sectors", f"{sector_sentiment['sector'].nunique()}")

    sectors = sorted(sector_sentiment["sector"].dropna().unique())
    selected = st.multiselect("Sectors", sectors, default=sectors)
    rolling = st.slider("Rolling average window (trading days)", 5, 63, 21, 1)

    if selected:
        st.plotly_chart(sentiment_line(sector_sentiment, selected, rolling), width="stretch")
    if not market.empty:
        st.plotly_chart(market_sentiment_chart(market, rolling), width="stretch")

    c1, c2 = st.columns(2)
    with c1:
        if not sector_summary.empty:
            st.write("Average sector sentiment")
            show = sector_summary.sort_values("mean_score_100", ascending=False)
            render_financial_table(
                show[
                    [
                        "sector",
                        "observations",
                        "mean_score_100",
                        "min_score_100",
                        "max_score_100",
                        "mean_ticker_coverage",
                    ]
                ],
                percent_cols=["mean_ticker_coverage"],
                number_cols=["mean_score_100", "min_score_100", "max_score_100"],
                integer_cols=["observations"],
            )
    with c2:
        if not coverage.empty:
            st.write("News coverage by sector")
            show = coverage.sort_values("total_headlines", ascending=False)
            render_financial_table(
                show[
                    [
                        "sector",
                        "ticker_days_with_news",
                        "total_headlines",
                        "mean_score_100",
                        "neutral_headline_share",
                    ]
                ],
                percent_cols=["neutral_headline_share"],
                number_cols=["mean_score_100"],
                integer_cols=["ticker_days_with_news", "total_headlines"],
            )


def show_fusion(frames: dict[str, pd.DataFrame]) -> None:
    fund_returns = frames["fund_returns"].copy()
    fusion_returns = frames["fusion_returns"].copy()
    comparison = frames["fusion_comparison"].copy()
    diagnostics = frames["fusion_diagnostics"].copy()

    st.subheader("Fusion check: base fund versus sentiment tilt")
    st.caption(
        "The sentiment signal is lagged before trading. "
        "A negative result is still informative for product design."
    )

    if comparison.empty or fusion_returns.empty:
        st.info("Fusion outputs are not available.")
        return

    display = comparison.copy()
    render_financial_table(
        display,
        percent_cols=[
            "annualised_return",
            "annualised_volatility",
            "max_drawdown",
            "delta_annualised_return_vs_base",
            "delta_annualised_volatility_vs_base",
            "delta_max_drawdown_vs_base",
        ],
        number_cols=[
            "sharpe_ratio",
            "final_growth_of_1",
            "delta_sharpe_ratio_vs_base",
            "delta_final_growth_of_1_vs_base",
        ],
    )

    base_id = comparison.loc[comparison["model"] == "Base", "fund_id"].iloc[0]
    tilted_id = comparison.loc[comparison["model"] != "Base", "fund_id"].iloc[0]
    base = fund_returns[fund_returns["fund_id"] == base_id][
        ["date", "fund_id", "growth_of_1", "drawdown"]
    ]
    tilted = fusion_returns[["date", "fund_id", "growth_of_1", "drawdown"]]
    combined = pd.concat([base, tilted], ignore_index=True)

    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            growth_chart(combined, [base_id, tilted_id], "Base vs sentiment tilt: growth of $1"),
            width="stretch",
        )
    with right:
        st.plotly_chart(
            drawdown_chart(combined, [base_id, tilted_id], "Base vs sentiment tilt: drawdown"),
            width="stretch",
        )

    if not diagnostics.empty:
        st.write("Fusion diagnostics")
        render_financial_table(diagnostics, integer_cols=["lag_violations"])
        lag = int(diagnostics["lag_violations"].iloc[0]) if "lag_violations" in diagnostics else 0
        if lag == 0:
            st.success("Timing check passed: the tilt uses prior sentiment only.")
        else:
            st.warning(f"Timing check needs review: {lag} lag issue(s) detected.")

    base_sharpe = comparison.loc[comparison["model"] == "Base", "sharpe_ratio"].iloc[0]
    tilt_sharpe = comparison.loc[comparison["model"] != "Base", "sharpe_ratio"].iloc[0]
    if tilt_sharpe < base_sharpe:
        st.warning(
            "The sentiment tilt reduced Sharpe in this sample. That does not invalidate "
            "the sentiment index; it shows that this simple tilt rule needs refinement "
            "before being marketed as return-enhancing."
        )
    else:
        st.success("The sentiment tilt improved Sharpe in this sample.")


def show_report_figure_audit() -> None:
    figures = report_figure_frame()

    missing = figures[~figures["png_exists"] | ~figures["pdf_exists"]]
    if missing.empty:
        st.success("All redesigned PNG and PDF files are available.")
    else:
        st.warning("Some redesigned figure files are missing. Check the manifest below.")

    render_financial_table(figures[["stage", "title", "png_exists", "pdf_exists", "png_path"]])

    preview = st.selectbox(
        "Optional preview",
        ["No preview", *figures["title"].tolist()],
        help="Use this only when checking that the written report figure exports still exist.",
    )
    if preview != "No preview":
        figure = figures[figures["title"] == preview].iloc[0]
        render_report_figure(figure, key_prefix="data_health_preview")


def show_data_health(frames: dict[str, pd.DataFrame]) -> None:
    st.subheader("Method and data checks")
    st.caption(
        "This page is mainly for markers and reproducibility review. "
        "It confirms which saved evidence files power the live dashboard."
    )
    rows = []
    for key, path in {**REQUIRED_FILES, **OPTIONAL_FILES}.items():
        frame = frames.get(key, pd.DataFrame())
        rows.append(
            {
                "artifact": key,
                "path": str(path.relative_to(ROOT)),
                "loaded": path.exists(),
                "rows": len(frame),
                "columns": len(frame.columns) if not frame.empty else 0,
            }
        )
    render_financial_table(pd.DataFrame(rows), integer_cols=["rows", "columns"])
    with st.expander("Written report figure exports", expanded=False):
        st.caption(
            "These PNG/PDF files are static visuals used by the written report. "
            "They are kept here for reproducibility checks, not as a primary "
            "investor workflow page."
        )
        show_report_figure_audit()
    st.info(
        "The deployed dashboard is intentionally lightweight: it reads saved evidence "
        "files and does not rerun portfolio backtests or sentiment scoring during "
        "a user session."
    )


def main() -> None:
    try:
        frames = load_results()
    except Exception as exc:
        st.error(str(exc))
        st.stop()

    if "pending_page" in st.session_state:
        st.session_state["page"] = st.session_state.pop("pending_page")
    if "page" not in st.session_state:
        st.session_state["page"] = "Overview"

    st.sidebar.title("NovaAlloc")
    st.sidebar.caption("Systematic funds and news sentiment evidence")
    st.sidebar.markdown("**Data:** validated 2020-2023 fund and news dataset")
    st.sidebar.markdown("**Evidence:** walk-forward out-of-sample tests")
    st.sidebar.markdown("**Status:** live academic prototype")
    st.sidebar.divider()
    page = st.sidebar.radio(
        "Navigation",
        PAGES,
        index=0,
        key="page",
    )

    if page == "Overview":
        show_overview(frames)
    elif page == "Funds":
        show_funds(frames)
    elif page == "Allocation":
        show_allocation(frames)
    elif page == "Sentiment":
        show_sentiment(frames)
    elif page == "Fusion":
        show_fusion(frames)
    elif page == "Method & Data Checks":
        show_data_health(frames)


if __name__ == "__main__":
    main()
