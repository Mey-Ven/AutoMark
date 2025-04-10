import os
import cv2
import argparse
import time
import datetime
import pandas as pd
from typing import Dict, Any, Optional

from src.face_recognition_module.face_detector import FaceDetector
from src.face_recognition_module.attendance_recorder import AttendanceRecorder


def parse_arguments():
    """
    Parse les arguments de ligne de commande.
    
    Returns:
        Arguments parsés.
    """
    parser = argparse.ArgumentParser(description="Système de reconnaissance faciale pour la gestion de présence")
    
    parser.add_argument(
        "--course", "-c",
        type=str,
        required=True,
        help="ID du cours pour lequel enregistrer les présences"
    )
    
    parser.add_argument(
        "--camera", "-cam",
        type=int,
        default=0,
        help="ID de la caméra à utiliser (défaut: 0)"
    )
    
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=5,
        help="Intervalle en secondes entre les détections (défaut: 5)"
    )
    
    parser.add_argument(
        "--threshold", "-t",
        type=float,
        default=0.6,
        help="Seuil de confiance pour la reconnaissance faciale (défaut: 0.6)"
    )
    
    return parser.parse_args()


def main():
    """
    Point d'entrée principal du système de reconnaissance faciale.
    """
    # Parser les arguments
    args = parse_arguments()
    
    # Chemins des répertoires
    base_dir = os.path.dirname(os.path.abspath(__file__))
    students_dir = os.path.join(base_dir, "data", "students")
    attendance_dir = os.path.join(base_dir, "data", "attendance")
    
    # Créer les répertoires s'ils n'existent pas
    os.makedirs(students_dir, exist_ok=True)
    os.makedirs(attendance_dir, exist_ok=True)
    
    # Initialiser le détecteur de visages
    face_detector = FaceDetector(students_dir)
    
    # Initialiser l'enregistreur de présences
    attendance_recorder = AttendanceRecorder(attendance_dir)
    
    # Ouvrir la caméra
    cap = cv2.VideoCapture(args.camera)
    
    if not cap.isOpened():
        print(f"Erreur: Impossible d'ouvrir la caméra {args.camera}")
        return
    
    # Variables pour le contrôle de l'intervalle
    last_detection_time = time.time() - args.interval
    
    print(f"Démarrage de la reconnaissance faciale pour le cours {args.course}")
    print("Appuyez sur 'q' pour quitter")
    
    while True:
        # Lire une image de la caméra
        ret, frame = cap.read()
        
        if not ret:
            print("Erreur: Impossible de lire l'image de la caméra")
            break
        
        # Vérifier si l'intervalle est écoulé
        current_time = time.time()
        time_elapsed = current_time - last_detection_time
        
        # Afficher le temps restant avant la prochaine détection
        remaining_time = max(0, args.interval - time_elapsed)
        cv2.putText(
            frame,
            f"Prochaine detection dans: {remaining_time:.1f}s",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )
        
        # Effectuer la détection à intervalles réguliers
        if time_elapsed >= args.interval:
            # Traiter l'image pour détecter et reconnaître les visages
            processed_frame, face_names = face_detector.process_frame(frame)
            
            # Enregistrer les présences
            for name in face_names:
                if name != "Inconnu":
                    if attendance_recorder.record_attendance(args.course, name):
                        print(f"Présence enregistrée: {name}")
            
            # Mettre à jour le temps de la dernière détection
            last_detection_time = current_time
            
            # Utiliser l'image traitée
            frame = processed_frame
        
        # Afficher l'image
        cv2.imshow("AutoMark - Reconnaissance faciale", frame)
        
        # Quitter si 'q' est pressé
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Libérer les ressources
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
