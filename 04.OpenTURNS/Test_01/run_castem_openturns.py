import openturns as ot
import os
import subprocess
import glob

# =========================================================
# 1. HÀM WRAPPER ĐỂ OPENTURNS GỌI CAST3M
# =========================================================
def run_cast3m(X, run_number):
    # Nhận 4 giá trị từ OpenTURNS
    kd0, cps0, sl, phi = X
    
    # Các thư mục cấu hình
    castem_bat = r"C:\Cast3M\PCW_24\bin\castem24.bat"
    start_in_dir = r"C:\Cast3M\PCW_24\sources"
    working_dir = r"D:\cast3m-m2internship\04.OpenTURNS\Test_01"
    
    template_file = os.path.join(working_dir, "transient-sample.dgibi.in") # Template file with placeholders
    run_file = os.path.join(working_dir, "run_temp.dgibi")
    # 2. Tạo tên file động theo ý bạn: temp_results-no[1].csv
    csv_output = os.path.join(working_dir, f"temp_results_no_{run_number}.csv")
    
    # Xóa file CSV cũ nếu tồn tại
    if os.path.exists(csv_output):
        os.remove(csv_output)
    
    # Đọc template và thay số
    with open(template_file, 'r') as file:
        template = file.read()
    content = template.replace('@KD0@', str(kd0)).replace('@CPS0@', str(cps0))\
                      .replace('@SL@', str(sl)).replace('@PHI@', str(phi))\
                      .replace('@CSV_NAME@', csv_output) # Điền tên file mới vào
    
    with open(run_file, 'w') as file:
        file.write(content)
        
    command = [castem_bat, run_file]
    
    # Gán giá trị phạt (Penalty) mặc định nếu mô phỏng bị crash
    T_max_out = 9999.0 
    T_min_out = -9999.0
    
    try:
        subprocess.run(
            command,
            cwd=start_in_dir,
            shell=False,
        )
    except Exception as e:
        print(f"Lỗi khi gọi hệ thống: {e}")        
# CHUYỂN ĐOẠN ĐỌC FILE CSV RA NGOÀI KHỐI TRY...EXCEPT
    # Dùng sự tồn tại của file CSV làm "Bằng chứng sống" cho việc Cast3M đã chạy thành công
    if os.path.exists(csv_output):
        try:
            with open(csv_output, 'r') as f:
                lines = f.readlines()
                # Cast3M xuất file EXCE: Dòng 3 (index 2) là Max, Dòng 4 (index 3) là Min
                if len(lines) >= 4:
                    line_max = lines[2].strip() 
                    line_min = lines[3].strip() 
                    
                    T_max_out = float(line_max.split(';')[1])
                    T_min_out = float(line_min.split(';')[1])
        except Exception as read_error:
             print(f"[CẢNH BÁO] Không thể đọc số liệu trong CSV: {read_error}")
    else:
        # Nếu chạy xong mà không thấy CSV đâu, thì đó mới ĐÍCH THỰC là Crash phân kỳ
        print(f"[CẢNH BÁO] MÔ PHỎNG CRASH (Không hội tụ) tại [KD0={kd0:.2f}, CPS0={cps0:.2f}]. Trả về giá trị phạt.")
        
        # Dọn dẹp rác hệ thống sau khi chạy xong
    for d in [start_in_dir, working_dir]:
        for ext in ['*.trace', '*.ps', '*.err']:
            for f in glob.glob(os.path.join(d, ext)):
                try: 
                    os.remove(f)
                except: pass
                    
    # TRẢ VỀ CẢ 2 GIÁ TRỊ DƯỚI DẠNG MẢNG (LIST)
    return [T_max_out, T_min_out]

# =========================================================
# 2. THIẾT LẬP OPENTURNS VÀ CHẠY VÒNG LẶP
# =========================================================
if __name__ == "__main__":
    print("Khởi tạo môi trường OpenTURNS...")
    
    # 1. Định nghĩa phân phối cho 4 biến đầu vào (X)
    dist_KD0 = ot.Uniform(1.5, 2.5)
    dist_CPS0 = ot.Normal(948.0, 50.0)
    dist_SL = ot.Uniform(0.1, 0.3)
    dist_PHI = ot.Uniform(0.15, 0.20)
    
    my_distribution = ot.JointDistribution([dist_KD0, dist_CPS0, dist_SL, dist_PHI])
    
    # 2. LƯU Ý QUAN TRỌNG: Hàm bây giờ có 4 Input và 2 Output
    # Cú pháp: ot.PythonFunction(Số_Input, Số_Output, tên_hàm)
    my_model = ot.PythonFunction(4, 2, run_cast3m)
    
    # 3. Tạo mẫu ngẫu nhiên LHS
    N_loops = 5 # Chạy thử 5 vòng lặp
    experiment = ot.LHSExperiment(my_distribution, N_loops)
    input_sample = experiment.generate()
    
    print(f"Đã tạo {N_loops} bộ thông số. Bắt đầu chạy Cast3M tự động...")
    
    final_results = []
    for i in range(N_loops):
        print(f"--- Đang chạy vòng lặp số: {i+1} ---")
        # Truyền thêm i+1 vào để đặt tên file là [1], [2], [3]...
        res = run_cast3m(input_sample[i], i + 1)
        final_results.append(res)
        
    print("Xong toàn bộ!")




#  old code for reference:
    output_sample = my_model(input_sample)
    
    # 5. In kết quả tổng hợp
    print("-" * 50)
    print("KẾT QUẢ MÔ PHỎNG:")
    print("   [KD0, CPS0, SL, PHI]   -->   T_MAX")
    for i in range(N_loops):
        in_vals = [round(val, 3) for val in input_sample[i]]
        out_val = round(output_sample[i][0], 2)
        print(f"Mẫu {i+1}: {in_vals} --> {out_val} °C")