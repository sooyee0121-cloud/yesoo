import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="국가별 우세 혈액형 분석", layout="wide")

st.title("🌍 국가별 우세 혈액형 분석 앱")
st.markdown("CSV를 업로드하거나 GitHub Raw URL을 입력해주세요.")

# =======================
# 데이터 로드 함수
# =======================
def load_data_from_github(url):
    try:
        return pd.read_csv(url)
    except:
        st.error("⚠️ GitHub Raw URL을 불러오지 못했습니다.")
        return None


def load_uploaded_file(file):
    try:
        return pd.read_csv(file)
    except:
        st.error("⚠️ CSV 파일을 불러오지 못했습니다.")
        return None


# =======================
# 사이드바 입력
# =======================
st.sidebar.header("데이터 입력 방식")

upload_file = st.sidebar.file_uploader("CSV 업로드", type=["csv"])
github_url = st.sidebar.text_input("GitHub RAW CSV URL 입력")

sample_btn = st.sidebar.button("샘플 데이터 불러오기")

# =======================
# 데이터 불러오기
# =======================
df = None

if upload_file:
    df = load_uploaded_file(upload_file)
elif github_url:
    df = load_data_from_github(github_url)
elif sample_btn:
    df = pd.DataFrame({
        "country": ["Korea", "Korea", "USA", "USA", "Japan", "Japan", "Japan"],
        "blood_type": ["A", "O", "O", "A", "B", "A", "A"]
    })
    st.success("샘플 데이터를 불러왔습니다.")

# =======================
# 데이터 존재 시 처리
# =======================
if df is not None:

    st.subheader("📌 원본 데이터 미리보기")
    st.dataframe(df.head())

    # 필수 컬럼 체크
    if "country" not in df.columns or "blood_type" not in df.columns:
        st.error("❌ CSV 컬럼 이름은 반드시 country, blood_type 이어야 합니다.")
        st.stop()

    # =======================
    # 국가별 혈액형 개수 집계
    # =======================
    count_df = df.groupby(["country", "blood_type"]).size().reset_index(name="count")

    # =======================
    # 우세 혈액형 계산
    # =======================
    dominant_df = count_df.loc[count_df.groupby("country")['count'].idxmax()]
    dominant_df = dominant_df.sort_values(by="count", ascending=False)

    st.subheader("🏆 국가별 우세 혈액형")
    st.dataframe(dominant_df)

    # =======================
    # 막대그래프: 우세 혈액형 개수
    # =======================
    st.subheader("📊 국가별 우세 혈액형 (막대그래프)")
    fig = px.bar(
        dominant_df,
        x="country",
        y="count",
        color="blood_type",
        text="blood_type",
        title="국가별 우세 혈액형 분포",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(xaxis_title="국가", yaxis_title="해당 혈액형 개수")
    st.plotly_chart(fig, use_container_width=True)

    # =======================
    # 특정 국가 선택 → 혈액형 비율 그래프
    # =======================
    st.subheader("🔎 특정 국가 혈액형 비율 분석")

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
    st.info("👉 데이터를 업로드하거나 GitHub Raw URL을 입력해주세요.")
