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



def setup_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('index.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open("BlogPhilippe").sheet1
    return sheet

def generer_contenu(theme, section):
    # Dictionnaire de prompts pour chaque section
    prompts = {
        "Formule": f"Générer un contenu captivant pour promouvoir une formule de dépôt à partir de 99€ pour le thème {theme}.",
        "Titre 2": f"Expliquer l'importance de la protection de la propriété intellectuelle pour {theme}, en se concentrant sur les enjeux éthiques et économiques.",
        "Block renfort": f"Créer un contenu qui met en avant les avantages et la reconnaissance juridique de la protection de la propriété intellectuelle pour {theme}.",
        "Block de 3 steps": f"Décrire un processus en trois étapes pour enregistrer et protéger une création intellectuelle dans le domaine de {theme}.",
        "Titres 3": f"Discuter de la législation autour de la protection des œuvres pour {theme}, en mettant l'accent sur les aspects internationaux.",
        "Titre 4": f"Présenter une solution fiable pour protéger les œuvres liées à {theme} contre la contrefaçon et le plagiat.",
        "Titres final": f"Résumer comment Fidealis peut aider à protéger la propriété intellectuelle dans le cadre de {theme}."
    }

    prompt_contenu = prompts.get(section, "Section inconnue")

    # Génération du contenu en utilisant l'API OpenAI
    response_contenu = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Tu es le meilleur rédacteur de contenu."},
            {"role": "user", "content": prompt_contenu}
        ],
        max_tokens=1024
    )

    return response_contenu.choices[0].message['content']




sheet = setup_google_sheets()

# Mapping des sections aux colonnes de la feuille Google Sheets
section_to_col = {
    "Formule": 'A',
    "Titre 2": 'B',
    "Block renfort": 'C',
    "Block de 3 steps": 'D',
    "Titres 3": 'E',
    "Titre 4": 'F',
    "Titres final": 'G'
}


# Interface Streamlit
theme = st.text_input("Entrez le thème du blog")
section = st.selectbox("Choisissez la section pour laquelle générer du contenu",
                       ["Formule", "Titre 2", "Block renfort", "Block de 3 steps", "Titres 3", "Titre 4",
                        "Titres final"])

if 'current_line' not in st.session_state:
    st.session_state['current_line'] = 2  # Commence à la ligne 2

if st.button('Générer le contenu'):
    generated_content = generer_contenu(theme, section)
    st.session_state['contenu_genere'] = generated_content
    st.text_area("Contenu généré", value=generated_content, height=300)

contenu_modifie = st.text_area("Modifier/Ajouter du contenu ici", value=st.session_state.get('contenu_genere', ''))
def sauvegarder_contenu(sheet, ligne, colonne, contenu):
    cellule = f'{colonne}{ligne}'
    sheet.update(cellule, [[contenu]])
    st.success(f"Contenu sauvegardé dans la section '{section}' à la ligne '{ligne}'.")

# Sauvegarder le contenu généré/modifié
if st.button('Sauvegarder le contenu dans la feuille'):
    colonne = section_to_col[section]  # Trouver la colonne correspondante à la section
    sauvegarder_contenu(sheet, st.session_state['current_line'], colonne, contenu_modifie)

# Passer à une nouvelle page
if st.button('Nouvelle Page'):
    st.session_state['current_line'] += 1
    st.session_state.pop('contenu_genere', None)  # Réinitialiser le contenu généré pour la nouvelle page
    st.info(f"Prêt pour la nouvelle page à la ligne {st.session_state['current_line']}.")

