import streamlit as st
import os
import sys

# Ajouter le répertoire parent au chemin d'importation
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.dashboard.utils.data_loader import DataLoader
from src.dashboard.pages.home import render_home_page
from src.dashboard.pages.attendance_stats import render_attendance_stats_page
from src.dashboard.pages.student_details import render_student_details_page
from src.dashboard.pages.reports import render_reports_page
from src.dashboard.pages.admin_improved import render_admin_page
from src.dashboard.pages.face_recognition import render_face_recognition_page
from src.dashboard.utils.plotly_config import apply_french_layout

# Importer les modules d'authentification et les interfaces spécifiques par rôle
from src.auth import AuthManager
from src.dashboard.pages.login import render_login_page, check_authentication, logout
from src.dashboard.pages.admin_home import render_admin_home
from src.dashboard.pages.teacher_home import render_teacher_home
from src.dashboard.pages.student_home import render_student_home

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

# Masquer le menu par défaut de Streamlit et appliquer les styles personnalisés
hide_menu = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_menu, unsafe_allow_html=True)

# Charger le fichier CSS personnalisé pour le menu
css_file_path = os.path.join(os.path.dirname(__file__), 'src/dashboard/utils/menu_style.css')
with open(css_file_path, 'r') as f:
    css = f.read()
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# Chemin vers le répertoire de données
data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

# Créer l'instance de DataLoader
data_loader = DataLoader(data_dir)

# Créer la barre latérale pour la navigation avec un style amélioré
st.sidebar.title("AutoMark")

# Ajouter du CSS pour s'assurer que le logo n'est pas cliquable et a un style amélioré
st.markdown("""
<style>
    [data-testid="stSidebar"] [data-testid="stImage"] {
        pointer-events: none;  /* Rend l'image non cliquable */
        border-radius: 10px;   /* Coins arrondis */
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);  /* Légère ombre */
        margin: 0 auto;        /* Centrage */
        display: block;        /* Assure que le centrage fonctionne */
        transition: all 0.3s ease;  /* Animation douce */
    }
</style>
""", unsafe_allow_html=True)

# Afficher le logo
st.sidebar.image("https://img.icons8.com/color/96/000000/face-recognition.png", width=100)

# Ajouter un séparateur visuel
st.sidebar.markdown("<div style='margin: 1rem 0; height: 3px; background: linear-gradient(to right, #FF4B4B, transparent);'></div>", unsafe_allow_html=True)

# Utiliser session_state pour conserver l'état du thème
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

# Obtenir l'état actuel du thème pour l'appliquer
dark_mode = st.session_state.dark_mode

# Appliquer le thème en fonction du choix de l'utilisateur
if dark_mode:
    theme_css = """
    <style>
    :root {
        --background-color: #0E1117;
        --text-color: #FAFAFA;
        --card-background: #262730;
        --accent-color: #FF4B4B;
        --secondary-background: #1E2A38;
    }
    </style>
    """
else:
    theme_css = """
    <style>
    :root {
        --background-color: #FFFFFF;
        --text-color: #31333F;
        --card-background: #F0F2F6;
        --accent-color: #FF4B4B;
        --secondary-background: #EAEAEA;
    }
    </style>
    """

# Appliquer le thème
st.markdown(theme_css, unsafe_allow_html=True)

# Initialiser le gestionnaire d'authentification
auth_manager = AuthManager(data_dir)

# Vérifier si l'utilisateur est authentifié
user_info = check_authentication()

# Si l'utilisateur n'est pas authentifié, afficher la page de connexion
if not user_info:
    render_login_page(auth_manager)
    st.stop()  # Arrêter l'exécution pour ne pas afficher le reste de l'interface

# Menu de navigation en fonction du rôle de l'utilisateur
role = user_info['role']

if role == 'admin':
    pages = {
        "Accueil Admin": lambda dl: render_admin_home(dl, auth_manager),
        "Statistiques de présence": render_attendance_stats_page,
        "Détails des étudiants": render_student_details_page,
        "Rapports": render_reports_page,
        "Administration": render_admin_page,
        "Reconnaissance Faciale": render_face_recognition_page,
        "Déconnexion": lambda dl: logout()
    }
elif role == 'teacher':
    pages = {
        "Accueil Enseignant": lambda dl: render_teacher_home(dl, auth_manager),
        "Statistiques de présence": render_attendance_stats_page,
        "Détails des étudiants": render_student_details_page,
        "Rapports": render_reports_page,
        "Reconnaissance Faciale": render_face_recognition_page,
        "Déconnexion": lambda dl: logout()
    }
elif role == 'student':
    pages = {
        "Accueil Étudiant": lambda dl: render_student_home(dl, auth_manager),
        "Mon emploi du temps": render_home_page,
        "Mes présences": render_attendance_stats_page,
        "Déconnexion": lambda dl: logout()
    }
else:
    # Rôle inconnu, afficher un menu limité
    pages = {
        "Accueil": render_home_page,
        "Déconnexion": lambda dl: logout()
    }

# Sélecteur de page avec un style amélioré
st.sidebar.markdown("### Navigation")

# Utiliser des boutons personnalisés au lieu de radio buttons
selection = None

# Style CSS pour indiquer la page active
st.markdown("""
<style>
    /* Style pour le bouton de page active */
    [data-testid="stSidebar"] [data-active="true"] button {
        border-left: 4px solid #FF4B4B !important;
        background-color: rgba(255, 75, 75, 0.2) !important;
        font-weight: bold !important;
        transform: translateX(5px) !important;
    }
</style>
""", unsafe_allow_html=True)

# Stocker la sélection dans session_state pour la conserver entre les rechargements
if 'page_selection' not in st.session_state:
    st.session_state.page_selection = "Accueil"

# Afficher les boutons de navigation
for page in pages.keys():
    # Vérifier si c'est la page active
    is_active = st.session_state.page_selection == page
    button_key = f"btn_{page}"

    # Ajouter un attribut data-active au div parent du bouton
    if is_active:
        st.markdown(f"<style>[data-testid='stSidebar'] [data-key='{button_key}'] {{ data-active: 'true'; }}</style>", unsafe_allow_html=True)

    # Créer le bouton
    if st.sidebar.button(page, key=button_key, use_container_width=True):
        selection = page
        st.session_state.page_selection = page

# Si aucun bouton n'est cliqué, utiliser la première page du menu comme page par défaut
if selection is None:
    # Sélectionner la première page du dictionnaire en fonction du rôle
    selection = list(pages.keys())[0]

# Ajouter une animation de transition entre les pages
st.markdown("""
<style>
    /* Animation de transition pour le contenu principal */
    [data-testid="stAppViewContainer"] > div:nth-child(2) {
        animation: fadeIn 0.5s ease-in-out;
    }

    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(10px); }
        100% { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# Ajouter une animation de chargement lors du changement de page
with st.spinner(f"Chargement de la page {selection}..."):
    # Afficher la page sélectionnée avec un effet de transition
    pages[selection](data_loader)

# Pied de page avec un style amélioré
st.sidebar.markdown("<div style='margin: 2rem 0; height: 2px; background: linear-gradient(to right, transparent, #FF4B4B, transparent);'></div>", unsafe_allow_html=True)

# Ajouter un bouton de basculement du thème dans la barre latérale
st.sidebar.markdown("### Thème")

# Bouton de basculement du thème avec icône
theme_icon = "☀️" if dark_mode else "🌙"
theme_text = "Mode Clair" if dark_mode else "Mode Sombre"
theme_button_label = f"{theme_icon} {theme_text}"

# Style CSS pour le bouton de thème
st.markdown("""
<style>
    /* Style pour le bouton de thème */
    [data-testid="stSidebar"] [data-testid="stButton"] button {
        background-color: var(--secondary-background, #1e2a38) !important;
        color: var(--text-color, #ffffff) !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        font-weight: bold !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2) !important;
        transition: all 0.3s ease !important;
        text-align: left !important;
        width: 100% !important;
    }

    [data-testid="stSidebar"] [data-testid="stButton"] button:hover {
        background-color: rgba(255, 75, 75, 0.2) !important;
        border-left: 4px solid #FF4B4B !important;
        transform: translateX(5px) !important;
    }
</style>
""", unsafe_allow_html=True)

# Bouton de basculement du thème
if st.sidebar.button(theme_button_label, key="theme_toggle_btn", use_container_width=True):
    # Inverser l'état du thème
    st.session_state.dark_mode = not dark_mode
    # Recharger l'application pour appliquer le nouveau thème
    st.rerun()


# Informations sur l'application
st.sidebar.markdown("""
<div style='background-color: rgba(255, 75, 75, 0.1); border-left: 4px solid #FF4B4B; padding: 1rem; border-radius: 5px;'>
<h4 style='margin: 0; color: #ffffff;'>AutoMark</h4>
<p style='margin: 0.5rem 0 0 0; color: #ffffff; font-size: 0.9rem;'>Système intelligent de reconnaissance faciale pour la gestion automatisée de la présence des étudiants.</p>
</div>
""", unsafe_allow_html=True)

# Ajouter des informations de version
st.sidebar.markdown("<div style='text-align: center; color: rgba(255,255,255,0.5); font-size: 0.8rem; margin-top: 2rem;'>Version 1.0.0</div>", unsafe_allow_html=True)
