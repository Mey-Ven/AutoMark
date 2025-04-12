"""
Script de test des opérations de base de données.
Ce script teste les opérations d'ajout, de modification et de suppression dans la base de données.
"""

import os
import sys
import sqlite3

# Ajouter le répertoire src au chemin Python
sys.path.append(os.path.abspath("."))

from src.database.db_manager_v2 import DatabaseManager

def test_db_operations():
    """
    Teste les opérations d'ajout, de modification et de suppression dans la base de données.
    """
    print("Test des opérations de base de données...")
    
    # Initialiser le gestionnaire de base de données
    db_path = "data/automark.db"
    db_manager = DatabaseManager(db_path)
    
    # Tester l'ajout d'un cours
    print("\nTest de l'ajout d'un cours...")
    course_name = "Test Course"
    instructor = "Test Instructor"
    group_name = "Test Group"
    schedule = "Test Schedule"
    
    print(f"Ajout d'un cours: {course_name}, {instructor}, {group_name}, {schedule}")
    course_id = db_manager.add_course(course_name, instructor, group_name, schedule)
    print(f"Cours ajouté avec l'ID: {course_id}")
    
    # Vérifier que le cours a été ajouté
    print("\nVérification de l'ajout du cours...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
    course = cursor.fetchone()
    if course:
        print("Cours ajouté avec succès:")
        print(f"  - ID: {course[0]}")
        print(f"  - Nom: {course[1]}")
        print(f"  - Enseignant: {course[2]}")
        print(f"  - Groupe: {course[3]}")
        print(f"  - Horaire: {course[4]}")
    else:
        print("Erreur: Le cours n'a pas été ajouté!")
    
    # Tester la modification d'un cours
    print("\nTest de la modification d'un cours...")
    new_course_name = "Updated Test Course"
    new_instructor = "Updated Test Instructor"
    new_group_name = "Updated Test Group"
    new_schedule = "Updated Test Schedule"
    
    print(f"Modification du cours {course_id}: {new_course_name}, {new_instructor}, {new_group_name}, {new_schedule}")
    success = db_manager.update_course(course_id, new_course_name, new_instructor, new_group_name, new_schedule)
    print(f"Modification du cours: {success}")
    
    # Vérifier que le cours a été modifié
    print("\nVérification de la modification du cours...")
    cursor.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
    course = cursor.fetchone()
    if course:
        print("Cours modifié avec succès:")
        print(f"  - ID: {course[0]}")
        print(f"  - Nom: {course[1]}")
        print(f"  - Enseignant: {course[2]}")
        print(f"  - Groupe: {course[3]}")
        print(f"  - Horaire: {course[4]}")
    else:
        print("Erreur: Le cours n'a pas été trouvé après modification!")
    
    # Tester la suppression d'un cours
    print("\nTest de la suppression d'un cours...")
    print(f"Suppression du cours {course_id}")
    success = db_manager.delete_course(course_id)
    print(f"Suppression du cours: {success}")
    
    # Vérifier que le cours a été supprimé
    print("\nVérification de la suppression du cours...")
    cursor.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
    course = cursor.fetchone()
    if course:
        print("Erreur: Le cours n'a pas été supprimé!")
    else:
        print("Cours supprimé avec succès!")
    
    # Fermer la connexion
    conn.close()
    
    print("\nTest des opérations de base de données terminé!")

if __name__ == "__main__":
    test_db_operations()
