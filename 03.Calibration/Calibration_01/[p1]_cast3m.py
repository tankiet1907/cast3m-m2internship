import os
import subprocess
import glob
import itertools
import csv

# CALIBRATION OF THE SURFACE EXCHANGE COEFFICIENT

# =========================================================
# ESTABLISHING PROJECT PATHWAYS
# =========================================================
working_dir = r"D:\cast3m-m2internship\03.Calibration\Calibration_01"
csv_dir = os.path.join(working_dir, "CSV")
os.makedirs(csv_dir, exist_ok=True)


# =========================================================
# HELPER: CHECK IF A RESULT CSV IS ALREADY VALID (for resume)
# =========================================================
def _csv_has_valid_data(csv_path):
    """Return True if csv_path exists and contains at least one numeric data row.
    Uses the same header-filtering logic as read_max_from_column so that a file
    with only headers / blank lines is NOT considered 'done'."""
    if not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0:
        return False
    try:
        with open(csv_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('*') or 'Time' in line or 'T_' in line or 'P_' in line:
                    continue
                for part in line.split(';'):
                    s = part.strip().upper().replace('D', 'E')
                    try:
                        float(s)
                        return True  # found at least one real numeric value
                    except ValueError:
                        continue
    except Exception:
        return False
    return False


# =========================================================
# 1. WRAPPER FUNCTION TO CALL CAST3M
# =========================================================
def run_cast3m(X, run_number):
    epsilon, hhot = X

    castem_bat = r"C:\Cast3M\PCW_24\bin\castem24.bat"
    start_in_dir = r"C:\Cast3M\PCW_24\sources"

    # make sure the dgibi has fin; at the end and turn off trac and dess to avoid hanging.
    template_file = os.path.join(working_dir, "20260521-kalifa.dgibi.in")
    run_file = os.path.join(working_dir, "run_temp.dgibi")

    csv_temp = os.path.join(csv_dir, f"temp_results_no_{run_number}_epsilon_{epsilon}_h-hot_{hhot}.csv")
    csv_pg = os.path.join(csv_dir, f"pg_results_no_{run_number}_epsilon_{epsilon}_h-hot_{hhot}.csv")

    # ====================================================================
    # RESUME LOGIC
    # If BOTH result CSVs already exist and contain valid data, skip the
    # (expensive) Cast3M run. We still re-read the existing CSVs below so
    # that final_results / combined_samples.csv stay complete and correct.
    # NOTE: this relies on epsilon_values / h_values (and therefore the
    # run_number <-> parameter mapping) being unchanged between runs.
    # ====================================================================
    already_done = _csv_has_valid_data(csv_temp) and _csv_has_valid_data(csv_pg)

    if already_done:
        print(f"\n[SKIP loop no {run_number}] Already computed: "
              f"Epsilon={epsilon:.2e}, H-hot={hhot:.2e} -> reusing existing CSV.")
    else:
        # Remove any partial / corrupted files left over from a crashed run.
        for f_path in [csv_temp, csv_pg]:
            if os.path.exists(f_path):
                os.remove(f_path)

        with open(template_file, 'r', encoding='utf-8') as file:
            template = file.read()

        content = template.replace('@EPSILON@', str(epsilon))\
                          .replace('@HHOT@', str(hhot))\
                          .replace('@CSV_TEMP@', csv_temp)\
                          .replace('@CSV_PG@', csv_pg)

        with open(run_file, 'w', encoding='utf-8') as file:
            file.write(content)

        print(f"\n[Running loop no {run_number}] Loading: "
              f"Epsilon={epsilon:.2e}, H-hot={hhot:.2e}")

        # ====================================================================
        # CALL CAST3M BY "COPY-PASTE" THE FILE INTO STDIN (Exactly like the < command in CMD)
        # cd /d "C:\Cast3M\PCW_24\sources"
        # call "C:\Cast3M\PCW_24\bin\castem24.bat" < "...\run_temp.dgibi"
        # ====================================================================
        try:
            with open(run_file, 'r', encoding='utf-8') as f_in:
                subprocess.run(
                    [castem_bat],
                    cwd=start_in_dir,
                    stdin=f_in,  # <-- Simulate the "copy-paste" by feeding the .dgibi content into Cast3M's stdin.
                    shell=True
                )
        except Exception as e:
            print(f"System Error: {e}")


# =========================================================
# 2. ESTABLISHING VALUES AND RUNNING LOOPS + SAVING DATA
# =========================================================
if __name__ == "__main__":
    print("Khởi tạo danh sách các tổ hợp thông số epsilon và h...")

    # 1. Declare the values you want to test (You can add/remove them as you wish)
    epsilon_values = [0.65, 0.68, 0.72]
    h_values = [9.0, 10.0, 11.0]

    # 2. Create all possible combinations.
    parameter_sets = list(itertools.product(epsilon_values, h_values))
    N_loops = len(parameter_sets)

    print(f"{N_loops} parameter sets have been created. Cast3M will resume / run automatically.")

    # 3. Run Cast3M loop (skips already-completed runs automatically)
    final_results = []
    for i, X in enumerate(parameter_sets):
        run_number = i + 1
        # Pass the parameter set X to the run_cast3m function.
        res = run_cast3m(X, run_number)
        final_results.append(res)

    print("\n[LOOP COMPLETED] You can check the results!")