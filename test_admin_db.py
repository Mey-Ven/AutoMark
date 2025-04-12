"""
Script de test de l'interface d'administration avec la base de données.
Ce script teste les fonctionnalités de base de l'interface d'administration avec la base de données.
"""

import os
import sys
import pandas as pd

# Ajouter le répertoire src au chemin Python
sys.path.append(os.path.abspath("."))

from src.database.db_manager_v2 import DatabaseManager
from src.dashboard.utils.db_data_loader import DBDataLoader

def test_admin_db():
    """
    Teste les fonctionnalités de base de l'interface d'administration avec la base de données.
    """
    print("Test de l'interface d'administration avec la base de données...")
    
    # Initialiser le gestionnaire de base de données
    db_manager = DatabaseManager("data/automark.db")
    
    # Initialiser le chargeur de données
    data_loader = DBDataLoader("data")
    
    # Tester la gestion des cours
    print("\nTest de la gestion des cours...")
    
    # Récupérer les cours
    courses_df = data_loader.get_courses()
    print(f"Nombre de cours: {len(courses_df)}")
    if not courses_df.empty:
        print("Cours disponibles:")
        for i, row in courses_df.iterrows():
            print(f"  - {row['CourseName']} ({row['CourseID']})")
    
    # Ajouter un cours
    course_name = "Test Course"
    instructor = "Test Instructor"
    group = "Test Group"
    schedule = "Test Schedule"
    
    print(f"\nAjout d'un cours: {course_name}, {instructor}, {group}, {schedule}")
    course_id = data_loader.add_course(course_name, instructor, group, schedule)
    print(f"Cours ajouté avec l'ID: {course_id}")
    
    # Vérifier que le cours a été ajouté
    courses_df = data_loader.get_courses()
    course_added = courses_df[courses_df['CourseID'] == course_id]
    if not course_added.empty:
        print("Cours ajouté avec succès:")
        print(f"  - {course_added.iloc[0]['CourseName']} ({course_added.iloc[0]['CourseID']})")
    else:
        print("Erreur: Le cours n'a pas été ajouté!")
    
    # Mettre à jour le cours
    new_course_name = "Updated Test Course"
    new_instructor = "Updated Test Instructor"
    new_group = "Updated Test Group"
    new_schedule = "Updated Test Schedule"
    
    print(f"\nMise à jour du cours {course_id}: {new_course_name}, {new_instructor}, {new_group}, {new_schedule}")
    success = data_loader.update_course(course_id, new_course_name, new_instructor, new_group, new_schedule)
    print(f"Mise à jour du cours: {success}")
    
    # Vérifier que le cours a été mis à jour
    courses_df = data_loader.get_courses()
    course_updated = courses_df[courses_df['CourseID'] == course_id]
    if not course_updated.empty:
        print("Cours mis à jour avec succès:")
        print(f"  - {course_updated.iloc[0]['CourseName']} ({course_updated.iloc[0]['CourseID']})")
    else:
        print("Erreur: Le cours n'a pas été mis à jour!")
    
    # Supprimer le cours
    print(f"\nSuppression du cours {course_id}")
    success = data_loader.delete_course(course_id)
    print(f"Suppression du cours: {success}")
    
    # Vérifier que le cours a été supprimé
    courses_df = data_loader.get_courses()
    course_deleted = courses_df[courses_df['CourseID'] == course_id]
    if course_deleted.empty:
        print("Cours supprimé avec succès!")
    else:
        print("Erreur: Le cours n'a pas été supprimé!")
    
    # Tester la gestion des étudiants
    print("\nTest de la gestion des étudiants...")
    
    # Récupérer les étudiants
    students_df = data_loader.get_students()
    print(f"Nombre d'étudiants: {len(students_df)}")
    if not students_df.empty:
        print("Étudiants disponibles:")
        for i, row in students_df.iterrows():
            print(f"  - {row['FirstName']} {row['LastName']} ({row['StudentID']})")
    
    # Ajouter un étudiant
    first_name = "Test"
    last_name = "Student"
    group = "Test Group"
    
    print(f"\nAjout d'un étudiant: {first_name} {last_name}, {group}")
    student_id = data_loader.add_student(first_name, last_name, group)
    print(f"Étudiant ajouté avec l'ID: {student_id}")
    
    # Vérifier que l'étudiant a été ajouté
    students_df = data_loader.get_students()
    student_added = students_df[students_df['StudentID'] == student_id]
    if not student_added.empty:
        print("Étudiant ajouté avec succès:")
        print(f"  - {student_added.iloc[0]['FirstName']} {student_added.iloc[0]['LastName']} ({student_added.iloc[0]['StudentID']})")
    else:
        print("Erreur: L'étudiant n'a pas été ajouté!")
    
    # Mettre à jour l'étudiant
    new_first_name = "Updated Test"
    new_last_name = "Updated Student"
    new_group = "Updated Test Group"
    
    print(f"\nMise à jour de l'étudiant {student_id}: {new_first_name} {new_last_name}, {new_group}")
    success = data_loader.update_student(student_id, new_first_name, new_last_name, new_group)
    print(f"Mise à jour de l'étudiant: {success}")
    
    # Vérifier que l'étudiant a été mis à jour
    students_df = data_loader.get_students()
    student_updated = students_df[students_df['StudentID'] == student_id]
    if not student_updated.empty:
        print("Étudiant mis à jour avec succès:")
        print(f"  - {student_updated.iloc[0]['FirstName']} {student_updated.iloc[0]['LastName']} ({student_updated.iloc[0]['StudentID']})")
    else:
        print("Erreur: L'étudiant n'a pas été mis à jour!")
    
    # Tester la gestion des présences
    print("\nTest de la gestion des présences...")
    
    # Ajouter un cours et un étudiant pour le test
    course_id = data_loader.add_course("Test Course", "Test Instructor", "Test Group", "Test Schedule")
    
    # Récupérer les présences
    attendance_df = data_loader.get_attendance()
    print(f"Nombre d'enregistrements de présence: {len(attendance_df)}")
    
    # Ajouter un enregistrement de présence
    date = "2023-09-04"
    status = "present"
    method = "Test"
    
    print(f"\nAjout d'un enregistrement de présence: {course_id}, {student_id}, {date}, {status}, {method}")
    attendance_id = data_loader.add_attendance(course_id, student_id, date, status, method)
    print(f"Enregistrement de présence ajouté avec l'ID: {attendance_id}")
    
    # Vérifier que l'enregistrement de présence a été ajouté
    attendance_df = data_loader.get_attendance()
    attendance_added = attendance_df[attendance_df['ID'] == attendance_id]
    if not attendance_added.empty:
        print("Enregistrement de présence ajouté avec succès:")
        print(f"  - Cours: {attendance_added.iloc[0]['CourseID']}")
        print(f"  - Étudiant: {attendance_added.iloc[0]['StudentID']}")
        print(f"  - Date: {attendance_added.iloc[0]['Date']}")
        print(f"  - Statut: {attendance_added.iloc[0]['Status']}")
    else:
        print("Erreur: L'enregistrement de présence n'a pas été ajouté!")
    
    # Supprimer l'enregistrement de présence
    print(f"\nSuppression de l'enregistrement de présence {attendance_id}")
    success = data_loader.delete_attendance(attendance_id)
    print(f"Suppression de l'enregistrement de présence: {success}")
    
    # Vérifier que l'enregistrement de présence a été supprimé
    attendance_df = data_loader.get_attendance()
    attendance_deleted = attendance_df[attendance_df['ID'] == attendance_id]
    if attendance_deleted.empty:
        print("Enregistrement de présence supprimé avec succès!")
    else:
        print("Erreur: L'enregistrement de présence n'a pas été supprimé!")
    
    # Supprimer l'étudiant
    print(f"\nSuppression de l'étudiant {student_id}")
    success = data_loader.delete_student(student_id)
    print(f"Suppression de l'étudiant: {success}")
    
    # Vérifier que l'étudiant a été supprimé
    students_df = data_loader.get_students()
    student_deleted = students_df[students_df['StudentID'] == student_id]
    if student_deleted.empty:
        print("Étudiant supprimé avec succès!")
    else:
        print("Erreur: L'étudiant n'a pas été supprimé!")
    
    # Supprimer le cours
    print(f"\nSuppression du cours {course_id}")
    success = data_loader.delete_course(course_id)
    print(f"Suppression du cours: {success}")
    
    # Vérifier que le cours a été supprimé
    courses_df = data_loader.get_courses()
    course_deleted = courses_df[courses_df['CourseID'] == course_id]
    if course_deleted.empty:
        print("Cours supprimé avec succès!")
    else:
        print("Erreur: Le cours n'a pas été supprimé!")
    
    print("\nTest de l'interface d'administration avec la base de données terminé avec succès!")

if __name__ == "__main__":
    test_admin_db()
