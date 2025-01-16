import streamlit as st

st.write("Pour utilisier l'IA EtudIAnt, tu dois rendre sur le site de google")
st.link_button("https://aistudio.google.com/app/u/2/apikey")
st.write("Une fois connecté à Google, appuis sur le bouton créer une clée API")
st.write("Reviens ensuite sur cette page et rentre ta clée api ici :")

api_key = st.text_input("Clée API")