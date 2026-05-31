import openturns as ot
import os
import subprocess
import glob

# =========================================================
# 1. HÀM WRAPPER ĐỂ OPENTURNS GỌI CAST3M
# =========================================================
def run_cast3m(X, run_number):
    # Nhận 4 giá trị từ OpenTURNS
    kd0, cps0, sl, phi = X
    
    # Các thư mục cấu hình
    castem_bat = r"C:\Cast3M\PCW_24\bin\castem24.bat"
    start_in_dir = r"C:\Cast3M\PCW_24\sources"
    working_dir = r"D:\cast3m-m2internship\04.OpenTURNS\Test_01"
    
    template_file = os.path.join(working_dir, "transient-sample.dgibi.in") # Template file with placeholders
    run_file = os.path.join(working_dir, "run_temp.dgibi")
    # 2. Tạo tên file động theo ý bạn: temp_results-no[1].csv
    csv_output = os.path.join(working_dir, f"temp_results_no_{run_number}.csv")
    
    # Xóa file CSV cũ nếu tồn tại
    if os.path.exists(csv_output):
        os.remove(csv_output)
    
    # Đọc template và thay số
    with open(template_file, 'r') as file:
        template = file.read()
    content = template.replace('@KD0@', str(kd0)).replace('@CPS0@', str(cps0))\
                      .replace('@SL@', str(sl)).replace('@PHI@', str(phi))\
                      .replace('@CSV_NAME@', csv_output) # Điền tên file mới vào
    
    with open(run_file, 'w') as file:
        file.write(content)
        
    command = [castem_bat, run_file]
    
    # Gán giá trị phạt (Penalty) mặc định nếu mô phỏng bị crash
    T_max_out = 9999.0 
    T_min_out = -9999.0
    
    print(f"\n Đang nạp thông số vào Cast3M: KD0={kd0:.3f}, CPS0={cps0:.1f}, SL={sl:.3f}, PHI={phi:.3f}")
    try:
        subprocess.run(
            command,
            cwd=start_in_dir,
            shell=False,  # <--- SỬA THÀNH TRUE Ở ĐÂY
        )
    except Exception as e:
        print(f"Lỗi khi gọi hệ thống (Python Error): {e}") 

    # ====================================================================
    # ĐOẠN ĐỌC FILE CSV CHUẨN XÁC THEO INDEX CỦA CAST3M
    # ====================================================================
    if os.path.exists(csv_output):
        try:
            with open(csv_output, 'r') as f:
                lines = f.readlines()
            
            # Quét từng dòng trong file CSV
            for line in lines:
                line = line.strip()
                
                # Bỏ qua dòng trống hoặc dòng tiêu đề (chứa chữ 'Index' hoặc '*')
                if not line or line.startswith('*') or 'Index' in line:
                    continue
                
                parts = line.split(';')
                
                if len(parts) >= 2:
                    try:
                        # Thay thế chữ 'D' thành 'E' (đề phòng Cast3M xuất số mũ Fortran)
                        idx_str = parts[0].strip().upper().replace('D', 'E')
                        val_str = parts[1].strip().upper().replace('D', 'E')
                        
                        # Chuyển đổi sang số thực
                        idx_val = float(idx_str)
                        temp_val = float(val_str)
                        
                        # Nếu Index = 1 -> Đây là Tmax
                        if abs(idx_val - 1.0) < 1e-6:
                            T_max_out = temp_val
                            
                        # Nếu Index = 2 -> Đây là Tmin
                        elif abs(idx_val - 2.0) < 1e-6:
                            T_min_out = temp_val
                            
                    except ValueError:
                        # Bỏ qua nếu có lỗi ép kiểu ở một dòng nào đó không phải dữ liệu
                        continue

        except Exception as read_error:
            print(f"[LỖI ĐỌC SỐ] File: {csv_output} | Chi tiết: {read_error}")
    else:
        # Nếu không có file, đích thực là Cast3M đã phân kỳ (Crash)
        print(f"[CRASH] KHÔNG TÌM THẤY FILE {csv_output} TẠI BỘ THÔNG SỐ NÀY.")
        
        # Dọn dẹp rác hệ thống sau khi chạy xong
    for d in [start_in_dir, working_dir]:
        for ext in ['*.trace', '*.ps', '*.err']:
            for f in glob.glob(os.path.join(d, ext)):
                try: 
                    os.remove(f)
                except: pass
                    
    # TRẢ VỀ CẢ 2 GIÁ TRỊ DƯỚI DẠNG MẢNG (LIST)
    return [T_max_out, T_min_out]

# =========================================================
# 2. THIẾT LẬP OPENTURNS VÀ CHẠY VÒNG LẶP
# =========================================================
if __name__ == "__main__":
    print("Khởi tạo môi trường OpenTURNS...")
    
    # 1. Định nghĩa phân phối cho 4 biến đầu vào (X)
    dist_KD0 = ot.Uniform(1.5, 2.5)
    dist_CPS0 = ot.Normal(948.0, 50.0)
    dist_SL = ot.Uniform(0.1, 0.3)
    dist_PHI = ot.Uniform(0.15, 0.20)
    
    my_distribution = ot.JointDistribution([dist_KD0, dist_CPS0, dist_SL, dist_PHI])
    
    # 2. LƯU Ý QUAN TRỌNG: Hàm bây giờ có 4 Input và 2 Output
    # Cú pháp: ot.PythonFunction(Số_Input, Số_Output, tên_hàm)
    my_model = ot.PythonFunction(4, 2, run_cast3m)
    
    # 3. Tạo mẫu ngẫu nhiên LHS
    N_loops = 30 # Chạy thử 30 vòng lặp
    experiment = ot.LHSExperiment(my_distribution, N_loops)
    input_sample = experiment.generate()
    
    print(f"Đã tạo {N_loops} bộ thông số. Bắt đầu chạy Cast3M tự động...")
    
    final_results = []
    for i in range(N_loops):
        print(f"--- Đang chạy vòng lặp số: {i+1} ---")
        # Truyền thêm i+1 vào để đặt tên file là [1], [2], [3]...
        res = run_cast3m(input_sample[i], i + 1)
        final_results.append(res)
        
    print("Xong toàn bộ!")

    # =========================================================
    # 3. HIỂN THỊ TỔNG HỢP INPUT VÀ OUTPUT
    # =========================================================
    print("\n" + "="*90)
    print(f"|| {'INPUT (KD0, CPS0, SL, PHI)':<50} || {'OUTPUT (Tmax, Tmin)':<30} ||")
    print("="*90)
    
    for i in range(N_loops):
        # Lấy giá trị đầu vào (biến uncertain)
        kd0, cps0, sl, phi = input_sample[i]
        
        # Lấy giá trị đầu ra (đã đọc từ CSV và lưu trong final_results)
        t_max, t_min = final_results[i]
        
        # Định dạng chuỗi để in ra thẳng hàng
        input_str = f"KD0={kd0:.3f}, CPS={cps0:.1f}, SL={sl:.3f}, PHI={phi:.3f}"
        output_str = f"Tmax={t_max:.2f}, Tmin={t_min:.2f}"
        
        print(f"|| {input_str:<50} || {output_str:<30} ||")
        
    print("="*90)

    # =========================================================
    # 4. PHÂN TÍCH HẬU KỲ (POST-PROCESSING) VỚI OPENTURNS
    # =========================================================
    import matplotlib.pyplot as plt
    import numpy as np

    print("\nBắt đầu Phân tích hậu kỳ (Post-processing)...")
    
    # Chuyển đổi dữ liệu Python List sang OpenTURNS Sample
    input_ot = ot.Sample(input_sample)
    input_ot.setDescription(["KD0", "CPS0", "SL", "PHI"])
    
    output_ot = ot.Sample(final_results)
    output_ot.setDescription(["Tmax", "Tmin"])
    
    # Tách riêng Tmax để phân tích
    tmax_sample = output_ot[:, 0]

    # ---------------------------------------------------------
    # 4.1. SCATTER PLOTS & CORRELATION (Phân tích Tương quan)
    # ---------------------------------------------------------
    print(" -> Đang vẽ Scatter Plots...")
    in_array = np.array(input_ot)
    out_array = np.array(tmax_sample).flatten()
    
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    fig.suptitle('Scatter Plots: Inputs vs Tmax', fontsize=16)
    
    for i in range(4):
        x_data = in_array[:, i]
        # Tính hệ số tương quan Pearson
        corr = np.corrcoef(x_data, out_array)[0, 1] 
        
        axes[i].scatter(x_data, out_array, alpha=0.7, color='b', edgecolors='k')
        axes[i].set_xlabel(input_ot.getDescription()[i], fontsize=12)
        axes[i].set_ylabel('Tmax (°C)', fontsize=12)
        axes[i].set_title(f'Correlation: {corr:.2f}')
        axes[i].grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig("Scatter_Plots_Tmax.png", dpi=300)
    plt.show() # Bỏ comment nếu bạn muốn biểu đồ hiện lên ngay lập tức

    # ---------------------------------------------------------
    # 4.2. METAMODEL & SENSITIVITY ANALYSIS (Chỉ số Sobol')
    # ---------------------------------------------------------
    print(" -> Đang xây dựng Metamodel (Polynomial Chaos Expansion)...")
    try:
        # Huấn luyện mô hình PCE bằng dữ liệu đầu vào và Tmax
        algo = ot.FunctionalChaosAlgorithm(input_ot, tmax_sample, my_distribution)
        algo.run()
        result_pce = algo.getResult()
        metamodel = result_pce.getMetaModel()
        
        print(" -> Đang tính toán Chỉ số Sobol'...")
        sobol = ot.FunctionalChaosSobolIndices(result_pce)
        
        sobol_1st = [sobol.getSobolIndex(i) * 100 for i in range(4)]       # Bậc 1 (First-order) in %
        sobol_tot = [sobol.getSobolTotalIndex(i) * 100 for i in range(4)]  # Tổng hợp (Total-order) in %
        
        # In kết quả ra màn hình
        print("\n--- CHỈ SỐ SOBOL' CHO TMAX (%) ---")
        for i, name in enumerate(input_ot.getDescription()):
            print(f"{name:<5}: Bậc 1 = {sobol_1st[i]:5.2f}% | Tổng hợp = {sobol_tot[i]:5.2f}%")
            
        # Vẽ biểu đồ Bar Chart cho Sobol
        fig, ax = plt.subplots(figsize=(8, 5))
        bar_width = 0.35
        index = np.arange(4)
        
        b1 = ax.bar(index, sobol_1st, bar_width, label='Bậc 1 (First Order)', color='#1f77b4')
        b2 = ax.bar(index + bar_width, sobol_tot, bar_width, label='Tổng hợp (Total Order)', color='#ff7f0e')
        
        ax.set_xlabel('Biến đầu vào', fontsize=12)
        ax.set_ylabel("Chỉ số Sobol' (%)", fontsize=12)
        ax.set_title("Phân tích Độ nhạy Sobol' cho Tmax", fontsize=14)
        ax.set_xticks(index + bar_width / 2)
        ax.set_xticklabels(input_ot.getDescription())
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.savefig("Sobol_Sensitivity_Tmax.png", dpi=300)
        plt.show() # Bỏ comment nếu bạn muốn biểu đồ hiện lên ngay lập tức
        # ---------------------------------------------------------
        # 4.2.B. SECOND-ORDER SOBOL' INDICES (Phân tích Tương tác)
        # ---------------------------------------------------------
        print("\n -> Đang tính toán Chỉ số Sobol' Bậc 2 (Tương tác chéo)...")
        
        # Sử dụng Metamodel để sinh 10,000 mẫu siêu tốc cho thuật toán Saltelli
        saltelli_size = 10000 
        sie = ot.SobolIndicesExperiment(my_distribution, saltelli_size, True)
        inputDesign = sie.generate()
        
        # Đánh giá 10,000 mẫu này bằng Metamodel (Thay vì gọi Cast3M)
        outputDesign = metamodel(inputDesign)
        
        # Chạy thuật toán Saltelli
        saltelli = ot.SaltelliSensitivityAlgorithm(inputDesign, outputDesign, saltelli_size)
        
        # Lấy ma trận đối xứng chứa các chỉ số Sobol Bậc 2
        s2_matrix = saltelli.getSecondOrderIndices()
        
        var_names = input_ot.getDescription()
        num_vars = len(var_names)
        
        print("\n--- MA TRẬN SOBOL' BẬC 2 (INTERACTIONS) CHO TMAX (%) ---")
        for i in range(num_vars):
            for j in range(i + 1, num_vars):
                val = s2_matrix[i, j] * 100
                # Chỉ in ra những tương tác đáng kể (> 0.5%)
                if val > 0.5:
                    print(f" Tương tác [{var_names[i]} x {var_names[j]}]: {val:.2f}%")
        
        # --- VẼ BIỂU ĐỒ HEATMAP CHO BẬC 2 ---
        print(" -> Đang vẽ biểu đồ Heatmap cho Sobol Bậc 2...")
        # Chuyển SymmetricTensor của OpenTURNS thành Numpy Array
        s2_np = np.zeros((num_vars, num_vars))
        for i in range(num_vars):
            for j in range(num_vars):
                if i != j:
                    s2_np[i, j] = s2_matrix[i, j] * 100
                    
        fig, ax = plt.subplots(figsize=(6, 5))
        cax = ax.imshow(s2_np, cmap='Oranges', vmin=0)
        
        # Thêm text giá trị % vào từng ô vuông
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
        ax.set_title("Sobol' Second-Order Indices (%)", fontsize=14)
        
        fig.colorbar(cax, ax=ax, label='Tỷ lệ đóng góp phương sai (%)')
        plt.tight_layout()
        plt.savefig("Sobol_SecondOrder_Heatmap.png", dpi=300)
        plt.show()

        # ---------------------------------------------------------
        # 4.3. RELIABILITY ANALYSIS (Phân tích độ tin cậy)
        # ---------------------------------------------------------
        # Giả sử ngưỡng nứt vỡ (spalling threshold) của Tmax là 30 độ C
        T_THRESHOLD = 30.0
        print(f"\n -> Đang chạy Phân tích Độ tin cậy (Ngưỡng Tmax > {T_THRESHOLD}°C)...")
        
        # Định nghĩa biến ngẫu nhiên dựa trên Metamodel thay vì gọi Cast3M (cực nhanh)
        X_rnd = ot.RandomVector(my_distribution)
        Y_metamodel = ot.CompositeRandomVector(metamodel, X_rnd)
        
        # Sự kiện: Tmax > 30
        event = ot.ThresholdEvent(Y_metamodel, ot.Greater(), T_THRESHOLD)
        
        # Chạy Monte Carlo trên Metamodel (100,000 lần lặp chỉ mất ~1 giây)
        mc_algo = ot.ProbabilitySimulationAlgorithm(event, ot.MonteCarloExperiment())
        mc_algo.setMaximumOuterSampling(100000)
        mc_algo.run()
        
        pf = mc_algo.getResult().getProbabilityEstimate()
        print(f"=========================================================")
        print(f" KẾT QUẢ ĐÁNH GIÁ ĐỘ TIN CẬY (RELIABILITY)")
        print(f" Xác suất Tmax vượt quá {T_THRESHOLD}°C là: {pf * 100:.3f} %")
        print(f"=========================================================")

    except Exception as e:
        print(f"\n[LƯU Ý] Không thể chạy PCE & Sobol. Lỗi: {e}")
        print("-> Giải pháp: Đảm bảo bạn đặt N_loops >= 30 để OpenTURNS có đủ dữ liệu vẽ Metamodel.")
    
