import streamlit as st
import json
import hashlib

users_file = "users.json"
api_key_file = "api_key.json"

if "user_id" not in st.session_state:
    st.session_state["user_id"] = None
if "password" not in st.session_state:
    st.session_state["password"] = None
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

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
    users[user_id] = hash_password(password)
    return users.get(user_id) == hash_password(password)

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

st.title("Connexion à l'EtudIAnt")

action = st.sidebar.selectbox("Selectionnez :", ["Se connecter", "Créer un compte"])

if action == "Créer un compte":
    st.session_state["authenticated"] = False
    user_id = st.text_input("Créez votre identifiant utilisateur.", placeholder="Exemple : user123")
    password = st.text_input("Créez votre mot de passe.",type="password")
    if st.button("Valider"):
        if user_id and password:
            if user_id in load_users():
                st.error("L'utilisateur existe déjà")
            else:
                save_user(user_id, password)
                st.success("Compte créé avec succès. Veuillez vous connecter maintenant")
    else:
            st.error("Veuillez remplir tous les champs.")

elif action == "Se connecter":
    user_id = st.text_input("Entrez votre identifiant utilisateur.", placeholder="Exemple : user123")
    password = st.text_input("Entrez votre mot de passe.",type="password")
    if st.button("Valider"):
        if authenticate(user_id, password):
            st.success(f"Bienvenue, {user_id}!")
            st.session_state["authenticated"] = True
        else:
            st.error("Identifiant ou mot de passe incorrect.")

if st.session_state["authenticated"] == True:
    st.subheader("Votre clé API")
    api_key = get_api_key(user_id)
    if api_key:
        st.success(f"Clée API existante : {api_key}")
        st.session_state["api_key"] = api_key
    else:
        new_api_key = st.text_input("Entrez une nouvelle clé API")
        if st.button("Enregistrer la clée"):
            if new_api_key:
                save_api_key(user_id, new_api_key)
                st.success("Clé API enregistrée avec succès.")
                st.session_state["api_key"] = new_api_key
            else:
                st.error("Veuillez entrer une clé API.")



