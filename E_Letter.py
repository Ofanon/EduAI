import streamlit as st
import google.generativeai as genai
import json
import requests
import re

genai.configure(api_key=st.secrets["API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash-002")

st.title("EtudIAnt : Créateur de lettre de motivation")

if "letter_started" not in st.session_state:
    st.session_state.letter = False
    st.session_state.name = None
    st.session_state.last_name = None
    st.session_state.level_letter = None
    st.session_state.subject_letter = None
    st.session_state.business = None

if st.session_state.letter is False:
    st.session_state.name = st.text_input("Ton prénom :")
    st.session_state.last_name = st.text_input("Ton nom de famille :")
    st.session_state.level_letter = st.checkbox("Le sujet de ta lettre :", ["Stage d'observation", "demande"] )
    st.session_state.subject_letter = None
    st.session_state.business = None
