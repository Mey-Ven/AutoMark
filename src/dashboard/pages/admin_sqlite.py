"""
Module pour l'interface d'administration simplifiée.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

def render_admin_page(data_loader):
    """
    Affiche la page d'administration.
    
    Args:
        data_loader: Chargeur de données
    """
    st.title("Administration")
    
    # Créer des onglets pour les différentes sections
    tab1, tab2, tab3 = st.tabs(["Cours", "Étudiants", "Présences"])
    
    # Onglet Cours
    with tab1:
        st.header("Gestion des Cours")
        
        # Afficher les cours existants
        courses_df = data_loader.get_courses()
        st.subheader("Cours existants")
        st.dataframe(courses_df)
        
        # Formulaire d'ajout de cours
        st.subheader("Ajouter un cours")
        with st.form(key="add_course_form"):
            col1, col2 = st.columns(2)
            with col1:
                course_name = st.text_input("Nom du cours")
                instructor = st.text_input("Enseignant")
            with col2:
                group = st.selectbox("Groupe", ["Groupe A", "Groupe B", "Groupe C"])
                schedule = st.text_input("Horaire (ex: Lundi 10h-12h)")
            
            submit_button = st.form_submit_button(label="Ajouter le cours")
            
            if submit_button and course_name and instructor:
                course_id = data_loader.add_course(course_name, instructor, group, schedule)
                if course_id:
                    st.success(f"Cours '{course_name}' ajouté avec succès! ID: {course_id}")
                    st.rerun()
                else:
                    st.error(f"Erreur lors de l'ajout du cours '{course_name}'")
        
        # Formulaire de modification de cours
        st.subheader("Modifier un cours")
        course_id_to_update = st.selectbox(
            "Sélectionner un cours à modifier",
            options=courses_df["CourseID"].tolist() if not courses_df.empty else [],
            format_func=lambda x: f"{courses_df[courses_df['CourseID'] == x]['CourseName'].iloc[0]} ({x})" if not courses_df.empty else x
        )
        
        if course_id_to_update:
            course_to_update = courses_df[courses_df["CourseID"] == course_id_to_update].iloc[0]
            
            with st.form(key="update_course_form"):
                col1, col2 = st.columns(2)
                with col1:
                    updated_name = st.text_input("Nom du cours", value=course_to_update["CourseName"])
                    updated_instructor = st.text_input("Enseignant", value=course_to_update["Instructor"])
                with col2:
                    updated_group = st.selectbox("Groupe", ["Groupe A", "Groupe B", "Groupe C"], index=["Groupe A", "Groupe B", "Groupe C"].index(course_to_update["Group"]) if course_to_update["Group"] in ["Groupe A", "Groupe B", "Groupe C"] else 0)
                    updated_schedule = st.text_input("Horaire", value=course_to_update["Schedule"])
                
                update_button = st.form_submit_button(label="Mettre à jour le cours")
                
                if update_button:
                    success = data_loader.update_course(
                        course_id_to_update,
                        updated_name,
                        updated_instructor,
                        updated_group,
                        updated_schedule
                    )
                    if success:
                        st.success(f"Cours '{updated_name}' mis à jour avec succès!")
                        st.rerun()
                    else:
                        st.error(f"Erreur lors de la mise à jour du cours '{updated_name}'")
        
        # Formulaire de suppression de cours
        st.subheader("Supprimer un cours")
        course_id_to_delete = st.selectbox(
            "Sélectionner un cours à supprimer",
            options=courses_df["CourseID"].tolist() if not courses_df.empty else [],
            format_func=lambda x: f"{courses_df[courses_df['CourseID'] == x]['CourseName'].iloc[0]} ({x})" if not courses_df.empty else x,
            key="delete_course_select"
        )
        
        if course_id_to_delete:
            course_to_delete = courses_df[courses_df["CourseID"] == course_id_to_delete].iloc[0]
            st.warning(f"Vous êtes sur le point de supprimer le cours '{course_to_delete['CourseName']}'. Cette action est irréversible.")
            
            if st.button("Confirmer la suppression", key="confirm_delete_course"):
                success = data_loader.delete_course(course_id_to_delete)
                if success:
                    st.success(f"Cours '{course_to_delete['CourseName']}' supprimé avec succès!")
                    st.rerun()
                else:
                    st.error(f"Erreur lors de la suppression du cours '{course_to_delete['CourseName']}'")
    
    # Onglet Étudiants
    with tab2:
        st.header("Gestion des Étudiants")
        
        # Afficher les étudiants existants
        students_df = data_loader.get_students()
        st.subheader("Étudiants existants")
        st.dataframe(students_df)
        
        # Formulaire d'ajout d'étudiant
        st.subheader("Ajouter un étudiant")
        with st.form(key="add_student_form"):
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("Prénom")
                last_name = st.text_input("Nom")
            with col2:
                group = st.selectbox("Groupe", ["Groupe A", "Groupe B", "Groupe C"])
            
            submit_button = st.form_submit_button(label="Ajouter l'étudiant")
            
            if submit_button and first_name and last_name:
                student_id = data_loader.add_student(first_name, last_name, group)
                if student_id:
                    st.success(f"Étudiant '{first_name} {last_name}' ajouté avec succès! ID: {student_id}")
                    st.rerun()
                else:
                    st.error(f"Erreur lors de l'ajout de l'étudiant '{first_name} {last_name}'")
        
        # Formulaire de modification d'étudiant
        st.subheader("Modifier un étudiant")
        student_id_to_update = st.selectbox(
            "Sélectionner un étudiant à modifier",
            options=students_df["StudentID"].tolist() if not students_df.empty else [],
            format_func=lambda x: f"{students_df[students_df['StudentID'] == x]['FirstName'].iloc[0]} {students_df[students_df['StudentID'] == x]['LastName'].iloc[0]} ({x})" if not students_df.empty else x
        )
        
        if student_id_to_update:
            student_to_update = students_df[students_df["StudentID"] == student_id_to_update].iloc[0]
            
            with st.form(key="update_student_form"):
                col1, col2 = st.columns(2)
                with col1:
                    updated_first_name = st.text_input("Prénom", value=student_to_update["FirstName"])
                    updated_last_name = st.text_input("Nom", value=student_to_update["LastName"])
                with col2:
                    updated_group = st.selectbox("Groupe", ["Groupe A", "Groupe B", "Groupe C"], index=["Groupe A", "Groupe B", "Groupe C"].index(student_to_update["Group"]) if student_to_update["Group"] in ["Groupe A", "Groupe B", "Groupe C"] else 0)
                
                update_button = st.form_submit_button(label="Mettre à jour l'étudiant")
                
                if update_button:
                    success = data_loader.update_student(
                        student_id_to_update,
                        updated_first_name,
                        updated_last_name,
                        updated_group
                    )
                    if success:
                        st.success(f"Étudiant '{updated_first_name} {updated_last_name}' mis à jour avec succès!")
                        st.rerun()
                    else:
                        st.error(f"Erreur lors de la mise à jour de l'étudiant '{updated_first_name} {updated_last_name}'")
        
        # Formulaire de suppression d'étudiant
        st.subheader("Supprimer un étudiant")
        student_id_to_delete = st.selectbox(
            "Sélectionner un étudiant à supprimer",
            options=students_df["StudentID"].tolist() if not students_df.empty else [],
            format_func=lambda x: f"{students_df[students_df['StudentID'] == x]['FirstName'].iloc[0]} {students_df[students_df['StudentID'] == x]['LastName'].iloc[0]} ({x})" if not students_df.empty else x,
            key="delete_student_select"
        )
        
        if student_id_to_delete:
            student_to_delete = students_df[students_df["StudentID"] == student_id_to_delete].iloc[0]
            student_name = f"{student_to_delete['FirstName']} {student_to_delete['LastName']}"
            st.warning(f"Vous êtes sur le point de supprimer l'étudiant '{student_name}'. Cette action est irréversible.")
            
            if st.button("Confirmer la suppression", key="confirm_delete_student"):
                success = data_loader.delete_student(student_id_to_delete)
                if success:
                    st.success(f"Étudiant '{student_name}' supprimé avec succès!")
                    st.rerun()
                else:
                    st.error(f"Erreur lors de la suppression de l'étudiant '{student_name}'")
    
    # Onglet Présences
    with tab3:
        st.header("Gestion des Présences")
        
        # Afficher les présences existantes
        attendance_df = data_loader.get_attendance()
        st.subheader("Présences existantes")
        st.dataframe(attendance_df)
        
        # Formulaire d'ajout de présence
        st.subheader("Ajouter une présence")
        with st.form(key="add_attendance_form"):
            col1, col2 = st.columns(2)
            with col1:
                course_id_for_attendance = st.selectbox(
                    "Cours",
                    options=courses_df["CourseID"].tolist() if not courses_df.empty else [],
                    format_func=lambda x: f"{courses_df[courses_df['CourseID'] == x]['CourseName'].iloc[0]} ({x})" if not courses_df.empty else x
                )
                student_id_for_attendance = st.selectbox(
                    "Étudiant",
                    options=students_df["StudentID"].tolist() if not students_df.empty else [],
                    format_func=lambda x: f"{students_df[students_df['StudentID'] == x]['FirstName'].iloc[0]} {students_df[students_df['StudentID'] == x]['LastName'].iloc[0]} ({x})" if not students_df.empty else x
                )
            with col2:
                attendance_date = st.date_input("Date", value=datetime.now())
                attendance_status = st.radio("Statut", ["Présent", "Absent"])
                attendance_method = st.selectbox("Méthode", ["Manuel", "Reconnaissance faciale", "Autre"])
            
            submit_button = st.form_submit_button(label="Ajouter la présence")
            
            if submit_button and course_id_for_attendance and student_id_for_attendance:
                date_str = attendance_date.strftime("%Y-%m-%d")
                status_str = "present" if attendance_status == "Présent" else "absent"
                
                attendance_id = data_loader.add_attendance(
                    course_id_for_attendance,
                    student_id_for_attendance,
                    date_str,
                    status_str,
                    attendance_method
                )
                
                if attendance_id:
                    st.success(f"Présence ajoutée avec succès! ID: {attendance_id}")
                    st.rerun()
                else:
                    st.error("Erreur lors de l'ajout de la présence. Un enregistrement existe peut-être déjà pour cet étudiant, ce cours et cette date.")
        
        # Formulaire de suppression de présence
        st.subheader("Supprimer une présence")
        attendance_id_to_delete = st.selectbox(
            "Sélectionner une présence à supprimer",
            options=attendance_df["ID"].tolist() if not attendance_df.empty else [],
            format_func=lambda x: f"ID: {x}" if not attendance_df.empty else x
        )
        
        if attendance_id_to_delete:
            attendance_to_delete = attendance_df[attendance_df["ID"] == attendance_id_to_delete].iloc[0]
            st.warning(f"Vous êtes sur le point de supprimer la présence avec l'ID '{attendance_id_to_delete}'. Cette action est irréversible.")
            
            if st.button("Confirmer la suppression", key="confirm_delete_attendance"):
                success = data_loader.delete_attendance(attendance_id_to_delete)
                if success:
                    st.success(f"Présence supprimée avec succès!")
                    st.rerun()
                else:
                    st.error(f"Erreur lors de la suppression de la présence")
