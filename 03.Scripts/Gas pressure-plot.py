import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ===================================================================
# 1. NHẬP DỮ LIỆU DAUTI VÀ THỰC NGHIỆM (GAS PRESSURE)
# ===================================================================

# --- Trục thời gian ---
time_dauti = np.arange(0, 245, 5)  # Từ 0 đến 240, bước nhảy 5 (49 điểm)
time_exp = np.arange(5, 245, 5)    # Từ 5 đến 240, bước nhảy 5 (48 điểm)

# --- Dữ liệu Áp suất khí Dauti (Reference) ---
LPG_DA_10 = [0.1, 0.1515, 0.5455, 1.0152, 1.3535, 1.6414, 1.8687, 2.0354, 2.1414, 2.1414, 2.1061, 2.0606, 2.0152, 1.9697, 1.9293, 1.8838, 1.8485, 1.8131, 1.7778, 1.7475, 1.7172, 1.6919, 1.6667, 1.6414, 1.6162, 1.5960, 1.5758, 1.5556, 1.5303, 1.5152, 1.4949, 1.4798, 1.4646, 1.4495, 1.4394, 1.4242, 1.4141, 1.3990, 1.3939, 1.3838, 1.3737, 1.3586, 1.3485, 1.3333, 1.3283, 1.3182, 1.3030, 1.2879, 1.2828]
LPG_DA_20 = [0.1, 0.0606, 0.1212, 0.2980, 0.5606, 0.9192, 1.1869, 1.4343, 1.6364, 1.7980, 1.9697, 2.1010, 2.2475, 2.3788, 2.4899, 2.5455, 2.5556, 2.5303, 2.5051, 2.4697, 2.4394, 2.4040, 2.3737, 2.3434, 2.3081, 2.2828, 2.2576, 2.2323, 2.1970, 2.1768, 2.1515, 2.1263, 2.1061, 2.0808, 2.0657, 2.0455, 2.0253, 2.0101, 1.9899, 1.9747, 1.9596, 1.9394, 1.9192, 1.9040, 1.8889, 1.8687, 1.8535, 1.8333, 1.8131]
LPG_DA_30 = [0.1, 0.0909, 0.0606, 0.0960, 0.1616, 0.3081, 0.4899, 0.7525, 0.9949, 1.1970, 1.3838, 1.5404, 1.6717, 1.8030, 1.9293, 2.0505, 2.1616, 2.2828, 2.4091, 2.5253, 2.6414, 2.7424, 2.8081, 2.8283, 2.8283, 2.8131, 2.7929, 2.7778, 2.7525, 2.7222, 2.6970, 2.6667, 2.6414, 2.6162, 2.5909, 2.5707, 2.5455, 2.5253, 2.5000, 2.4798, 2.4596, 2.4343, 2.4091, 2.3889, 2.3687, 2.3434, 2.3182, 2.2980, 2.2778]
LPG_DA_40 = [0.1, 0.1010, 0.0657, 0.0556, 0.0758, 0.1162, 0.1768, 0.2778, 0.4192, 0.5909, 0.7778, 0.9697, 1.1465, 1.2929, 1.4343, 1.5556, 1.6717, 1.7828, 1.8889, 1.9899, 2.0960, 2.1919, 2.2980, 2.4040, 2.5051, 2.6212, 2.7374, 2.8485, 2.9646, 3.0404, 3.0808, 3.0909, 3.0859, 3.0657, 3.0455, 3.0253, 3.0000, 2.9747, 2.9495, 2.9242, 2.9040, 2.8788, 2.8535, 2.8283, 2.7980, 2.7727, 2.7475, 2.7222, 2.6919]
LPG_DA_50 = [0.1, 0.1010, 0.0960, 0.0606, 0.0505, 0.0606, 0.0808, 0.1263, 0.1768, 0.2424, 0.3384, 0.4596, 0.6061, 0.7576, 0.9091, 1.0556, 1.2020, 1.3232, 1.4444, 1.5556, 1.6717, 1.7727, 1.8687, 1.9697, 2.0606, 2.1465, 2.2475, 2.3384, 2.4343, 2.5404, 2.6465, 2.7475, 2.8586, 2.9646, 3.0606, 3.1566, 3.2323, 3.2778, 3.2980, 3.2929, 3.2778, 3.2576, 3.2374, 3.2121, 3.1869, 3.1616, 3.1313, 3.1010, 3.0707]

# --- Dữ liệu Áp suất khí Thực nghiệm (Experimental) ---
LPGE_10 = [0.0442, 0.1125, 0.3040, 0.5271, 0.8036, 1.1488, 1.4976, 1.8497, 2.0802, 1.8728, 1.3952, 1.1615, 0.9911, 0.9317, 0.8685, 0.8429, 0.8174, 0.7919, 0.7664, 0.7408, 0.7153, 0.6922, 0.6700, 0.6495, 0.6309, 0.6123, 0.5963, 0.5831, 0.5699, 0.5568, 0.5436, 0.5278, 0.5111, 0.4943, 0.4776, 0.4609, 0.4441, 0.4274, 0.4107, 0.3950, 0.3817, 0.3683, 0.3549, 0.3415, 0.3281, 0.3148, 0.3012, 0.2869]
LPGE_20 = [0.0255, 0.0510, 0.0766, 0.1702, 0.2833, 0.4639, 0.6643, 0.8896, 1.1589, 1.4350, 1.7111, 2.0132, 2.3404, 2.6461, 2.8814, 2.9006, 2.3996, 2.1459, 2.0572, 2.0344, 2.0171, 1.9998, 1.9847, 1.9695, 1.9543, 1.9392, 1.9240, 1.9074, 1.8567, 1.8061, 1.7554, 1.7047, 1.6539, 1.6029, 1.5519, 1.5009, 1.4499, 1.3989, 1.3479, 1.2987, 1.2510, 1.2034, 1.1557, 1.1080, 1.0604, 1.0127, 0.9650, 0.9174]
LPGE_30 = [0.0188, 0.0334, 0.0480, 0.0626, 0.0773, 0.1221, 0.2200, 0.3406, 0.4776, 0.6246, 0.7715, 0.9298, 1.1326, 1.3354, 1.5067, 1.6779, 1.8324, 1.9252, 2.0179, 2.1107, 2.1752, 2.1974, 2.2197, 2.2160, 2.2105, 2.2051, 2.1811, 2.1500, 2.1190, 2.0879, 2.0509, 2.0136, 1.9763, 1.9389, 1.9016, 1.8643, 1.8185, 1.7708, 1.7231, 1.6754, 1.6277, 1.5800, 1.5323, 1.4846, 1.4369, 1.3892, 1.3405, 1.2782]
LPGE_40 = [0.0074, 0.0142, 0.0209, 0.0277, 0.0418, 0.0688, 0.1149, 0.1622, 0.2336, 0.3450, 0.4564, 0.6312, 0.8171, 1.0503, 1.2947, 1.5536, 1.8125, 2.0577, 2.2622, 2.4667, 2.6453, 2.7939, 2.9425, 3.0897, 3.2260, 3.2645, 3.2388, 3.1999, 3.1611, 3.1062, 3.0448, 2.9835, 2.9222, 2.8609, 2.7808, 2.6938, 2.6068, 2.5198, 2.4327, 2.3457, 2.2587, 2.1717, 2.0846, 1.9976, 1.9106, 1.8251, 1.7474, 1.6696]
LPGE_50 = [0.0068, 0.0137, 0.0205, 0.0386, 0.0583, 0.0779, 0.0976, 0.1362, 0.1826, 0.2291, 0.2755, 0.3462, 0.4485, 0.5507, 0.6529, 0.7551, 0.8763, 1.0770, 1.2778, 1.4785, 1.6793, 1.8801, 2.0808, 2.2801, 2.4755, 2.6653, 2.7772, 2.8891, 3.0010, 3.1129, 3.1897, 3.2612, 3.3326, 3.4009, 3.4529, 3.5048, 3.5567, 3.6085, 3.6600, 3.6646, 3.6153, 3.4466, 3.1950, 2.9832, 2.7869, 2.6043, 2.4752, 2.3461]

# Màu sắc map theo Castem
colors = {
    '10': 'blue',       # BLEU
    '20': 'red',     # ORAN
    '30': 'gold',       # JAUN
    '40': 'deeppink',   # ROSE
    '50': 'green'       # VERT
}

# ===================================================================
# 2. ĐỌC DỮ LIỆU TỪ CASTEM CSV (GAS PRESSURE) VÀ PLOT
# ===================================================================

plt.figure(figsize=(10, 8))

# Đường dẫn file CSV kết quả Gas Pressure (sửa lại theo tên file thực tế của bạn)
csv_file = r'D:\cast3m-m2internship\02.Simulation\02.Results\GasPressure_5min_Intervals.csv'

try:
    # Đọc file CSV
    df_castem = pd.read_csv(csv_file, sep=';')
    time_sim = time_dauti 
    
    # Vẽ mô phỏng (Nét liền). 
    # Lưu ý: Vì không có 0mm, nếu bạn chỉ export 5 đường (10,20,30,40,50), 
    # thì index các cột giá trị Y sẽ là 1, 3, 5, 7, 9. 
    # Bạn hãy kiểm tra lại cấu trúc file CSV nếu code bị lỗi out-of-bounds nhé!
    plt.plot(time_sim, df_castem.iloc[:, 1], color=colors['10'], linestyle='-', label='Sim Pg 10mm')
    plt.plot(time_sim, df_castem.iloc[:, 3], color=colors['20'], linestyle='-', label='Sim Pg 20mm')
    plt.plot(time_sim, df_castem.iloc[:, 5], color=colors['30'], linestyle='-', label='Sim Pg 30mm')
    plt.plot(time_sim, df_castem.iloc[:, 7], color=colors['40'], linestyle='-', label='Sim Pg 40mm')
    plt.plot(time_sim, df_castem.iloc[:, 9], color=colors['50'], linestyle='-', label='Sim Pg 50mm')

except FileNotFoundError:
    print(f"Không tìm thấy file: {csv_file}. Vui lòng kiểm tra lại đường dẫn!")
except Exception as e:
    print(f"Lỗi khi đọc file CSV: {e}")

# ===================================================================
# 3. VẼ DỮ LIỆU DAUTI & EXPERIMENTAL
# ===================================================================

# Vẽ Dauti (Nét đứt / Dashed)
plt.plot(time_dauti, LPG_DA_10, color=colors['10'], linestyle='--', label='Dauti Pg 10')
plt.plot(time_dauti, LPG_DA_20, color=colors['20'], linestyle='--', label='Dauti Pg 20')
plt.plot(time_dauti, LPG_DA_30, color=colors['30'], linestyle='--', label='Dauti Pg 30')
plt.plot(time_dauti, LPG_DA_40, color=colors['40'], linestyle='--', label='Dauti Pg 40')
plt.plot(time_dauti, LPG_DA_50, color=colors['50'], linestyle='--', label='Dauti Pg 50')

# Vẽ Thực nghiệm (Nét chấm / Dotted)
plt.plot(time_exp, LPGE_10, color=colors['10'], linestyle=':', linewidth=2, label='Exp Pg 10')
plt.plot(time_exp, LPGE_20, color=colors['20'], linestyle=':', linewidth=2, label='Exp Pg 20')
plt.plot(time_exp, LPGE_30, color=colors['30'], linestyle=':', linewidth=2, label='Exp Pg 30')
plt.plot(time_exp, LPGE_40, color=colors['40'], linestyle=':', linewidth=2, label='Exp Pg 40')
plt.plot(time_exp, LPGE_50, color=colors['50'], linestyle=':', linewidth=2, label='Exp Pg 50')

# ===================================================================
# 4. TÙY CHỈNH GIAO DIỆN ĐỒ THỊ
# ===================================================================

plt.title('Gas Pressure: Current (Solid) vs Dauti (Dashed) vs Exp (Dotted)', fontsize=14, fontweight='bold')
plt.xlabel('Time (min)', fontsize=12)
plt.ylabel('Gas Pressure (MPa or bar)', fontsize=12)

# Thiết lập giới hạn trục toạ độ (theo đúng XBOR và YBOR của Castem)
plt.xlim(0, 240)
plt.ylim(0, 4.0)

# Thiết lập bước nhảy (Tick steps) - theo XGRA 10. và YGRA 0.25
plt.xticks(np.arange(0, 241, 10))
plt.yticks(np.arange(0, 4.25, 0.25))

# Xoay nhãn trục X 45 độ nếu bước nhảy 10 làm các số sát nhau khó nhìn
plt.xticks(rotation=45)

plt.grid(True, which='both', linestyle='-', color='lightgrey')

# Tối ưu legend (Gom thành 3 cột và đẩy ra ngoài hoặc vị trí an toàn)
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=9, ncol=2)

plt.tight_layout()

# Lưu file (Đổi đường dẫn nếu cần)
plt.savefig(r'D:\cast3m-m2internship\01.Report\figures\plots\Gas-pressure_results_Comparison.png', dpi=300)

plt.show()