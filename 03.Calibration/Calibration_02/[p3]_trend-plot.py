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
working_dir = r"D:\cast3m-m2internship\03.Calibration\Calibration_02"
csv_dir    = os.path.join(working_dir, "CSV")
output_dir = os.path.join(working_dir, "Trend")
os.makedirs(output_dir, exist_ok=True)

# =========================================================
# REFERENCE SET (inherited from Calibration 01) AND SELECTED VALUES
# =========================================================
# Reference (starting point) : eps=0.68, h=11, cp=948, KS(lambda)=1.67
EPS_REF, H_REF, CP_REF, LAM_REF = 0.68, 11.0, 948, 1.67

# Selected endpoint of each step
LAM_SEL = 1.38      # KS reduced  1.67 -> 1.38
EPS_SEL = 0.6       # epsilon re-calibrated down 0.68 -> 0.6
CP_SEL  = 960       # CS increased 948 -> 960

# Swept values for each figure
LAMBDA_VALUES  = [1.67, 1.55, 1.38]     # Fig 2 : KS decreasing
EPSILON_VALUES = [0.68, 0.6]            # Fig 3 : epsilon re-calibration
CP_VALUES      = [948, 955, 960]        # Fig 4 : CS increasing

# Tokens used in the CSV filenames  -> adjust here if your names differ
TOK_EPS, TOK_H, TOK_CP, TOK_LAM = "epsilon", "h-hot", "cp", "lamda"

# Depth colours (Cast3M standard) and depths drawn
DEPTH_COLORS = {
    '00': 'blue', '10': 'red',   '20': 'gold',
    '30': 'deeppink', '40': 'green', '50': 'cyan',
}
ACTIVE_DEPTHS = ['00', '10', '20', '30', '40', '50']
LINE_WIDTH = 1.0                         # weight = 1

# =========================================================
# HELPERS
# =========================================================
def get_val(filename, token):
    m = re.search(re.escape(token) + r'[_-]([0-9]+(?:\.[0-9]+)?)', filename)
    return float(m.group(1)) if m else None


def load_temp_table():
    """Map (eps, h, cp, lam) -> filepath for every temperature CSV."""
    files = glob.glob(os.path.join(csv_dir, "temp_results_no_*.csv"))
    table = {}
    for f in files:
        name = os.path.basename(f)
        eps = get_val(name, TOK_EPS); h = get_val(name, TOK_H)
        cp  = get_val(name, TOK_CP);  lam = get_val(name, TOK_LAM)
        if None not in (eps, h, cp, lam):
            table[(round(eps, 3), round(h, 3), round(cp, 3), round(lam, 3))] = f
    return table


def depth_columns(df):
    out = []
    for col in df.columns[1:]:
        m = re.search(r'(\d+)', col)
        if m:
            key = m.group(1).zfill(2)
            if key in ACTIVE_DEPTHS:
                out.append((key, col))
    return out


def key(eps, h, cp, lam):
    return (round(eps, 3), round(h, 3), round(cp, 3), round(lam, 3))


# =========================================================
# GENERIC TREND PLOT (all depths, equal thickness = 1)
# =========================================================
def plot_trend(table, curves, title, save_name, legend_title):
    style_map, extra, i = {}, ['--', ':', '-.'], 0
    for c in curves:
        if c['base']:
            style_map[c['value']] = '-'
        else:
            style_map[c['value']] = extra[i]; i += 1

    plt.figure(figsize=(10, 8))
    for c in curves:
        fpath = table.get(c['key'])
        if fpath is None:
            print(f"-> Missing CSV for {c['key']}, skipped.")
            continue
        df    = pd.read_csv(fpath, sep=';')
        x_col = df.columns[0]
        for dkey, col in depth_columns(df):
            plt.plot(df[x_col], df[col],
                     color=DEPTH_COLORS[dkey],
                     linestyle=style_map[c['value']],
                     linewidth=LINE_WIDTH)

    plt.xlim(0, 240)
    plt.xticks(np.arange(0, 241, 20), fontsize=10)
    plt.xlabel("Time (min)", fontsize=12)
    plt.ylabel("Temperature (°C)", fontsize=12)
    plt.ylim(0, 500)
    plt.yticks(np.arange(0, 501, 50))
    plt.title(title, fontsize=14, fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.6)

    depth_handles = [Line2D([0], [0], color=DEPTH_COLORS[d], lw=LINE_WIDTH,
                            label=f"{d}mm") for d in ACTIVE_DEPTHS]
    style_handles = [Line2D([0], [0], color='black', lw=LINE_WIDTH,
                            linestyle=style_map[c['value']],
                            label=f"{c['value']:g}" + (" (selected)" if c['base'] else ""))
                     for c in curves]
    leg1 = plt.legend(handles=depth_handles, loc="upper left",
                      fontsize=9, title="Depth")
    plt.gca().add_artist(leg1)
    plt.legend(handles=style_handles, loc="lower right",
               fontsize=10, title=legend_title)

    out = os.path.join(output_dir, save_name)
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"-> Image saved: {save_name}")


# =========================================================
# RUN  ->  Fig 2 (KS down), Fig 3 (eps recal), Fig 4 (CS up)
# =========================================================
if __name__ == "__main__":
    table = load_temp_table()
    print(f"Found {len(table)} temperature CSV files.\n")

    # Fig 2 : decreasing KS, fixed eps/h/cp at reference
    curves_ks = [{'value': lam,
                  'key':   key(EPS_REF, H_REF, CP_REF, lam),
                  'base':  abs(lam - LAM_SEL) < 1e-3} for lam in LAMBDA_VALUES]
    plot_trend(table, curves_ks,
               title=rf"Step 1 - decreasing $\lambda_{{d0}}$ (KS)  "
                     rf"($\epsilon$={EPS_REF:g}, $h_{{hot}}$={H_REF:g}, $C_{{ps}}$={CP_REF:g})",
               save_name="depth_KS_sweep.png", legend_title=r"$\lambda_{d0}$ (KS)")

    # Fig 3 : epsilon re-calibration, fixed h/cp at reference, KS at selected
    curves_eps = [{'value': eps,
                   'key':   key(eps, H_REF, CP_REF, LAM_SEL),
                   'base':  abs(eps - EPS_SEL) < 1e-3} for eps in EPSILON_VALUES]
    plot_trend(table, curves_eps,
               title=rf"Step 2 - re-calibration of $\epsilon$  "
                     rf"($h_{{hot}}$={H_REF:g}, $C_{{ps}}$={CP_REF:g}, $\lambda_{{d0}}$={LAM_SEL:g})",
               save_name="depth_eps_recal.png", legend_title=r"$\epsilon$")

    # Fig 4 : increasing CS, eps at selected, h at reference, KS at selected
    curves_cs = [{'value': cp,
                  'key':   key(EPS_SEL, H_REF, cp, LAM_SEL),
                  'base':  abs(cp - CP_SEL) < 1e-3} for cp in CP_VALUES]
    plot_trend(table, curves_cs,
               title=rf"Step 3 - increasing $C_{{ps}}$ (CS)  "
                     rf"($\epsilon$={EPS_SEL:g}, $h_{{hot}}$={H_REF:g}, $\lambda_{{d0}}$={LAM_SEL:g})",
               save_name="depth_CS_sweep.png", legend_title=r"$C_{ps}$ (CS)")

    print(f"\n[COMPLETE] Check '{output_dir}'.")