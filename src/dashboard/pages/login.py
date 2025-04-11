import streamlit as st
import time
from typing import Dict, Optional

def render_login_page(auth_manager):
    """
    Affiche la page de connexion.
    
    Args:
        auth_manager: Gestionnaire d'authentification
    """
    st.title("Connexion à AutoMark")
    
    # Centrer le formulaire de connexion
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Ajouter un logo
        st.image("https://img.icons8.com/color/96/000000/face-recognition.png", width=100)
        
        # Formulaire de connexion
        with st.form("login_form"):
            username = st.text_input("Nom d'utilisateur")
            password = st.text_input("Mot de passe", type="password")
            submit = st.form_submit_button("Se connecter")
            
            if submit:
                if not username or not password:
                    st.error("Veuillez remplir tous les champs.")
                else:
                    # Afficher un spinner pendant l'authentification
                    with st.spinner("Authentification en cours..."):
                        time.sleep(0.5)  # Simuler un délai d'authentification
                        success, user_info = auth_manager.authenticate(username, password)
                        
                    if success:
                        # Stocker les informations utilisateur dans la session
                        st.session_state.user = user_info
                        st.session_state.authenticated = True
                        
                        # Rediriger vers la page d'accueil appropriée selon le rôle
                        if user_info['role'] == 'admin':
                            st.session_state.page_selection = "Accueil Admin"
                        elif user_info['role'] == 'teacher':
                            st.session_state.page_selection = "Accueil Enseignant"
                        elif user_info['role'] == 'student':
                            st.session_state.page_selection = "Accueil Étudiant"
                        
                        # Afficher un message de succès et recharger la page
                        st.success(f"Bienvenue, {user_info['first_name']} {user_info['last_name']}!")
                        st.rerun()
                    else:
                        st.error("Nom d'utilisateur ou mot de passe incorrect.")
        
        # Lien pour réinitialiser le mot de passe (non fonctionnel pour l'instant)
        st.markdown("<div style='text-align: center;'><a href='#' style='color: var(--text-color);'>Mot de passe oublié ?</a></div>", unsafe_allow_html=True)

def check_authentication() -> Optional[Dict]:
    """
    Vérifie si l'utilisateur est authentifié.
    
    Returns:
        Informations utilisateur si authentifié, None sinon
    """
    if 'authenticated' in st.session_state and st.session_state.authenticated:
        return st.session_state.user
    return None

def logout():
    """Déconnecte l'utilisateur en effaçant les données de session."""
    if 'authenticated' in st.session_state:
        del st.session_state.authenticated
    if 'user' in st.session_state:
        del st.session_state.user
    st.session_state.page_selection = "Login"
    st.rerun()
