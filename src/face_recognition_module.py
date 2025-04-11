import os
import json
from datetime import datetime
import pickle
import time
import random
from typing import List, Dict, Tuple, Optional, Union

# Import des dépendances optionnelles
try:
    import cv2
    import numpy as np
    print("OpenCV importé avec succès, version:", cv2.__version__)
except ImportError as e:
    print("Erreur d'importation OpenCV:", str(e))
    raise ImportError("OpenCV est requis pour ce module. Installez-le avec 'pip install opencv-python'")

# Essayer d'importer face_recognition (optionnel)
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
    print("face_recognition importé avec succès")
except ImportError as e:
    FACE_RECOGNITION_AVAILABLE = False
    print("face_recognition n'est pas disponible. Utilisation d'OpenCV uniquement.")

class FaceRecognitionModule:
    """
    Module avancé de reconnaissance faciale pour AutoMark.
    Inclut l'entraînement avec plusieurs photos, la détection de liveness,
    et la reconnaissance par lots.
    """

    def __init__(self, data_dir: str):
        """
        Initialise le module de reconnaissance faciale.

        Args:
            data_dir: Répertoire contenant les données (photos, encodages, etc.)
        """

        self.data_dir = data_dir
        self.photos_dir = os.path.join(data_dir, 'photos')
        self.encodings_file = os.path.join(data_dir, 'face_encodings.pkl')
        self.training_dir = os.path.join(data_dir, 'training_photos')

        # Créer les répertoires s'ils n'existent pas
        os.makedirs(self.photos_dir, exist_ok=True)
        os.makedirs(self.training_dir, exist_ok=True)

        # Initialiser le détecteur de visage avec OpenCV
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # Initialiser le reconnaisseur de visage
        if FACE_RECOGNITION_AVAILABLE:
            # Utiliser face_recognition si disponible
            self.known_face_encodings = {}
            self.load_encodings()
            self.face_detection_model = "hog"  # Options: "hog" (plus rapide) ou "cnn" (plus précis)
            self.recognition_tolerance = 0.6   # Seuil de tolérance pour la reconnaissance (plus bas = plus strict)
        else:
            # Utiliser OpenCV comme alternative
            self.recognizer = cv2.face.LBPHFaceRecognizer_create()
            self.model_path = os.path.join(data_dir, 'face_model.yml')
            self.labels_file = os.path.join(data_dir, 'face_labels.json')

            # Charger le modèle s'il existe
            if os.path.exists(self.model_path):
                try:
                    self.recognizer.read(self.model_path)
                    self.model_trained = True
                except Exception as e:
                    print(f"Erreur lors du chargement du modèle : {e}")
                    self.model_trained = False
            else:
                self.model_trained = False

            # Charger les labels des étudiants
            if os.path.exists(self.labels_file):
                with open(self.labels_file, 'r') as f:
                    self.student_labels = json.load(f)
            else:
                self.student_labels = {}

        # Paramètres communs
        self.min_training_images = 3       # Nombre minimum d'images pour l'entraînement

        # Paramètres de liveness detection
        self.liveness_enabled = True
        self.blink_detection_enabled = False  # Simplifié pour cette version
        self.movement_detection_enabled = False  # Simplifié pour cette version
        self.texture_analysis_enabled = True

    def load_encodings(self) -> None:
        """Charge les encodages faciaux depuis le fichier."""
        if os.path.exists(self.encodings_file):
            try:
                with open(self.encodings_file, 'rb') as f:
                    self.known_face_encodings = pickle.load(f)
                print(f"Encodages chargés : {len(self.known_face_encodings)} étudiants")
            except Exception as e:
                print(f"Erreur lors du chargement des encodages : {e}")
                self.known_face_encodings = {}
        else:
            self.known_face_encodings = {}

    def save_encodings(self) -> None:
        """Sauvegarde les encodages faciaux dans un fichier."""
        try:
            with open(self.encodings_file, 'wb') as f:
                pickle.dump(self.known_face_encodings, f)
            print(f"Encodages sauvegardés : {len(self.known_face_encodings)} étudiants")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des encodages : {e}")

    def add_training_image(self, student_id: str, image) -> Tuple[bool, str]:
        """
        Ajoute une image d'entraînement pour un étudiant.

        Args:
            student_id: ID de l'étudiant
            image: Image à ajouter (numpy array ou chemin de fichier)

        Returns:
            Tuple (succès, message)
        """
        # Créer le répertoire d'entraînement pour l'étudiant s'il n'existe pas
        student_training_dir = os.path.join(self.training_dir, student_id)
        os.makedirs(student_training_dir, exist_ok=True)

        # Charger l'image si c'est un chemin de fichier
        if isinstance(image, str):
            if os.path.exists(image):
                image = cv2.imread(image)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                return False, f"Le fichier {image} n'existe pas"

        # Détecter les visages dans l'image
        face_locations = face_recognition.face_locations(image, model=self.face_detection_model)

        if not face_locations:
            return False, "Aucun visage détecté dans l'image"

        if len(face_locations) > 1:
            return False, "Plusieurs visages détectés dans l'image. Veuillez fournir une image avec un seul visage."

        # Sauvegarder l'image d'entraînement
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = random.randint(1000, 9999)
        image_filename = f"{student_id}_{timestamp}_{random_suffix}.jpg"
        image_path = os.path.join(student_training_dir, image_filename)

        # Convertir l'image en BGR pour la sauvegarde
        cv2.imwrite(image_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

        return True, f"Image d'entraînement ajoutée avec succès : {image_path}"

    def train_student(self, student_id: str) -> Tuple[bool, str]:
        """
        Entraîne le modèle de reconnaissance faciale pour un étudiant spécifique
        en utilisant toutes ses images d'entraînement.

        Args:
            student_id: ID de l'étudiant

        Returns:
            Tuple (succès, message)
        """
        student_training_dir = os.path.join(self.training_dir, student_id)

        if not os.path.exists(student_training_dir):
            return False, f"Aucun répertoire d'entraînement trouvé pour l'étudiant {student_id}"

        # Récupérer toutes les images d'entraînement
        training_images = [f for f in os.listdir(student_training_dir)
                          if f.endswith(('.jpg', '.jpeg', '.png'))]

        if len(training_images) < self.min_training_images:
            return False, f"Pas assez d'images d'entraînement. Minimum requis : {self.min_training_images}"

        # Extraire les encodages de toutes les images
        encodings = []

        for img_file in training_images:
            img_path = os.path.join(student_training_dir, img_file)
            image = cv2.imread(img_path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(image, model=self.face_detection_model)

            if not face_locations:
                continue

            # Prendre le premier visage détecté
            face_encoding = face_recognition.face_encodings(image, [face_locations[0]])[0]
            encodings.append(face_encoding)

        if not encodings:
            return False, "Aucun visage n'a pu être encodé à partir des images d'entraînement"

        # Stocker les encodages pour cet étudiant
        self.known_face_encodings[student_id] = encodings

        # Sauvegarder les encodages mis à jour
        self.save_encodings()

        return True, f"Entraînement réussi avec {len(encodings)} images pour l'étudiant {student_id}"

    def train_all_students(self) -> Tuple[int, int]:
        """
        Entraîne le modèle pour tous les étudiants ayant des images d'entraînement.

        Returns:
            Tuple (nombre d'étudiants entraînés avec succès, nombre d'échecs)
        """
        success_count = 0
        failure_count = 0

        # Parcourir tous les répertoires d'étudiants
        for student_id in os.listdir(self.training_dir):
            student_dir = os.path.join(self.training_dir, student_id)
            if os.path.isdir(student_dir):
                success, _ = self.train_student(student_id)
                if success:
                    success_count += 1
                else:
                    failure_count += 1

        return success_count, failure_count

    def detect_faces(self, image) -> List[Tuple[int, int, int, int]]:
        """
        Détecte les visages dans une image.

        Args:
            image: Image à analyser

        Returns:
            Liste des coordonnées des visages (top, right, bottom, left)
        """
        if isinstance(image, str):
            if os.path.exists(image):
                image = cv2.imread(image)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                return []

        return face_recognition.face_locations(image, model=self.face_detection_model)

    def recognize_faces(self, image) -> List[Dict]:
        """
        Reconnaît les visages dans une image et retourne les identifiants des étudiants.

        Args:
            image: Image à analyser

        Returns:
            Liste de dictionnaires contenant les informations de reconnaissance
        """
        if isinstance(image, str):
            if os.path.exists(image):
                image = cv2.imread(image)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                return []

        # Détecter les visages
        face_locations = face_recognition.face_locations(image, model=self.face_detection_model)

        if not face_locations:
            return []

        # Encoder les visages détectés
        face_encodings = face_recognition.face_encodings(image, face_locations)

        results = []

        # Pour chaque visage détecté
        for i, (face_encoding, face_location) in enumerate(zip(face_encodings, face_locations)):
            # Initialiser le résultat pour ce visage
            result = {
                "face_index": i,
                "location": face_location,
                "matches": [],
                "is_live": self.check_liveness(image, face_location) if self.liveness_enabled else True
            }

            # Comparer avec tous les encodages connus
            for student_id, encodings in self.known_face_encodings.items():
                # Calculer les distances avec tous les encodages de cet étudiant
                distances = face_recognition.face_distance(encodings, face_encoding)

                # Prendre la distance minimale (meilleure correspondance)
                if len(distances) > 0:
                    min_distance = min(distances)
                    match_confidence = 1 - min_distance

                    # Si la confiance est suffisante, ajouter à la liste des correspondances
                    if min_distance <= self.recognition_tolerance:
                        result["matches"].append({
                            "student_id": student_id,
                            "confidence": float(match_confidence),
                            "distance": float(min_distance)
                        })

            # Trier les correspondances par confiance décroissante
            result["matches"].sort(key=lambda x: x["confidence"], reverse=True)

            # Ajouter ce résultat à la liste
            results.append(result)

        return results

    def check_liveness(self, image, face_location) -> bool:
        """
        Vérifie si un visage détecté appartient à une personne réelle (et non une photo).

        Args:
            image: Image contenant le visage
            face_location: Coordonnées du visage (top, right, bottom, left)

        Returns:
            True si le visage semble appartenir à une personne réelle, False sinon
        """
        # Cette implémentation est simplifiée et devrait être améliorée
        # avec des techniques plus avancées comme la détection de clignement,
        # l'analyse de texture, etc.

        top, right, bottom, left = face_location
        face_image = image[top:bottom, left:right]

        # 1. Vérification basique de la variance des couleurs (les photos ont souvent moins de variance)
        color_variance = np.var(face_image)
        if color_variance < 100:  # Seuil arbitraire, à ajuster
            return False

        # 2. Analyse de texture simplifiée
        if self.texture_analysis_enabled:
            gray_face = cv2.cvtColor(face_image, cv2.COLOR_RGB2GRAY)
            laplacian_var = cv2.Laplacian(gray_face, cv2.CV_64F).var()
            if laplacian_var < 50:  # Seuil arbitraire, à ajuster
                return False

        # Note: Pour une détection de liveness plus robuste, il faudrait implémenter:
        # - Détection de clignement des yeux (nécessite plusieurs images)
        # - Détection de mouvements de la tête (nécessite une séquence vidéo)
        # - Analyse de réflexion de la lumière
        # - Détection de texture de la peau

        return True

    def recognize_batch(self, image, max_faces: int = 10) -> Dict:
        """
        Reconnaît plusieurs visages dans une image et retourne les résultats.

        Args:
            image: Image à analyser
            max_faces: Nombre maximum de visages à reconnaître

        Returns:
            Dictionnaire contenant les résultats de reconnaissance
        """
        start_time = time.time()

        # Reconnaître les visages
        recognition_results = self.recognize_faces(image)

        # Limiter le nombre de visages
        recognition_results = recognition_results[:max_faces]

        # Préparer le résultat
        result = {
            "timestamp": datetime.now().isoformat(),
            "processing_time": time.time() - start_time,
            "faces_detected": len(recognition_results),
            "results": recognition_results
        }

        return result

    def capture_training_images(self, student_id: str, camera_index: int = 0, num_images: int = 5) -> Tuple[int, str]:
        """
        Capture plusieurs images d'entraînement à partir de la webcam.

        Args:
            student_id: ID de l'étudiant
            camera_index: Index de la caméra à utiliser
            num_images: Nombre d'images à capturer

        Returns:
            Tuple (nombre d'images capturées, message)
        """
        cap = cv2.VideoCapture(camera_index)

        if not cap.isOpened():
            return 0, "Impossible d'ouvrir la caméra"

        images_captured = 0

        try:
            while images_captured < num_images:
                # Attendre un peu entre chaque capture pour avoir des variations
                time.sleep(1)

                # Capturer une image
                ret, frame = cap.read()

                if not ret:
                    continue

                # Convertir en RGB pour face_recognition
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Détecter les visages
                face_locations = face_recognition.face_locations(rgb_frame, model=self.face_detection_model)

                if not face_locations or len(face_locations) != 1:
                    # Ignorer les images sans visage ou avec plusieurs visages
                    continue

                # Ajouter l'image d'entraînement
                success, message = self.add_training_image(student_id, rgb_frame)

                if success:
                    images_captured += 1
                    print(f"Image {images_captured}/{num_images} capturée")

        finally:
            cap.release()

        return images_captured, f"{images_captured} images capturées avec succès"

    def get_student_training_info(self, student_id: str) -> Dict:
        """
        Récupère les informations d'entraînement pour un étudiant.

        Args:
            student_id: ID de l'étudiant

        Returns:
            Dictionnaire contenant les informations d'entraînement
        """
        student_training_dir = os.path.join(self.training_dir, student_id)

        result = {
            "student_id": student_id,
            "has_encodings": student_id in self.known_face_encodings,
            "num_encodings": len(self.known_face_encodings.get(student_id, [])),
            "training_images": [],
            "is_trained": False
        }

        # Vérifier si le répertoire d'entraînement existe
        if os.path.exists(student_training_dir):
            # Récupérer toutes les images d'entraînement
            training_images = [f for f in os.listdir(student_training_dir)
                              if f.endswith(('.jpg', '.jpeg', '.png'))]

            result["training_images"] = training_images
            result["num_training_images"] = len(training_images)
            result["is_trained"] = (student_id in self.known_face_encodings and
                                   len(self.known_face_encodings[student_id]) > 0)
        else:
            result["num_training_images"] = 0

        return result

    def delete_training_image(self, student_id: str, image_filename: str) -> bool:
        """
        Supprime une image d'entraînement.

        Args:
            student_id: ID de l'étudiant
            image_filename: Nom du fichier image à supprimer

        Returns:
            True si l'image a été supprimée, False sinon
        """
        student_training_dir = os.path.join(self.training_dir, student_id)
        image_path = os.path.join(student_training_dir, image_filename)

        if os.path.exists(image_path):
            os.remove(image_path)
            return True

        return False

    def delete_all_training_data(self, student_id: str) -> bool:
        """
        Supprime toutes les données d'entraînement pour un étudiant.

        Args:
            student_id: ID de l'étudiant

        Returns:
            True si les données ont été supprimées, False sinon
        """
        # Supprimer les encodages
        if student_id in self.known_face_encodings:
            del self.known_face_encodings[student_id]
            self.save_encodings()

        # Supprimer le répertoire d'entraînement
        student_training_dir = os.path.join(self.training_dir, student_id)

        if os.path.exists(student_training_dir):
            for file in os.listdir(student_training_dir):
                file_path = os.path.join(student_training_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)

            os.rmdir(student_training_dir)
            return True

        return False
