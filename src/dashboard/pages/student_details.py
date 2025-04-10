import streamlit as st
import pandas as pd
import datetime
from typing import Dict, Any

from src.dashboard.utils.data_loader import DataLoader
from src.dashboard.utils.visualizations import create_student_attendance_chart


def render_student_details_page(data_loader: DataLoader) -> None:
    """
    Affiche la page des détails des étudiants.
    
    Args:
        data_loader: Instance de DataLoader pour charger les données.
    """
    st.title("Détails des étudiants")
    
    # Recharger les données
    data_loader.reload_data()
    
    # Obtenir les données
    attendance_df = data_loader.get_attendance()
    students_df = data_loader.get_students()
    courses_df = data_loader.get_courses()
    
    if students_df.empty:
        st.info("Aucun étudiant enregistré.")
        return
    
    # Créer un sélecteur d'étudiant
    all_students = []
    
    if 'StudentID' in students_df.columns and 'FirstName' in students_df.columns and 'LastName' in students_df.columns:
        # Créer une liste d'étudiants avec leur nom complet
        for _, row in students_df.iterrows():
            student_id = row['StudentID']
            full_name = f"{row['FirstName']} {row['LastName']} ({student_id})"
            all_students.append((student_id, full_name))
    else:
        # Utiliser uniquement l'ID de l'étudiant
        all_students = [(student_id, student_id) for student_id in students_df['StudentID'].unique()]
    
    # Trier les étudiants par nom
    all_students.sort(key=lambda x: x[1])
    
    # Créer le sélecteur
    selected_student_tuple = st.selectbox(
        "Sélectionner un étudiant",
        all_students,
        format_func=lambda x: x[1]
    )
    
    if selected_student_tuple:
        selected_student = selected_student_tuple[0]
        
        # Afficher les informations de l'étudiant
        st.header("Informations de l'étudiant")
        
        student_info = students_df[students_df['StudentID'] == selected_student]
        
        if not student_info.empty:
            # Créer des colonnes pour afficher les informations
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if 'FirstName' in student_info.columns and 'LastName' in student_info.columns:
                    st.metric("Nom", f"{student_info.iloc[0]['FirstName']} {student_info.iloc[0]['LastName']}")
                else:
                    st.metric("ID", selected_student)
            
            with col2:
                if 'Group' in student_info.columns:
                    st.metric("Groupe", student_info.iloc[0]['Group'])
            
            with col3:
                # Calculer le taux de présence
                attendance_rate = data_loader.get_student_attendance_rate(selected_student)
                st.metric("Taux de présence", f"{attendance_rate:.1%}")
        
        # Obtenir les présences de l'étudiant
        student_attendance = data_loader.get_attendance_by_student(selected_student)
        
        # Afficher les statistiques de présence
        st.header("Statistiques de présence")
        
        if not student_attendance.empty:
            # Nombre total de présences
            total_attendances = len(student_attendance)
            
            # Nombre de cours différents
            unique_courses = student_attendance['CourseID'].nunique()
            
            # Créer des colonnes pour afficher les statistiques
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total des présences", total_attendances)
            
            with col2:
                st.metric("Cours suivis", unique_courses)
            
            # Afficher un graphique des présences par cours
            st.subheader("Présences par cours")
            
            chart = create_student_attendance_chart(student_attendance, courses_df)
            st.plotly_chart(chart, use_container_width=True)
            
            # Afficher l'historique des présences
            st.subheader("Historique des présences")
            
            # Trier par date et heure (les plus récentes en premier)
            history = student_attendance.sort_values(by=['Date', 'Time'], ascending=False)
            st.dataframe(history)
        else:
            st.info("Aucune présence enregistrée pour cet étudiant.")
