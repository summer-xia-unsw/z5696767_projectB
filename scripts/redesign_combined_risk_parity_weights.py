"""Redesign the combined risk-parity weights figure in an FT-inspired style."""
from __future__ import annotations

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter, MultipleLocator


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "results" / "data" / "fund_weights.csv"
OUT_DIR = ROOT / "results" / "figures" / "Redesign"
PNG_DIR = OUT_DIR / "png"
PDF_DIR = OUT_DIR / "pdf"

FUND_ID = "Combined - Risk Parity"

BUCKET_ORDER = [
    "Comm",
    "Consumer",
    "Crypto",
    "Energy",
    "Financials",
    "Industrials",
    "Tech",
    "RealEstate",
    "Materials",
    "Utilities",
    "Healthcare",
]

COLORS = {
    "Comm": "#355C7D",
    "Consumer": "#6C8EAD",
    "Crypto": "#D9822B",
    "Energy": "#B84A3A",
    "Financials": "#7A6FA8",
    "Industrials": "#C77DBB",
    "Tech": "#37A6A6",
    "RealEstate": "#B9B93B",
    "Materials": "#8B8D84",
    "Utilities": "#557A46",
    "Healthcare": "#9A6A5E",
}

DISPLAY_LABELS = {
    "Comm": "Communication",
    "Consumer": "Consumer",
    "Crypto": "Crypto",
    "Energy": "Energy",
    "Financials": "Financials",
    "Industrials": "Industrials",
    "Tech": "Technology",
    "RealEstate": "Real estate",
    "Materials": "Materials",
    "Utilities": "Utilities",
    "Healthcare": "Healthcare",
}


def percent_axis(value: float, _pos: int) -> str:
    return f"{value:.0%}"


def load_weights() -> tuple[pd.DataFrame, pd.DataFrame]:
    data = pd.read_csv(DATA_PATH, parse_dates=["rebalance_date", "live_start_date", "live_end_date"])
    weights = data[data["fund_id"].eq(FUND_ID)].copy()
    if weights.empty:
        raise ValueError(f"No rows found for {FUND_ID}")

    weights["bucket"] = weights["sector"].where(weights["asset_class"].eq("Equity"), "Crypto")
    grouped = weights.groupby(["live_start_date", "bucket"], as_index=False)["weight"].sum()
    wide = (
        grouped.pivot(index="live_start_date", columns="bucket", values="weight")
        .fillna(0.0)
        .sort_index()
    )
    for bucket in BUCKET_ORDER:
        if bucket not in wide.columns:
            wide[bucket] = 0.0
    wide = wide[BUCKET_ORDER]

    totals = wide.sum(axis=1)
    if not ((totals - 1.0).abs() < 1e-8).all():
        raise ValueError("Risk-parity bucket weights do not sum to one")

    summary = pd.DataFrame(
        {
            "latest_weight": wide.iloc[-1],
            "average_weight": wide.mean(),
            "min_weight": wide.min(),
            "max_weight": wide.max(),
        }
    ).sort_values("latest_weight", ascending=False)
    return wide, summary


def make_figure(wide: pd.DataFrame, summary: pd.DataFrame) -> plt.Figure:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titlesize": 17,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
        }
    )

    fig = plt.figure(figsize=(12.2, 6.7), dpi=220, facecolor="#fff1e5")
    grid = fig.add_gridspec(1, 2, width_ratios=[4.7, 1.85], wspace=0.08)
    ax = fig.add_subplot(grid[0, 0])
    table_ax = fig.add_subplot(grid[0, 1])
    ax.set_facecolor("#fff7ef")
    table_ax.set_facecolor("#fff1e5")

    x = wide.index.to_pydatetime()
    y = [wide[bucket].to_numpy(dtype="float64") for bucket in BUCKET_ORDER]
    ax.stackplot(
        x,
        y,
        colors=[COLORS[bucket] for bucket in BUCKET_ORDER],
        linewidth=0.25,
        edgecolor="#fff7ef",
        alpha=0.96,
    )

    ax.set_ylim(0, 1.0)
    ax.yaxis.set_major_locator(MultipleLocator(0.2))
    ax.yaxis.set_major_formatter(FuncFormatter(percent_axis))
    ax.set_xlim(pd.Timestamp("2021-01-01"), pd.Timestamp("2024-01-01"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.grid(axis="y", color="#d7c8b4", linewidth=0.8, alpha=0.7)
    ax.grid(axis="x", visible=False)
    ax.set_xlabel("")
    ax.set_ylabel("Portfolio weight", color="#33302e")

    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#9b8c78")
    ax.tick_params(axis="both", colors="#33302e", length=0)

    crypto = wide["Crypto"]
    max_crypto_date = crypto.idxmax()
    max_crypto_value = float(crypto.max())
    ax.axvline(max_crypto_date, color="#7b6a58", linewidth=0.8, linestyle=(0, (3, 3)), alpha=0.75)
    ax.annotate(
        f"Crypto allocation peaks\nat {max_crypto_value:.1%}",
        xy=(max_crypto_date, 0.36),
        xytext=(18, 24),
        textcoords="offset points",
        fontsize=8.8,
        color="#33302e",
        arrowprops=dict(arrowstyle="-", color="#6f6258", linewidth=0.9),
        bbox=dict(boxstyle="round,pad=0.35", facecolor="#fff7ef", edgecolor="#d7c8b4"),
    )

    title = "Combined risk parity: broad equity mix with capped crypto exposure"
    subtitle = (
        "Monthly live weights aggregated by sector or asset class, Jan 2021-Dec 2023. "
        "Weights are formed from prior returns only."
    )
    fig.text(0.055, 0.955, title, fontsize=18, fontweight="bold", color="#33302e")
    fig.text(0.055, 0.915, subtitle, fontsize=10.5, color="#5a5149")

    table_ax.axis("off")
    latest_date = wide.index.max().strftime("%b %Y")
    equity_latest = 1.0 - float(summary.loc["Crypto", "latest_weight"])
    crypto_latest = float(summary.loc["Crypto", "latest_weight"])
    table_ax.text(
        0.0,
        0.965,
        "Allocation snapshot",
        fontsize=12,
        fontweight="bold",
        color="#33302e",
        transform=table_ax.transAxes,
    )
    table_ax.text(
        0.0,
        0.925,
        f"Latest live month: {latest_date}",
        fontsize=8.7,
        color="#6b6258",
        transform=table_ax.transAxes,
    )
    table_ax.text(
        0.0,
        0.875,
        f"Equity {equity_latest:.1%}",
        fontsize=10.5,
        fontweight="bold",
        color="#33302e",
        transform=table_ax.transAxes,
    )
    table_ax.text(
        0.42,
        0.875,
        f"Crypto {crypto_latest:.1%}",
        fontsize=10.5,
        fontweight="bold",
        color=COLORS["Crypto"],
        transform=table_ax.transAxes,
    )

    table_ax.plot([0.0, 0.98], [0.835, 0.835], color="#9b8c78", linewidth=0.9)
    headers = ["Bucket", "Latest", "Avg", "Range"]
    x_positions = [0.00, 0.52, 0.70, 0.96]
    y0 = 0.79
    row_h = 0.052
    for x_pos, header in zip(x_positions, headers):
        ha = "left" if header == "Bucket" else "right"
        table_ax.text(
            x_pos,
            y0,
            header,
            fontsize=8.25,
            fontweight="bold",
            color="#4a423b",
            ha=ha,
            transform=table_ax.transAxes,
        )
    table_ax.plot([0.0, 0.98], [y0 - 0.028, y0 - 0.028], color="#9b8c78", linewidth=0.8)

    for i, (bucket, row) in enumerate(summary.iterrows()):
        y_pos = y0 - (i + 1) * row_h
        table_ax.text(
            0.00,
            y_pos,
            DISPLAY_LABELS[bucket],
            fontsize=7.8,
            color=COLORS[bucket],
            ha="left",
            transform=table_ax.transAxes,
        )
        table_ax.text(
            0.52,
            y_pos,
            f"{row['latest_weight']:.1%}",
            fontsize=7.8,
            color="#33302e",
            ha="right",
            transform=table_ax.transAxes,
        )
        table_ax.text(
            0.70,
            y_pos,
            f"{row['average_weight']:.1%}",
            fontsize=7.8,
            color="#33302e",
            ha="right",
            transform=table_ax.transAxes,
        )
        table_ax.text(
            0.96,
            y_pos,
            f"{row['min_weight']:.1%}-{row['max_weight']:.1%}",
            fontsize=7.8,
            color="#33302e",
            ha="right",
            transform=table_ax.transAxes,
        )
        table_ax.plot([0.0, 0.98], [y_pos - 0.023, y_pos - 0.023], color="#e0d2bd", linewidth=0.55)

    table_ax.text(
        0.0,
        0.085,
        "Read-through",
        fontsize=9.3,
        fontweight="bold",
        color="#33302e",
        transform=table_ax.transAxes,
    )
    table_ax.text(
        0.0,
        0.005,
        "Risk parity spreads capital broadly.\nCrypto remains a satellite weight,\nnot the core of the combined fund.",
        fontsize=8.0,
        color="#4f4942",
        linespacing=1.22,
        transform=table_ax.transAxes,
    )

    fig.text(
        0.055,
        0.055,
        "Source: NovaAlloc results/data/fund_weights.csv. Combined - Risk Parity fund only.",
        fontsize=8.2,
        color="#6b6258",
    )
    fig.text(
        0.055,
        0.031,
        "Note: Security-level monthly live weights are aggregated to equity sectors; crypto assets are grouped as one bucket.",
        fontsize=8.2,
        color="#6b6258",
    )
    fig.subplots_adjust(left=0.07, right=0.965, top=0.865, bottom=0.16)
    return fig


def main() -> None:
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    wide, summary = load_weights()
    fig = make_figure(wide, summary)
    png_path = PNG_DIR / "02_combined_risk_parity_weights.png"
    pdf_path = PDF_DIR / "02_combined_risk_parity_weights.pdf"
    fig.savefig(png_path, facecolor=fig.get_facecolor(), bbox_inches="tight")
    fig.savefig(pdf_path, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {png_path}")
    print(f"Saved {pdf_path}")


if __name__ == "__main__":
    main()


