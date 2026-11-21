#!/usr/bin/env python3
"""Parse deepecg_eval_*.log and plot 10-attempt acceptance curves."""
import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]


def parse_rates(log_path):
    rates = []
    with open(log_path) as f:
        for line in f:
            m = re.match(r"^(\d+\.\d+)\t", line.strip())
            if m:
                rates.append(float(m.group(1)))
    return rates


def main():
    orig = parse_rates(ROOT / "docs/deepecg_eval_original.log")
    spoof = parse_rates(ROOT / "docs/deepecg_eval_spoof.log")
    attempts = list(range(1, len(orig) + 1))
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(attempts, orig, "o-", label="Original ECG (genuine)")
    ax.plot(attempts, spoof, "s--", label="Spoofed ECG (PPG→ECG)")
    ax.set_xlabel("Authentication attempt")
    ax.set_ylabel("Acceptance rate")
    ax.set_title("DeepECG on BIDMC — accumulating acceptance")
    ax.set_ylim(0, 1.05)
    ax.legend()
    fig.tight_layout()
    out = ROOT / "docs/acceptance_curve_bidmc_deepecg.png"
    fig.savefig(out, dpi=150)
    print("Wrote", out)


if __name__ == "__main__":
    main()