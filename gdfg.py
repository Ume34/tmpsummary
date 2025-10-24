import pandas as pd
import numpy as np
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

# === データ補間（大気温） ===
df_raw = df.set_index("Timestamp_fixed")
df_interp = df_raw.copy()
df_interp[col_air] = df_interp[col_air].interpolate(method='time', limit_direction='both')

# === ギャップ計算 ===
df_interp["Gap1_C1-Air"] = df_interp[col_c1] - df_interp[col_air]
df_interp["Gap2_C2-Air"] = df_interp[col_c2] - df_interp[col_air]

# === Excel出力 + グラフ埋め込み ===
out_xlsx = "container_temp_chart.xlsx"
with pd.ExcelWriter(out_xlsx, engine='xlsxwriter') as writer:
    df_reset = df_interp.reset_index()
    df_reset.to_excel(writer, sheet_name='Data', index=False)
    workbook = writer.book
    worksheet = writer.sheets['Data']

    # 折れ線グラフ（温度）
    chart = workbook.add_chart({'type': 'line'})

    # Ambient
    chart.add_series({
        'name':       'Ambient',
        'categories': ['Data', 1, 0, len(df_reset), 0],
        'values':     ['Data', 1, 3, len(df_reset), 3],
        'line':       {'color': 'gray', 'dash_type': 'dash'}
    })

    # Container 1
    chart.add_series({
        'name':       'Container 1',
        'categories': ['Data', 1, 0, len(df_reset), 0],
        'values':     ['Data', 1, 1, len(df_reset), 1],
        'line':       {'color': 'red', 'width': 2}
    })

    # Container 2
    chart.add_series({
        'name':       'Container 2',
        'categories': ['Data', 1, 0, len(df_reset), 0],
        'values':     ['Data', 1, 2, len(df_reset), 2],
        'line':       {'color': 'purple', 'width': 2, 'dash_type': 'dot'}
    })

    chart.set_title({'name': 'Container vs Ambient Temperature'})
    chart.set_x_axis({'name': 'Timestamp'})
    chart.set_y_axis({'name': 'Temperature (°C)'})
    chart.set_legend({'position': 'top'})

    # 棒グラフ（Gap）
    chart2 = workbook.add_chart({'type': 'column'})

    chart2.add_series({
        'name':       'Gap 1',
        'categories': ['Data', 1, 0, len(df_reset), 0],
        'values':     ['Data', 1, 6, len(df_reset), 6],
        'fill':       {'color': 'red'},
        'border':     {'color': 'black'}
    })

    chart2.add_series({
        'name':       'Gap 2',
        'categories': ['Data', 1, 0, len(df_reset), 0],
        'values':     ['Data', 1, 7, len(df_reset), 7],
        'fill':       {'color': 'blue'},
        'border':     {'color': 'black'}
    })

    chart2.set_title({'name': 'Temperature Gap'})
    chart2.set_x_axis({'name': 'Timestamp'})
    chart2.set_y_axis({'name': 'Δ Temp (°C)'})
    chart2.set_legend({'position': 'top'})

    # Excelシートにグラフを配置
    worksheet.insert_chart('K2', chart, {'x_scale': 2.0, 'y_scale': 1.3})
    worksheet.insert_chart('K25', chart2, {'x_scale': 2.0, 'y_scale': 1.3})

print(f"✅ Excelファイルにグラフを埋め込みました: {out_xlsx}")


