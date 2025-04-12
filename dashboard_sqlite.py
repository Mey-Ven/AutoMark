"""
Application Streamlit pour le système de gestion de présence AutoMark.
Version corrigée qui n'utilise que les modules existants.
"""

import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime

# Ajouter le répertoire src au chemin Python
sys.path.append(os.path.abspath("."))

# Importer les modules nécessaires
from src.dashboard.pages.home import render_home_page
from src.dashboard.pages.admin_sqlite import render_admin_page  # Interface d'administration pour SQLite
from src.dashboard.pages.face_recognition import render_face_recognition_page
from src.dashboard.pages.reports import render_reports_page
# Utiliser les modules existants pour les pages étudiant et enseignant
from src.dashboard.pages.student_home import render_student_home
from src.dashboard.pages.teacher_home import render_teacher_home
from src.dashboard.utils.db_data_loader import DBDataLoader
from src.dashboard.utils.auth_sqlite import authenticate, is_authenticated, get_user_role, logout

# Initialiser le chargeur de données
data_loader = DBDataLoader("data")

# Configurer la page Streamlit
st.set_page_config(
    page_title="AutoMark - Système de Gestion de Présence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fonction principale
def main():
    # Vérifier si l'utilisateur est authentifié
    if not is_authenticated():
        # Afficher le formulaire de connexion
        with st.form("login_form"):
            st.title("Connexion")
            username = st.text_input("Nom d'utilisateur")
            password = st.text_input("Mot de passe", type="password")
            submitted = st.form_submit_button("Se connecter")

            if submitted:
                if authenticate(username, password):
                    st.success(f"Connexion réussie en tant que {username}")
                    st.rerun()
                else:
                    st.error("Nom d'utilisateur ou mot de passe incorrect")
    else:
        # Afficher la barre latérale
        with st.sidebar:
            st.title("AutoMark")
            st.write(f"Connecté en tant que: **{st.session_state.username}**")

            # Obtenir le rôle de l'utilisateur
            user_role = get_user_role(st.session_state.username)

            # Afficher les options de navigation en fonction du rôle
            if user_role == "admin":
                page = st.radio("Navigation", ["Accueil", "Administration", "Reconnaissance Faciale", "Rapports"])
            elif user_role == "teacher":
                page = st.radio("Navigation", ["Accueil", "Enseignant", "Reconnaissance Faciale", "Rapports"])
            else:  # student
                page = st.radio("Navigation", ["Accueil", "Étudiant"])

            # Bouton de déconnexion
            if st.button("Déconnexion"):
                logout()
                st.rerun()

        # Afficher la page sélectionnée
        if page == "Accueil":
            render_home_page(data_loader)
        elif page == "Administration" and user_role == "admin":
            render_admin_page(data_loader)
        elif page == "Enseignant" and user_role == "teacher":
            render_teacher_home(data_loader)  # Utiliser render_teacher_home au lieu de render_teacher_page
        elif page == "Étudiant" and user_role == "student":
            render_student_home(data_loader)  # Utiliser render_student_home au lieu de render_student_page
        elif page == "Reconnaissance Faciale" and (user_role == "admin" or user_role == "teacher"):
            render_face_recognition_page(data_loader)
        elif page == "Rapports" and (user_role == "admin" or user_role == "teacher"):
            render_reports_page(data_loader)

# Exécuter l'application
if __name__ == "__main__":
    main()
