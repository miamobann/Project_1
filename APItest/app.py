import os
import requests
import streamlit as st
from dotenv import load_dotenv

# 환경 변수 로드 (.env 파일)
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# 웹 페이지 레이아웃 및 기본 설정
st.set_page_config(page_title="글로벌 실시간 날씨 정보", layout="wide")

# API 인증 키 유효성 검증
if not API_KEY:
    st.error("API 키를 찾을 수 없습니다. .env 파일 내 OPENWEATHER_API_KEY 설정을 확인해 주십시오.")
    st.stop()

# 지원 도시 목록 정의 (화면 표시 명칭: API 요청용 영문 도시명)
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

# 날씨 데이터 조회 함수 (캐시 적용: 10분 동안 동일 도시 요청 시 캐시 반환)
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

# 사이드바: 도시 선택 영역 (선택 시 즉각 반영)
with st.sidebar:
    st.header("검색 옵션")
    selected_display_name = st.selectbox(
        "조회할 도시를 선택하십시오.",
        options=list(CITY_MAPPING.keys())
    )

# 메인 화면 구성
st.title("글로벌 실시간 날씨 정보 시스템")
st.markdown("---")

# 선택된 도시의 영문명 추출 및 데이터 호출
city_query = CITY_MAPPING[selected_display_name]
status_code, data = fetch_weather_data(city_query, API_KEY)

# 응답 처리 및 렌더링
if status_code == 200:
    weather_desc = data["weather"][0]["description"]
    icon_code = data["weather"][0]["icon"]
    temp = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]
    pressure = data["main"]["pressure"]
    country = data["sys"]["country"]
    wind_speed = data.get("wind", {}).get("speed", 0.0)
    wind_gust = data.get("wind", {}).get("gust", None)
    clouds = data.get("clouds", {}).get("all", 0)
    visibility_km = data.get("visibility", 0) / 1000

    # 관측 대상 도시 표기
    st.subheader(f"{selected_display_name} ({country}) 관측 정보")

    # 기상 아이콘 및 상태 요약 배치
    icon_col, desc_col = st.columns([1, 5])
    with icon_col:
        icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
        st.image(icon_url, width=90)
    with desc_col:
        st.markdown(f"### **{weather_desc}**")
        st.caption(f"기압: {pressure} hPa | 구름량: {clouds}%")

    st.write("")

    # 1차 기상 지표 (기온 및 습도)
    row1_col1, row1_col2, row1_col3 = st.columns(3)
    row1_col1.metric("현재 기온", f"{temp} °C")
    row1_col2.metric("체감 기온", f"{feels_like} °C")
    row1_col3.metric("습도", f"{humidity} %")

    # 2차 기상 지표 (바람 및 대기 환경)
    row2_col1, row2_col2, row2_col3 = st.columns(3)
    gust_text = f" (돌풍: {wind_gust} m/s)" if wind_gust else ""
    row2_col1.metric("풍속", f"{wind_speed} m/s{gust_text}")
    row2_col2.metric("해면 기압", f"{pressure} hPa")
    row2_col3.metric("가시거리", f"{visibility_km:.1f} km")

elif status_code == 401:
    st.error("API 키 인증에 실패했습니다. 키 유효성 및 활성화 상태를 확인해 주십시오.")
else:
    message = data.get("message", "알 수 없는 오류")
    st.error(f"요청 처리 중 오류가 발생했습니다: {message}")