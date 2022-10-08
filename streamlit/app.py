import streamlit as st

from display_trend import display_trend
from display_trends import display_trends

query_params = st.experimental_get_query_params()
selected_role = query_params.get("role", ["Accountant"])[0]
selected_trend = query_params.get("trend", ["Trends"])[0]


if selected_trend == "Trends":
    display_trends("resources/accountant.json", "Бухгалтер")
    display_trends("resources/accountant.json", "Генеральный Директор")
else:
    if selected_role == "Бухгалтер":
        display_trend(filename="resources/accountant.json", trend=selected_trend)
    elif selected_role == "Генеральный Директор":
        display_trend(filename="resources/accountant.json", trend=selected_trend)

