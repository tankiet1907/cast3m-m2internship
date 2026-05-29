import subprocess
import os
import glob

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
    command = [castem_bat, absolute_path]
    
    print(f"[INFO] Running Cast3M with the following details:")
    print(f"  - Start in (CWD) : {start_in_dir}")
    print(f"  - File run : {absolute_path}")
    print("-" * 50)

    try:
    # 4. Execute the order
        subprocess.run(
            command,
            cwd=start_in_dir,  # Force Cast3M to run in the background in the sources folder
            shell=False, 
            check=True
        )
        print("-" * 50)
        print("Cast3M simulation completed successfully!")
        
    except subprocess.CalledProcessError as e:
        print("-" * 50)
        print(f"Cast3M encountered an error (Crash). Error code: {e.returncode}")
    finally:
        # ---------------------------------------------------------
        # 5. CLEAN UP JUNK FILES AFTER RUNNING (Clean up whether successful or crashed)
        # ---------------------------------------------------------
        print("Cleaning up junk files (.trace, .ps, .err)...")
        
        # Create a list of file extensions to delete (You can add more extensions if needed)
        directories_to_clean = [file_path]
        extensions_to_delete = ['*.trace', '*.ps', '*.err']
        
        for directory in directories_to_clean:
            for ext in extensions_to_delete:
                # Find all files with the corresponding extension in the start_in_dir (sources) directory
                search_pattern = os.path.join(directory, ext)
                files_to_remove = glob.glob(search_pattern)
            
                # Delete each found file
                for f in files_to_remove:
                    try:
                        os.remove(f)
                        print(f"Deleted: {f}") # Uncomment this line if you want to see which files are being deleted
                    except OSError as e:
                        print(f"Error when deleting {f}: {e}")
        print("Cleaning is complete!")
# ==========================================
# RUNNING
# ==========================================
if __name__ == "__main__":
    # Assuming your file is located on drive D, completely separate from Cast3M
    file_path = r"D:\cast3m-m2internship\04.OpenTURNS\Test_01"
    file_name = "transient-sample.dgibi"
    
    run_cast3m_external_file(file_path, file_name)