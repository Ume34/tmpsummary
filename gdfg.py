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

# === 差分計算 ===
df_interp["Gap1_C1-Air"] = df_interp[col_c1] - df_interp[col_air]
df_interp["Gap2_C2-Air"] = df_interp[col_c2] - df_interp[col_air]

# === グラフ描画 ===
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})

# --- 上段：温度 ---
ax1.plot(df_interp.index, df_interp[col_air],
         label="Ambient (Interpolated)",
         linestyle="--", color="gray", linewidth=1.2)

ax1.plot(df_interp.index, df_interp[col_c1],
         label="Container 1 (Measured)",
         color="tab:red", linewidth=1.8)

ax1.plot(df_interp.index, df_interp[col_c2],
         label="Container 2 (Measured)",
         color="tab:purple", linewidth=1.8, linestyle="-.")

ax1.set_ylabel("Temperature (°C)")
ax1.set_title("Container vs Ambient Temperature (Weekly Date Labels)")
ax1.legend(loc="upper left")
ax1.grid(True)

# --- 下段：ギャップ ---
bar_width = 0.02
ax2.bar(df_interp.index,
        df_interp["Gap1_C1-Air"],
        width=bar_width,
        label="Gap 1 (C1 - Air)",
        color="tab:red",
        alpha=0.7,
        edgecolor="black",
        linewidth=0.3)

ax2.bar(df_interp.index,
        df_interp["Gap2_C2-Air"],
        width=bar_width,
        label="Gap 2 (C2 - Air)",
        color="tab:blue",
        alpha=0.7,
        edgecolor="black",
        linewidth=0.3)

ax2.set_ylabel("Δ Temp (°C)")
ax2.set_title("Temperature Gap (Measured - Interpolated Ambient)")
ax2.legend(loc="upper left")
ax2.grid(True)

# === 横軸設定 ===
# 1週間ごとの日付ラベル
ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))

# 1日ごとの補助線
ax2.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
ax2.grid(True, which='minor', axis='x', linestyle=':', color='gray', alpha=0.5)

# ラベルを小さく・縦書き
plt.setp(ax2.get_xticklabels(), rotation=90, ha='center', fontsize=6)

# === レイアウトと保存 ===
plt.tight_layout()
out_fig = "container_temp_gap_color_improved.png"
plt.savefig(out_fig, dpi=150)
plt.show()

print(f"✅ グラフ生成完了: {out_fig}")

# === CSVに出力 ===
out_csv = "temperature_gap_output.csv"
df_export = df_interp.reset_index()
df_export.to_csv(out_csv, index=False, encoding='utf-8-sig')  # Excel対応BOM付き
print(f"✅ CSV出力完了: {out_csv}")

