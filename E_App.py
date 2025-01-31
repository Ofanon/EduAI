import streamlit as st
from streamlit_lottie import st_lottie
import db_manager as db
user_id = db.get_user_id()
db.initialize_user()  # 🔄 Assure l’initialisation de l’utilisateur

st.write(f"🔍 DEBUG - Votre ID utilisateur : `{user_id}`")

# Vérification en base SQLite
DB_FILE = "data/request_logs.db"
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("SELECT user_id, experience_points, requests FROM users WHERE user_id = ?", (user_id,))
user_data = cursor.fetchone()

if user_data:
    st.success(f"✅ Utilisateur retrouvé en base ! ID : {user_data[0]}, XP : {user_data[1]}, Étoiles restantes : {user_data[2]}")
else:
    st.error("❌ Utilisateur introuvable en base ! Vérifie `initialize_user()`.")

conn.close()
with st.sidebar:
    st.write(f"⭐ Etoiles restantes : {db.get_requests_left()}")
    pg = st.navigation([st.Page("E_Shop.py", title="🛒 Boutique"),st.Page("E_Quiz.py", title = "🎯 Quiz interactif"), st.Page("E_H.py", title = "📚 Aide aux devoirs"), st.Page("E_R.py", title = "📒 Créateur de fiches de révision"), st.Page("E_T.py", title= "📝 Créateur de contrôle"), st.Page("E_Help.py", title= "⭐💎 Aide")])

pg.run()

