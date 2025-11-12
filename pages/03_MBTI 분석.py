# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from pathlib import Path

st.set_page_config(page_title="Country MBTI Viewer", layout="wide")

st.title("🌍 국가별 MBTI 분포 (Interactive, Plotly + Streamlit)")
st.markdown(
    """
    - 사이드바에서 국가를 선택하면 선택한 국가의 **MBTI 16유형 비율**을 **인터랙티브 막대그래프**로 보여줍니다.
    - **1위(가장 높은 비율)**는 빨간색, 나머지는 파란색 그라데이션으로 표시됩니다.
    - CSV 파일은 앱과 동일한 디렉토리에 `countriesMBTI_16types.csv` (또는 `countriesMBTI_16types (2).csv`)로 두세요.
    """
)

# --- 파일 로드 (여러 이름 후보 허용) ---
candidates = [
    "countriesMBTI_16types.csv",
    "countriesMBTI_16types (2).csv",
    "countriesMBTI_16types (2).CSV",
    "countriesMBTI_16types (2).Csv",
]
df = None
for c in candidates:
    p = Path(c)
    if p.exists():
        df = pd.read_csv(p)
        break

if df is None:
    st.error(
        "데이터 파일을 찾을 수 없습니다. 앱 폴더에 `countriesMBTI_16types.csv` (또는 `countriesMBTI_16types (2).csv`) 를 업로드해주세요."
    )
    st.stop()

# --- 데이터 준비 ---
# 기대: 'Country' 컬럼 포함, 나머지 16개 컬럼은 MBTI 타입에 대한 비율(0~1) 또는 퍼센트(0~100)
if "Country" not in df.columns:
    st.error("CSV에 'Country' 컬럼이 없습니다. 파일을 확인해주세요.")
    st.stop()

# MBTI columns (Country 제외) — 유지된 순서대로 사용
mbti_cols = [c for c in df.columns if c != "Country"]

# convert to numeric (safe)
for c in mbti_cols:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# If values look like proportions (sum ~1), convert to percentages for display.
# Use the first row as a quick heuristic
row0_sum = df.loc[0, mbti_cols].sum()
if 0.9 <= row0_sum <= 1.1:
    df_pct = df.copy()
    df_pct[mbti_cols] = df_pct[mbti_cols] * 100.0
else:
    df_pct = df.copy()

# Sidebar: 국가 선택
countries = sorted(df_pct["Country"].tolist())
default_country = countries[0] if countries else None

st.sidebar.header("Control Panel")
country_selected = st.sidebar.selectbox("국가를 선택하세요", countries, index=countries.index(default_country))
show_raw = st.sidebar.checkbox("원본 데이터 보기 (선택 국가)", value=False)

# Fetch row for selected country
row = df_pct[df_pct["Country"] == country_selected].iloc[0]
vals = row[mbti_cols].astype(float).values
labels = mbti_cols

# Percent formatting for hover/labels
vals_display = np.round(vals, 2)

# Determine colors:
# - 최고값(1등)은 빨간색
# - 나머지는 파란색 그라데이션: 값이 클수록 더 진한(짙은) 파란색
blues = px.colors.sequential.Blues  # from light -> dark
n_shades = len(blues)

# Normalize other values to [0,1] excluding the max index
max_idx = int(np.argmax(vals))
colors = []
# For mapping, avoid setting top to a blue; we set it to red hex.
red_hex = "#e74c3c"  # red for 1등
# For other entries, map normalized value to index in blues
other_vals = np.delete(vals, max_idx)
if other_vals.max() - other_vals.min() == 0:
    # all equal except top (or all equal) -> use medium blue for all non-top
    default_blue = blues[-3] if len(blues) >= 3 else blues[-1]
    for i in range(len(vals)):
        colors.append(red_hex if i == max_idx else default_blue)
else:
    # compute normalization based on min/max of non-top values
    vmin = other_vals.min()
    vmax = other_vals.max()
    for i, v in enumerate(vals):
        if i == max_idx:
            colors.append(red_hex)
        else:
            norm = (v - vmin) / (vmax - vmin) if vmax > vmin else 0.5
            shade_idx = int(norm * (n_shades - 1))
            # ensure using darker tones for larger values:
            colors.append(blues[shade_idx])

# Create Plotly bar chart
fig = go.Figure(
    go.Bar(
        x=labels,
        y=vals_display,
        marker=dict(color=colors, line=dict(color="rgba(0,0,0,0.08)", width=1)),
        hovertemplate="%{x}<br>비율: %{y:.2f}%<extra></extra>",
    )
)

fig.update_layout(
    title=f"{country_selected} — MBTI 분포 (%)",
    xaxis_title="MBTI 유형",
    yaxis_title="비율 (%)",
    yaxis=dict(tickformat=".2f"),
    template="simple_white",
    margin=dict(l=40, r=20, t=80, b=40),
    hovermode="closest",
)

# Show bar with animation-friendly layout
st.plotly_chart(fig, use_container_width=True)

# Display table / extra info
if show_raw:
    st.subheader(f"{country_selected} — 원본 MBTI 비율 (데시멜/퍼센트 형태)")
    st.write(row[mbti_cols].to_frame(name="Value").transpose())

# Bonus: Show top 3 types for the country
sorted_idx = np.argsort(-vals)  # descending
top3 = [(labels[i], vals_display[i]) for i in sorted_idx[:3]]
st.markdown("**Top 3 MBTI for this country:**")
st.write(
    "\n".join([f"{rank+1}. **{t[0]}** — {t[1]:.2f}%" for rank, t in enumerate(top3)])
)

st.markdown("---")
st.caption("앱 제작: Streamlit + Plotly — 색상 규칙: 1등 = 빨강, 나머지 = 파란색 그라데이션")
