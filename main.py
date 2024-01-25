# Standard library imports
import os

# Related third party imports
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

# Local application/library specific imports
from openai import OpenAI

def generer(theme, openai_client):
    prompt_titre = f"Générer un titre captivant pour un article de blog sur le thème : {theme}."
    response_titre = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Tu es le meuilleurs redacteurs de prompt"},
            {"role": "user", "content": prompt_titre}
        ],
        max_tokens=50
    )
    return response_titre.choices[0].message.content

def sauvegarder_contenu_google_sheet(theme, titre, sheet):
    data = [theme, titre]
    sheet.append_row(data)

def setup_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('index.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open("fidealis web content").sheet1
    return sheet

def generer_et_sauvegarder_titres(openai_client, sheet, elements_list):
    for element in elements_list:
        with st.container():
            theme = st.text_input(f"Entrez le thème du blog pour {element}", key=f"theme_{element}")
            if theme:  # generate title only if theme input is not empty
                if st.button(f'Générer le titre pour {element}', key=f"btn_generate_{element}"):
                    titre_genere = generer(theme, openai_client)
                    titre_modifie = st.text_area("Modifier le titre ici:", titre_genere, key=f"area_{element}")
                    if st.button(f'Sauvegarder les modifications pour {element}', key=f"btn_save_{element}"):
                        sauvegarder_contenu_google_sheet(theme, titre_modifie, sheet)
                        st.success(f"Le contenu modifié pour {element} a été sauvegardé avec succès dans Google Sheets.")

def main():
    OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    sheet = setup_google_sheets()
    elements_list = [
        "TITRE", "Formule", "boutton 1", "Titre 2", "Contenue titre 2", 
        "Contenue  2 titre 2", "Contenue  2 titre 2", "Contenue 3 titre 3", 
        "Block renfort", "Block de 3 steps", "Block de 3 steps", "Boutons 3 steps", 
        "titres 3", "Sous titres", "Contenue 1 titres 1", "Contenue 2 titres 3"
    ]

    st.title('Générateur de contenu de blog avec GPT-4')
    generer_et_sauvegarder_titres(openai_client, sheet, elements_list)

if __name__ == "__main__":
    main()
