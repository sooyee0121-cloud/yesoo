# streamlit_app.py
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import math

st.set_page_config(page_title="Seoul Top10 - Folium Map", layout="wide")

st.title("서울 인기 관광지 Top10 (외국인 선호) — 지하철 & 일정표 포함")
st.markdown(
    "🔎 외국인에게 인기 있는 서울 명소 10곳을 지도에 표시합니다.<br>"
    "📍 각 명소에는 **가까운 지하철역과 노선 정보**가 포함되어 있으며,<br>"
    "🗓️ 하단에서 여행 일수를 선택하면 **자동 일정표**가 생성됩니다.",
    unsafe_allow_html=True
)

# ----------------------------
# 데이터: 관광지 + 지하철 정보
# ----------------------------
places = [
    {"name": "Gyeongbokgung Palace (경복궁)", "lat": 37.5796, "lon": 126.9770,
     "desc": "조선의 대표 궁궐, 광화문과 수문장 교대식이 유명함.",
     "subway": "3호선 경복궁역"},
    {"name": "N Seoul Tower (남산타워)", "lat": 37.5512, "lon": 126.9882,
     "desc": "서울 중심 전망대, 야경 명소로 유명함.",
     "subway": "4호선 명동역"},
    {"name": "Myeongdong (명동)", "lat": 37.5638, "lon": 126.9850,
     "desc": "쇼핑과 길거리 음식의 중심지.",
     "subway": "4호선 명동역"},
    {"name": "Bukchon Hanok Village (북촌한옥마을)", "lat": 37.5826, "lon": 126.9830,
     "desc": "전통 한옥 거리와 포토 스팟.",
     "subway": "3호선 안국역"},
    {"name": "Hongdae (홍대)", "lat": 37.5563, "lon": 126.9220,
     "desc": "젊음의 거리, 예술·음악·카페 문화가 활발한 지역.",
     "subway": "2호선 홍대입구역"},
    {"name": "Itaewon (이태원)", "lat": 37.5346, "lon": 126.9946,
     "desc": "다양한 외국 식당과 밤문화가 공존하는 거리.",
     "subway": "6호선 이태원역"},
    {"name": "Dongdaemun Design Plaza (동대문 DDP)", "lat": 37.5663, "lon": 127.0090,
     "desc": "현대적 디자인 랜드마크, 패션·야시장 중심지.",
     "subway": "2·4·5호선 동대문역사문화공원역"},
    {"name": "Insadong (인사동)", "lat": 37.5740, "lon": 126.9852,
     "desc": "전통 공예품과 찻집이 즐비한 거리.",
     "subway": "3호선 안국역"},
    {"name": "Lotte World Tower (롯데월드타워)", "lat": 37.5131, "lon": 127.1019,
     "desc": "서울 최고층 타워, 쇼핑몰·전망대 포함.",
     "subway": "2호선 잠실역"},
    {"name": "Hangang Park (한강공원, 여의도)", "lat": 37.5269, "lon": 126.9241,
     "desc": "한강변에서 자전거와 피크닉을 즐길 수 있음.",
     "subway": "5호선 여의나루역"}
]

df = pd.DataFrame(places)

# ----------------------------
# 지도 표시
# ----------------------------
center_lat = df["lat"].mean()
center_lon = df["lon"].mean()

m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

for _, row in df.iterrows():
    popup_html = f"""
    <b>{row['name']}</b><br>
    🚇 {row['subway']}<br>
    {row['desc']}
    """
    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=row["name"],
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

st.markdown("<div style='width:70%; margin:auto;'>", unsafe_allow_html=True)
st_folium(m, width=900, height=500)
st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# 하단: 관광지 간략 요약
# ----------------------------
st.subheader("📍 관광지 요약 정보 (지하철 포함)")
for i, row in enumerate(df.itertuples(), 1):
    st.markdown(f"**{i}. {row.name}** — {row.desc}  \n🚇 {row.subway}")

# ----------------------------
# 여행 일정 생성 기능
# ----------------------------
st.markdown("---")
st.subheader("🗓️ 나만의 서울 여행 일정 만들기")

days = st.slider("여행 일수를 선택하세요 (1~3일)", 1, 3, 2)
places_per_day = math.ceil(len(df) / days)

st.write(f"👉 총 {days}일 동안 {len(df)}곳을 방문하는 일정입니다:")

schedule = {}
for day in range(1, days + 1):
    start = (day - 1) * places_per_day
    end = start + places_per_day
    schedule[day] = df.iloc[start:end]

for day, subset in schedule.items():
    st.markdown(f"### Day {day}")
    for i, row in enumerate(subset.itertuples(), 1):
        st.markdown(f"- **{row.name}** — {row.desc} (🚇 {row.subway})")

st.caption("일정은 이동 동선보다는 관광지 분포 기준으로 균등 배분됩니다.")
