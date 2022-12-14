import streamlit as st

from datetime import datetime
from typing import Dict


def display_trend(data: Dict, trend: str):
    st.header(trend)
    for item in data["trands"]:
        if item["trand_title"] == trend:
            news = item["news"]
            break

    for item in news:
        date_object = datetime.strptime(item["post_dttm"], '%Y-%m-%dT%H:%M:%S').date()
        st.write(date_object)
        st.markdown(
            f"<p style='color: rgba(250, 250, 250, 1.0); font-size: 18px'>{item['title']} <a href={item['url']}>источник</a></p>",
            unsafe_allow_html=True
        )
        insights = item["insights"]["items"]
        mask = [0] * (insights[-1]["end"])
        insights = sorted(insights, key=lambda x: -x["score"])
        for insight in insights[:2]:
            mask[insight["start"]:insight["end"]] = [1] * (insight["end"] - insight["start"])
        html = ""
        for char, mask in zip(item["full_text"], mask):
            html += f"<span style='color: rgba(250, 250, 250, {1.0 if mask == 1 else 0.6}); font-size: 14px'>{char}</span>"
        st.markdown(html, unsafe_allow_html=True)
        st.markdown("""---""")
