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
# 2. TÁI TẠO [PARASTAT]: TÍNH TOÁN MOMEN THỐNG KÊ
# =========================================================
# Tính Mean (MU) và Variance
mu_S = np.average(strain_vals, weights=weights)
var_S = np.average((strain_vals - mu_S)**2, weights=weights)
sigma_S = np.sqrt(var_S)

# Tính Skewness (RB1) và Kurtosis (B2)
skew_S = np.average(((strain_vals - mu_S) / sigma_S)**3, weights=weights)
kurt_S = np.average(((strain_vals - mu_S) / sigma_S)**4, weights=weights)

print("\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
print("%%% STATISTICAL MOMENTS (Python PARASTAT equivalent)")
print(f"%%% MEAN        (MU)    = {mu_S:.4f} µm/m")
print(f"%%% STD DEV     (SIGMA) = {sigma_S:.4f} µm/m")
print(f"%%% SKEWNESS    (RB1)   = {skew_S:.4f}")
print(f"%%% KURTOSIS    (B2)    = {kurt_S:.4f}")
print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")

# =========================================================
# 3. TÁI TẠO [PROBDENS]: XÂY DỰNG PDF & CDF BẰNG PEARSON TYPE 3
# =========================================================
# Scipy Pearson3 sử dụng Skewness làm tham số hình dáng
# loc = Mean, scale = Std Dev
dist = pearson3(skew=skew_S, loc=mu_S, scale=sigma_S)

# Tạo trục X để vẽ đường cong
x_min = mu_S - 4 * sigma_S
x_max = mu_S + 4 * sigma_S
x_plot = np.linspace(x_min, x_max, 500)

pdf_plot = dist.pdf(x_plot)
cdf_plot = dist.cdf(x_plot)

# ---------------------------------------------------------
# VẼ ĐỒ THỊ PDF (XÁC SUẤT)
# ---------------------------------------------------------
fig, ax1 = plt.subplots(figsize=(8, 5))

# Vẽ đường cong PDF từ Pearson Type 3 (Giống PROBDENS)
ax1.plot(x_plot, pdf_plot, 'r-', lw=2, label='Fitted PDF (Pearson Type III)')

# Vẽ các điểm khối lượng (Dirac Masses) từ Quadrature
# Nhân weights với hệ số tỷ lệ để chúng hiển thị tương quan trên trục mật độ
scale_factor = np.max(pdf_plot) / np.max(weights)
ax1.vlines(strain_vals, 0, weights * scale_factor, color='blue', lw=3, label='Quadrature Weights (Scaled)')
ax1.scatter(strain_vals, weights * scale_factor, color='blue', s=50, zorder=5)

ax1.set_title("Probability Density Function (PDF) of Shrinkage Strain", fontsize=14, fontweight='bold')
ax1.set_xlabel("Shrinkage Strain (µm/m)", fontsize=12)
ax1.set_ylabel("Density", fontsize=12)
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.legend(loc='best')

pdf_path = os.path.join(output_dir, "Quadrature_PDF.png")
plt.savefig(pdf_path, dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"-> Đã lưu: {pdf_path}")

# ---------------------------------------------------------
# VẼ ĐỒ THỊ CDF (PHÂN BỐ TÍCH LŨY) VÀ TÍNH ĐỘ TIN CẬY
# ---------------------------------------------------------
# Sắp xếp dữ liệu rời rạc để vẽ CDF dạng bậc thang
sort_idx = np.argsort(strain_vals)
sorted_strains = strain_vals[sort_idx]
cumulative_weights = np.cumsum(weights[sort_idx])

fig2, ax2 = plt.subplots(figsize=(8, 5))

# Vẽ đường cong CDF (PROBDENS)
ax2.plot(x_plot, cdf_plot, 'r-', lw=2, label='Fitted CDF (Pearson Type III)')

# Vẽ CDF rời rạc từ Quadrature (Dạng bậc thang)
ax2.step(sorted_strains, cumulative_weights, where='post', color='blue', lw=2, linestyle='--', label='Discrete Cumulative Weights')
ax2.scatter(sorted_strains, cumulative_weights, color='blue', s=30, zorder=5)

# TÍNH XÁC SUẤT SỰ CỐ (Failure Probability)
CURRENT_THRESHOLD = -400.0
pf = dist.cdf(CURRENT_THRESHOLD)

ax2.axvline(x=CURRENT_THRESHOLD, color='black', linestyle='-.', lw=1.5, label=f'Threshold (< {CURRENT_THRESHOLD})')
ax2.fill_between(x_plot[x_plot <= CURRENT_THRESHOLD], cdf_plot[x_plot <= CURRENT_THRESHOLD], color='red', alpha=0.3, label=f'Pf = {pf*100:.2f}%')

ax2.set_title("Cumulative Distribution Function (CDF)", fontsize=14, fontweight='bold')
ax2.set_xlabel("Shrinkage Strain (µm/m)", fontsize=12)
ax2.set_ylabel("Cumulative Probability", fontsize=12)
ax2.grid(True, linestyle='--', alpha=0.6)
ax2.legend(loc='best')

cdf_path = os.path.join(output_dir, "Quadrature_CDF.png")
plt.savefig(cdf_path, dpi=150, bbox_inches='tight')
plt.close(fig2)
print(f"-> Đã lưu: {cdf_path}")