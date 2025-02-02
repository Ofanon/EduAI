import streamlit as st
import user_manager as db
import pandas as pd

st.title("🏆 Classement des meilleurs joueurs")

def get_leaderboard():
    db.cursor.execute("SELECT user_id, experience_points FROM users ORDER BY experience_points DESC LIMIT 10")
    rows = db.cursor.fetchall()
    return pd.DataFrame(rows, columns=["Utilisateur", "XP"])

leaderboard = get_leaderboard()

if leaderboard.empty:
    st.warning("Aucun joueur classé pour l’instant.")
else:
    st.dataframe(leaderboard)
