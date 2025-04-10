import os
import pandas as pd
import datetime
from typing import List, Dict, Tuple, Optional, Any

from src.utils.file_operations import load_courses, load_students, load_attendance_data


class DataLoader:
    """
    Classe pour charger et traiter les données pour le dashboard.
    """

    def __init__(self, data_dir: str):
        """
        Initialise le chargeur de données.

        Args:
            data_dir: Chemin vers le répertoire contenant les données.
        """
        self.data_dir = data_dir
        self.courses_file = os.path.join(data_dir, 'courses.csv')
        self.students_file = os.path.join(data_dir, 'students.csv')
        self.attendance_dir = os.path.join(data_dir, 'attendance')

        # Charger les données
        self.reload_data()

    def reload_data(self) -> None:
        """
        Recharge toutes les données.
        """
        self.courses_df = load_courses(self.courses_file)
        self.students_df = load_students(self.students_file)
        self.attendance_df = load_attendance_data(self.attendance_dir)

    def get_courses(self) -> pd.DataFrame:
        """
        Récupère les informations des cours.

        Returns:
            DataFrame pandas contenant les informations des cours.
        """
        return self.courses_df

    def get_students(self) -> pd.DataFrame:
        """
        Récupère les informations des étudiants.

        Returns:
            DataFrame pandas contenant les informations des étudiants.
        """
        return self.students_df

    def get_attendance(self) -> pd.DataFrame:
        """
        Récupère les données de présence.

        Returns:
            DataFrame pandas contenant les données de présence.
        """
        return self.attendance_df

    def get_attendance_by_course(self, course_id: str) -> pd.DataFrame:
        """
        Récupère les données de présence pour un cours spécifique.

        Args:
            course_id: Identifiant du cours.

        Returns:
            DataFrame pandas contenant les données de présence pour le cours spécifié.
        """
        return self.attendance_df[self.attendance_df['CourseID'] == course_id]

    def get_attendance_by_student(self, student_id: str) -> pd.DataFrame:
        """
        Récupère les données de présence pour un étudiant spécifique.

        Args:
            student_id: Identifiant de l'étudiant.

        Returns:
            DataFrame pandas contenant les données de présence pour l'étudiant spécifié.
        """
        return self.attendance_df[self.attendance_df['StudentID'] == student_id]

    def get_attendance_by_date(self, date: str) -> pd.DataFrame:
        """
        Récupère les données de présence pour une date spécifique.

        Args:
            date: Date au format YYYY-MM-DD.

        Returns:
            DataFrame pandas contenant les données de présence pour la date spécifiée.
        """
        return self.attendance_df[self.attendance_df['Date'] == date]

    def get_attendance_stats(self) -> Dict[str, Any]:
        """
        Calcule les statistiques de présence.

        Returns:
            Dictionnaire contenant diverses statistiques de présence.
        """
        stats = {}

        # Nombre total de présences
        stats['total_attendances'] = len(self.attendance_df)

        # Nombre d'étudiants uniques
        stats['unique_students'] = self.attendance_df['StudentID'].nunique()

        # Nombre de cours uniques
        stats['unique_courses'] = self.attendance_df['CourseID'].nunique()

        # Présences par jour
        attendance_by_date = self.attendance_df.groupby('Date').size()
        stats['attendance_by_date'] = attendance_by_date.to_dict()

        # Présences par cours
        attendance_by_course = self.attendance_df.groupby('CourseID').size()
        stats['attendance_by_course'] = attendance_by_course.to_dict()

        return stats

    def get_student_attendance_rate(self, student_id: str) -> float:
        """
        Calcule le taux de présence d'un étudiant.

        Args:
            student_id: Identifiant de l'étudiant.

        Returns:
            Taux de présence (entre 0 et 1).
        """
        # Obtenir toutes les présences de l'étudiant
        student_attendance = self.get_attendance_by_student(student_id)

        # Obtenir tous les cours auxquels l'étudiant est inscrit
        student_info = self.students_df[self.students_df['StudentID'] == student_id]
        if len(student_info) == 0:
            return 0.0

        student_group = student_info.iloc[0]['Group']

        # Obtenir tous les cours pour ce groupe
        group_courses = self.courses_df[self.courses_df['Group'] == student_group]

        # Calculer le nombre total de séances pour tous les cours du groupe
        # Note: Ceci est une simplification, dans un système réel, il faudrait
        # compter le nombre exact de séances pour chaque cours
        total_sessions = len(group_courses)

        if total_sessions == 0:
            return 0.0

        # Calculer le nombre de séances auxquelles l'étudiant a assisté
        attended_sessions = student_attendance['CourseID'].nunique()

        return attended_sessions / total_sessions

    def get_course_attendance_rate(self, course_id: str) -> float:
        """
        Calcule le taux de présence pour un cours.

        Args:
            course_id: Identifiant du cours.

        Returns:
            Taux de présence (entre 0 et 1).
        """
        # Obtenir toutes les présences pour ce cours
        course_attendance = self.get_attendance_by_course(course_id)

        # Obtenir les informations du cours
        course_info = self.courses_df[self.courses_df['CourseID'] == course_id]
        if len(course_info) == 0:
            return 0.0

        course_group = course_info.iloc[0]['Group']

        # Obtenir tous les étudiants de ce groupe
        group_students = self.students_df[self.students_df['Group'] == course_group]

        # Nombre total d'étudiants dans le groupe
        total_students = len(group_students)

        if total_students == 0:
            return 0.0

        # Nombre d'étudiants présents
        present_students = course_attendance['StudentID'].nunique()

        return present_students / total_students
