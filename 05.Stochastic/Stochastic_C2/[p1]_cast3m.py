import openturns as ot
import os
import csv
import subprocess

# =========================================================
# ESTABLISHING PROJECT PATHWAYS
# =========================================================
working_dir = r"D:\cast3m-m2internship\05.Stochastic\Stochastic_C2"
csv_dir = os.path.join(working_dir, "CSV")
os.makedirs(csv_dir, exist_ok=True)

output_csv_file = os.path.join(working_dir, "OpenTURNS_Outputs_Y.csv")
run_log_file    = os.path.join(working_dir, "run_log.csv")   # run, NBURN, strain (traceability)

# =========================================================
# CAMPAIGN CONTROL
#   N_loops   : total number of realizations wanted (1..N_loops)
#   START_RUN : first run to (re)compute this session.
#               Runs before START_RUN are assumed already done on disk
#               (their u_results_no_*.csv files are reused, not recomputed).
# =========================================================
N_loops   = 30
START_RUN = 1          # <-- resume here; 1 and 2 already ran

# =========================================================
# NBURN SCHEME  (CHEAP + DISTINCT + REPRODUCIBLE)
#   Each ALEA call advances the PRNG by a fixed chunk, so two runs only need
#   a DIFFERENT (and SMALL) burn count to read disjoint -> independent fields.
#   NBURN must stay small: each burn IS one real ALEA call (not free), so a
#   huge NBURN (e.g. 1e6) makes Cast3M crawl for minutes/hours. Keep it small.
#
#   nburn(run) = CAMPAIGN_OFFSET * N_loops + run_number
#     -> within a campaign: runs get distinct, non-overlapping stream segments
#     -> max burn = (CAMPAIGN_OFFSET + 1) * N_loops   (e.g. 30 -> instant)
#   To launch a NEW independent batch later, bump CAMPAIGN_OFFSET by 1.
# =========================================================
CAMPAIGN_OFFSET = 0

def nburn_for(run_number):
    return (CAMPAIGN_OFFSET * N_loops) + run_number


# =========================================================
# 1. RUN CAST3M FOR ONE REALIZATION (returns nburn, strain)
# =========================================================
def run_cast3m(run_number):
    castem_bat   = r"C:\Cast3M\PCW_24\bin\castem24.bat"
    start_in_dir = r"C:\Cast3M\PCW_24\sources"

    template_file = os.path.join(working_dir, "THM_pc_alea_NBURN.dgibi.in")
    run_file      = os.path.join(working_dir, "run_temp.dgibi")

    csv_u = os.path.join(csv_dir, f"u_results_no_{run_number}.csv")
    if os.path.exists(csv_u):
        os.remove(csv_u)

    nburn = nburn_for(run_number)

    with open(template_file, 'r', encoding='utf-8') as f:
        template = f.read()
    content = template.replace('@NBURN@', str(nburn))
    content = content.replace('@CSV_U@', csv_u)

    with open(run_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n[Run {run_number}]  NBURN = {nburn}")

    try:
        with open(run_file, 'r', encoding='utf-8') as f_in:
            subprocess.run([castem_bat], cwd=start_in_dir, stdin=f_in, shell=True)
    except Exception as e:
        print(f"System Error: {e}")

    return nburn, read_qoi(run_number)


# =========================================================
# 2. READ THE QoI FROM AN EXISTING per-run CSV (no Cast3M call)
# =========================================================
def read_qoi(run_number):
    csv_u = os.path.join(csv_dir, f"u_results_no_{run_number}.csv")
    if not os.path.exists(csv_u):
        return float("nan")
    with open(csv_u, 'r', encoding='utf-8') as f:
        lines = [ln for ln in f.read().splitlines() if ln.strip()]
    if len(lines) > 1:
        last_row = lines[-1].split(';')
        try:
            return float(last_row[1])
        except (IndexError, ValueError):
            print(f"  ! Could not parse strain from run {run_number}: {last_row}")
    return float("nan")


# =========================================================
# 3. RUN THE REMAINING REALIZATIONS, THEN ASSEMBLE ALL RESULTS
# =========================================================
if __name__ == "__main__":
    print(f"Resuming campaign: computing runs {START_RUN}..{N_loops} "
          f"(runs 1..{START_RUN - 1} reused from disk).")

    # --- append new runs to the log (create with header if it does not exist) ---
    log_exists = os.path.exists(run_log_file)
    with open(run_log_file, 'a', newline='', encoding='utf-8') as f:
        w = csv.writer(f, delimiter=';')
        if not log_exists:
            w.writerow(['run', 'NBURN', 'Shrinkage_Strain'])

        for i in range(START_RUN, N_loops + 1):
            nburn, y_val = run_cast3m(i)
            w.writerow([i, nburn, y_val])
            print(f"  -> strain = {y_val}")

    # --- assemble the FULL output (1..N_loops) by reading every per-run CSV ---
    final_results = []
    missing = []
    for i in range(1, N_loops + 1):
        y = read_qoi(i)
        final_results.append([y])
        if y != y:  # NaN check
            missing.append(i)

    if missing:
        print(f"\n! Warning: no valid result for runs {missing} "
              f"(missing/failed CSV). They appear as NaN in the output.")

    output_sample = ot.Sample(final_results)
    output_sample.setDescription(['Shrinkage_Strain'])
    output_sample.exportToCSVFile(output_csv_file, ";")
    print(f"\n-> Full output ({N_loops} runs) saved to: {output_csv_file}")
    print(f"-> Run log appended to: {run_log_file}")
    print("\n[SCRIPT 1 FINISHED] Data ready for PDF/CDF plotting.")