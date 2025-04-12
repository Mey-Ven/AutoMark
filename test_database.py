"""
Script de test de la base de données.
Ce script teste les fonctionnalités de base du gestionnaire de base de données.
"""

import os
import sys

# Ajouter le répertoire src au chemin Python
sys.path.append(os.path.abspath("."))

from src.database.db_manager_v2 import DatabaseManager

def test_database(db_path):
    """
    Teste les fonctionnalités de base du gestionnaire de base de données.
    
    Args:
        db_path: Chemin vers le fichier de base de données SQLite
    """
    print(f"Test de la base de données {db_path}...")
    
    # Initialiser le gestionnaire de base de données
    db_manager = DatabaseManager(db_path)
    
    # Tester la récupération des cours
    courses_df = db_manager.get_all_courses()
    print(f"Nombre de cours: {len(courses_df)}")
    if not courses_df.empty:
        print("Premier cours:")
        print(courses_df.iloc[0])
    
    # Tester la récupération des étudiants
    students_df = db_manager.get_all_students()
    print(f"Nombre d'étudiants: {len(students_df)}")
    if not students_df.empty:
        print("Premier étudiant:")
        print(students_df.iloc[0])
    
    # Tester la récupération des présences
    attendance_df = db_manager.get_all_attendance()
    print(f"Nombre d'enregistrements de présence: {len(attendance_df)}")
    if not attendance_df.empty:
        print("Premier enregistrement de présence:")
        print(attendance_df.iloc[0])
    
    # Tester l'ajout d'un cours
    course_id = db_manager.add_course("Test Course", "Test Instructor", "Test Group", "Test Schedule")
    print(f"Cours ajouté avec l'ID: {course_id}")
    
    # Tester la mise à jour d'un cours
    if course_id:
        success = db_manager.update_course(course_id, "Updated Test Course", "Updated Test Instructor", "Updated Test Group", "Updated Test Schedule")
        print(f"Mise à jour du cours: {success}")
    
    # Tester l'ajout d'un étudiant
    student_id = db_manager.add_student("Test", "Student", "Test Group")
    print(f"Étudiant ajouté avec l'ID: {student_id}")
    
    # Tester la mise à jour d'un étudiant
    if student_id:
        success = db_manager.update_student(student_id, "Updated Test", "Updated Student", "Updated Test Group")
        print(f"Mise à jour de l'étudiant: {success}")
    
    # Tester l'ajout d'un enregistrement de présence
    if course_id and student_id:
        attendance_id = db_manager.add_attendance(course_id, student_id, "2023-09-04", "present", "Test")
        print(f"Enregistrement de présence ajouté avec l'ID: {attendance_id}")
    
    # Tester la suppression d'un enregistrement de présence
    if 'attendance_id' in locals() and attendance_id:
        success = db_manager.delete_attendance(attendance_id)
        print(f"Suppression de l'enregistrement de présence: {success}")
    
    # Tester la suppression d'un étudiant
    if student_id:
        success = db_manager.delete_student(student_id)
        print(f"Suppression de l'étudiant: {success}")
    
    # Tester la suppression d'un cours
    if course_id:
        success = db_manager.delete_course(course_id)
        print(f"Suppression du cours: {success}")
    
    print("Test terminé avec succès!")

if __name__ == "__main__":
    db_path = "data/automark.db"
    test_database(db_path)
