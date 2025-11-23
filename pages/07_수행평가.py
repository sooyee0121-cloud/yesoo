import streamlit as st
import pandas as pd
import plotly.express as px
import io

st.set_page_config(page_title="나라별 우세 혈액형 분석", layout="wide")

st.title("🩸 나라별 가장 많은 혈액형 분석 대시보드")

st.markdown("""
이 앱은 **나라별 우세 혈액형을 자동으로 계산하고 시각화**합니다.  
CSV 업로드 전에도 샘플 데이터로 **바로 그래프를 볼 수 있습니다.**

### ✨ 기능
- CSV 파일 업로드 또는 GitHub RAW CSV URL 입력
- 나라별 혈액형 개수 & 비율 자동 계산
- 가장 많은 혈액형(우세 혈액형) 자동 탐색
- 상위 N개 국가 막대그래프
- 선택한 국가의 파이차트
- 결과 다운로드 (CSV)
""")

# ---------------- 샘플 데이터 ----------------
def load_sample_data():
    csv = """country,blood_type
South Korea,A
South Korea,A
South Korea,O
Japan,A
Japan,B
Japan,A
USA,O
USA,O
USA,A
India,B
India,O
India,B
Brazil,O
Brazil,O
Brazil,A
"""
    return pd.read_csv(io.StringIO(csv))

# ---------------- 데이터 입력 ----------------
st.sidebar.header("데이터 입력 방식")

choice = st.sidebar.radio("데이터 선택", ["샘플 데이터 사용", "파일 업로드", "GitHub RAW URL"])

df = None

if choice == "샘플 데이터 사용":
    df = load_sample_data()

elif choice == "파일 업로드":
    uploaded = st.sidebar.file_uploader("CSV 파일 업로드", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)

elif choice == "GitHub RAW URL":
    url = st.sidebar.text_input("RAW CSV URL 입력")
    if url:
        try:
            df = pd.read_csv(url)
        except:
            st.sidebar.error("CSV 파일을 불러올 수 없습니다. URL을 확인하세요.")

# ---------------- 데이터 없으면 안내 ----------------
if df is None:
    st.warning("📌 왼쪽에서 CSV를 업로드하거나 URL을 입력하거나 샘플 데이터를 선택하세요.")
    st.stop()

# ---------------- 데이터 정리 ----------------
df.columns = df.columns.str.lower().str.strip()
df["country"] = df["country"].astype(str)
df["blood_type"] = df["blood_type"].astype(str).str.upper().str.strip()

st.subheader("📄 데이터 미리보기")
st.dataframe(df.head())

# ---------------- 국가별 혈액형 집계 ----------------
counts = (
    df.groupby(["country", "blood_type"])
    .size()
    .reset_index(name="count")
)

total = counts.groupby("country")["count"].sum().reset_index(name="total_count")
counts = counts.merge(total, on="country")
counts["pct"] = counts["count"] / counts["total_count"] * 100

# ---------------- 우세 혈액형 계산 ----------------
idx = counts.groupby("country")["count"].idxmax()
dominant = counts.loc[idx].copy()
dominant = dominant.sort_values("count", ascending=False)
dominant = dominant.rename(columns={
    "blood_type": "dominant_blood_type",
    "count": "dominant_count",
    "pct": "dominant_pct"
})

# ---------------- 상위 N개 국가 ----------------
st.sidebar.header("그래프 옵션")
top_n = st.sidebar.slider("표시할 국가 수", 5, 50, 15)

top_df = dominant.head(top_n)

# ---------------- 막대그래프 ----------------
st.subheader("📊 나라별 우세 혈액형 (막대그래프)")
fig = px.bar(
    top_df,
    x="country",
    y="dominant_count",
    color="dominant_blood_type",
    title="상위 국가 우세 혈액형",
    labels={"dominant_count": "우세 혈액형 수"},
)
fig.update_layout(xaxis_tickangle=-40)
st.plotly_chart(fig, use_container_width=True)

# ---------------- 상세 국가 선택 ----------------
st.subheader("🔍 특정 국가 혈액형 비율")
selected_country = st.selectbox("국가 선택", sorted(df["country"].unique()))

detail = counts[counts["country"] == selected_country]

fig2 = px.pie(
    detail,
    names="blood_type",
    values="count",
    title=f"{selected_country}의 혈액형 비율"
)
st.plotly_chart(fig2, use_container_width=True)

# ---------------- 결과 다운로드 ----------------
st.subheader("⬇ 결과 다운로드")
csv_data = dominant.to_csv(index=False).encode("utf-8")
st.download_button(
    "우세 혈액형 결과 CSV 다운로드",
    csv_data,
    "dominant_blood_types.csv",
    "text/csv"
)

st.success("분석 완료! 필요하면 그래프 스타일도 커스터마이징해줄게 😊")
