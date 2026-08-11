"""Redesign the fund growth-of-one-dollar figure in an FT-inspired style."""
from __future__ import annotations

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter, FixedLocator, NullFormatter, NullLocator


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "results" / "data" / "fund_returns.csv"
METRICS_PATH = ROOT / "results" / "tables" / "performance_metrics.csv"
OUT_DIR = ROOT / "results" / "figures" / "Redesign"
PNG_DIR = OUT_DIR / "png"
PDF_DIR = OUT_DIR / "pdf"

UNIVERSE_COLORS = {
    "Combined": "#557A46",
    "Equity": "#2f6f9f",
    "Crypto": "#D9822B",
}

METHOD_COLORS = {
    "Equal Weight": "#2f6f9f",
    "Risk Parity": "#c9472c",
    "Minimum Variance": "#557A46",
    "Maximum Sharpe": "#D9822B",
}

METHOD_SHORT = {
    "Equal Weight": "EW",
    "Risk Parity": "RP",
    "Minimum Variance": "Min Var",
    "Maximum Sharpe": "Max Shp",
}


def dollar_axis(value: float, _pos: int) -> str:
    if value < 1:
        return f"${value:.2f}"
    if value < 2:
        return f"${value:.1f}"
    return f"${value:.0f}"


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    returns = pd.read_csv(DATA_PATH, parse_dates=["date"])
    metrics = pd.read_csv(METRICS_PATH)
    required_returns = {"date", "fund_id", "universe", "method_label", "growth_of_1", "drawdown"}
    required_metrics = {"fund_id", "sharpe_ratio", "max_drawdown", "final_growth_of_1"}
    missing_returns = required_returns.difference(returns.columns)
    missing_metrics = required_metrics.difference(metrics.columns)
    if missing_returns:
        raise ValueError(f"fund_returns.csv is missing columns: {sorted(missing_returns)}")
    if missing_metrics:
        raise ValueError(f"performance_metrics.csv is missing columns: {sorted(missing_metrics)}")
    return returns.sort_values(["fund_id", "date"]), metrics


def build_summary(returns: pd.DataFrame, metrics: pd.DataFrame) -> pd.DataFrame:
    meta = (
        returns.groupby(["fund_id", "universe", "method_label"], as_index=False)
        .agg(
            final_growth=("growth_of_1", "last"),
            max_drawdown=("drawdown", "min"),
            first_date=("date", "min"),
            last_date=("date", "max"),
        )
    )
    out = meta.merge(metrics[["fund_id", "sharpe_ratio"]], on="fund_id", how="left")
    out["display"] = out["universe"] + " " + out["method_label"].map(METHOD_SHORT)
    return out.sort_values("final_growth", ascending=False).reset_index(drop=True)


def make_figure(returns: pd.DataFrame, summary: pd.DataFrame) -> plt.Figure:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titlesize": 17,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
        }
    )

    fig = plt.figure(figsize=(12.4, 7.45), dpi=220, facecolor="#fff1e5")
    grid = fig.add_gridspec(3, 2, width_ratios=[4.8, 1.85], hspace=0.12, wspace=0.08)
    axes = [fig.add_subplot(grid[i, 0]) for i in range(3)]
    table_ax = fig.add_subplot(grid[:, 1])
    for ax in axes:
        ax.set_facecolor("#fff7ef")
    table_ax.set_facecolor("#fff1e5")

    panel_order = ["Equity", "Combined", "Crypto"]
    y_limits = {
        "Equity": (0.82, 1.9, [1.0, 1.25, 1.5, 1.75]),
        "Combined": (0.82, 1.9, [1.0, 1.25, 1.5, 1.75]),
        "Crypto": (0.55, 7.4, [0.75, 1.0, 2.0, 3.0, 5.0, 7.0]),
    }
    for ax, universe in zip(axes, panel_order):
        uni = returns[returns["universe"].eq(universe)]
        for method, part in uni.groupby("method_label", sort=False):
            ax.plot(
                part["date"],
                part["growth_of_1"],
                color=METHOD_COLORS[method],
                linewidth=1.9,
                alpha=0.95,
                label=method,
            )

        ymin, ymax, ticks = y_limits[universe]
        ax.axhline(1.0, color="#4d4d4d", linewidth=0.8)
        ax.set_yscale("log")
        ax.set_ylim(ymin, ymax)
        ax.yaxis.set_major_locator(FixedLocator(ticks))
        ax.yaxis.set_major_formatter(FuncFormatter(dollar_axis))
        ax.yaxis.set_minor_locator(NullLocator())
        ax.yaxis.set_minor_formatter(NullFormatter())
        ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
        ax.grid(axis="y", color="#d7c8b4", linewidth=0.75, alpha=0.7)
        ax.grid(axis="x", visible=False)
        ax.set_xlabel("")
        ax.text(
            0.01,
            0.82,
            universe,
            transform=ax.transAxes,
            fontsize=10.5,
            fontweight="bold",
            color=UNIVERSE_COLORS[universe],
            bbox=dict(boxstyle="round,pad=0.25", facecolor="#fff7ef", edgecolor="#d7c8b4"),
        )
        for spine in ["top", "right", "left"]:
            ax.spines[spine].set_visible(False)
        ax.spines["bottom"].set_color("#9b8c78")
        ax.tick_params(axis="both", colors="#33302e", length=0)

    axes[1].set_ylabel("Growth of USD 1, log scale", color="#33302e")
    for ax in axes[:-1]:
        ax.tick_params(labelbottom=False)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper left",
        bbox_to_anchor=(0.055, 0.887),
        frameon=False,
        ncol=4,
        fontsize=8.5,
        handlelength=2.3,
        columnspacing=1.6,
    )

    worst = summary.loc[summary["max_drawdown"].idxmin()]
    best = summary.iloc[0]
    fig.text(
        0.055,
        0.955,
        "Growth of USD 1: crypto leads, but drawdown risk changes the story",
        fontsize=18,
        fontweight="bold",
        color="#33302e",
    )
    fig.text(
        0.055,
        0.915,
        "Out-of-sample fund performance, Jan 2021-Dec 2023. Small multiples keep equity, combined and crypto funds readable.",
        fontsize=10.5,
        color="#5a5149",
    )

    table_ax.axis("off")
    table_ax.text(
        0.0,
        0.965,
        "Return snapshot",
        fontsize=12,
        fontweight="bold",
        color="#33302e",
        transform=table_ax.transAxes,
    )
    table_ax.text(
        0.0,
        0.925,
        "Sorted by ending value of USD 1",
        fontsize=8.7,
        color="#6b6258",
        transform=table_ax.transAxes,
    )
    table_ax.text(
        0.0,
        0.875,
        f"Top fund {best['display']}  ${best['final_growth']:.2f}",
        fontsize=9.3,
        fontweight="bold",
        color=UNIVERSE_COLORS[str(best["universe"])],
        transform=table_ax.transAxes,
    )
    table_ax.text(
        0.0,
        0.835,
        f"Worst max DD {worst['display']}  {worst['max_drawdown']:.1%}",
        fontsize=9.0,
        fontweight="bold",
        color=UNIVERSE_COLORS[str(worst["universe"])],
        transform=table_ax.transAxes,
    )
    table_ax.plot([0.0, 0.98], [0.795, 0.795], color="#9b8c78", linewidth=0.9)

    headers = ["Fund", "$1", "Max DD", "Sharpe"]
    x_positions = [0.00, 0.48, 0.73, 0.96]
    y0 = 0.74
    row_h = 0.043
    for x_pos, header in zip(x_positions, headers):
        ha = "left" if header == "Fund" else "right"
        table_ax.text(
            x_pos,
            y0,
            header,
            fontsize=8.0,
            fontweight="bold",
            color="#4a423b",
            ha=ha,
            transform=table_ax.transAxes,
        )
    table_ax.plot([0.0, 0.98], [y0 - 0.025, y0 - 0.025], color="#9b8c78", linewidth=0.8)

    for i, row in summary.iterrows():
        y_pos = y0 - (i + 1) * row_h
        color = UNIVERSE_COLORS[str(row["universe"])]
        table_ax.text(0.00, y_pos, row["display"], fontsize=7.3, color=color, ha="left", transform=table_ax.transAxes)
        table_ax.text(0.48, y_pos, f"{row['final_growth']:.2f}", fontsize=7.3, color="#33302e", ha="right", transform=table_ax.transAxes)
        table_ax.text(0.73, y_pos, f"{row['max_drawdown']:.0%}", fontsize=7.3, color="#33302e", ha="right", transform=table_ax.transAxes)
        table_ax.text(0.96, y_pos, f"{row['sharpe_ratio']:.2f}", fontsize=7.3, color="#33302e", ha="right", transform=table_ax.transAxes)
        table_ax.plot([0.0, 0.98], [y_pos - 0.020, y_pos - 0.020], color="#e0d2bd", linewidth=0.5)

    table_ax.text(
        0.0,
        0.168,
        "Read-through",
        fontsize=8.8,
        fontweight="bold",
        color="#33302e",
        transform=table_ax.transAxes,
    )
    table_ax.text(
        0.0,
        0.132,
        "Crypto funds finish highest,\nbut drawdowns are deep.\nCombined funds trade upside\nfor smoother paths.",
        fontsize=7.2,
        color="#4f4942",
        linespacing=1.04,
        va="top",
        transform=table_ax.transAxes,
    )

    fig.text(
        0.055,
        0.055,
        "Source: NovaAlloc results/data/fund_returns.csv and results/tables/performance_metrics.csv.",
        fontsize=8.2,
        color="#6b6258",
    )
    fig.text(
        0.055,
        0.031,
        "Note: Growth is cumulative out-of-sample value of USD 1 before transaction costs. "
        "Sharpe assumes a zero risk-free rate.",
        fontsize=8.2,
        color="#6b6258",
    )
    fig.subplots_adjust(left=0.075, right=0.965, top=0.815, bottom=0.14)
    return fig


def main() -> None:
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    returns, metrics = load_data()
    summary = build_summary(returns, metrics)
    fig = make_figure(returns, summary)
    png_path = PNG_DIR / "02_fund_growth_of_1.png"
    pdf_path = PDF_DIR / "02_fund_growth_of_1.pdf"
    fig.savefig(png_path, facecolor=fig.get_facecolor(), bbox_inches="tight")
    fig.savefig(pdf_path, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {png_path}")
    print(f"Saved {pdf_path}")


if __name__ == "__main__":
    main()


