import os
import glob
import pandas as pd

# =========================================================
# 1. CẤU HÌNH ĐƯỜNG DẪN 
# =========================================================
working_dir = r"D:\cast3m-m2internship\04.OpenTURNS\Test_02"
csv_dir = os.path.join(working_dir, "CSV")
output_csv_file = os.path.join(working_dir, "OpenTURNS_Outputs_Y.csv")

# =========================================================
# 2. HÀM ĐỌC GIÁ TRỊ MAX (DÙNG PANDAS ĐỂ ĐẢM BẢO CHÍNH XÁC)
# =========================================================
def get_max_from_raw_csv(file_path, col_idx):
    """
    Đọc file CSV thô của Cast3M, bỏ qua các dòng rác và lấy giá trị lớn nhất 
    ở cột col_idx (đếm từ 0).
    """
    if not os.path.exists(file_path):
        return -9999.0
    
    try:
        # Đọc dữ liệu, ép kiểu tất cả về chuỗi để xử lý chữ 'D' (ví dụ 1.2D03 -> 1.2E03)
        df = pd.read_csv(file_path, sep=';', header=None, dtype=str, on_bad_lines='skip')
        
        # Xóa các dòng có chứa chữ cái ở cột cần lấy (bỏ qua Header hoặc Comment)
        col_data = df.iloc[:, col_idx]
        col_data = col_data.dropna().astype(str).str.strip().str.upper()
        col_data = col_data.str.replace('D', 'E') # Đổi format khoa học của Fortran/Cast3M sang Python
        
        # Ép về kiểu số thực (float) và bắt lỗi các dòng chứa text (như 'T_10', 'Time')
        numeric_data = pd.to_numeric(col_data, errors='coerce').dropna()
        
        if len(numeric_data) > 0:
            return numeric_data.max()
        else:
            return -9999.0
            
    except Exception as e:
        print(f"  [Lỗi] Không thể đọc cột {col_idx} trong file {file_path}. Lỗi: {e}")
        return -9999.0

# =========================================================
# 3. QUÉT 30 FILE VÀ TỔNG HỢP DỮ LIỆU
# =========================================================
N_loops = 30
all_results = []

print(f"Đang càn quét thư mục {csv_dir} để lấy giá trị MAX...")

for i in range(1, N_loops + 1):
    csv_temp = os.path.join(csv_dir, f"temp_results_no_{i}.csv")
    csv_pg = os.path.join(csv_dir, f"pg_results_no_{i}.csv")
    
    # ---------------------------------------------------------
    # CHỈ SỐ CỘT (COL_INDEX) CHUẨN XÁC:
    # Cast3M xuất theo dạng: Time(0) ; Value(1) ; Time(2) ; Value(3) ...
    # ---------------------------------------------------------
    
    # Lấy nhiệt độ (T) - Đảm bảo lấy các cột LẺ
    T00_max = get_max_from_raw_csv(csv_temp, 1)
    T10_max = get_max_from_raw_csv(csv_temp, 3)
    T20_max = get_max_from_raw_csv(csv_temp, 5)
    T30_max = get_max_from_raw_csv(csv_temp, 7)
    T40_max = get_max_from_raw_csv(csv_temp, 9)
    T50_max = get_max_from_raw_csv(csv_temp, 11)
    T120_max = get_max_from_raw_csv(csv_temp, 13)

    # Lấy áp suất khí (Pg) - Tương tự, lấy các cột LẺ
    Pg10_max = get_max_from_raw_csv(csv_pg, 3)
    Pg20_max = get_max_from_raw_csv(csv_pg, 5)
    Pg30_max = get_max_from_raw_csv(csv_pg, 7)
    Pg40_max = get_max_from_raw_csv(csv_pg, 9)
    Pg50_max = get_max_from_raw_csv(csv_pg, 11)
    
    # Gom thành 1 mảng 12 phần tử cho vòng lặp hiện tại
    run_result = [T00_max, T10_max, T20_max, T30_max, T40_max, T50_max, T120_max, 
                  Pg10_max, Pg20_max, Pg30_max, Pg40_max, Pg50_max]
    
    all_results.append(run_result)
    
    # In nhẹ ra màn hình để kiểm tra xem đã hết bị dính số 240.0 chưa
    if i == 1:
        print(f"  -> Test Run 1 - T10_Max = {T10_max} (Không được là 240.0)")

# =========================================================
# 4. GHI ĐÈ LẠI FILE OUTPUT_Y.CSV CHUẨN XÁC
# =========================================================
column_names = [
    "T_00_Max", "T_10_Max", "T_20_Max", "T_30_Max", "T_40_Max", "T_50_Max", "T_120_Max",
    "Pg_10_Max", "Pg_20_Max", "Pg_30_Max", "Pg_40_Max", "Pg_50_Max"
]

# Tạo DataFrame bằng Pandas và xuất ra CSV
df_final = pd.DataFrame(all_results, columns=column_names)

# Xuất ra với separator là dấu chấm phẩy (;) để tương thích với OpenTURNS Script 2
df_final.to_csv(output_csv_file, sep=';', index=False)

print("\n" + "="*60)
print(f"ĐÃ TẠO THÀNH CÔNG FILE OUTPUT MỚI TẠI:")
print(output_csv_file)
print("Bây giờ bạn có thể mở Script 2 và chạy vòng lặp phân tích bình thường!")
print("="*60)