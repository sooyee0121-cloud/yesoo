import streamlit as st
import pandas as pd
import plotly.express as px
import io

st.set_page_config(page_title="나라별 우세 혈액형 분석 (개선판)", layout="wide")

st.title("🩸 나라별 우세 혈액형 — 개선된 대시보드")
st.markdown("샘플 데이터로 바로 시각화가 나타납니다. CSV 업로드 또는 GitHub RAW URL로 실제 데이터로 교체하세요.")

# ----------------- 샘플 데이터 -----------------
SAMPLE_CSV = """country,blood_type
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
Germany,A
Germany,A
Germany,B
France,O
France,A
France,A
"""

@st.cache_data
def load_sample():
    return pd.read_csv(io.StringIO(SAMPLE_CSV))

# ----------------- 입력 (사이드바) -----------------
st.sidebar.header("데이터 입력")
data_mode = st.sidebar.radio("데이터 소스", ["샘플 데이터 사용", "파일 업로드", "GitHub RAW URL"])

@st.cache_data
def read_csv_from_url(url: str):
    return pd.read_csv(url)

df = None
if data_mode == "샘플 데이터 사용":
    df = load_sample()
elif data_mode == "파일 업로드":
    uploaded = st.sidebar.file_uploader("CSV 파일 업로드", type=["csv"])
    if uploaded is not None:
        try:
            df = pd.read_csv(uploaded)
        except Exception as e:
            st.sidebar.error(f"파일 읽기 실패: {e}")
elif data_mode == "GitHub RAW URL":
    url = st.sidebar.text_input("RAW CSV URL 입력")
    if url:
        try:
            df = read_csv_from_url(url)
        except Exception as e:
            st.sidebar.error(f"URL에서 CSV 불러오기 실패: {e}")

if df is None:
    st.warning("왼쪽에서 데이터 소스를 선택하세요. (샘플 사용 권장)")
    st.stop()

# ----------------- 전처리 -----------------
df = df.rename(columns={c: c.strip().lower() for c in df.columns})
required_cols = {"country", "blood_type"}
if not required_cols.issubset(set(df.columns)):
    st.error("CSV에 최소한 'country'와 'blood_type' 컬럼이 있어야 합니다.")
    st.stop()

df["country"] = df["country"].astype(str).str.strip()
df["blood_type"] = df["blood_type"].astype(str).str.strip().str.upper()

st.subheader("원본 데이터(미리보기)")
st.dataframe(df.head(10))

# ----------------- 집계 -----------------
@st.cache_data
def compute_counts(df):
    counts = df.groupby(["country", "blood_type"], as_index=False).size().rename(columns={"size":"count"})
    total = counts.groupby("country", as_index=False)["count"].sum().rename(columns={"count":"total_count"})
    counts = counts.merge(total, on="country")
    counts["pct"] = counts["count"] / counts["total_count"] * 100

    idx = counts.groupby("country")["count"].idxmax()
    dominant = counts.loc[idx].reset_index(drop=True)
    dominant = dominant.rename(columns={
        "blood_type":"dominant_blood_type",
        "count":"dominant_count",
        "pct":"dominant_pct"
    }).sort_values("dominant_count", ascending=False).reset_index(drop=True)
    return counts, dominant

counts_df, dominant_df = compute_counts(df)

# ----------------- 그래프 옵션 -----------------
st.sidebar.header("그래프 옵션")
top_n = st.sidebar.slider("상위 국가 수 (Top N)", min_value=3, max_value=100, value=15)
metric = st.sidebar.selectbox("막대그래프 기준", ["dominant_count", "dominant_pct"])
stacked_view = st.sidebar.checkbox("누적(스택) 보기", value=True)

# ----------------- 상위 국가 막대그래프 -----------------
st.subheader("📊 상위 국가 — 우세 혈액형 (수평 막대)")

if metric == "dominant_count":
    top_df = dominant_df.nlargest(top_n, "dominant_count")
else:
    top_df = dominant_df.nlargest(top_n, "dominant_pct")

top_df = top_df.sort_values(by=metric, ascending=True)

fig_bar = px.bar(
    top_df,
    x=metric,
    y="country",
    orientation="h",
    color="dominant_blood_type",
    labels={
        "dominant_count": "우세 혈액형 수",
        "dominant_pct": "우세 비율(%)",
        "country": "국가"
    },
    hover_data=["dominant_count", "dominant_pct", "total_count"]
)
fig_bar.update_layout(yaxis=dict(tickfont=dict(size=11)))
st.plotly_chart(fig_bar, use_container_width=True)

# ----------------- 누적 스택 -----------------
if stacked_view:
    st.subheader(f"🔢 상위 {top_n}개 국가의 혈액형 비율 (누적 스택, %)")

    pivot = counts_df.pivot_table(
        index="country",
        columns="blood_type",
        values="pct",
        fill_value=0
    ).reset_index()

    use_countries = dominant_df.nlargest(top_n, "dominant_count")["country"].tolist()
    pivot = pivot[pivot["country"].isin(use_countries)]

    fig_stack = px.bar(
        pivot,
        x="country",
        y=[c for c in pivot.columns if c not in ["country"]],
        title="혈액형 비율 (누적)",
        labels={"value": "비율(%)"}
    )
    fig_stack.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_stack, use_container_width=True)

# ----------------- 특정 국
