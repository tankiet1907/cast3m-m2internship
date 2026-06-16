import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ===================================================================
# 1. THIẾT LẬP TRỤC THỜI GIAN VÀ MÀU SẮC
# ===================================================================

# Hệ màu chuẩn đồng nhất với các biểu đồ trước
colors = {
    '00': 'blue',       # BLEU
    '10': 'red',        # ORAN
    '20': 'gold',       # JAUN
    '30': 'deeppink',   # ROSE
    '40': 'green',      # VERT
    '50': 'cyan',       # TURQ
    '120': 'black'      # Dùng Đen/Xám để dễ nhìn trên nền trắng thay vì BLAN (trắng)
}

# ===================================================================
# 2. ĐỌC DỮ LIỆU TỪ CASTEM CSV VÀ PLOT
# ===================================================================

plt.figure(figsize=(10, 8))

# Đường dẫn file CSV kết quả Capillary Pressure
csv_file = r'D:\cast3m-m2internship\02.Simulation\02.Results\CapillaryPressure_1min_Intervals.csv'

try:
    # Đọc file CSV (Cast3M xuất ngăn cách bằng dấu chấm phẩy)
    df_castem = pd.read_csv(csv_file, sep=';')
    time_sim = df_castem.iloc[:, 0]
    
    # Vẽ kết quả mô phỏng (Nét liền - Solid lines)
    # Lấy các cột giá trị Y tương ứng ở index lẻ: 1, 3, 5, 7, 9
    plt.plot(time_sim, df_castem.iloc[:, 1], color=colors['10'], linestyle='-', linewidth=2, label='Sim Pc 10mm')
    plt.plot(time_sim, df_castem.iloc[:, 3], color=colors['20'], linestyle='-', linewidth=2, label='Sim Pc 20mm')
    plt.plot(time_sim, df_castem.iloc[:, 5], color=colors['30'], linestyle='-', linewidth=2, label='Sim Pc 30mm')
    plt.plot(time_sim, df_castem.iloc[:, 7], color=colors['40'], linestyle='-', linewidth=2, label='Sim Pc 40mm')
    plt.plot(time_sim, df_castem.iloc[:, 9], color=colors['50'], linestyle='-', linewidth=2, label='Sim Pc 50mm')

except FileNotFoundError:
    print(f"Không tìm thấy file: {csv_file}. Vui lòng kiểm tra lại đường dẫn!")
except Exception as e:
    print(f"Lỗi khi đọc file CSV: {e}")

# ===================================================================
# 3. TÙY CHỈNH GIAO DIỆN ĐỒ THỊ
# ===================================================================

plt.title('Capillary Pressure Evolution (Simulation Results)', fontsize=14, fontweight='bold')
plt.xlabel('Time (min)', fontsize=12)
plt.ylabel('Capillary Pressure (MPa)', fontsize=12)

# Thiết lập giới hạn trục X
plt.xlim(0, 240)

# Thiết lập bước nhảy trục X là 10 phút
plt.xticks(np.arange(0, 241, 20), rotation=0)

# (Tùy chọn) Trục Y để Matplotlib tự động scale (do PC có biên độ lớn). 
# Nếu bạn muốn cố định trục Y từ 0 đến một số cụ thể (VD: 30 MPa), bỏ comment dòng dưới:
# plt.ylim(0, 30)

plt.grid(True, which='both', linestyle='-', color='lightgrey')

# Hiển thị Legend
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10, ncol=1)

# Tự động căn chỉnh bố cục để không bị cắt chữ
plt.tight_layout()

# LƯU ẢNH (BẮT BUỘC TRƯỚC LỆNH PLT.SHOW)
output_img = r'D:\cast3m-m2internship\01.Report\figures\plots\Capillary_pressure_Simulation.png'
plt.savefig(output_img, dpi=300, bbox_inches='tight')

# HIỂN THỊ ĐỒ THỊ LÊN MÀN HÌNH
plt.show()