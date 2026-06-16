import os
import glob
import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# =========================================================
# ESTABLISHING PROJECT PATHWAYS
# =========================================================
working_dir = r"D:\cast3m-m2internship\03.Calibration\Calibration_02"
csv_dir = os.path.join(working_dir, "CSV")
output_dir = os.path.join(working_dir, "Plots")
if not os.path.exists(csv_dir):
    os.makedirs(csv_dir)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


# 1. Color definition according to Cast3M standard
colors = {
    '00': 'blue',
    '10': 'red',
    '20': 'gold',
    '30': 'deeppink',
    '40': 'green',
    '50': 'cyan',
    '120': 'black'
}

# =========================================================
# 2. FUNCTION FOR AUTOMATIC FILE READING AND GRAPH DRAWING (AXIS UPDATE)
# =========================================================
def plot_and_save(file_list, plot_type):
    # =========================================================
    # 1. DETERMINE THE REQUIRED DRAWING DEPTH BASED ON THE TYPE OF GRAPH
    # =========================================================
    if plot_type == "Temp":
        # Temperature: From surface (00) to 50mm
        active_depths = ['00', '10', '20', '30', '40', '50']
    elif plot_type == "Pg":
        # Air pressure: Ignore 00mm (only draw from 10mm to 50mm)
        active_depths = ['10', '20', '30', '40', '50']
    else:
        # Default for other graph types (such as Dch, Sw...)
        active_depths = ['00', '10', '20', '30', '40', '50']
        
    for file_path in file_list:
        filename = os.path.basename(file_path)
        
        # Extract epsilon and h-hot from filenames using Regex.
        match = re.search(r'epsilon_([^_]+)_h-hot_([^_]+)_lamda_([^_]+)_cp([^.]+)\.csv', filename)
        
        if match:
            epsilon_val = match.group(1)
            hhot_val    = match.group(2)
            lamda_val   = match.group(3)
            cp_val      = match.group(4)
            
            # Update the Title and File Name với đầy đủ 4 thông số
            title = f"{plot_type} | Eps: {epsilon_val} | h_hot: {hhot_val} | Lamda: {lamda_val} | Cp: {cp_val}"
            save_name = f"{plot_type}_epsilon_{epsilon_val}_h-hot_{hhot_val}_lamda_{lamda_val}_cp{cp_val}.png"
        else:
            title = f"{plot_type} - {filename}"
            save_name = f"{filename}.png"

        try:
            df = pd.read_csv(file_path, sep=';')
            plt.figure(figsize=(10, 8))
            x_col = df.columns[0]
            
            # SMART GRAPHING LOOP
            for y_col in df.columns[1:]:
                # FIND THE DEPTH IN COLUMN NAMES
                # Find the numbers that appear in column names
                match_depth = re.search(r'(\d+)', y_col)
                if match_depth:
                    depth_key = match_depth.group(1)
                    
                    # ONLY DRAW IF THE DEPTH IS WITHIN THE ALLOWED LIST
                    if depth_key in active_depths:
                        plot_color = colors.get(depth_key, 'gray')
                        plt.plot(df[x_col], df[y_col], color=plot_color, 
                                 label=f'Sim {depth_key}mm', linewidth=2)
            
            # ---------------------------------------------------------
            # SET UP A FIXED COORDINATE AXIS AS REQUIRED
            # ---------------------------------------------------------
            # Horizontal axis (Time): From 0 to 240, in increments of 20
            plt.xlim(0, 240)
            plt.xticks(np.arange(0, 241, 20), rotation=0, fontsize=10) 
            plt.xlabel("Time (min)", fontsize=12)

            # Y-axis (Temperature / Pressure)
            if plot_type == "Temp":
                plt.ylabel("Temperature (°C)", fontsize=12)
                plt.ylim(0, 500)
                plt.yticks(np.arange(0, 501, 50))
                plt.legend(loc="upper left", fontsize=10)
                
            elif plot_type == "Pg":
                plt.ylabel("Gas Pressure (MPa)", fontsize=12)
                plt.ylim(0, 4.0)
                plt.yticks(np.arange(0, 4.1, 0.5))
                plt.legend(loc="upper right", fontsize=10)
                
            # ---------------------------------------------------------
            
            plt.title(title, fontsize=14, fontweight='bold')
            plt.grid(True, linestyle='--', alpha=0.6)
            
            save_path = os.path.join(output_dir, save_name)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            plt.close() 
            
            print(f"-> Image saved: {save_name}")
            
        except Exception as e:
            print(f"-> File reading error {filename}: {e}")

# =========================================================
# 3. THỰC THI CHƯƠNG TRÌNH
# =========================================================
if __name__ == "__main__":
    temp_files = glob.glob(os.path.join(csv_dir, "temp_results_no_*.csv"))
    pg_files   = glob.glob(os.path.join(csv_dir, "pg_results_no_*.csv"))

    print(f"Found {len(temp_files)} Temp, {len(pg_files)} Pg.\n")

    print("--- START DRAWING THE TEMPERATURE GRAPH ---")
    plot_and_save(temp_files, "Temp")

    print("\n--- START DRAWING THE PRESSURE GRAPH ---")
    plot_and_save(pg_files, "Pg")
    
    print(f"\n[COMPLETE] Please check the '{output_dir}' folder to see the result!")