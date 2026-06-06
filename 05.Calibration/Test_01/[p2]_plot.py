import os
import glob
import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# =========================================================
# 1. THIẾT LẬP ĐƯỜNG DẪN THƯ MỤC
# =========================================================
working_dir = r"D:\cast3m-m2internship\05.Calibration\Test_01"
csv_dir = r"D:\cast3m-m2internship\05.Calibration\Test_01\CSV"
output_dir = os.path.join(working_dir, "Plots")
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 1. Định nghĩa màu sắc theo chuẩn Cast3M
colors = {
    '00': 'blue',
    '10': 'red',
    '20': 'gold',
    '30': 'deeppink',
    '40': 'green',
    '50': 'cyan',
    '120': 'black'
}

# =========================================================
# 2. HÀM TỰ ĐỘNG ĐỌC FILE VÀ VẼ ĐỒ THỊ (CẬP NHẬT TRỤC)
# =========================================================
def plot_and_save(file_list, plot_type):
    valid_depths = ['00', '10', '20', '30', '40', '50', '120']
    for file_path in file_list:
        filename = os.path.basename(file_path)
        
        # Trích xuất KINT và AK từ tên file bằng Regex
        match = re.search(r'KINT_(.+)_AK_([0-9.]+)', filename)
        if match:
            kint_val = match.group(1)
            ak_val = match.group(2)
            title = f"{plot_type} | KINT: {kint_val} | AK: {ak_val}"
            save_name = f"{plot_type}_KINT_{kint_val}_AK_{ak_val}.png"
        else:
            title = f"{plot_type} - {filename}"
            save_name = f"{filename}.png"

        try:
            df = pd.read_csv(file_path, sep=';')
            plt.figure(figsize=(10, 6))
            x_col = df.columns[0]
            
            # VÒNG LẶP VẼ ĐỒ THỊ THÔNG MINH
            for y_col in df.columns[1:]:
                # TÌM ĐỘ SÂU TRONG TÊN CỘT
                # Tìm các số xuất hiện trong tên cột
                match_depth = re.search(r'(\d+)', y_col)
                if match_depth:
                    depth_key = match_depth.group(1)
                    
                    # CHỈ VẼ NẾU ĐỘ SÂU NẰM TRONG DANH SÁCH CHO PHÉP
                    if depth_key in valid_depths:
                        plot_color = colors.get(depth_key, 'gray')
                        plt.plot(df[x_col], df[y_col], color=plot_color, 
                                 label=f'Sim {depth_key}mm', linewidth=2)
            
            # ---------------------------------------------------------
            # THIẾT LẬP CỐ ĐỊNH TRỤC TỌA ĐỘ THEO YÊU CẦU 
            # ---------------------------------------------------------
            # Trục hoành (Thời gian): Từ 0 đến 240, cách nhau 20
            plt.xlim(0, 240)
            plt.xticks(np.arange(0, 241, 20), rotation=45, fontsize=10) 
            plt.xlabel("Time (min)", fontsize=12)

            # Trục tung (Nhiệt độ / Áp suất)
            if plot_type == "Temp":
                plt.ylabel("Temperature (°C)", fontsize=12)
                plt.ylim(0, 500)
                plt.yticks(np.arange(0, 501, 50))  # Từ 0 đến 500, cách 50
                
            elif plot_type == "Pg":
                plt.ylabel("Gas Pressure (MPa)", fontsize=12)
                plt.ylim(0, 4.0)
                plt.yticks(np.arange(0, 4.1, 0.5)) # Từ 0 đến 4.0, cách 0.5
            # ---------------------------------------------------------
            
            # Làm đẹp đồ thị
            plt.title(title, fontsize=14, fontweight='bold')
            plt.grid(True, linestyle='--', alpha=0.6)
            plt.legend(loc="upper right", fontsize=10)
            
            save_path = os.path.join(output_dir, save_name)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            plt.close() 
            
            print(f"-> Đã lưu ảnh: {save_name}")
            
        except Exception as e:
            print(f"-> LỖI đọc file {filename}: {e}")

# =========================================================
# 3. THỰC THI CHƯƠNG TRÌNH
# =========================================================
if __name__ == "__main__":
    temp_files = glob.glob(os.path.join(csv_dir, "temp_results_no_*.csv"))
    pg_files = glob.glob(os.path.join(csv_dir, "pg_results_no_*.csv"))

    print(f"Tìm thấy {len(temp_files)} file Nhiệt độ và {len(pg_files)} file Áp suất.\n")

    print("--- BẮT ĐẦU VẼ ĐỒ THỊ NHIỆT ĐỘ ---")
    plot_and_save(temp_files, "Temp")

    print("\n--- BẮT ĐẦU VẼ ĐỒ THỊ ÁP SUẤT ---")
    plot_and_save(pg_files, "Pg")

    print(f"\n[HOÀN TẤT] Bạn hãy vào thư mục '{output_dir}' để kiểm tra thành quả!")