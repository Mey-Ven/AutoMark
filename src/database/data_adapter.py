"""
Adaptateur de données pour AutoMark.
Ce module fournit une interface compatible avec le chargeur de données existant,
mais utilise la base de données SQLite comme source de données.
"""

import os
import pandas as pd
import logging
from src.database.db_manager import DBManager

class SQLiteDataAdapter:
    """
    Adaptateur de données pour AutoMark utilisant SQLite.
    Cette classe fournit une interface compatible avec le chargeur de données existant,
    mais utilise la base de données SQLite comme source de données.
    """
    
    def __init__(self, data_dir):
        """
        Initialise l'adaptateur de données.
        
        Args:
            data_dir (str): Chemin vers le répertoire de données
        """
        self.data_dir = data_dir
        self.db_manager = DBManager(data_dir)
        
        # Configuration du logging
        logging.basicConfig(level=logging.INFO, 
                            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger("sqlite_data_adapter")
        
        # Charger les données
        self.students_df = self._load_students()
        self.courses_df = self._load_courses()
        self.attendance_data = self._load_attendance()
    
    def _load_students(self):
        """
        Charge les données des étudiants depuis la base de données.
        
        Returns:
            pandas.DataFrame: DataFrame contenant les données des étudiants
        """
        students = self.db_manager.get_students()
        if not students:
            self.logger.warning("Aucune donnée d'étudiant trouvée dans la base de données")
            return pd.DataFrame(columns=["StudentID", "FirstName", "LastName", "Email", "Group", "PhotoPath"])
        
        # Convertir la liste de dictionnaires en DataFrame
        df = pd.DataFrame(students)
        
        # Renommer les colonnes pour correspondre au format attendu
        column_mapping = {
            "student_id": "StudentID",
            "first_name": "FirstName",
            "last_name": "LastName",
            "email": "Email",
            "group_name": "Group",
            "photo_path": "PhotoPath"
        }
        
        df = df.rename(columns=column_mapping)
        
        # Sélectionner uniquement les colonnes nécessaires
        columns = ["StudentID", "FirstName", "LastName", "Email", "Group", "PhotoPath"]
        for col in columns:
            if col not in df.columns:
                df[col] = ""
        
        df = df[columns]
        
        return df
    
    def _load_courses(self):
        """
        Charge les données des cours depuis la base de données.
        
        Returns:
            pandas.DataFrame: DataFrame contenant les données des cours
        """
        courses = self.db_manager.get_courses()
        if not courses:
            self.logger.warning("Aucune donnée de cours trouvée dans la base de données")
            return pd.DataFrame(columns=["CourseID", "CourseName", "Instructor", "Group", "Schedule"])
        
        # Convertir la liste de dictionnaires en DataFrame
        df = pd.DataFrame(courses)
        
        # Renommer les colonnes pour correspondre au format attendu
        column_mapping = {
            "course_id": "CourseID",
            "course_name": "CourseName",
            "instructor": "Instructor",
            "group_name": "Group",
            "schedule": "Schedule"
        }
        
        df = df.rename(columns=column_mapping)
        
        # Sélectionner uniquement les colonnes nécessaires
        columns = ["CourseID", "CourseName", "Instructor", "Group", "Schedule"]
        for col in columns:
            if col not in df.columns:
                df[col] = ""
        
        df = df[columns]
        
        return df
    
    def _load_attendance(self):
        """
        Charge les données de présence depuis la base de données.
        
        Returns:
            dict: Dictionnaire contenant les données de présence par cours et par date
        """
        attendance = self.db_manager.get_attendance()
        if not attendance:
            self.logger.warning("Aucune donnée de présence trouvée dans la base de données")
            return {}
        
        # Organiser les données par cours et par date
        attendance_data = {}
        
        for record in attendance:
            course_id = record["course_code"]
            date = record["date"]
            
            # Créer la clé du cours s'il n'existe pas
            if course_id not in attendance_data:
                attendance_data[course_id] = {}
            
            # Créer la clé de la date s'il n'existe pas
            if date not in attendance_data[course_id]:
                attendance_data[course_id][date] = []
            
            # Ajouter l'enregistrement de présence
            attendance_record = {
                "StudentID": record["student_code"],
                "FirstName": record["first_name"],
                "LastName": record["last_name"],
                "Status": record["status"],
                "Present": 1 if record["status"] == "present" else 0
            }
            
            attendance_data[course_id][date].append(attendance_record)
        
        return attendance_data
    
    def get_students(self):
        """
        Récupère la liste de tous les étudiants.
        
        Returns:
            pandas.DataFrame: DataFrame contenant les données des étudiants
        """
        return self.students_df
    
    def get_courses(self):
        """
        Récupère la liste de tous les cours.
        
        Returns:
            pandas.DataFrame: DataFrame contenant les données des cours
        """
        return self.courses_df
    
    def get_attendance_for_course(self, course_id, date=None):
        """
        Récupère les données de présence pour un cours spécifique.
        
        Args:
            course_id (str): ID du cours
            date (str, optional): Date spécifique (format YYYY-MM-DD)
            
        Returns:
            pandas.DataFrame: DataFrame contenant les données de présence
        """
        if course_id not in self.attendance_data:
            self.logger.warning(f"Aucune donnée de présence trouvée pour le cours: {course_id}")
            return pd.DataFrame(columns=["StudentID", "FirstName", "LastName", "Status", "Present"])
        
        if date and date in self.attendance_data[course_id]:
            # Retourner les données pour une date spécifique
            return pd.DataFrame(self.attendance_data[course_id][date])
        elif not date:
            # Retourner toutes les données pour le cours
            all_records = []
            for date_records in self.attendance_data[course_id].values():
                all_records.extend(date_records)
            return pd.DataFrame(all_records)
        else:
            self.logger.warning(f"Aucune donnée de présence trouvée pour le cours {course_id} à la date {date}")
            return pd.DataFrame(columns=["StudentID", "FirstName", "LastName", "Status", "Present"])
    
    def get_attendance_dates_for_course(self, course_id):
        """
        Récupère les dates de présence pour un cours spécifique.
        
        Args:
            course_id (str): ID du cours
            
        Returns:
            list: Liste des dates de présence
        """
        if course_id not in self.attendance_data:
            return []
        
        return list(self.attendance_data[course_id].keys())
    
    def reload_data(self):
        """
        Recharge toutes les données depuis la base de données.
        """
        self.students_df = self._load_students()
        self.courses_df = self._load_courses()
        self.attendance_data = self._load_attendance()
        self.logger.info("Données rechargées depuis la base de données")
