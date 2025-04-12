"""
Module de chargement des données depuis la base de données SQLite.
Ce module remplace le chargeur de données basé sur les fichiers CSV.
"""

import os
import pandas as pd
from typing import List, Dict, Tuple, Optional, Any
from src.database.db_manager_v2 import DatabaseManager

class DBDataLoader:
    """
    Classe pour charger et traiter les données depuis la base de données SQLite.
    Cette classe est compatible avec l'interface du chargeur de données original.
    """

    def __init__(self, data_dir: str):
        """
        Initialise le chargeur de données.
        
        Args:
            data_dir: Chemin vers le répertoire contenant les données.
        """
        self.data_dir = data_dir
        self.db_path = os.path.join(data_dir, 'automark.db')
        self.db_manager = DatabaseManager(self.db_path)
        
        # Fichiers CSV pour la compatibilité avec le code existant
        self.courses_file = os.path.join(data_dir, 'courses.csv')
        self.students_file = os.path.join(data_dir, 'students.csv')
        self.attendance_dir = os.path.join(data_dir, 'attendance')
        
        # Charger les données
        self.reload_data()

    def reload_data(self) -> None:
        """
        Recharge toutes les données depuis la base de données.
        """
        # Charger les données depuis la base de données
        self.courses_df = self.db_manager.get_all_courses()
        self.students_df = self.db_manager.get_all_students()
        self.attendance_df = self.db_manager.get_all_attendance()
        
        # Renommer les colonnes pour la compatibilité avec le code existant
        if not self.courses_df.empty:
            self.courses_df = self.courses_df.rename(columns={
                'id': 'CourseID',
                'name': 'CourseName',
                'instructor': 'Instructor',
                'group_name': 'Group',
                'schedule': 'Schedule'
            })
        
        if not self.students_df.empty:
            self.students_df = self.students_df.rename(columns={
                'id': 'StudentID',
                'first_name': 'FirstName',
                'last_name': 'LastName',
                'group_name': 'Group'
            })
        
        if not self.attendance_df.empty:
            self.attendance_df = self.attendance_df.rename(columns={
                'id': 'ID',
                'course_id': 'CourseID',
                'student_id': 'StudentID',
                'date': 'Date',
                'time': 'Time',
                'status': 'Status',
                'method': 'Method'
            })

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
        df = self.db_manager.get_attendance_by_course(course_id)
        
        # Renommer les colonnes pour la compatibilité avec le code existant
        if not df.empty:
            df = df.rename(columns={
                'id': 'ID',
                'course_id': 'CourseID',
                'student_id': 'StudentID',
                'date': 'Date',
                'time': 'Time',
                'status': 'Status',
                'method': 'Method'
            })
        
        return df

    def get_attendance_by_student(self, student_id: str) -> pd.DataFrame:
        """
        Récupère les données de présence pour un étudiant spécifique.
        
        Args:
            student_id: Identifiant de l'étudiant.
        
        Returns:
            DataFrame pandas contenant les données de présence pour l'étudiant spécifié.
        """
        df = self.db_manager.get_attendance_by_student(student_id)
        
        # Renommer les colonnes pour la compatibilité avec le code existant
        if not df.empty:
            df = df.rename(columns={
                'id': 'ID',
                'course_id': 'CourseID',
                'student_id': 'StudentID',
                'date': 'Date',
                'time': 'Time',
                'status': 'Status',
                'method': 'Method'
            })
        
        return df

    def get_attendance_by_date(self, date: str) -> pd.DataFrame:
        """
        Récupère les données de présence pour une date spécifique.
        
        Args:
            date: Date au format YYYY-MM-DD.
        
        Returns:
            DataFrame pandas contenant les données de présence pour la date spécifiée.
        """
        df = self.db_manager.get_attendance_by_date(date)
        
        # Renommer les colonnes pour la compatibilité avec le code existant
        if not df.empty:
            df = df.rename(columns={
                'id': 'ID',
                'course_id': 'CourseID',
                'student_id': 'StudentID',
                'date': 'Date',
                'time': 'Time',
                'status': 'Status',
                'method': 'Method'
            })
        
        return df

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
        stats['unique_students'] = self.attendance_df['StudentID'].nunique() if not self.attendance_df.empty else 0
        
        # Nombre de cours uniques
        stats['unique_courses'] = self.attendance_df['CourseID'].nunique() if not self.attendance_df.empty else 0
        
        # Présences par jour
        if not self.attendance_df.empty:
            attendance_by_date = self.attendance_df.groupby('Date').size()
            stats['attendance_by_date'] = attendance_by_date.to_dict()
        else:
            stats['attendance_by_date'] = {}
        
        # Présences par cours
        if not self.attendance_df.empty:
            attendance_by_course = self.attendance_df.groupby('CourseID').size()
            stats['attendance_by_course'] = attendance_by_course.to_dict()
        else:
            stats['attendance_by_course'] = {}
        
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
        attended_sessions = student_attendance['CourseID'].nunique() if not student_attendance.empty else 0
        
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
        present_students = course_attendance['StudentID'].nunique() if not course_attendance.empty else 0
        
        return present_students / total_students

    # Méthodes pour la modification des données
    def add_course(self, course_name: str, instructor: str, group: str, schedule: str) -> str:
        """
        Ajoute un nouveau cours à la base de données.
        
        Args:
            course_name: Nom du cours
            instructor: Nom de l'enseignant
            group: Nom du groupe
            schedule: Horaire du cours
            
        Returns:
            ID du cours ajouté ou None si un cours avec le même nom existe déjà
        """
        course_id = self.db_manager.add_course(course_name, instructor, group, schedule)
        if course_id:
            self.reload_data()
        return course_id

    def update_course(self, course_id: str, course_name: str, instructor: str, group: str, schedule: str) -> bool:
        """
        Met à jour un cours existant.
        
        Args:
            course_id: ID du cours à mettre à jour
            course_name: Nouveau nom du cours
            instructor: Nouveau nom de l'enseignant
            group: Nouveau nom du groupe
            schedule: Nouvel horaire du cours
            
        Returns:
            True si la mise à jour a réussi, False sinon
        """
        success = self.db_manager.update_course(course_id, course_name, instructor, group, schedule)
        if success:
            self.reload_data()
        return success

    def delete_course(self, course_id: str) -> bool:
        """
        Supprime un cours de la base de données.
        
        Args:
            course_id: ID du cours à supprimer
            
        Returns:
            True si la suppression a réussi, False sinon
        """
        success = self.db_manager.delete_course(course_id)
        if success:
            self.reload_data()
        return success

    def add_student(self, first_name: str, last_name: str, group: str) -> str:
        """
        Ajoute un nouvel étudiant à la base de données.
        
        Args:
            first_name: Prénom de l'étudiant
            last_name: Nom de l'étudiant
            group: Nom du groupe
            
        Returns:
            ID de l'étudiant ajouté
        """
        student_id = self.db_manager.add_student(first_name, last_name, group)
        if student_id:
            self.reload_data()
        return student_id

    def update_student(self, student_id: str, first_name: str, last_name: str, group: str) -> bool:
        """
        Met à jour un étudiant existant.
        
        Args:
            student_id: ID de l'étudiant à mettre à jour
            first_name: Nouveau prénom de l'étudiant
            last_name: Nouveau nom de l'étudiant
            group: Nouveau nom du groupe
            
        Returns:
            True si la mise à jour a réussi, False sinon
        """
        success = self.db_manager.update_student(student_id, first_name, last_name, group)
        if success:
            self.reload_data()
        return success

    def delete_student(self, student_id: str) -> bool:
        """
        Supprime un étudiant de la base de données.
        
        Args:
            student_id: ID de l'étudiant à supprimer
            
        Returns:
            True si la suppression a réussi, False sinon
        """
        success = self.db_manager.delete_student(student_id)
        if success:
            self.reload_data()
        return success

    def add_attendance(self, course_id: str, student_id: str, date: str, status: str, method: str = "Manuel") -> str:
        """
        Ajoute un nouvel enregistrement de présence à la base de données.
        
        Args:
            course_id: ID du cours
            student_id: ID de l'étudiant
            date: Date de présence au format YYYY-MM-DD
            status: Statut de présence ('present' ou 'absent')
            method: Méthode d'enregistrement
            
        Returns:
            ID de l'enregistrement ajouté ou None si un enregistrement existe déjà
        """
        attendance_id = self.db_manager.add_attendance(course_id, student_id, date, status, method)
        if attendance_id:
            self.reload_data()
        return attendance_id

    def update_attendance(self, attendance_id: str, status: str, method: str = None) -> bool:
        """
        Met à jour un enregistrement de présence existant.
        
        Args:
            attendance_id: ID de l'enregistrement à mettre à jour
            status: Nouveau statut de présence ('present' ou 'absent')
            method: Nouvelle méthode d'enregistrement (optionnel)
            
        Returns:
            True si la mise à jour a réussi, False sinon
        """
        success = self.db_manager.update_attendance(attendance_id, status, method)
        if success:
            self.reload_data()
        return success

    def delete_attendance(self, attendance_id: str) -> bool:
        """
        Supprime un enregistrement de présence de la base de données.
        
        Args:
            attendance_id: ID de l'enregistrement à supprimer
            
        Returns:
            True si la suppression a réussi, False sinon
        """
        success = self.db_manager.delete_attendance(attendance_id)
        if success:
            self.reload_data()
        return success

    def delete_attendance_by_filter(self, course_id: str = None, student_id: str = None, date: str = None) -> int:
        """
        Supprime des enregistrements de présence selon des critères de filtrage.
        
        Args:
            course_id: ID du cours (optionnel)
            student_id: ID de l'étudiant (optionnel)
            date: Date au format YYYY-MM-DD (optionnel)
            
        Returns:
            Nombre d'enregistrements supprimés
        """
        deleted_count = self.db_manager.delete_attendance_by_filter(course_id, student_id, date)
        if deleted_count > 0:
            self.reload_data()
        return deleted_count
