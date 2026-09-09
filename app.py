import base64
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
FONT_PATH = BASE_DIR / "NanumGothic.otf"

st.set_page_config(page_title="무역 분석 대시보드", page_icon="📊", layout="wide")


@st.cache_data
def get_font_css(font_path: str) -> str:
    """배포 환경의 브라우저에도 한글 폰트를 제공한다."""
    font_base64 = base64.b64encode(Path(font_path).read_bytes()).decode("ascii")
    return f"""
    <style>
        @font-face {{
            font-family: 'NanumGothicWeb';
            src: url(data:font/otf;base64,{font_base64}) format('opentype');
        }}
        html, body, [class*="st-"], [data-testid="stDataFrame"] * {{
            font-family: 'NanumGothicWeb', 'Noto Sans KR', sans-serif;
        }}
        .stApp {{ background: #f7f9fc; }}
        .section-heading {{
            display: flex; align-items: center; gap: 0.65rem;
            margin: 2.1rem 0 0.7rem; font-size: 1.28rem; font-weight: 700;
            color: #173b67;
        }}
        .section-number {{
            display: inline-flex; align-items: center; justify-content: center;
            width: 1.8rem; height: 1.8rem; border-radius: 50%;
            background: #dbeafe; color: #1d4ed8; font-size: 0.85rem;
        }}
        [data-testid="stMetric"] {{
            background: #ffffff; border: 1px solid #dbe4f0; border-radius: 12px;
            padding: 1rem 1.2rem;
        }}
        [data-testid="stDataFrame"] {{
            border: 1px solid #dbe4f0; border-radius: 10px; overflow: hidden;
        }}
    </style>
    """


if not FONT_PATH.exists():
    st.error("한글 폰트 파일(NanumGothic.otf)을 찾을 수 없습니다.")
    st.stop()

# Matplotlib 차트와 Streamlit 표 모두에 같은 한글 폰트를 적용한다.
font_prop = fm.FontProperties(fname=FONT_PATH)
plt.rc("font", family=font_prop.get_name())
plt.rcParams["axes.unicode_minus"] = False
st.markdown(get_font_css(str(FONT_PATH)), unsafe_allow_html=True)


def section_heading(number: int, title: str) -> None:
    st.markdown(
        f'<div class="section-heading"><span class="section-number">{number}</span>{title}</div>',
        unsafe_allow_html=True,
    )


@st.cache_data
def load_data():
    # 명시적 UTF-8 지정으로 GitHub 배포 환경에서도 한글 CSV를 같은 방식으로 읽는다.
    baci = pd.read_csv(BASE_DIR / "baci_85_sample.csv", encoding="utf-8")
    codes = pd.read_csv(BASE_DIR / "country_codes_sample.csv", encoding="utf-8")
    df = pd.merge(baci, codes, on="j")
    return df.rename(
        columns={
            "i": "수출국_코드",
            "j": "수입국_코드",
            "k": "품목_코드",
            "t": "연도",
            "v": "수출액",
            "country_name": "수입국명",
        }
    )


df = load_data()
df["trade_class"] = pd.cut(
    df["수출액"], bins=[0, 30000, 60000, np.inf], labels=["소", "중", "대"]
)

with st.sidebar:
    st.title("필터")
    st.caption("표시할 국가와 무역 규모를 선택하세요.")
    countries = st.multiselect(
        "국가 선택", options=df["수입국명"].unique(), default=df["수입국명"].unique()
    )
    classes = st.multiselect(
        "무역규모 등급 선택", options=["대", "중", "소"], default=["대", "중", "소"]
    )

filtered_df = df[df["수입국명"].isin(countries) & df["trade_class"].isin(classes)]

st.title("무역 분석 대시보드")
st.caption("국가별·연도별 수출 데이터를 필터링하고 비교합니다.")

section_heading(1, "데이터 품질")
missing_df = filtered_df.isnull().sum().rename_axis("항목").reset_index(name="결측치 개수")
st.dataframe(
    missing_df,
    hide_index=True,
    use_container_width=True,
    column_config={
        "항목": st.column_config.TextColumn("항목", width="medium"),
        "결측치 개수": st.column_config.NumberColumn("결측치 개수", format="%d", width="small"),
    },
)

section_heading(2, "핵심 지표")
col1, col2 = st.columns(2)
col1.metric("총 거래 건수", f"{len(filtered_df):,}건")
col2.metric("총 수출액", f"${filtered_df['수출액'].sum():,.2f}")

section_heading(3, "데이터 시각화")
if filtered_df.empty:
    st.info("선택한 조건에 해당하는 데이터가 없습니다. 사이드바 필터를 조정해 주세요.")
else:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("##### 국가·연도별 수출액 — 상위 8개국")
        top_8 = filtered_df.groupby("수입국명")["수출액"].sum().nlargest(8).index
        heatmap_df = filtered_df[filtered_df["수입국명"].isin(top_8)].pivot_table(
            index="수입국명", columns="연도", values="수출액", aggfunc="sum"
        )
        fig, ax = plt.subplots(figsize=(10, 5.5))
        sns.heatmap(heatmap_df, annot=True, fmt=".1f", cmap="YlGnBu", linewidths=0.5, ax=ax)
        ax.set_xlabel("연도")
        ax.set_ylabel("수입국")
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    with c2:
        st.markdown("##### 무역액 등급 분포")
        class_counts = filtered_df["trade_class"].value_counts().reindex(["대", "중", "소"], fill_value=0)
        fig, ax = plt.subplots(figsize=(6, 5.5))
        ax.pie(class_counts, labels=class_counts.index, autopct="%1.1f%%", startangle=90,
               colors=["#2563eb", "#60a5fa", "#bfdbfe"], wedgeprops={"edgecolor": "white"})
        ax.set_title("거래 건수 기준")
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

section_heading(4, "상위 5개국 × 무역액 등급")
if not filtered_df.empty:
    top_5 = filtered_df.groupby("수입국명")["수출액"].sum().nlargest(5).index
    cross_tab = pd.crosstab(
        filtered_df.loc[filtered_df["수입국명"].isin(top_5), "수입국명"],
        filtered_df["trade_class"],
    ).reindex(columns=["대", "중", "소"], fill_value=0)

    left, right = st.columns(2)
    with left:
        st.markdown("##### 원본 건수")
        st.dataframe(cross_tab.reset_index(), hide_index=True, use_container_width=True)
    with right:
        st.markdown("##### 국가별 구성 비율")
        ratio_table = (cross_tab.div(cross_tab.sum(axis=1), axis=0).fillna(0) * 100).reset_index()
        st.dataframe(
            ratio_table,
            hide_index=True,
            use_container_width=True,
            column_config={"대": st.column_config.NumberColumn(format="%.1f%%"),
                           "중": st.column_config.NumberColumn(format="%.1f%%"),
                           "소": st.column_config.NumberColumn(format="%.1f%%")},
        )
