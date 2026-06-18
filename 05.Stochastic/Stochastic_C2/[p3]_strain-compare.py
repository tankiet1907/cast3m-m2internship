"""
Consolidate shrinkage-strain histories from two stochastic analyses and
plot the mean evret(t) curve of each:

    C1 (LHS)  -> simple mean over runs
    C2 (ALEA) -> simple mean over runs

Each run CSV is produced by Cast3M:  SORT 'EXCE' evret 'SEPA' 'PVIR'
-> 2 columns, semicolon-separated:  JOURS ; MICRON/METER  (+ a header line).
"""

import os
import re
import glob
import numpy as np
import matplotlib
matplotlib.use("Agg")           # remove this line if you want an interactive window
import matplotlib.pyplot as plt

# =========================================================
# CONFIG  -- edit the folders to match your machine
# =========================================================
C1_DIR = r"D:\cast3m-m2internship\05.Stochastic\Stochastic_C1\CSV"   # LHS
C2_DIR = r"D:\cast3m-m2internship\05.Stochastic\Stochastic_C2\CSV"   # ALEA

PATTERN = "u_results_no_*.csv"

working_dir = r"D:\cast3m-m2internship\05.Stochastic\Stochastic_C2"
OUT_DIR = os.path.join(working_dir, "Plots")
os.makedirs(OUT_DIR, exist_ok=True)

OUT_PNG = os.path.join(OUT_DIR, "evret_C1_C2.png")
OUT_CSV = os.path.join(OUT_DIR, "evret_means_C1_C2.csv")

SHOW_INDIVIDUAL = True   # draw faint per-run curves behind each mean


# =========================================================
# HELPERS
# =========================================================
def run_index(path):
    """Integer found in the file name, used to sort runs in order."""
    m = re.search(r"(\d+)", os.path.basename(path))
    return int(m.group(1)) if m else 0


def load_history(path):
    """Parse one EXCE csv -> (t[days], strain[micron/m]). Robust to header/
    title lines and to comma-or-dot decimals."""
    t, y = [], []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(";")
            if len(parts) < 2:
                continue
            try:
                ti = float(parts[0].replace(",", "."))
                yi = float(parts[1].replace(",", "."))
            except ValueError:
                continue          # header / title line -> skip
            t.append(ti)
            y.append(yi)
    return np.asarray(t), np.asarray(y)


def collect(folder, pattern=PATTERN):
    """Return (t_ref, mean_curve, Y_matrix, files).
    All run curves are interpolated onto the time grid of the first run."""
    files = sorted(glob.glob(os.path.join(folder, pattern)), key=run_index)
    if not files:
        raise FileNotFoundError(f"No files matching {pattern} in {folder}")

    histories = [load_history(f) for f in files]
    t_ref = histories[0][0]
    Y = np.vstack([np.interp(t_ref, t, y) for (t, y) in histories])  # (n_runs, n_t)
    mean_curve = Y.mean(axis=0)
    return t_ref, mean_curve, Y, files


def plot_analysis(ax, t, Y, mean_curve, color, label):
    if SHOW_INDIVIDUAL:
        for row in Y:
            ax.plot(t, row, color=color, alpha=0.12, linewidth=0.8)
    ax.plot(t, mean_curve, color=color, linewidth=2.2, label=label)


# =========================================================
# MAIN
# =========================================================
if __name__ == "__main__":
    t1, m1, Y1, f1 = collect(C1_DIR)
    t2, m2, Y2, f2 = collect(C2_DIR)

    print(f"C1 (LHS)  : {len(f1)} runs")
    print(f"C2 (ALEA) : {len(f2)} runs")

    # ---- figure ----
    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    plot_analysis(ax, t1, Y1, m1, "tab:blue",   "C1 - LHS (mean)")
    plot_analysis(ax, t2, Y2, m2, "tab:orange", "C2 - ALEA (mean)")

    ax.set_xlabel("Time [days]")
    ax.set_ylabel("Longitudinal shrinkage strain [micron/m]")
    ax.set_title("Mean shrinkage history: C1 (LHS) vs C2 (ALEA)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=200)
    print(f"-> figure saved: {OUT_PNG}")

    # ---- combined CSV (both means on C1's time grid) ----
    m2i = np.interp(t1, t2, m2)
    header = "days;C1_LHS_mean;C2_ALEA_mean"
    data = np.column_stack([t1, m1, m2i])
    np.savetxt(OUT_CSV, data, delimiter=";", header=header, comments="", fmt="%.6g")
    print(f"-> means csv saved: {OUT_CSV}")

    # plt.show()   # uncomment (and remove matplotlib.use('Agg')) for a window