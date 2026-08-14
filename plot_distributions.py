#!/usr/bin/env python3
"""Histogram plots for the SWB-1 silence & floor-transfer-offset distributions.

Reads the raw event dump written by `per_conversation_swbd.py`
(`results/swbd_silences.csv`: conversation_id, type in {pause, gap, overlap},
value_s) and renders one histogram per requested distribution:

  * pause  — within-turn same-speaker silence (s), positive
  * gap    — between-speaker silence at a floor transfer (positive FTO)
  * fto    — the full signed floor-transfer offset (gap U overlap U exact-0
             flush); the 0 line is drawn and the overlap region (value < 0)
             shaded

    python plot_distributions.py \
        --silences results/swbd_silences.csv --out-dir results/plots

Use `--log-count` for the heavy tails. `--{pause,gap,fto}-xlim` set the axis
range; values outside it are folded into the edge (overflow) bins, and the
caption reports how many. Caption stats are over the full, unclipped data.
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from collections import defaultdict

import numpy as np

import matplotlib

matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt  # noqa: E402


def load_silences(path):
    """type -> np.array(value_s). fto = gap U overlap."""
    by_type = defaultdict(list)
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            by_type[row["type"]].append(float(row["value_s"]))
    out = {k: np.asarray(v, dtype=float) for k, v in by_type.items()}
    out["fto"] = np.concatenate(
        [out.get("gap", np.array([])), out.get("overlap", np.array([])),
         out.get("flush", np.array([]))]  # exact-0 transfers complete the FTOs
    )
    return out


def _stats_caption(a):
    return (f"n={a.size:,}  mean={a.mean():.3f}s  median={np.median(a):.3f}s  "
            f"p10={np.percentile(a, 10):.3f}  p90={np.percentile(a, 90):.3f}")


def plot_hist(a, title, out_path, bin_width, xlim, log_count, signed=False):
    if a.size == 0:
        print(f"  (skip {title}: no data)", file=sys.stderr)
        return
    lo, hi = (xlim if xlim else (float(a.min()), float(a.max())))
    lo = float(np.floor(lo / bin_width) * bin_width)
    hi = float(np.ceil(hi / bin_width) * bin_width)
    # linspace, not arange: arange's float drift can leave edges[-1] < hi, and
    # np.clip lands the whole right tail exactly on hi -- outside the last bin,
    # silently dropping it. linspace guarantees edges[-1] == hi.
    edges = np.linspace(lo, hi, int(round((hi - lo) / bin_width)) + 1)
    n_lo = int((a < lo).sum())
    n_hi = int((a > hi).sum())
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    ax.hist(np.clip(a, lo, hi), bins=edges, color="#3b6ea5", edgecolor="none")
    if signed:
        ax.axvline(0.0, color="black", lw=1)
        ax.axvspan(lo, 0.0, color="#d9534f", alpha=0.10)  # overlap region
        ax.text(0.01, 0.95, "overlap", color="#a33", transform=ax.transAxes,
                ha="left", va="top", fontsize=9)
        ax.text(0.99, 0.95, "gap", color="#357", transform=ax.transAxes,
                ha="right", va="top", fontsize=9)
    if log_count:
        ax.set_yscale("log")
    ax.set_xlim(lo, hi)
    ax.set_xlabel("seconds")
    ax.set_ylabel("count" + (" (log)" if log_count else ""))
    ax.set_title(title)
    ax.margins(x=0)
    cap = _stats_caption(a)
    if n_lo or n_hi:
        cap += (f"   [edge bins fold in the out-of-range tail: "
                f"{n_lo:,} < {lo:g}s, {n_hi:,} > {hi:g}s]")
    fig.text(0.5, -0.02, cap, ha="center", fontsize=8, color="#555")
    fig.tight_layout()
    fig.savefig(out_path, dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {out_path}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--silences", default="results/swbd_silences.csv")
    ap.add_argument("--out-dir", default="results/plots")
    ap.add_argument("--bin-width", type=float, default=0.05)
    ap.add_argument("--pause-xlim", type=float, nargs=2, default=(0.0, 5.0))
    ap.add_argument("--gap-xlim", type=float, nargs=2, default=(0.0, 5.0))
    ap.add_argument("--fto-xlim", type=float, nargs=2, default=(-3.0, 3.0))
    ap.add_argument("--log-count", action="store_true",
                    help="log-scale the count axis (heavy tails)")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    d = load_silences(args.silences)
    j = os.path.join
    plot_hist(d.get("pause", np.array([])), "SWB-1 pause durations (within-turn)",
              j(args.out_dir, "pause_hist.png"), args.bin_width, args.pause_xlim,
              args.log_count)
    plot_hist(d.get("gap", np.array([])), "SWB-1 gap durations (between-speaker)",
              j(args.out_dir, "gap_hist.png"), args.bin_width, args.gap_xlim,
              args.log_count)
    plot_hist(d.get("fto", np.array([])), "SWB-1 floor-transfer offset (signed)",
              j(args.out_dir, "fto_hist.png"), args.bin_width, args.fto_xlim,
              args.log_count, signed=True)


if __name__ == "__main__":
    main()
