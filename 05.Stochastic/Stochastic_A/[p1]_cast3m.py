import openturns as ot
import os
import subprocess
import glob

# =========================================================
# ESTABLISHING PROJECT PATHWAYS
# =========================================================
working_dir = r"D:\cast3m-m2internship\05.Stochastic\Stochastic_A"
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

    template_file = os.path.join(working_dir, "20260521-kalifa.dgibi.in") 
    run_file = os.path.join(working_dir, "run_temp.dgibi")
    
    csv_temp = os.path.join(csv_dir, f"temp_results_no_{run_number}.csv")
    csv_pg = os.path.join(csv_dir, f"pg_results_no_{run_number}.csv")
    
    for f_path in [csv_temp, csv_pg]:
        if os.path.exists(f_path): os.remove(f_path)
    
    with open(template_file, 'r', encoding='utf-8') as file:
        template = file.read()
        
    # Thay thế @KINT@ bằng giá trị k0 (dùng định dạng khoa học E để Cast3M dễ đọc)
    # LƯU Ý: Đảm bảo trong file dgibi.in của bạn có dùng biến @KINT@
    content = template.replace('@KINT@', f"{k0_val:.4E}")\
                      .replace('@CSV_TEMP@', csv_temp).replace('@CSV_PG@', csv_pg)

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
                if not line or line.startswith('*') or 'Time' in line or 'T_' in line or 'P_' in line:
                    continue
                
                parts = line.split(';')
                if len(parts) > col_index:
                    val_str = parts[col_index].strip().upper().replace('D', 'E')
                    if val_str:
                        try:
                            val = float(val_str)
                            if val > max_val:
                                max_val = val
                        except ValueError:
                            pass 
        except Exception as e:
            print(f"[NUMBER READING ERROR] File: {csv_path} | Error: {e}")
            
        return max_val

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
        
    for d in [start_in_dir, working_dir]:
        for ext in ['*.trace', '*.ps', '*.err']:
            for f in glob.glob(os.path.join(d, ext)):
                try: os.remove(f)
                except: pass
                    
    return [T_00_max, T_10_max, T_20_max, T_30_max, T_40_max, T_50_max, T_120_max, 
            Pg_10_max, Pg_20_max, Pg_30_max, Pg_40_max, Pg_50_max]

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
    
    input_sample.exportToCSVFile(input_csv_file, ";")
    print(f"-> Saved Input Samples to: {input_csv_file}")
    
    final_results = []
    for i in range(N_loops):
        res = run_cast3m(input_sample[i], i + 1)
        final_results.append(res)

    output_sample = ot.Sample(final_results)
    output_sample.setDescription([
        "T_00_Max", "T_10_Max", "T_20_Max", "T_30_Max", "T_40_Max", "T_50_Max", "T_120_Max",
        "Pg_10_Max", "Pg_20_Max", "Pg_30_Max", "Pg_40_Max", "Pg_50_Max"
    ])
    output_sample.exportToCSVFile(output_csv_file, ";")
    print(f"-> Saved Output Samples to: {output_csv_file}")
   
    print("\n[SCRIPT 1 FINISHED RUNNING] You can now close this file and run Script 2!")