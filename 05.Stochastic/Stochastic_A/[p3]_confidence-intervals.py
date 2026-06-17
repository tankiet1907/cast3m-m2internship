import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import glob

# ===================================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN VÀ THÔNG SỐ
# =========================================================
working_dir = r"D:\cast3m-m2internship\05.Stochastic\Stochastic_A"
csv_dir = os.path.join(working_dir, "CSV")
output_dir = os.path.join(working_dir, "Plots")
N_loops = 30

# MỚI: Đường dẫn đến file kết quả gốc (Baseline)
baseline_T_file  = r'D:\cast3m-m2internship\03.Calibration\Calibration_03\temp_results_no_32_KINT_8.5e-20_AK_4.0.csv'
baseline_Pg_file = r'D:\cast3m-m2internship\03.Calibration\Calibration_03\pg_results_no_32_KINT_8.5e-20_AK_4.0.csv'

colors = {
    '00': 'blue',     # Không có trong trend plot, giữ màu đen
    '10': 'red',       
    '20': 'gold',      
    '30': 'deeppink',  
    '40': 'green',     
    '50': 'cyan',      
    '120': 'gray'      # Không có trong trend plot, giữ màu xám
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
# 4. HÀM VẼ ĐỒ THỊ 
# ===================================================================
def plot_confidence_intervals(time_array, data_matrix_dict, baseline_file, columns_dict, title, ylabel, save_name):
    # Đổi sang figsize=(10, 8) giống trend plot
    plt.figure(figsize=(10, 8))
    
    df_baseline = None
    try:
        if os.path.exists(baseline_file):
            df_baseline = pd.read_csv(baseline_file, sep=';', on_bad_lines='skip')
            time_base = df_baseline.iloc[:, 0].values
        else:
            print(f"Cảnh báo: Không tìm thấy file gốc {baseline_file}")
    except Exception as e:
        print(f"Lỗi đọc file gốc: {e}")

    added_ci_legend = False

    for depth, matrix in data_matrix_dict.items():
        if len(matrix) == 0: continue
            
        mean_curve = np.mean(matrix, axis=0)
        lower_bound = np.percentile(matrix, 5, axis=0)  
        upper_bound = np.percentile(matrix, 95, axis=0) 
        
        c = colors.get(depth, 'black')
        
        # Plot theo style trend plot: linewidth mỏng hơn
        label_ci = '95% Confidence Band' if not added_ci_legend else ""
        plt.fill_between(time_array, lower_bound, upper_bound, color=c, alpha=0.15, label=label_ci)
        plt.plot(time_array, mean_curve, color=c, linestyle='-', linewidth=1.0, label=f'Sim Mean {depth}mm')
        
        added_ci_legend = True

        if df_baseline is not None:
            col_idx = columns_dict.get(depth)
            if col_idx is not None and col_idx < len(df_baseline.columns):
                val_base = df_baseline.iloc[:, col_idx].values
                min_len_base = min(len(time_base), len(val_base))
                plt.plot(time_base[:min_len_base], val_base[:min_len_base], color=c, linestyle='--', linewidth=1.0, label=f'Baseline {depth}mm')

    # Trang trí đồ thị đồng bộ với trend plot
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel('Time (min)', fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    
    # Cài đặt giới hạn trục X
    plt.xlim(0, 240)
    plt.xticks(np.arange(0, 241, 20), fontsize=10)
    
    # Cài đặt giới hạn trục Y riêng cho áp suất (giống trend plot)
    if "Pressure" in title:
        plt.ylim(0, 4.0)
        plt.yticks(np.arange(0, 4.1, 0.5), fontsize=10)
    else:
        plt.yticks(fontsize=10)
        
    plt.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=9, ncol=2)
    plt.grid(True, linestyle='--', alpha=0.6)
    
    save_path = os.path.join(output_dir, save_name)
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"-> Đã lưu biểu đồ tại: {save_path}")
    plt.close()

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