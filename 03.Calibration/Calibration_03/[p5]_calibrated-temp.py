import os
import glob
import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
from matplotlib.lines import Line2D

# ===================================================================
# PROJECT PATHWAYS
# ===================================================================
# Trỏ đến thư mục Calibration 03 (chứa kết quả sau khi đã fix Gas Pressure)
working_dir = r"D:\cast3m-m2internship\03.Calibration\Calibration_03"
csv_dir    = os.path.join(working_dir, "CSV")
output_dir = os.path.join(working_dir, "Calibrated")
os.makedirs(output_dir, exist_ok=True)

# ===================================================================
# TARGET PARAMETERS (Gas Pressure Calibration)
# ===================================================================
TARGET_RUN = {
    "name": "Temperature Profile (Post-Gas Pressure Calibration)",
    "kint": 8.5e-20,
    "ak": 4.0,
    "save": "Temp_compare_final_calibration.png"
}

SHOW_120MM = False

# Tokens used in the CSV filenames
TOK_KINT = "KINT"
TOK_AK   = "AK"

# Depth colours: Giữ lại '00' vì đây là biểu đồ Temperature
colors = {
    '00': 'blue', '10': 'red', '20': 'gold',
    '30': 'deeppink', '40': 'green', '50': 'cyan', '120': 'black',
}
ACTIVE_DEPTHS = ['00', '10', '20', '30', '40', '50']

# ===================================================================
# REFERENCE DATA : DAUTI (dashed) AND EXPERIMENTAL (dotted)
# ===================================================================
time_dauti = np.arange(0, 245, 5)
time_exp   = np.arange(5, 245, 5)

DAUTI = {
 '00':[20.0,116.6,158.0,186.7,204.9,225.2,239.2,251.0,261.5,272.0,281.1,289.5,296.5,303.5,310.5,316.1,323.1,329.4,334.3,339.2,344.8,349.7,355.2,359.4,363.6,368.5,372.7,376.2,379.7,381.8,384.6,386.7,388.8,390.2,392.3,393.7,395.1,396.5,397.9,399.3,400.7,402.1,403.5,404.9,405.6,407.0,407.7,408.4,408.4],
 '10':[20.0,65.7,103.5,131.5,154.5,169.9,184.6,197.2,209.1,219.6,230.8,239.2,247.6,255.2,262.2,269.2,275.5,281.8,288.1,294.4,300.0,304.9,309.8,315.4,320.3,325.2,329.4,334.3,337.8,340.6,344.8,346.9,350.3,352.4,355.2,356.6,359.4,361.5,363.6,365.7,368.5,369.9,372.0,373.4,374.8,376.2,377.6,379.0,380.4],
 '20':[20.0,39.2,65.7,89.5,110.5,129.4,145.5,155.9,167.8,177.6,187.4,195.8,205.6,213.3,220.3,226.6,234.3,241.3,246.9,253.1,258.7,264.3,270.6,276.2,281.1,286.0,290.9,295.1,299.3,304.2,307.7,311.9,315.4,318.2,321.0,323.8,326.6,329.4,332.2,334.3,336.4,338.5,340.6,343.4,344.8,346.9,349.7,351.0,353.1],
 '30':[20.0,26.6,46.2,64.3,81.8,97.9,111.9,123.1,135.0,144.1,154.5,162.9,171.3,178.3,186.0,193.0,200.0,206.3,211.9,218.2,224.5,230.1,235.7,240.6,246.2,251.7,256.6,261.5,265.7,270.6,274.8,279.0,283.2,286.0,290.2,293.0,295.8,299.3,302.1,304.9,307.7,310.5,312.6,315.4,318.2,319.6,322.4,323.8,325.9],
 '40':[20.0,23.1,30.8,43.4,58.0,72.0,83.9,94.4,105.6,116.1,124.5,133.6,142.0,149.0,157.3,163.6,169.9,176.9,183.9,189.5,195.1,201.4,206.3,211.2,216.8,221.7,226.6,231.5,235.0,240.6,244.8,249.0,253.8,256.6,260.8,263.6,267.8,270.6,274.1,277.6,281.1,283.9,286.0,288.8,291.6,294.4,297.2,299.3,301.4],
 '50':[20.0,20.3,25.2,33.6,42.7,53.1,63.6,72.7,82.5,92.3,100.0,109.1,116.8,124.5,131.5,138.5,144.8,151.7,158.7,164.3,169.9,175.5,181.8,187.4,192.3,197.2,202.1,207.0,211.9,216.1,221.0,224.5,228.7,232.9,236.4,239.9,243.4,246.2,249.7,253.1,256.6,259.4,262.2,265.7,268.5,271.3,273.4,276.2,279.0],
}

EXP = {
 '00':[85.5,132.8,164.0,186.3,205.8,222.3,236.5,250.0,261.5,273.1,283.6,291.5,299.3,307.1,314.9,321.3,326.9,332.5,338.2,343.8,349.4,354.1,357.6,361.0,364.4,367.9,371.3,374.7,378.2,380.9,383.0,385.1,387.2,389.3,391.5,393.6,395.7,397.8,399.2,400.7,402.1,403.6,405.0,406.5,407.9,409.4,410.9,412.3],
 '10':[58.4,98.0,128.8,150.1,170.6,183.4,196.1,208.8,216.1,223.4,228.8,238.5,246.9,254.5,262.1,269.7,275.8,280.2,284.7,289.1,293.6,298.0,302.4,306.9,311.3,315.8,320.2,324.7,329.1,332.0,334.3,336.5,338.8,341.1,343.4,345.6,347.9,350.2,352.5,354.7,356.6,358.2,359.8,361.5,363.1,364.7,366.3,367.9],
 '20':[40.3,63.7,87.1,110.5,124.8,139.1,153.4,167.7,179.3,188.7,198.1,206.5,214.0,221.4,228.9,232.6,236.1,240.7,246.6,252.5,258.4,264.3,269.2,273.3,277.4,281.5,285.6,289.7,293.8,297.5,300.3,303.2,306.1,308.9,311.8,314.7,317.5,320.4,323.3,325.8,327.8,329.8,331.7,333.7,335.7,337.7,339.7,341.7],
 '30':[35.7,51.4,67.1,83.4,100.0,114.3,126.0,137.7,149.3,161.0,171.8,178.2,184.5,190.9,197.3,203.7,210.0,214.8,219.5,224.3,229.0,233.8,238.5,243.3,248.0,252.6,256.0,259.3,262.7,266.0,269.4,272.7,276.1,279.4,282.8,286.0,288.3,290.7,293.0,295.4,297.7,300.1,302.4,304.8,307.1,309.5,311.8,314.2],
 '40':[25.9,37.9,52.0,65.7,79.3,93.8,107.9,119.7,131.5,143.2,151.4,159.1,166.7,174.4,182.0,189.3,195.1,200.9,206.7,212.4,217.4,221.6,225.7,229.9,233.4,235.3,237.2,239.1,241.0,242.9,248.9,251.7,254.6,257.4,260.2,263.0,265.8,268.7,271.5,274.2,276.8,279.4,282.0,284.0,286.0,288.0,290.1,292.1],
 '50':[23.6,30.6,41.7,53.3,64.8,76.3,87.0,97.3,107.6,117.1,125.0,132.9,140.8,147.9,154.6,161.4,168.1,174.8,180.0,184.5,189.0,193.6,197.9,201.7,205.6,209.4,213.0,216.0,219.0,222.0,225.0,227.9,230.1,232.3,234.6,236.6,237.9,239.3,240.6,241.9,243.3,244.6,246.1,248.0,250.0,251.9,253.9,255.8],
 '120':[22.6,24.6,29.6,34.5,39.5,44.4,49.3,54.4,59.5,64.5,69.6,74.6,79.7,84.8,89.8,94.9,99.9,105.0,109.1,113.1,117.0,121.0,124.9,128.9,132.8,136.7,138.8,140.8,142.9,144.9,146.9,149.0,151.0,153.0,155.1,156.8,157.9,159.0,160.1,161.3,162.4,163.5,164.6,165.8,166.9,168.0,169.1,170.3],
}

# ===================================================================
# HELPERS
# ===================================================================
def get_val(filename, token):
    """Extract a float (incl. scientific notation) after '<token>_'."""
    m = re.search(re.escape(token) + r'[_-]([0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)', filename)
    return float(m.group(1)) if m else None

def find_csv(kint, ak):
    """Return the temperature CSV whose KINT and AK match the target set."""
    for f in glob.glob(os.path.join(csv_dir, "temp_results_no_*.csv")):
        name = os.path.basename(f)
        k = get_val(name, TOK_KINT)
        a = get_val(name, TOK_AK)
        if (k is not None and a is not None
                and math.isclose(k, kint, rel_tol=1e-3, abs_tol=1e-30)
                and math.isclose(a, ak, rel_tol=1e-3, abs_tol=1e-30)):
            return f
    return None

# ===================================================================
# PLOT
# ===================================================================
def plot_compare(run_config):
    csv_file = find_csv(run_config["kint"], run_config["ak"])
    if csv_file is None:
        print(f"-> No CSV matches {run_config['name']} "
              f"(KINT={run_config['kint']}, AK={run_config['ak']}).")
        return

    df    = pd.read_csv(csv_file, sep=';')
    x_col = df.columns[0]
    plt.figure(figsize=(10, 8))

    # ---- simulation : solid ----
    for y_col in df.columns[1:]:
        md = re.search(r'(\d+)', y_col)
        if not md:
            continue
        depth = md.group(1).zfill(2)
        if depth in ACTIVE_DEPTHS or (depth == '120' and SHOW_120MM):
            plt.plot(df[x_col], df[y_col], color=colors.get(depth, 'gray'),
                     linestyle='-', linewidth=1.3)

    # ---- Dauti (dashed) + Exp (dotted) ----
    for d in ACTIVE_DEPTHS:
        if d in DAUTI:
            plt.plot(time_dauti, DAUTI[d], color=colors[d], linestyle='--', linewidth=1.1)
        if d in EXP:
            plt.plot(time_exp, EXP[d], color=colors[d], linestyle=':', linewidth=1.6)
    if SHOW_120MM and '120' in EXP:
        plt.plot(time_exp, EXP['120'], color=colors['120'], linestyle=':', linewidth=1.6)

    # ---- axes ----
    plt.xlim(0, 240)
    plt.xticks(np.arange(0, 241, 20), fontsize=10)
    plt.xlabel("Time (min)", fontsize=12)
    plt.ylabel("Temperature (°C)", fontsize=12)
    plt.ylim(0, 500)
    plt.yticks(np.arange(0, 501, 50))
    
    # Cập nhật tiêu đề đồ thị (Title)
    plt.title(f"{run_config['name']} \n"
              f"($K_0$={run_config['kint']:.1e} m$^2$, $A_\\Gamma$ (AK)={run_config['ak']:g})",
              fontsize=14, fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.6)

    # ---- two compact legends ----
    depth_handles = [Line2D([0], [0], color=colors[d], lw=1.3, label=f"{d}mm")
                     for d in ACTIVE_DEPTHS]
    src_handles = [
        Line2D([0], [0], color='black', lw=1.3, linestyle='-',  label='Sim'),
        Line2D([0], [0], color='black', lw=1.1, linestyle='--', label='Dauti'),
        Line2D([0], [0], color='black', lw=1.6, linestyle=':',  label='Exp'),
    ]
    leg1 = plt.legend(handles=depth_handles, loc="upper left", fontsize=9, title="Depth")
    plt.gca().add_artist(leg1)
    plt.legend(handles=src_handles, loc="lower right", fontsize=10, title="Source")

    save_path = os.path.join(output_dir, run_config["save"])
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"-> Image saved: {run_config['save']}  (from {os.path.basename(csv_file)})")

# ===================================================================
# RUN
# ===================================================================
if __name__ == "__main__":
    print("Plotting Temperature Comparison for Post-Gas Pressure Calibration\n")
    plot_compare(TARGET_RUN)
    print(f"\n[COMPLETE] Check '{output_dir}'.")