import openturns as ot
import openturns.viewer as viewer
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# =========================================================
# ESTABLISHING PROJECT PATHWAYS
# =========================================================
working_dir = r"D:\cast3m-m2internship\04.OpenTURNS\Test_02"
output_dir = os.path.join(working_dir, "Plots")
input_csv_file = os.path.join(working_dir, "OpenTURNS_Inputs_X.csv")
output_csv_file = os.path.join(working_dir, "OpenTURNS_Outputs_Y.csv")


# =========================================================
# 1. READING SAVED DATA FROM SCRIPT 1
# =========================================================
print("Đang nạp dữ liệu bằng Pandas...")
try:
    # on_bad_lines='skip': Bỏ qua các dòng bị lỗi cấu trúc nếu có
    df_in = pd.read_csv(input_csv_file, sep=';', on_bad_lines='skip')
    df_out = pd.read_csv(output_csv_file, sep=';', on_bad_lines='skip')

    # Dọn dẹp cột thừa: Cast3M/OpenTURNS thỉnh thoảng để dư dấu ';' ở cuối dòng, 
    # Pandas sẽ đọc thành một cột tên là 'Unnamed: ...'. Ta cần xóa chúng đi.
    df_in = df_in.loc[:, ~df_in.columns.str.contains('^Unnamed')]
    df_out = df_out.loc[:, ~df_out.columns.str.contains('^Unnamed')]

    # Lấy danh sách tên cột
    input_names = list(df_in.columns)
    output_names = list(df_out.columns)
    
    # Chuyển đổi DataFrame của Pandas sang mảng Numpy, rồi bọc vào ot.Sample
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
# 2. REDECLARING THE DISTRIBUTIONS (REQUIRED FOR PCE & RELIABILITY)
# =========================================================
dist_CEM  = ot.Normal(377.0, 15.0)     
dist_AGGR = ot.Normal(1920.0, 50.0)    
dist_WC   = ot.Uniform(0.30, 0.38)     
dist_SC   = ot.Uniform(0.08, 0.12)     
my_distribution = ot.JointDistribution([dist_CEM, dist_AGGR, dist_WC, dist_SC])

# =========================================================
# 3. POST-PROCESSING & ANALYSIS
# =========================================================
# VÒNG LẶP TỰ ĐỘNG CHO TẤT CẢ CÁC ĐẠI LƯỢNG ĐẦU RA (TARGETS)
for target_name in output_names:
    print(f"\n" + "="*70)
    print(f"  ĐANG TỰ ĐỘNG PHÂN TÍCH CHO BIẾN: {target_name}")
    print("="*70)
    
    col_idx = output_names.index(target_name)
    target_sample = output_ot[:, col_idx]

# ---------------------------------------------------------
# 3.1. SCATTER PLOTS & CORRELATION
# ---------------------------------------------------------
    print("\n -> Drawing Scatter Plots...")
    in_array = np.array(input_ot)
    out_array = np.array(target_sample).flatten()

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    fig.suptitle(f'Scatter Plots: Inputs vs {target_name}', fontsize=16)

    for i in range(4):
        x_data = in_array[:, i]
        corr = np.corrcoef(x_data, out_array)[0, 1] 
    
        axes[i].scatter(x_data, out_array, alpha=0.7, color='b', edgecolors='k')
        axes[i].set_xlabel(input_ot.getDescription()[i], fontsize=12)
        axes[i].set_ylabel(target_name, fontsize=12)
        axes[i].set_title(f'Correlation: {corr:.2f}')
        axes[i].grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"Scatter_Plots_{target_name}.png"), dpi=300)
    plt.close(fig)
    # plt.show()

# ---------------------------------------------------------
# 3.2. METAMODEL (PCE) 
# ---------------------------------------------------------
    print(" -> Constructing Metamodel (PCE)...")
    algo = ot.FunctionalChaosAlgorithm(input_ot, target_sample, my_distribution)
    algo.run()
    result_pce = algo.getResult()
    metamodel = result_pce.getMetaModel() # <--- Virtual Mathematical Functions

    # === TRÍCH XUẤT THỐNG KÊ (MEAN, VARIANCE, STD DEV) ===
    mean_val = target_sample.computeMean()[0]
    var_val = target_sample.computeCovariance()[0, 0]
    std_val = np.sqrt(var_val)

    print(f"\n--- THỐNG KÊ KẾT QUẢ ĐẦU RA ({target_name}) ---")
    print(f" + Giá trị trung bình (Mean)   : {mean_val:.4f}")
    print(f" + Phương sai (Variance)       : {var_val:.4f}")
    print(f" + Độ lệch chuẩn (Std. Dev.)   : {std_val:.4f}")
    print("-------------------------------------------------")

# ---------------------------------------------------------
# 3.3 TÍNH TOÁN VÀ VẼ BIỂU ĐỒ ĐỘ NHẠY SOBOL'
# ---------------------------------------------------------
    print(" -> Calculating Sobol' Indices...")
    sobol = ot.FunctionalChaosSobolIndices(result_pce)
    sobol_1st = [sobol.getSobolIndex(i) * 100 for i in range(4)]       
    sobol_tot = [sobol.getSobolTotalIndex(i) * 100 for i in range(4)]  

    print(f"\n--- SOBOL'S INDEX FOR {target_name} (%) ---")
    for i, name in enumerate(input_ot.getDescription()):
        print(f"{name:<5}: 1st Order = {sobol_1st[i]:5.2f}% | Total = {sobol_tot[i]:5.2f}%")

# --- VẼ BIỂU ĐỒ BAR CHART CÓ CHỨA TEXT BOX THỐNG KÊ ---
    fig, ax = plt.subplots(figsize=(8, 6))
    bar_width = 0.35
    index = np.arange(4)

# Vẽ các cột        
    ax.bar(index, sobol_1st, bar_width, label='1st Order', color='#1f77b4')
    ax.bar(index + bar_width, sobol_tot, bar_width, label='Total Order', color='#ff7f0e')

# Thiết lập trục và tiêu đề        
    ax.set_xlabel('Input Variables', fontsize=12)
    ax.set_ylabel("Sobol' Indices (%)", fontsize=12)
    ax.set_title(f"Sobol' Sensitivity Analysis for {target_name}", fontsize=14)
    ax.set_xticks(index + bar_width / 2)
    ax.set_xticklabels(input_ot.getDescription())

# Đặt chú thích (Legend)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)

# Mở rộng giới hạn trục Y thêm một chút để không bị che khuất bởi Text Box
    y_max = max(max(sobol_1st), max(sobol_tot))
    ax.set_ylim(0, y_max * 1.2) # Mở rộng 20%

# --- THÊM TEXT BOX CHỨA MEAN VÀ VARIANCE ---
# Chuẩn bị nội dung chữ
    stats_text = (
    f"Output Statistics ({target_name}):\n"
    f"$\\mu$ (Mean): {mean_val:.4f} MPa\n"
    f"$\\sigma^2$ (Variance): {var_val:.5f}\n"
    f"$\\sigma$ (Std. Dev.): {std_val:.4f} MPa"
    )
        
# Cấu hình khung hộp (box)
    props = dict(boxstyle='round,pad=0.6', facecolor='white', edgecolor='gray', alpha=0.9)
        
# Chèn Text Box vào góc trên cùng bên trái (x=0.02, y=0.95 theo hệ tọa độ của trục)
    ax.text(0.02, 0.96, stats_text, transform=ax.transAxes, 
        fontsize=10, verticalalignment='top', bbox=props, color='#333333')
        
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"Sobol_Sensitivity_{target_name}.png"), dpi=300)
    plt.close(fig)
    #plt.show()
        
# ---------------------------------------------------------
# SECOND-ORDER SOBOL' INDICES 
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
        
# HEATMAP
    s2_np = np.zeros((num_vars, num_vars))
    for i in range(num_vars):
        for j in range(num_vars):
            if i != j:
                s2_np[i, j] = s2_matrix[i, j] * 100
                    
    fig, ax = plt.subplots(figsize=(6, 5))
    cax = ax.imshow(s2_np, cmap='Oranges', vmin=0)
        
    for i in range(num_vars):
        for j in range(num_vars):
            if i != j:
                ax.text(j, i, f"{s2_np[i, j]:.1f}%", ha="center", va="center", color="black", fontsize=10)
            else:
                ax.text(j, i, "-", ha="center", va="center", color="gray", fontsize=10)

    ax.set_xticks(np.arange(num_vars))
    ax.set_yticks(np.arange(num_vars))
    ax.set_xticklabels(var_names)
    ax.set_yticklabels(var_names)
    ax.set_title(f"Sobol' Second-Order Indices (%) - {target_name}", fontsize=14)
        
    fig.colorbar(cax, ax=ax, label='Contribution Rate (%)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"Sobol_SecondOrder_Heatmap_{target_name}.png"), dpi=300)
    plt.close(fig)
    #plt.show()

# ---------------------------------------------------------
# 3.3. RELIABILITY ANALYSIS USING METAMODEL DỰA TRÊN LOẠI BIẾN (T vs Pg) VỚI NGƯỠNG ĐỘNG (DYNAMIC THRESHOLD)
# ---------------------------------------------------------
    thresholds_dict = {
        "T_00_Max": 600.0,   # Mặt ngoài tiếp xúc lửa, chịu được nhiệt rất cao
        "_10_Max": 400.0,
        "T_20_Max": 350.0,
        "T_30_Max": 300.0,
        "T_40_Max": 250.0,
        "T_50_Max": 200.0,
        "T_120_Max": 150.0,  # Lõi sâu bên trong, ngưỡng an toàn thấp hơn
        "Pg_10_Max": 2.5,    # Áp suất khí gây nổ vỡ (MPa)
        "Pg_20_Max": 2.0,
        "Pg_30_Max": 1.8,
        "Pg_40_Max": 1.5,
        "Pg_50_Max": 1.2
    }

    # Lấy ngưỡng và đơn vị tương ứng cho biến hiện tại
    if target_name in thresholds_dict:
        CURRENT_THRESHOLD = thresholds_dict[target_name]
    else:
        # Giá trị mặc định dự phòng nếu tên biến không có trong từ điển
        CURRENT_THRESHOLD = 300.0 if target_name.startswith("T") else 2.0
        print(f"  [Cảnh báo] Không tìm thấy ngưỡng cụ thể cho {target_name}, dùng mặc định {CURRENT_THRESHOLD}.")

    unit = "°C" if target_name.startswith("T") else "MPa"

    print(f"   -> Đang chạy Phân tích Độ tin cậy (Ngưỡng {target_name} > {CURRENT_THRESHOLD} {unit})...")

    # Kết nối Metamodel với không gian phân phối
    X_rnd = ot.RandomVector(my_distribution)
    Y_metamodel = ot.CompositeRandomVector(metamodel, X_rnd)

    # Sự kiện vượt ngưỡng
    event = ot.ThresholdEvent(Y_metamodel, ot.Greater(), CURRENT_THRESHOLD)

    # --- 1. TÍNH BẰNG MONTE CARLO ---
    print("\n   [Đang tính bằng Monte Carlo...]")
    mc_algo = ot.ProbabilitySimulationAlgorithm(event, ot.MonteCarloExperiment())
    mc_algo.setMaximumOuterSampling(100000)
    mc_algo.run()
    pf_mc = mc_algo.getResult().getProbabilityEstimate()

    # --- 2. TÍNH BẰNG FORM ---
    print("   [Đang tính bằng FORM...]")
    starting_point = my_distribution.getMean()
    solver = ot.Cobyla()
    pf_form = 0.0 # Giá trị mặc định nếu FORM thất bại
    try:
        algo_FORM = ot.FORM(solver, event, my_distribution.getMean())
        algo_FORM.run()
        pf_form = algo_FORM.getResult().getEventProbability()
    except Exception as e:
        print(f"   [CẢNH BÁO FORM] Thuật toán FORM không hội tụ. Lý do: Xác suất xảy ra quá thấp (hầu như bằng 0) hoặc bề mặt quá phức tạp. Bỏ qua FORM cho biến này.")
        pf_form = 0.0 # Đặt xác suất = 0

    # --- 3. TÍNH BẰNG SORM ---
    print("   [Đang tính bằng SORM...]")
    pf_sorm = None
    try:
        # SORM lấy kết quả từ FORM làm điểm khởi đầu (Design Point)
        algo_SORM = ot.SORM(solver, event, starting_point)
        algo_SORM.run()
        result_SORM = algo_SORM.getResult()
        
        # Sử dụng phương pháp Hohenbichler cho SORM
        beta_sorm_hohen = result_SORM.getGeneralisedReliabilityIndexHohenbichler()
        dist_norm = ot.Normal()
        pf_sorm = dist_norm.computeComplementaryCDF(beta_sorm_hohen)
    except Exception as e:
        print(f"      [LỖI SORM] Bề mặt có thể quá gồ ghề: {e}")

    # In kết quả tổng hợp ra terminal
    print(f"=========================================================")
    print(f" RELIABILITY ANALYSIS RESULTS")
    print(f" Threshold: {CURRENT_THRESHOLD} {unit}")
    print(f" Monte Carlo Pf : {pf_mc * 100:.4f} %")
    print(f" FORM Pf        : {pf_form * 100:.4f} %")
    if pf_sorm is not None:
        print(f" SORM Pf        : {pf_sorm * 100:.4f} %")
    else:
        print(f" SORM Pf        : N/A")
    print(f"=========================================================")

    # =========================================================
    # VẼ ĐỒ THỊ (PLOT PDF & FAILURE REGION)
    # =========================================================
    print(" -> Đang tạo đồ thị phân phối xác suất...")
    
    Y_sample_plot = Y_metamodel.getSample(10000)
    graph = ot.KernelSmoothing().build(Y_sample_plot).drawPDF()
    
    fig2 = plt.figure(figsize=(8, 6))
    ax2 = fig2.add_subplot(111)
    view = viewer.View(graph, figure=fig2, axes=[ax2])
    
    # Trích xuất đường cong để tô màu Failure Region
    line = ax2.lines[0]
    x_data = line.get_xdata()
    y_data = line.get_ydata()
    x_tail = x_data[x_data >= CURRENT_THRESHOLD]
    y_tail = y_data[x_data >= CURRENT_THRESHOLD]
    
    # Tạo nội dung chú thích cho vùng phá hủy
    legend_text = (f'Failure Region (>{CURRENT_THRESHOLD} {unit})\n'
                   f'MC Pf   : {pf_mc*100:.4f}%\n'
                   f'FORM Pf : {pf_form*100:.4f}%')
    if pf_sorm is not None:
        legend_text += f'\nSORM Pf : {pf_sorm*100:.4f}%'
        
    ax2.fill_between(x_tail, y_tail, color='red', alpha=0.4, label=legend_text)
    ax2.axvline(x=CURRENT_THRESHOLD, color='black', linestyle='--', linewidth=2, label=f'Threshold: {CURRENT_THRESHOLD} {unit}')
    
    ax2.set_title(f'Probability Density & Failure Probability for {target_name}', fontsize=12, fontweight='bold')
    ax2.set_xlabel(f'Values ({unit})', fontsize=11)
    ax2.set_ylabel('Density', fontsize=11)
    ax2.legend(loc='upper right', fontsize=9)
    ax2.grid(True, linestyle=':', alpha=0.6)
    
    plt.tight_layout()
    rel_plot_path = os.path.join(output_dir, f"Reliability_Analysis_{target_name}.png")
    plt.savefig(rel_plot_path, dpi=300)
    plt.close(fig2)
    #plt.show()
    print(f"   [OK] Đã lưu đồ thị Reliability tại: {rel_plot_path}")

print("\n" + "="*70)
print(" TOÀN BỘ QUÁ TRÌNH PHÂN TÍCH TỰ ĐỘNG ĐÃ HOÀN THÀNH!")
print("="*70)   