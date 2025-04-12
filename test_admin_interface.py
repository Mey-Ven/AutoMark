"""
Script de test de l'interface d'administration.
Ce script crée une interface d'administration simplifiée pour tester les fonctionnalités d'ajout, de modification et de suppression.
"""

import streamlit as st
import pandas as pd
import os
import sys
import uuid
from datetime import datetime

# Ajouter le répertoire src au chemin Python
sys.path.append(os.path.abspath("."))

from src.dashboard.utils.db_data_loader import DBDataLoader

def main():
    st.title("Test de l'interface d'administration")
    
    # Initialiser le chargeur de données
    data_loader = DBDataLoader("data")
    
    # Créer des onglets pour les différentes sections d'administration
    tabs = st.tabs(["Cours", "Étudiants", "Présences"])
    
    # Onglet Cours
    with tabs[0]:
        st.header("Gestion des Cours")
        
        # Charger les données des cours
        courses_df = data_loader.get_courses()
        
        # Afficher les cours
        st.subheader("Liste des cours")
        if not courses_df.empty:
            st.dataframe(courses_df)
        else:
            st.info("Aucun cours trouvé.")
        
        # Formulaire d'ajout
        st.subheader("Ajouter un nouveau cours")
        with st.form("add_course_form"):
            course_name = st.text_input("Nom du cours")
            instructor = st.text_input("Enseignant")
            group = st.selectbox("Groupe", ["Groupe A", "Groupe B", "Groupe C"])
            schedule = st.text_input("Horaire (ex: Lundi 10h-12h)")
            
            submitted = st.form_submit_button("Ajouter")
            
            if submitted and course_name and instructor:
                # Ajouter le nouveau cours
                course_id = data_loader.add_course(course_name, instructor, group, schedule)
                
                if course_id:
                    st.success(f"Cours '{course_name}' ajouté avec succès!")
                    st.experimental_rerun()
                else:
                    st.error(f"Un cours avec le nom '{course_name}' existe déjà!")
        
        # Formulaire de modification
        st.subheader("Modifier un cours")
        course_to_modify = st.selectbox("Sélectionner un cours à modifier", courses_df['CourseID'].tolist() if not courses_df.empty else [])
        
        if course_to_modify:
            course_to_edit = courses_df[courses_df['CourseID'] == course_to_modify].iloc[0]
            
            with st.form("edit_course_form"):
                new_course_name = st.text_input("Nom du cours", value=course_to_edit['CourseName'])
                new_instructor = st.text_input("Enseignant", value=course_to_edit['Instructor'])
                new_group = st.text_input("Groupe", value=course_to_edit['Group'])
                new_schedule = st.text_input("Horaire", value=course_to_edit['Schedule'])
                
                submitted = st.form_submit_button("Modifier")
                
                if submitted:
                    # Mettre à jour le cours
                    success = data_loader.update_course(course_to_modify, new_course_name, new_instructor, new_group, new_schedule)
                    
                    if success:
                        st.success("Cours mis à jour avec succès!")
                        st.experimental_rerun()
                    else:
                        st.error("Erreur lors de la mise à jour du cours")
        
        # Formulaire de suppression
        st.subheader("Supprimer un cours")
        course_to_delete = st.selectbox("Sélectionner un cours à supprimer", courses_df['CourseID'].tolist() if not courses_df.empty else [], key="delete_course")
        
        if course_to_delete:
            if st.button("Supprimer"):
                # Supprimer le cours
                success = data_loader.delete_course(course_to_delete)
                
                if success:
                    st.success("Cours supprimé avec succès!")
                    st.experimental_rerun()
                else:
                    st.error("Erreur lors de la suppression du cours")
    
    # Onglet Étudiants
    with tabs[1]:
        st.header("Gestion des Étudiants")
        
        # Charger les données des étudiants
        students_df = data_loader.get_students()
        
        # Afficher les étudiants
        st.subheader("Liste des étudiants")
        if not students_df.empty:
            st.dataframe(students_df)
        else:
            st.info("Aucun étudiant trouvé.")
        
        # Formulaire d'ajout
        st.subheader("Ajouter un nouvel étudiant")
        with st.form("add_student_form"):
            first_name = st.text_input("Prénom")
            last_name = st.text_input("Nom")
            group = st.selectbox("Groupe", ["Groupe A", "Groupe B", "Groupe C"])
            
            submitted = st.form_submit_button("Ajouter")
            
            if submitted and first_name and last_name:
                # Ajouter le nouvel étudiant
                student_id = data_loader.add_student(first_name, last_name, group)
                
                if student_id:
                    st.success(f"Étudiant '{first_name} {last_name}' ajouté avec succès!")
                    st.experimental_rerun()
                else:
                    st.error(f"Erreur lors de l'ajout de l'étudiant '{first_name} {last_name}'")
        
        # Formulaire de modification
        st.subheader("Modifier un étudiant")
        student_to_modify = st.selectbox("Sélectionner un étudiant à modifier", students_df['StudentID'].tolist() if not students_df.empty else [])
        
        if student_to_modify:
            student_to_edit = students_df[students_df['StudentID'] == student_to_modify].iloc[0]
            
            with st.form("edit_student_form"):
                new_first_name = st.text_input("Prénom", value=student_to_edit['FirstName'])
                new_last_name = st.text_input("Nom", value=student_to_edit['LastName'])
                new_group = st.selectbox("Groupe", ["Groupe A", "Groupe B", "Groupe C"], index=["Groupe A", "Groupe B", "Groupe C"].index(student_to_edit['Group']) if student_to_edit['Group'] in ["Groupe A", "Groupe B", "Groupe C"] else 0)
                
                submitted = st.form_submit_button("Modifier")
                
                if submitted:
                    # Mettre à jour l'étudiant
                    success = data_loader.update_student(student_to_modify, new_first_name, new_last_name, new_group)
                    
                    if success:
                        st.success("Étudiant mis à jour avec succès!")
                        st.experimental_rerun()
                    else:
                        st.error("Erreur lors de la mise à jour de l'étudiant")
        
        # Formulaire de suppression
        st.subheader("Supprimer un étudiant")
        student_to_delete = st.selectbox("Sélectionner un étudiant à supprimer", students_df['StudentID'].tolist() if not students_df.empty else [], key="delete_student")
        
        if student_to_delete:
            if st.button("Supprimer"):
                # Supprimer l'étudiant
                success = data_loader.delete_student(student_to_delete)
                
                if success:
                    st.success("Étudiant supprimé avec succès!")
                    st.experimental_rerun()
                else:
                    st.error("Erreur lors de la suppression de l'étudiant")
    
    # Onglet Présences
    with tabs[2]:
        st.header("Gestion des Présences")
        
        # Charger les données
        attendance_df = data_loader.get_attendance()
        
        # Afficher les présences
        st.subheader("Liste des présences")
        if not attendance_df.empty:
            st.dataframe(attendance_df)
        else:
            st.info("Aucune présence trouvée.")
        
        # Formulaire d'ajout
        st.subheader("Ajouter une présence")
        with st.form("add_attendance_form"):
            # Sélection du cours
            course_options = courses_df['CourseName'].tolist() if not courses_df.empty else []
            if course_options:
                course = st.selectbox("Cours", course_options)
                course_id = courses_df[courses_df['CourseName'] == course]['CourseID'].iloc[0]
            else:
                st.warning("Aucun cours disponible. Veuillez d'abord ajouter des cours.")
                course_id = None
            
            # Sélection de l'étudiant
            student_options = [f"{row['FirstName']} {row['LastName']}" for _, row in students_df.iterrows()] if not students_df.empty else []
            if student_options:
                student = st.selectbox("Étudiant", student_options)
                first_name, last_name = student.split(" ", 1)
                student_id = students_df[(students_df['FirstName'] == first_name) & (students_df['LastName'] == last_name)]['StudentID'].iloc[0]
            else:
                st.warning("Aucun étudiant disponible. Veuillez d'abord ajouter des étudiants.")
                student_id = None
            
            # Date et statut
            date = st.date_input("Date", value=datetime.now())
            status = st.radio("Statut", ["Présent", "Absent"])
            method = st.selectbox("Méthode", ["Manuel", "Reconnaissance faciale", "Autre"])
            
            submitted = st.form_submit_button("Ajouter")
            
            if submitted and course_id and student_id:
                # Créer un nouvel enregistrement
                date_str = date.strftime("%Y-%m-%d")
                status_str = "present" if status == "Présent" else "absent"
                
                # Ajouter l'enregistrement
                attendance_id = data_loader.add_attendance(course_id, student_id, date_str, status_str, method)
                
                if attendance_id:
                    st.success(f"Enregistrement de présence ajouté avec succès!")
                    st.experimental_rerun()
                else:
                    st.error("Un enregistrement existe déjà pour cet étudiant, ce cours et cette date!")
        
        # Formulaire de suppression
        st.subheader("Supprimer une présence")
        attendance_to_delete = st.selectbox("Sélectionner une présence à supprimer", attendance_df['ID'].tolist() if not attendance_df.empty else [])
        
        if attendance_to_delete:
            if st.button("Supprimer"):
                # Supprimer la présence
                success = data_loader.delete_attendance(attendance_to_delete)
                
                if success:
                    st.success("Présence supprimée avec succès!")
                    st.experimental_rerun()
                else:
                    st.error("Erreur lors de la suppression de la présence")

if __name__ == "__main__":
    main()
