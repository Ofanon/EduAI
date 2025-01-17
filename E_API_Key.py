import streamlit as st
import json

api_key_file = "api_key.json"
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None
if "password" not in st.session_state:
    st.session_state["password"] = None

def generate_api_key():
    api_key = st.text_input("Entre ta clée API ici.")
    st.text("Si tu ne sais pas comment faire, clique ici sur 'Obtenir une clée API':")
    st.link_button("Obtenir une clée API", "https://aistudio.google.com/app/u/2/apikey",)
    if st.button("Enregistrer la clée API"):
        if not api_key == "":
            return api_key
        else:
            st.error("Veuillez remplir le champ.")

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

user_id = st.text_input("Entrez votre identifiant utilisateur.", placeholder="Exemple : user123")
password = st.text_input("Entrez votre mot de passe.",type="password")

st.session_state["user_id"] = user_id
st.session_state["password"] = password

if user_id:

    api_key = get_api_key(user_id)
    if api_key:
        st.success(f"Votre clé API existante : {api_key}")
        st.session_state["api_key"] = api_key
    else:
        api_key = generate_api_key()
        save_api_key(user_id, api_key)
        st.session_state["api_key"] = api_key

else:
    st.error("Veuillez remplir les deux champs.")

