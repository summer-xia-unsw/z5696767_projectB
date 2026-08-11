"""Redesign the fund risk-return scatter figure in an FT-inspired style."""
from __future__ import annotations

from pathlib import Path

import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter, MultipleLocator


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "results" / "tables" / "performance_metrics.csv"
OUT_DIR = ROOT / "results" / "figures" / "Redesign"
PNG_DIR = OUT_DIR / "png"
PDF_DIR = OUT_DIR / "pdf"

UNIVERSE_COLORS = {
    "Equity": "#2f6f9f",
    "Combined": "#557A46",
    "Crypto": "#D9822B",
}

METHOD_MARKERS = {
    "Equal Weight": "o",
    "Risk Parity": "D",
    "Minimum Variance": "s",
    "Maximum Sharpe": "^",
}

METHOD_SHORT = {
    "Equal Weight": "EW",
    "Risk Parity": "RP",
    "Minimum Variance": "Min Var",
    "Maximum Sharpe": "Max Shp",
}

LABEL_OFFSETS = {
    "Equity - Equal Weight": (16, 12),
    "Combined - Risk Parity": (15, -30),
    "Crypto - Risk Parity": (-108, 6),
    "Crypto - Maximum Sharpe": (-105, 12),
    "Combined - Maximum Sharpe": (14, -24),
}


def percent_axis(value: float, _pos: int) -> str:
    return f"{value:.0%}"


def load_metrics() -> pd.DataFrame:
    data = pd.read_csv(DATA_PATH)
    required = {
        "fund_id",
        "universe",
        "method_label",
        "annualised_return",
        "annualised_volatility",
        "sharpe_ratio",
        "max_drawdown",
    }
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"performance_metrics.csv is missing columns: {sorted(missing)}")
    data = data.copy()
    data["display"] = data["universe"] + " " + data["method_label"].map(METHOD_SHORT)
    return data.sort_values("sharpe_ratio", ascending=False).reset_index(drop=True)


def add_sharpe_guides(ax: plt.Axes, x_min: float, x_max: float, y_max: float) -> None:
    for sharpe in [0.25, 0.50, 0.75]:
        x_end = min(x_max, y_max / sharpe)
        ax.plot(
            [0.0, x_end],
            [0.0, sharpe * x_end],
            color="#b8aa98",
            linewidth=0.8,
            linestyle=(0, (4, 4)),
            alpha=0.75,
            zorder=0,
        )
        label_x = max(x_min + 0.02, x_end - 0.08)
        label_y = sharpe * label_x
        ax.text(
            label_x,
            label_y + 0.006,
            f"Sharpe {sharpe:.2f}",
            fontsize=7.2,
            color="#7a6c5d",
            rotation=18,
            ha="left",
            va="bottom",
        )


def make_figure(data: pd.DataFrame) -> plt.Figure:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titlesize": 17,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
        }
    )

    fig = plt.figure(figsize=(12.2, 6.75), dpi=220, facecolor="#fff1e5")
    grid = fig.add_gridspec(1, 2, width_ratios=[4.45, 2.05], wspace=0.08)
    ax = fig.add_subplot(grid[0, 0])
    table_ax = fig.add_subplot(grid[0, 1])
    ax.set_facecolor("#fff7ef")
    table_ax.set_facecolor("#fff1e5")

    x_min, x_max = 0.08, 0.86
    y_min, y_max = 0.03, 0.39
    add_sharpe_guides(ax, x_min, x_max, y_max)

    for _, row in data.iterrows():
        universe = str(row["universe"])
        method = str(row["method_label"])
        ax.scatter(
            row["annualised_volatility"],
            row["annualised_return"],
            s=92,
            marker=METHOD_MARKERS[method],
            color=UNIVERSE_COLORS[universe],
            edgecolor="#fff7ef",
            linewidth=1.1,
            alpha=0.96,
            zorder=3,
        )

    for fund_id, offset in LABEL_OFFSETS.items():
        row = data[data["fund_id"].eq(fund_id)].iloc[0]
        label = row["display"]
        if fund_id == "Equity - Equal Weight":
            label = f"Best Sharpe\n{label} {row['sharpe_ratio']:.2f}"
        elif fund_id == "Combined - Risk Parity":
            label = f"Best combined\n{label} {row['sharpe_ratio']:.2f}"
        elif fund_id == "Crypto - Risk Parity":
            label = f"Highest return\n{label} {row['annualised_return']:.1%}"
        elif fund_id == "Crypto - Maximum Sharpe":
            label = f"High risk, low reward\n{label}"
        elif fund_id == "Combined - Maximum Sharpe":
            label = f"Optimizer drag\n{label}"
        ax.annotate(
            label,
            xy=(row["annualised_volatility"], row["annualised_return"]),
            xytext=offset,
            textcoords="offset points",
            fontsize=8.0,
            color="#33302e",
            arrowprops=dict(arrowstyle="-", color="#7b6a58", linewidth=0.8),
            bbox=dict(boxstyle="round,pad=0.28", facecolor="#fff7ef", edgecolor="#d7c8b4"),
            zorder=4,
        )

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.xaxis.set_major_locator(MultipleLocator(0.10))
    ax.yaxis.set_major_locator(MultipleLocator(0.05))
    ax.xaxis.set_major_formatter(FuncFormatter(percent_axis))
    ax.yaxis.set_major_formatter(FuncFormatter(percent_axis))
    ax.grid(axis="both", color="#d7c8b4", linewidth=0.75, alpha=0.65)
    ax.set_xlabel("Annualised volatility")
    ax.set_ylabel("Annualised return")

    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#9b8c78")
    ax.tick_params(axis="both", colors="#33302e", length=0)

    title = "Risk-return map: diversification beats chasing raw crypto return"
    subtitle = (
        "Out-of-sample annualised return versus volatility, Jan 2021-Dec 2023. "
        "Dotted lines show zero-rate Sharpe guides."
    )
    fig.text(0.055, 0.955, title, fontsize=18, fontweight="bold", color="#33302e")
    fig.text(0.055, 0.915, subtitle, fontsize=10.5, color="#5a5149")

    universe_handles = [
        mlines.Line2D(
            [],
            [],
            marker="o",
            linestyle="None",
            markersize=7.5,
            markerfacecolor=color,
            markeredgecolor="#fff7ef",
            label=name,
        )
        for name, color in UNIVERSE_COLORS.items()
    ]
    method_handles = [
        mlines.Line2D(
            [],
            [],
            marker=marker,
            linestyle="None",
            markersize=7.0,
            markerfacecolor="#6f6258",
            markeredgecolor="#fff7ef",
            label=METHOD_SHORT[name],
        )
        for name, marker in METHOD_MARKERS.items()
    ]
    fig.legend(
        universe_handles + method_handles,
        [h.get_label() for h in universe_handles + method_handles],
        loc="upper left",
        bbox_to_anchor=(0.055, 0.875),
        frameon=False,
        ncol=7,
        fontsize=8.0,
        handletextpad=0.5,
        columnspacing=1.15,
    )

    table_ax.axis("off")
    best = data.iloc[0]
    highest_return = data.loc[data["annualised_return"].idxmax()]
    table_ax.text(
        0.0,
        0.965,
        "Risk-adjusted scorecard",
        fontsize=12,
        fontweight="bold",
        color="#33302e",
        transform=table_ax.transAxes,
    )
    table_ax.text(
        0.0,
        0.925,
        "Sorted by Sharpe ratio",
        fontsize=8.7,
        color="#6b6258",
        transform=table_ax.transAxes,
    )
    table_ax.text(
        0.0,
        0.875,
        f"Best Sharpe {best['display']}  {best['sharpe_ratio']:.2f}",
        fontsize=9.3,
        fontweight="bold",
        color=UNIVERSE_COLORS[str(best["universe"])],
        transform=table_ax.transAxes,
    )
    table_ax.text(
        0.0,
        0.835,
        f"Highest return {highest_return['display']}  {highest_return['annualised_return']:.1%}",
        fontsize=9.0,
        fontweight="bold",
        color=UNIVERSE_COLORS[str(highest_return["universe"])],
        transform=table_ax.transAxes,
    )
    table_ax.plot([0.0, 0.98], [0.795, 0.795], color="#9b8c78", linewidth=0.9)

    headers = ["Fund", "Ret", "Vol", "Shp", "DD"]
    x_positions = [0.00, 0.48, 0.64, 0.79, 0.96]
    y0 = 0.74
    row_h = 0.043
    for x_pos, header in zip(x_positions, headers):
        ha = "left" if header == "Fund" else "right"
        table_ax.text(
            x_pos,
            y0,
            header,
            fontsize=7.9,
            fontweight="bold",
            color="#4a423b",
            ha=ha,
            transform=table_ax.transAxes,
        )
    table_ax.plot([0.0, 0.98], [y0 - 0.025, y0 - 0.025], color="#9b8c78", linewidth=0.8)

    for i, row in data.iterrows():
        y_pos = y0 - (i + 1) * row_h
        color = UNIVERSE_COLORS[str(row["universe"])]
        table_ax.text(0.00, y_pos, row["display"], fontsize=7.2, color=color, ha="left", transform=table_ax.transAxes)
        table_ax.text(0.48, y_pos, f"{row['annualised_return']:.0%}", fontsize=7.2, color="#33302e", ha="right", transform=table_ax.transAxes)
        table_ax.text(0.64, y_pos, f"{row['annualised_volatility']:.0%}", fontsize=7.2, color="#33302e", ha="right", transform=table_ax.transAxes)
        table_ax.text(0.79, y_pos, f"{row['sharpe_ratio']:.2f}", fontsize=7.2, color="#33302e", ha="right", transform=table_ax.transAxes)
        table_ax.text(0.96, y_pos, f"{row['max_drawdown']:.0%}", fontsize=7.2, color="#33302e", ha="right", transform=table_ax.transAxes)
        table_ax.plot([0.0, 0.98], [y_pos - 0.020, y_pos - 0.020], color="#e0d2bd", linewidth=0.5)

    table_ax.text(
        0.0,
        0.158,
        "Read-through",
        fontsize=9.0,
        fontweight="bold",
        color="#33302e",
        transform=table_ax.transAxes,
    )
    table_ax.text(
        0.0,
        0.118,
        "Crypto dominates raw return but sits far right.\nEquity EW and Combined RP deliver better\nrisk-adjusted results for a coursework investor.",
        fontsize=7.4,
        color="#4f4942",
        linespacing=1.13,
        va="top",
        transform=table_ax.transAxes,
    )

    fig.text(
        0.055,
        0.055,
        "Source: NovaAlloc results/tables/performance_metrics.csv.",
        fontsize=8.2,
        color="#6b6258",
    )
    fig.text(
        0.055,
        0.031,
        "Note: Return, volatility and Sharpe are annualised from daily out-of-sample returns. "
        "Sharpe assumes a zero risk-free rate.",
        fontsize=8.2,
        color="#6b6258",
    )
    fig.subplots_adjust(left=0.08, right=0.965, top=0.81, bottom=0.16)
    return fig


def main() -> None:
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    data = load_metrics()
    fig = make_figure(data)
    png_path = PNG_DIR / "02_fund_risk_return_scatter.png"
    pdf_path = PDF_DIR / "02_fund_risk_return_scatter.pdf"
    fig.savefig(png_path, facecolor=fig.get_facecolor(), bbox_inches="tight")
    fig.savefig(pdf_path, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {png_path}")
    print(f"Saved {pdf_path}")


if __name__ == "__main__":
    main()


