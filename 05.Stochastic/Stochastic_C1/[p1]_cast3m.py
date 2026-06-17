import openturns as ot
import os
import subprocess
import glob
import csv

# =========================================================
# ESTABLISHING PROJECT PATHWAYS
# =========================================================
working_dir = r"D:\cast3m-m2internship\05.Stochastic\Stochastic_C1"
csv_dir = os.path.join(working_dir, "CSV")
os.makedirs(csv_dir, exist_ok=True)

input_csv_file = os.path.join(working_dir, "OpenTURNS_Inputs_X.csv")
output_csv_file = os.path.join(working_dir, "OpenTURNS_Outputs_Y.csv")

# =========================================================
# 1. WRAPPER FUNCTION TO OPENTURNS CALL CAST3M
# =========================================================
def run_cast3m(X, run_number):
    # Giải nén giá trị K0 từ biến đầu vào X (X hiện tại chỉ có 1 phần tử)
    k0_val = X[0]
    
    castem_bat = r"C:\Cast3M\PCW_24\bin\castem24.bat"
    start_in_dir = r"C:\Cast3M\PCW_24\sources"

    template_file = os.path.join(working_dir, "THM_pc (lhs).dgibi.in") 
    run_file = os.path.join(working_dir, "run_temp.dgibi")
    
    csv_u = os.path.join(csv_dir, f"u_results_no_{run_number}.csv")
    
    for f_path in [csv_u]:
        if os.path.exists(f_path): os.remove(f_path)
    
    with open(template_file, 'r', encoding='utf-8') as file:
        template = file.read()
        
    # Thay thế @KINT@ bằng giá trị k0 (dùng định dạng khoa học E để Cast3M dễ đọc)
    content = template.replace('@KINT@', f"{k0_val:.4E}")\
                      .replace('@CSV_U@', csv_u)
    with open(run_file, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"\n[Running loop no {run_number}] Loading: K0={k0_val:.4E}")
    
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
    # TRÍCH XUẤT KẾT QUẢ TỪ FILE CSV_U (Mới bổ sung)
    # ---------------------------------------------------------
    y_val = 0.0 # Giá trị mặc định nếu có lỗi
    if os.path.exists(csv_u):
        with open(csv_u, 'r', encoding='utf-8') as f:
            # Đọc tất cả các dòng, bỏ qua dòng trống
            lines = [line for line in f.read().splitlines() if line.strip()]
            if len(lines) > 1:
                # Lấy dòng cuối cùng (bước thời gian cuối) và tách bằng dấu ';'
                last_row = lines[-1].split(';') 
                try:
                    # LƯU Ý TÙY CHỈNH: 
                    # last_row[1] nghĩa là lấy cột thứ 2 (index 1). 
                    # Nếu độ co ngót của bạn ở cột khác, hãy đổi số 1 này.
                    y_val = float(last_row[1]) 
                except (IndexError, ValueError):
                    print(f"Lỗi: Không thể chuyển đổi dữ liệu '{last_row}' thành số.")
    else:
        print(f"Lỗi: Không tìm thấy file đầu ra {csv_u}. Cast3M có thể đã bị lỗi.")

    # Trả về kết quả dưới dạng danh sách (list) để tương thích với OpenTURNS Sample
    return [y_val]


# =========================================================
# 2. ESTABLISHING OPENTURNS AND RUNNING LOOPS + SAVING DATA
# =========================================================
if __name__ == "__main__":
    print("Initialize OpenTURNS environment to generate LHS samples...")
    
    # 1. Định nghĩa phân phối duy nhất cho K0
    mean_k0 = 8.5e-20
    cv_k0 = 0.3
    std_k0 = mean_k0 * cv_k0  # Độ lệch chuẩn = 2.55e-20
    
    # Sử dụng phân phối LogNormal
    dist_K0 = ot.LogNormalMuSigma(mean_k0, std_k0, 0.0).getDistribution()
    
    my_distribution = ot.JointDistribution([dist_K0])
    my_distribution.setDescription(['K0'])

    N_loops = 30
    experiment = ot.LHSExperiment(my_distribution, N_loops)
    input_sample = experiment.generate()
    print(f"{N_loops} parameter set has been created. Start running Cast3M automatically.")
    
    # Xuất Input (X)
    input_sample.exportToCSVFile(input_csv_file, ";")
    print(f"-> Saved Input Samples to: {input_csv_file}")
    
    # Chạy vòng lặp và thu thập Output (Y)
    final_results = []
    for i in range(N_loops):
        res = run_cast3m(input_sample[i], i + 1)
        final_results.append(res)
   
    # ---------------------------------------------------------
    # XUẤT OUTPUT (Y) RA FILE CSV (Mới bổ sung)
    # ---------------------------------------------------------
    output_sample = ot.Sample(final_results)
    output_sample.setDescription(['Shrinkage_Strain']) # Đổi tên cột cho phù hợp
    output_sample.exportToCSVFile(output_csv_file, ";")
    print(f"-> Saved Output Samples to: {output_csv_file}")
    
    print("\n[SCRIPT 1 FINISHED RUNNING] You can now close this file and run Script 2!")