import os
import subprocess

# =========================================================
# THIẾT LẬP ĐƯỜNG DẪN DỰ ÁN
# =========================================================
working_dir = r"D:\cast3m-m2internship\05.Stochastic\Stochastic_C3"
csv_dir = os.path.join(working_dir, "CSV")
os.makedirs(csv_dir, exist_ok=True)

# =========================================================
# KHỞI CHẠY CAST3M
# =========================================================
def run_cast3m_quadrature():
    castem_bat = r"C:\Cast3M\PCW_24\bin\castem24.bat"
    start_in_dir = r"C:\Cast3M\PCW_24\sources"

    template_file = os.path.join(working_dir, "THM_pc (quadrature).dgibi.in") 
    run_file = os.path.join(working_dir, "run_temp.dgibi")
    csv_u = os.path.join(csv_dir, "Quadrature_Results.csv")
    
    if os.path.exists(csv_u): 
        os.remove(csv_u)
    
    with open(template_file, 'r', encoding='utf-8') as file:
        template = file.read()
        
    # Cast3M sẽ tự xuất file CSV đến đúng vị trí này
    content = template.replace('@CSV_U@', csv_u)
    
    with open(run_file, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print("\n[Đang chạy Cast3M Quadrature Solver...] Vui lòng đợi.")
    
    try:
        with open(run_file, 'r', encoding='utf-8') as f_in:
            subprocess.run([castem_bat], cwd=start_in_dir, stdin=f_in, shell=True)
        print(f"\n[HOÀN THÀNH] Dữ liệu Quadrature đã được xuất ra tại: {csv_u}")
    except Exception as e:
        print(f"System Error: {e}")

if __name__ == "__main__":
    run_cast3m_quadrature()