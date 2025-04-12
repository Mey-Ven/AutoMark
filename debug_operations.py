"""
Script de débogage pour tester les opérations d'ajout, de modification et de suppression.
"""

import os
import sys
import pandas as pd
from datetime import datetime

# Ajouter le répertoire src au chemin Python
sys.path.append(os.path.abspath("."))

from src.dashboard.utils.db_data_loader import DBDataLoader

def debug_operations():
    """
    Teste les opérations d'ajout, de modification et de suppression.
    """
    print("Débogage des opérations d'ajout, de modification et de suppression...")
    
    # Initialiser le chargeur de données
    data_loader = DBDataLoader("data")
    
    # Afficher les cours existants
    courses_df = data_loader.get_courses()
    print(f"Nombre de cours existants: {len(courses_df)}")
    if not courses_df.empty:
        print("Cours existants:")
        for _, row in courses_df.iterrows():
            print(f"  - {row['CourseName']} ({row['CourseID']})")
    
    # Ajouter un cours
    course_name = f"Test Course {datetime.now().strftime('%H%M%S')}"
    instructor = "Test Instructor"
    group = "Groupe A"
    schedule = "Test Schedule"
    
    print(f"\nAjout d'un cours: {course_name}, {instructor}, {group}, {schedule}")
    course_id = data_loader.add_course(course_name, instructor, group, schedule)
    print(f"Résultat de l'ajout: {course_id}")
    
    # Vérifier que le cours a été ajouté
    courses_df = data_loader.get_courses()
    course_added = courses_df[courses_df['CourseID'] == course_id] if course_id else pd.DataFrame()
    if not course_added.empty:
        print("Cours ajouté avec succès:")
        print(f"  - {course_added.iloc[0]['CourseName']} ({course_added.iloc[0]['CourseID']})")
    else:
        print("Erreur: Le cours n'a pas été ajouté!")
    
    # Modifier le cours
    if course_id:
        new_course_name = f"Updated {course_name}"
        new_instructor = "Updated Instructor"
        new_group = "Groupe B"
        new_schedule = "Updated Schedule"
        
        print(f"\nModification du cours {course_id}: {new_course_name}, {new_instructor}, {new_group}, {new_schedule}")
        success = data_loader.update_course(course_id, new_course_name, new_instructor, new_group, new_schedule)
        print(f"Résultat de la modification: {success}")
        
        # Vérifier que le cours a été modifié
        courses_df = data_loader.get_courses()
        course_updated = courses_df[courses_df['CourseID'] == course_id]
        if not course_updated.empty:
            print("Cours modifié avec succès:")
            print(f"  - {course_updated.iloc[0]['CourseName']} ({course_updated.iloc[0]['CourseID']})")
        else:
            print("Erreur: Le cours n'a pas été modifié!")
    
    # Supprimer le cours
    if course_id:
        print(f"\nSuppression du cours {course_id}")
        success = data_loader.delete_course(course_id)
        print(f"Résultat de la suppression: {success}")
        
        # Vérifier que le cours a été supprimé
        courses_df = data_loader.get_courses()
        course_deleted = courses_df[courses_df['CourseID'] == course_id]
        if course_deleted.empty:
            print("Cours supprimé avec succès!")
        else:
            print("Erreur: Le cours n'a pas été supprimé!")
    
    print("\nDébogage terminé!")

if __name__ == "__main__":
    debug_operations()
