# app.py
import streamlit as st
import pandas as pd
import io
import plotly.express as px

st.set_page_config(page_title="나라별 우세 혈액형", layout="wide")

st.title("🌍 나라별 가장 많은 혈액형 (Most common blood type by country)")

st.markdown("""
앱 기능:
- 로컬 CSV 업로드 또는 GitHub raw URL 입력으로 데이터 불러오기
- 국가별 혈액형 개수 집계 및 비율 계산
- 각 국가의 **가장 많은 혈액형(우세 혈액형)** 표시
- 상위 N개 국가를 막대그래프 / 표로 표시
- 필요시 간단한 지도 시각화(국가명 ISO 매핑이 필요)
""")

# --- 입력 섹션 ---
st.sidebar.header("데이터 입력")
data_source = st.sidebar.radio("데이터 불러오기 방식", ("파일 업로드", "GitHub raw CSV URL", "샘플 데이터 사용"))

def load_sample():
    csv = """country,blood_type
South Korea,A
South Korea,A
South Korea,O
Japan,A
Japan,A
Japan,B
USA,O
USA,A
USA,O
India,B
India,O
India,B
Brazil,O
Brazil,O
Brazil,A
"""
    return pd.read_csv(io.StringIO(csv))

df = None
if data_source == "파일 업로드":
    uploaded_file = st.sidebar.file_uploader("CSV 파일 업로드", type=["csv"])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
        except Exception as e:
            st.sidebar.error(f"CSV 로드 실패: {e}")
elif data_source == "GitHub raw CSV URL":
    url = st.sidebar.text_input("GitHub raw CSV URL (예: https://raw.githubusercontent.com/사용자/레포/브랜치/파일.csv)")
    if url:
        try:
            df = pd.read_csv(url)
        except Exception as e:
            st.sidebar.error(f"URL에서 CSV 로드 실패: {e}")
else:
    df = load_sample()

# --- 데이터 기본 검사 / 정리 ---
if df is None:
    st.info("왼쪽 사이드바에서 CSV를 업로드하거나 GitHub raw URL을 입력하거나 샘플을 선택하세요.")
    st.stop()

st.subheader("원본 데이터 (미리보기)")
st.write("데이터의 첫 10행을 확인하세요. 필요한 컬럼: `country`, `blood_type` (대/소문자 무관)")
st.dataframe(df.head(10))

# 표준화: 컬럼 이름 소문자화, 공백 제거
df.columns = [c.strip() for c in df.columns]
lower_cols = {c: c.lower() for c in df.columns}
df = df.rename(columns=lower_cols)

if 'country' not in df.columns or 'blood_type' not in df.columns:
    st.error("CSV에 `country`와 `blood_type` 컬럼이 반드시 있어야 합니다. (예: country,blood_type)")
    st.stop()

# 정리
df['country'] = df['country'].astype(str).str.strip()
df['blood_type'] = df['blood_type'].astype(str).str.strip().str.upper()

# 필터/파라미터
st.sidebar.header("표시 옵션")
top_n = st.sidebar.number_input("상위 N개 국가 표시", min_value=1, max_value=200, value=20)
show_map = st.sidebar.checkbox("지도 표시 (국가명->ISO 매핑 필요)", value=False)

# --- 집계: 국가별 혈액형 카운트 & 우세 혈액형 ---
counts = df.groupby(['country', 'blood_type']).size().reset_index(name='count')
# pivot for percentages
total_by_country = counts.groupby('country', as_index=False)['count'].sum().rename(columns={'count':'total'})
counts = counts.merge(total_by_country, on='country')
counts['pct'] = counts['count'] / counts['total'] * 100

# 우세 혈액형 선택
idx = counts.groupby('country')['count'].idxmax()
dominant = counts.loc[idx].reset_index(drop=True).sort_values(by='count', ascending=False)
dominant = dominant[['country','blood_type','count','total','pct']]
dominant = dominant.rename(columns={
    'blood_type':'dominant_blood_type',
    'count':'dominant_count',
    'total':'total_count',
    'pct':'dominant_pct'
})

st.subheader("국가별 우세 혈액형 (정렬된 상위 국가)")
st.write(f"총 국가 수: {dominant['country'].nunique()}")
st.dataframe(dominant.head(top_n).style.format({'dominant_pct':'{:.1f}%'}))

# --- 그래프: 상위 N개 국가 막대그래프 ---
st.subheader(f"상위 {top_n}개 국가의 우세 혈액형 (빈도 순)")
plot_df = dominant.sort_values(by='dominant_count', ascending=False).head(top_n)
fig = px.bar(plot_df, x='country', y='dominant_count', color='dominant_blood_type',
             labels={'dominant_count':'우세 혈액형 보유 수', 'country':'국가'},
             hover_data=['dominant_pct','total_count'])
fig.update_layout(xaxis_tickangle=-45, legend_title_text='우세 혈액형')
st.plotly_chart(fig, use_container_width=True)

# --- 자세히 보기: 특정 국가 상세 ---
st.subheader("특정 국가의 혈액형 분포 보기")
country_selected = st.selectbox("국가 선택", sorted(df['country'].unique()))
dist = counts[counts['country'] == country_selected].sort_values(by='count', ascending=False)
st.write(dist[['blood_type','count','pct']].reset_index(drop=True).style.format({'pct':'{:.1f}%'}))
fig2 = px.pie(dist, names='blood_type', values='count', title=f"{country_selected} - 혈액형 분포")
st.plotly_chart(fig2, use_container_width=True)

# --- (선택) 지도: 사용자에게 ISO 매핑 필요 ---
if show_map:
    st.subheader("지도 시각화 (주의: 국가명→ISO 매핑 필요)")
    st.info("모든 국가가 정확히 매핑되지 않을 수 있습니다. 정확한 지도를 원하면 country 컬럼에 ISO 3166-1 alpha-3 코드를 추가하거나 직접 매핑하세요.")
    # 시도: pycountry로 alpha_3 매핑 (pycountry가 설치되어 있으면 작동)
    try:
        import pycountry
        def country_to_iso3(name):
            try:
                return pycountry.countries.lookup(name).alpha_3
            except Exception:
                return None
        plot_df['iso_a3'] = plot_df['country'].apply(country_to_iso3)
        map_df = plot_df.dropna(subset=['iso_a3'])
        if map_df.empty:
            st.warning("매핑 가능한 국가가 없습니다.")
        else:
            map_df['text'] = map_df['country'] + ": " + map_df['dominant_blood_type'] + " (" + map_df['dominant_count'].astype(str)+")"
            fig_map = px.choropleth(map_df, locations="iso_a3", color="dominant_blood_type",
                                    hover_name="text", title="우세 혈액형(지도)")
            st.plotly_chart(fig_map, use_container_width=True)
    except Exception as e:
        st.error("지도 표시를 위해 `pycountry`가 필요합니다. requirements.txt에 추가하고 재시작하세요. 오류: " + str(e))

# --- 다운로드 ---
st.subheader("결과 다운로드")
csv_bytes = dominant.to_csv(index=False).encode('utf-8')
st.download_button("우세 혈액형 결과 CSV 다운로드", data=csv_bytes, file_name="dominant_blood_types_by_country.csv", mime="text/csv")

st.success("완료! CSV 포맷/데이터가 다르면 앱이 못 읽을 수 있으니, 아래 샘플 포맷을 확인하세요.")
