import subprocess
import os

def run_cast3m_external_file(file_path, file_name):
    # 1. Cast3M System Folders
    castem_bat = r"C:\Cast3M\PCW_24\bin\castem24.bat"
    start_in_dir = r"C:\Cast3M\PCW_24\sources"
    
    # 2. Create an ABSOLUTE PATH to your dgibi file
    # For example, it will create: "D:\My_Projects\beam_thm.dgibi"
    relative_path = os.path.join(file_path, file_name)
    absolute_path = os.path.abspath(relative_path)

    # Checking
    if not os.path.exists(start_in_dir):
        print(f"Error: Not found the Cast3M working directory at{start_in_dir}")
        return
    if not os.path.exists(absolute_path):
        print(f"Error: Not found file at {absolute_path}")
        return

    # 3. Run command: Wrap the absolute path in double quotes r'"{...}"'
    # to prevent your directory name from containing spaces
    command = f'"{castem_bat}" "{absolute_path}" --pause'
    
    print(f"[THIẾT LẬP]")
    print(f"  - Start in (CWD) : {start_in_dir}")
    print(f"  - File run : {absolute_path}")
    print("-" * 50)

    try:
        # 4. Thực thi lệnh
        subprocess.run(
            command,
            cwd=start_in_dir,  # Force Cast3M to run in the background in the sources folder
            shell=True,
            check=True
        )
        print("-" * 50)
        print("Cast3M simulation completed successfully!")
        
    except subprocess.CalledProcessError as e:
        print("-" * 50)
        print(f"Cast3M encountered an error (Crash). Error code: {e.returncode}")

# ==========================================
# RUNNING
# ==========================================
if __name__ == "__main__":
    # Assuming your file is located on drive D, completely separate from Cast3M
    file_path = r"D:\PhD_Grenoble\Persalys_Project"
    file_name = "transient-sample.dgibi"
    
    run_cast3m_external_file(file_path, file_name)