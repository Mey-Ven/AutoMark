"""
Module d'authentification pour l'application AutoMark avec SQLite.
Ce module fournit des fonctions pour l'authentification des utilisateurs.
"""

import streamlit as st
import time
from typing import Dict, Optional, Tuple

# Utilisateurs par défaut pour la démonstration
DEFAULT_USERS = {
    "admin": {
        "password": "admin",
        "role": "admin",
        "first_name": "Admin",
        "last_name": "User"
    },
    "teacher": {
        "password": "teacher",
        "role": "teacher",
        "first_name": "Teacher",
        "last_name": "User"
    },
    "student": {
        "password": "student",
        "role": "student",
        "first_name": "Student",
        "last_name": "User"
    }
}

def authenticate(username: str, password: str) -> bool:
    """
    Authentifie un utilisateur.
    
    Args:
        username: Nom d'utilisateur
        password: Mot de passe
    
    Returns:
        True si l'authentification réussit, False sinon
    """
    # Vérifier si l'utilisateur existe
    if username in DEFAULT_USERS:
        # Vérifier le mot de passe
        if DEFAULT_USERS[username]["password"] == password:
            # Stocker les informations utilisateur dans la session
            st.session_state.username = username
            st.session_state.role = DEFAULT_USERS[username]["role"]
            st.session_state.first_name = DEFAULT_USERS[username]["first_name"]
            st.session_state.last_name = DEFAULT_USERS[username]["last_name"]
            st.session_state.authenticated = True
            return True
    
    return False

def is_authenticated() -> bool:
    """
    Vérifie si l'utilisateur est authentifié.
    
    Returns:
        True si l'utilisateur est authentifié, False sinon
    """
    return st.session_state.get("authenticated", False)

def get_user_role(username: str) -> str:
    """
    Récupère le rôle d'un utilisateur.
    
    Args:
        username: Nom d'utilisateur
    
    Returns:
        Rôle de l'utilisateur
    """
    if is_authenticated():
        return st.session_state.get("role", "")
    
    return ""

def logout() -> None:
    """
    Déconnecte l'utilisateur en effaçant les données de session.
    """
    if "authenticated" in st.session_state:
        del st.session_state["authenticated"]
    if "username" in st.session_state:
        del st.session_state["username"]
    if "role" in st.session_state:
        del st.session_state["role"]
    if "first_name" in st.session_state:
        del st.session_state["first_name"]
    if "last_name" in st.session_state:
        del st.session_state["last_name"]
