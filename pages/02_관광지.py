# streamlit_app.py
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import webbrowser

st.set_page_config(page_title="Seoul Top10 - Folium Map", layout="wide")

st.title("서울 인기 관광지 Top10 (외국인 선호) — Folium 지도 표시")
st.markdown(
    "아래 마커를 클릭하면 이름과 간단 설명을 볼 수 있습니다. "
    "좌측에서 목록 필터링/확대가 가능합니다."
)

# 데이터: 이름, 위도, 경도, 짧은 설명
places = [
    {"name": "Gyeongbokgung Palace (경복궁)", "lat": 37.5796, "lon": 126.9770,
     "desc": "조선의 대표 궁궐. 광화문/수문장 교대식 등."},
    {"name": "N Seoul Tower (남산타워)", "lat": 37.5512, "lon": 126.9882,
     "desc": "서울 중심 전망대 — 야경 명소."},
    {"name": "Myeongdong (명동)", "lat": 37.5638, "lon": 126.9850,
     "desc": "쇼핑·스트리트푸드의 중심지."},
    {"name": "Bukchon Hanok Village (북촌한옥마을)", "lat": 37.5826, "lon": 126.9830,
     "desc": "전통 한옥 거리와 포토 스팟."},
    {"name": "Hongdae (홍대)", "lat": 37.5563, "lon": 126.9220,
     "desc": "젊음의 거리, 공연·카페·클럽 문화."},
    {"name": "Itaewon (이태원)", "lat": 37.5346, "lon": 126.9946,
     "desc": "다양한 외국 식당과 밤문화."},
    {"name": "Dongdaemun Design Plaza (동대문 DDP)", "lat": 37.5663, "lon": 127.0090,
     "desc": "현대적 디자인 랜드마크·야시장 인접."},
    {"name": "Insadong (인사동)", "lat": 37.5740, "lon": 126.9852,
     "desc": "전통 공예·찻집 골목."},
    {"name": "Lotte World Tower / Jamsil (롯데월드타워)", "lat": 37.5131, "lon": 127.1019,
     "desc": "서울 최고층 타워·몰·전망대."},
    {"name": "Hangang Park (한강공원, Yeouido 포함)", "lat": 37.5269, "lon": 126.9241,
     "desc": "한강변에서 자전거·피크닉·야경을 즐길 수 있음."}
]

df = pd.DataFrame(places)

# 사이드바: 리스트와 선택
st.sidebar.header("관광지 목록")
selected = st.sidebar.multiselect(
    "표시할 장소를 선택하세요 (모두 선택하면 전체 표시)", options=df["name"].tolist(), default=df["name"].tolist()
)

zoom = st.sidebar.slider("초기 확대 레벨 (zoom)", min_value=10, max_value=16, value=12)
map_width = st.sidebar.number_input("지도 너비(px)", value=900)
map_height = st.sidebar.number_input("지도 높이(px)", value=600)

# 초기 중심 계산: 선택한 항목의 평균 위치
if len(selected) == 0:
    st.warning("사이드바에서 최소 한 곳을 선택하세요.")
else:
    sel_df = df[df["name"].isin(selected)]
    center_lat = sel_df["lat"].mean()
    center_lon = sel_df["lon"].mean()

    # Folium 맵 생성
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom)

    # 마커 추가
    for _, row in sel_df.iterrows():
        popup_html = f"<b>{row['name']}</b><br/>{row['desc']}"
        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=row["name"],
        ).add_to(m)

    # 지도 렌더링
    st_data = st_folium(m, width=map_width, height=map_height)

    # 아래에 테이블로 정보 출력
    with st.expander("선택된 관광지 정보 보기"):
        st.dataframe(sel_df.reset_index(drop=True))

    st.markdown("---")
    st.caption("데이터 출처 예시: VisitSeoul, Tripadvisor, KoreaToDo 등(종합).")
