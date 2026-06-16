import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import glob

# ===================================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN VÀ THÔNG SỐ
# =========================================================
csv_dir = r'D:\cast3m-m2internship\04.OpenTURNS\Test_02\CSV'
working_dir = r"D:\cast3m-m2internship\04.OpenTURNS\Test_02"
output_dir = os.path.join(working_dir, "Plots")
N_loops = 30

# MỚI: Đường dẫn đến file kết quả gốc (Baseline)
baseline_T_file  = r'D:\cast3m-m2internship\02.Simulation\02.Results\Temperature_1min_Intervals.csv'
baseline_Pg_file = r'D:\cast3m-m2internship\02.Simulation\02.Results\GasPressure_1min_Intervals.csv'

colors = {
    '00': '#d62728',   # Đỏ
    '10': '#ff7f0e',   # Cam
    '20': '#2ca02c',   # Xanh lá
    '30': '#1f77b4',   # Xanh dương
    '40': '#9467bd',   # Tím
    '50': '#8c564b',   # Nâu
    '120': '#7f7f7f'   # Xám
}

cols_T = {'00': 1, '10': 3, '20': 5, '30': 7, '40': 9, '50': 11, '120': 13}
cols_Pg = {'10': 3, '20': 5, '30': 7, '40': 9, '50': 11} 

# ===================================================================
# 2. HÀM ĐỌC VÀ GOM DỮ LIỆU TỪ 30 FILE
# ===================================================================
def collect_all_evolutions(prefix, columns_dict):
    data_store = {depth: [] for depth in columns_dict.keys()}
    common_time = None
    min_length = 99999
    
    for i in range(1, N_loops + 1):
        file_path = os.path.join(csv_dir, f"{prefix}_no_{i}.csv")
        if not os.path.exists(file_path): continue
            
        try:
            df = pd.read_csv(file_path, sep=';', on_bad_lines='skip')
            if common_time is None:
                common_time = df.iloc[:, 0].values
                
            current_len = len(df)
            if current_len < min_length:
                min_length = current_len
                
            for depth, col_idx in columns_dict.items():
                if col_idx < len(df.columns):
                    data_store[depth].append(df.iloc[:, col_idx].values)
                    
        except Exception as e:
            print(f"Lỗi đọc file {file_path}: {e}")
            
    if common_time is not None:
        common_time = common_time[:min_length]
        for depth in data_store.keys():
            data_store[depth] = np.array([run_data[:min_length] for run_data in data_store[depth]])
        
    return common_time, data_store

# ===================================================================
# 3. THU THẬP DỮ LIỆU
# ===================================================================
print("Đang tổng hợp dữ liệu Nhiệt độ (T)...")
time_T, matrix_T = collect_all_evolutions("temp_results", cols_T)

print("Đang tổng hợp dữ liệu Áp suất (Pg)...")
time_Pg, matrix_Pg = collect_all_evolutions("pg_results", cols_Pg)

# ===================================================================
# 4. HÀM VẼ ĐỒ THỊ (CÓ VẼ CHỒNG DỮ LIỆU GỐC)
# ===================================================================
def plot_confidence_intervals(time_array, data_matrix_dict, baseline_file, columns_dict, title, ylabel, save_name):
    plt.figure(figsize=(12, 8))
    
    # MỚI: Tải dữ liệu gốc (Baseline)
    df_baseline = None
    try:
        if os.path.exists(baseline_file):
            df_baseline = pd.read_csv(baseline_file, sep=';', on_bad_lines='skip')
            time_base = df_baseline.iloc[:, 0].values
        else:
            print(f"Cảnh báo: Không tìm thấy file gốc {baseline_file}")
    except Exception as e:
        print(f"Lỗi đọc file gốc: {e}")

    # Cờ (Flags) để chỉ thêm các mục vào legend một lần duy nhất
    added_ci_legend = False

    for depth, matrix in data_matrix_dict.items():
        if len(matrix) == 0: continue
            
        mean_curve = np.mean(matrix, axis=0)
        lower_bound = np.percentile(matrix, 5, axis=0)  
        upper_bound = np.percentile(matrix, 95, axis=0) 
        
        c = colors.get(depth, 'black')
        
        # Nhóm Legend 1: Mô phỏng xác suất (Solid line & shaded area)
        label_ci = '95% Confidence Band' if not added_ci_legend else ""
        plt.fill_between(time_array, lower_bound, upper_bound, color=c, alpha=0.15, label=label_ci)
        plt.plot(time_array, mean_curve, color=c, linestyle='-', linewidth=2, label=f'Sim Mean {depth}mm')
        
        added_ci_legend = True

        # Nhóm Legend 2: Dữ liệu gốc (Dashed line)
        if df_baseline is not None:
            col_idx = columns_dict.get(depth)
            if col_idx is not None and col_idx < len(df_baseline.columns):
                val_base = df_baseline.iloc[:, col_idx].values
                # Cắt độ dài cho khớp với time_base
                min_len_base = min(len(time_base), len(val_base))
                plt.plot(time_base[:min_len_base], val_base[:min_len_base], color=c, linestyle='--', linewidth=2.5, label=f'Baseline {depth}mm')

    # Trang trí đồ thị
    plt.title(title, fontsize=15, fontweight='bold')
    plt.xlabel('Time (minutes)', fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.xlim(0, max(time_array) if time_array is not None else 240)
    
    # MỚI: Tạo Legend 2 cột để không bị quá dài
    plt.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=10, ncol=2)
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.tight_layout() 
    
    save_path = os.path.join(output_dir, save_name)
    plt.savefig(save_path, dpi=300)
    print(f"-> Đã lưu biểu đồ tại: {save_path}")
    # plt.show()

# ===================================================================
# 5. THỰC THI VẼ
# ===================================================================
if time_T is not None:
    plot_confidence_intervals(time_T, matrix_T, baseline_T_file, cols_T,
                              "Temperature Evolution (Sim vs Baseline)", 
                              "Temperature (°C)", "Confidence_Intervals_Temperature.png")

if time_Pg is not None:
    plot_confidence_intervals(time_Pg, matrix_Pg, baseline_Pg_file, cols_Pg,
                              "Gas Pressure Evolution (Sim vs Baseline)", 
                              "Gas Pressure (MPa)", "Confidence_Intervals_GasPressure.png")