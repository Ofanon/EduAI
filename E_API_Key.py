import streamlit as st

api_key = st.text_input("Clée API")
st.session_state["api_key"] = api_key