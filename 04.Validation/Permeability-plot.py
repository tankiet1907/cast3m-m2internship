import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. THÔNG SỐ CALIBRATION (Cần trùng khớp với trong Cast3M)
AK = 3.0          # Thay đổi thông số này để giống với Cast3M (nếu cần) - Lưu ý: AK càng lớn thì độ thấm giảm nhanh hơn theo thời gian do hydration tăng lên
KK0 = 2.E-19     # Thay đổi thông số này để giống với Cast3M (kint). Hệ số K0 cơ bản
BKLI = 100000.    # Hiệu ứng Klinkenberg
F_MAX = 100.
P_ATM = 101325.

# Màu sắc map theo Castem
colors = {
    '00': 'blue',       # BLEU
    '10': 'red',        # ORAN
    '20': 'gold',       # JAUN
    '30': 'deeppink',   # ROSE
    '40': 'green',      # VERT
    '50': 'cyan',       # TURQ
    '120': 'black'      # Dùng Đen/Xám để dễ nhìn trên nền trắng thay vì BLAN (trắng)
}

# 2. ĐỌC DỮ LIỆU TỪ CSV
# Lưu ý: Các file CSV cần có cùng số dòng và cùng trục thời gian
df_hyd = pd.read_csv(r'D:\cast3m-m2internship\02.Simulation\02.Results\HydrationDegree_1min_Intervals.csv', sep=';')
df_pg = pd.read_csv(r'D:\cast3m-m2internship\02.Simulation\02.Results\GasPressure_1min_Intervals.csv', sep=';')

# Giả sử file có cấu trúc cột: [Time, Val_10mm, Val_20mm, ...]
# Lấy Time (cột 0)
time_sim = df_hyd.iloc[:, 0]

# 3. TÍNH TOÁN CÔNG THỨC CHO K DÙNG HYDRATION DEGREE (Vectorized bằng numpy)
def calculate_permeability(hyd_val, pg_val):
    # HYEFF_K = EXP (2.302585 * AK * (1. - HYDR))
    hyeff_k = np.exp(2.302585 * AK * (1. - hyd_val))
    hyeff_k = np.clip(hyeff_k, None, F_MAX)
    
    # Tính KINTL
    kintl = KK0 * hyeff_k
    
    # Tính KINTG 
    kintg = KK0 * hyeff_k * (1. + (BKLI * ((pg_val * 1.E6)**-1.)))
    
    return kintl, kintg

# 4. VẼ ĐỒ THỊ
hyd_00 = df_hyd.iloc[:, 1]
hyd_10 = df_hyd.iloc[:, 3]
hyd_20 = df_hyd.iloc[:, 5]
hyd_30 = df_hyd.iloc[:, 7]
hyd_40 = df_hyd.iloc[:, 9]
hyd_50 = df_hyd.iloc[:, 11]
hyd_120 = df_hyd.iloc[:, 13]

pg_00  = df_pg.iloc[:, 1]
pg_10  = df_pg.iloc[:, 3]
pg_20  = df_pg.iloc[:, 5]
pg_30  = df_pg.iloc[:, 7]
pg_40  = df_pg.iloc[:, 9]
pg_50  = df_pg.iloc[:, 11]
pg_120 = df_pg.iloc[:, 13]

kintl_00, kintg_00 = calculate_permeability(hyd_00, pg_00)
kintl_10, kintg_10 = calculate_permeability(hyd_10, pg_10)
kintl_20, kintg_20 = calculate_permeability(hyd_20, pg_20)
kintl_30, kintg_30 = calculate_permeability(hyd_30, pg_30)
kintl_40, kintg_40 = calculate_permeability(hyd_40, pg_40)
kintl_50, kintg_50 = calculate_permeability(hyd_50, pg_50)
kintl_120, kintg_120 = calculate_permeability(hyd_120, pg_120)

#plt.plot(time_sim, kintl_00, color=colors['00'], linestyle='-', label='KINTL 00mm')
plt.plot(time_sim, kintl_10, color=colors['10'], linestyle='-', label='KINTL 10mm')
plt.plot(time_sim, kintl_20, color=colors['20'], linestyle='-', label='KINTL 20mm')
plt.plot(time_sim, kintl_30, color=colors['30'], linestyle='-', label='KINTL 30mm')
plt.plot(time_sim, kintl_40, color=colors['40'], linestyle='-', label='KINTL 40mm')
plt.plot(time_sim, kintl_50, color=colors['50'], linestyle='-', label='KINTL 50mm')
#plt.plot(time_sim, kintl_120, color=colors['120'], linestyle='-', label='KINTL 120mm')

#plt.plot(time_sim, kintg_00, color=colors['00'], linestyle='--', label='KINTG 00mm')
plt.plot(time_sim, kintg_10, color=colors['10'], linestyle='--', label='KINTG 10mm')
plt.plot(time_sim, kintg_20, color=colors['20'], linestyle='--', label='KINTG 20mm')
plt.plot(time_sim, kintg_30, color=colors['30'], linestyle='--', label='KINTG 30mm')
plt.plot(time_sim, kintg_40, color=colors['40'], linestyle='--', label='KINTG 40mm')
plt.plot(time_sim, kintg_50, color=colors['50'], linestyle='--', label='KINTG 50mm')
#plt.plot(time_sim, kintg_120, color=colors['120'], linestyle='--', label='KINTG 120mm')
    


# DỮ LIỆU THAM CHIẾU (Dauti)
K0 = 7.5E-20  # Hệ số K0 cơ bản
AT = 0.005
AP = 0.01
T0 = 20.0

time_dauti = np.arange(0, 245, 5)  # Từ 0 đến 240, bước nhảy 5 (49 điểm)

# --- Dữ liệu Dauti - Temperature (Reference) ---
LTD_00 = [20.0, 116.6, 158.0, 186.7, 204.9, 225.2, 239.2, 251.0, 261.5, 272.0, 281.1, 289.5, 296.5, 303.5, 310.5, 316.1, 323.1, 329.4, 334.3, 339.2, 344.8, 349.7, 355.2, 359.4, 363.6, 368.5, 372.7, 376.2, 379.7, 381.8, 384.6, 386.7, 388.8, 390.2, 392.3, 393.7, 395.1, 396.5, 397.9, 399.3, 400.7, 402.1, 403.5, 404.9, 405.6, 407.0, 407.7, 408.4, 408.4]
LTD_10 = [20.0, 65.7, 103.5, 131.5, 154.5, 169.9, 184.6, 197.2, 209.1, 219.6, 230.8, 239.2, 247.6, 255.2, 262.2, 269.2, 275.5, 281.8, 288.1, 294.4, 300.0, 304.9, 309.8, 315.4, 320.3, 325.2, 329.4, 334.3, 337.8, 340.6, 344.8, 346.9, 350.3, 352.4, 355.2, 356.6, 359.4, 361.5, 363.6, 365.7, 368.5, 369.9, 372.0, 373.4, 374.8, 376.2, 377.6, 379.0, 380.4]
LTD_20 = [20.0, 39.2, 65.7, 89.5, 110.5, 129.4, 145.5, 155.9, 167.8, 177.6, 187.4, 195.8, 205.6, 213.3, 220.3, 226.6, 234.3, 241.3, 246.9, 253.1, 258.7, 264.3, 270.6, 276.2, 281.1, 286.0, 290.9, 295.1, 299.3, 304.2, 307.7, 311.9, 315.4, 318.2, 321.0, 323.8, 326.6, 329.4, 332.2, 334.3, 336.4, 338.5, 340.6, 343.4, 344.8, 346.9, 349.7, 351.0, 353.1]
LTD_30 = [20.0, 26.6, 46.2, 64.3, 81.8, 97.9, 111.9, 123.1, 135.0, 144.1, 154.5, 162.9, 171.3, 178.3, 186.0, 193.0, 200.0, 206.3, 211.9, 218.2, 224.5, 230.1, 235.7, 240.6, 246.2, 251.7, 256.6, 261.5, 265.7, 270.6, 274.8, 279.0, 283.2, 286.0, 290.2, 293.0, 295.8, 299.3, 302.1, 304.9, 307.7, 310.5, 312.6, 315.4, 318.2, 319.6, 322.4, 323.8, 325.9]
LTD_40 = [20.0, 23.1, 30.8, 43.4, 58.0, 72.0, 83.9, 94.4, 105.6, 116.1, 124.5, 133.6, 142.0, 149.0, 157.3, 163.6, 169.9, 176.9, 183.9, 189.5, 195.1, 201.4, 206.3, 211.2, 216.8, 221.7, 226.6, 231.5, 235.0, 240.6, 244.8, 249.0, 253.8, 256.6, 260.8, 263.6, 267.8, 270.6, 274.1, 277.6, 281.1, 283.9, 286.0, 288.8, 291.6, 294.4, 297.2, 299.3, 301.4]
LTD_50 = [20.0, 20.3, 25.2, 33.6, 42.7, 53.1, 63.6, 72.7, 82.5, 92.3, 100.0, 109.1, 116.8, 124.5, 131.5, 138.5, 144.8, 151.7, 158.7, 164.3, 169.9, 175.5, 181.8, 187.4, 192.3, 197.2, 202.1, 207.0, 211.9, 216.1, 221.0, 224.5, 228.7, 232.9, 236.4, 239.9, 243.4, 246.2, 249.7, 253.1, 256.6, 259.4, 262.2, 265.7, 268.5, 271.3, 273.4, 276.2, 279.0]

# --- Dữ liệu Áp suất khí Dauti (Reference) ---
LPG_DA_10 = [0.1, 0.1515, 0.5455, 1.0152, 1.3535, 1.6414, 1.8687, 2.0354, 2.1414, 2.1414, 2.1061, 2.0606, 2.0152, 1.9697, 1.9293, 1.8838, 1.8485, 1.8131, 1.7778, 1.7475, 1.7172, 1.6919, 1.6667, 1.6414, 1.6162, 1.5960, 1.5758, 1.5556, 1.5303, 1.5152, 1.4949, 1.4798, 1.4646, 1.4495, 1.4394, 1.4242, 1.4141, 1.3990, 1.3939, 1.3838, 1.3737, 1.3586, 1.3485, 1.3333, 1.3283, 1.3182, 1.3030, 1.2879, 1.2828]
LPG_DA_20 = [0.1, 0.0606, 0.1212, 0.2980, 0.5606, 0.9192, 1.1869, 1.4343, 1.6364, 1.7980, 1.9697, 2.1010, 2.2475, 2.3788, 2.4899, 2.5455, 2.5556, 2.5303, 2.5051, 2.4697, 2.4394, 2.4040, 2.3737, 2.3434, 2.3081, 2.2828, 2.2576, 2.2323, 2.1970, 2.1768, 2.1515, 2.1263, 2.1061, 2.0808, 2.0657, 2.0455, 2.0253, 2.0101, 1.9899, 1.9747, 1.9596, 1.9394, 1.9192, 1.9040, 1.8889, 1.8687, 1.8535, 1.8333, 1.8131]
LPG_DA_30 = [0.1, 0.0909, 0.0606, 0.0960, 0.1616, 0.3081, 0.4899, 0.7525, 0.9949, 1.1970, 1.3838, 1.5404, 1.6717, 1.8030, 1.9293, 2.0505, 2.1616, 2.2828, 2.4091, 2.5253, 2.6414, 2.7424, 2.8081, 2.8283, 2.8283, 2.8131, 2.7929, 2.7778, 2.7525, 2.7222, 2.6970, 2.6667, 2.6414, 2.6162, 2.5909, 2.5707, 2.5455, 2.5253, 2.5000, 2.4798, 2.4596, 2.4343, 2.4091, 2.3889, 2.3687, 2.3434, 2.3182, 2.2980, 2.2778]
LPG_DA_40 = [0.1, 0.1010, 0.0657, 0.0556, 0.0758, 0.1162, 0.1768, 0.2778, 0.4192, 0.5909, 0.7778, 0.9697, 1.1465, 1.2929, 1.4343, 1.5556, 1.6717, 1.7828, 1.8889, 1.9899, 2.0960, 2.1919, 2.2980, 2.4040, 2.5051, 2.6212, 2.7374, 2.8485, 2.9646, 3.0404, 3.0808, 3.0909, 3.0859, 3.0657, 3.0455, 3.0253, 3.0000, 2.9747, 2.9495, 2.9242, 2.9040, 2.8788, 2.8535, 2.8283, 2.7980, 2.7727, 2.7475, 2.7222, 2.6919]
LPG_DA_50 = [0.1, 0.1010, 0.0960, 0.0606, 0.0505, 0.0606, 0.0808, 0.1263, 0.1768, 0.2424, 0.3384, 0.4596, 0.6061, 0.7576, 0.9091, 1.0556, 1.2020, 1.3232, 1.4444, 1.5556, 1.6717, 1.7727, 1.8687, 1.9697, 2.0606, 2.1465, 2.2475, 2.3384, 2.4343, 2.5404, 2.6465, 2.7475, 2.8586, 2.9646, 3.0606, 3.1566, 3.2323, 3.2778, 3.2980, 3.2929, 3.2778, 3.2576, 3.2374, 3.2121, 3.1869, 3.1616, 3.1313, 3.1010, 3.0707]

# 3. Nội suy về lưới 1 phút để đồng bộ
# Code gốc không nội suy mà chỉ lấy dữ liệu 5 phút một lần dùng array
#TD_10 = np.array(LTD_10)
#PGD_10 = np.array(LPG_DA_10)
#plt.plot(time_dauti, K_10, color=colors['10'], linestyle='--', label='Dauti K - 10mm')

TD_10 = np.interp(time_sim, time_dauti, LTD_10)
TD_20 = np.interp(time_sim, time_dauti, LTD_20)
TD_30 = np.interp(time_sim, time_dauti, LTD_30)
TD_40 = np.interp(time_sim, time_dauti, LTD_40)
TD_50 = np.interp(time_sim, time_dauti, LTD_50)

PGD_10 = np.interp(time_sim, time_dauti, LPG_DA_10)
PGD_20 = np.interp(time_sim, time_dauti, LPG_DA_20)
PGD_30 = np.interp(time_sim, time_dauti, LPG_DA_30)
PGD_40 = np.interp(time_sim, time_dauti, LPG_DA_40)
PGD_50 = np.interp(time_sim, time_dauti, LPG_DA_50)

def dauti_permeability(TD, PGD):
    K=K0 * (10**(AT * (TD - T0))) * ((PGD * 1.E6/ P_ATM)**AP)
    return K

K_10 = dauti_permeability(TD_10, PGD_10)
K_20 = dauti_permeability(TD_20, PGD_20)
K_30 = dauti_permeability(TD_30, PGD_30)
K_40 = dauti_permeability(TD_40, PGD_40)
K_50 = dauti_permeability(TD_50, PGD_50)

plt.plot(time_sim, K_10, color=colors['10'], linestyle=':', label='Dauti K - 10mm')
plt.plot(time_sim, K_20, color=colors['20'], linestyle=':', label='Dauti K - 20mm')
plt.plot(time_sim, K_30, color=colors['30'], linestyle=':', label='Dauti K - 30mm')
plt.plot(time_sim, K_40, color=colors['40'], linestyle=':', label='Dauti K - 40mm')
plt.plot(time_sim, K_50, color=colors['50'], linestyle=':', label='Dauti K - 50mm')


plt.yscale('log') # Rất quan trọng vì độ thấm thay đổi theo bậc độ lớn
plt.title(f'Permeability Evolution - Simulation vs Dauti (AK={AK}, KK0={KK0:.1e})', fontsize=14, fontweight='bold')
plt.xlabel('Time (min)')
plt.ylabel('Permeability (m²)')

# Thiết lập giới hạn trục X
plt.xlim(0, 240)
# Thiết lập bước nhảy trục X là 20 phút
plt.xticks(np.arange(0, 241, 20), rotation=0)

plt.grid(True, which='both', linestyle='-', color='lightgrey')

# Hiển thị Legend
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10, ncol=1)
# Tự động căn chỉnh bố cục để không bị cắt chữ
plt.tight_layout()

# Lưu hình ảnh với độ phân giải cao
output_img = r'D:\cast3m-m2internship\01.Report\figures\plots\Permeability_results_Comparison.png'
plt.savefig(output_img, dpi=300, bbox_inches='tight')

plt.show()