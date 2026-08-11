"""Create the remaining report-ready redesigned figures for ProjectB."""
from __future__ import annotations

from pathlib import Path
import textwrap

import matplotlib.dates as mdates
import matplotlib.lines as mlines
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter, MultipleLocator

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "results" / "data"
TABLE_DIR = ROOT / "results" / "tables"
REDESIGN_DIR = ROOT / "results" / "figures" / "Redesign"
PNG_DIR = REDESIGN_DIR / "png"
PDF_DIR = REDESIGN_DIR / "pdf"

FT_BG = "#fff1e5"
PANEL_BG = "#fff7ef"
GRID = "#d7c8b4"
TEXT = "#33302e"
MUTED = "#6b6258"
LINE = "#9b8c78"

UNIVERSE_COLORS = {"Equity": "#2f6f9f", "Combined": "#557A46", "Crypto": "#D9822B"}
METHOD_COLORS = {
    "Equal Weight": "#2f6f9f",
    "Risk Parity": "#c9472c",
    "Minimum Variance": "#557A46",
    "Maximum Sharpe": "#D9822B",
    "Sentiment Tilt": "#c9472c",
}
METHOD_SHORT = {
    "Equal Weight": "EW",
    "Risk Parity": "RP",
    "Minimum Variance": "Min Var",
    "Maximum Sharpe": "Max Shp",
    "Sentiment Tilt": "Tilt",
}
SECTOR_COLORS = {
    "Comm": "#355C7D",
    "Consumer": "#6C8EAD",
    "Energy": "#B84A3A",
    "Financials": "#7A6FA8",
    "Healthcare": "#9A6A5E",
    "Industrials": "#C77DBB",
    "Materials": "#8B8D84",
    "RealEstate": "#B9B93B",
    "Tech": "#37A6A6",
    "Utilities": "#557A46",
    "Crypto": "#D9822B",
}


def configure_style() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "axes.titlesize": 13,
        "axes.labelsize": 9.5,
        "xtick.labelsize": 8.3,
        "ytick.labelsize": 8.3,
    })


def ensure_dirs() -> None:
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)


def percent_axis(value: float, _pos: int) -> str:
    return f"{value:.0%}"


def score_axis(value: float, _pos: int) -> str:
    return f"{value:.0f}"


def dollar_axis(value: float, _pos: int) -> str:
    return f"${value:.2f}" if value < 1.5 else f"${value:.1f}"


def style_axis(ax: plt.Axes, grid_axis: str = "x") -> None:
    ax.set_facecolor(PANEL_BG)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(LINE)
    ax.tick_params(axis="both", colors=TEXT, length=0)
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.75, alpha=0.68)


def save_figure(fig: plt.Figure, stem: str) -> None:
    ensure_dirs()
    png_path = PNG_DIR / f"{stem}.png"
    pdf_path = PDF_DIR / f"{stem}.pdf"
    fig.savefig(png_path, facecolor=fig.get_facecolor(), bbox_inches="tight")
    fig.savefig(pdf_path, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {png_path}")
    print(f"Saved {pdf_path}")


def add_source_note(fig: plt.Figure, source: str, note: str) -> None:
    fig.text(0.055, 0.055, source, fontsize=8.0, color=MUTED)
    fig.text(0.055, 0.031, note, fontsize=8.0, color=MUTED)


def make_sharpe_barplot() -> None:
    data = pd.read_csv(TABLE_DIR / "performance_metrics.csv").sort_values("sharpe_ratio")
    data["display"] = data["universe"] + " " + data["method_label"].map(METHOD_SHORT)
    colors = data["universe"].map(UNIVERSE_COLORS)
    fig = plt.figure(figsize=(12.2, 6.7), dpi=220, facecolor=FT_BG)
    grid = fig.add_gridspec(1, 2, width_ratios=[4.35, 1.85], wspace=0.08)
    ax = fig.add_subplot(grid[0, 0])
    table_ax = fig.add_subplot(grid[0, 1])
    style_axis(ax, "x")
    table_ax.set_facecolor(FT_BG)
    y = range(len(data))
    ax.barh(y, data["sharpe_ratio"], color=colors, height=0.62, alpha=0.95)
    ax.set_yticks(list(y))
    ax.set_yticklabels(data["display"])
    ax.set_xlim(0, 0.86)
    ax.xaxis.set_major_locator(MultipleLocator(0.1))
    ax.axvline(0.5, color=LINE, linewidth=0.9, linestyle=(0, (4, 4)))
    ax.text(0.505, len(data) - 0.8, "Sharpe 0.50", fontsize=8, color=MUTED, va="center")
    ax.set_xlabel("Sharpe ratio")
    ax.set_ylabel("")
    for idx, row in data.reset_index(drop=True).iterrows():
        ax.text(row["sharpe_ratio"] + 0.012, idx, f"{row['sharpe_ratio']:.2f}", fontsize=8.0, va="center", color=TEXT)
    fig.text(0.055, 0.955, "Sharpe ranking: diversified funds lead the scorecard", fontsize=18, fontweight="bold", color=TEXT)
    fig.text(0.055, 0.915, "Out-of-sample Sharpe ratio by fund, Jan 2021-Dec 2023. Higher values indicate better return per unit of volatility.", fontsize=10.5, color=MUTED)
    table_ax.axis("off")
    ranked = data.sort_values("sharpe_ratio", ascending=False).reset_index(drop=True)
    top = ranked.iloc[0]
    bottom = ranked.iloc[-1]
    table_ax.text(0.0, 0.965, "What matters", fontsize=12, fontweight="bold", color=TEXT, transform=table_ax.transAxes)
    table_ax.plot([0.0, 0.98], [0.93, 0.93], color=LINE, linewidth=0.9)
    table_ax.text(0.0, 0.875, f"Best: {top['display']}  {top['sharpe_ratio']:.2f}", fontsize=9.2, fontweight="bold", color=UNIVERSE_COLORS[str(top["universe"])], transform=table_ax.transAxes)
    table_ax.text(0.0, 0.835, f"Worst: {bottom['display']}  {bottom['sharpe_ratio']:.2f}", fontsize=9.0, fontweight="bold", color=UNIVERSE_COLORS[str(bottom["universe"])], transform=table_ax.transAxes)
    table_ax.text(0.0, 0.755, "Top five funds", fontsize=8.7, fontweight="bold", color=TEXT, transform=table_ax.transAxes)
    table_ax.plot([0.0, 0.98], [0.725, 0.725], color=LINE, linewidth=0.8)
    for i, row in ranked.head(5).iterrows():
        y_pos = 0.675 - i * 0.075
        table_ax.text(0.0, y_pos, row["display"], fontsize=8.0, color=UNIVERSE_COLORS[str(row["universe"])], transform=table_ax.transAxes)
        table_ax.text(0.96, y_pos, f"{row['sharpe_ratio']:.2f}", fontsize=8.0, color=TEXT, ha="right", transform=table_ax.transAxes)
        table_ax.plot([0.0, 0.98], [y_pos - 0.028, y_pos - 0.028], color="#e0d2bd", linewidth=0.55)
    table_ax.text(0.0, 0.23, "Read-through", fontsize=9.2, fontweight="bold", color=TEXT, transform=table_ax.transAxes)
    table_ax.text(0.0, 0.09, "The best risk-adjusted funds are not the highest-return crypto funds. Equity EW and Combined RP dominate because volatility and drawdown remain controlled.", fontsize=8.1, color="#4f4942", linespacing=1.22, wrap=True, transform=table_ax.transAxes)
    add_source_note(fig, "Source: NovaAlloc results/tables/performance_metrics.csv.", "Note: Sharpe ratios are annualised from daily out-of-sample returns and use a zero risk-free rate.")
    fig.subplots_adjust(left=0.19, right=0.965, top=0.865, bottom=0.16)
    save_figure(fig, "02_fund_sharpe_barplot")


def make_sector_sentiment_index() -> None:
    data = pd.read_csv(DATA_DIR / "sector_sentiment_index.csv", parse_dates=["date"])
    pivot = data.pivot_table(index="date", columns="sector", values="score_100", aggfunc="mean").sort_index()
    smooth = pivot.rolling(21, min_periods=5).mean()
    summary = pd.read_csv(TABLE_DIR / "sector_sentiment_summary.csv")
    sectors = summary.sort_values("mean_score_100", ascending=False)["sector"].tolist()
    y_min = max(48, float(smooth.quantile(0.02).min()) - 1.0)
    y_max = min(70, float(smooth.quantile(0.98).max()) + 1.0)
    fig, axes = plt.subplots(5, 2, figsize=(12.2, 8.6), dpi=220, facecolor=FT_BG, sharex=True, sharey=True)
    axes = axes.ravel()
    for ax, sector in zip(axes, sectors):
        style_axis(ax, "y")
        ax.plot(smooth.index, smooth[sector], color=SECTOR_COLORS.get(sector, "#666666"), linewidth=1.45)
        ax.axhline(50, color=LINE, linewidth=0.75, linestyle=(0, (4, 4)))
        ax.set_ylim(y_min, y_max)
        latest = smooth[sector].dropna().iloc[-1]
        mean = summary.loc[summary["sector"].eq(sector), "mean_score_100"].iloc[0]
        ax.text(0.02, 0.82, f"{sector}  latest {latest:.1f}", fontsize=8.4, fontweight="bold", color=SECTOR_COLORS.get(sector, TEXT), transform=ax.transAxes)
        ax.text(0.02, 0.68, f"mean {mean:.1f}", fontsize=7.2, color=MUTED, transform=ax.transAxes)
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.yaxis.set_major_formatter(FuncFormatter(score_axis))
    for ax in axes[::2]:
        ax.set_ylabel("Score")
    for ax in axes[-2:]:
        ax.set_xlabel("Date")
    fig.text(0.055, 0.965, "Sector sentiment: broad positive tone with sector-level dispersion", fontsize=17.5, fontweight="bold", color=TEXT)
    fig.text(0.055, 0.935, "21-day rolling finance-VADER fear/greed score, 0-100. Small multiples replace the unreadable ten-line plot.", fontsize=10.2, color=MUTED)
    add_source_note(fig, "Source: NovaAlloc results/data/sector_sentiment_index.csv.", "Note: 50 is neutral. Scores above 50 indicate greed/positive news tone; below 50 indicates fear/negative news tone.")
    fig.subplots_adjust(left=0.07, right=0.97, top=0.885, bottom=0.12, hspace=0.25, wspace=0.08)
    save_figure(fig, "03_sector_sentiment_index")


def make_sector_sentiment_ranking() -> None:
    data = pd.read_csv(TABLE_DIR / "sector_sentiment_summary.csv").sort_values("mean_score_100")
    fig = plt.figure(figsize=(11.2, 6.45), dpi=220, facecolor=FT_BG)
    grid = fig.add_gridspec(1, 2, width_ratios=[4.1, 1.75], wspace=0.08)
    ax = fig.add_subplot(grid[0, 0])
    table_ax = fig.add_subplot(grid[0, 1])
    style_axis(ax, "x")
    y = range(len(data))
    colors = [SECTOR_COLORS.get(s, "#666666") for s in data["sector"]]
    ax.hlines(y, 50, data["mean_score_100"], color=colors, linewidth=4.0, alpha=0.82)
    ax.scatter(data["mean_score_100"], y, s=86, color=colors, edgecolor=PANEL_BG, linewidth=1.0, zorder=3)
    ax.axvline(50, color=LINE, linewidth=0.9, linestyle=(0, (4, 4)))
    ax.set_yticks(list(y))
    ax.set_yticklabels(data["sector"])
    ax.set_xlim(49, 61.5)
    ax.xaxis.set_major_locator(MultipleLocator(2))
    ax.set_xlabel("Mean fear/greed score, 0-100")
    for idx, row in data.reset_index(drop=True).iterrows():
        ax.text(row["mean_score_100"] + 0.18, idx, f"{row['mean_score_100']:.1f}", fontsize=8.0, va="center", color=TEXT)
    fig.text(0.055, 0.955, "Average sector sentiment: Utilities leads, Financials lags", fontsize=17.5, fontweight="bold", color=TEXT)
    fig.text(0.055, 0.915, "Full-sample sector averages from headline-level finance-VADER scores. All sectors remain above the neutral 50 line.", fontsize=10.2, color=MUTED)
    table_ax.axis("off")
    table_ax.set_facecolor(FT_BG)
    ranked = data.sort_values("mean_score_100", ascending=False).reset_index(drop=True)
    table_ax.text(0.0, 0.96, "Coverage check", fontsize=12, fontweight="bold", color=TEXT, transform=table_ax.transAxes)
    table_ax.text(0.0, 0.91, "Score and headline depth", fontsize=8.6, color=MUTED, transform=table_ax.transAxes)
    xs = [0.0, 0.55, 0.96]
    headers = ["Sector", "Mean", "Headlines"]
    y0 = 0.82
    for x, h in zip(xs, headers):
        table_ax.text(x, y0, h, fontsize=8.0, fontweight="bold", color="#4a423b", ha="left" if h == "Sector" else "right", transform=table_ax.transAxes)
    table_ax.plot([0, 0.98], [y0 - 0.03, y0 - 0.03], color=LINE, linewidth=0.8)
    for i, row in ranked.iterrows():
        y_pos = y0 - (i + 1) * 0.061
        table_ax.text(0.0, y_pos, row["sector"], fontsize=7.55, color=SECTOR_COLORS.get(row["sector"], TEXT), transform=table_ax.transAxes)
        table_ax.text(0.55, y_pos, f"{row['mean_score_100']:.1f}", fontsize=7.55, color=TEXT, ha="right", transform=table_ax.transAxes)
        table_ax.text(0.96, y_pos, f"{int(row['total_headlines']):,}", fontsize=7.55, color=TEXT, ha="right", transform=table_ax.transAxes)
        table_ax.plot([0, 0.98], [y_pos - 0.023, y_pos - 0.023], color="#e0d2bd", linewidth=0.5)
    add_source_note(fig, "Source: NovaAlloc results/tables/sector_sentiment_summary.csv.", "Note: Mean score is computed from sector-day fear/greed observations, not from equal ticker counts.")
    fig.subplots_adjust(left=0.14, right=0.965, top=0.865, bottom=0.16)
    save_figure(fig, "03_sector_sentiment_ranking")


def make_market_fear_greed_index() -> None:
    data = pd.read_csv(DATA_DIR / "market_fear_greed_index.csv", parse_dates=["date"])
    data["rolling_score_100"] = data["score_100"].rolling(21, min_periods=5).mean()
    clean = data.dropna(subset=["rolling_score_100"]).copy()
    latest = clean.iloc[-1]
    high = clean.loc[clean["rolling_score_100"].idxmax()]
    low = clean.loc[clean["rolling_score_100"].idxmin()]
    fig = plt.figure(figsize=(12.0, 6.35), dpi=220, facecolor=FT_BG)
    grid = fig.add_gridspec(1, 2, width_ratios=[4.45, 1.75], wspace=0.08)
    ax = fig.add_subplot(grid[0, 0])
    table_ax = fig.add_subplot(grid[0, 1])
    style_axis(ax, "y")
    table_ax.set_facecolor(FT_BG)
    ax.axhspan(50, 55, color="#f4dfc7", alpha=0.8)
    ax.axhspan(55, 60, color="#ead1ab", alpha=0.55)
    ax.plot(clean["date"], clean["rolling_score_100"], color="#9A6A5E", linewidth=1.75)
    ax.axhline(50, color=LINE, linewidth=0.9, linestyle=(0, (4, 4)))
    ax.scatter([latest["date"]], [latest["rolling_score_100"]], s=55, color="#c9472c", edgecolor=PANEL_BG, zorder=4)
    ax.annotate(f"Latest {latest['rolling_score_100']:.1f}", xy=(latest["date"], latest["rolling_score_100"]), xytext=(-75, 24), textcoords="offset points", fontsize=8.3, color=TEXT, arrowprops=dict(arrowstyle="-", color=LINE, linewidth=0.8), bbox=dict(boxstyle="round,pad=0.28", facecolor=PANEL_BG, edgecolor=GRID))
    ax.set_ylim(49.5, 58.8)
    ax.yaxis.set_major_locator(MultipleLocator(1))
    ax.yaxis.set_major_formatter(FuncFormatter(score_axis))
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.set_ylabel("Fear/greed score, 0-100")
    ax.set_xlabel("")
    fig.text(0.055, 0.955, "Market fear/greed: positive but not extreme", fontsize=17.5, fontweight="bold", color=TEXT)
    fig.text(0.055, 0.915, "21-day rolling headline sentiment index, Jan 2020-Dec 2023. The market stays above the neutral line for most of the sample.", fontsize=10.2, color=MUTED)
    table_ax.axis("off")
    table_ax.text(0, 0.96, "Market snapshot", fontsize=12, fontweight="bold", color=TEXT, transform=table_ax.transAxes)
    table_ax.plot([0, 0.98], [0.925, 0.925], color=LINE, linewidth=0.9)
    rows = [("Latest", latest["rolling_score_100"]), ("Average", clean["rolling_score_100"].mean()), ("High", high["rolling_score_100"]), ("Low", low["rolling_score_100"]), ("Avg coverage", data["average_sector_coverage"].mean() * 100)]
    for i, (label, value) in enumerate(rows):
        y_pos = 0.86 - i * 0.095
        table_ax.text(0.0, y_pos, label, fontsize=8.7, color=MUTED, transform=table_ax.transAxes)
        suffix = "%" if label == "Avg coverage" else ""
        table_ax.text(0.96, y_pos, f"{value:.1f}{suffix}", fontsize=9.2, fontweight="bold" if i == 0 else "normal", color=TEXT, ha="right", transform=table_ax.transAxes)
        table_ax.plot([0, 0.98], [y_pos - 0.035, y_pos - 0.035], color="#e0d2bd", linewidth=0.55)
    table_ax.text(0, 0.27, "Read-through", fontsize=9.2, fontweight="bold", color=TEXT, transform=table_ax.transAxes)
    table_ax.text(0, 0.12, "The market index is useful as context, but the fusion strategy relies on lagged sector signals rather than same-day market sentiment.", fontsize=8.1, color="#4f4942", wrap=True, transform=table_ax.transAxes)
    add_source_note(fig, "Source: NovaAlloc results/data/market_fear_greed_index.csv.", "Note: 50 is neutral. Rolling score smooths headline noise and is not used with look-ahead in portfolio weights.")
    fig.subplots_adjust(left=0.07, right=0.965, top=0.865, bottom=0.16)
    save_figure(fig, "03_market_fear_greed_index")


def _fusion_series() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    fund_returns = pd.read_csv(DATA_DIR / "fund_returns.csv", parse_dates=["date"])
    fusion_returns = pd.read_csv(DATA_DIR / "fusion_fund_returns.csv", parse_dates=["date"])
    comparison = pd.read_csv(TABLE_DIR / "fusion_comparison.csv")
    base = fund_returns[fund_returns["fund_id"].eq("Equity - Minimum Variance")][["date", "growth_of_1", "drawdown"]].copy()
    base["model"] = "Base"
    tilted = fusion_returns[["date", "growth_of_1", "drawdown"]].copy()
    tilted["model"] = "Sentiment Tilt"
    return base, tilted, comparison


def _fusion_table(table_ax: plt.Axes, comparison: pd.DataFrame, y0: float = 0.74) -> None:
    headers = ["Model", "Ret", "Vol", "Shp", "DD", "$1"]
    xs = [0.0, 0.38, 0.54, 0.69, 0.84, 0.98]
    for x, h in zip(xs, headers):
        table_ax.text(x, y0, h, fontsize=7.8, fontweight="bold", color="#4a423b", ha="left" if h == "Model" else "right", transform=table_ax.transAxes)
    table_ax.plot([0, 0.98], [y0 - 0.03, y0 - 0.03], color=LINE, linewidth=0.8)
    for i, row in comparison.iterrows():
        y_pos = y0 - (i + 1) * 0.085
        color = METHOD_COLORS.get(str(row["model"]), "#2f6f9f")
        table_ax.text(0, y_pos, row["model"], fontsize=8.0, color=color, transform=table_ax.transAxes)
        table_ax.text(0.38, y_pos, f"{row['annualised_return']:.1%}", fontsize=8.0, color=TEXT, ha="right", transform=table_ax.transAxes)
        table_ax.text(0.54, y_pos, f"{row['annualised_volatility']:.1%}", fontsize=8.0, color=TEXT, ha="right", transform=table_ax.transAxes)
        table_ax.text(0.69, y_pos, f"{row['sharpe_ratio']:.2f}", fontsize=8.0, color=TEXT, ha="right", transform=table_ax.transAxes)
        table_ax.text(0.84, y_pos, f"{row['max_drawdown']:.0%}", fontsize=8.0, color=TEXT, ha="right", transform=table_ax.transAxes)
        table_ax.text(0.98, y_pos, f"{row['final_growth_of_1']:.2f}", fontsize=8.0, color=TEXT, ha="right", transform=table_ax.transAxes)
        table_ax.plot([0, 0.98], [y_pos - 0.032, y_pos - 0.032], color="#e0d2bd", linewidth=0.55)


def make_fusion_growth_comparison() -> None:
    base, tilted, comparison = _fusion_series()
    base_end = float(base["growth_of_1"].iloc[-1])
    tilt_end = float(tilted["growth_of_1"].iloc[-1])
    gap = tilt_end - base_end
    fig = plt.figure(figsize=(12.0, 6.35), dpi=220, facecolor=FT_BG)
    grid = fig.add_gridspec(1, 2, width_ratios=[4.45, 1.85], wspace=0.08)
    ax = fig.add_subplot(grid[0, 0])
    table_ax = fig.add_subplot(grid[0, 1])
    style_axis(ax, "y")
    table_ax.set_facecolor(FT_BG)
    ax.plot(base["date"], base["growth_of_1"], color="#2f6f9f", linewidth=1.85, label="Base Min Var")
    ax.plot(tilted["date"], tilted["growth_of_1"], color="#c9472c", linewidth=1.75, label="Sentiment Tilt")
    ax.fill_between(base["date"], tilted["growth_of_1"], base["growth_of_1"], color="#c9472c", alpha=0.10)
    ax.axhline(1.0, color=LINE, linewidth=0.8)
    ax.yaxis.set_major_formatter(FuncFormatter(dollar_axis))
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.set_ylabel("Growth of USD 1")
    ax.set_xlabel("")
    ax.legend(frameon=False, loc="upper left", fontsize=8.4)
    ax.annotate(f"Tilt ends ${abs(gap):.3f} below base", xy=(base["date"].iloc[-1], tilt_end), xytext=(-115, -40), textcoords="offset points", fontsize=8.4, color=TEXT, arrowprops=dict(arrowstyle="-", color=LINE, linewidth=0.8), bbox=dict(boxstyle="round,pad=0.28", facecolor=PANEL_BG, edgecolor=GRID))
    fig.text(0.055, 0.955, "Fusion growth: sentiment tilt fails to beat the base fund", fontsize=17.5, fontweight="bold", color=TEXT)
    fig.text(0.055, 0.915, "Growth of USD 1 for Equity Minimum Variance versus lagged sector-sentiment tilt, Jan 2021-Dec 2023.", fontsize=10.2, color=MUTED)
    table_ax.axis("off")
    table_ax.text(0, 0.96, "Fusion scorecard", fontsize=12, fontweight="bold", color=TEXT, transform=table_ax.transAxes)
    table_ax.text(0, 0.915, "Base versus sentiment tilt", fontsize=8.6, color=MUTED, transform=table_ax.transAxes)
    _fusion_table(table_ax, comparison, 0.80)
    delta = comparison.loc[comparison["model"].eq("Sentiment Tilt"), "delta_sharpe_ratio_vs_base"].iloc[0]
    table_ax.text(0, 0.42, "Read-through", fontsize=9.2, fontweight="bold", color=TEXT, transform=table_ax.transAxes)
    table_ax.text(0, 0.25, f"The tilt lowers Sharpe by {delta:.2f} and finishes below the base fund. This is a useful negative result rather than a hidden failure.", fontsize=8.1, color="#4f4942", wrap=True, transform=table_ax.transAxes)
    add_source_note(fig, "Source: NovaAlloc results/data/fund_returns.csv, fusion_fund_returns.csv and results/tables/fusion_comparison.csv.", "Note: Sentiment weights use lagged sector z-scores, so the comparison is out-of-sample.")
    fig.subplots_adjust(left=0.07, right=0.965, top=0.865, bottom=0.16)
    save_figure(fig, "03_fusion_growth_comparison")


def make_fusion_drawdown_comparison() -> None:
    base, tilted, comparison = _fusion_series()
    worst_base = base.loc[base["drawdown"].idxmin()]
    worst_tilt = tilted.loc[tilted["drawdown"].idxmin()]
    fig = plt.figure(figsize=(12.0, 6.35), dpi=220, facecolor=FT_BG)
    grid = fig.add_gridspec(1, 2, width_ratios=[4.45, 1.85], wspace=0.08)
    ax = fig.add_subplot(grid[0, 0])
    table_ax = fig.add_subplot(grid[0, 1])
    style_axis(ax, "y")
    table_ax.set_facecolor(FT_BG)
    ax.plot(base["date"], base["drawdown"], color="#2f6f9f", linewidth=1.85, label="Base Min Var")
    ax.plot(tilted["date"], tilted["drawdown"], color="#c9472c", linewidth=1.75, label="Sentiment Tilt")
    ax.axhline(0, color=LINE, linewidth=0.85)
    ax.yaxis.set_major_formatter(FuncFormatter(percent_axis))
    ax.yaxis.set_major_locator(MultipleLocator(0.025))
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.set_ylabel("Drawdown from previous peak")
    ax.set_xlabel("")
    ax.legend(frameon=False, loc="lower left", fontsize=8.4)
    ax.annotate(f"Base worst {worst_base['drawdown']:.1%}", xy=(worst_base["date"], worst_base["drawdown"]), xytext=(-110, -28), textcoords="offset points", fontsize=8.3, color=TEXT, arrowprops=dict(arrowstyle="-", color=LINE, linewidth=0.8), bbox=dict(boxstyle="round,pad=0.28", facecolor=PANEL_BG, edgecolor=GRID))
    ax.annotate(f"Tilt worst {worst_tilt['drawdown']:.1%}", xy=(worst_tilt["date"], worst_tilt["drawdown"]), xytext=(25, 32), textcoords="offset points", fontsize=8.3, color=TEXT, arrowprops=dict(arrowstyle="-", color=LINE, linewidth=0.8), bbox=dict(boxstyle="round,pad=0.28", facecolor=PANEL_BG, edgecolor=GRID))
    fig.text(0.055, 0.955, "Fusion drawdown: small risk relief does not offset lower growth", fontsize=17.5, fontweight="bold", color=TEXT)
    fig.text(0.055, 0.915, "Drawdown comparison for the base Equity Minimum Variance fund and the sentiment-tilted extension.", fontsize=10.2, color=MUTED)
    table_ax.axis("off")
    table_ax.text(0, 0.96, "Drawdown scorecard", fontsize=12, fontweight="bold", color=TEXT, transform=table_ax.transAxes)
    table_ax.text(0, 0.915, "Lower is worse", fontsize=8.6, color=MUTED, transform=table_ax.transAxes)
    _fusion_table(table_ax, comparison, 0.80)
    dd_delta = comparison.loc[comparison["model"].eq("Sentiment Tilt"), "delta_max_drawdown_vs_base"].iloc[0]
    table_ax.text(0, 0.42, "Read-through", fontsize=9.2, fontweight="bold", color=TEXT, transform=table_ax.transAxes)
    table_ax.text(0, 0.25, f"The tilt improves maximum drawdown by only {dd_delta:.1%}. The improvement is too small to compensate for the lower return and lower Sharpe.", fontsize=8.1, color="#4f4942", wrap=True, transform=table_ax.transAxes)
    add_source_note(fig, "Source: NovaAlloc results/data/fund_returns.csv, fusion_fund_returns.csv and results/tables/fusion_comparison.csv.", "Note: Drawdown is measured relative to each model's own previous high-water mark.")
    fig.subplots_adjust(left=0.07, right=0.965, top=0.865, bottom=0.16)
    save_figure(fig, "03_fusion_drawdown_comparison")


def draw_box(
    ax: plt.Axes,
    xy: tuple[float, float],
    w: float,
    h: float,
    title: str,
    body: str,
    fc: str,
    ec: str = LINE,
    title_color: str = TEXT,
    wrap_width: int = 26,
    body_size: float = 6.8,
) -> None:
    box = patches.FancyBboxPatch(xy, w, h, boxstyle="round,pad=0.012,rounding_size=0.012", facecolor=fc, edgecolor=ec, linewidth=0.9, transform=ax.transAxes)
    ax.add_patch(box)
    ax.text(xy[0] + 0.015, xy[1] + h - 0.035, title, fontsize=8.5, fontweight="bold", color=title_color, transform=ax.transAxes, va="top")
    wrapped = "\n".join(textwrap.wrap(body, width=wrap_width))
    ax.text(xy[0] + 0.015, xy[1] + h - 0.075, wrapped, fontsize=body_size, color="#4f4942", transform=ax.transAxes, va="top", linespacing=1.15)


def arrow(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float], color: str = LINE) -> None:
    ax.annotate("", xy=end, xytext=start, xycoords=ax.transAxes, textcoords=ax.transAxes, arrowprops=dict(arrowstyle="->", color=color, lw=0.9, shrinkA=3, shrinkB=3))


def make_app_page_data_map() -> None:
    data_manifest = pd.read_csv(DATA_DIR / "app_data_manifest.csv")
    table_manifest = pd.read_csv(TABLE_DIR / "app_table_manifest.csv")
    required_files = int(data_manifest["exists"].sum() + table_manifest["exists"].sum())
    fig, ax = plt.subplots(figsize=(12.2, 6.8), dpi=220, facecolor=FT_BG)
    ax.set_facecolor(FT_BG)
    ax.axis("off")
    fig.text(0.055, 0.955, "App stage: precomputed results power six Streamlit pages", fontsize=17.5, fontweight="bold", color=TEXT)
    fig.text(0.055, 0.915, "The deployed app reads CSV outputs rather than rerunning backtests or VADER at runtime.", fontsize=10.2, color=MUTED)
    draw_box(
        ax,
        (0.055, 0.43),
        0.20,
        0.30,
        "Canonical results",
        "fund returns, fund weights, metrics, latest holdings, sector sentiment, fusion tables and diagnostics",
        "#f8ead7",
        "#9b8c78",
        wrap_width=24,
    )
    page_boxes = [
        ((0.35, 0.66), "Overview", "top fund evidence and KPI summary"),
        ((0.58, 0.66), "Funds", "growth, drawdown and fact sheets"),
        ((0.81, 0.66), "Allocation", "selected fund holdings and weights"),
        ((0.35, 0.42), "Sentiment", "sector and market fear/greed"),
        ((0.58, 0.42), "Fusion", "base versus sentiment-tilt test"),
        ((0.81, 0.42), "Data Health", "loaded files, rows and columns"),
    ]
    for xy, title, body in page_boxes:
        draw_box(ax, xy, 0.17, 0.14, title, body, "#e4eff4", "#355C7D", "#355C7D", wrap_width=23)
        arrow(ax, (0.255, 0.60), (xy[0], xy[1] + 0.07), "#6f6258")
    value_boxes = [
        ((0.35, 0.19), "Investor view", "compare funds and inspect fact sheets"),
        ((0.58, 0.19), "Model view", "test sentiment fusion and lag diagnostics"),
        ((0.81, 0.19), "Marker view", "verify files without opening raw CSVs"),
    ]
    for xy, title, body in value_boxes:
        draw_box(ax, xy, 0.17, 0.12, title, body, "#edf3e6", "#557A46", "#557A46", wrap_width=24)
    ax.text(0.055, 0.31, f"Files available to app: {required_files}", fontsize=9.0, fontweight="bold", color=TEXT, transform=ax.transAxes)
    ax.text(0.055, 0.27, "Runtime design:", fontsize=8.0, fontweight="bold", color=MUTED, transform=ax.transAxes)
    ax.text(0.055, 0.225, "load precomputed files,\nthen filter interactively.", fontsize=8.0, color=MUTED, transform=ax.transAxes, linespacing=1.15)
    add_source_note(fig, "Source: streamlit_app.py and results/data|tables app manifests.", "Note: This map documents the app consumption layer; it does not introduce new modelling data.")
    save_figure(fig, "04_app_page_data_map")


def make_report_combined_asset_class_weights() -> None:
    weights = pd.read_csv(DATA_DIR / "fund_weights.csv", parse_dates=["live_start_date"])
    data = weights[weights["universe"].eq("Combined")].copy()
    grouped = data.groupby(["live_start_date", "method_label", "asset_class"], as_index=False)["weight"].sum()
    methods = ["Equal Weight", "Minimum Variance", "Maximum Sharpe", "Risk Parity"]
    colors = {"Equity": "#2f6f9f", "Crypto": "#D9822B"}
    summary_rows = []
    fig = plt.figure(figsize=(12.2, 7.0), dpi=220, facecolor=FT_BG)
    grid = fig.add_gridspec(2, 3, width_ratios=[1, 1, 0.85], hspace=0.28, wspace=0.12)
    axes = [fig.add_subplot(grid[i // 2, i % 2]) for i in range(4)]
    table_ax = fig.add_subplot(grid[:, 2])
    for ax, method in zip(axes, methods):
        style_axis(ax, "y")
        part = grouped[grouped["method_label"].eq(method)]
        wide = part.pivot(index="live_start_date", columns="asset_class", values="weight").fillna(0.0).sort_index()
        for col in ["Equity", "Crypto"]:
            if col not in wide.columns:
                wide[col] = 0.0
        wide = wide[["Equity", "Crypto"]]
        ax.stackplot(wide.index, wide["Equity"], wide["Crypto"], colors=[colors["Equity"], colors["Crypto"]], alpha=0.94, linewidth=0.3, edgecolor=PANEL_BG)
        ax.set_ylim(0, 1.0)
        ax.yaxis.set_major_formatter(FuncFormatter(percent_axis))
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.set_title(method, loc="left", fontsize=10.0, fontweight="bold", color=TEXT, pad=4)
        if ax in axes[::2]:
            ax.set_ylabel("Weight")
        summary_rows.append({"method": method, "latest_crypto": wide["Crypto"].iloc[-1], "avg_crypto": wide["Crypto"].mean(), "max_crypto": wide["Crypto"].max()})
    handles = [mlines.Line2D([], [], color=colors["Equity"], linewidth=7, label="Equity"), mlines.Line2D([], [], color=colors["Crypto"], linewidth=7, label="Crypto")]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.055, 0.888), frameon=False, ncol=2, fontsize=8.5)
    fig.text(0.055, 0.955, "Combined funds: crypto allocation depends on portfolio rule", fontsize=17.5, fontweight="bold", color=TEXT)
    fig.text(0.055, 0.915, "Monthly live asset-class weights for Combined universe funds, Jan 2021-Dec 2023.", fontsize=10.2, color=MUTED)
    table_ax.axis("off")
    table_ax.set_facecolor(FT_BG)
    summary = pd.DataFrame(summary_rows).sort_values("avg_crypto", ascending=False).reset_index(drop=True)
    table_ax.text(0, 0.96, "Crypto allocation", fontsize=12, fontweight="bold", color=TEXT, transform=table_ax.transAxes)
    table_ax.text(0, 0.915, "Latest, average and peak", fontsize=8.6, color=MUTED, transform=table_ax.transAxes)
    xs = [0.0, 0.54, 0.74, 0.96]
    headers = ["Method", "Latest", "Avg", "Peak"]
    y0 = 0.82
    for x, h in zip(xs, headers):
        table_ax.text(x, y0, h, fontsize=8.0, fontweight="bold", color="#4a423b", ha="left" if h == "Method" else "right", transform=table_ax.transAxes)
    table_ax.plot([0, 0.98], [y0 - 0.03, y0 - 0.03], color=LINE, linewidth=0.8)
    for i, row in summary.iterrows():
        y_pos = y0 - (i + 1) * 0.08
        table_ax.text(0, y_pos, METHOD_SHORT[row["method"]], fontsize=8.2, color=METHOD_COLORS.get(row["method"], TEXT), transform=table_ax.transAxes)
        table_ax.text(0.54, y_pos, f"{row['latest_crypto']:.1%}", fontsize=8.2, color=TEXT, ha="right", transform=table_ax.transAxes)
        table_ax.text(0.74, y_pos, f"{row['avg_crypto']:.1%}", fontsize=8.2, color=TEXT, ha="right", transform=table_ax.transAxes)
        table_ax.text(0.96, y_pos, f"{row['max_crypto']:.1%}", fontsize=8.2, color=TEXT, ha="right", transform=table_ax.transAxes)
        table_ax.plot([0, 0.98], [y_pos - 0.03, y_pos - 0.03], color="#e0d2bd", linewidth=0.55)
    table_ax.text(0, 0.30, "Read-through", fontsize=9.2, fontweight="bold", color=TEXT, transform=table_ax.transAxes)
    table_ax.text(0, 0.16, "Equal Weight mechanically keeps crypto higher. Minimum Variance almost removes crypto, while Risk Parity keeps it as a small satellite exposure.", fontsize=8.1, color="#4f4942", wrap=True, transform=table_ax.transAxes)
    add_source_note(fig, "Source: NovaAlloc results/data/fund_weights.csv.", "Note: Security-level weights are aggregated to Equity and Crypto for each Combined fund.")
    fig.subplots_adjust(left=0.07, right=0.965, top=0.865, bottom=0.16)
    save_figure(fig, "05_report_combined_asset_class_weights")


def make_workflow_data_flow() -> None:
    fig, ax = plt.subplots(figsize=(12.4, 7.2), dpi=220, facecolor=FT_BG)
    ax.set_facecolor(FT_BG)
    ax.axis("off")
    fig.text(0.055, 0.955, "NovaAlloc workflow: returns, news sentiment and fusion connect end-to-end", fontsize=17.2, fontweight="bold", color=TEXT)
    fig.text(0.055, 0.918, "ProjectB pipeline from raw inputs to app, report and AI workflow evidence.", fontsize=10.2, color=MUTED)
    draw_box(ax, (0.04, 0.68), 0.17, 0.13, "Price data", "equity prices and crypto prices loaded and cleaned", "#e4eff4", "#355C7D", "#355C7D")
    draw_box(ax, (0.04, 0.43), 0.17, 0.13, "News data", "headlines mapped to tickers and sectors", "#e4eff4", "#355C7D", "#355C7D")
    draw_box(ax, (0.27, 0.68), 0.18, 0.13, "Returns foundation", "daily returns, trading calendar alignment and combined panel", "#edf3e6", "#557A46", "#557A46")
    draw_box(ax, (0.27, 0.43), 0.18, 0.13, "Headline panel", "ticker-day news counts and raw VADER-ready text", "#edf3e6", "#557A46", "#557A46")
    draw_box(ax, (0.51, 0.70), 0.17, 0.12, "Funds", "12 OOS portfolios, returns, weights and metrics", "#f8ead7", "#D9822B", "#D9822B")
    draw_box(ax, (0.51, 0.47), 0.17, 0.12, "Sentiment index", "finance-VADER scores, 0-100 fear/greed and lagged sector signal", "#f8ead7", "#D9822B", "#D9822B")
    draw_box(ax, (0.51, 0.25), 0.17, 0.12, "Fusion test", "lagged sentiment tilt versus base Minimum Variance", "#f8ead7", "#D9822B", "#D9822B")
    draw_box(ax, (0.73, 0.53), 0.15, 0.17, "Canonical results", "CSV tables and PNG figures used by both report and app", "#f5eadf", "#9b8c78")
    draw_box(ax, (0.91, 0.70), 0.08, 0.10, "App", "Streamlit dashboard", "#e4eff4", "#355C7D", "#355C7D")
    draw_box(ax, (0.91, 0.53), 0.08, 0.10, "Report", "Word paper and exhibits", "#e4eff4", "#355C7D", "#355C7D")
    draw_box(ax, (0.91, 0.36), 0.08, 0.10, "AI logs", "AGENTS and prompt logs", "#e4eff4", "#355C7D", "#355C7D")
    draw_box(
        ax,
        (0.04, 0.16),
        0.41,
        0.14,
        "Key rules",
        "Prior-return data only; lagged sentiment before trading; app consumes precomputed results; report states the negative fusion result.",
        "#fff7ef",
        "#9b8c78",
        wrap_width=56,
        body_size=7.0,
    )
    draw_box(
        ax,
        (0.73, 0.20),
        0.26,
        0.12,
        "Empirical message",
        "Crypto raises raw return but deepens drawdown. The sentiment tilt does not improve Sharpe in this sample.",
        "#fff7ef",
        "#9b8c78",
        wrap_width=38,
        body_size=7.0,
    )
    arrow(ax, (0.21, 0.745), (0.27, 0.745))
    arrow(ax, (0.21, 0.495), (0.27, 0.495))
    arrow(ax, (0.45, 0.745), (0.51, 0.755))
    arrow(ax, (0.45, 0.495), (0.51, 0.53))
    arrow(ax, (0.595, 0.70), (0.595, 0.59), "#D9822B")
    arrow(ax, (0.595, 0.47), (0.595, 0.37), "#D9822B")
    arrow(ax, (0.68, 0.76), (0.73, 0.62))
    arrow(ax, (0.68, 0.53), (0.73, 0.61))
    arrow(ax, (0.68, 0.31), (0.73, 0.55))
    arrow(ax, (0.88, 0.63), (0.91, 0.75), "#355C7D")
    arrow(ax, (0.88, 0.61), (0.91, 0.58), "#355C7D")
    arrow(ax, (0.88, 0.57), (0.91, 0.41), "#355C7D")
    add_source_note(fig, "Source: ProjectB scripts, results manifests, streamlit_app.py and AI workflow logs.", "Note: This diagram is a documentation exhibit; it does not create or alter modelling outputs.")
    save_figure(fig, "05_report_projectb_workflow_data_flow")


def main() -> None:
    configure_style()
    make_sharpe_barplot()
    make_sector_sentiment_index()
    make_sector_sentiment_ranking()
    make_market_fear_greed_index()
    make_fusion_growth_comparison()
    make_fusion_drawdown_comparison()
    make_app_page_data_map()
    make_report_combined_asset_class_weights()
    make_workflow_data_flow()


if __name__ == "__main__":
    main()
