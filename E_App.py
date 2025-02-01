import streamlit as st
import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def initialize_database():
    conn = sqlite3.connect("users_data.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)")
    conn.commit()
    conn.close()

def create_user_table(username):
    conn = sqlite3.connect("users_data.db")
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS user_{username} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT
        )
    """)
    conn.commit()
    conn.close()

def register_user(username, password):
    conn = sqlite3.connect("users_data.db")
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        create_user_table(username)
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect("users_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row and row[0] == hash_password(password)

def save_user_data(username, data):
    conn = sqlite3.connect("users_data.db")
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO user_{username} (data) VALUES (?)", (data,))
    conn.commit()
    conn.close()

def get_user_data(username):
    conn = sqlite3.connect("users_data.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM user_{username}")
    data = cursor.fetchall()
    conn.close()
    return data

initialize_database()
st.title("Connexion / Inscription")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""

if not st.session_state["logged_in"]:
    option = st.radio("Choisissez une option", ["Se connecter", "Créer un compte"])
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")
    
    if option == "Créer un compte":
        if st.button("S'inscrire"):
            if register_user(username, password):
                st.success("Compte créé avec succès. Connectez-vous maintenant.")
            else:
                st.error("Ce nom d'utilisateur est déjà pris.")
    
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
    new_data = st.text_area("Ajoutez des informations :")
    if st.button("Sauvegarder"):
        save_user_data(st.session_state["username"], new_data)
        st.success("Données enregistrées avec succès !")
    
    if st.button("Voir mes données"):
        data = get_user_data(st.session_state["username"])
        for row in data:
            st.write(row[1])
    
    st.button("Déconnexion", on_click=lambda: st.session_state.update({"logged_in": False, "username": ""}))

with st.sidebar:
    pg = st.navigation([st.Page("E_Shop.py", title="🛒 Boutique"),st.Page("E_Quiz.py", title = "🎯 Quiz interactif"), st.Page("E_H.py", title = "📚 Aide aux devoirs"), st.Page("E_R.py", title = "📒 Créateur de fiches de révision"), st.Page("E_T.py", title= "📝 Créateur de contrôle"), st.Page("E_Help.py", title= "⭐💎 Aide")])

pg.run()

