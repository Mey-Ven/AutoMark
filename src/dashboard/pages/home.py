import streamlit as st
import pandas as pd
import datetime
from typing import Dict, Any

from src.dashboard.utils.data_loader import DataLoader
from src.dashboard.utils.visualizations import (
    create_attendance_heatmap,
    create_attendance_bar_chart,
    create_attendance_trend_chart
)


def render_home_page(data_loader: DataLoader) -> None:
    """
    Affiche la page d'accueil du dashboard.
    
    Args:
        data_loader: Instance de DataLoader pour charger les données.
    """
    st.title("AutoMark - Tableau de bord de présence")
    
    # Afficher un résumé des statistiques
    st.header("Résumé")
    
    # Recharger les données
    data_loader.reload_data()
    
    # Obtenir les statistiques
    stats = data_loader.get_attendance_stats()
    
    # Créer des colonnes pour afficher les statistiques
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total des présences", stats['total_attendances'])
    
    with col2:
        st.metric("Étudiants uniques", stats['unique_students'])
    
    with col3:
        st.metric("Cours uniques", stats['unique_courses'])
    
    # Afficher un graphique de tendance des présences
    st.header("Tendance des présences")
    
    attendance_df = data_loader.get_attendance()
    
    if not attendance_df.empty:
        trend_chart = create_attendance_trend_chart(attendance_df)
        st.plotly_chart(trend_chart, use_container_width=True)
    else:
        st.info("Aucune donnée de présence disponible.")
    
    # Afficher un graphique à barres des présences par cours
    st.header("Présences par cours")
    
    if not attendance_df.empty:
        bar_chart = create_attendance_bar_chart(attendance_df, group_by='CourseID')
        st.plotly_chart(bar_chart, use_container_width=True)
    else:
        st.info("Aucune donnée de présence disponible.")
    
    # Afficher une heatmap des présences
    st.header("Heatmap des présences")
    
    if not attendance_df.empty:
        heatmap = create_attendance_heatmap(attendance_df)
        st.plotly_chart(heatmap, use_container_width=True)
    else:
        st.info("Aucune donnée de présence disponible.")
    
    # Afficher les dernières présences enregistrées
    st.header("Dernières présences enregistrées")
    
    if not attendance_df.empty:
        # Trier par date et heure (les plus récentes en premier)
        latest_attendance = attendance_df.sort_values(by=['Date', 'Time'], ascending=False).head(10)
        st.dataframe(latest_attendance)
