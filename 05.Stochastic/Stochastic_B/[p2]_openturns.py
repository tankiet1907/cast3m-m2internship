import openturns as ot
import openturns.viewer as viewer
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# =========================================================
# ESTABLISHING PROJECT PATHWAYS
# =========================================================
working_dir = r"D:\cast3m-m2internship\05.Stochastic\Stochastic_B"
output_dir = os.path.join(working_dir, "Plots")
os.makedirs(output_dir, exist_ok=True)
input_csv_file = os.path.join(working_dir, "OpenTURNS_Inputs_X.csv")
output_csv_file = os.path.join(working_dir, "OpenTURNS_Outputs_Y.csv")

# =========================================================
# 1. READING SAVED DATA FROM SCRIPT 1
# =========================================================
print("Đang nạp dữ liệu bằng Pandas...")
try:
    df_in = pd.read_csv(input_csv_file, sep=';', on_bad_lines='skip')
    df_out = pd.read_csv(output_csv_file, sep=';', on_bad_lines='skip')

    df_in = df_in.loc[:, ~df_in.columns.str.contains('^Unnamed')]
    df_out = df_out.loc[:, ~df_out.columns.str.contains('^Unnamed')]

    input_names = list(df_in.columns)
    output_names = list(df_out.columns)

    input_ot = ot.Sample(df_in.values)
    input_ot.setDescription(input_names)

    output_ot = ot.Sample(df_out.values)
    output_ot.setDescription(output_names)

    print(f"-> Đã nạp thành công {input_ot.getSize()} mẫu (samples).")
    print(f"-> Các biến Đầu vào (X): {input_names}")
    print(f"-> Các biến Đầu ra (Y) : {output_names}")

except FileNotFoundError:
    print(f"LỖI: Không tìm thấy file CSV tại {working_dir}.")
    print("Vui lòng đảm bảo Script 1 đã chạy xong và sinh ra file.")
    exit()
except Exception as e:
    print(f"LỖI KHÔNG XÁC ĐỊNH KHI ĐỌC DỮ LIỆU: {e}")
    exit()

# =========================================================
# 2. REDECLARING THE DISTRIBUTIONS (REQUIRED FOR PCE & SOBOL)
# =========================================================
dist_CEM  = ot.Normal(377.0, 15.0)
dist_AGGR = ot.Normal(1920.0, 50.0)
dist_WC   = ot.Uniform(0.30, 0.38)
dist_SC   = ot.Uniform(0.08, 0.12)
my_distribution = ot.JointDistribution([dist_CEM, dist_AGGR, dist_WC, dist_SC])

# =========================================================
# 3. CẤU HÌNH NGƯỠNG (failure khi Y > threshold)
# =========================================================
thresholds_dict = {
    "T_00_Max": 600.0,
    "T_10_Max": 400.0,
    "T_20_Max": 350.0,
    "T_30_Max": 300.0,
    "T_40_Max": 250.0,
    "T_50_Max": 200.0,
    "T_120_Max": 150.0,
    "Pg_10_Max": 2.5,
    "Pg_20_Max": 2.0,
    "Pg_30_Max": 1.8,
    "Pg_40_Max": 1.5,
    "Pg_50_Max": 1.2
}
operator_str = ">"

# =========================================================
# 4. POST-PROCESSING & ANALYSIS
# =========================================================
for target_name in output_names:
    print(f"\n" + "=" * 70)
    print(f"  ĐANG TỰ ĐỘNG PHÂN TÍCH CHO BIẾN: {target_name}")
    print("=" * 70)

    col_idx = output_names.index(target_name)
    target_sample = output_ot[:, col_idx]
    out_array = np.array(target_sample).flatten()

    # Ngưỡng + đơn vị cho biến hiện tại
    if target_name in thresholds_dict:
        CURRENT_THRESHOLD = thresholds_dict[target_name]
    else:
        CURRENT_THRESHOLD = 300.0 if target_name.startswith("T") else 2.0
        print(f"  [Cảnh báo] Không tìm thấy ngưỡng cụ thể cho {target_name}, dùng mặc định {CURRENT_THRESHOLD}.")
    unit = "°C" if target_name.startswith("T") else "MPa"

# ---------------------------------------------------------
# 4.1. SCATTER PLOTS & CORRELATION
# ---------------------------------------------------------
    print("\n -> Drawing Scatter Plots...")
    in_array = np.array(input_ot)

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    fig.suptitle(f'Scatter Plots: Inputs vs {target_name}', fontsize=14, fontweight='bold')

    for i in range(4):
        x_data = in_array[:, i]
        corr = np.corrcoef(x_data, out_array)[0, 1]

        axes[i].scatter(x_data, out_array, alpha=0.7, color='b', edgecolors='k')
        axes[i].set_xlabel(input_ot.getDescription()[i], fontsize=12)
        axes[i].set_ylabel(target_name, fontsize=12)
        axes[i].set_title(f'Correlation: {corr:.2f}', fontsize=12)
        axes[i].grid(True, linestyle='--', alpha=0.6)
        axes[i].tick_params(axis='both', labelsize=10)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"Scatter_Plots_{target_name}.png"), dpi=150, bbox_inches='tight')
    plt.close(fig)

# ---------------------------------------------------------
# 4.2. METAMODEL (PCE) — cần cho Sobol
# ---------------------------------------------------------
    print(" -> Constructing Metamodel (PCE)...")
    algo = ot.FunctionalChaosAlgorithm(input_ot, target_sample, my_distribution)
    algo.run()
    result_pce = algo.getResult()
    metamodel = result_pce.getMetaModel()

    # Moments tính trên DỮ LIỆU THẬT
    mean_val = target_sample.computeMean()[0]
    var_val = target_sample.computeCovariance()[0, 0]
    std_val = np.sqrt(var_val)
    skew_val = target_sample.computeSkewness()[0]
    kurt_val = target_sample.computeKurtosis()[0]

    # Kiểm tra chất lượng fit PCE (ảnh hưởng độ tin cậy của Sobol)
    try:
        valid = ot.MetaModelValidation(input_ot, target_sample, metamodel)
        q2 = valid.computePredictivityFactor()[0]
        print(f"    [PCE] Q2 = {q2:.4f}")
    except Exception as e:
        print(f"    [PCE] Không tính được Q2: {e}")

    print(f"\n--- THỐNG KÊ KẾT QUẢ ĐẦU RA ({target_name}) ---")
    print(f" + Giá trị trung bình (Mean)   : {mean_val:.4f}")
    print(f" + Phương sai (Variance)       : {var_val:.4f}")
    print(f" + Độ lệch chuẩn (Std. Dev.)   : {std_val:.4f}")
    print(f" + Hệ số bất đối xứng (Skew)   : {skew_val:.4f}")
    print(f" + Độ nhọn (Kurtosis)          : {kurt_val:.4f}")
    print("-------------------------------------------------")

# ---------------------------------------------------------
# 4.3 SOBOL' INDICES (1st & Total Order)
# ---------------------------------------------------------
    print(" -> Calculating Sobol' Indices...")
    sobol = ot.FunctionalChaosSobolIndices(result_pce)
    sobol_1st = [sobol.getSobolIndex(i) * 100 for i in range(4)]
    sobol_tot = [sobol.getSobolTotalIndex(i) * 100 for i in range(4)]

    print(f"\n--- SOBOL'S INDEX FOR {target_name} (%) ---")
    for i, name in enumerate(input_ot.getDescription()):
        print(f"{name:<5}: 1st Order = {sobol_1st[i]:5.2f}% | Total = {sobol_tot[i]:5.2f}%")

    fig, ax = plt.subplots(figsize=(10, 8))
    bar_width = 0.35
    index = np.arange(4)

    ax.bar(index, sobol_1st, bar_width, label='1st Order', color='#1f77b4')
    ax.bar(index + bar_width, sobol_tot, bar_width, label='Total Order', color='#ff7f0e')

    ax.set_xlabel('Input Variables', fontsize=12)
    ax.set_ylabel("Sobol' Indices (%)", fontsize=12)
    ax.set_title(f"Sobol' Sensitivity Analysis for {target_name}", fontsize=14, fontweight='bold')
    ax.set_xticks(index + bar_width / 2)
    ax.set_xticklabels(input_ot.getDescription(), fontsize=10)
    ax.tick_params(axis='y', labelsize=10)

    ax.legend(fontsize=10)
    ax.grid(axis='y', linestyle='--', alpha=0.6)

    y_max = max(max(sobol_1st), max(sobol_tot))
    ax.set_ylim(0, y_max * 1.2)

    stats_text = (
        f"Output Statistics ({target_name}):\n"
        f"$\\mu$ (Mean): {mean_val:.4f}\n"
        f"$\\sigma^2$ (Variance): {var_val:.5f}\n"
        f"$\\sigma$ (Std. Dev.): {std_val:.4f}"
    )
    props = dict(boxstyle='round,pad=0.6', facecolor='white', edgecolor='gray', alpha=0.9)
    ax.text(0.02, 0.96, stats_text, transform=ax.transAxes,
            fontsize=10, verticalalignment='top', bbox=props, color='#333333')

    plt.savefig(os.path.join(output_dir, f"Sobol_Sensitivity_{target_name}.png"), dpi=150, bbox_inches='tight')
    plt.close(fig)

# ---------------------------------------------------------
# 4.4 SECOND-ORDER SOBOL' INDICES (Cross-Interactions)
# ---------------------------------------------------------
    print("\n -> Calculating Second-Order Sobol' Indices (Cross-Interactions)...")
    saltelli_size = 10000
    sie = ot.SobolIndicesExperiment(my_distribution, saltelli_size, True)
    inputDesign = sie.generate()
    outputDesign = metamodel(inputDesign)
    saltelli = ot.SaltelliSensitivityAlgorithm(inputDesign, outputDesign, saltelli_size)
    s2_matrix = saltelli.getSecondOrderIndices()
    var_names = input_ot.getDescription()
    num_vars = len(var_names)

    print(f"\n--- SECOND-ORDER SOBOL' MATRIX FOR {target_name} (%) ---")
    for i in range(num_vars):
        for j in range(i + 1, num_vars):
            val = s2_matrix[i, j] * 100
            if val > 0.5:
                print(f" Cross-Interaction [{var_names[i]} x {var_names[j]}]: {val:.2f}%")

    s2_np = np.zeros((num_vars, num_vars))
    for i in range(num_vars):
        for j in range(num_vars):
            if i != j:
                s2_np[i, j] = s2_matrix[i, j] * 100

    fig, ax = plt.subplots(figsize=(8, 6))
    cax = ax.imshow(s2_np, cmap='Oranges', vmin=0)

    for i in range(num_vars):
        for j in range(num_vars):
            if i != j:
                ax.text(j, i, f"{s2_np[i, j]:.1f}%", ha="center", va="center", color="black", fontsize=10)
            else:
                ax.text(j, i, "-", ha="center", va="center", color="gray", fontsize=10)

    ax.set_xticks(np.arange(num_vars))
    ax.set_yticks(np.arange(num_vars))
    ax.set_xticklabels(var_names, fontsize=10)
    ax.set_yticklabels(var_names, fontsize=10)
    ax.set_title(f"Sobol' Second-Order Indices (%) - {target_name}", fontsize=14, fontweight='bold')

    fig.colorbar(cax, ax=ax, label='Contribution Rate (%)')
    plt.savefig(os.path.join(output_dir, f"Sobol_SecondOrder_Heatmap_{target_name}.png"), dpi=150, bbox_inches='tight')
    plt.close(fig)

# ---------------------------------------------------------
# 4.5 KERNEL SMOOTHING & RELIABILITY (trên dữ liệu thật)
# ---------------------------------------------------------
    print(" -> Đang xây dựng PDF trơn (KDE) trực tiếp từ dữ liệu thật...")
    fitted_dist = ot.KernelSmoothing().build(target_sample)

    # Failure khi Y > threshold => Pf = đuôi PHẢI = 1 - CDF(threshold)
    pf = fitted_dist.computeComplementaryCDF(CURRENT_THRESHOLD)

    print(f"=========================================================")
    print(f" RELIABILITY ANALYSIS RESULTS (Dựa trên KDE)")
    print(f" Threshold: {operator_str} {CURRENT_THRESHOLD} {unit}")
    print(f" Estimated Pf : {pf * 100:.4f} %")
    print(f"=========================================================")

    # =========================================================
    # VẼ ĐỒ THỊ PDF & FAILURE REGION
    # =========================================================
    print(" -> Đang tạo đồ thị phân phối xác suất...")
    graph = fitted_dist.drawPDF()

    fig2 = plt.figure(figsize=(10, 8))
    ax2 = fig2.add_subplot(111)

    # Histogram dữ liệu thật vẽ trước (nằm dưới)
    ax2.hist(out_array, bins='auto', density=True, alpha=0.5, color='gray',
             edgecolor='black', label='Empirical Data (Histogram)', zorder=1)

    # KDE vẽ sau (nằm trên)
    view = viewer.View(graph, figure=fig2, axes=[ax2])
    line = ax2.lines[0]
    line.set_color('blue')
    line.set_linewidth(2)
    line.set_label('KDE PDF')
    line.set_zorder(5)

    x_data = line.get_xdata()
    y_data = line.get_ydata()

    # Failure ở đuôi PHẢI (Y >= threshold)
    x_tail = x_data[x_data >= CURRENT_THRESHOLD]
    y_tail = y_data[x_data >= CURRENT_THRESHOLD]

    legend_text = (f'Failure Region ({operator_str} {CURRENT_THRESHOLD} {unit})\n'
                   f'Failure Prob (Pf) : {pf * 100:.2f}%')
    ax2.fill_between(x_tail, y_tail, color='red', alpha=0.4, label=legend_text, zorder=3)
    ax2.axvline(x=CURRENT_THRESHOLD, color='black', linestyle='--', linewidth=1.5,
                label=f'Threshold: {CURRENT_THRESHOLD} {unit}', zorder=4)

    ax2.set_title(f'Probability Density & Failure Probability for {target_name}', fontsize=14, fontweight='bold')
    ax2.set_xlabel(f'Values ({unit})', fontsize=12)
    ax2.set_ylabel('Density', fontsize=12)
    ax2.tick_params(axis='both', labelsize=10)

    ax2.legend(loc='upper right', fontsize=10)
    ax2.grid(True, linestyle='--', alpha=0.6)

    rel_plot_path = os.path.join(output_dir, f"Reliability_Analysis_{target_name}.png")
    plt.savefig(rel_plot_path, dpi=150, bbox_inches='tight')
    plt.close(fig2)
    print(f"   [OK] Đã lưu đồ thị Reliability tại: {rel_plot_path}")

print("\n" + "=" * 70)
print(" TOÀN BỘ QUÁ TRÌNH PHÂN TÍCH TỰ ĐỘNG ĐÃ HOÀN THÀNH!")
print("=" * 70)