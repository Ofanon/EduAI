import streamlit as st
from user_manager import load_users
import user_manager

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
st.write("🔍 Utilisateurs en mémoire :", load_users())  # Vérifie ce qui est chargé

with st.sidebar:
    pg = st.navigation([
        st.Page("auth_page.py", title="🔑 Connexion à l'EtudIAnt"),
        st.Page("shop_page.py", title="🛒 Boutique"),
        st.Page("quiz_page.py", title="🎯 Quiz interactif"),
        st.Page("homework_page.py", title="📚 Aide aux devoirs"),
        st.Page("revision_sheet_page.py", title="📒 Créateur de fiches de révision"),
        st.Page("test_page.py", title="📝 Créateur de contrôle"),
        st.Page("help_page.py", title="⭐💎 Aide")
    ])
    st.write(f"⭐ Etoiles : {user_manager.get_requests_left()}")
    st.write(f"💎 Points d'experience : {user_manager.get_experience_points()}")

if st.session_state.authenticated:
    if st.sidebar.button("🔴 Se déconnecter"):
        st.session_state["authenticated"] = False
        st.session_state.pop("username", None)
        st.session_state.pop("experience_points", None)
        st.session_state.pop("requests", None)
        st.success("✅ Déconnecté avec succès !")
        st.switch_page("pages/auth_page.py")
        st.stop()

pg.run()
