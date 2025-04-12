"""
Script de test des fonctionnalités de filtrage et de recherche dans l'interface d'administration.
Ce script teste les fonctionnalités de filtrage et de recherche dans l'interface d'administration.
"""

import os
import sys
import pandas as pd

# Ajouter le répertoire src au chemin Python
sys.path.append(os.path.abspath("."))

from src.database.db_manager_v2 import DatabaseManager
from src.dashboard.utils.db_data_loader import DBDataLoader

def test_admin_filtering():
    """
    Teste les fonctionnalités de filtrage et de recherche dans l'interface d'administration.
    """
    print("Test des fonctionnalités de filtrage et de recherche dans l'interface d'administration...")
    
    # Initialiser le gestionnaire de base de données
    db_manager = DatabaseManager("data/automark.db")
    
    # Initialiser le chargeur de données
    data_loader = DBDataLoader("data")
    
    # Tester le filtrage des cours
    print("\nTest du filtrage des cours...")
    
    # Récupérer les cours
    courses_df = data_loader.get_courses()
    print(f"Nombre total de cours: {len(courses_df)}")
    
    # Filtrer les cours par nom
    search_term = "Math"
    print(f"\nFiltrage des cours par nom: {search_term}")
    filtered_courses = courses_df[courses_df['CourseName'].str.contains(search_term, case=False)]
    print(f"Nombre de cours filtrés: {len(filtered_courses)}")
    if not filtered_courses.empty:
        print("Cours filtrés:")
        for i, row in filtered_courses.iterrows():
            print(f"  - {row['CourseName']} ({row['CourseID']})")
    
    # Filtrer les cours par enseignant
    search_term = "Dupont"
    print(f"\nFiltrage des cours par enseignant: {search_term}")
    filtered_courses = courses_df[courses_df['Instructor'].str.contains(search_term, case=False)]
    print(f"Nombre de cours filtrés: {len(filtered_courses)}")
    if not filtered_courses.empty:
        print("Cours filtrés:")
        for i, row in filtered_courses.iterrows():
            print(f"  - {row['CourseName']} ({row['CourseID']})")
    
    # Filtrer les cours par groupe
    search_term = "Groupe A"
    print(f"\nFiltrage des cours par groupe: {search_term}")
    filtered_courses = courses_df[courses_df['Group'] == search_term]
    print(f"Nombre de cours filtrés: {len(filtered_courses)}")
    if not filtered_courses.empty:
        print("Cours filtrés:")
        for i, row in filtered_courses.iterrows():
            print(f"  - {row['CourseName']} ({row['CourseID']})")
    
    # Tester le filtrage des étudiants
    print("\nTest du filtrage des étudiants...")
    
    # Récupérer les étudiants
    students_df = data_loader.get_students()
    print(f"Nombre total d'étudiants: {len(students_df)}")
    
    # Filtrer les étudiants par prénom
    search_term = "Jean"
    print(f"\nFiltrage des étudiants par prénom: {search_term}")
    filtered_students = students_df[students_df['FirstName'].str.contains(search_term, case=False)]
    print(f"Nombre d'étudiants filtrés: {len(filtered_students)}")
    if not filtered_students.empty:
        print("Étudiants filtrés:")
        for i, row in filtered_students.iterrows():
            print(f"  - {row['FirstName']} {row['LastName']} ({row['StudentID']})")
    
    # Filtrer les étudiants par nom
    search_term = "Dupont"
    print(f"\nFiltrage des étudiants par nom: {search_term}")
    filtered_students = students_df[students_df['LastName'].str.contains(search_term, case=False)]
    print(f"Nombre d'étudiants filtrés: {len(filtered_students)}")
    if not filtered_students.empty:
        print("Étudiants filtrés:")
        for i, row in filtered_students.iterrows():
            print(f"  - {row['FirstName']} {row['LastName']} ({row['StudentID']})")
    
    # Filtrer les étudiants par groupe
    search_term = "Groupe A"
    print(f"\nFiltrage des étudiants par groupe: {search_term}")
    filtered_students = students_df[students_df['Group'] == search_term]
    print(f"Nombre d'étudiants filtrés: {len(filtered_students)}")
    if not filtered_students.empty:
        print("Étudiants filtrés:")
        for i, row in filtered_students.iterrows():
            print(f"  - {row['FirstName']} {row['LastName']} ({row['StudentID']})")
    
    # Tester le filtrage des présences
    print("\nTest du filtrage des présences...")
    
    # Récupérer les présences
    attendance_df = data_loader.get_attendance()
    print(f"Nombre total d'enregistrements de présence: {len(attendance_df)}")
    
    # Filtrer les présences par cours
    course_id = "MATH101"
    print(f"\nFiltrage des présences par cours: {course_id}")
    filtered_attendance = attendance_df[attendance_df['CourseID'] == course_id]
    print(f"Nombre d'enregistrements de présence filtrés: {len(filtered_attendance)}")
    if not filtered_attendance.empty:
        print("Enregistrements de présence filtrés:")
        for i, row in filtered_attendance.iterrows():
            print(f"  - Cours: {row['CourseID']}, Étudiant: {row['StudentID']}, Date: {row['Date']}")
    
    # Filtrer les présences par étudiant
    student_id = "S001"
    print(f"\nFiltrage des présences par étudiant: {student_id}")
    filtered_attendance = attendance_df[attendance_df['StudentID'] == student_id]
    print(f"Nombre d'enregistrements de présence filtrés: {len(filtered_attendance)}")
    if not filtered_attendance.empty:
        print("Enregistrements de présence filtrés:")
        for i, row in filtered_attendance.iterrows():
            print(f"  - Cours: {row['CourseID']}, Étudiant: {row['StudentID']}, Date: {row['Date']}")
    
    # Filtrer les présences par date
    date = "2023-09-01"
    print(f"\nFiltrage des présences par date: {date}")
    filtered_attendance = attendance_df[attendance_df['Date'] == date]
    print(f"Nombre d'enregistrements de présence filtrés: {len(filtered_attendance)}")
    if not filtered_attendance.empty:
        print("Enregistrements de présence filtrés:")
        for i, row in filtered_attendance.iterrows():
            print(f"  - Cours: {row['CourseID']}, Étudiant: {row['StudentID']}, Date: {row['Date']}")
    
    # Filtrer les présences par statut
    status = "present"
    print(f"\nFiltrage des présences par statut: {status}")
    filtered_attendance = attendance_df[attendance_df['Status'] == status]
    print(f"Nombre d'enregistrements de présence filtrés: {len(filtered_attendance)}")
    if not filtered_attendance.empty:
        print("Enregistrements de présence filtrés (échantillon de 5 premiers):")
        for i, row in filtered_attendance.head(5).iterrows():
            print(f"  - Cours: {row['CourseID']}, Étudiant: {row['StudentID']}, Date: {row['Date']}")
    
    print("\nTest des fonctionnalités de filtrage et de recherche terminé avec succès!")

if __name__ == "__main__":
    test_admin_filtering()
