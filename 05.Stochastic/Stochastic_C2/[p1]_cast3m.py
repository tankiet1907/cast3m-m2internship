import openturns as ot
import os
import subprocess

# =========================================================
# ESTABLISHING PROJECT PATHWAYS
# =========================================================
working_dir = r"D:\cast3m-m2internship\05.Stochastic\Stochastic_C2"
csv_dir = os.path.join(working_dir, "CSV")
os.makedirs(csv_dir, exist_ok=True)

# Bỏ input_csv_file vì Cast3M tự sinh random K0
output_csv_file = os.path.join(working_dir, "OpenTURNS_Outputs_Y.csv")

# =========================================================
# 1. WRAPPER FUNCTION TO OPENTURNS CALL CAST3M
# =========================================================
def run_cast3m(run_number):
    castem_bat = r"C:\Cast3M\PCW_24\bin\castem24.bat"
    start_in_dir = r"C:\Cast3M\PCW_24\sources"

    # Tên file template của bạn (có thể đổi tên cho phù hợp với bản ALEA)
    template_file = os.path.join(working_dir, "THM_pc (alea).dgibi.in") 
    run_file = os.path.join(working_dir, "run_temp.dgibi")
    
    csv_u = os.path.join(csv_dir, f"u_results_no_{run_number}.csv")
    
    # Xóa file cũ nếu đã tồn tại để tránh đọc nhầm dữ liệu cũ
    if os.path.exists(csv_u): 
        os.remove(csv_u)
    
    with open(template_file, 'r', encoding='utf-8') as file:
        template = file.read()
        
    # Chỉ cần thay thế vị trí lưu file xuất (@CSV_U@)
    # Cast3M sẽ tự động dùng ALEA để tính toán bên trong
    content = template.replace('@CSV_U@', csv_u)
    
    with open(run_file, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"\n[Đang chạy vòng lặp số {run_number}] ...")
    
    try:
        with open(run_file, 'r', encoding='utf-8') as f_in:
            subprocess.run(
                [castem_bat],          
                cwd=start_in_dir,      
                stdin=f_in,           
                shell=True             
            )
    except Exception as e:
        print(f"System Error: {e}")

    # ---------------------------------------------------------
    # TRÍCH XUẤT KẾT QUẢ TỪ FILE CSV_U 
    # ---------------------------------------------------------
    y_val = 0.0 
    if os.path.exists(csv_u):
        with open(csv_u, 'r', encoding='utf-8') as f:
            lines = [line for line in f.read().splitlines() if line.strip()]
            if len(lines) > 1:
                last_row = lines[-1].split(';') 
                try:
                    y_val = float(last_row[1]) 
                except (IndexError, ValueError):
                    print(f"Lỗi: Không thể chuyển đổi dữ liệu '{last_row}' thành số.")
    else:
        print(f"Lỗi: Không tìm thấy file đầu ra {csv_u}. Cast3M có thể đã bị lỗi.")

    return [y_val]


# =========================================================
# 2. RUNNING LOOPS & COLLECTING DATA
# =========================================================
if __name__ == "__main__":
    
    N_loops = 30
    print(f"Bắt đầu chạy mô hình Cast3M {N_loops} lần.")
    print("Ghi chú: Trường ngẫu nhiên ALEA được xử lý tự động bên trong file dgibi.")
    
    final_results = []
    
    # Chạy vòng lặp từ 1 đến N_loops
    for i in range(1, N_loops + 1):
        res = run_cast3m(i)
        final_results.append(res)
   
    # ---------------------------------------------------------
    # XUẤT OUTPUT (Y) RA FILE CSV
    # ---------------------------------------------------------
    output_sample = ot.Sample(final_results)
    output_sample.setDescription(['Shrinkage_Strain']) 
    output_sample.exportToCSVFile(output_csv_file, ";")
    print(f"\n-> Đã lưu kết quả Output vào: {output_csv_file}")
    
    print("\n[SCRIPT 1 FINISHED RUNNING] Dữ liệu đã sẵn sàng để vẽ PDF/CDF!")