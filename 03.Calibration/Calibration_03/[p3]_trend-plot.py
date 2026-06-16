import os
import glob
import re
import math
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

# ===================================================================
# PROJECT PATHWAYS
# ===================================================================
working_dir = r"D:\cast3m-m2internship\03.Calibration\Calibration_03"
csv_dir    = os.path.join(working_dir, "CSV")
output_dir = os.path.join(working_dir, "Trend")
os.makedirs(output_dir, exist_ok=True)

# ===================================================================
# SWEEP CONFIGURATION
# ===================================================================
# Figure 1 : KINT = 2e-19 (initial reference), AK = 3/4/5  (AK=3 reference)
#   -> not very physical and does not fit the experiment
# Figure 2 : KINT = 8.5e-20 (reduced), AK = 3/4/5
#   -> effect of reducing KINT
KINT_REF = 2e-19
KINT_LOW = 8.5e-20
AK_VALUES = [3, 4, 5]
AK_REF    = 3                 # initial reference AK -> drawn solid

# Tokens used in the CSV filenames -> adjust if your names differ
TOK_KINT = "KINT"
TOK_AK   = "AK"

# Gas pressure : depths 10..50 mm (00 mm ignored, as for Pg)
DEPTH_COLORS = {
    '10': 'red', '20': 'gold', '30': 'deeppink', '40': 'green', '50': 'cyan',
}
ACTIVE_DEPTHS = ['10', '20', '30', '40', '50']

LINE_WIDTH = 1.0
PG_YMAX    = 4.0

# ===================================================================
# HELPERS
# ===================================================================
def get_val(filename, token):
    """Extract a float (incl. scientific notation) after '<token>_'."""
    m = re.search(re.escape(token) + r'[_-]([0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)',
                  filename)
    return float(m.group(1)) if m else None


def find_csv(kint, ak):
    """Return the Pg CSV whose (KINT, AK) match the targets (relative tolerance)."""
    for f in glob.glob(os.path.join(csv_dir, "pg_results_no_*.csv")):
        name = os.path.basename(f)
        k = get_val(name, TOK_KINT)
        a = get_val(name, TOK_AK)
        if (k is not None and a is not None
                and math.isclose(k, kint, rel_tol=1e-3, abs_tol=1e-30)
                and math.isclose(a, ak, rel_tol=1e-3, abs_tol=1e-30)):
            return f
    return None


def depth_columns(df):
    out = []
    for col in df.columns[1:]:
        m = re.search(r'(\d+)', col)
        if m:
            key = m.group(1).zfill(2)
            if key in ACTIVE_DEPTHS:
                out.append((key, col))
    return out


# ===================================================================
# TREND PLOT : effect of AK at a fixed KINT
# ===================================================================
def plot_trend(kint, title, save_name):
    # linestyle per AK value : reference solid, others dashed/dotted
    style_map, extra, i = {AK_REF: '-'}, ['--', ':', '-.'], 0
    for ak in AK_VALUES:
        if ak != AK_REF:
            style_map[ak] = extra[i]; i += 1

    plt.figure(figsize=(10, 8))
    for ak in AK_VALUES:
        f = find_csv(kint, ak)
        if f is None:
            print(f"-> Missing CSV for KINT={kint:.2e}, AK={ak:g}, skipped.")
            continue
        df    = pd.read_csv(f, sep=';')
        x_col = df.columns[0]
        for dkey, col in depth_columns(df):
            plt.plot(df[x_col], df[col],
                     color=DEPTH_COLORS[dkey],
                     linestyle=style_map[ak],
                     linewidth=LINE_WIDTH)

    # ---- axes (gas pressure) ----
    plt.xlim(0, 240)
    plt.xticks(np.arange(0, 241, 20), fontsize=10)
    plt.xlabel("Time (min)", fontsize=12)
    plt.ylabel("Gas Pressure (MPa)", fontsize=12)
    plt.ylim(0, PG_YMAX)
    plt.yticks(np.arange(0, PG_YMAX + 0.1, 0.5))
    plt.title(title, fontsize=14, fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.6)

    # ---- two legends : depth (colour) + AK (linestyle) ----
    depth_handles = [Line2D([0], [0], color=DEPTH_COLORS[d], lw=LINE_WIDTH,
                            label=f"{d}mm") for d in ACTIVE_DEPTHS]
    ak_handles = [Line2D([0], [0], color='black', lw=LINE_WIDTH,
                         linestyle=style_map[ak],
                         label=f"AK={ak:g}" + (" (ref)" if ak == AK_REF else ""))
                  for ak in AK_VALUES]
    leg1 = plt.legend(handles=depth_handles, loc="upper left", fontsize=9, title="Depth")
    plt.gca().add_artist(leg1)
    plt.legend(handles=ak_handles, loc="upper right", fontsize=10, title=r"$A_\Gamma$ (AK)")

    out = os.path.join(output_dir, save_name)
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"-> Image saved: {save_name}")


# ===================================================================
# RUN  -> 2 figures
# ===================================================================
if __name__ == "__main__":
    print("Calibration 03 - effect of AK at two KINT levels\n")

    plot_trend(KINT_REF,
               title=rf"Effect of $A_\Gamma$ (AK) at $K_0$ = {KINT_REF:.1e} m$^2$",
               save_name="pg_AK_sweep_KINT_2e-19.png")

    plot_trend(KINT_LOW,
               title=rf"Effect of $A_\Gamma$ (AK) at reduced $K_0$ = {KINT_LOW:.1e} m$^2$",
               save_name="pg_AK_sweep_KINT_8.5e-20.png")

    print(f"\n[COMPLETE] Check '{output_dir}'.")