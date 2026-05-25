import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# =====================================================================
# 1. KHỞI TẠO DỮ LIỆU THỰC NGHIỆM ĐỐI CHIẾU CỦA DAUTI (MỖI 5 PHÚT)
# =====================================================================
time_dauti = np.arange(0, 245, 5)  # Từ 0 đến 240 phút, bước nhảy 5

# Dữ liệu mẫu trích xuất từ file của bạn cho các vị trí (ví dụ tại 00mm và 10mm)
# Thay thế/bổ sung chính xác mảng số liệu Dauti của bạn tại đây
t_dauti_00mm = np.array([
    20.0, 116.6, 158.0, 186.7, 204.9, 225.2, 239.2, 251.0, 261.5, 272.0,
    281.1, 289.5, 296.5, 303.5, 310.5, 316.1, 323.1, 329.4, 334.3, 339.2,
    344.8, 349.7, 355.2, 359.4, 363.6, 368.5, 372.7, 377.0, 381.2, 385.4,
    389.6, 393.8, 397.3, 400.8, 404.3, 407.8, 411.3, 414.1, 417.6, 420.4,
    423.2, 426.0, 428.8, 431.6, 434.4, 437.2, 440.0, 442.1, 444.9, 447.0
])

# Trường hợp mảng Dauti ngắn hơn do chưa nhập đủ, ta cắt ngắn thời gian tương ứng để vẽ không lỗi
if len(t_dauti_00mm) < len(time_dauti):
    time_dauti = time_dauti[:len(t_dauti_00mm)]

# =====================================================================
# 2. ĐỌC DỮ LIỆU MÔ PHỎNG TỪ FILE CSV (XUẤT TỪ CAST3M)
# =====================================================================
csv_file = r"D:\castem\Temperature_5min_Intervals.csv"  # Thay bằng tên file thực tế của bạn

try:
    df_sim = pd.read_csv(csv_file)
    sim_available = True
    print(f"--> Đọc thành công file mô phỏng: {csv_file}")
except FileNotFoundError:
    sim_available = False
    print(f"[CẢNH BÁO] Không tìm thấy file {csv_file}. Chỉ vẽ dữ liệu Dauti.")

# =====================================================================
# 3. PHẦN CẤU HÌNH ĐỒ THỊ CHUẨN ĐỂ ĐƯA VÀO LATEX
# =====================================================================
plt.figure(figsize=(8, 6), dpi=300)  # Độ phân giải cao cho bài báo/báo cáo

# Vẽ dữ liệu Dauti (Dạng nét đứt - Dashed lines theo đúng yêu cầu)
plt.plot(time_dauti, t_dauti_00mm, linestyle='--', color='black', linewidth=1.5, label='Dauti 2018 - 00mm (Exp)')

# Vẽ dữ liệu mô phỏng từ Cast3M nếu có file (Nét liền - Solid lines)
if sim_available:
    # Đảm bảo trục thời gian trong file trùng khớp (phút)
    # Nếu Cast3M đang lưu giây, hãy chia cho 60: df_sim['Time(min)'] = df_sim['Time(s)'] / 60
    plt.plot(df_sim['Time(min)'], df_sim['T_00mm'], linestyle='-', color='blue', linewidth=2, label='Cast3M - 00mm (Sim)')
    
    # Bạn có thể un-comment để vẽ thêm các vị trí khác khi có dữ liệu
    # plt.plot(df_sim['Time(min)'], df_sim['T_10mm'], linestyle='-', color='green', linewidth=2, label='Cast3M - 10mm (Sim)')

# =====================================================================
# 4. ĐỒNG NHẤT TRỤC TỌA ĐỘ VÀ FORMAT (Theo form của luận văn Dauti)
# =====================================================================
plt.title("Temperature Evolution: Comparison between Dauti and Cast3M", fontsize=12, fontweight='bold', pad=15)
plt.xlabel("Time (minutes)", fontsize=11)
plt.ylabel("Temperature (°C)", fontsize=11)

plt.xlim(0, 240)      # Giới hạn trục X giống hệt Dauti
plt.ylim(0, 500)      # Thay đổi tùy thuộc vào đỉnh nhiệt độ dải thực nghiệm

plt.grid(True, linestyle=':', alpha=0.6)  # Đổ lưới mờ giúp dễ so sánh tọa độ
plt.legend(loc='lower right', frameon=True, edgecolor='gray')
plt.tight_layout()

# Lưu đồ thị dạng Vector (.pdf) để chèn vào LaTeX không bị vỡ nét, kèm 1 file .png xem nhanh
plt.savefig("temperature_comparison.pdf", format="pdf")
plt.savefig("temperature_comparison.png", format="png")
print("--> Đã xuất đồ thị thành công ra file PDF và PNG!")

# Hiển thị đồ thị lên màn hình
plt.show()
