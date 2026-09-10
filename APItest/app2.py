import os
import requests
import streamlit as st
from dotenv import load_dotenv

# 환경 변수 로드 (.env 파일)
load_dotenv()
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
EXCHANGE_API_KEY = os.getenv("EXCHANGERATE_API_KEY")

# 웹 페이지 레이아웃 및 기본 설정
st.set_page_config(page_title="글로벌 실시간 날씨 및 환율 정보", layout="wide")

# API 인증 키 유효성 검증
if not WEATHER_API_KEY or not EXCHANGE_API_KEY:
    missing_keys = []
    if not WEATHER_API_KEY:
        missing_keys.append("OPENWEATHER_API_KEY")
    if not EXCHANGE_API_KEY:
        missing_keys.append("EXCHANGERATE_API_KEY")
    st.error(f"환경 변수 설정 누락: {', '.join(missing_keys)}. .env 파일을 확인해 주십시오.")
    st.stop()

# 반투명 카드 레이어 전용 CSS 주입
custom_card_css = """
<style>
/* 컨테이너 카드 블록만 반투명 레이어로 지정 */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(30, 41, 59, 0.45) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 14px !important;
    padding: 24px !important;
}

/* 카드 내부 지표 레이블 가독성 확보 */
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMetricLabel"] p {
    color: #94a3b8 !important;
    font-size: 0.9rem !important;
}

/* 사이드바 스타일 격리 유지 */
section[data-testid="stSidebar"] {
    background-color: inherit;
}
</style>
"""
st.markdown(custom_card_css, unsafe_allow_html=True)

# 지원 도시 및 통화 매핑 정의
CITY_DATA = {
    "서울 (대한민국)": {"city_query": "Seoul", "currency": "KRW"},
    "부산 (대한민국)": {"city_query": "Busan", "currency": "KRW"},
    "제주 (대한민국)": {"city_query": "Jeju", "currency": "KRW"},
    "인천 (대한민국)": {"city_query": "Incheon", "currency": "KRW"},
    "도쿄 (일본)": {"city_query": "Tokyo", "currency": "JPY"},
    "오사카 (일본)": {"city_query": "Osaka", "currency": "JPY"},
    "베이징 (중국)": {"city_query": "Beijing", "currency": "CNY"},
    "상하이 (중국)": {"city_query": "Shanghai", "currency": "CNY"},
    "뉴욕 (미국)": {"city_query": "New York", "currency": "USD"},
    "로스앤젤레스 (미국)": {"city_query": "Los Angeles", "currency": "USD"},
    "런던 (영국)": {"city_query": "London", "currency": "GBP"},
    "파리 (프랑스)": {"city_query": "Paris", "currency": "EUR"},
    "시드니 (호주)": {"city_query": "Sydney", "currency": "AUD"}
}

# 날씨 데이터 조회 함수 (캐시 적용: 10분)
@st.cache_data(ttl=600)
def fetch_weather_data(city_name: str, api_key: str):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city_name,
        "appid": api_key,
        "units": "metric",
        "lang": "kr"
    }
    response = requests.get(url, params=params)
    return response.status_code, response.json()

# 환율 데이터 조회 함수 (캐시 적용: 10분)
@st.cache_data(ttl=600)
def fetch_exchange_rates(api_key: str):
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
    response = requests.get(url)
    return response.status_code, response.json()

# 사이드바: 도시 선택 영역
with st.sidebar:
    st.header("검색 옵션")
    selected_display_name = st.selectbox(
        "조회할 도시를 선택하십시오.",
        options=list(CITY_DATA.keys())
    )

# 메인 화면 기본 구성
st.title("글로벌 실시간 정보 시스템")
st.markdown("---")

# 화면 분할: 좌측(날씨), 우측(환율)
weather_col, exchange_col = st.columns([1, 1], gap="large")

current_city_info = CITY_DATA[selected_display_name]
city_query = current_city_info["city_query"]
local_currency = current_city_info["currency"]

# 1. 좌측 열: 실시간 날씨 영역 (반투명 카드 적용)
with weather_col:
    with st.container(border=True):
        st.subheader(f"{selected_display_name} 실시간 기상 관측 정보")
        w_status, w_data = fetch_weather_data(city_query, WEATHER_API_KEY)

        if w_status == 200:
            weather_desc = w_data["weather"][0]["description"]
            icon_code = w_data["weather"][0]["icon"]
            temp = w_data["main"]["temp"]
            feels_like = w_data["main"]["feels_like"]
            humidity = w_data["main"]["humidity"]
            pressure = w_data["main"]["pressure"]
            country = w_data["sys"]["country"]
            wind_speed = w_data.get("wind", {}).get("speed", 0.0)
            wind_gust = w_data.get("wind", {}).get("gust", None)
            clouds = w_data.get("clouds", {}).get("all", 0)
            visibility_km = w_data.get("visibility", 0) / 1000

            icon_area, desc_area = st.columns([1, 5])
            with icon_area:
                icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
                st.image(icon_url, width=90)
            with desc_area:
                st.markdown(f"### **{weather_desc}**")
                st.caption(f"기압: {pressure} hPa | 구름량: {clouds}%")

            st.write("")

            row1_col1, row1_col2, row1_col3 = st.columns(3)
            row1_col1.metric("현재 기온", f"{temp} °C")
            row1_col2.metric("체감 기온", f"{feels_like} °C")
            row1_col3.metric("습도", f"{humidity} %")

            st.write("")

            row2_col1, row2_col2, row2_col3 = st.columns(3)
            gust_text = f" (돌풍: {wind_gust} m/s)" if wind_gust else ""
            row2_col1.metric("풍속", f"{wind_speed} m/s{gust_text}")
            row2_col2.metric("해면 기압", f"{pressure} hPa")
            row2_col3.metric("가시거리", f"{visibility_km:.1f} km")

        elif w_status == 401:
            st.error("OpenWeather API 키 인증에 실패했습니다. 키 유효성을 확인해 주십시오.")
        else:
            message = w_data.get("message", "알 수 없는 오류")
            st.error(f"요청 처리 중 오류가 발생했습니다: {message}")

# 2. 우측 열: 실시간 환율 영역 (반투명 카드 적용)
with exchange_col:
    with st.container(border=True):
        st.subheader("글로벌 주요 환율 정보")
        e_status, e_data = fetch_exchange_rates(EXCHANGE_API_KEY)

        if e_status == 200 and e_data.get("result") == "success":
            rates = e_data.get("conversion_rates", {})
            usd_to_krw = rates.get("KRW", 1.0)

            usd_rate = usd_to_krw
            jpy_rate = (usd_to_krw / rates.get("JPY", 1.0)) * 100 if rates.get("JPY") else 0.0
            eur_rate = usd_to_krw / rates.get("EUR", 1.0) if rates.get("EUR") else 0.0
            cny_rate = usd_to_krw / rates.get("CNY", 1.0) if rates.get("CNY") else 0.0

            st.caption(f"기준 시각: {e_data.get('time_last_update_utc', 'N/A')[:16]}")
            st.write("")

            ex_row1_col1, ex_row1_col2 = st.columns(2)
            ex_row1_col1.metric("미국 (1 USD)", f"{usd_rate:,.2f} KRW")
            ex_row1_col2.metric("일본 (100 JPY)", f"{jpy_rate:,.2f} KRW")

            st.write("")
            ex_row2_col1, ex_row2_col2 = st.columns(2)
            ex_row2_col1.metric("유럽연합 (1 EUR)", f"{eur_rate:,.2f} KRW")
            ex_row2_col2.metric("중국 (1 CNY)", f"{cny_rate:,.2f} KRW")

            st.markdown("---")
            if local_currency == "KRW":
                st.info("선택된 도시는 대한민국 지역으로 기준 통화(KRW)와 동일합니다.")
            else:
                local_rate_krw = usd_to_krw / rates.get(local_currency, 1.0)
                st.metric(f"선택 도시 현지 통화 (1 {local_currency})", f"{local_rate_krw:,.2f} KRW")

        elif e_status == 401 or e_data.get("result") == "error":
            error_msg = e_data.get("error-type", "인증 실패")
            st.error(f"ExchangeRate API 조회 실패: {error_msg}")
        else:
            st.error("환율 서버 응답을 수신하지 못했습니다.")