#!/usr/bin/env python3
"""
Script de test pour l'adaptateur de données SQLite dans AutoMark.
"""

import os
import sys
import argparse
import logging
import pandas as pd

# Ajouter le répertoire courant au chemin de recherche des modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.database.data_adapter import SQLiteDataAdapter

def main():
    """Fonction principale du script."""
    # Configuration du logging
    logging.basicConfig(level=logging.INFO, 
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger = logging.getLogger("test_adapter")
    
    # Analyser les arguments de ligne de commande
    parser = argparse.ArgumentParser(description="Tester l'adaptateur de données SQLite pour AutoMark")
    parser.add_argument("--data-dir", default="data", help="Chemin vers le répertoire de données")
    args = parser.parse_args()
    
    # Chemin absolu vers le répertoire de données
    data_dir = os.path.abspath(args.data_dir)
    if not os.path.exists(data_dir):
        logger.error(f"Le répertoire de données n'existe pas: {data_dir}")
        return 1
    
    # Créer l'adaptateur de données SQLite
    logger.info("Création de l'adaptateur de données SQLite")
    adapter = SQLiteDataAdapter(data_dir)
    
    # Tester les fonctions de l'adaptateur
    
    # Récupérer les étudiants
    students = adapter.get_students()
    logger.info(f"Nombre d'étudiants: {len(students)}")
    if not students.empty:
        logger.info(f"Premier étudiant: {students.iloc[0]['FirstName']} {students.iloc[0]['LastName']}")
    
    # Récupérer les cours
    courses = adapter.get_courses()
    logger.info(f"Nombre de cours: {len(courses)}")
    if not courses.empty:
        logger.info(f"Premier cours: {courses.iloc[0]['CourseName']}")
    
    # Récupérer les présences pour un cours
    course_id = "MATH101"
    attendance = adapter.get_attendance_for_course(course_id)
    logger.info(f"Nombre de présences pour le cours {course_id}: {len(attendance)}")
    
    # Récupérer les dates de présence pour un cours
    dates = adapter.get_attendance_dates_for_course(course_id)
    logger.info(f"Dates de présence pour le cours {course_id}: {dates}")
    
    # Récupérer les présences pour un cours à une date spécifique
    if dates:
        date = dates[0]
        attendance = adapter.get_attendance_for_course(course_id, date)
        logger.info(f"Nombre de présences pour le cours {course_id} à la date {date}: {len(attendance)}")
    
    logger.info("Test de l'adaptateur de données SQLite terminé avec succès")
    return 0

if __name__ == "__main__":
    sys.exit(main())
