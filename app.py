import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 페이지 설정
st.set_page_config(page_title="무역 분석 대시보드", layout="wide")

# 한글 폰트 설정 (NanumGothic.otf 사용)
font_path = 'NanumGothic.otf'
font_prop = fm.FontProperties(fname=font_path)
plt.rc('font', family=font_prop.get_name())

# 데이터 로드
@st.cache_data
def load_data():
    baci = pd.read_csv('baci_85_sample.csv')
    codes = pd.read_csv('country_codes_sample.csv')
    # 국가명 병합
    df = pd.merge(baci, codes, on='j')
    
    # 컬럼명 한국어 변경
    df = df.rename(columns={
        'i': '수출국_코드',
        'j': '수입국_코드',
        'k': '품목_코드',
        't': '연도',
        'v': '수출액',
        'country_name': '수입국명'
    })
    return df

df = load_data()

# 사이드바
st.sidebar.title("필터")
countries = st.sidebar.multiselect("국가 선택", options=df['수입국명'].unique(), default=df['수입국명'].unique())
# 무역 규모 등급 (예시로 임의 분류)
df['trade_class'] = pd.cut(df['수출액'], bins=[0, 30000, 60000, np.inf], labels=['소', '중', '대'])
classes = st.sidebar.multiselect("무역규모 등급 선택", options=['대', '중', '소'], default=['대', '중', '소'])

# 데이터 필터링
mask = (df['수입국명'].isin(countries)) & (df['trade_class'].isin(classes))
filtered_df = df[mask]

# 메인 화면
st.title("무역 분석 대시보드")

# 2. baci_85_sample.csv 파일의 결측치
st.subheader("2. baci_85_sample.csv 파일의 결측치")
st.dataframe(filtered_df.isnull().sum().to_frame(name='결측치 개수'))

# 3. 총거래건수, 총 수출액
st.subheader("3. 총거래건수 및 총 수출액")
col1, col2 = st.columns(2)
col1.metric("총 거래 건수", len(filtered_df))
col2.metric("총 수출액 (달러)", f"{filtered_df['수출액'].sum():,.2f}")

# 4. 국가*년도 수출액 히트맵(상위 8개국), 무역액 등급 분포
st.subheader("4. 데이터 시각화")
c1, c2 = st.columns(2)

with c1:
    st.write("국가*년도 수출액 히트맵 (상위 8개국)")
    top_8_countries = filtered_df.groupby('수입국명')['수출액'].sum().nlargest(8).index
    heatmap_df = filtered_df[filtered_df['수입국명'].isin(top_8_countries)].pivot_table(index='수입국명', columns='연도', values='수출액', aggfunc='sum')
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(heatmap_df, annot=True, fmt='.1f', cmap='YlGnBu', ax=ax)
    st.pyplot(fig)

with c2:
    st.write("무역액 등급 분포")
    class_counts = filtered_df['trade_class'].value_counts()
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(class_counts, labels=class_counts.index, autopct='%1.1f%%', startangle=90)
    st.pyplot(fig)

# 5. 상위 5개국 * 무역액 등급 교차표
st.subheader("5. 상위 5개국 * 무역액 등급 교차표")
top_5_countries = filtered_df.groupby('수입국명')['수출액'].sum().nlargest(5).index
cross_tab = pd.crosstab(filtered_df[filtered_df['수입국명'].isin(top_5_countries)]['수입국명'], filtered_df['trade_class'])

st.write("원본 건수")
st.dataframe(cross_tab)

st.write("정규화 비율")
st.dataframe(cross_tab.div(cross_tab.sum(axis=1), axis=0))
