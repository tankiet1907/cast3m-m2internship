import openturns as ot
import openturns.viewer as viewer
import os
import matplotlib.pyplot as plt
import numpy as np

# =========================================================
# ESTABLISHING PROJECT PATHWAYS
# =========================================================
working_dir = r"D:\cast3m-m2internship\04.OpenTURNS\Test_02"
input_csv_file = os.path.join(working_dir, "OpenTURNS_Inputs_X.csv")
output_csv_file = os.path.join(working_dir, "OpenTURNS_Outputs_Y.csv")


# =========================================================
# 1. READING SAVED DATA FROM SCRIPT 1
# =========================================================
try:
    input_ot = ot.Sample.BuildFromCSV(input_csv_file, ";")
    output_ot = ot.Sample.BuildFromCSV(output_csv_file, ";")
except Exception as e:
    print(f"File not found. Please run Script 1 first. Details: {e}")
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
# TÙY CHỈNH: CHỌN ĐẠI LƯỢNG MUỐN PHÂN TÍCH
# Lựa chọn: "T00_Max", "T10_Max", ..., "T120_Max", "Pg10_Max", ..., "Pg50_Max"
target_name = "Pg_20_Max" # <<< Đổi tên ở đây

# Tìm index cột tương ứng
output_desc = output_ot.getDescription()
if target_name not in output_desc:
    print(f"Lỗi: Không tìm thấy '{target_name}'. Các cột có sẵn: {output_desc}")
    exit()

col_idx = output_desc.index(target_name)
target_sample = output_ot[:, col_idx]
print(f"\n---> ĐANG PHÂN TÍCH CHO BIẾN: {target_name} <---")

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
plt.savefig(os.path.join(working_dir, f"Scatter_Plots_{target_name}.png"), dpi=300)
# plt.show()

# ---------------------------------------------------------
# 3.2. METAMODEL (PCE) & SOBOL INDICES
# ---------------------------------------------------------
print(" -> Constructing Metamodel (PCE)...")
algo = ot.FunctionalChaosAlgorithm(input_ot, target_sample, my_distribution)
algo.run()
result_pce = algo.getResult()
metamodel = result_pce.getMetaModel() # <--- Virtual Mathematical Functions

# === TRÍCH XUẤT THỐNG KÊ (MEAN, VARIANCE, STD DEV) ===
mean_val = result_pce.getMean()[0]
var_val = result_pce.getCovariance()[0, 0]
std_val = np.sqrt(var_val)

print(f"\n--- THỐNG KÊ KẾT QUẢ ĐẦU RA ({target_name}) ---")
print(f" + Giá trị trung bình (Mean)   : {mean_val:.4f}")
print(f" + Phương sai (Variance)       : {var_val:.4f}")
print(f" + Độ lệch chuẩn (Std. Dev.)   : {std_val:.4f}")
print("-------------------------------------------------")

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
plt.savefig(os.path.join(working_dir, f"Sobol_Sensitivity_{target_name}.png"), dpi=300)
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
plt.savefig(os.path.join(working_dir, f"Sobol_SecondOrder_Heatmap_{target_name}.png"), dpi=300)
#plt.show()

# ---------------------------------------------------------
# 3.3. RELIABILITY ANALYSIS USING METAMODEL
# ---------------------------------------------------------
try:
    PG_THRESHOLD = 2.0 
    print(f"\n -> Running Reliability Analysis (Threshold {target_name} > {PG_THRESHOLD})...")

    # Kết nối Metamodel với không gian phân phối
    X_rnd = ot.RandomVector(my_distribution)
    Y_metamodel = ot.CompositeRandomVector(metamodel, X_rnd)

    # Sự kiện vượt ngưỡng
    event = ot.ThresholdEvent(Y_metamodel, ot.Greater(), PG_THRESHOLD)

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
    algo_FORM = ot.FORM(solver, event, starting_point)
    algo_FORM.run()
    result_FORM = algo_FORM.getResult()
    pf_form = result_FORM.getEventProbability()

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
    print(f" Threshold: {PG_THRESHOLD} MPa")
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
    
    # Rút ngẫu nhiên 10,000 điểm từ Metamodel để tạo đồ thị PDF mượt mà
    sample_size_plot = 10000
    Y_sample_plot = Y_metamodel.getSample(sample_size_plot)
    
    # Tạo đối tượng vẽ đồ thị từ OpenTURNS
    graph = ot.KernelSmoothing().build(Y_sample_plot).drawPDF()
    graph.setTitle(f'Probability Density Function of {target_name}')
    graph.setXTitle('Gas Pressure (MPa)')
    graph.setYTitle('Density')

    # Chuyển đổi graph của OpenTURNS sang Matplotlib Figure
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111)
    view = viewer.View(graph, figure=fig, axes=[ax])

    # Lấy dữ liệu x, y của đường cong vừa vẽ để tô màu
    line = ax.lines[0]
    x_data = line.get_xdata()
    y_data = line.get_ydata()

    # Lọc phần đuôi (vượt ngưỡng Threshold)
    x_tail = x_data[x_data >= PG_THRESHOLD]
    y_tail = y_data[x_data >= PG_THRESHOLD]

    # Cấu trúc nội dung Legend
    legend_text = (f'Failure Region (>{PG_THRESHOLD} MPa)\n'
                   f'MC Pf   : {pf_mc*100:.4f}%\n'
                   f'FORM Pf : {pf_form*100:.4f}%')
    if pf_sorm is not None:
        legend_text += f'\nSORM Pf : {pf_sorm*100:.4f}%'

    # Tô màu đỏ vùng vượt ngưỡng (Vùng nứt vỡ)
    ax.fill_between(x_tail, y_tail, color='red', alpha=0.5, label=legend_text)
    
    # Vẽ đường thẳng phân cách tại Threshold
    ax.axvline(x=PG_THRESHOLD, color='black', linestyle='--', linewidth=2, label=f'Threshold: {PG_THRESHOLD}')

    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, linestyle=':', alpha=0.6)
    
    plt.tight_layout()
    plot_path = os.path.join(working_dir, f"Reliability_Plot_{target_name}.png")
    plt.savefig(plot_path, dpi=300)
    print(f"Đã lưu đồ thị Reliability tại: {plot_path}")
    # plt.show()

except Exception as e:
    print(f"\n[NOTE] Lỗi trong phần Reliability: {e}")