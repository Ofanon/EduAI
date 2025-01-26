import streamlit as st
from google.oauth2.credentials import Credentials
import google_auth_oauthlib.flow

# Chemin vers votre fichier JSON
CREDENTIALS_FILE = 'client_secrets.json'

# Scopes nécessaires pour l'accès à l'API
SCOPES = ['https://www.googleapis.com/auth/cloud-platform']

# Fonction pour obtenir les identifiants de l'utilisateur
@st.cache_data(ttl=3600)
def get_credentials():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CREDENTIALS_FILE, scopes=SCOPES)

    # Définir le redirect URI (utilisez directement la valeur ici)
    flow.redirect_uri = "votre_redirect_uri"  # Remplacez par votre redirect URI

    # Récupérer le code d'autorisation
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    # Afficher le lien d'autorisation
    st.write(f"Veuillez autoriser l'accès à votre compte Google : [Lien]({authorization_url})")

    # Récupérer le code d'autorisation depuis l'URL de redirection
    code = st.experimental_get_query_params()['code']

    # Échanger le code d'autorisation contre des jetons d'accès
    flow.fetch_token(code=code)
    credentials = flow.credentials
    return credentials

# Interface Streamlit
st.title("Authentification Google")

# Authentification avec le fichier JSON
credentials = get_credentials()

# Afficher les informations de l'utilisateur si l'authentification réussit
if credentials:
    st.success("Connecté avec succès !")
    st.write(f"Token d'accès : {credentials.token}")