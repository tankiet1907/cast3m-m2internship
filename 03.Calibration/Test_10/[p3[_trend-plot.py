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
working_dir = r"D:\cast3m-m2internship\03.Calibration\Test_10"
csv_dir    = os.path.join(working_dir, "CSV")
output_dir = os.path.join(working_dir, "Trend")
os.makedirs(output_dir, exist_ok=True)

# ===================================================================
# TEST 10 CONFIGURATION
# ===================================================================
TEST_NO   = 10          # files: pg_results_no_10_KINT_..._AK_....csv
HG        = 0.001       # reduced from reference 0.018  (shown in the title)
AK_VALUES = [1, 2, 3, 4]
AK_REF    = None        # set to e.g. 2 to draw that AK solid; None = no highlight

TOK_KINT = "KINT"
TOK_AK   = "AK"

# Gas pressure : depths 10..50 mm
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
    m = re.search(re.escape(token) + r'[_-]([0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)',
                  filename)
    return float(m.group(1)) if m else None


def find_test_csv(test_no, ak):
    """Return the test-`test_no` Pg CSV whose AK matches `ak`."""
    for f in glob.glob(os.path.join(csv_dir, f"pg_results_no_{test_no}_*.csv")):
        a = get_val(os.path.basename(f), TOK_AK)
        if a is not None and math.isclose(a, ak, rel_tol=1e-3, abs_tol=1e-30):
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
# TREND PLOT : effect of AK (test 10)
# ===================================================================
def plot_trend():
    # linestyle per AK value (4 distinct styles; AK_REF solid if set)
    styles = ['-', '--', ':', '-.']
    style_map = {}
    if AK_REF is not None:
        style_map[AK_REF] = '-'
        extra = [s for s in styles if s != '-']
        i = 0
        for ak in AK_VALUES:
            if ak != AK_REF:
                style_map[ak] = extra[i]; i += 1
    else:
        for ak, s in zip(AK_VALUES, styles):
            style_map[ak] = s

    kint_found = None
    plt.figure(figsize=(10, 8))
    for ak in AK_VALUES:
        f = find_test_csv(TEST_NO, ak)
        if f is None:
            print(f"-> Missing CSV for test {TEST_NO}, AK={ak:g}, skipped.")
            continue
        if kint_found is None:
            kint_found = get_val(os.path.basename(f), TOK_KINT)
        df    = pd.read_csv(f, sep=';')
        x_col = df.columns[0]
        for dkey, col in depth_columns(df):
            plt.plot(df[x_col], df[col],
                     color=DEPTH_COLORS[dkey],
                     linestyle=style_map[ak],
                     linewidth=LINE_WIDTH)

    # ---- axes ----
    plt.xlim(0, 240)
    plt.xticks(np.arange(0, 241, 20), fontsize=10)
    plt.xlabel("Time (min)", fontsize=12)
    plt.ylabel("Gas Pressure (MPa)", fontsize=12)
    plt.ylim(0, PG_YMAX)
    plt.yticks(np.arange(0, PG_YMAX + 0.1, 0.5))

    kint_txt = f"{kint_found:.1e}" if kint_found is not None else "?"
    plt.title(rf"Test {TEST_NO} - effect of $A_\Gamma$ (AK)  "
              rf"($K_0$={kint_txt} m$^2$, $h_g$={HG:g})",
              fontsize=14, fontweight='bold')
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

    save_name = f"pg_test{TEST_NO}_AK_sweep_hg{HG:g}.png"
    plt.savefig(os.path.join(output_dir, save_name), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"-> Image saved: {save_name}")


# ===================================================================
# RUN
# ===================================================================
if __name__ == "__main__":
    print(f"Test {TEST_NO}: effect of AK {AK_VALUES} with hg={HG:g}\n")
    plot_trend()
    print(f"\n[COMPLETE] Check '{output_dir}'.")