import openturns as ot
import os
import subprocess
import glob
import matplotlib.pyplot as plt
import numpy as np

# =========================================================
# ESTABLISHING PROJECT PATHWAYS
# =========================================================
working_dir = r"D:\cast3m-m2internship\04.OpenTURNS\Test_02"
csv_dir = r"D:\cast3m-m2internship\04.OpenTURNS\Test_02\CSV"

os.makedirs(csv_dir, exist_ok=True)

# =========================================================
# 1. WRAPPER FUNCTION TO OPENTURNS CALL CAST3M
# =========================================================
def run_cast3m(X, run_number):
    cem, aggr, wc, sc = X
    
    castem_bat = r"C:\Cast3M\PCW_24\bin\castem24.bat"
    start_in_dir = r"C:\Cast3M\PCW_24\sources"

    # make sure the dgibi has fin; at the end and turn off trac and dess to avoid hanging.    
    template_file = os.path.join(working_dir, "20260521-kalifa.dgibi.in") 
    run_file = os.path.join(working_dir, "run_temp.dgibi")
    
    csv_temp = os.path.join(csv_dir, f"temp_results_no_{run_number}.csv")
    csv_pg = os.path.join(csv_dir, f"pg_results_no_{run_number}.csv")
    
    for f_path in [csv_temp, csv_pg]:
        if os.path.exists(f_path):
            os.remove(f_path)
    
    with open(template_file, 'r', encoding='utf-8') as file:
        template = file.read()
        
    content = template.replace('@CEM@', str(cem)).replace('@AGG@', str(aggr))\
                      .replace('@WC@', str(wc)).replace('@SC@', str(sc))\
                      .replace('@CSV_TEMP@', csv_temp).replace('@CSV_PG@', csv_pg)

    with open(run_file, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"\n[Running loop no {run_number}] Loading: CEM={cem:.1f}, AGG={aggr:.1f}, WC={wc:.3f}, SC={sc:.3f}")
    
    # ====================================================================
    # CALL CAST3M BY "COPY-PASTE" THE FILE INTO STDIN (Exactly like the < command in CMD)
    # cd /d "C:\Cast3M\PCW_24\sources" 
    # call "C:\Cast3M\PCW_24\bin\castem24.bat" < "D:\cast3m-m2internship\04.OpenTURNS\Test_02\run_temp.dgibi" --> THIS IS THE EXACT COMMAND WE ARE SIMULATING IN PYTHON BELO (COPY AND PASTE THE CONTENT OF THE .dgibi INTO CASTEM'S STDIN)
    # call "C:\Cast3M\PCW_24\bin\castem24.bat" "D:\cast3m-m2internship\04.OpenTURNS\Test_02\run_temp.dgibi" --> THIS IS NOT WORKING WHEN RUNNING DIRECTLY IN PYTHON, CASTEM CANNOT RUN THE CUSTOM VERSION.
    # ====================================================================
    try:
        # Open the newly created .dgibi file to read it.
        with open(run_file, 'r', encoding='utf-8') as f_in:
            subprocess.run(
                [castem_bat],          
                cwd=start_in_dir,      # Start in: sources
                stdin=f_in,            # <-- Simulate the "copy-paste" by feeding the .dgibi content into Cast3M's stdin. (< run_temp.dgibi)
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

    # Extract Max of T_00mm (located in parts[1])
    T_00_max = read_max_from_column(csv_temp, col_index=1)
    
    # Extract Max of Pg_10mm (located in parts[3])
    Pg_10_max = read_max_from_column(csv_pg, col_index=3)
        
    # Clean up system debris (Optional)
    for d in [start_in_dir, working_dir]:
        for ext in ['*.trace', '*.ps', '*.err']:
            for f in glob.glob(os.path.join(d, ext)):
                try: os.remove(f)
                except: pass
                    
    return [T_00_max, Pg_10_max]

# =========================================================
# 2. ESTABLISHING OPENTURNS AND RUNNING LOOPS
# =========================================================
if __name__ == "__main__":
    print("Initialize the OpenTURNS environment...")
    
    # 1. Define the distribution for the four input variables Kalifa.
    # (Established around reference values: cem=377, aggr=1920, wc=0.34, sc=0.1)
    dist_CEM  = ot.Normal(377.0, 15.0)     # Mean=377, Std=15
    dist_AGGR = ot.Normal(1920.0, 50.0)    # Mean=1920, Std=50
    dist_WC   = ot.Uniform(0.30, 0.38)     # Mean +/- ~10%
    dist_SC   = ot.Uniform(0.08, 0.12)     # Mean +/- ~20%
    
    my_distribution = ot.JointDistribution([dist_CEM, dist_AGGR, dist_WC, dist_SC])
    
    # The function has 4 inputs and 2 outputs.
    my_model = ot.PythonFunction(4, 2, run_cast3m)
    
    # Random sampling with Latin Hypercube Sampling (LHS) to create input sets for Cast3M.
    N_loops = 30
    experiment = ot.LHSExperiment(my_distribution, N_loops)
    input_sample = experiment.generate()
    
    print(f"{N_loops} parameter set has been created. Start running Cast3M automatically.")
    
    final_results = []
    for i in range(N_loops):
        print(f"\n--- Running loop number: {i+1}/{N_loops} ---")
        res = run_cast3m(input_sample[i], i + 1)
        final_results.append(res)
        
    print("\nThe entire loop is complete!")

# =========================================================
# 3. DISPLAY SUMMARY OF INPUT AND OUTPUT
# =========================================================
    print("\n" + "="*95)
    print(f"|| {'INPUT (CEM, AGGR, WC, SC)':<50} || {'OUTPUT (Tmax, Pg_max)':<35} ||")
    print("="*95)
    
    for i in range(N_loops):
        cem, aggr, wc, sc = input_sample[i]
        t_max, pg_max = final_results[i]
        
        input_str = f"CEM={cem:.1f}, AGGR={aggr:.1f}, WC={wc:.3f}, SC={sc:.3f}"
        output_str = f"Tmax={t_max:.2f}, Pg_max={pg_max:.2f}"
        
        print(f"|| {input_str:<50} || {output_str:<35} ||")
        
    print("="*95)

# =========================================================
# 4. POST-PROCESSING ANALYSIS WITH OPENTURNS
# =========================================================
    print("\nStart Post-processing Analysis...")
    
    input_ot = ot.Sample(input_sample)
    input_ot.setDescription(["CEM", "AGGR", "WC", "SC"])
    
    output_ot = ot.Sample(final_results)
    output_ot.setDescription(["T_00mm_Max", "Pg_10mm_Max"])
    
    # NOTE: By default, the analysis below will focus on the Pg_max gas pressure analysis.
    # (Because in the Kalifa model, spalling is often associated with peak pore pressure.)
    target_sample = output_ot[:, 1] # Column 1 is Pg_max. If you want Tmax, change it to output_ot[:, 0]
    target_name = "Pg_10mm_Max"

    # ---------------------------------------------------------
    # 4.1. SCATTER PLOTS & CORRELATION
    # ---------------------------------------------------------
    print(" -> Drawing Scatter Plots...")
    in_array = np.array(input_ot)
    out_array = np.array(target_sample).flatten()
    
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    fig.suptitle(f'Scatter Plots: Inputs vs {target_name}', fontsize=16)
    
    for i in range(4):
        x_data = in_array[:, i]
        corr = np.corrcoef(x_data, out_array)[0, 1] 
        
        axes[i].scatter(x_data, out_array, alpha=0.7, color='b', edgecolors='k')
        axes[i].set_xlabel(input_ot.getDescription()[i], fontsize=12)
        axes[i].set_ylabel(target_name, fontsize=12)
        axes[i].set_title(f'Correlation: {corr:.2f}')
        axes[i].grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(os.path.join(working_dir, f"Scatter_Plots_{target_name}.png"), dpi=300)
    #plt.show()

    # ---------------------------------------------------------
    # 4.2. METAMODEL & SOBOL' INDICES
    # ---------------------------------------------------------
    print(" -> Drawing Metamodel (PCE)...")
    try:
        algo = ot.FunctionalChaosAlgorithm(input_ot, target_sample, my_distribution)
        algo.run()
        result_pce = algo.getResult()
        metamodel = result_pce.getMetaModel()
        
        print(" -> Calculating Sobol' Indices...")
        sobol = ot.FunctionalChaosSobolIndices(result_pce)
        
        sobol_1st = [sobol.getSobolIndex(i) * 100 for i in range(4)]       
        sobol_tot = [sobol.getSobolTotalIndex(i) * 100 for i in range(4)]  
        
        print(f"\n--- SOBOL'S INDEX FOR {target_name} (%) ---")
        for i, name in enumerate(input_ot.getDescription()):
            print(f"{name:<5}: 1st Order = {sobol_1st[i]:5.2f}% | Total = {sobol_tot[i]:5.2f}%")
            
        fig, ax = plt.subplots(figsize=(8, 5))
        bar_width = 0.35
        index = np.arange(4)
        
        ax.bar(index, sobol_1st, bar_width, label='1st Order', color='#1f77b4')
        ax.bar(index + bar_width, sobol_tot, bar_width, label='Total Order', color='#ff7f0e')
        
        ax.set_xlabel('Input Variables', fontsize=12)
        ax.set_ylabel("Sobol' Indices (%)", fontsize=12)
        ax.set_title(f"Sobol' Sensitivity Analysis for {target_name}", fontsize=14)
        ax.set_xticks(index + bar_width / 2)
        ax.set_xticklabels(input_ot.getDescription())
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.savefig(os.path.join(working_dir, f"Sobol_Sensitivity_{target_name}.png"), dpi=300)
        #plt.show()
        
        # ---------------------------------------------------------
        # SECOND-ORDER SOBOL' INDICES 
        # ---------------------------------------------------------
        print("\n -> Calculating Second-Order Sobol' Indices (Cross-Interactions)...")
        saltelli_size = 10000 
        sie = ot.SobolIndicesExperiment(my_distribution, saltelli_size, True)
        inputDesign = sie.generate()
        outputDesign = metamodel(inputDesign)
        saltelli = ot.SaltelliSensitivityAlgorithm(inputDesign, outputDesign, saltelli_size)
        s2_matrix = saltelli.getSecondOrderIndices()
        var_names = input_ot.getDescription()
        num_vars = len(var_names)
        
        print(f"\n--- SECOND-ORDER SOBOL' MATRIX FOR {target_name} (%) ---")
        for i in range(num_vars):
            for j in range(i + 1, num_vars):
                val = s2_matrix[i, j] * 100
                if val > 0.5:
                    print(f" Cross-Interaction [{var_names[i]} x {var_names[j]}]: {val:.2f}%")
        
        # HEATMAP
        s2_np = np.zeros((num_vars, num_vars))
        for i in range(num_vars):
            for j in range(num_vars):
                if i != j:
                    s2_np[i, j] = s2_matrix[i, j] * 100
                    
        fig, ax = plt.subplots(figsize=(6, 5))
        cax = ax.imshow(s2_np, cmap='Oranges', vmin=0)
        
        for i in range(num_vars):
            for j in range(num_vars):
                if i != j:
                    ax.text(j, i, f"{s2_np[i, j]:.1f}%", ha="center", va="center", color="black", fontsize=10)
                else:
                    ax.text(j, i, "-", ha="center", va="center", color="gray", fontsize=10)

        ax.set_xticks(np.arange(num_vars))
        ax.set_yticks(np.arange(num_vars))
        ax.set_xticklabels(var_names)
        ax.set_yticklabels(var_names)
        ax.set_title(f"Sobol' Second-Order Indices (%) - {target_name}", fontsize=14)
        
        fig.colorbar(cax, ax=ax, label='Contribution Rate (%)')
        plt.tight_layout()
        plt.savefig(os.path.join(working_dir, f"Sobol_SecondOrder_Heatmap_{target_name}.png"), dpi=300)
        #plt.show()

    # ---------------------------------------------------------
    # 4.3. RELIABILITY ANALYSIS
    # ---------------------------------------------------------
        # NOTE: Set Threshold corresponding to Pg_max (Pressure that can cause cracking). Assume it is 2.0 MPa.
        PG_THRESHOLD = 2.0 
        print(f"\n -> Running Reliability Analysis (Threshold {target_name} > {PG_THRESHOLD})...")
        
        X_rnd = ot.RandomVector(my_distribution)
        Y_metamodel = ot.CompositeRandomVector(metamodel, X_rnd)
        
        event = ot.ThresholdEvent(Y_metamodel, ot.Greater(), PG_THRESHOLD)
        
        mc_algo = ot.ProbabilitySimulationAlgorithm(event, ot.MonteCarloExperiment())
        mc_algo.setMaximumOuterSampling(100000)
        mc_algo.run()
        
        pf = mc_algo.getResult().getProbabilityEstimate()
        print(f"=========================================================")
        print(f" RELIABILITY ANALYSIS RESULTS")
        print(f" Probability that {target_name} exceeds {PG_THRESHOLD} is: {pf * 100:.3f} %")
        print(f"=========================================================")

    except Exception as e:
        print(f"\n[NOTE] Cannot run PCE & Sobol. Error: {e}")