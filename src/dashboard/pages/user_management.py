"""
Module pour la gestion des utilisateurs dans l'application AutoMark.
"""

import streamlit as st
import pandas as pd
import hashlib
from src.database.db_manager import DBManager

def render_user_management(data_loader, auth_manager):
    """
    Affiche la page de gestion des utilisateurs.
    
    Args:
        data_loader: Chargeur de données
        auth_manager: Gestionnaire d'authentification
    """
    st.title("Gestion des utilisateurs")
    
    # Vérifier que l'utilisateur est un administrateur
    if not auth_manager.is_admin():
        st.error("Vous n'avez pas les droits d'accès à cette page.")
        return
    
    # Créer une instance du gestionnaire de base de données
    db_manager = DBManager(data_loader.data_dir)
    
    # Créer des onglets pour les différentes fonctionnalités
    tab1, tab2, tab3, tab4 = st.tabs(["Liste des utilisateurs", "Ajouter un utilisateur", "Modifier un utilisateur", "Supprimer un utilisateur"])
    
    # Onglet 1: Liste des utilisateurs
    with tab1:
        st.subheader("Liste des utilisateurs")
        
        # Récupérer la liste des utilisateurs
        users = db_manager.get_users()
        
        if not users:
            st.info("Aucun utilisateur trouvé.")
        else:
            # Convertir la liste en DataFrame pour l'affichage
            users_df = pd.DataFrame(users)
            
            # Renommer les colonnes pour l'affichage
            users_df = users_df.rename(columns={
                "id": "ID",
                "username": "Nom d'utilisateur",
                "role": "Rôle",
                "created_at": "Date de création",
                "last_login": "Dernière connexion"
            })
            
            # Traduire les rôles
            role_mapping = {
                "admin": "Administrateur",
                "teacher": "Enseignant",
                "student": "Étudiant"
            }
            users_df["Rôle"] = users_df["Rôle"].map(role_mapping)
            
            # Afficher le tableau
            st.dataframe(users_df)
    
    # Onglet 2: Ajouter un utilisateur
    with tab2:
        st.subheader("Ajouter un utilisateur")
        
        # Formulaire d'ajout d'utilisateur
        with st.form("add_user_form"):
            username = st.text_input("Nom d'utilisateur", key="add_username")
            password = st.text_input("Mot de passe", type="password", key="add_password")
            role = st.selectbox("Rôle", ["admin", "teacher", "student"], format_func=lambda x: role_mapping.get(x, x), key="add_role")
            
            # Champs spécifiques au rôle
            if role == "student":
                # Récupérer la liste des étudiants
                students = data_loader.get_students()
                student_options = [f"{row['StudentID']} - {row['FirstName']} {row['LastName']}" for _, row in students.iterrows()]
                student_option = st.selectbox("Étudiant", [""] + student_options, key="add_student")
                student_id = student_option.split(" - ")[0] if student_option else ""
            elif role == "teacher":
                # Récupérer la liste des cours
                courses = data_loader.get_courses()
                course_options = [f"{row['CourseID']} - {row['CourseName']}" for _, row in courses.iterrows()]
                course_selections = st.multiselect("Cours", course_options, key="add_courses")
                course_ids = [selection.split(" - ")[0] for selection in course_selections]
            
            # Bouton de soumission
            submit_button = st.form_submit_button("Ajouter")
            
            if submit_button:
                if not username or not password:
                    st.error("Veuillez remplir tous les champs obligatoires.")
                else:
                    # Préparer les données de l'utilisateur
                    user_data = {
                        "username": username,
                        "password": password,
                        "role": role
                    }
                    
                    # Ajouter les données spécifiques au rôle
                    if role == "student" and student_id:
                        user_data["student_id"] = student_id
                    elif role == "teacher" and course_ids:
                        user_data["courses"] = course_ids
                    
                    # Ajouter l'utilisateur
                    if db_manager.add_user(user_data):
                        st.success(f"L'utilisateur {username} a été ajouté avec succès.")
                        # Réinitialiser les champs du formulaire
                        st.session_state["add_username"] = ""
                        st.session_state["add_password"] = ""
                        st.session_state["add_role"] = "admin"
                        if "add_student" in st.session_state:
                            st.session_state["add_student"] = ""
                        if "add_courses" in st.session_state:
                            st.session_state["add_courses"] = []
                    else:
                        st.error(f"Erreur lors de l'ajout de l'utilisateur {username}.")
    
    # Onglet 3: Modifier un utilisateur
    with tab3:
        st.subheader("Modifier un utilisateur")
        
        # Récupérer la liste des utilisateurs
        users = db_manager.get_users()
        
        if not users:
            st.info("Aucun utilisateur trouvé.")
        else:
            # Créer une liste d'options pour le sélecteur
            user_options = [f"{user['id']} - {user['username']} ({role_mapping.get(user['role'], user['role'])})" for user in users]
            user_option = st.selectbox("Sélectionner un utilisateur", [""] + user_options, key="edit_user")
            
            if user_option:
                user_id = int(user_option.split(" - ")[0])
                
                # Récupérer les informations de l'utilisateur
                user = db_manager.get_user_by_id(user_id)
                
                if user:
                    # Formulaire de modification
                    with st.form("edit_user_form"):
                        username = st.text_input("Nom d'utilisateur", value=user["username"], key="edit_username")
                        password = st.text_input("Nouveau mot de passe (laisser vide pour ne pas changer)", type="password", key="edit_password")
                        role = st.selectbox("Rôle", ["admin", "teacher", "student"], index=["admin", "teacher", "student"].index(user["role"]), format_func=lambda x: role_mapping.get(x, x), key="edit_role")
                        
                        # Champs spécifiques au rôle
                        if role == "student":
                            # Récupérer la liste des étudiants
                            students = data_loader.get_students()
                            student_options = [f"{row['StudentID']} - {row['FirstName']} {row['LastName']}" for _, row in students.iterrows()]
                            student_option = st.selectbox("Étudiant", [""] + student_options, key="edit_student")
                            student_id = student_option.split(" - ")[0] if student_option else ""
                        elif role == "teacher":
                            # Récupérer la liste des cours
                            courses = data_loader.get_courses()
                            course_options = [f"{row['CourseID']} - {row['CourseName']}" for _, row in courses.iterrows()]
                            course_selections = st.multiselect("Cours", course_options, key="edit_courses")
                            course_ids = [selection.split(" - ")[0] for selection in course_selections]
                        
                        # Bouton de soumission
                        submit_button = st.form_submit_button("Modifier")
                        
                        if submit_button:
                            if not username:
                                st.error("Le nom d'utilisateur ne peut pas être vide.")
                            else:
                                # Préparer les données de l'utilisateur
                                user_data = {
                                    "username": username,
                                    "role": role
                                }
                                
                                # Ajouter le mot de passe s'il a été modifié
                                if password:
                                    user_data["password"] = password
                                
                                # Ajouter les données spécifiques au rôle
                                if role == "student" and student_id:
                                    user_data["student_id"] = student_id
                                elif role == "teacher" and course_ids:
                                    user_data["courses"] = course_ids
                                
                                # Mettre à jour l'utilisateur
                                if db_manager.update_user(user_id, user_data):
                                    st.success(f"L'utilisateur {username} a été modifié avec succès.")
                                    # Réinitialiser le sélecteur
                                    st.session_state["edit_user"] = ""
                                else:
                                    st.error(f"Erreur lors de la modification de l'utilisateur {username}.")
    
    # Onglet 4: Supprimer un utilisateur
    with tab4:
        st.subheader("Supprimer un utilisateur")
        
        # Récupérer la liste des utilisateurs
        users = db_manager.get_users()
        
        if not users:
            st.info("Aucun utilisateur trouvé.")
        else:
            # Créer une liste d'options pour le sélecteur
            user_options = [f"{user['id']} - {user['username']} ({role_mapping.get(user['role'], user['role'])})" for user in users]
            user_option = st.selectbox("Sélectionner un utilisateur", [""] + user_options, key="delete_user")
            
            if user_option:
                user_id = int(user_option.split(" - ")[0])
                username = user_option.split(" - ")[1].split(" (")[0]
                
                # Demander confirmation
                st.warning(f"Êtes-vous sûr de vouloir supprimer l'utilisateur {username} ?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Oui, supprimer", key="confirm_delete"):
                        # Supprimer l'utilisateur
                        if db_manager.delete_user(user_id):
                            st.success(f"L'utilisateur {username} a été supprimé avec succès.")
                            # Réinitialiser le sélecteur
                            st.session_state["delete_user"] = ""
                        else:
                            st.error(f"Erreur lors de la suppression de l'utilisateur {username}.")
                with col2:
                    if st.button("Non, annuler", key="cancel_delete"):
                        # Réinitialiser le sélecteur
                        st.session_state["delete_user"] = ""
