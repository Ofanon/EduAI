import streamlit as st
from streamlit_lottie import st_lottie
import requests


# Fonction pour charger une animation Lottie
def load_lottieurl(url):
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json()

# Charger une animation Lottie pour un design visuel
lottie_shop = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_jcikwtux.json")

# Titre du shop
st.title("🛒 Bienvenue dans le Shop des Gemmes 💎")

# Animation de présentation
st_lottie(lottie_shop, height=300, key="shop_animation")

# Définir le nombre de gemmes de l'utilisateur
if "gemmes" not in st.session_state:
    st.session_state["gemmes"] = 0

st.subheader(f"💰 Vous avez actuellement : **{st.session_state['gemmes']}** gemmes")

# Colonne des items disponibles
st.markdown("### Sélectionnez vos gemmes :")

# Layout avec colonnes pour différents packs de gemmes
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 💎 Pack Petit")
    st.image("https://via.placeholder.com/150", caption="10 Gemmes", use_column_width=True)
    if st.button("Acheter - 2€", key="pack_petit"):
        st.session_state["gemmes"] += 10
        st.success("Vous avez acheté 10 gemmes !")

with col2:
    st.markdown("#### 💎 Pack Moyen")
    st.image("https://via.placeholder.com/150", caption="50 Gemmes", use_column_width=True)
    if st.button("Acheter - 8€", key="pack_moyen"):
        st.session_state["gemmes"] += 50
        st.success("Vous avez acheté 50 gemmes !")

with col3:
    st.markdown("#### 💎 Pack Grand")
    st.image("https://via.placeholder.com/150", caption="200 Gemmes", use_column_width=True)
    if st.button("Acheter - 20€", key="pack_grand"):
        st.session_state["gemmes"] += 200
        st.success("Vous avez acheté 200 gemmes !")

# Ligne séparatrice
st.markdown("---")

# Section des gemmes disponibles
st.subheader("✨ Vos gemmes")
st.metric("Total de gemmes :", st.session_state["gemmes"])
st.balloons()  # Effet visuel pour célébrer l'achat

