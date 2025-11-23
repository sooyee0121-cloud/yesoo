import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="국가별 우세 혈액형 분석", layout="wide")

st.title("🩸 국가별 우세 혈액형 분석")

st.markdown("""
CSV를 업로드하거나 GitHub RAW URL을 입력해 국가별 우세 혈액형을 분석하는 앱입니다.  
""")

# ----------------------------
# 데이터 로드 함수
# ----------------------------
def load_data_from_github(url):
    try:
        return pd.read_csv(url)
    except:
        st.error("⚠️ GitHub RAW URL에서 데이터를 불러오지 못했습니다.")
        return None

def load_uploaded_file(file):
    try:
        return pd.read_csv(file)
    except:
        st.error("⚠️ CSV 파일을 불러오지 못했습니다.")
        return None

# ----------------------------
# 사이드바 입력
# ----------------------------
st.sidebar.header("데이터 입력")

upload_file = st.sidebar.file_uploader("CSV 업로드", type=["csv"])
github_url = st.sidebar.text_input("GitHub RAW CSV URL")
sample_btn = st.sidebar.button("샘플 데이터 불러오기")

# ----------------------------
# 데이터 로드
# ----------------------------
df = None

if upload_file:
    df = load_uploaded_file(upload_file)
elif github_url:
    df = load_data_from_github(github_url)
elif sample_btn:
    df = pd.DataFrame({
        "country": ["Korea", "Korea", "Korea", "Japan", "Japan", "USA"],
        "blood_type": ["A", "O", "B", "A", "O", "O"]
    })
    st.success("샘플 데이터를 불러왔습니다!")

# ----------------------------
# 데이터 있으면 분석 시작
# ----------------------------
if df is not None:

    # 컬럼 정리
    df.columns = df.columns.str.lower().str.strip()

    if "country" not in df.columns or "blood_type" not in df.columns:
        st.error("❌ CSV 컬럼 이름은 반드시 country, blood_type 이어야 합니다.")
        st.stop()

    df["country"] = df["country"].astype(str).str.strip()
    df["blood_type"] = df["blood_type"].astype(str).str.upper().str.strip()

    # ----------------------------
    # ✔ 국가별 요약 테이블 (중복 국가 제거해 깔끔하게 표시)
    # ----------------------------
    st.subheader("📄 국가별 데이터 요약 (중복 제거 버전)")

    summary = (
        df.groupby("country")["blood_type"]
        .count()
        .reset_index(name="total_records")
        .sort_values("total_records", ascending=False)
    )

    st.dataframe(summary, use_container_width=True)

    # ----------------------------
    # 혈액형 개수 집계
    # ----------------------------
    count_df = df.groupby(["country", "blood_type"]).size().reset_index(name="count")

    # ----------------------------
    # 우세 혈액형 계산
    # ----------------------------
    dominant_df = count_df.loc[count_df.groupby("country")['count'].idxmax()]
    dominant_df = dominant_df.sort_values("count", ascending=False)

    st.subheader("🏆 국가별 우세 혈액형")
    st.dataframe(dominant_df, use_container_width=True)

    # ----------------------------
    # 막대그래프
    # ----------------------------
    st.subheader("📊 국가별 우세 혈액형 (막대그래프)")

    fig = px.bar(
        dominant_df,
        x="country",
        y="count",
        color="blood_type",
        text="blood_type",
        title="국가별 우세 혈액형 개수",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(xaxis_title="국가", yaxis_title="해당 혈액형 개수")

    st.plotly_chart(fig, use_container_width=True)

    # ----------------------------
    # 특정 국가 혈액형 비율 분석
    # ----------------------------
    st.subheader("🔍 특정 국가 혈액형 비율 분석")

    countries = sorted(df["country"].unique())
    selected_country = st.selectbox("국가 선택", countries)

    country_data = df[df["country"] == selected_country]

    pie_df = country_data["blood_type"].value_counts().reset_index()
    pie_df.columns = ["blood_type", "count"]

    fig2 = px.pie(
        pie_df,
        names="blood_type",
        values="count",
        title=f"{selected_country} 혈액형 비율"
    )
    st.plotly_chart(fig2, use_container_width=True)

else:
    st.info("👉 데이터를 업로드하거나 GitHub RAW URL을 입력해주세요.")

