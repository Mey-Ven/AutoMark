"""
Script de migration des données des fichiers CSV vers la base de données SQLite.
Ce script est utilisé pour initialiser la base de données avec les données existantes.
"""

import os
import argparse
from db_manager_v2 import DatabaseManager

def migrate_data(data_dir, db_path):
    """
    Migre les données des fichiers CSV vers la base de données SQLite.
    
    Args:
        data_dir: Répertoire contenant les fichiers CSV
        db_path: Chemin vers le fichier de base de données SQLite
    """
    print(f"Migration des données de {data_dir} vers {db_path}...")
    
    # Initialiser le gestionnaire de base de données
    db_manager = DatabaseManager(db_path)
    
    # Migrer les cours
    courses_file = os.path.join(data_dir, 'courses.csv')
    if os.path.exists(courses_file):
        courses_count = db_manager.import_courses_from_csv(courses_file)
        print(f"Importation de {courses_count} cours depuis {courses_file}")
    else:
        print(f"Fichier {courses_file} introuvable")
    
    # Migrer les étudiants
    students_file = os.path.join(data_dir, 'students.csv')
    if os.path.exists(students_file):
        students_count = db_manager.import_students_from_csv(students_file)
        print(f"Importation de {students_count} étudiants depuis {students_file}")
    else:
        print(f"Fichier {students_file} introuvable")
    
    # Migrer les présences
    attendance_dir = os.path.join(data_dir, 'attendance')
    if os.path.exists(attendance_dir):
        attendance_count = db_manager.import_attendance_from_directory(attendance_dir)
        print(f"Importation de {attendance_count} enregistrements de présence depuis {attendance_dir}")
    else:
        print(f"Répertoire {attendance_dir} introuvable")
    
    print("Migration terminée avec succès!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrer les données des fichiers CSV vers la base de données SQLite")
    parser.add_argument("--data-dir", default="data", help="Répertoire contenant les fichiers CSV")
    parser.add_argument("--db-path", default="data/automark.db", help="Chemin vers le fichier de base de données SQLite")
    
    args = parser.parse_args()
    
    migrate_data(args.data_dir, args.db_path)
