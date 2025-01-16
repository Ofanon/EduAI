import streamlit as st

api_key = st.text_input("Clée API")
if api_key:
    st.session_state["api_key"] = api_key