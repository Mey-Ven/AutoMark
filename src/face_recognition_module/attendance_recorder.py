import os
import csv
import datetime
from typing import List, Dict, Optional


class AttendanceRecorder:
    """
    Classe pour l'enregistrement des présences.
    """
    
    def __init__(self, attendance_dir: str):
        """
        Initialise l'enregistreur de présences.
        
        Args:
            attendance_dir: Chemin vers le répertoire pour stocker les fichiers de présence.
        """
        self.attendance_dir = attendance_dir
        self.recorded_students = set()  # Pour éviter les doublons dans une même session
        
        # Créer le répertoire s'il n'existe pas
        if not os.path.exists(attendance_dir):
            os.makedirs(attendance_dir)
    
    def record_attendance(self, course_id: str, student_name: str) -> bool:
        """
        Enregistre la présence d'un étudiant pour un cours.
        
        Args:
            course_id: Identifiant du cours.
            student_name: Nom de l'étudiant.
            
        Returns:
            True si l'enregistrement a réussi, False sinon.
        """
        # Vérifier si l'étudiant a déjà été enregistré dans cette session
        student_key = f"{course_id}_{student_name}"
        if student_key in self.recorded_students:
            return False
        
        # Obtenir la date et l'heure actuelles
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        
        # Créer le nom du fichier CSV pour ce cours et cette date
        filename = f"{course_id}_{date_str}.csv"
        file_path = os.path.join(self.attendance_dir, filename)
        
        # Vérifier si le fichier existe déjà
        file_exists = os.path.isfile(file_path)
        
        # Ouvrir le fichier en mode append
        with open(file_path, 'a', newline='') as csvfile:
            fieldnames = ['StudentID', 'Date', 'Time']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Écrire l'en-tête si le fichier est nouveau
            if not file_exists:
                writer.writeheader()
            
            # Écrire la présence
            writer.writerow({
                'StudentID': student_name,
                'Date': date_str,
                'Time': time_str
            })
        
        # Marquer l'étudiant comme enregistré pour cette session
        self.recorded_students.add(student_key)
        
        return True
    
    def reset_session(self) -> None:
        """
        Réinitialise la session d'enregistrement.
        """
        self.recorded_students = set()
    
    def get_attendance_for_course(self, course_id: str, date: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Récupère les présences pour un cours à une date donnée.
        
        Args:
            course_id: Identifiant du cours.
            date: Date au format YYYY-MM-DD. Si None, utilise la date actuelle.
            
        Returns:
            Dictionnaire avec les noms des étudiants comme clés et les heures de présence comme valeurs.
        """
        if date is None:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        filename = f"{course_id}_{date}.csv"
        file_path = os.path.join(self.attendance_dir, filename)
        
        attendance_data = {}
        
        if os.path.isfile(file_path):
            with open(file_path, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    student_id = row['StudentID']
                    time = row['Time']
                    
                    if student_id not in attendance_data:
                        attendance_data[student_id] = []
                    
                    attendance_data[student_id].append(time)
        
        return attendance_data
