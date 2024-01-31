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

def sauvegarder_contenu_google_sheet(theme, section, contenu):
    sheet = setup_google_sheets()

    # Dictionnaire associant chaque section à une ligne spécifique
    lignes_sections = {
        "Formule": 2,
        "Titre 2": 3,
        "Block renfort": 4,
        "Block de 3 steps": 5,
        "Titres 3": 6,
        "Titre 4": 7,
        "Titres final": 8
    }

    ligne = lignes_sections.get(section)

    if ligne:
        # Écrire le contenu dans la ligne spécifiée pour la section donnée
        # La colonne A contient le thème, la colonne B la section, et la colonne C le contenu
        sheet.update(f'A{ligne}:C{ligne}', [[theme, section, contenu]])
        st.success(f"Le contenu pour '{section}' a été sauvegardé avec succès dans Google Sheets.")
    else:
        st.error("Section non reconnue. Impossible de sauvegarder.")


# Interface Streamlit pour la génération de contenu
theme = st.text_input("Entrez le thème du blog")

section = st.selectbox("Choisissez la section pour laquelle générer du contenu",
                       ["Formule", "Titre 2", "Block renfort", "Block de 3 steps", "Titres 3", "Titre 4",
                        "Titres final"])

if st.button(f'Générer le contenu pour {section}'):
    contenu_genere = generer_contenu(theme, section)
    st.session_state['contenu_genere'] = contenu_genere
    st.write(contenu_genere)

# Zone de texte pour modification du contenu généré
if 'contenu_genere' in st.session_state:
    contenu_modifie = st.text_area("Modifier le contenu ici", value=st.session_state['contenu_genere'])
else:
    st.write("Veuillez générer du contenu pour une section.")
if st.button('Sauvegarder les modifications', key='save_content'):
    if 'contenu_genere' in st.session_state and theme and section:
        # Assurez-vous de passer le contenu modifié `contenu_modifie` à la fonction de sauvegarde
        sauvegarder_contenu_google_sheet(theme, section, contenu_modifie)
    else:
        st.error("Merci de générer du contenu avant de sauvegarder.")
