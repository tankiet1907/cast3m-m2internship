import os
import subprocess
import glob
import itertools
import csv

# CALIBRATION OF THE PERMEABILITY PARAMETERS (KINT, AK) FOR HPC M100

# =========================================================
# ESTABLISHING PROJECT PATHWAYS
# =========================================================
working_dir = r"D:\cast3m-m2internship\05.Calibration\Test_01"
csv_dir = r"D:\cast3m-m2internship\05.Calibration\Test_01\CSV"
os.makedirs(csv_dir, exist_ok=True)

# =========================================================
# 1. WRAPPER FUNCTION TO OPENTURNS CALL CAST3M
# =========================================================
def run_cast3m(X, run_number):
    kint, ak = X
    
    castem_bat = r"C:\Cast3M\PCW_24\bin\castem24.bat"
    start_in_dir = r"C:\Cast3M\PCW_24\sources"

    # make sure the dgibi has fin; at the end and turn off trac and dess to avoid hanging.    
    template_file = os.path.join(working_dir, "20260521-kalifa.dgibi.in") 
    run_file = os.path.join(working_dir, "run_temp.dgibi")
    
    kint_name = f"{kint:.1e}"
    csv_temp = os.path.join(csv_dir, f"temp_results_no_{run_number}_KINT_{kint_name}_AK_{ak}.csv")
    csv_pg = os.path.join(csv_dir, f"pg_results_no_{run_number}_KINT_{kint_name}_AK_{ak}.csv")
    
    for f_path in [csv_temp, csv_pg]:
        if os.path.exists(f_path): os.remove(f_path)
    
    with open(template_file, 'r', encoding='utf-8') as file:
        template = file.read()
    
    kint_str = f"{kint:E}" 
    ak_str = str(ak)
        
    content = template.replace('@KINT@', kint_str)\
                      .replace('@AK@', ak_str)\
                      .replace('@CSV_TEMP@', csv_temp)\
                      .replace('@CSV_PG@', csv_pg)

    with open(run_file, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"\n[Running loop no {run_number}] Loading: KINT={kint:.2e}, AK={ak:.2e}")
    
    # ====================================================================
    # CALL CAST3M BY "COPY-PASTE" THE FILE INTO STDIN (Exactly like the < command in CMD)
    # cd /d "C:\Cast3M\PCW_24\sources" 
    # call "C:\Cast3M\PCW_24\bin\castem24.bat" < "D:\cast3m-m2internship\04.OpenTURNS\Test_02\run_temp.dgibi" --> THIS IS THE EXACT COMMAND WE ARE SIMULATING IN PYTHON BELO (COPY AND PASTE THE CONTENT OF THE .dgibi INTO CASTEM'S STDIN)
    # call "C:\Cast3M\PCW_24\bin\castem24.bat" "D:\cast3m-m2internship\04.OpenTURNS\Test_02\run_temp.dgibi" --> THIS IS NOT WORKING WHEN RUNNING DIRECTLY IN PYTHON, CASTEM CANNOT RUN THE CUSTOM VERSION.
    # ====================================================================
    try:
        with open(run_file, 'r', encoding='utf-8') as f_in:
            subprocess.run(
                [castem_bat],          
                cwd=start_in_dir,      
                stdin=f_in,  # <-- Simulate the "copy-paste" by feeding the .dgibi content into Cast3M's stdin. (< run_temp.dgibi)          
                shell=True             
            )
    except Exception as e:
        print(f"System Error: {e}")

    # ====================================================================
    # WRAPPER FUNCTION TO READ CSV: Extract Max at a Specific Column (Depth)
    # ====================================================================
    def read_max_from_column(csv_path, col_index):
        max_val = -9999.0
        if not os.path.exists(csv_path):
            print(f"[CRASH] File not found {csv_path}.")
            return max_val
            
        try:
            with open(csv_path, 'r') as f:
                lines = f.readlines()
                
            for line in lines:
                line = line.strip()
                # Ignore blank lines or headers.
                if not line or line.startswith('*') or 'Time' in line or 'T_' in line or 'P_' in line:
                    continue
                
                parts = line.split(';')
                
                # Check if this row has enough columns to retrieve data
                if len(parts) > col_index:
                    val_str = parts[col_index].strip().upper().replace('D', 'E')
                    if val_str:
                        try:
                            val = float(val_str)
                            if val > max_val:
                                max_val = val
                        except ValueError:
                            pass # Ignore if conversion fails
                            
        except Exception as e:
            print(f"[NUMBER READING ERROR] File: {csv_path} | Error: {e}")
            
        return max_val

    # EXTRACT MAXIMUM QUANTITIES (Assuming based on column index in your CSV file)
    T_00_max = read_max_from_column(csv_temp, 1)
    T_10_max = read_max_from_column(csv_temp, 3)
    T_20_max = read_max_from_column(csv_temp, 5)
    T_30_max = read_max_from_column(csv_temp, 7)
    T_40_max = read_max_from_column(csv_temp, 9)
    T_50_max = read_max_from_column(csv_temp, 11)
    T_120_max = read_max_from_column(csv_temp, 13)

    Pg_10_max = read_max_from_column(csv_pg, 3) 
    Pg_20_max = read_max_from_column(csv_pg, 5)
    Pg_30_max = read_max_from_column(csv_pg, 7)
    Pg_40_max = read_max_from_column(csv_pg, 9)
    Pg_50_max = read_max_from_column(csv_pg, 11)
        
    # Clean up system debris (Optional)
    for d in [start_in_dir, working_dir]:
        for ext in ['*.trace', '*.ps', '*.err']:
            for f in glob.glob(os.path.join(d, ext)):
                try: os.remove(f)
                except: pass
                    
    # Returns the output string
    return [T_00_max, T_10_max, T_20_max, T_30_max, T_40_max, T_50_max, T_120_max, 
            Pg_10_max, Pg_20_max, Pg_30_max, Pg_40_max, Pg_50_max]

# =========================================================
# 2. ESTABLISHING OPENTURNS AND RUNNING LOOPS + SAVING DATA
# =========================================================
if __name__ == "__main__":
    print("Khởi tạo danh sách các tổ hợp thông số KINT và AK...")
    
    # 1. Khai báo các giá trị muốn thử (Bạn có thể thêm/bớt tùy ý)
    KINT_values = [1e-20, 5e-20, 8e-20, 1e-19, 2e-19]
    AK_values = [1.0, 1.5, 2.0, 2.5, 3.0]
    
    # Tạo tất cả các tổ hợp có thể có (25 tổ hợp)
    # Mỗi phần tử trong parameter_sets sẽ là một tuple: ví dụ (1e-20, 1.0)
    parameter_sets = list(itertools.product(KINT_values, AK_values))
    N_loops = len(parameter_sets)
    
    print(f"Đã tạo {N_loops} bộ thông số. Bắt đầu chạy Cast3M tự động.")
    
    # 3. Chạy vòng lặp Cast3M
    final_results = []
    for i, X in enumerate(parameter_sets):
        run_number = i + 1
        # Truyền bộ thông số X vào hàm run_cast3m
        res = run_cast3m(X, run_number)
        final_results.append(res)

    # 3. Ghi gộp Input và Output ra MỘT file CSV duy nhất
    combined_csv_file = os.path.join(working_dir, "combined_samples.csv")
    with open(combined_csv_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        
        # Viết dòng tiêu đề (Header): Gộp tên cột Input và Output
        headers = [
            "KINT", "AK", 
            "T_00_Max", "T_10_Max", "T_20_Max", "T_30_Max", "T_40_Max", "T_50_Max", "T_120_Max",
            "Pg_10_Max", "Pg_20_Max", "Pg_30_Max", "Pg_40_Max", "Pg_50_Max"
        ]
        writer.writerow(headers)
                
    print(f"-> Đã lưu Combined Samples tại: {combined_csv_file}")
    print("\n[VÒNG LẶP ĐÃ CHẠY XONG] Bạn có thể kiểm tra kết quả!")