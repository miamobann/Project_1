# 날씨 API 실습
# OpenWeatherMap 현재 날씨 API
# 사전준비 OpenWeatherMap 회원 가입후 API 발급
# pip install requests python-dotenv  = 내 env를 파일로 만들어서 함께 배포
# .env 파일을 생성하고 여기에 OPENWEATHER_API_KEY = 발급받은_API_키
# .env.example에는 OPENWEATHER_API_KEY=your_key
# .env.example 받아서 .env로 이름 바꾸고 자기 API를 채운다.


import os
import requests
import streamlit
from dotenv import load_dotenv

load_dotenv()  #.env 파일을 읽어 환경 변수로 등록한다.
API_KEY = os.getenv("EXCHANGERATE_API_KEY")
