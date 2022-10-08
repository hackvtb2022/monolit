from display_trend import display_trend
from display_trends import display_trends
from utils import hide_streamlit, download_data, Period

import streamlit as st


query_params = st.experimental_get_query_params()
selected_role = query_params.get("role", ["Trends"])[0]
selected_trend = query_params.get("trend", ["Trends"])[0]
selected_period = query_params.get("period", ["week"])[0]


def main():
    accountant_data = download_data(role_name="Бухгалтер", period=Period(selected_period), num_trands=3, num_trand_news=3, num_trand_news_insights=1)
    ceo_data = download_data(role_name="Генеральный Директор", period=Period(selected_period), num_trands=3, num_trand_news=3, num_trand_news_insights=2)
    st.markdown(f"<div>"
                f"<a target='_self' style='color: white; text-decoration: none; font-size: 18px; font-weight: 500; padding: 0px; margin: 0px; margin-right: 10px' href='?period=day'>Day</a>"
                f"<a target='_self' style='color: white; text-decoration: none; font-size: 18px; font-weight: 500; padding: 0px; margin: 0px; margin-right: 10px' href='?period=week'>Week</a>"
                f"<a target='_self' style='color: white; text-decoration: none; font-size: 18px; font-weight: 500; padding: 0px; margin: 0px; margin-right: 10px' href='?period=month'>Month</a>"
                f"</div>", unsafe_allow_html=True)
    if selected_trend == "Trends":
        st.title(selected_period.capitalize())
        display_trends(accountant_data, "Бухгалтер", selected_period)
        display_trends(ceo_data, "Генеральный Директор", selected_period)
    else:
        if selected_role == "Бухгалтер":
            display_trend(accountant_data, trend=selected_trend)
        elif selected_role == "Генеральный Директор":
            display_trend(ceo_data, trend=selected_trend)


main()
hide_streamlit()
