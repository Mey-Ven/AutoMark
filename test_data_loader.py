"""
Script de test du chargeur de données.
Ce script teste les fonctionnalités de base du chargeur de données.
"""

import os
import sys

# Ajouter le répertoire src au chemin Python
sys.path.append(os.path.abspath("."))

from src.dashboard.utils.db_data_loader import DBDataLoader

def test_data_loader(data_dir):
    """
    Teste les fonctionnalités de base du chargeur de données.
    
    Args:
        data_dir: Répertoire contenant les données
    """
    print(f"Test du chargeur de données {data_dir}...")
    
    # Initialiser le chargeur de données
    data_loader = DBDataLoader(data_dir)
    
    # Tester la récupération des cours
    courses_df = data_loader.get_courses()
    print(f"Nombre de cours: {len(courses_df)}")
    if not courses_df.empty:
        print("Premier cours:")
        print(courses_df.iloc[0])
    
    # Tester la récupération des étudiants
    students_df = data_loader.get_students()
    print(f"Nombre d'étudiants: {len(students_df)}")
    if not students_df.empty:
        print("Premier étudiant:")
        print(students_df.iloc[0])
    
    # Tester la récupération des présences
    attendance_df = data_loader.get_attendance()
    print(f"Nombre d'enregistrements de présence: {len(attendance_df)}")
    if not attendance_df.empty:
        print("Premier enregistrement de présence:")
        print(attendance_df.iloc[0])
    
    # Tester l'ajout d'un cours
    course_id = data_loader.add_course("Test Course", "Test Instructor", "Test Group", "Test Schedule")
    print(f"Cours ajouté avec l'ID: {course_id}")
    
    # Tester la mise à jour d'un cours
    if course_id:
        success = data_loader.update_course(course_id, "Updated Test Course", "Updated Test Instructor", "Updated Test Group", "Updated Test Schedule")
        print(f"Mise à jour du cours: {success}")
    
    # Tester l'ajout d'un étudiant
    student_id = data_loader.add_student("Test", "Student", "Test Group")
    print(f"Étudiant ajouté avec l'ID: {student_id}")
    
    # Tester la mise à jour d'un étudiant
    if student_id:
        success = data_loader.update_student(student_id, "Updated Test", "Updated Student", "Updated Test Group")
        print(f"Mise à jour de l'étudiant: {success}")
    
    # Tester l'ajout d'un enregistrement de présence
    if course_id and student_id:
        attendance_id = data_loader.add_attendance(course_id, student_id, "2023-09-04", "present", "Test")
        print(f"Enregistrement de présence ajouté avec l'ID: {attendance_id}")
    
    # Tester la suppression d'un enregistrement de présence
    if 'attendance_id' in locals() and attendance_id:
        success = data_loader.delete_attendance(attendance_id)
        print(f"Suppression de l'enregistrement de présence: {success}")
    
    # Tester la suppression d'un étudiant
    if student_id:
        success = data_loader.delete_student(student_id)
        print(f"Suppression de l'étudiant: {success}")
    
    # Tester la suppression d'un cours
    if course_id:
        success = data_loader.delete_course(course_id)
        print(f"Suppression du cours: {success}")
    
    print("Test terminé avec succès!")

if __name__ == "__main__":
    data_dir = "data"
    test_data_loader(data_dir)
