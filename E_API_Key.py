import streamlit as st
import secrets
import json

api_key_file = "api_key.json"

def generate_api_key():
    api_key = st.text_input("Entre ta clée API ici.")
    return api_key

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
    
user_id = st.text_input("Entrez votre identifiant utilisateur", placeholder="Exemple : user123")

if user_id:

    api_key = get_api_key(user_id)
    if api_key:
        st.success(f"Votre clé API existante : {api_key}")
    else:
        api_key = generate_api_key()
        save_api_key(user_id, api_key)
        st.session_state["api_key"] = api_key

