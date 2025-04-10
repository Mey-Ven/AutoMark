import streamlit as st
import pandas as pd
import datetime
from typing import Dict, Any

from src.dashboard.utils.data_loader import DataLoader
from src.dashboard.utils.visualizations import (
    create_attendance_bar_chart,
    create_attendance_pie_chart,
    create_attendance_heatmap
)


def render_attendance_stats_page(data_loader: DataLoader) -> None:
    """
    Affiche la page des statistiques de présence.
    
    Args:
        data_loader: Instance de DataLoader pour charger les données.
    """
    st.title("Statistiques de présence")
    
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
        selected_date = st.sidebar.selectbox(
            "Sélectionner une date",
            ["Toutes les dates"] + all_dates
        )
    else:
        selected_date = "Toutes les dates"
    
    # Filtre par cours
    all_courses = sorted(attendance_df['CourseID'].unique())
    if all_courses:
        selected_course = st.sidebar.selectbox(
            "Sélectionner un cours",
            ["Tous les cours"] + all_courses
        )
    else:
        selected_course = "Tous les cours"
    
    # Appliquer les filtres
    filtered_df = attendance_df.copy()
    
    if selected_date != "Toutes les dates":
        filtered_df = filtered_df[filtered_df['Date'] == selected_date]
    
    if selected_course != "Tous les cours":
        filtered_df = filtered_df[filtered_df['CourseID'] == selected_course]
    
    # Afficher les statistiques filtrées
    st.header("Statistiques filtrées")
    
    # Métriques de base
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total des présences", len(filtered_df))
    
    with col2:
        st.metric("Étudiants uniques", filtered_df['StudentID'].nunique())
    
    with col3:
        if selected_course != "Tous les cours":
            # Calculer le taux de présence pour le cours sélectionné
            attendance_rate = data_loader.get_course_attendance_rate(selected_course)
            st.metric("Taux de présence", f"{attendance_rate:.1%}")
        else:
            st.metric("Cours uniques", filtered_df['CourseID'].nunique())
    
    # Afficher les graphiques
    st.header("Visualisations")
    
    # Onglets pour différentes visualisations
    tab1, tab2, tab3 = st.tabs(["Par cours", "Par étudiant", "Heatmap"])
    
    with tab1:
        if not filtered_df.empty:
            bar_chart = create_attendance_bar_chart(filtered_df, group_by='CourseID')
            st.plotly_chart(bar_chart, use_container_width=True)
        else:
            st.info("Aucune donnée disponible pour les filtres sélectionnés.")
    
    with tab2:
        if not filtered_df.empty:
            pie_chart = create_attendance_pie_chart(filtered_df, column='StudentID')
            st.plotly_chart(pie_chart, use_container_width=True)
        else:
            st.info("Aucune donnée disponible pour les filtres sélectionnés.")
    
    with tab3:
        if not filtered_df.empty and selected_date == "Toutes les dates":
            heatmap = create_attendance_heatmap(filtered_df)
            st.plotly_chart(heatmap, use_container_width=True)
        else:
            st.info("La heatmap n'est disponible que lorsque 'Toutes les dates' est sélectionné.")
    
    # Afficher les données brutes
    st.header("Données brutes")
    
    if not filtered_df.empty:
        st.dataframe(filtered_df)
