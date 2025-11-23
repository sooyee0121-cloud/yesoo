import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="한국 관광지 정보", layout="wide")

st.title("🏞️ 한국 관광지 정보 대시보드")
st.write("한국관광 100선을 기반으로 만든 관광지 검색 및 시각화 앱입니다.")

# 관광지 기본 데이터 (원하면 실제 목록으로 모두 교체해 줄게)
tour_list = [
    {"region": "서울", "name": "경복궁", "type": "역사"},
    {"region": "서울", "name": "남산타워", "type": "도시"},
    {"region": "부산", "name": "해운대해수욕장", "type": "해변"},
    {"region": "경주", "name": "불국사", "type": "역사"},
    {"region": "제주", "name": "성산일출봉", "type": "자연"},
    {"region": "전주", "name": "한옥마을", "type": "전통"},
    {"region": "강원", "name": "속초 설악산", "type": "산"},
]

df = pd.DataFrame(tour_list)

# -------------------------------------
# 관광지 이미지 경로 설정 (GitHub Raw 경로 이용)
# -------------------------------------
st.sidebar.header("📁 이미지 경로 설정")
base_url = st.sidebar.text_input(
    "GitHub Raw 이미지 폴더 URL 입력",
    "https://raw.githubusercontent.com/사용자명/레포명/main/images/"
)

st.sidebar.write("예시: `https://raw.githubusercontent.com/suye/test/main/images/`")

# 관광지 선택 박스
st.subheader("🔎 관광지 검색")
selected = st.selectbox("관광지를 선택하세요", df["name"])

row = df[df["name"] == selected].iloc[0]

st.write(f"### 📍 {row['name']}")
st.write(f"- 지역: **{row['region']}**")
st.write(f"- 분류: **{row['type']}**")

# 이미지 표시
image_url = base_url + row["name"] + ".png"
st.image(image_url, caption=row["name"], use_container_width=True)

# -------------------------------------
# 시각화: 지역별 관광지 수 막대그래프
# -------------------------------------
st.subheader("📊 지역별 관광지 개수")

region_count = df["region"].value_counts().reset_index()
region_count.columns = ["region", "count"]

fig = px.bar(
    region_count,
    x="region",
    y="count",
    title="지역별 관광지 수",
    text="count"
)
fig.update_traces(textposition="outside")
st.plotly_chart(fig, use_container_width=True)

# -------------------------------------
# 시각화: 관광지 분류 비율
# -------------------------------------
st.subheader("🧭 관광지 분류 비율")

type_count = df["type"].value_counts().reset_index()
type_count.columns = ["type", "count"]

fig2 = px.pie(
    type_count,
    names="type",
    values="count",
    title="관광지 종류 비율"
)
st.plotly_chart(fig2, use_container_width=True)
