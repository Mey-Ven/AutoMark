import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Tuple
from src.dashboard.utils.plotly_config import apply_french_layout


def create_attendance_heatmap(attendance_df: pd.DataFrame) -> go.Figure:
    """
    Crée une heatmap des présences par jour et par cours.

    Args:
        attendance_df: DataFrame pandas contenant les données de présence.

    Returns:
        Figure Plotly contenant la heatmap.
    """
    # Compter les présences par jour et par cours
    heatmap_data = attendance_df.groupby(['Date', 'CourseID']).size().reset_index(name='Nombre')

    # Pivoter les données pour créer la heatmap
    heatmap_pivot = heatmap_data.pivot(index='Date', columns='CourseID', values='Nombre')

    # Remplir les valeurs manquantes par 0
    heatmap_pivot = heatmap_pivot.fillna(0)

    # Créer la heatmap
    fig = px.imshow(
        heatmap_pivot,
        labels=dict(x="Cours", y="Date", color="Nombre de présences", value="Nombre de présences"),
        x=heatmap_pivot.columns,
        y=heatmap_pivot.index,
        color_continuous_scale='Viridis'
    )

    fig.update_layout(
        title="Heatmap des présences par jour et par cours",
        xaxis_title="Cours",
        yaxis_title="Date",
        coloraxis_colorbar=dict(title="Nombre de présences")
    )

    # Appliquer la configuration française
    return apply_french_layout(fig)


def create_attendance_bar_chart(attendance_df: pd.DataFrame, group_by: str = 'CourseID') -> go.Figure:
    """
    Crée un graphique à barres des présences.

    Args:
        attendance_df: DataFrame pandas contenant les données de présence.
        group_by: Colonne à utiliser pour grouper les données ('CourseID' ou 'Date').

    Returns:
        Figure Plotly contenant le graphique à barres.
    """
    # Compter les présences par groupe
    bar_data = attendance_df.groupby(group_by).size().reset_index(name='Nombre')

    # Créer le graphique à barres
    fig = px.bar(
        bar_data,
        x=group_by,
        y='Nombre',
        labels={group_by: 'Groupe', 'Nombre': 'Nombre de présences'},
        color='Nombre',
        color_continuous_scale='Viridis'
    )

    title = "Nombre de présences par cours" if group_by == 'CourseID' else "Nombre de présences par jour"

    fig.update_layout(
        title=title,
        xaxis_title="Cours" if group_by == 'CourseID' else "Date",
        yaxis_title="Nombre de présences",
        coloraxis_colorbar=dict(title="Nombre de présences")
    )

    # Appliquer la configuration française
    return apply_french_layout(fig)


def create_attendance_pie_chart(attendance_df: pd.DataFrame, column: str = 'CourseID') -> go.Figure:
    """
    Crée un graphique circulaire des présences.

    Args:
        attendance_df: DataFrame pandas contenant les données de présence.
        column: Colonne à utiliser pour le graphique ('CourseID' ou 'StudentID').

    Returns:
        Figure Plotly contenant le graphique circulaire.
    """
    # Compter les présences par valeur de colonne
    pie_data = attendance_df.groupby(column).size().reset_index(name='Nombre')

    # Créer le graphique circulaire
    fig = px.pie(
        pie_data,
        names=column,
        values='Nombre',
        title=f"Répartition des présences par {('cours' if column == 'CourseID' else 'étudiant')}"
    )

    # Appliquer la configuration française
    return apply_french_layout(fig)


def create_student_attendance_chart(student_attendance: pd.DataFrame, courses_df: pd.DataFrame) -> go.Figure:
    """
    Crée un graphique des présences d'un étudiant par cours.

    Args:
        student_attendance: DataFrame pandas contenant les présences de l'étudiant.
        courses_df: DataFrame pandas contenant les informations des cours.

    Returns:
        Figure Plotly contenant le graphique.
    """
    # Compter les présences par cours
    course_counts = student_attendance.groupby('CourseID').size().reset_index(name='Nombre')

    # Fusionner avec les informations des cours pour obtenir les noms des cours
    if 'CourseName' in courses_df.columns:
        course_info = courses_df[['CourseID', 'CourseName']]
        course_counts = pd.merge(course_counts, course_info, on='CourseID', how='left')

        # Utiliser le nom du cours pour l'affichage si disponible
        if 'CourseName' in course_counts.columns:
            course_counts['DisplayName'] = course_counts['CourseName']
        else:
            course_counts['DisplayName'] = course_counts['CourseID']
    else:
        course_counts['DisplayName'] = course_counts['CourseID']

    # Créer le graphique à barres
    fig = px.bar(
        course_counts,
        x='DisplayName',
        y='Nombre',
        labels={'DisplayName': 'Cours', 'Nombre': 'Nombre de présences'},
        color='Nombre',
        color_continuous_scale='Viridis'
    )

    fig.update_layout(
        title="Présences par cours",
        xaxis_title="Cours",
        yaxis_title="Nombre de présences",
        coloraxis_colorbar=dict(title="Nombre de présences")
    )

    # Appliquer la configuration française
    return apply_french_layout(fig)


def create_attendance_trend_chart(attendance_df: pd.DataFrame) -> go.Figure:
    """
    Crée un graphique de tendance des présences au fil du temps.

    Args:
        attendance_df: DataFrame pandas contenant les données de présence.

    Returns:
        Figure Plotly contenant le graphique de tendance.
    """
    # Compter les présences par jour
    trend_data = attendance_df.groupby('Date').size().reset_index(name='Nombre')

    # Trier par date
    trend_data = trend_data.sort_values('Date')

    # Créer le graphique de ligne
    fig = px.line(
        trend_data,
        x='Date',
        y='Nombre',
        labels={'Date': 'Date', 'Nombre': 'Nombre de présences'},
        markers=True
    )

    fig.update_layout(
        title="Tendance des présences au fil du temps",
        xaxis_title="Date",
        yaxis_title="Nombre de présences"
    )

    # Appliquer la configuration française
    return apply_french_layout(fig)