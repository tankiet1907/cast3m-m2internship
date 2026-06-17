import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearson3
import os

# =========================================================
# 1. ĐỌC DỮ LIỆU TỪ SCRIPT 1
# =========================================================
working_dir = r"D:\cast3m-m2internship\05.Stochastic\Stochastic_C3"
output_dir = os.path.join(working_dir, "Plots")
os.makedirs(output_dir, exist_ok=True)

csv_file = os.path.join(working_dir, "CSV", "Quadrature_Results.csv")

try:
    df = pd.read_csv(csv_file, sep=';', on_bad_lines='skip')
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    # Cast3M xuất EVOL có cấu trúc X1, Y1, X2, Y2
    k0_vals     = df.iloc[:, 0].values
    strain_vals = df.iloc[:, 1].values
    weights     = df.iloc[:, 3].values

    # Đảm bảo tổng trọng số bằng 1
    weights = weights / np.sum(weights)
    print(f"Đã nạp {len(strain_vals)} điểm Quadrature.")
except Exception as e:
    print(f"LỖI ĐỌC DỮ LIỆU: {e}")
    exit()

# =========================================================
# 2. CẤU HÌNH PHÂN TÍCH
# =========================================================
CURRENT_THRESHOLD = -90.0       # đồng bộ với alea/lhs (đổi lại -400 nếu cần)
unit = "µm/m"
operator_str = "<"

# =========================================================
# 3. TÁI TẠO [PARASTAT]: TÍNH TOÁN MOMEN THỐNG KÊ
# =========================================================
mu_S = np.average(strain_vals, weights=weights)
var_S = np.average((strain_vals - mu_S)**2, weights=weights)
sigma_S = np.sqrt(var_S)
skew_S = np.average(((strain_vals - mu_S) / sigma_S)**3, weights=weights)
kurt_S = np.average(((strain_vals - mu_S) / sigma_S)**4, weights=weights)

print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
print("%%% STATISTICAL MOMENTS (Python PARASTAT equivalent)")
print(f"%%% MEAN        (MU)    = {mu_S:.4f} {unit}")
print(f"%%% STD DEV     (SIGMA) = {sigma_S:.4f} {unit}")
print(f"%%% SKEWNESS    (RB1)   = {skew_S:.4f}")
print(f"%%% KURTOSIS    (B2)    = {kurt_S:.4f}")
print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")

# =========================================================
# 4. TÁI TẠO [PROBDENS]: PEARSON TYPE 3
# =========================================================
dist = pearson3(skew=skew_S, loc=mu_S, scale=sigma_S)

x_min = mu_S - 4 * sigma_S
x_max = mu_S + 4 * sigma_S
x_plot = np.linspace(x_min, x_max, 500)

pdf_plot = dist.pdf(x_plot)
cdf_plot = dist.cdf(x_plot)

# Xác suất sự cố
pf = dist.cdf(CURRENT_THRESHOLD)

print(f"=========================================================")
print(f" RELIABILITY ANALYSIS RESULTS (Pearson Type III)")
print(f" Threshold: {operator_str} {CURRENT_THRESHOLD} {unit}")
print(f" Failure Prob (Pf) : {pf * 100:.4f} %")
print(f"=========================================================")

# =========================================================
# 5. VẼ ĐỒ THỊ PDF (style giống alea)
# =========================================================
print(" -> Đang tạo đồ thị PDF...")
fig = plt.figure(figsize=(10, 8))
ax1 = fig.add_subplot(111)

# Dữ liệu rời rạc (Dirac masses) — đóng vai trò "Empirical Data" như histogram bên alea
scale_factor = np.max(pdf_plot) / np.max(weights)
ax1.vlines(strain_vals, 0, weights * scale_factor, color='gray', lw=3,
           label='Quadrature Weights (Scaled)', zorder=1)
ax1.scatter(strain_vals, weights * scale_factor, color='gray',
            edgecolors='black', s=50, zorder=2)

# Đường PDF Pearson III (màu xanh, nằm trên)
ax1.plot(x_plot, pdf_plot, color='blue', lw=2,
         label='Fitted PDF (Pearson Type III)', zorder=5)

# Vùng failure + đường ngưỡng
x_tail = x_plot[x_plot <= CURRENT_THRESHOLD]
y_tail = pdf_plot[x_plot <= CURRENT_THRESHOLD]
legend_text = (f'Failure Region ({operator_str} {CURRENT_THRESHOLD} {unit})\n'
               f'Failure Prob (Pf) : {pf * 100:.2f}%')
ax1.fill_between(x_tail, y_tail, color='red', alpha=0.4, label=legend_text, zorder=3)
ax1.axvline(x=CURRENT_THRESHOLD, color='black', linestyle='--', linewidth=1.5,
            label=f'Threshold: {CURRENT_THRESHOLD} {unit}', zorder=4)

ax1.set_title("Probability Density & Failure Probability (Quadrature)",
              fontsize=14, fontweight='bold')
ax1.set_xlabel(f'Shrinkage Strain ({unit})', fontsize=12)
ax1.set_ylabel('Density', fontsize=12)
ax1.tick_params(axis='both', labelsize=10)
ax1.legend(loc='upper left', fontsize=10)
ax1.grid(True, linestyle='--', alpha=0.6)

pdf_path = os.path.join(output_dir, "Quadrature_PDF.png")
plt.savefig(pdf_path, dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"   [OK] Đã lưu: {pdf_path}")

# =========================================================
# 6. VẼ ĐỒ THỊ CDF (style giống alea)
# =========================================================
print(" -> Đang tạo đồ thị CDF...")
fig2 = plt.figure(figsize=(10, 8))
ax2 = fig2.add_subplot(111)

# CDF rời rạc từ Quadrature (bậc thang) — đóng vai trò "Empirical Data"
sort_idx = np.argsort(strain_vals)
sorted_strains = strain_vals[sort_idx]
cumulative_weights = np.cumsum(weights[sort_idx])
ax2.step(sorted_strains, cumulative_weights, where='post', color='gray',
         lw=2, linestyle='--', label='Discrete Cumulative Weights', zorder=1)
ax2.scatter(sorted_strains, cumulative_weights, color='gray',
            edgecolors='black', s=30, zorder=2)

# Đường CDF Pearson III (màu xanh, nằm trên)
ax2.plot(x_plot, cdf_plot, color='blue', lw=2,
         label='Fitted CDF (Pearson Type III)', zorder=5)

# Vùng failure + đường ngưỡng
x_tail_c = x_plot[x_plot <= CURRENT_THRESHOLD]
y_tail_c = cdf_plot[x_plot <= CURRENT_THRESHOLD]
legend_text_c = (f'Failure Region ({operator_str} {CURRENT_THRESHOLD} {unit})\n'
                 f'Failure Prob (Pf) : {pf * 100:.2f}%')
ax2.fill_between(x_tail_c, y_tail_c, color='red', alpha=0.4, label=legend_text_c, zorder=3)
ax2.axvline(x=CURRENT_THRESHOLD, color='black', linestyle='--', linewidth=1.5,
            label=f'Threshold: {CURRENT_THRESHOLD} {unit}', zorder=4)

ax2.set_title("Cumulative Distribution & Failure Probability (Quadrature)",
              fontsize=14, fontweight='bold')
ax2.set_xlabel(f'Shrinkage Strain ({unit})', fontsize=12)
ax2.set_ylabel('Cumulative Probability', fontsize=12)
ax2.tick_params(axis='both', labelsize=10)
ax2.legend(loc='upper left', fontsize=10)
ax2.grid(True, linestyle='--', alpha=0.6)

cdf_path = os.path.join(output_dir, "Quadrature_CDF.png")
plt.savefig(cdf_path, dpi=150, bbox_inches='tight')
plt.close(fig2)
print(f"   [OK] Đã lưu: {cdf_path}")