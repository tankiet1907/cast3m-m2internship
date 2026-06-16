import os
import glob
import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

# =========================================================
# PROJECT PATHWAYS
# =========================================================
working_dir = r"D:\cast3m-m2internship\03.Calibration\Calibration_01"
csv_dir    = os.path.join(working_dir, "CSV")
output_dir = os.path.join(working_dir, "Trend")     # <-- output folder: Trend
os.makedirs(output_dir, exist_ok=True)

# =========================================================
# SWEEP VALUES AND PRELIMINARY CHOSEN (BASELINE) PARAMETERS
# =========================================================
EPSILON_VALUES = [0.65, 0.68, 0.72]
H_VALUES       = [9.0, 10.0, 11.0]

EPSILON_BASE   = 0.68          # selected emissivity
H_BASE         = 11.0          # selected h_hot

# Depth colours (Cast3M standard) and the depths to draw
DEPTH_COLORS = {
    '00': 'blue', '10': 'red',   '20': 'gold',
    '30': 'deeppink', '40': 'green', '50': 'cyan',
}
ACTIVE_DEPTHS = ['00', '10', '20', '30', '40', '50']

LINE_WIDTH = 1.0             # equal thickness for every curve

# =========================================================
# HELPERS
# =========================================================
def parse_params(filename):
    """Return (epsilon, h_hot) as floats from a filename, else (None, None)."""
    m = re.search(r'epsilon_([^_]+)_h-hot_(.+)\.csv', filename)
    if m:
        try:
            return float(m.group(1)), float(m.group(2))
        except ValueError:
            return None, None
    return None, None


def load_temp_table():
    """Map (epsilon, h_hot) -> filepath for every temperature CSV."""
    files = glob.glob(os.path.join(csv_dir, "temp_results_no_*.csv"))
    table = {}
    for f in files:
        eps, h = parse_params(os.path.basename(f))
        if eps is not None:
            table[(round(eps, 3), round(h, 3))] = f
    return table


def depth_columns(df):
    """Return ordered [(depth_key, column_name)] for the active depths."""
    out = []
    for col in df.columns[1:]:
        m = re.search(r'(\d+)', col)
        if m:
            key = m.group(1).zfill(2)
            if key in ACTIVE_DEPTHS:
                out.append((key, col))
    return out


# =========================================================
# SENSITIVITY PLOT (all depths, equal line thickness)
# =========================================================
def plot_sensitivity(table, sweep_param):
    """
    sweep_param == 'epsilon' : vary epsilon, fix h_hot = H_BASE
    sweep_param == 'h'       : vary h_hot, fix epsilon = EPSILON_BASE
    Colour  -> depth ; Linestyle -> swept parameter value.
    """
    if sweep_param == 'epsilon':
        values, base_val = EPSILON_VALUES, EPSILON_BASE
        title      = rf"Effect of $\epsilon$  ($h_{{hot}}$ = {H_BASE:g} fixed)"
        save_name  = "surf_eps_sweep.png"
        style_lbl  = lambda v: rf"$\epsilon$ = {v:g}"
        legend_ttl = "Emissivity"
    else:
        values, base_val = H_VALUES, H_BASE
        title      = rf"Effect of $h_{{hot}}$  ($\epsilon$ = {EPSILON_BASE:g} fixed)"
        save_name  = "surf_h_sweep.png"
        style_lbl  = lambda v: rf"$h_{{hot}}$ = {v:g}"
        legend_ttl = "h_hot"

    # linestyle per value: the selected value is solid, the others dashed/dotted
    style_map = {base_val: '-'}
    for v, s in zip([v for v in values if abs(v - base_val) > 1e-3], ['--', ':', '-.']):
        style_map[v] = s

    plt.figure(figsize=(10, 8))

    for val in values:
        key = (round(val, 3), round(H_BASE, 3)) if sweep_param == 'epsilon' \
              else (round(EPSILON_BASE, 3), round(val, 3))
        fpath = table.get(key)
        if fpath is None:
            print(f"-> Missing CSV for {key}, skipped.")
            continue

        df    = pd.read_csv(fpath, sep=';')
        x_col = df.columns[0]
        for dkey, col in depth_columns(df):
            plt.plot(df[x_col], df[col],
                     color=DEPTH_COLORS[dkey],
                     linestyle=style_map[val],
                     linewidth=LINE_WIDTH)

    # ---- fixed axes ----
    plt.xlim(0, 240)
    plt.xticks(np.arange(0, 241, 20), fontsize=10)
    plt.xlabel("Time (min)", fontsize=12)
    plt.ylabel("Temperature (°C)", fontsize=12)
    plt.ylim(0, 500)
    plt.yticks(np.arange(0, 501, 50))
    plt.title(title, fontsize=14, fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.6)

    # ---- two legends: depth (colour) + parameter value (linestyle) ----
    depth_handles = [Line2D([0], [0], color=DEPTH_COLORS[d], lw=LINE_WIDTH,
                            label=f"{d}mm") for d in ACTIVE_DEPTHS]
    style_handles = [Line2D([0], [0], color='black', lw=LINE_WIDTH,
                            linestyle=style_map[v],
                            label=style_lbl(v) + (" (selected)"
                                  if abs(v - base_val) < 1e-3 else ""))
                     for v in values]

    leg1 = plt.legend(handles=depth_handles, loc="upper left",
                      fontsize=9, title="Depth")
    plt.gca().add_artist(leg1)
    plt.legend(handles=style_handles, loc="lower right",
               fontsize=10, title=legend_ttl)

    out = os.path.join(output_dir, save_name)
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"-> Image saved: {save_name}")


# =========================================================
# RUN
# =========================================================
if __name__ == "__main__":
    table = load_temp_table()
    print(f"Found {len(table)} temperature CSV files with (epsilon, h_hot).\n")

    print("--- Sensitivity to epsilon (h_hot fixed) ---")
    plot_sensitivity(table, 'epsilon')

    print("\n--- Sensitivity to h_hot (epsilon fixed) ---")
    plot_sensitivity(table, 'h')

    print(f"\n[COMPLETE] Check '{output_dir}'.")