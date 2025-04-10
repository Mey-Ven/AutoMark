import os
import csv
import pandas as pd
from typing import List, Dict, Any, Optional


def load_courses(file_path: str) -> pd.DataFrame:
    """
    Charge les informations des cours à partir d'un fichier CSV.
    
    Args:
        file_path: Chemin vers le fichier CSV contenant les informations des cours.
        
    Returns:
        DataFrame pandas contenant les informations des cours.
    """
    if not os.path.exists(file_path):
        # Créer un DataFrame vide avec les colonnes appropriées
        return pd.DataFrame(columns=['CourseID', 'CourseName', 'Instructor', 'Group', 'Schedule'])
    
    return pd.read_csv(file_path)


def save_courses(courses_df: pd.DataFrame, file_path: str) -> None:
    """
    Sauvegarde les informations des cours dans un fichier CSV.
    
    Args:
        courses_df: DataFrame pandas contenant les informations des cours.
        file_path: Chemin vers le fichier CSV où sauvegarder les informations.
    """
    courses_df.to_csv(file_path, index=False)


def load_students(file_path: str) -> pd.DataFrame:
    """
    Charge les informations des étudiants à partir d'un fichier CSV.
    
    Args:
        file_path: Chemin vers le fichier CSV contenant les informations des étudiants.
        
    Returns:
        DataFrame pandas contenant les informations des étudiants.
    """
    if not os.path.exists(file_path):
        # Créer un DataFrame vide avec les colonnes appropriées
        return pd.DataFrame(columns=['StudentID', 'FirstName', 'LastName', 'Group'])
    
    return pd.read_csv(file_path)


def save_students(students_df: pd.DataFrame, file_path: str) -> None:
    """
    Sauvegarde les informations des étudiants dans un fichier CSV.
    
    Args:
        students_df: DataFrame pandas contenant les informations des étudiants.
        file_path: Chemin vers le fichier CSV où sauvegarder les informations.
    """
    students_df.to_csv(file_path, index=False)


def load_attendance_data(attendance_dir: str) -> pd.DataFrame:
    """
    Charge toutes les données de présence à partir des fichiers CSV dans le répertoire spécifié.
    
    Args:
        attendance_dir: Chemin vers le répertoire contenant les fichiers CSV de présence.
        
    Returns:
        DataFrame pandas contenant toutes les données de présence.
    """
    all_data = []
    
    if not os.path.exists(attendance_dir):
        return pd.DataFrame(columns=['CourseID', 'StudentID', 'Date', 'Time'])
    
    for filename in os.listdir(attendance_dir):
        if filename.endswith('.csv'):
            # Extraire l'ID du cours et la date du nom de fichier
            parts = filename.split('_')
            if len(parts) >= 2:
                course_id = parts[0]
                date = parts[1].replace('.csv', '')
                
                file_path = os.path.join(attendance_dir, filename)
                
                try:
                    # Charger les données du fichier
                    df = pd.read_csv(file_path)
                    
                    # Ajouter l'ID du cours si la colonne n'existe pas
                    if 'CourseID' not in df.columns:
                        df['CourseID'] = course_id
                    
                    all_data.append(df)
                except Exception as e:
                    print(f"Erreur lors du chargement du fichier {filename}: {e}")
    
    if not all_data:
        return pd.DataFrame(columns=['CourseID', 'StudentID', 'Date', 'Time'])
    
    # Concaténer tous les DataFrames
    return pd.concat(all_data, ignore_index=True)


def export_attendance_report(attendance_df: pd.DataFrame, output_path: str, format: str = 'csv') -> str:
    """
    Exporte un rapport de présence dans le format spécifié.
    
    Args:
        attendance_df: DataFrame pandas contenant les données de présence.
        output_path: Chemin où sauvegarder le rapport.
        format: Format du rapport ('csv' ou 'excel').
        
    Returns:
        Chemin vers le fichier exporté.
    """
    if format.lower() == 'csv':
        file_path = f"{output_path}.csv"
        attendance_df.to_csv(file_path, index=False)
    elif format.lower() == 'excel':
        file_path = f"{output_path}.xlsx"
        attendance_df.to_excel(file_path, index=False)
    else:
        raise ValueError(f"Format non supporté: {format}")
    
    return file_path
