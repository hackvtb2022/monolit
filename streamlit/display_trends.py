import json
import streamlit as st


def display_trends(filename: str, role: str):
    with open(filename, "r") as file:
        mock = json.load(file)
    st.header(role)
    for trend in mock["trands"]:
        trand_title = trend["trand_title"]
        st.markdown(
            f"<a style='color: white; text-decoration: none; font-size: 18px; font-weight: 500; padding: 0px; margin: 0px' href='/?trend={trand_title}&role={role}'>{trand_title}</a>",
            unsafe_allow_html=True)
        st.markdown(
            """<hr style="height:1px;border:none;color:#333;background-color:#333; margin: 0px; padding: 0px" /> """,
            unsafe_allow_html=True)
