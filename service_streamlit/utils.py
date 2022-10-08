import requests
import streamlit as st

from enum import Enum


endpoint = "http://146.185.210.44/api/v1/trands"

role_name_to_role_id = {
    "Бухгалтер": "%D0%B1%D1%83%D1%85%D0%B3%D0%B0%D0%BB%D1%82%D0%B5%D1%80",
    "Генеральный Директор": "%D0%B3%D0%B5%D0%BD_%D0%B4%D0%B8%D1%80%D0%B5%D0%BA%D1%82%D0%BE%D1%80"
}


class Period(str, Enum):
    day = "day"
    week = "week"
    month = "month"
    quarter = "quarter"


def download_data(role_name: str, period: Period, num_trands: int, num_trand_news: int, num_trand_news_insights: int):
    response = requests.get(
        f"{endpoint}/{role_name_to_role_id[role_name]}?period={period.value}&num_trands={num_trands}&num_trand_news={num_trand_news}&num_trand_news_insights={num_trand_news_insights}")
    return response.json()


def hide_streamlit():
    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
