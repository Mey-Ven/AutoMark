import streamlit as st
import os
import sys

# Ajouter le répertoire parent au chemin d'importation
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.dashboard.utils.data_loader import DataLoader
from src.dashboard.pages.home import render_home_page
from src.dashboard.pages.attendance_stats import render_attendance_stats_page
from src.dashboard.pages.student_details import render_student_details_page
from src.dashboard.pages.reports import render_reports_page
from src.dashboard.utils.plotly_config import apply_french_layout


def main():
    """
    Point d'entrée principal de l'application Streamlit.
    """
    # Configuration de la page
    st.set_page_config(
        page_title="AutoMark - Tableau de bord de présence",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Configuration locale pour Plotly (pour avoir les graphiques en français)
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'fr_FR')
        except:
            pass

    # Masquer le menu par défaut de Streamlit et tous les éléments non désirés
    # Charger le fichier CSS externe
    css_file_path = os.path.join(os.path.dirname(__file__), 'utils/style.css')
    with open(css_file_path, 'r') as f:
        css = f.read()

    # Appliquer le CSS
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

    # CSS supplémentaire pour masquer spécifiquement le menu du haut
    hide_top_menu = """
    <style>
    /* Masquer le menu du haut avec les liens en anglais */
    .main-nav {display: none !important;}
    nav {display: none !important;}
    .css-1d391kg {display: none !important;}
    .css-1lsmgbg {display: none !important;}
    .st-emotion-cache-1cypcdb {display: none !important;}

    /* Masquer les liens spécifiques */
    a[href="app"], a[href="attendance_stats"], a[href="home"], a[href="init"], a[href="reports"], a[href="student_details"] {display: none !important;}
    </style>
    """
    st.markdown(hide_top_menu, unsafe_allow_html=True)

    # Chemin vers le répertoire de données
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))

    # Créer l'instance de DataLoader
    data_loader = DataLoader(data_dir)

    # Créer la barre latérale pour la navigation
    st.sidebar.title("AutoMark")
    st.sidebar.image("https://img.icons8.com/color/96/000000/face-recognition.png", width=100)

    # Menu de navigation
    pages = {
        "Accueil": render_home_page,
        "Statistiques de présence": render_attendance_stats_page,
        "Détails des étudiants": render_student_details_page,
        "Rapports": render_reports_page
    }

    # Sélecteur de page
    selection = st.sidebar.radio("Navigation", list(pages.keys()))

    # Afficher la page sélectionnée
    pages[selection](data_loader)

    # Pied de page
    st.sidebar.markdown("---")
    st.sidebar.info(
        "AutoMark - Système intelligent de reconnaissance faciale pour la gestion automatisée de la présence des étudiants."
    )


if __name__ == "__main__":
    main()
