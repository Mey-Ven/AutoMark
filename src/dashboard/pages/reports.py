import streamlit as st
import pandas as pd
import datetime
import os
from typing import Dict, Any

from src.dashboard.utils.data_loader import DataLoader
from src.utils.file_operations import export_attendance_report


def render_reports_page(data_loader: DataLoader) -> None:
    """
    Affiche la page des rapports.
    
    Args:
        data_loader: Instance de DataLoader pour charger les données.
    """
    st.title("Rapports de présence")
    
    # Recharger les données
    data_loader.reload_data()
    
    # Obtenir les données
    attendance_df = data_loader.get_attendance()
    courses_df = data_loader.get_courses()
    students_df = data_loader.get_students()
    
    if attendance_df.empty:
        st.info("Aucune donnée de présence disponible.")
        return
    
    # Créer des filtres
    st.sidebar.header("Filtres")
    
    # Filtre par date
    all_dates = sorted(attendance_df['Date'].unique())
    if all_dates:
        start_date = st.sidebar.selectbox(
            "Date de début",
            all_dates
        )
        
        # Filtrer les dates après la date de début
        end_dates = [d for d in all_dates if d >= start_date]
        end_date = st.sidebar.selectbox(
            "Date de fin",
            end_dates
        )
    else:
        start_date = None
        end_date = None
    
    # Filtre par cours
    all_courses = sorted(attendance_df['CourseID'].unique())
    selected_courses = st.sidebar.multiselect(
        "Cours",
        all_courses,
        default=all_courses
    )
    
    # Appliquer les filtres
    filtered_df = attendance_df.copy()
    
    if start_date and end_date:
        filtered_df = filtered_df[(filtered_df['Date'] >= start_date) & (filtered_df['Date'] <= end_date)]
    
    if selected_courses:
        filtered_df = filtered_df[filtered_df['CourseID'].isin(selected_courses)]
    
    # Afficher les données filtrées
    st.header("Données filtrées")
    
    if not filtered_df.empty:
        st.dataframe(filtered_df)
        
        # Afficher des statistiques de base
        st.subheader("Statistiques")
        
        # Nombre total de présences
        total_attendances = len(filtered_df)
        
        # Nombre d'étudiants uniques
        unique_students = filtered_df['StudentID'].nunique()
        
        # Nombre de cours uniques
        unique_courses = filtered_df['CourseID'].nunique()
        
        # Créer des colonnes pour afficher les statistiques
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total des présences", total_attendances)
        
        with col2:
            st.metric("Étudiants uniques", unique_students)
        
        with col3:
            st.metric("Cours uniques", unique_courses)
        
        # Options d'exportation
        st.header("Exporter le rapport")
        
        # Format d'exportation
        export_format = st.radio(
            "Format d'exportation",
            ["CSV", "Excel"]
        )
        
        # Nom du fichier
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        default_filename = f"rapport_presence_{current_date}"
        
        filename = st.text_input(
            "Nom du fichier (sans extension)",
            value=default_filename
        )
        
        # Bouton d'exportation
        if st.button("Exporter"):
            # Créer le répertoire d'exportation s'il n'existe pas
            export_dir = os.path.join(data_loader.data_dir, "exports")
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)
            
            # Chemin complet du fichier
            file_path = os.path.join(export_dir, filename)
            
            # Exporter le rapport
            exported_file = export_attendance_report(
                filtered_df,
                file_path,
                format=export_format.lower()
            )
            
            st.success(f"Rapport exporté avec succès : {exported_file}")
    else:
        st.info("Aucune donnée disponible pour les filtres sélectionnés.")
