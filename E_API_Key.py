import streamlit as st
import json
import hashlib
import requests

users_file = "users.json"
api_key_file = "api_key.json"

if "user_id" not in st.session_state:
    st.session_state["user_id"] = []
if "password" not in st.session_state:
    st.session_state["password"] = None
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "action" not in st.session_state:
    st.session_state["action"] = "Créer un compte"
if "hide_buttons" not in st.session_state:
    st.session_state["hide_buttons"] = False


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    try: 
        with open(users_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_user(user_id, password):
    users = load_users()
    users[user_id] = hash_password(password)
    with open(users_file, "w") as f:
        json.dump(users, f, indent=4)

def authenticate(user_id, password):
    users = load_users()
    hashed_password = users.get(user_id)
    return hashed_password == hash_password(password)

def save_api_key(user_id, api_key):
    try:
        with open(api_key_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    data[user_id] = api_key
    with open(api_key_file, "w") as f:
        json.dump(data, f, indent=4)

def get_api_key(user_id):
    try:
        with open(api_key_file, "r") as f:
            data = json.load(f)
        return data.get(user_id)
    except FileNotFoundError:
        return None

def verify_api_key(api_key):
    url = "https://generativelanguage.googleapis.com/v1beta/models"
    params = {"key": api_key}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        return False

if "connected" not in st.session_state:   
    if st.session_state["action"] == "Créer un compte":
        st.title("Créer un compte EtudIAnt")
        user_id = st.text_input("Créez votre identifiant utilisateur.", placeholder="Exemple : user123")
        password = st.text_input("Créez votre mot de passe.",type="password")
        if not st.session_state["hide_buttons"]:
            if st.button("Créer mon compte"):
                if user_id and password:
                    if user_id in load_users():
                        st.error("L'utilisateur existe déjà.")
                    else:
                        save_user(user_id, password)
                        st.success("Compte créé avec succès.")
                        st.session_state["user_id"] = user_id
                        if authenticate(user_id, password):
                            st.subheader(f"Bienvenue, {user_id} ! Vous êtes connecté.")
                            st.session_state["authenticated"] = True
                        st.session_state["hide_buttons"] = True
                else:
                    st.error("Veuillez remplir tous les champs.")
            elif st.button("Déjà un compte, connectez-vous"):
                st.session_state["action"] = "Se connecter"
                st.rerun()

    elif st.session_state["action"] == "Se connecter":
        st.title("Se connecter à l'EtudIAnt")
        user_id = st.text_input("Entrez votre identifiant utilisateur.", placeholder="Exemple : user123")
        password = st.text_input("Entrez votre mot de passe.",type="password")
        if not st.session_state["hide_buttons"]:
            if st.button("Me connecter"):
                if authenticate(user_id, password):
                    st.subheader(f"Bienvenue, {user_id} !")
                    st.session_state["user_id"] = user_id
                    st.session_state["authenticated"] = True
                    st.session_state["hide_buttons"] = True
                else:
                    st.error("Identifiant ou mot de passe incorrect.")

            elif st.button("Pas de compte ? En créer un"):
                st.session_state["action"] = "Créer un compte"
                st.rerun()


    if st.session_state["authenticated"] == True:
        api_key = get_api_key(user_id)
        if api_key:
            st.session_state["api_key"] = api_key
            st.session_state["connected"] = True
            st.rerun()
            st.session_state["user_id"] = user_id
        else:
            st.subheader("Votre clé API")
            api_key = st.text_input("Entrez une nouvelle clé API")
            if st.button("Enregistrer la clée"):
                if api_key:
                    if verify_api_key(api_key):
                        save_api_key(user_id, api_key)
                        st.session_state["user_id"] = user_id
                        st.success("Clé API enregistrée avec succès.")
                        st.session_state["api_key"] = api_key
                    else:
                        st.error("Veuillez entrer un clé API valide.")
                else:
                    st.error("Veuillez entrer une clé API.")
if "connected" not in st.session_state:
    st.link_button("Pas de clé API Gemini ? Cliquez ici","https://aistudio.google.com/app/u/2/apikey")

if "connected" in st.session_state:
    st.title(f"Vous êtes connecté !")
    st.success(f"Clée API existante : {st.session_state["api_key"]}")
    st.session_state["authenticated"] = True

