import openturns as ot
import openturns.viewer as viewer
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# =========================================================
# ESTABLISHING PROJECT PATHWAYS
# =========================================================
working_dir = r"D:\cast3m-m2internship\05.Stochastic\Stochastic_C2"
output_dir = os.path.join(working_dir, "Plots")
os.makedirs(output_dir, exist_ok=True)

# Chỉ nạp file Output
output_csv_file = os.path.join(working_dir, "OpenTURNS_Outputs_Y.csv")

# =========================================================
# 1. READING SAVED DATA FROM SCRIPT 1
# =========================================================
print("Đang nạp dữ liệu Output bằng Pandas...")
try:
    df_out = pd.read_csv(output_csv_file, sep=';', on_bad_lines='skip')
    df_out = df_out.loc[:, ~df_out.columns.str.contains('^Unnamed')]
    output_names = list(df_out.columns)
    
    output_ot = ot.Sample(df_out.values)
    output_ot.setDescription(output_names)

    print(f"-> Đã nạp thành công {output_ot.getSize()} mẫu (samples).")
    print(f"-> Các biến Đầu ra (Y) : {output_names}")
    
except Exception as e:
    print(f"LỖI ĐỌC DỮ LIỆU: {e}")
    exit()

# =========================================================
# 2. POST-PROCESSING & ANALYSIS
# =========================================================
for target_name in output_names:
    print(f"\n" + "="*70)
    print(f"  ĐANG TỰ ĐỘNG PHÂN TÍCH CHO BIẾN: {target_name}")
    print("="*70)
    
    col_idx = output_names.index(target_name)
    target_sample = output_ot[:, col_idx]
    out_array = np.array(target_sample).flatten()

# ---------------------------------------------------------
# 2.1. SCATTER PLOT (Sự phân tán dữ liệu theo vòng lặp)
# ---------------------------------------------------------
    print("\n -> Drawing Scatter Plot (Run Index vs Output)...")
    run_indices = np.arange(1, len(out_array) + 1)

    fig1, ax1 = plt.subplots(figsize=(8, 5))
    
    # Vẽ các điểm phân tán
    ax1.scatter(run_indices, out_array, alpha=0.7, color='b', edgecolors='k', label='Dữ liệu đầu ra')
    
    # Vẽ thêm đường trung bình để dễ tham chiếu
    mean_val = np.mean(out_array)
    ax1.axhline(y=mean_val, color='r', linestyle='--', linewidth=1.5, label=f'Mean: {mean_val:.2f}')

    ax1.set_xlabel("Vòng lặp (Run Index)", fontsize=12)
    ax1.set_ylabel(f"Giá trị {target_name}", fontsize=12)
    ax1.set_title(f'Scatter Plot: Sự phân tán của {target_name}', fontsize=14, fontweight='bold')
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.tick_params(axis='both', labelsize=10)
    ax1.legend(loc='best')

    plt.tight_layout()
    scatter_path = os.path.join(output_dir, f"Scatter_Plot_{target_name}.png")
    plt.savefig(scatter_path, dpi=150, bbox_inches='tight')
    plt.close(fig1)
    print(f"   [OK] Đã lưu Scatter Plot tại: {scatter_path}")

# ---------------------------------------------------------
# 2.2. STATISTICAL MOMENTS (Thống kê mô tả)
# ---------------------------------------------------------
    var_val = target_sample.computeCovariance()[0, 0]
    std_val = np.sqrt(var_val)
    skew_val = target_sample.computeSkewness()[0]
    kurt_val = target_sample.computeKurtosis()[0]

    print(f"\n--- THỐNG KÊ KẾT QUẢ ĐẦU RA ({target_name}) ---")
    print(f" + Số lượng mẫu (N)            : {target_sample.getSize()}")
    print(f" + Giá trị trung bình (Mean)   : {mean_val:.4f}")
    print(f" + Độ lệch chuẩn (Std. Dev.)   : {std_val:.4f}")
    print(f" + Hệ số bất đối xứng (Skew)   : {skew_val:.4f}")
    print(f" + Độ nhọn (Kurtosis)          : {kurt_val:.4f}")
    print("-------------------------------------------------")

# ---------------------------------------------------------
# 2.3. KERNEL SMOOTHING & RELIABILITY ANALYSIS
# ---------------------------------------------------------
    print(" -> Đang xây dựng phân bố xác suất trơn (Kernel Smoothing) từ dữ liệu...")
    factory = ot.KernelSmoothing()
    fitted_dist = factory.build(target_sample)

    CURRENT_THRESHOLD = -400.0 
    unit = "µm/m"
    operator_str = "<"

    print(f"   -> Đang chạy Phân tích Độ tin cậy (Ngưỡng {target_name} {operator_str} {CURRENT_THRESHOLD} {unit})...")
    pf_estimate = fitted_dist.computeCDF(CURRENT_THRESHOLD)

    print(f"=========================================================")
    print(f" RELIABILITY ANALYSIS RESULTS (Dựa trên KDE)")
    print(f" Threshold: {operator_str} {CURRENT_THRESHOLD} {unit}")
    print(f" Estimated Pf : {pf_estimate * 100:.4f} %")
    print(f"=========================================================")

    # =========================================================
    # VẼ ĐỒ THỊ PDF & FAILURE REGION
    # =========================================================
    print(" -> Đang tạo đồ thị phân phối xác suất...")
    graph = fitted_dist.drawPDF()
    
    fig2 = plt.figure(figsize=(10, 8))
    ax2 = fig2.add_subplot(111)
    view = viewer.View(graph, figure=fig2, axes=[ax2])
    
    line = ax2.lines[0]
    line.set_color('blue')
    line.set_linewidth(2)
    line.set_label('KDE PDF')
    
    x_data = line.get_xdata()
    y_data = line.get_ydata()
    
    x_tail = x_data[x_data <= CURRENT_THRESHOLD] 
    y_tail = y_data[x_data <= CURRENT_THRESHOLD]
    
    legend_text = (f'Failure Region ({operator_str} {CURRENT_THRESHOLD} {unit})\n'
                   f'Failure Prob (Pf) : {pf_estimate * 100:.2f}%')
    ax2.fill_between(x_tail, y_tail, color='red', alpha=0.4, label=legend_text)
    ax2.axvline(x=CURRENT_THRESHOLD, color='black', linestyle='--', linewidth=1.5, label=f'Threshold: {CURRENT_THRESHOLD} {unit}')
    
    ax2.hist(out_array, bins='auto', density=True, alpha=0.5, color='gray', edgecolor='black', label='Empirical Data (Histogram)')

    ax2.set_title(f'Distribution & Failure Probability for {target_name}', fontsize=14, fontweight='bold')
    ax2.set_xlabel(f'Values ({unit})', fontsize=12)
    ax2.set_ylabel('Density', fontsize=12)
    ax2.tick_params(axis='both', labelsize=10)

    ax2.legend(loc='upper left', fontsize=10) 
    ax2.grid(True, linestyle='--', alpha=0.6)
    
    rel_plot_path = os.path.join(output_dir, f"Reliability_Analysis_{target_name}.png")
    plt.savefig(rel_plot_path, dpi=150, bbox_inches='tight')
    plt.close(fig2)
    print(f"   [OK] Đã lưu đồ thị Reliability tại: {rel_plot_path}")

print("\n" + "="*70)
print(" TOÀN BỘ QUÁ TRÌNH PHÂN TÍCH TỰ ĐỘNG ĐÃ HOÀN THÀNH!")
print("="*70)