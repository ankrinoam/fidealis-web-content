# Standard library imports
import os

# Related third party imports
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
from openai import OpenAI

def generer_contenu(openai_client, theme, element):
    prompt = f"Générer du contenu pour '{element}' sur le thème : {theme}."
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un expert en création de contenu de blog"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erreur lors de la génération du contenu pour '{element}': {e}"

def sauvegarder_contenu_google_sheet(client, sheet_name, data):
    try:
        sheet = client.open(sheet_name).sheet1
        sheet.append_row(data)
        return True
    except Exception as e:
        return False, str(e)

def main():
    OPENAI_API_KEY = os.environ['OPENAI_API_KEY'] 
    openai_client = OpenAI(api_key=OPENAI_API_KEY)

    # Google Sheets Configuration
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('index.json', scope)  # Replace 'index.json' with your actual credentials file
    client = gspread.authorize(creds)

    st.title('Générateur de contenu de blog avec GPT-4')

    theme = st.text_input("Entrez le thème du blog")
    elements_list = [
        "TITRE", "Formule", "bouton 1", "Titre 2", "Contenu titre 2", 
        "Contenu 2 titre 2", "Contenu 3 titre 3", "Block renfort", 
        "Block de 3 steps", "Boutons 3 steps", "titres 3", "Sous titres", 
        "Contenu 1 titres 1", "Contenu 2 titres 3"
    ]

    if theme and 'content_generated' not in st.session_state:
        for element in elements_list:
            st.session_state[element] = generer_contenu(openai_client, theme, element)
        st.session_state['content_generated'] = True

    for element in elements_list:
        with st.expander(f"{element}"):
            st.text_area("", st.session_state.get(element, ""), key=f"text_{element}")
            if st.button(f'Régénérer {element}', key=f"btn_{element}"):
                st.session_state[element] = generer_contenu(openai_client, theme, element)
                st.experimental_rerun()

    if st.button('Sauvegarder les modifications'):
        data = [theme]
        for element in elements_list:
            data.append(st.session_state.get(f"text_{element}", ""))
        success, message = sauvegarder_contenu_google_sheet(client, "fidealis web content", data)  # Replace 'BlogPhilippe' with your actual Google Sheets name
        if success:
            st.success("Le contenu modifié a été sauvegardé avec succès dans Google Sheets.")
        else:
            st.error(f"Erreur lors de la sauvegarde : {message}")

if __name__ == "__main__":
    main()
