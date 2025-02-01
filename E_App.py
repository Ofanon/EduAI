import streamlit as st
import db_manager
import hashlib
import sqlite3

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user_table(username):
    conn = sqlite3.connect("users_data.db")
    cursor = conn.cursor()
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS user_{username} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT
        )
    ''')
    conn.commit()
    conn.close()

def register_user(username, password):
    conn = sqlite3.connect("users_data.db")
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()
    create_user_table(username)

def authenticate_user(username, password):
    conn = sqlite3.connect("users_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0] == hash_password(password):
        return True
    return False

st.title("Login / Sign Up")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    option = st.selectbox("Choisissez une option", ["Se connecter", "Créer un compte"])
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")
    
    if option == "Créer un compte":
        if st.button("S'inscrire"):
            conn = sqlite3.connect("users_data.db")
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                st.error("Ce nom d'utilisateur est déjà pris.")
            else:
                register_user(username, password)
                st.success("Compte créé avec succès. Connectez-vous maintenant.")
            conn.close()
    
    elif option == "Se connecter":
        if st.button("Connexion"):
            if authenticate_user(username, password):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success("Connexion réussie !")
                st.rerun()
            else:
                st.error("Nom d'utilisateur ou mot de passe incorrect.")

if st.session_state["logged_in"]:
    st.write(f"Bienvenue, {st.session_state['username']} !")
    st.button("Déconnexion", on_click=lambda: st.session_state.update({"logged_in": False, "username": None}))


with st.sidebar:
    pg = st.navigation([st.Page("E_Shop.py", title="🛒 Boutique"),st.Page("E_Quiz.py", title = "🎯 Quiz interactif"), st.Page("E_H.py", title = "📚 Aide aux devoirs"), st.Page("E_R.py", title = "📒 Créateur de fiches de révision"), st.Page("E_T.py", title= "📝 Créateur de contrôle"), st.Page("E_Help.py", title= "⭐💎 Aide")])

pg.run()

