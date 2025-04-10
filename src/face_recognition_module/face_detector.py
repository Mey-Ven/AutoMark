import os
import cv2
import numpy as np
import face_recognition
from typing import List, Dict, Tuple, Optional


class FaceDetector:
    """
    Classe pour la détection et la reconnaissance des visages.
    """
    
    def __init__(self, students_dir: str):
        """
        Initialise le détecteur de visages.
        
        Args:
            students_dir: Chemin vers le répertoire contenant les images des étudiants.
        """
        self.students_dir = students_dir
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_known_faces()
        
    def load_known_faces(self) -> None:
        """
        Charge les visages connus à partir du répertoire des étudiants.
        """
        print("Chargement des visages connus...")
        
        # Parcourir tous les fichiers dans le répertoire des étudiants
        for filename in os.listdir(self.students_dir):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                # Extraire le nom de l'étudiant du nom de fichier (sans l'extension)
                student_name = os.path.splitext(filename)[0]
                
                # Charger l'image
                image_path = os.path.join(self.students_dir, filename)
                image = face_recognition.load_image_file(image_path)
                
                # Trouver les encodages de visage dans l'image
                face_encodings = face_recognition.face_encodings(image)
                
                # S'assurer qu'un visage a été trouvé
                if len(face_encodings) > 0:
                    face_encoding = face_encodings[0]
                    self.known_face_encodings.append(face_encoding)
                    self.known_face_names.append(student_name)
                    print(f"Visage chargé: {student_name}")
                else:
                    print(f"Aucun visage trouvé dans l'image de {student_name}")
        
        print(f"Total des visages chargés: {len(self.known_face_names)}")
    
    def detect_faces(self, frame: np.ndarray) -> Tuple[List[Tuple[int, int, int, int]], List[np.ndarray]]:
        """
        Détecte les visages dans une image.
        
        Args:
            frame: Image à analyser.
            
        Returns:
            Tuple contenant les emplacements des visages et leurs encodages.
        """
        # Redimensionner l'image pour accélérer le traitement
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        
        # Convertir l'image de BGR (OpenCV) à RGB (face_recognition)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Trouver tous les visages dans l'image
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        # Redimensionner les emplacements des visages à la taille originale
        face_locations_original = [(top * 4, right * 4, bottom * 4, left * 4) 
                                  for (top, right, bottom, left) in face_locations]
        
        return face_locations_original, face_encodings
    
    def recognize_faces(self, face_encodings: List[np.ndarray]) -> List[str]:
        """
        Reconnaît les visages à partir de leurs encodages.
        
        Args:
            face_encodings: Liste des encodages de visages à reconnaître.
            
        Returns:
            Liste des noms des personnes reconnues.
        """
        face_names = []
        
        for face_encoding in face_encodings:
            # Comparer le visage avec tous les visages connus
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Inconnu"
            
            # Utiliser la distance euclidienne pour trouver le visage le plus proche
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
            
            face_names.append(name)
        
        return face_names
    
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, List[str]]:
        """
        Traite une image pour détecter et reconnaître les visages.
        
        Args:
            frame: Image à traiter.
            
        Returns:
            Tuple contenant l'image annotée et la liste des noms des personnes reconnues.
        """
        # Détecter les visages
        face_locations, face_encodings = self.detect_faces(frame)
        
        # Reconnaître les visages
        face_names = self.recognize_faces(face_encodings)
        
        # Annoter l'image
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Dessiner un rectangle autour du visage
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            
            # Dessiner une étiquette avec le nom sous le visage
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        
        return frame, face_names
