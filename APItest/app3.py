import os
import base64
import requests
import streamlit as st
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
EXCHANGE_API_KEY = os.getenv("EXCHANGERATE_API_KEY")

# 페이지 레이아웃 및 타이틀 설정
st.set_page_config(page_title="실시간 세계 정보", layout="wide")

# API 인증 키 유효성 검증
if not WEATHER_API_KEY or not EXCHANGE_API_KEY:
    missing = []
    if not WEATHER_API_KEY:
        missing.append("OPENWEATHER_API_KEY")
    if not EXCHANGE_API_KEY:
        missing.append("EXCHANGERATE_API_KEY")
    st.error(f"환경 변수 누락: {', '.join(missing)}. .env 파일을 확인하십시오.")
    st.stop()

# 로컬 폰트 로드 및 사이드바 버튼 커스텀 스타일 주입
def apply_sidebar_custom_style(font_path: str):
    font_face = ""
    font_family_rule = ""
    
    if os.path.exists(font_path):
        with open(font_path, "rb") as f:
            b64_font = base64.b64encode(f.read()).decode("utf-8")
        font_face = f"""
        @font-face {{
            font-family: 'NanumGothicCustom';
            src: url('data:font/opentype;base64,{b64_font}') format('opentype');
            font-weight: normal;
            font-style: normal;
        }}
        """
        font_family_rule = "font-family: 'NanumGothicCustom', sans-serif !important;"

    custom_css = f"""
    <style>
    {font_face}

    /* 사이드바 전역 폰트 적용 */
    section[data-testid="stSidebar"] {{
        {font_family_rule}
    }}

    /* 사이드바 헤더 및 텍스트 크기 조정 */
    section[data-testid="stSidebar"] h1 {{
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        {font_family_rule}
    }}
    
    section[data-testid="stSidebar"] p {{
        font-size: 1.05rem !important;
        {font_family_rule}
    }}

    /* 사이드바 탭 버튼 폰트 크기 및 높이 지정 */
    section[data-testid="stSidebar"] div[data-testid="stButton"] button {{
        width: 100% !important;
        padding: 12px 16px !important;
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
        {font_family_rule}
    }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

# 폰트 경로 지정 및 스타일 적용
apply_sidebar_custom_style("../fonts/NanumGothic.otf")

# 지원 도시 매핑 테이블
CITY_MAPPING = {
    "서울 (대한민국)": "Seoul",
    "부산 (대한민국)": "Busan",
    "제주 (대한민국)": "Jeju",
    "인천 (대한민국)": "Incheon",
    "도쿄 (일본)": "Tokyo",
    "오사카 (일본)": "Osaka",
    "베이징 (중국)": "Beijing",
    "상하이 (중국)": "Shanghai",
    "뉴욕 (미국)": "New York",
    "로스앤젤레스 (미국)": "Los Angeles",
    "런던 (영국)": "London",
    "파리 (프랑스)": "Paris",
    "시드니 (호주)": "Sydney"
}

# 통화 목록 매핑 테이블
CURRENCY_MAPPING = {
    "KRW (대한민국 원)": "KRW",
    "USD (미국 달러)": "USD",
    "JPY (일본 엔)": "JPY",
    "EUR (유럽연합 유로)": "EUR",
    "GBP (영국 파운드)": "GBP",
    "CNY (중국 위안)": "CNY",
    "AUD (호주 달러)": "AUD",
    "CAD (캐나다 달러)": "CAD",
    "CHF (스위스 프랑)": "CHF"
}

# 날씨 데이터 호출 함수 (10분 캐싱)
@st.cache_data(ttl=600)
def fetch_weather(city_name: str, api_key: str):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city_name,
        "appid": api_key,
        "units": "metric",
        "lang": "kr"
    }
    response = requests.get(url, params=params)
    return response.status_code, response.json()

# 환율 데이터 호출 함수 (10분 캐싱)
@st.cache_data(ttl=600)
def fetch_exchange_rates(api_key: str):
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
    response = requests.get(url)
    return response.status_code, response.json()

# 메뉴 세션 상태 초기화
if "menu" not in st.session_state:
    st.session_state["menu"] = "날씨 정보"

# 사이드바: 순수 버튼형 탭 내비게이션
with st.sidebar:
    st.title("메뉴")
    st.write("이동할 페이지를 선택하십시오.")

    weather_type = "primary" if st.session_state["menu"] == "날씨 정보" else "secondary"
    if st.button("날씨 정보", key="nav_weather", type=weather_type, use_container_width=True):
        st.session_state["menu"] = "날씨 정보"
        st.rerun()

    exchange_type = "primary" if st.session_state["menu"] == "환율 정보" else "secondary"
    if st.button("환율 정보", key="nav_exchange", type=exchange_type, use_container_width=True):
        st.session_state["menu"] = "환율 정보"
        st.rerun()

st.title("실시간 세계 정보")
st.markdown("---")

# 1. 날씨 정보 페이지
if st.session_state["menu"] == "날씨 정보":
    st.subheader("실시간 날씨 정보")
    
    selected_city = st.selectbox(
        "조회할 도시를 선택하십시오.",
        options=list(CITY_MAPPING.keys())
    )
    city_query = CITY_MAPPING[selected_city]
    status_code, weather_data = fetch_weather(city_query, WEATHER_API_KEY)

    if status_code == 200:
        weather_desc = weather_data["weather"][0]["description"]
        icon_code = weather_data["weather"][0]["icon"]
        temp = weather_data["main"]["temp"]
        feels_like = weather_data["main"]["feels_like"]
        humidity = weather_data["main"]["humidity"]
        pressure = weather_data["main"]["pressure"]
        country = weather_data["sys"]["country"]
        wind_speed = weather_data.get("wind", {}).get("speed", 0.0)
        visibility_km = weather_data.get("visibility", 0) / 1000

        st.caption(f"관측 대상: {selected_city} ({country})")

        icon_col, desc_col = st.columns([1, 6])
        with icon_col:
            icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
            st.image(icon_url, width=90)
        with desc_col:
            st.markdown(f"### **{weather_desc}**")
            st.write(f"해면 기압: {pressure} hPa | 가시거리: {visibility_km:.1f} km")

        st.write("")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("현재 기온", f"{temp} °C")
        col2.metric("체감 기온", f"{feels_like} °C")
        col3.metric("습도", f"{humidity} %")
        col4.metric("풍속", f"{wind_speed} m/s")

    elif status_code == 401:
        st.error("OpenWeather API 키 인증 실패. 설정을 확인하십시오.")
    else:
        st.error(f"날씨 데이터 조회 오류: {weather_data.get('message', '알 수 없는 오류')}")

# 2. 환율 정보 페이지
elif st.session_state["menu"] == "환율 정보":
    st.subheader("환율 정보")
    status_code, exchange_data = fetch_exchange_rates(EXCHANGE_API_KEY)

    if status_code == 200 and exchange_data.get("result") == "success":
        rates = exchange_data.get("conversion_rates", {})
        usd_to_krw = rates.get("KRW", 1.0)

        # 환율 정보 표시 보드
        with st.container(border=True):
            st.markdown("#### **실시간 기축통화 환율 현황 (KRW 기준)**")
            st.caption(f"기준 시각: {exchange_data.get('time_last_update_utc', 'N/A')[:16]}")
            st.write("")

            usd_rate = usd_to_krw
            jpy_rate = (usd_to_krw / rates.get("JPY", 1.0)) * 100 if rates.get("JPY") else 0.0
            eur_rate = usd_to_krw / rates.get("EUR", 1.0) if rates.get("EUR") else 0.0
            gbp_rate = usd_to_krw / rates.get("GBP", 1.0) if rates.get("GBP") else 0.0

            b_col1, b_col2, b_col3, b_col4 = st.columns(4)
            b_col1.metric("미국 (1 USD)", f"{usd_rate:,.2f} KRW")
            b_col2.metric("일본 (100 JPY)", f"{jpy_rate:,.2f} KRW")
            b_col3.metric("유럽연합 (1 EUR)", f"{eur_rate:,.2f} KRW")
            b_col4.metric("영국 (1 GBP)", f"{gbp_rate:,.2f} KRW")

        st.write("")
        st.write("")

        # 실시간 환율 계산기
        st.subheader("실시간 환율 계산기")
        currency_keys = list(CURRENCY_MAPPING.keys())

        curr_col1, _, curr_col2 = st.columns([5, 1, 5])
        with curr_col1:
            curr1_label = st.selectbox(
                "통화 1",
                options=currency_keys,
                index=currency_keys.index("KRW (대한민국 원)"),
                key="curr1_select"
            )
        with curr_col2:
            curr2_label = st.selectbox(
                "통화 2",
                options=currency_keys,
                index=currency_keys.index("USD (미국 달러)"),
                key="curr2_select"
            )

        code1 = CURRENCY_MAPPING[curr1_label]
        code2 = CURRENCY_MAPPING[curr2_label]
        rate1 = rates.get(code1, 1.0)
        rate2 = rates.get(code2, 1.0)

        ratio_1_to_2 = rate2 / rate1 if rate1 > 0 else 0.0
        ratio_2_to_1 = rate1 / rate2 if rate2 > 0 else 0.0

        krw_per_unit1 = (usd_to_krw / rate1) if rate1 > 0 else 0.0
        krw_per_unit2 = (usd_to_krw / rate2) if rate2 > 0 else 0.0

        if "amount_1" not in st.session_state:
            st.session_state["amount_1"] = 1000.0
        if "amount_2" not in st.session_state:
            st.session_state["amount_2"] = round(st.session_state["amount_1"] * ratio_1_to_2, 2)

        def update_from_amount_1():
            st.session_state["amount_2"] = round(st.session_state["amount_1"] * ratio_1_to_2, 2)

        def update_from_amount_2():
            st.session_state["amount_1"] = round(st.session_state["amount_2"] * ratio_2_to_1, 2)

        calc_col1, arrow_col, calc_col2 = st.columns([5, 1, 5])

        with calc_col1:
            st.write("금액 입력")
            in1_col, unit1_col = st.columns([4, 1])
            with in1_col:
                st.number_input(
                    "금액 입력 (통화 1)",
                    min_value=0.0,
                    step=100.0,
                    format="%.2f",
                    key="amount_1",
                    label_visibility="collapsed",
                    on_change=update_from_amount_1
                )
            with unit1_col:
                st.markdown(f"<div style='line-height: 2.5rem; font-weight: bold;'>{code1}</div>", unsafe_allow_html=True)

        with arrow_col:
            st.write("")
            st.markdown("<h3 style='text-align: center; margin-top: 15px;'>⇄</h3>", unsafe_allow_html=True)

        with calc_col2:
            st.write("금액 입력")
            in2_col, unit2_col = st.columns([4, 1])
            with in2_col:
                st.number_input(
                    "금액 입력 (통화 2)",
                    min_value=0.0,
                    step=1.0,
                    format="%.2f",
                    key="amount_2",
                    label_visibility="collapsed",
                    on_change=update_from_amount_2
                )
            with unit2_col:
                st.markdown(f"<div style='line-height: 2.5rem; font-weight: bold;'>{code2}</div>", unsafe_allow_html=True)

        caption_parts = []
        if code1 != "KRW":
            caption_parts.append(f"1 {code1} = {krw_per_unit1:,.2f} KRW")
        if code2 != "KRW":
            caption_parts.append(f"1 {code2} = {krw_per_unit2:,.2f} KRW")

        if caption_parts:
            st.caption("적용 환율: " + " | ".join(caption_parts))
        else:
            st.caption("적용 환율: 1 KRW = 1.00 KRW")

    elif status_code == 401 or exchange_data.get("result") == "error":
        error_msg = exchange_data.get("error-type", "인증 실패")
        st.error(f"ExchangeRate API 조회 실패: {error_msg}")
    else:
        st.error("환율 서버와의 통신에 실패했습니다.")