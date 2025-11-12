import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from pathlib import Path

st.set_page_config(page_title="Country MBTI Dashboard", layout="wide")

st.title("🌍 국가별 MBTI 시각화 대시보드")
st.markdown(
    """
    이 앱은 전 세계 158개국의 MBTI 유형 비율 데이터를 시각화합니다.  
    아래 탭을 전환해 보세요:
    1️⃣ **국가별 MBTI 분포 보기**  
    2️⃣ **MBTI 유형별 상위 국가 보기**
    """
)

# --- CSV 파일 로드 ---
candidates = [
    "countriesMBTI_16types.csv",
    "countriesMBTI_16types (2).csv",
]
df = None
for c in candidates:
    p = Path(c)
    if p.exists():
        df = pd.read_csv(p)
        break

if df is None:
    st.error("❌ 데이터 파일을 찾을 수 없습니다. CSV 파일을 앱 폴더에 넣어주세요.")
    st.stop()

if "Country" not in df.columns:
    st.error("❌ CSV에 'Country' 컬럼이 없습니다.")
    st.stop()

mbti_cols = [c for c in df.columns if c != "Country"]
for c in mbti_cols:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# 비율(0~1)형태라면 퍼센트 변환
if 0.9 <= df.loc[0, mbti_cols].sum() <= 1.1:
    df[mbti_cols] *= 100

# --- 탭 구성 ---
tab1, tab2 = st.tabs(["📊 국가별 MBTI 분포", "🌎 MBTI 유형별 상위 국가"])

# --------------------------------------------------------------------
# TAB 1: 국가 선택 → MBTI 분포 보기
# --------------------------------------------------------------------
with tab1:
    st.subheader("📊 국가별 MBTI 비율 보기")

    country_selected = st.selectbox("국가를 선택하세요", sorted(df["Country"].tolist()))
    row = df[df["Country"] == country_selected].iloc[0]
    vals = row[mbti_cols].astype(float).values
    labels = mbti_cols
    vals_display = np.round(vals, 2)
    max_idx = int(np.argmax(vals))

    # 색상: 1등은 빨강, 나머지는 파란색(값이 높을수록 밝게)
    blues = px.colors.sequential.Blues
    n_shades = len(blues)
    red_hex = "#e74c3c"
    colors = []
    other_vals = np.delete(vals, max_idx)

    if other_vals.max() - other_vals.min() == 0:
        default_blue = blues[-3]
        for i in range(len(vals)):
            colors.append(red_hex if i == max_idx else default_blue)
    else:
        vmin, vmax = other_vals.min(), other_vals.max()
        for i, v in enumerate(vals):
            if i == max_idx:
                colors.append(red_hex)
            else:
                norm = (v - vmin) / (vmax - vmin)
                shade_idx = int((1 - norm) * (n_shades - 1))  # ✅ 반전: 값이 높을수록 밝은 파랑
                colors.append(blues[shade_idx])

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
        template="simple_white",
        margin=dict(l=40, r=20, t=80, b=40),
    )

    st.plotly_chart(fig, use_container_width=True)

    # Top 3 표시
    sorted_idx = np.argsort(-vals)
    top3 = [(labels[i], vals_display[i]) for i in sorted_idx[:3]]
    st.markdown("**🏆 Top 3 MBTI 유형:**")
    for i, (t, v) in enumerate(top3, start=1):
        st.write(f"{i}. **{t}** — {v:.2f}%")

# --------------------------------------------------------------------
# TAB 2: MBTI 유형 선택 → 상위 국가 그래프
# --------------------------------------------------------------------
with tab2:
    st.subheader("🌎 MBTI 유형별 상위 10개국 보기")

    mbti_selected = st.selectbox("MBTI 유형을 선택하세요", mbti_cols, index=0)

    sorted_df = df[["Country", mbti_selected]].sort_values(by=mbti_selected, ascending=False)
    top10 = sorted_df.head(10).copy()

    # 한국이 포함되어 있는지 확인
    korea_mask = sorted_df["Country"].str.lower().str.contains("korea")
    korea_row = sorted_df[korea_mask]
    if not korea_row.empty:
        korea_row = korea_row.iloc[[0]]
        if korea_row["Country"].values[0] not in top10["Country"].values:
            top10 = pd.concat([top10, korea_row])

    # 색상 지정
    blues = px.colors.sequential.Blues[::-1]  # ✅ 값이 높을수록 진한 파랑
    n_shades = len(blues)
    vals = top10[mbti_selected].values
    vmin, vmax = vals.min(), vals.max()

    colors = []
    for _, r in top10.iterrows():
        country = r["Country"]
        if "korea" in country.lower():
            colors.append("#ff4d4d")  # 한국은 밝은 빨강
        else:
            norm = (r[mbti_selected] - vmin) / (vmax - vmin)
            shade_idx = int(norm * (n_shades - 1))
            colors.append(blues[shade_idx])

    fig2 = go.Figure(
        go.Bar(
            x=top10["Country"],
            y=top10[mbti_selected],
            marker=dict(color=colors, line=dict(color="rgba(0,0,0,0.08)", width=1)),
            hovertemplate="%{x}<br>%{y:.2f}%<extra></extra>",
        )
    )
    fig2.update_layout(
        title=f"{mbti_selected} 유형이 높은 국가 TOP 10 (+한국)",
        xaxis_title="국가",
        yaxis_title=f"{mbti_selected} 비율 (%)",
        template="simple_white",
        margin=dict(l=40, r=20, t=80, b=40),
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.caption("🔹 한국은 빨간색으로 표시됩니다.")
