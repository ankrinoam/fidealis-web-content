import os

# Related third party imports
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
from openai import OpenAI
print("API Key-----------------------")
print(os.environ['OPENAI_API_KEY'])
print("API Key-----------------------")

openai_client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# Local application/library specific imports

scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('index.json', scope)
client = gspread.authorize(creds)
sheet = client.open("BlogPhilippe").sheet1



def generer_fonction_titre(nom_fonction, prompt_base, model_default="gpt-3.5-turbo", max_tokens_default=50, system_message_default="Tu es le meilleur rédacteur de prompt"):
    def fonction_dynamique(theme, model=model_default, max_tokens=max_tokens_default, system_message=system_message_default):
        prompt_titre = prompt_base.format(theme=theme)
        response_titre = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt_titre}
            ],
            max_tokens=max_tokens
        )
        return response_titre.choices[0].message.content

    fonction_dynamique.__name__ = nom_fonction
    return fonction_dynamique

# Utilisation
generer_titre = generer_fonction_titre("generer_titre", "Générer un titre captivant pour un article de blog sur le thème : {theme}.")
if st.button('Générer le titre'):
    st.session_state.titre_genere = generer_titre(theme)

titre_modifie = st.text_area("Modifier le titre ici", st.session_state.titre_genere if 'titre_genere' in st.session_state else '')
