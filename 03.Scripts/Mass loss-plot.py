import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ===================================================================
# 1. NHẬP DỮ LIỆU THỰC NGHIỆM (MASS LOSS)
# ===================================================================

# Trục thời gian thực nghiệm: từ 5 đến 240, bước 5 (48 điểm)
time_exp = np.arange(5, 245, 5)

# Dữ liệu Mass Loss thực nghiệm (từ ảnh, đơn vị: %)
ML_EXP = [
    -0.01193, -0.02516, -0.0447,  -0.07573, -0.10676,
    -0.14948, -0.19356, -0.21865, -0.168,   -0.19419,
    -0.08909, -0.21216, -0.50029, -0.34954, -0.71796,
    -0.68435, -0.73788, -0.80226, -0.86813, -0.93581,
    -1.00429, -1.07277, -1.14125, -1.21438, -1.29057,
    -1.36677, -1.44296, -1.51915, -1.59569, -1.67273,
    -1.74976, -1.82679, -1.90383, -1.9757,  -2.04728,
    -2.11886, -2.19044, -2.26202, -2.33111, -2.39502,
    -2.45892, -2.52283, -2.58673, -2.65064, -2.71454,
    -2.77845, -2.84235, -2.90418
]

# Màu sắc (giữ nhất quán với Gas Pressure script)
color_exp  = 'blue'
color_sim  = 'red'

# ===================================================================
# 2. ĐỌC DỮ LIỆU TỪ CASTEM CSV (MASS LOSS)
# ===================================================================

plt.figure(figsize=(10, 8))

csv_file = r'D:\cast3m-m2internship\02.Simulation\02.Results\MassLoss_1min_Intervals.csv'

try:
    df_castem = pd.read_csv(csv_file, sep=';')
    time_sim  = df_castem.iloc[:, 0]

    # Điều chỉnh chỉ số cột theo cấu trúc file CSV của bạn
    plt.plot(time_sim, df_castem.iloc[:, 1], color=color_sim, linestyle='-', linewidth=1.5, label='Sim Mass Loss')

except FileNotFoundError:
    print(f"Không tìm thấy file: {csv_file}. Vui lòng kiểm tra lại đường dẫn!")
except Exception as e:
    print(f"Lỗi khi đọc file CSV: {e}")

# ===================================================================
# 3. VẼ DỮ LIỆU THỰC NGHIỆM
# ===================================================================

plt.plot(time_exp, ML_EXP, color=color_exp, linestyle=':', linewidth=2, label='Exp Mass Loss')

# ===================================================================
# 4. TÙY CHỈNH GIAO DIỆN ĐỒ THỊ
# ===================================================================

plt.title('Mass Loss: Simulation (Solid) vs Experimental (Dotted)',
          fontsize=14, fontweight='bold')
plt.xlabel('Time (min)', fontsize=12)
plt.ylabel('Mass Loss (%)', fontsize=12)

plt.xlim(0, 240)
#plt.ylim(-3.5, 0.)

plt.xticks(np.arange(0, 241, 20))
#plt.yticks(np.arange(-3.5, 0.51, 0.5))

plt.grid(True, which='both', linestyle='-', color='lightgrey')
plt.legend(loc='lower left', fontsize=10)

plt.tight_layout()

plt.savefig(
    r'D:\cast3m-m2internship\01.Report\figures\plots\MassLoss_results_Comparison.png',
    dpi=300
)

plt.show()