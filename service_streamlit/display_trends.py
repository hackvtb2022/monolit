import streamlit as st

from typing import Dict


def display_trends(data: Dict, role: str, period: str):
    st.header(role)
    for trend in data["trands"]:
        trand_title = trend["trand_title"]
        st.markdown(
            f"<a target='_self' style='color: white; text-decoration: none; font-size: 18px; font-weight: 500; padding: 0px; margin: 0px' href='?trend={trand_title}&role={role}&period={period}'>{trand_title}</a>",
            unsafe_allow_html=True)
        st.markdown(
            """<hr style="height:1px;border:none;color:#333;background-color:#333; margin: 0px; padding: 0px" /> """,
            unsafe_allow_html=True)
