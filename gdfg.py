import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

# === CSVファイル ===
path = Path("adafg.csv")
df = pd.read_csv(path)

# === 列名 ===
col_c1 = "中央 Recorded Tmp（℃）"
col_c2 = "間口 Recorded Tmp（℃）"
col_air = "Air tmp（℃）"
col_d1 = "中央 Diff"
col_d2 = "間口 Diff"

# === タイムスタンプ列（30分間隔） ===
start = pd.Timestamp("2025-08-28 10:30:00")
dt_index = start + pd.to_timedelta(np.arange(len(df)), unit="m") * 30
df["Timestamp_fixed"] = dt_index

# === 数値変換 ===
for c in [col_c1, col_c2, col_air]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

df[col_d1] = df[col_d1].astype(str).str.replace('%', '', regex=False)
df[col_d2] = df[col_d2].astype(str).str.replace('%', '', regex=False)
df[col_d1] = pd.to_numeric(df[col_d1], errors="coerce")
df[col_d2] = pd.to_numeric(df[col_d2], errors="coerce")

df_raw = df.set_index("Timestamp_fixed")

# === 大気温補間 ===
df_interp = df_raw.copy()
df_interp[col_air] = df_interp[col_air].interpolate(method='time', limit_direction='both')

# === グラフ描画 ===
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})

# 上段
ax1.plot(df_interp.index, df_interp[col_air], label="Ambient (Interpolated)", linestyle="--", color="tab:blue")
ax1.plot(df_interp.index, df_interp[col_c1], label="Container 1 (Measured)", color="tab:orange")
ax1.plot(df_interp.index, df_interp[col_c2], label="Container 2 (Measured)", color="tab:green")
ax1.set_ylabel("Temperature (°C)")
ax1.set_title("Container vs Ambient Temperature (Weekly Date Labels)")
ax1.legend(loc="upper right")
ax1.grid(True)

# 下段
bar_width = 0.02
ax2.bar(df_interp.index, df_interp[col_d1], width=bar_width, label="Gap 1", color="tab:red", alpha=0.6)
ax2.bar(df_interp.index, df_interp[col_d2], width=bar_width, label="Gap 2", color="tab:pink", alpha=0.6)
ax2.set_ylabel("Δ Temp (%)")
ax2.set_title("Temperature Gap (Measured - Interpolated Ambient)")
ax2.legend(loc="upper right")
ax2.grid(True)

# === 横軸設定 ===
# 1週間ごとのラベルを「Minor」ではなく「Major」に
ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))

# 1日ごとの補助線だけ残す
ax2.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
ax2.grid(True, which='minor', axis='x', linestyle=':', color='gray', alpha=0.5)

# 日付ラベルのフォントサイズ・回転
plt.setp(ax2.get_xticklabels(), rotation=90, ha='center', fontsize=6)

# === 保存 ===
plt.tight_layout()
out_path = "container_temp_gap_weekly_date_labels.png"
plt.savefig(out_path, dpi=150)
plt.show()

print("✅ グラフ生成完了:", out_path)
