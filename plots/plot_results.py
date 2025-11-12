#!/usr/bin/env python3
import argparse
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, os.pardir))


def read_orders_csv(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        sys.exit(f"Orders CSV not found: {path}")
    df = pd.read_csv(path)
    required_cols = {"ts_ns", "qty", "limit_px"}
    missing = required_cols.difference(df.columns)
    if missing:
        sys.exit(f"Orders CSV missing columns: {', '.join(sorted(missing))}")
    df["ts_ns"] = pd.to_numeric(df["ts_ns"], errors="coerce")
    df["qty"] = pd.to_numeric(df["qty"], errors="coerce")
    df["limit_px"] = pd.to_numeric(df["limit_px"], errors="coerce")
    df = df.dropna(subset=["ts_ns", "qty", "limit_px"]).reset_index(drop=True)
    return df


def read_summary_csv(path: str) -> pd.Series:
    if not os.path.exists(path):
        sys.exit(f"Summary CSV not found: {path}")
    df = pd.read_csv(path)
    required_cols = {"avg_px", "slippage_bps"}
    missing = required_cols.difference(df.columns)
    if missing:
        sys.exit(f"Summary CSV missing columns: {', '.join(sorted(missing))}")
    if df.empty:
        sys.exit("Summary CSV is empty.")
    row = df.iloc[0]
    row["avg_px"] = pd.to_numeric(row["avg_px"], errors="coerce")
    row["slippage_bps"] = pd.to_numeric(row["slippage_bps"], errors="coerce")
    if pd.isna(row["avg_px"]) or pd.isna(row["slippage_bps"]):
        sys.exit("Summary CSV contains non-numeric values in metrics.")
    return row


def plot_orders(df: pd.DataFrame, output_path: str) -> None:
    time_min = df["ts_ns"] / 1e9 / 60.0

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(time_min, df["qty"], marker="o", linewidth=1, markersize=3, label="Quantity", color="tab:blue")
    ax.set_xlabel("Time (minutes)")
    ax.set_ylabel("Quantity per slice", color="tab:blue")
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.set_title("Order Slices Over Time")

    if df["limit_px"].nunique() > 1:
        ax2 = ax.twinx()
        ax2.plot(time_min, df["limit_px"], color="tab:orange", alpha=0.75, label="Limit Price")
        ax2.set_ylabel("Limit Price", color="tab:orange")
    else:
        const_px = float(df["limit_px"].iloc[0])
        ax.axhline(y=ax.get_ylim()[0], color="none")  
        ax.text(
            0.02, 0.95, f"Limit Px: {const_px:.0f}",
            transform=ax.transAxes, ha="left", va="top",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
            color="tab:orange"
        )

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_summary(summary: pd.Series, output_path: str) -> None:
    avg_px = float(summary["avg_px"])
    slippage_bps = float(summary["slippage_bps"])

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(["Slippage (bps)"], [slippage_bps], color="tab:red", alpha=0.8)
    ax.set_ylim(bottom=0)
    ax.set_ylabel("Basis points")
    ax.set_title("Execution Summary")

    ax.bar_label(ax.containers[0], fmt="%.3f", padding=4)

    ax.text(
        0.98, 0.98, f"Avg Px: {avg_px:.4f}",
        transform=ax.transAxes, ha="right", va="top",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.9)
    )
    ax.grid(axis="y", linestyle="--", alpha=0.3)

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_report(df_orders: pd.DataFrame, summary: pd.Series, output_path: str) -> None:
    time_min = df_orders["ts_ns"] / 1e9 / 60.0
    avg_px = float(summary["avg_px"])
    slippage_bps = float(summary["slippage_bps"])

    fig, axes = plt.subplots(2, 1, figsize=(10, 9), constrained_layout=True)

    ax = axes[0]
    ax.plot(time_min, df_orders["qty"], marker="o", linewidth=1, markersize=3, label="Quantity", color="tab:blue")
    ax.set_xlabel("Time (minutes)")
    ax.set_ylabel("Quantity per slice", color="tab:blue")
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.set_title("Order Slices Over Time")
    if df_orders["limit_px"].nunique() > 1:
        ax2 = ax.twinx()
        ax2.plot(time_min, df_orders["limit_px"], color="tab:orange", alpha=0.75, label="Limit Price")
        ax2.set_ylabel("Limit Price", color="tab:orange")
    else:
        const_px = float(df_orders["limit_px"].iloc[0])
        ax.text(
            0.02, 0.95, f"Limit Px: {const_px:.0f}",
            transform=ax.transAxes, ha="left", va="top",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
            color="tab:orange"
        )

    axb = axes[1]
    axb.bar(["Slippage (bps)"], [slippage_bps], color="tab:red", alpha=0.8)
    axb.set_ylim(bottom=0)
    axb.set_ylabel("Basis points")
    axb.set_title("Execution Summary")
    axb.bar_label(axb.containers[0], fmt="%.3f", padding=4)
    axb.text(
        0.98, 0.98, f"Avg Px: {avg_px:.4f}",
        transform=axb.transAxes, ha="right", va="top",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.9)
    )
    axb.grid(axis="y", linestyle="--", alpha=0.3)

    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot orders and summary CSVs.")
    parser.add_argument(
        "--orders",
        default=os.path.join(REPO_ROOT, "build", "orders.csv"),
        help="Path to orders.csv (default: <repo>/build/orders.csv)",
    )
    parser.add_argument(
        "--summary",
        default=os.path.join(REPO_ROOT, "build", "summary.csv"),
        help="Path to summary.csv (default: <repo>/build/summary.csv)",
    )
    parser.add_argument(
        "--outdir",
        default=os.path.join(REPO_ROOT, "plots", "build"),
        help="Directory to write plots (default: <repo>/plots/build)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_dir(args.outdir)

    orders_df = read_orders_csv(args.orders)
    summary_row = read_summary_csv(args.summary)

    orders_plot_path = os.path.join(args.outdir, "orders_plot.png")
    summary_plot_path = os.path.join(args.outdir, "summary_plot.png")
    report_plot_path = os.path.join(args.outdir, "report.png")

    plot_orders(orders_df, orders_plot_path)
    plot_summary(summary_row, summary_plot_path)
    plot_report(orders_df, summary_row, report_plot_path)

    print("Wrote plots:")
    print(f" - {orders_plot_path}")
    print(f" - {summary_plot_path}")
    print(f" - {report_plot_path}")


if __name__ == "__main__":
    main()


