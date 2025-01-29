import streamlit as st
import db_manager as db

st.markdown("""
    <style>
        .shop-container {
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 20px;
            padding-top: 20px;
        }
        .shop-card {
            background: linear-gradient(135deg, #ffdd57, #ffaf00);
            border-radius: 15px;
            padding: 15px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.15);
            text-align: center;
            width: 250px;
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
        }
        .shop-card:hover {
            transform: scale(1.05);
            box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.2);
        }
        .shop-card img {
            width: 80px;
            border-radius: 50%;
            margin-bottom: 10px;
        }
        .shop-card button {
            background: #0084ff;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.3s;
            font-size: 16px;
        }
        .shop-card button:hover {
            background: #005bb5;
        }
    </style>
""", unsafe_allow_html=True)


experience_points = db.get_experience_points()

st.title("🌟 Boutique de l'EtudIAnt 🌟")
st.subheader(f"💎 Vous avez **{experience_points}** points d'expérience.")

st.markdown("---")

# 📦 Conteneur pour les cartes
st.markdown('<div class="shop-container">', unsafe_allow_html=True)

# 📌 Liste des articles (image, nom, prix, quantité)
items = [
    {"image": "star (2).png", "name": "⭐ 5 étoiles", "price": 1000, "amount": 5, "key": "buy_5"},
    {"image": "branding.png", "name": "⭐⭐ 10 étoiles", "price": 2800, "amount": 10, "key": "buy_10"},
    {"image": "star.png", "name": "⭐⭐⭐ 20 étoiles", "price": 5700, "amount": 20, "key": "buy_20"},
]

# 🎁 Affichage des cartes d'achat
for item in items:
    col = st.columns(3)[items.index(item)]  # Utilisation de colonnes pour aligner les cartes
    with col:
        st.markdown(f'''
            <div class="shop-card">
                <img src="{item["image"]}">
                <h3>{item["name"]}</h3>
                <p><b>💎 Prix :</b> {item["price"]} XP</p>
        ''', unsafe_allow_html=True)
        
        # 🎯 Bouton d'achat avec confirmation
        if st.button(f"🛒 Acheter ({item['amount']} étoiles)", key=item["key"]):
            success = db.purchase_requests(cost_in_experience=item["price"], requests_to_add=item["amount"])
            if success:
                st.success(f"✨ {item['amount']} étoiles ajoutées !")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Pas assez de points.")

        st.markdown("</div>", unsafe_allow_html=True)

# 📦 Ferme le conteneur
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ⭐ Affichage du nombre d'étoiles restantes après achat
total_requests = db.get_requests_left()
st.write(f"🌟 **Étoiles restantes** : {total_requests}")
