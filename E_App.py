import streamlit as st
import db_manager
import uuid
import re
import os
import socket
import requests
import hashlib

def get_public_ip():
    """Récupère l'adresse IP publique de l'utilisateur."""
    try:
        response = requests.get("https://api64.ipify.org?format=text", timeout=5)
        ip = response.text
    except requests.RequestException:
        ip = "Inconnue"
    return ip

def generate_device_id():
    """Génère un identifiant unique du périphérique stocké localement."""
    if "device_id" not in st.session_state:
        st.session_state["device_id"] = str(uuid.uuid4())
    return st.session_state["device_id"]

def generate_user_id(first_name, device_id, ip):
    """Génère un identifiant unique basé sur le prénom, l'ID du périphérique et l'IP publique."""
    user_id = hashlib.sha256(f"{first_name}_{device_id}_{ip}".encode()).hexdigest()
    return user_id

# Demander le prénom lors de la première connexion
if "first_name" not in st.session_state:
    st.session_state["first_name"] = st.text_input("Entrez votre prénom :", key="first_name_input")
    if st.session_state["first_name"]:
        st.session_state["user_confirmed"] = True
        st.rerun()

if "user_confirmed" in st.session_state and st.session_state["first_name"]:
    first_name = st.session_state["first_name"]
    device_id = generate_device_id()
    ip_address = get_public_ip()
    user_id = generate_user_id(first_name, device_id, ip_address)

    # Vérifier si un identifiant de session existe déjà, sinon en créer un
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())

    session_id = st.session_state["session_id"]
    st.session_state["user_id"] = user_id

    st.title("Bienvenue sur l'App EtudIAnt")
    st.write(f"Bonjour {first_name}!")
    st.write(f"Votre identifiant unique : `{user_id}`")
    st.write(f"Votre identifiant de session : `{session_id}`")
    st.write(f"Votre identifiant de périphérique : `{device_id}`")
    st.write(f"Votre adresse IP publique : `{ip_address}`")

    # Afficher les points d'expérience et les requêtes restantes
    points = db_manager.get_experience_points(user_id)
    requests_left = db_manager.get_requests_left(user_id)

    st.write(f"Points d'expérience : `{points}`")
    st.write(f"Requêtes restantes : `{requests_left}`")

    # Ajouter des points et des requêtes (exemple d'interaction)
    if st.button("Gagner 10 points d'expérience"):
        db_manager.update_experience_points(user_id, 10)
        st.success("10 points ajoutés !")
        st.rerun()

    if st.button("Acheter 1 requête avec 20 points"):
        if points >= 20:
            db_manager.update_experience_points(user_id, -20)
            db_manager.update_requests(user_id, 1)
            st.success("1 requête ajoutée !")
            st.rerun()
        else:
            st.error("Pas assez de points pour acheter une requête.")

    if st.button("Utiliser une requête"):
        if requests_left > 0:
            db_manager.update_requests(user_id, -1)
            st.success("Requête utilisée !")
            st.rerun()
        else:
            st.error("Vous n'avez plus de requêtes disponibles.")

with st.sidebar:
    st.write(f"⭐ Etoiles restantes : {db_manager.get_requests_left()}")
    pg = st.navigation([st.Page("E_Shop.py", title="🛒 Boutique"),st.Page("E_Quiz.py", title = "🎯 Quiz interactif"), st.Page("E_H.py", title = "📚 Aide aux devoirs"), st.Page("E_R.py", title = "📒 Créateur de fiches de révision"), st.Page("E_T.py", title= "📝 Créateur de contrôle"), st.Page("E_Help.py", title= "⭐💎 Aide")])

pg.run()

