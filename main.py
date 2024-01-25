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
    # Dictionnaire pour stocker les titres générés
    generated_titles = {}

    # Générerez tous les titres et contenus dès le premier titre saisi
    trigger_key = "trigger_generation"
    if st.button("Générer tout les titres et contenus", key=trigger_key):
        for element in elements_list:
            generated_titles[element] = generer(element, openai_client)

    # Pour chaque élément, l'utilisateur peut modifier, régénérer ou sauvegarder individuellement
    for index, element in enumerate(elements_list):
        with st.container():
            theme_key = f"theme_{element}_{index}"
            theme = generated_titles.get(element) or st.text_input(f"Entrez le thème du blog pour {element}", key=theme_key)

            # Possibilité de régénérer un titre/contenu individuellement
            btn_regenerate_key = f"btn_regenerate_{element}_{index}"
            if st.button(f'Régénérer le titre pour {element}', key=btn_regenerate_key):
                generated_titles[element] = generer(theme, openai_client)

            # Champs d'édition pour les titres/contenus
            area_key = f"area_{element}_{index}"
            titre_modifie = st.text_area("Modifier le titre ici:", generated_titles.get(element, ""), key=area_key)

            # Possibilité de sauvegarder un titre/contenu individuellement
            btn_save_key = f"btn_save_{element}_{index}"
            if st.button(f'Sauvegarder les modifications pour {element}', key=btn_save_key):
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
