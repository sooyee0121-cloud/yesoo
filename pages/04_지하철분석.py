import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="지하철 분석", layout="wide")

st.title("🚇 2025년 10월 지하철 승·하차 분석")

# CSV 불러오기
@st.cache_data
def load_data():
    return pd.read_csv("subway.csv", encoding="cp949")

df = load_data()

# 날짜 필터 (2025년 10월만)
df["사용일자"] = df["사용일자"].astype(str)
df_oct = df[df["사용일자"].str.startswith("202510")]

# 선택 UI
col1, col2 = st.columns(2)

with col1:
    selected_date = st.selectbox(
        "📅 날짜 선택",
        sorted(df_oct["사용일자"].unique())
    )

with col2:
    selected_line = st.selectbox(
        "🚇 호선 선택",
        sorted(df_oct["노선명"].unique())
    )

# 선택 반영한 데이터
filtered = df_oct[
    (df_oct["사용일자"] == selected_date) &
    (df_oct["노선명"] == selected_line)
]

# 승차총승객수 + 하차총승객수 계산
filtered["총이용객"] = filtered["승차총승객수"] + filtered["하차총승객수"]

# 가장 높은 순서대로 정렬
filtered = filtered.sort_values("총이용객", ascending=False)

# 색상 설정: 1등 빨간색, 나머지는 파란색 그라데이션
colors = ["red"] + [
    f"rgba(0,0,255,{0.3 + 0.7 * (i / (len(filtered)-1))})"
    for i in range(len(filtered)-1)
]

# Plotly Bar Chart
fig = px.bar(
    filtered,
    x="역명",
    y="총이용객",
    title=f"{selected_date} · {selected_line} 승·하차 총계 TOP 역",
)

fig.update_traces(marker_color=colors)

fig.update_layout(
    xaxis_title="역명",
    yaxis_title="총 이용객수",
    font=dict(size=16),
    title_x=0.5
)

st.plotly_chart(fig, use_container_width=True)

st.dataframe(filtered[["역명", "총이용객", "승차총승객수", "하차총승객수"]])
