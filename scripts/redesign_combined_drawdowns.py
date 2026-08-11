"""Redesign the combined-fund drawdown figure in an FT-inspired style."""
from __future__ import annotations

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter, MultipleLocator


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "results" / "data" / "fund_returns.csv"
OUT_DIR = ROOT / "results" / "figures" / "Redesign"
PNG_DIR = OUT_DIR / "png"
PDF_DIR = OUT_DIR / "pdf"


METHOD_ORDER = [
    "Minimum Variance",
    "Risk Parity",
    "Equal Weight",
    "Maximum Sharpe",
]

COLORS = {
    "Minimum Variance": "#4f7b58",
    "Risk Parity": "#c9472c",
    "Equal Weight": "#2f6f9f",
    "Maximum Sharpe": "#d77b20",
}

DISPLAY_LABELS = {
    "Minimum Variance": "Min variance",
    "Risk Parity": "Risk parity",
    "Equal Weight": "Equal weight",
    "Maximum Sharpe": "Max Sharpe",
}


def percent_axis(value: float, _pos: int) -> str:
    return f"{value:.0%}"


def load_combined_drawdowns() -> pd.DataFrame:
    data = pd.read_csv(DATA_PATH, parse_dates=["date"])
    combined = data[data["universe"].eq("Combined")].copy()
    if combined.empty:
        raise ValueError("No Combined universe rows found in fund_returns.csv")
    combined["method_label"] = pd.Categorical(
        combined["method_label"], categories=METHOD_ORDER, ordered=True
    )
    return combined.sort_values(["method_label", "date"])


def build_summary(data: pd.DataFrame) -> pd.DataFrame:
    return (
        data.groupby(["method_label"], observed=True)
        .agg(
            max_drawdown=("drawdown", "min"),
            final_drawdown=("drawdown", "last"),
            final_growth=("growth_of_1", "last"),
        )
        .reindex(METHOD_ORDER)
        .reset_index()
    )


def make_figure(data: pd.DataFrame, summary: pd.DataFrame) -> plt.Figure:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titlesize": 17,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
        }
    )

    fig = plt.figure(figsize=(12.2, 6.6), dpi=220, facecolor="#fff1e5")
    grid = fig.add_gridspec(1, 2, width_ratios=[4.6, 1.85], wspace=0.08)
    ax = fig.add_subplot(grid[0, 0])
    table_ax = fig.add_subplot(grid[0, 1])
    ax.set_facecolor("#fff7ef")
    table_ax.set_facecolor("#fff1e5")

    for method in METHOD_ORDER:
        part = data[data["method_label"].eq(method)]
        lw = 2.1 if method == "Maximum Sharpe" else 1.85
        alpha = 0.98 if method == "Maximum Sharpe" else 0.92
        ax.plot(
            part["date"],
            part["drawdown"],
            color=COLORS[method],
            linewidth=lw,
            alpha=alpha,
            label=method,
        )

    ax.axhline(0, color="#4d4d4d", linewidth=0.9)
    ax.set_ylim(-0.56, 0.025)
    ax.yaxis.set_major_locator(MultipleLocator(0.1))
    ax.yaxis.set_major_formatter(FuncFormatter(percent_axis))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.grid(axis="y", color="#d7c8b4", linewidth=0.8, alpha=0.7)
    ax.grid(axis="x", visible=False)
    ax.set_xlabel("")
    ax.set_ylabel("Drawdown from previous peak", color="#33302e")

    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#9b8c78")
    ax.tick_params(axis="both", colors="#33302e", length=0)

    # Mark the deepest drawdown, because it is the main risk lesson in the chart.
    worst = data.loc[data["drawdown"].idxmin()]
    ax.scatter(
        [worst["date"]],
        [worst["drawdown"]],
        color=COLORS[str(worst["method_label"])],
        s=38,
        zorder=5,
        edgecolor="#fff1e5",
        linewidth=1.0,
    )
    ax.annotate(
        f"Maximum Sharpe worst loss\n{worst['drawdown']:.1%}",
        xy=(worst["date"], worst["drawdown"]),
        xytext=(24, 26),
        textcoords="offset points",
        fontsize=9,
        color="#33302e",
        arrowprops=dict(arrowstyle="-", color="#6f6258", linewidth=0.9),
        bbox=dict(boxstyle="round,pad=0.35", facecolor="#fff7ef", edgecolor="#d7c8b4"),
    )

    title = "Combined funds: drawdown risk is concentrated in Maximum Sharpe"
    subtitle = (
        "Out-of-sample drawdown from previous peak, Jan 2021-Dec 2023. "
        "Lower values mean larger investor losses."
    )
    fig.text(0.055, 0.955, title, fontsize=18, fontweight="bold", color="#33302e")
    fig.text(0.055, 0.915, subtitle, fontsize=10.5, color="#5a5149")

    table_ax.axis("off")
    table_ax.text(
        0.0,
        0.965,
        "Risk snapshot",
        fontsize=12,
        fontweight="bold",
        color="#33302e",
        transform=table_ax.transAxes,
    )
    table_ax.text(
        0.0,
        0.925,
        "Combined universe only",
        fontsize=8.7,
        color="#6b6258",
        transform=table_ax.transAxes,
    )

    headers = ["Method", "Max DD", "End DD", "$1"]
    x_positions = [0.00, 0.52, 0.74, 0.96]
    y0 = 0.84
    row_h = 0.105
    for x, header in zip(x_positions, headers):
        ha = "left" if header == "Method" else "right"
        table_ax.text(
            x,
            y0,
            header,
            fontsize=8.5,
            fontweight="bold",
            color="#4a423b",
            ha=ha,
            transform=table_ax.transAxes,
        )
    table_ax.plot([0.0, 0.98], [y0 - 0.03, y0 - 0.03], color="#9b8c78", linewidth=0.9)

    for i, row in summary.iterrows():
        y = y0 - (i + 1) * row_h
        method = str(row["method_label"])
        table_ax.text(
            0.00,
            y,
            DISPLAY_LABELS[method],
            fontsize=8.6,
            color=COLORS[method],
            ha="left",
            transform=table_ax.transAxes,
        )
        table_ax.text(0.54, y, f"{row['max_drawdown']:.1%}", fontsize=8.6, color="#33302e", ha="right", transform=table_ax.transAxes)
        table_ax.text(0.76, y, f"{row['final_drawdown']:.1%}", fontsize=8.6, color="#33302e", ha="right", transform=table_ax.transAxes)
        table_ax.text(0.94, y, f"{row['final_growth']:.2f}", fontsize=8.6, color="#33302e", ha="right", transform=table_ax.transAxes)
        table_ax.plot([0.0, 0.98], [y - 0.035, y - 0.035], color="#e0d2bd", linewidth=0.6)

    table_ax.text(
        0.0,
        0.245,
        "Read-through",
        fontsize=9.3,
        fontweight="bold",
        color="#33302e",
        transform=table_ax.transAxes,
    )
    table_ax.text(
        0.0,
        0.09,
        "Minimum variance gives the\nsmallest peak-to-trough loss.\nMaximum Sharpe is most fragile\nbecause expected-return estimates\ncreate concentrated positions.",
        fontsize=8.3,
        color="#4f4942",
        linespacing=1.25,
        transform=table_ax.transAxes,
    )

    fig.text(
        0.055,
        0.055,
        "Source: NovaAlloc results/data/fund_returns.csv. "
        "Monthly walk-forward out-of-sample backtest; combined equity-plus-crypto funds only.",
        fontsize=8.2,
        color="#6b6258",
    )
    fig.text(
        0.055,
        0.031,
        "Note: Drawdown is measured relative to each fund's own previous high-water mark. "
        "Returns are before transaction costs.",
        fontsize=8.2,
        color="#6b6258",
    )

    fig.subplots_adjust(left=0.07, right=0.965, top=0.865, bottom=0.16)
    return fig


def main() -> None:
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    data = load_combined_drawdowns()
    summary = build_summary(data)
    fig = make_figure(data, summary)
    png_path = PNG_DIR / "02_combined_fund_drawdowns.png"
    pdf_path = PDF_DIR / "02_combined_fund_drawdowns.pdf"
    fig.savefig(png_path, facecolor=fig.get_facecolor(), bbox_inches="tight")
    fig.savefig(pdf_path, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {png_path}")
    print(f"Saved {pdf_path}")


if __name__ == "__main__":
    main()


