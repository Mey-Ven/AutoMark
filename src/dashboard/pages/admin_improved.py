import streamlit as st
import pandas as pd
import os
import json
import uuid
import csv
from datetime import datetime, timedelta

def render_admin_page(data_loader):
    st.title("Administration")

    # Créer des onglets pour les différentes sections d'administration
    tabs = st.tabs(["Cours", "Étudiants", "Présences"])

    # Onglet Cours
    with tabs[0]:
        manage_courses(data_loader)

    # Onglet Étudiants
    with tabs[1]:
        manage_students(data_loader)

    # Onglet Présences
    with tabs[2]:
        manage_attendance(data_loader)

def manage_courses(data_loader):
    st.header("Gestion des Cours")

    # Charger les données des cours
    courses_df = data_loader.get_courses()
    
    # Créer des colonnes pour organiser la mise en page
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Liste des cours")
        
        # Ajouter une barre de recherche
        search_term = st.text_input("Rechercher un cours", key="search_courses")
        
        # Filtrer les cours en fonction du terme de recherche
        if search_term and not courses_df.empty:
            filtered_courses = courses_df[
                courses_df['CourseName'].str.contains(search_term, case=False) | 
                courses_df['CourseID'].str.contains(search_term, case=False) |
                courses_df['Instructor'].str.contains(search_term, case=False)
            ]
        else:
            filtered_courses = courses_df
        
        # Afficher les cours dans un tableau interactif
        if not filtered_courses.empty:
            # Créer une copie du DataFrame pour éviter les avertissements de modification
            display_df = filtered_courses.copy()
            
            # Afficher le tableau
            edited_df = st.data_editor(
                display_df,
                column_config={
                    "CourseID": st.column_config.TextColumn("ID", disabled=True),
                    "CourseName": st.column_config.TextColumn("Nom du cours"),
                    "Instructor": st.column_config.TextColumn("Enseignant"),
                    "Group": st.column_config.TextColumn("Groupe"),
                    "Schedule": st.column_config.TextColumn("Horaire")
                },
                hide_index=True,
                use_container_width=True,
                key="courses_table"
            )
            
            # Détecter les modifications
            if not edited_df.equals(display_df):
                # Mettre à jour le fichier CSV
                edited_df.to_csv(data_loader.courses_file, index=False)
                st.success("Cours mis à jour avec succès!")
                # Recharger les données
                data_loader.reload_data()
                st.experimental_rerun()
            
            # Ajouter des boutons pour chaque ligne
            for i, row in filtered_courses.iterrows():
                course_id = row['CourseID']
                col_edit, col_delete = st.columns([1, 1])
                
                with col_edit:
                    if st.button(f"Modifier", key=f"edit_{course_id}"):
                        st.session_state.edit_course_id = course_id
                        st.session_state.edit_course_mode = True
                
                with col_delete:
                    if st.button(f"Supprimer", key=f"delete_{course_id}"):
                        # Demander confirmation
                        st.session_state.delete_course_id = course_id
                        st.session_state.delete_course_name = row['CourseName']
                        st.session_state.confirm_delete_course = True
                
                st.markdown("---")
        else:
            st.info("Aucun cours trouvé.")
    
    with col2:
        # Gestion de la suppression
        if 'confirm_delete_course' in st.session_state and st.session_state.confirm_delete_course:
            st.subheader(f"Supprimer le cours {st.session_state.delete_course_name}?")
            st.warning("Cette action est irréversible!")
            
            col_cancel, col_confirm = st.columns([1, 1])
            
            with col_cancel:
                if st.button("Annuler"):
                    st.session_state.confirm_delete_course = False
            
            with col_confirm:
                if st.button("Confirmer", type="primary"):
                    # Supprimer le cours
                    courses_df = courses_df[courses_df['CourseID'] != st.session_state.delete_course_id]
                    courses_df.to_csv(data_loader.courses_file, index=False)
                    st.success(f"Cours {st.session_state.delete_course_name} supprimé avec succès!")
                    
                    # Réinitialiser l'état
                    st.session_state.confirm_delete_course = False
                    
                    # Recharger les données
                    data_loader.reload_data()
                    st.experimental_rerun()
        
        # Gestion de la modification
        elif 'edit_course_mode' in st.session_state and st.session_state.edit_course_mode:
            st.subheader("Modifier un cours")
            
            # Récupérer les informations du cours
            course_to_edit = courses_df[courses_df['CourseID'] == st.session_state.edit_course_id].iloc[0]
            
            # Formulaire de modification
            with st.form("edit_course_form"):
                course_name = st.text_input("Nom du cours", value=course_to_edit['CourseName'])
                instructor = st.text_input("Enseignant", value=course_to_edit['Instructor'])
                group = st.text_input("Groupe", value=course_to_edit['Group'])
                schedule = st.text_input("Horaire", value=course_to_edit['Schedule'])
                
                col_cancel, col_save = st.columns([1, 1])
                
                with col_cancel:
                    cancel_button = st.form_submit_button("Annuler")
                
                with col_save:
                    save_button = st.form_submit_button("Enregistrer")
                
                if cancel_button:
                    st.session_state.edit_course_mode = False
                    st.experimental_rerun()
                
                if save_button:
                    # Mettre à jour le cours
                    courses_df.loc[courses_df['CourseID'] == st.session_state.edit_course_id, 'CourseName'] = course_name
                    courses_df.loc[courses_df['CourseID'] == st.session_state.edit_course_id, 'Instructor'] = instructor
                    courses_df.loc[courses_df['CourseID'] == st.session_state.edit_course_id, 'Group'] = group
                    courses_df.loc[courses_df['CourseID'] == st.session_state.edit_course_id, 'Schedule'] = schedule
                    
                    # Sauvegarder les modifications
                    courses_df.to_csv(data_loader.courses_file, index=False)
                    
                    st.success("Cours mis à jour avec succès!")
                    
                    # Réinitialiser l'état
                    st.session_state.edit_course_mode = False
                    
                    # Recharger les données
                    data_loader.reload_data()
                    st.experimental_rerun()
        
        # Formulaire d'ajout
        else:
            st.subheader("Ajouter un nouveau cours")
            
            with st.form("add_course_form"):
                # Générer un ID unique
                course_id = f"C{str(uuid.uuid4())[:6].upper()}"
                
                course_name = st.text_input("Nom du cours")
                instructor = st.text_input("Enseignant")
                group = st.selectbox("Groupe", ["Groupe A", "Groupe B", "Groupe C"])
                schedule = st.text_input("Horaire (ex: Lundi 10h-12h)")
                
                submitted = st.form_submit_button("Ajouter")
                
                if submitted and course_name and instructor:
                    # Vérifier si le cours existe déjà
                    if not courses_df.empty and course_name in courses_df['CourseName'].values:
                        st.error(f"Un cours avec le nom '{course_name}' existe déjà!")
                    else:
                        # Créer un nouveau cours
                        new_course = pd.DataFrame({
                            'CourseID': [course_id],
                            'CourseName': [course_name],
                            'Instructor': [instructor],
                            'Group': [group],
                            'Schedule': [schedule]
                        })
                        
                        # Ajouter le nouveau cours
                        if courses_df.empty:
                            updated_courses = new_course
                        else:
                            updated_courses = pd.concat([courses_df, new_course], ignore_index=True)
                        
                        # Sauvegarder les modifications
                        updated_courses.to_csv(data_loader.courses_file, index=False)
                        
                        st.success(f"Cours '{course_name}' ajouté avec succès!")
                        
                        # Recharger les données
                        data_loader.reload_data()
                        st.experimental_rerun()

def manage_students(data_loader):
    st.header("Gestion des Étudiants")

    # Charger les données des étudiants
    students_df = data_loader.get_students()
    
    # Charger les données des cours pour l'association
    courses_df = data_loader.get_courses()
    
    # Créer des colonnes pour organiser la mise en page
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Liste des étudiants")
        
        # Ajouter une barre de recherche
        search_term = st.text_input("Rechercher un étudiant", key="search_students")
        
        # Filtrer les étudiants en fonction du terme de recherche
        if search_term and not students_df.empty:
            filtered_students = students_df[
                students_df['FirstName'].str.contains(search_term, case=False) | 
                students_df['LastName'].str.contains(search_term, case=False) |
                students_df['StudentID'].str.contains(search_term, case=False) |
                students_df['Group'].str.contains(search_term, case=False)
            ]
        else:
            filtered_students = students_df
        
        # Afficher les étudiants dans un tableau interactif
        if not filtered_students.empty:
            # Créer une copie du DataFrame pour éviter les avertissements de modification
            display_df = filtered_students.copy()
            
            # Afficher le tableau
            edited_df = st.data_editor(
                display_df,
                column_config={
                    "StudentID": st.column_config.TextColumn("ID", disabled=True),
                    "FirstName": st.column_config.TextColumn("Prénom"),
                    "LastName": st.column_config.TextColumn("Nom"),
                    "Group": st.column_config.TextColumn("Groupe")
                },
                hide_index=True,
                use_container_width=True,
                key="students_table"
            )
            
            # Détecter les modifications
            if not edited_df.equals(display_df):
                # Mettre à jour le fichier CSV
                edited_df.to_csv(data_loader.students_file, index=False)
                st.success("Étudiant mis à jour avec succès!")
                # Recharger les données
                data_loader.reload_data()
                st.experimental_rerun()
            
            # Ajouter des boutons pour chaque ligne
            for i, row in filtered_students.iterrows():
                student_id = row['StudentID']
                col_edit, col_delete = st.columns([1, 1])
                
                with col_edit:
                    if st.button(f"Modifier", key=f"edit_student_{student_id}"):
                        st.session_state.edit_student_id = student_id
                        st.session_state.edit_student_mode = True
                
                with col_delete:
                    if st.button(f"Supprimer", key=f"delete_student_{student_id}"):
                        # Demander confirmation
                        st.session_state.delete_student_id = student_id
                        st.session_state.delete_student_name = f"{row['FirstName']} {row['LastName']}"
                        st.session_state.confirm_delete_student = True
                
                st.markdown("---")
        else:
            st.info("Aucun étudiant trouvé.")
    
    with col2:
        # Gestion de la suppression
        if 'confirm_delete_student' in st.session_state and st.session_state.confirm_delete_student:
            st.subheader(f"Supprimer l'étudiant {st.session_state.delete_student_name}?")
            st.warning("Cette action est irréversible!")
            
            col_cancel, col_confirm = st.columns([1, 1])
            
            with col_cancel:
                if st.button("Annuler", key="cancel_delete_student"):
                    st.session_state.confirm_delete_student = False
            
            with col_confirm:
                if st.button("Confirmer", key="confirm_delete_student", type="primary"):
                    # Supprimer l'étudiant
                    students_df = students_df[students_df['StudentID'] != st.session_state.delete_student_id]
                    students_df.to_csv(data_loader.students_file, index=False)
                    st.success(f"Étudiant {st.session_state.delete_student_name} supprimé avec succès!")
                    
                    # Réinitialiser l'état
                    st.session_state.confirm_delete_student = False
                    
                    # Recharger les données
                    data_loader.reload_data()
                    st.experimental_rerun()
        
        # Gestion de la modification
        elif 'edit_student_mode' in st.session_state and st.session_state.edit_student_mode:
            st.subheader("Modifier un étudiant")
            
            # Récupérer les informations de l'étudiant
            student_to_edit = students_df[students_df['StudentID'] == st.session_state.edit_student_id].iloc[0]
            
            # Formulaire de modification
            with st.form("edit_student_form"):
                first_name = st.text_input("Prénom", value=student_to_edit['FirstName'])
                last_name = st.text_input("Nom", value=student_to_edit['LastName'])
                group = st.selectbox("Groupe", ["Groupe A", "Groupe B", "Groupe C"], index=["Groupe A", "Groupe B", "Groupe C"].index(student_to_edit['Group']) if student_to_edit['Group'] in ["Groupe A", "Groupe B", "Groupe C"] else 0)
                
                col_cancel, col_save = st.columns([1, 1])
                
                with col_cancel:
                    cancel_button = st.form_submit_button("Annuler")
                
                with col_save:
                    save_button = st.form_submit_button("Enregistrer")
                
                if cancel_button:
                    st.session_state.edit_student_mode = False
                    st.experimental_rerun()
                
                if save_button:
                    # Mettre à jour l'étudiant
                    students_df.loc[students_df['StudentID'] == st.session_state.edit_student_id, 'FirstName'] = first_name
                    students_df.loc[students_df['StudentID'] == st.session_state.edit_student_id, 'LastName'] = last_name
                    students_df.loc[students_df['StudentID'] == st.session_state.edit_student_id, 'Group'] = group
                    
                    # Sauvegarder les modifications
                    students_df.to_csv(data_loader.students_file, index=False)
                    
                    st.success("Étudiant mis à jour avec succès!")
                    
                    # Réinitialiser l'état
                    st.session_state.edit_student_mode = False
                    
                    # Recharger les données
                    data_loader.reload_data()
                    st.experimental_rerun()
        
        # Formulaire d'ajout
        else:
            st.subheader("Ajouter un nouvel étudiant")
            
            with st.form("add_student_form"):
                # Générer un ID unique
                student_id = f"S{str(uuid.uuid4())[:6].upper()}"
                
                first_name = st.text_input("Prénom")
                last_name = st.text_input("Nom")
                group = st.selectbox("Groupe", ["Groupe A", "Groupe B", "Groupe C"])
                
                submitted = st.form_submit_button("Ajouter")
                
                if submitted and first_name and last_name:
                    # Créer un nouvel étudiant
                    new_student = pd.DataFrame({
                        'StudentID': [student_id],
                        'FirstName': [first_name],
                        'LastName': [last_name],
                        'Group': [group]
                    })
                    
                    # Ajouter le nouvel étudiant
                    if students_df.empty:
                        updated_students = new_student
                    else:
                        updated_students = pd.concat([students_df, new_student], ignore_index=True)
                    
                    # Sauvegarder les modifications
                    updated_students.to_csv(data_loader.students_file, index=False)
                    
                    st.success(f"Étudiant '{first_name} {last_name}' ajouté avec succès!")
                    
                    # Recharger les données
                    data_loader.reload_data()
                    st.experimental_rerun()

def manage_attendance(data_loader):
    st.header("Gestion des Présences")

    # Charger les données
    attendance_df = data_loader.get_attendance()
    students_df = data_loader.get_students()
    courses_df = data_loader.get_courses()
    
    # Créer des colonnes pour organiser la mise en page
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Enregistrements de présence")
        
        # Filtres
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            # Filtre par cours
            course_filter = st.selectbox(
                "Filtrer par cours",
                ["Tous les cours"] + courses_df['CourseName'].tolist() if not courses_df.empty else ["Tous les cours"],
                key="attendance_course_filter"
            )
        
        with filter_col2:
            # Filtre par date
            date_filter = st.date_input(
                "Filtrer par date",
                value=None,
                key="attendance_date_filter"
            )
        
        with filter_col3:
            # Filtre par étudiant
            student_options = ["Tous les étudiants"]
            if not students_df.empty:
                student_options += [f"{row['FirstName']} {row['LastName']}" for _, row in students_df.iterrows()]
            
            student_filter = st.selectbox(
                "Filtrer par étudiant",
                student_options,
                key="attendance_student_filter"
            )
        
        # Appliquer les filtres
        filtered_attendance = attendance_df.copy() if not attendance_df.empty else pd.DataFrame()
        
        if not filtered_attendance.empty:
            if course_filter != "Tous les cours" and not courses_df.empty:
                course_id = courses_df[courses_df['CourseName'] == course_filter]['CourseID'].iloc[0]
                filtered_attendance = filtered_attendance[filtered_attendance['CourseID'] == course_id]
            
            if date_filter is not None:
                date_str = date_filter.strftime("%Y-%m-%d")
                filtered_attendance = filtered_attendance[filtered_attendance['Date'] == date_str]
            
            if student_filter != "Tous les étudiants" and not students_df.empty:
                first_name, last_name = student_filter.split(" ", 1)
                student_id = students_df[(students_df['FirstName'] == first_name) & (students_df['LastName'] == last_name)]['StudentID'].iloc[0]
                filtered_attendance = filtered_attendance[filtered_attendance['StudentID'] == student_id]
        
        # Préparer les données pour l'affichage
        if not filtered_attendance.empty:
            display_records = []
            
            for idx, record in filtered_attendance.iterrows():
                course_name = "Inconnu"
                if 'CourseID' in record and not courses_df.empty:
                    course_matches = courses_df[courses_df['CourseID'] == record['CourseID']]
                    if not course_matches.empty:
                        course_name = course_matches['CourseName'].iloc[0]
                
                student_name = "Inconnu"
                if 'StudentID' in record and not students_df.empty:
                    student_matches = students_df[students_df['StudentID'] == record['StudentID']]
                    if not student_matches.empty:
                        student_name = f"{student_matches['FirstName'].iloc[0]} {student_matches['LastName'].iloc[0]}"
                
                status = "Présent"
                if 'Status' in record:
                    status = "Présent" if record['Status'] == 'present' else "Absent"
                
                display_records.append({
                    "ID": idx,
                    "Date": record.get('Date', ''),
                    "Cours": course_name,
                    "Étudiant": student_name,
                    "Présent": status,
                })
            
            # Créer un DataFrame pour l'affichage
            if display_records:
                display_df = pd.DataFrame(display_records)
                
                # Afficher le tableau
                st.dataframe(
                    display_df,
                    hide_index=True,
                    use_container_width=True
                )
                
                # Ajouter des boutons pour les actions globales
                col_export, col_delete = st.columns([1, 1])
                
                with col_export:
                    if st.button("Exporter les données filtrées (CSV)"):
                        # Exporter les données filtrées
                        csv_data = filtered_attendance.to_csv(index=False)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        st.download_button(
                            label="Télécharger le CSV",
                            data=csv_data,
                            file_name=f"presence_export_{timestamp}.csv",
                            mime="text/csv"
                        )
                
                with col_delete:
                    if st.button("Supprimer les enregistrements filtrés", type="primary"):
                        # Demander confirmation
                        st.session_state.confirm_delete_attendance = True
                        st.session_state.filtered_attendance_indices = filtered_attendance.index.tolist()
            else:
                st.info("Aucun enregistrement de présence trouvé avec les filtres actuels.")
        else:
            st.info("Aucun enregistrement de présence disponible.")
    
    with col2:
        # Gestion de la suppression
        if 'confirm_delete_attendance' in st.session_state and st.session_state.confirm_delete_attendance:
            st.subheader("Supprimer les enregistrements?")
            st.warning(f"Vous êtes sur le point de supprimer {len(st.session_state.filtered_attendance_indices)} enregistrements de présence. Cette action est irréversible!")
            
            col_cancel, col_confirm = st.columns([1, 1])
            
            with col_cancel:
                if st.button("Annuler", key="cancel_delete_attendance"):
                    st.session_state.confirm_delete_attendance = False
            
            with col_confirm:
                if st.button("Confirmer", key="confirm_delete_attendance", type="primary"):
                    # Supprimer les enregistrements
                    attendance_df = attendance_df.drop(st.session_state.filtered_attendance_indices)
                    
                    # Sauvegarder les modifications
                    # Comme les données de présence sont stockées dans des fichiers séparés,
                    # nous devons recréer tous les fichiers
                    attendance_dir = data_loader.attendance_dir
                    os.makedirs(attendance_dir, exist_ok=True)
                    
                    # Grouper par cours et date
                    if not attendance_df.empty:
                        for (course_id, date), group in attendance_df.groupby(['CourseID', 'Date']):
                            filename = f"{course_id}_{date}.csv"
                            file_path = os.path.join(attendance_dir, filename)
                            group.to_csv(file_path, index=False)
                    
                    st.success(f"{len(st.session_state.filtered_attendance_indices)} enregistrements supprimés avec succès!")
                    
                    # Réinitialiser l'état
                    st.session_state.confirm_delete_attendance = False
                    
                    # Recharger les données
                    data_loader.reload_data()
                    st.experimental_rerun()
        
        # Formulaire d'ajout
        else:
            st.subheader("Ajouter un enregistrement de présence")
            
            with st.form("add_attendance_form"):
                # Sélection du cours
                course_options = courses_df['CourseName'].tolist() if not courses_df.empty else []
                if course_options:
                    course = st.selectbox(
                        "Cours",
                        course_options,
                        key="add_attendance_course"
                    )
                    course_id = courses_df[courses_df['CourseName'] == course]['CourseID'].iloc[0]
                else:
                    st.warning("Aucun cours disponible. Veuillez d'abord ajouter des cours.")
                    course_id = None
                
                # Sélection de l'étudiant
                student_options = [f"{row['FirstName']} {row['LastName']}" for _, row in students_df.iterrows()] if not students_df.empty else []
                if student_options:
                    student = st.selectbox(
                        "Étudiant",
                        student_options,
                        key="add_attendance_student"
                    )
                    first_name, last_name = student.split(" ", 1)
                    student_id = students_df[(students_df['FirstName'] == first_name) & (students_df['LastName'] == last_name)]['StudentID'].iloc[0]
                else:
                    st.warning("Aucun étudiant disponible. Veuillez d'abord ajouter des étudiants.")
                    student_id = None
                
                # Date et statut
                date = st.date_input("Date", value=datetime.now())
                status = st.radio("Statut", ["Présent", "Absent"])
                
                submitted = st.form_submit_button("Ajouter")
                
                if submitted and course_id and student_id:
                    # Créer un nouvel enregistrement
                    date_str = date.strftime("%Y-%m-%d")
                    status_str = "present" if status == "Présent" else "absent"
                    
                    # Vérifier si un enregistrement existe déjà pour cet étudiant, ce cours et cette date
                    if not attendance_df.empty:
                        existing = attendance_df[
                            (attendance_df['CourseID'] == course_id) & 
                            (attendance_df['StudentID'] == student_id) & 
                            (attendance_df['Date'] == date_str)
                        ]
                    else:
                        existing = pd.DataFrame()
                    
                    if not existing.empty:
                        st.error("Un enregistrement existe déjà pour cet étudiant, ce cours et cette date!")
                    else:
                        # Créer le fichier de présence s'il n'existe pas
                        attendance_dir = data_loader.attendance_dir
                        os.makedirs(attendance_dir, exist_ok=True)
                        
                        filename = f"{course_id}_{date_str}.csv"
                        file_path = os.path.join(attendance_dir, filename)
                        
                        # Créer ou mettre à jour le fichier
                        if os.path.exists(file_path):
                            # Charger le fichier existant
                            existing_df = pd.read_csv(file_path)
                            
                            # Ajouter le nouvel enregistrement
                            new_record = pd.DataFrame({
                                'CourseID': [course_id],
                                'StudentID': [student_id],
                                'Date': [date_str],
                                'Time': [datetime.now().strftime("%H:%M:%S")],
                                'Status': [status_str]
                            })
                            
                            updated_df = pd.concat([existing_df, new_record], ignore_index=True)
                            updated_df.to_csv(file_path, index=False)
                        else:
                            # Créer un nouveau fichier
                            new_record = pd.DataFrame({
                                'CourseID': [course_id],
                                'StudentID': [student_id],
                                'Date': [date_str],
                                'Time': [datetime.now().strftime("%H:%M:%S")],
                                'Status': [status_str]
                            })
                            
                            new_record.to_csv(file_path, index=False)
                        
                        st.success(f"Enregistrement de présence ajouté avec succès!")
                        
                        # Recharger les données
                        data_loader.reload_data()
                        st.experimental_rerun()
