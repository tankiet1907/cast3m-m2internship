import matplotlib
# Cấu hình bắt buộc cho Windows / VS Code để tự bật cửa sổ đồ thị độc lập
matplotlib.use('TkAgg') 
import matplotlib.pyplot as plt
import numpy as np

print("--- KHỞI CHẠY ĐOẠN CODE TEST TUYẾN TÍNH ---")

# 1. Tạo dữ liệu cơ bản cho 2 trục X và Y (Ví dụ: phương trình y = 2x + 5)
x = np.array([0, 1, 2, 3, 4, 5])
y = 2 * x + 5

# 2. Tiến hành vẽ đường thẳng đồ thị
plt.figure(figsize=(6, 4)) # Khởi tạo kích thước khung hình
plt.plot(x, y, linestyle='-', marker='o', color='blue', label='Đường tuyến tính (y = 2x + 5)')

# 3. Định dạng tiêu đề, tên trục và lưới mờ
plt.title('Basic Linear Plot Test', fontsize=12, fontweight='bold')
plt.xlabel('Trục X (Tọa độ X)', fontsize=10)
plt.ylabel('Trục Y (Tọa độ Y)', fontsize=10)
plt.grid(True, linestyle=':', alpha=0.6) # Đổ lưới mờ tọa độ
plt.legend(loc='upper left') # Hiển thị chú thích bảng màu ở góc trên bên trái
plt.tight_layout()

# 4. Gọi lệnh hiển thị và giữ cửa sổ đồ thị tương tác không bị tự đóng
print("--> Đang bật cửa sổ đồ thị... Hãy nhấn nút X ở góc cửa sổ đó để kết thúc test.")
plt.show(block=True)

print("--- KIỂM TRA HOÀN TẤT ---")