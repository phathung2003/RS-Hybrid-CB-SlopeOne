import streamlit as st
from process.components import navigation

def sidebar():
    st.title("🎬 CINEMATIC")
    if st.button("🏠 Trang chủ", use_container_width=True): navigation("home")
    if st.button("📜 Lịch sử đánh giá", use_container_width=True): navigation("history")
    st.divider()
    search_q = st.text_input("🔍 Tìm kiếm", "")
    return search_q