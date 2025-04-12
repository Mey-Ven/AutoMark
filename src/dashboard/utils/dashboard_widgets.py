"""
Module contenant des widgets personnalisés pour le tableau de bord AutoMark.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional, Union, Tuple

def stat_card(title: str, value: Union[str, int, float], 
              delta: Optional[Union[str, int, float]] = None,
              delta_color: str = "normal", icon: str = "📊",
              help_text: Optional[str] = None) -> None:
    """
    Affiche une carte de statistique avec un titre, une valeur et une variation optionnelle.
    
    Args:
        title: Titre de la statistique
        value: Valeur principale à afficher
        delta: Variation par rapport à une période précédente (optionnel)
        delta_color: Couleur de la variation ("normal", "inverse", "off")
        icon: Icône à afficher
        help_text: Texte d'aide à afficher au survol
    """
    # Créer un conteneur avec une bordure et un fond
    with st.container():
        # Appliquer un style CSS personnalisé
        st.markdown(f"""
        <div style="
            background-color: var(--card-background);
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 10px;
        ">
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <div style="font-size: 24px; margin-right: 10px;">{icon}</div>
                <div style="font-size: 16px; color: var(--text-color); opacity: 0.8;">{title}</div>
            </div>
            <div style="font-size: 28px; font-weight: bold; color: var(--text-color);">{value}</div>
            {f'<div style="font-size: 14px; color: {"#4CAF50" if delta_color == "normal" and str(delta).startswith("+") else "#F44336" if delta_color == "normal" and str(delta).startswith("-") else "#4CAF50" if delta_color == "inverse" and str(delta).startswith("-") else "#F44336" if delta_color == "inverse" and str(delta).startswith("+") else "var(--text-color)"};">{delta}</div>' if delta else ''}
        </div>
        """, unsafe_allow_html=True)
        
        if help_text:
            st.caption(help_text)

def stats_dashboard(attendance_data: pd.DataFrame, 
                    students_data: pd.DataFrame, 
                    courses_data: pd.DataFrame,
                    period: str = "all") -> None:
    """
    Affiche un tableau de bord de statistiques de présence.
    
    Args:
        attendance_data: DataFrame contenant les données de présence
        students_data: DataFrame contenant les données des étudiants
        courses_data: DataFrame contenant les données des cours
        period: Période à considérer ("all", "month", "week", "day")
    """
    # Filtrer les données selon la période
    if period != "all":
        today = pd.Timestamp.now()
        if period == "month":
            start_date = today - pd.Timedelta(days=30)
        elif period == "week":
            start_date = today - pd.Timedelta(days=7)
        elif period == "day":
            start_date = today - pd.Timedelta(days=1)
        
        attendance_data = attendance_data[attendance_data['date'] >= start_date.strftime('%Y-%m-%d')]
    
    # Calculer les statistiques clés
    total_students = len(students_data)
    total_courses = len(courses_data)
    
    # Calculer le taux de présence global
    if len(attendance_data) > 0:
        present_count = len(attendance_data[attendance_data['status'] == 'present'])
        total_count = len(attendance_data)
        attendance_rate = round(present_count / total_count * 100, 1)
    else:
        attendance_rate = 0
    
    # Créer une mise en page en colonnes pour les cartes de statistiques
    col1, col2, col3 = st.columns(3)
    
    with col1:
        stat_card(
            title="Taux de présence",
            value=f"{attendance_rate}%",
            delta="+2.5%" if period == "week" else None,  # Exemple de variation
            icon="📈",
            help_text="Pourcentage d'étudiants présents sur le total des présences attendues"
        )
    
    with col2:
        stat_card(
            title="Étudiants",
            value=str(total_students),
            icon="👨‍🎓",
            help_text="Nombre total d'étudiants enregistrés"
        )
    
    with col3:
        stat_card(
            title="Cours",
            value=str(total_courses),
            icon="📚",
            help_text="Nombre total de cours enregistrés"
        )

def attendance_trend_chart(attendance_data: pd.DataFrame, 
                          period: str = "month") -> None:
    """
    Affiche un graphique de tendance des présences sur une période donnée.
    
    Args:
        attendance_data: DataFrame contenant les données de présence
        period: Période à afficher ("month", "week", "year")
    """
    if len(attendance_data) == 0:
        st.warning("Aucune donnée de présence disponible pour afficher la tendance.")
        return
    
    # Convertir la colonne de date en datetime si ce n'est pas déjà fait
    attendance_data['date'] = pd.to_datetime(attendance_data['date'])
    
    # Déterminer le format de regroupement en fonction de la période
    if period == "week":
        groupby_format = attendance_data['date'].dt.date
        title = "Tendance des présences (7 derniers jours)"
    elif period == "month":
        groupby_format = attendance_data['date'].dt.date
        title = "Tendance des présences (30 derniers jours)"
    elif period == "year":
        groupby_format = attendance_data['date'].dt.to_period('M').dt.to_timestamp()
        title = "Tendance des présences (12 derniers mois)"
    
    # Grouper les données par date et statut
    grouped = attendance_data.groupby([groupby_format, 'status']).size().unstack(fill_value=0)
    
    # S'assurer que les colonnes 'present' et 'absent' existent
    if 'present' not in grouped.columns:
        grouped['present'] = 0
    if 'absent' not in grouped.columns:
        grouped['absent'] = 0
    
    # Calculer le taux de présence
    grouped['attendance_rate'] = grouped['present'] / (grouped['present'] + grouped['absent']) * 100
    
    # Créer le graphique avec Plotly
    fig = go.Figure()
    
    # Ajouter la ligne de tendance du taux de présence
    fig.add_trace(go.Scatter(
        x=grouped.index,
        y=grouped['attendance_rate'],
        mode='lines+markers',
        name='Taux de présence (%)',
        line=dict(color='#4CAF50', width=3),
        marker=dict(size=8, color='#4CAF50')
    ))
    
    # Personnaliser le graphique
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Taux de présence (%)",
        hovermode="x unified",
        template="plotly_white",
        height=400,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    
    # Afficher le graphique
    st.plotly_chart(fig, use_container_width=True)

def attendance_by_course_chart(attendance_data: pd.DataFrame, 
                              courses_data: pd.DataFrame) -> None:
    """
    Affiche un graphique des taux de présence par cours.
    
    Args:
        attendance_data: DataFrame contenant les données de présence
        courses_data: DataFrame contenant les données des cours
    """
    if len(attendance_data) == 0 or len(courses_data) == 0:
        st.warning("Données insuffisantes pour afficher les statistiques par cours.")
        return
    
    # Fusionner les données de présence avec les données de cours
    merged_data = pd.merge(
        attendance_data,
        courses_data,
        left_on='course_id',
        right_on='id',
        how='left'
    )
    
    # Grouper par cours et calculer le taux de présence
    course_stats = merged_data.groupby(['course_name', 'status']).size().unstack(fill_value=0)
    
    # S'assurer que les colonnes 'present' et 'absent' existent
    if 'present' not in course_stats.columns:
        course_stats['present'] = 0
    if 'absent' not in course_stats.columns:
        course_stats['absent'] = 0
    
    # Calculer le taux de présence
    course_stats['total'] = course_stats['present'] + course_stats['absent']
    course_stats['attendance_rate'] = course_stats['present'] / course_stats['total'] * 100
    
    # Trier par taux de présence
    course_stats = course_stats.sort_values('attendance_rate', ascending=False)
    
    # Créer le graphique avec Plotly
    fig = px.bar(
        course_stats.reset_index(),
        x='course_name',
        y='attendance_rate',
        color='attendance_rate',
        color_continuous_scale=['#F44336', '#FFC107', '#4CAF50'],
        labels={'course_name': 'Cours', 'attendance_rate': 'Taux de présence (%)'},
        title="Taux de présence par cours"
    )
    
    # Personnaliser le graphique
    fig.update_layout(
        xaxis_title="Cours",
        yaxis_title="Taux de présence (%)",
        coloraxis_showscale=False,
        height=400,
        margin=dict(l=10, r=10, t=50, b=100)
    )
    
    # Rotation des étiquettes de l'axe x pour une meilleure lisibilité
    fig.update_xaxes(tickangle=45)
    
    # Afficher le graphique
    st.plotly_chart(fig, use_container_width=True)

def student_attendance_heatmap(attendance_data: pd.DataFrame, 
                              students_data: pd.DataFrame,
                              courses_data: pd.DataFrame,
                              max_students: int = 15) -> None:
    """
    Affiche une heatmap des présences par étudiant et par cours.
    
    Args:
        attendance_data: DataFrame contenant les données de présence
        students_data: DataFrame contenant les données des étudiants
        courses_data: DataFrame contenant les données des cours
        max_students: Nombre maximum d'étudiants à afficher
    """
    if len(attendance_data) == 0:
        st.warning("Aucune donnée de présence disponible pour afficher la heatmap.")
        return
    
    # Fusionner les données
    merged_data = pd.merge(
        attendance_data,
        students_data,
        left_on='student_id',
        right_on='id',
        how='left'
    )
    
    merged_data = pd.merge(
        merged_data,
        courses_data,
        left_on='course_id',
        right_on='id',
        how='left',
        suffixes=('_student', '_course')
    )
    
    # Créer un nom complet pour les étudiants
    merged_data['student_name'] = merged_data['first_name'] + ' ' + merged_data['last_name']
    
    # Grouper par étudiant, cours et calculer le taux de présence
    heatmap_data = merged_data.groupby(['student_name', 'course_name', 'status']).size().unstack(fill_value=0)
    
    # S'assurer que les colonnes 'present' et 'absent' existent
    if 'present' not in heatmap_data.columns:
        heatmap_data['present'] = 0
    if 'absent' not in heatmap_data.columns:
        heatmap_data['absent'] = 0
    
    # Calculer le taux de présence
    heatmap_data['total'] = heatmap_data['present'] + heatmap_data['absent']
    heatmap_data['attendance_rate'] = heatmap_data['present'] / heatmap_data['total'] * 100
    
    # Réorganiser les données pour la heatmap
    heatmap_df = heatmap_data.reset_index()[['student_name', 'course_name', 'attendance_rate']]
    
    # Limiter le nombre d'étudiants si nécessaire
    unique_students = heatmap_df['student_name'].unique()
    if len(unique_students) > max_students:
        # Sélectionner les étudiants avec les taux de présence les plus bas
        student_avg_rates = heatmap_df.groupby('student_name')['attendance_rate'].mean()
        students_to_show = student_avg_rates.sort_values().index[:max_students]
        heatmap_df = heatmap_df[heatmap_df['student_name'].isin(students_to_show)]
    
    # Pivoter les données pour la heatmap
    pivot_df = heatmap_df.pivot(index='student_name', columns='course_name', values='attendance_rate')
    
    # Créer la heatmap avec Plotly
    fig = px.imshow(
        pivot_df,
        labels=dict(x="Cours", y="Étudiant", color="Taux de présence (%)"),
        x=pivot_df.columns,
        y=pivot_df.index,
        color_continuous_scale=['#F44336', '#FFC107', '#4CAF50'],
        title="Taux de présence par étudiant et par cours"
    )
    
    # Personnaliser la heatmap
    fig.update_layout(
        height=500,
        margin=dict(l=10, r=10, t=50, b=50),
        xaxis_tickangle=45
    )
    
    # Afficher les valeurs dans les cellules
    fig.update_traces(text=pivot_df.round(1), texttemplate="%{text}%")
    
    # Afficher la heatmap
    st.plotly_chart(fig, use_container_width=True)
