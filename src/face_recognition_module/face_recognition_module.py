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
            # Utiliser une approche simplifiée basée uniquement sur OpenCV de base
            print("Utilisation du mode de reconnaissance faciale simplifié (sans cv2.face)")
            self.simple_mode = True  # Mode simplifié sans cv2.face
            self.model_trained = False
            self.labels_file = os.path.join(data_dir, 'face_labels.json')

            # Ajouter les attributs nécessaires pour la compatibilité avec l'interface
            self.face_detection_model = "hog"  # Valeur par défaut
            self.recognition_tolerance = 0.6   # Valeur par défaut

            # Initialiser les structures pour le mode simplifié
            self.faces = []
            self.labels = np.array([])

            # Essayer de charger les données d'entraînement si elles existent
            try:
                self.faces = np.load(os.path.join(data_dir, 'faces.npy'), allow_pickle=True)
                self.labels = np.load(os.path.join(data_dir, 'labels.npy'))
                self.model_trained = True
                print(f"Modèle simplifié chargé avec {len(self.faces)} visages")
            except:
                print("Aucun modèle simplifié trouvé, un nouvel entraînement sera nécessaire")

            # Charger les correspondances ID -> étudiant si elles existent
            if os.path.exists(self.labels_file):
                try:
                    with open(self.labels_file, 'r') as f:
                        self.student_labels = json.load(f)
                except Exception as e:
                    print(f"Erreur lors du chargement des étiquettes : {e}")

            # Si les étiquettes n'ont pas été chargées précédemment
            if not hasattr(self, 'student_labels'):
                self.student_labels = {}

        # Paramètres communs
        self.min_training_images = 3       # Nombre minimum d'images pour l'entraînement

        # Paramètres de liveness detection
        self.liveness_enabled = True
        self.blink_detection_enabled = False  # Simplifié pour cette version
        self.movement_detection_enabled = False  # Simplifié pour cette version
        self.texture_analysis_enabled = True

        # S'assurer que tous les attributs nécessaires sont définis, même en mode simplifié
        if not hasattr(self, 'face_detection_model'):
            self.face_detection_model = "hog"
        if not hasattr(self, 'recognition_tolerance'):
            self.recognition_tolerance = 0.6

    def load_encodings(self) -> None:
        """Charge les encodages faciaux depuis le fichier."""
        if os.path.exists(self.encodings_file):
            try:
                with open(self.encodings_file, 'rb') as f:
                    self.known_face_encodings = pickle.load(f)
                print(f"Encodages chargés pour {len(self.known_face_encodings)} étudiants.")
            except Exception as e:
                print(f"Erreur lors du chargement des encodages : {e}")
                self.known_face_encodings = {}

    def save_encodings(self) -> None:
        """Sauvegarde les encodages faciaux dans un fichier."""
        try:
            with open(self.encodings_file, 'wb') as f:
                pickle.dump(self.known_face_encodings, f)
            print(f"Encodages sauvegardés pour {len(self.known_face_encodings)} étudiants.")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des encodages : {e}")

    def add_training_image(self, student_id: str, image) -> Tuple[bool, str]:
        """
        Ajoute une image d'entraînement pour un étudiant.

        Args:
            student_id: Identifiant de l'étudiant
            image: Image contenant le visage de l'étudiant

        Returns:
            Tuple (succès, message)
        """
        # Créer le répertoire d'entraînement pour l'étudiant s'il n'existe pas
        student_training_dir = os.path.join(self.training_dir, student_id)
        os.makedirs(student_training_dir, exist_ok=True)

        # Détecter les visages dans l'image
        if FACE_RECOGNITION_AVAILABLE:
            face_locations = face_recognition.face_locations(image, model=self.face_detection_model)
        else:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            face_locations = [(y, x + w, y + h, x) for (x, y, w, h) in faces]

        if not face_locations:
            return False, "Aucun visage détecté dans l'image."

        if len(face_locations) > 1:
            return False, "Plusieurs visages détectés. Veuillez fournir une image avec un seul visage."

        # Sauvegarder l'image d'entraînement
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"{student_id}_{timestamp}.jpg"
        image_path = os.path.join(student_training_dir, image_filename)

        cv2.imwrite(image_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

        # Si face_recognition est disponible, calculer et stocker l'encodage facial
        if FACE_RECOGNITION_AVAILABLE:
            face_encoding = face_recognition.face_encodings(image, face_locations)[0]

            if student_id not in self.known_face_encodings:
                self.known_face_encodings[student_id] = []

            self.known_face_encodings[student_id].append(face_encoding)
            self.save_encodings()

        return True, f"Image d'entraînement ajoutée pour l'étudiant {student_id}."

    def train_model(self) -> Tuple[bool, str]:
        """
        Entraîne le modèle de reconnaissance faciale avec les images disponibles.

        Returns:
            Tuple (succès, message)
        """
        if FACE_RECOGNITION_AVAILABLE:
            # Avec face_recognition, nous utilisons simplement les encodages stockés
            # Vérifier si nous avons suffisamment d'images pour chaque étudiant
            students_with_few_images = []
            for student_id, encodings in self.known_face_encodings.items():
                if len(encodings) < self.min_training_images:
                    students_with_few_images.append((student_id, len(encodings)))

            if students_with_few_images:
                message = "Entraînement terminé, mais certains étudiants ont peu d'images :\n"
                for student_id, count in students_with_few_images:
                    message += f"- Étudiant {student_id}: {count}/{self.min_training_images} images\n"
                return True, message

            return True, f"Modèle entraîné avec succès pour {len(self.known_face_encodings)} étudiants."
        else:
            # Avec OpenCV, nous devons entraîner un modèle LBPH
            faces = []
            labels = []
            label_ids = {}
            next_label_id = 0

            # Parcourir tous les répertoires d'étudiants
            for student_id in os.listdir(self.training_dir):
                student_dir = os.path.join(self.training_dir, student_id)
                if not os.path.isdir(student_dir):
                    continue

                # Attribuer un ID numérique à l'étudiant
                if student_id not in label_ids:
                    label_ids[student_id] = next_label_id
                    next_label_id += 1

                # Charger toutes les images d'entraînement
                image_count = 0
                for image_file in os.listdir(student_dir):
                    if not image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        continue

                    image_path = os.path.join(student_dir, image_file)
                    image = cv2.imread(image_path)
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                    try:
                        # Détecter les visages
                        face_rects = self.face_cascade.detectMultiScale(gray, 1.3, 5)

                        for (x, y, w, h) in face_rects:
                            # S'assurer que les coordonnées sont valides
                            if x >= 0 and y >= 0 and x+w <= gray.shape[1] and y+h <= gray.shape[0]:
                                # Redimensionner tous les visages à une taille standard
                                face_roi = gray[y:y+h, x:x+w]
                                face_roi = cv2.resize(face_roi, (100, 100))

                                faces.append(face_roi)
                                labels.append(label_ids[student_id])
                                image_count += 1
                    except Exception as e:
                        print(f"Erreur lors du traitement de l'image {image_file}: {e}")
                        continue

                if image_count < self.min_training_images:
                    print(f"Attention: L'étudiant {student_id} n'a que {image_count} images (minimum recommandé: {self.min_training_images})")

            if not faces:
                return False, "Aucune image d'entraînement trouvée."

            # Mode simplifié : stocker les visages et étiquettes pour la reconnaissance
            self.faces = faces
            self.labels = np.array(labels)

            # Sauvegarder les données d'entraînement
            np.save(os.path.join(self.data_dir, 'faces.npy'), np.array(faces))
            np.save(os.path.join(self.data_dir, 'labels.npy'), np.array(labels))

            # Sauvegarder les correspondances ID -> étudiant
            self.student_labels = {str(label_id): student_id for student_id, label_id in label_ids.items()}
            with open(self.labels_file, 'w') as f:
                json.dump(self.student_labels, f)

            self.model_trained = True
            return True, f"Modèle entraîné avec succès pour {len(label_ids)} étudiants."

    def get_student_training_info(self, student_id: str) -> Dict:
        """
        Récupère les informations d'entraînement pour un étudiant.

        Args:
            student_id: Identifiant de l'étudiant

        Returns:
            Dictionnaire contenant les informations d'entraînement
        """
        # Récupérer les images d'entraînement
        training_images = []
        student_training_dir = os.path.join(self.training_dir, student_id)
        if os.path.exists(student_training_dir):
            for image_file in os.listdir(student_training_dir):
                if image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    training_images.append(image_file)

        # Vérifier si l'étudiant a des encodages
        num_encodings = 0
        if FACE_RECOGNITION_AVAILABLE and student_id in self.known_face_encodings:
            num_encodings = len(self.known_face_encodings[student_id])

        # Déterminer si l'étudiant est entraîné
        is_trained = False
        if FACE_RECOGNITION_AVAILABLE:
            is_trained = num_encodings >= self.min_training_images
        else:
            # Avec OpenCV, vérifier si le modèle est entraîné
            is_trained = self.model_trained and len(training_images) >= self.min_training_images

        return {
            "training_images": training_images,
            "num_training_images": len(training_images),
            "num_encodings": num_encodings,
            "is_trained": is_trained
        }

    def get_training_images(self, student_id: str) -> List[Dict]:
        """
        Récupère les images d'entraînement pour un étudiant.

        Args:
            student_id: Identifiant de l'étudiant

        Returns:
            Liste des chemins d'images d'entraînement
        """
        student_training_dir = os.path.join(self.training_dir, student_id)
        if not os.path.exists(student_training_dir):
            return []

        images = []
        for image_file in os.listdir(student_training_dir):
            if not image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue

            image_path = os.path.join(student_training_dir, image_file)
            timestamp = os.path.getmtime(image_path)
            date_added = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

            images.append({
                "path": image_path,
                "filename": image_file,
                "date_added": date_added
            })

        # Trier par date d'ajout (plus récent en premier)
        images.sort(key=lambda x: x["date_added"], reverse=True)
        return images

    def delete_training_image(self, student_id: str, image_filename: str) -> Tuple[bool, str]:
        """
        Supprime une image d'entraînement.

        Args:
            student_id: Identifiant de l'étudiant
            image_filename: Nom du fichier image à supprimer

        Returns:
            Tuple (succès, message)
        """
        student_training_dir = os.path.join(self.training_dir, student_id)
        image_path = os.path.join(student_training_dir, image_filename)

        if not os.path.exists(image_path):
            return False, f"L'image {image_filename} n'existe pas."

        try:
            os.remove(image_path)

            # Si face_recognition est disponible, recalculer les encodages
            if FACE_RECOGNITION_AVAILABLE and student_id in self.known_face_encodings:
                # Recalculer tous les encodages pour cet étudiant
                self.known_face_encodings[student_id] = []

                for image_info in self.get_training_images(student_id):
                    image = cv2.imread(image_info["path"])
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                    face_locations = face_recognition.face_locations(image, model=self.face_detection_model)
                    if face_locations:
                        face_encoding = face_recognition.face_encodings(image, face_locations)[0]
                        self.known_face_encodings[student_id].append(face_encoding)

                if not self.known_face_encodings[student_id]:
                    del self.known_face_encodings[student_id]

                self.save_encodings()

            return True, f"Image {image_filename} supprimée."
        except Exception as e:
            return False, f"Erreur lors de la suppression de l'image : {e}"

    def delete_all_training_data(self, student_id: str) -> Tuple[bool, str]:
        """
        Supprime toutes les données d'entraînement pour un étudiant.

        Args:
            student_id: Identifiant de l'étudiant

        Returns:
            Tuple (succès, message)
        """
        student_training_dir = os.path.join(self.training_dir, student_id)

        if not os.path.exists(student_training_dir):
            return False, f"Aucune donnée d'entraînement pour l'étudiant {student_id}."

        try:
            # Supprimer toutes les images
            for image_file in os.listdir(student_training_dir):
                image_path = os.path.join(student_training_dir, image_file)
                if os.path.isfile(image_path):
                    os.remove(image_path)

            # Supprimer le répertoire
            os.rmdir(student_training_dir)

            # Supprimer les encodages si face_recognition est disponible
            if FACE_RECOGNITION_AVAILABLE and student_id in self.known_face_encodings:
                del self.known_face_encodings[student_id]
                self.save_encodings()

            return True, f"Toutes les données d'entraînement pour l'étudiant {student_id} ont été supprimées."
        except Exception as e:
            return False, f"Erreur lors de la suppression des données : {e}"

    def capture_training_images(self, student_id: str, num_images: int = 5) -> Tuple[bool, str, int]:
        """
        Capture plusieurs images d'entraînement à partir de la webcam.

        Args:
            student_id: Identifiant de l'étudiant
            num_images: Nombre d'images à capturer

        Returns:
            Tuple (succès, message, nombre d'images capturées)
        """
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return False, "Impossible d'accéder à la webcam.", 0

            images_captured = 0
            last_capture_time = 0
            capture_interval = 1.0  # Intervalle en secondes entre les captures

            while images_captured < num_images:
                ret, frame = cap.read()
                if not ret:
                    break

                # Convertir en RGB pour face_recognition
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Détecter les visages
                if FACE_RECOGNITION_AVAILABLE:
                    face_locations = face_recognition.face_locations(rgb_frame, model=self.face_detection_model)
                else:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                    face_locations = [(y, x + w, y + h, x) for (x, y, w, h) in faces]

                current_time = time.time()
                if face_locations and current_time - last_capture_time >= capture_interval:
                    if len(face_locations) > 1:
                        continue

                    # Ajouter l'image d'entraînement
                    success, message = self.add_training_image(student_id, rgb_frame)

                    if success:
                        images_captured += 1
                        last_capture_time = current_time

            cap.release()

            if images_captured == 0:
                return False, "Aucun visage détecté pendant la capture.", 0

            return True, f"{images_captured} images capturées avec succès.", images_captured
        except Exception as e:
            return False, f"Erreur lors de la capture des images : {e}", 0

    def detect_faces(self, image) -> Dict:
        """
        Détecte les visages dans une image.

        Args:
            image: Image à analyser

        Returns:
            Dictionnaire avec les résultats de détection
        """
        if FACE_RECOGNITION_AVAILABLE:
            # Utiliser face_recognition pour la détection
            face_locations = face_recognition.face_locations(image, model=self.face_detection_model)

            faces = []
            for face_location in face_locations:
                top, right, bottom, left = face_location
                faces.append({
                    "location": (left, top, right, bottom),
                    "is_live": self.check_liveness(image, face_location)
                })

            return {
                "faces_detected": len(faces),
                "faces": faces
            }
        else:
            # Utiliser OpenCV pour la détection
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            face_rects = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            faces = []
            for (x, y, w, h) in face_rects:
                face_location = (y, x + w, y + h, x)  # Convertir au format (top, right, bottom, left)
                faces.append({
                    "location": (x, y, x + w, y + h),
                    "is_live": self.check_liveness(image, face_location)
                })

            return {
                "faces_detected": len(faces),
                "faces": faces
            }

    def train_student(self, student_id: str) -> Tuple[bool, str]:
        """
        Entraîne le modèle pour un étudiant spécifique.

        Args:
            student_id: Identifiant de l'étudiant

        Returns:
            Tuple (succès, message)
        """
        # Vérifier si l'étudiant a suffisamment d'images d'entraînement
        training_info = self.get_student_training_info(student_id)

        if training_info["num_training_images"] < self.min_training_images:
            return False, f"Pas assez d'images d'entraînement. Minimum requis : {self.min_training_images}"

        if FACE_RECOGNITION_AVAILABLE:
            # Avec face_recognition, recalculer tous les encodages
            student_training_dir = os.path.join(self.training_dir, student_id)

            if not os.path.exists(student_training_dir):
                return False, f"Aucune image d'entraînement trouvée pour l'étudiant {student_id}"

            # Réinitialiser les encodages pour cet étudiant
            self.known_face_encodings[student_id] = []

            # Parcourir toutes les images d'entraînement
            for image_file in os.listdir(student_training_dir):
                if not image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    continue

                image_path = os.path.join(student_training_dir, image_file)
                image = cv2.imread(image_path)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                # Détecter les visages
                face_locations = face_recognition.face_locations(image, model=self.face_detection_model)

                if face_locations:
                    # Calculer l'encodage facial
                    face_encoding = face_recognition.face_encodings(image, face_locations)[0]
                    self.known_face_encodings[student_id].append(face_encoding)

            # Sauvegarder les encodages
            self.save_encodings()

            return True, f"Modèle entraîné avec succès pour l'étudiant {student_id} avec {len(self.known_face_encodings[student_id])} encodages."
        else:
            # Avec OpenCV, nous devons réentraîner tout le modèle
            return self.train_model()

    def recognize_batch(self, image) -> Dict:
        """
        Reconnaît les visages dans une image et renvoie des résultats détaillés.

        Args:
            image: Image à analyser

        Returns:
            Dictionnaire avec les résultats de reconnaissance
        """
        start_time = time.time()

        # Reconnaître les visages
        recognition_results = self.recognize_faces(image)

        # Formater les résultats
        results = {
            "faces_detected": recognition_results["faces_detected"],
            "processing_time": time.time() - start_time,
            "results": []
        }

        # Traiter chaque visage
        for face in recognition_results["faces"]:
            face_result = {
                "location": face["location"],
                "is_live": face.get("is_live", True),
                "matches": face.get("matches", [])
            }

            results["results"].append(face_result)

        return results

    def recognize_faces(self, image) -> Dict:
        """
        Reconnaît les visages dans une image.

        Args:
            image: Image à analyser

        Returns:
            Dictionnaire avec les résultats de reconnaissance
        """
        # Détecter les visages
        detection_results = self.detect_faces(image)

        if detection_results["faces_detected"] == 0:
            return detection_results

        # Reconnaître chaque visage
        if FACE_RECOGNITION_AVAILABLE:
            # Utiliser face_recognition pour la reconnaissance
            face_locations = [face["location"] for face in detection_results["faces"]]
            face_encodings = face_recognition.face_encodings(image, face_locations)

            for i, face_encoding in enumerate(face_encodings):
                matches = []

                for student_id, encodings in self.known_face_encodings.items():
                    # Comparer avec tous les encodages de l'étudiant
                    match_scores = face_recognition.face_distance(encodings, face_encoding)
                    best_match_score = min(match_scores) if match_scores.size > 0 else 1.0

                    if best_match_score <= self.recognition_tolerance:
                        confidence = 1.0 - best_match_score
                        matches.append({
                            "student_id": student_id,
                            "confidence": confidence
                        })

                # Trier par confiance (décroissant)
                matches.sort(key=lambda x: x["confidence"], reverse=True)
                detection_results["faces"][i]["matches"] = matches
        else:
            # Utiliser OpenCV pour la reconnaissance
            if not self.model_trained:
                for i in range(detection_results["faces_detected"]):
                    detection_results["faces"][i]["matches"] = []
                return detection_results

            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

            for i, face in enumerate(detection_results["faces"]):
                x, y, w, h = face["location"]
                face_roi = gray[y:y+h, x:x+w]

                # Redimensionner si nécessaire
                face_roi = cv2.resize(face_roi, (100, 100))

                # Mode simplifié : utiliser une comparaison basée sur la distance euclidienne
                if not hasattr(self, 'faces') or not hasattr(self, 'labels'):
                    # Essayer de charger les données d'entraînement
                    try:
                        self.faces = np.load(os.path.join(self.data_dir, 'faces.npy'), allow_pickle=True)
                        self.labels = np.load(os.path.join(self.data_dir, 'labels.npy'))
                    except:
                        # Pas de données d'entraînement disponibles
                        label_id, confidence = -1, 100
                        continue

                # Redimensionner pour correspondre aux visages d'entraînement
                if len(self.faces) > 0:
                    try:
                        target_shape = self.faces[0].shape[:2]
                        face_roi = cv2.resize(face_roi, target_shape)
                    except Exception as e:
                        print(f"Erreur lors du redimensionnement: {e}")
                        # Utiliser une taille par défaut si le redimensionnement échoue
                        face_roi = cv2.resize(face_roi, (100, 100))

                # Calculer les distances avec tous les visages d'entraînement
                min_dist = float('inf')
                label_id = -1

                for i, train_face in enumerate(self.faces):
                    try:
                        # S'assurer que les dimensions correspondent
                        if train_face.shape != face_roi.shape:
                            train_face_resized = cv2.resize(train_face, face_roi.shape[:2])
                        else:
                            train_face_resized = train_face

                        # Calculer la distance euclidienne
                        dist = np.sqrt(np.sum((train_face_resized.astype("float") - face_roi.astype("float")) ** 2))

                        if dist < min_dist:
                            min_dist = dist
                            label_id = self.labels[i]
                    except Exception as e:
                        print(f"Erreur lors de la comparaison avec le visage {i}: {e}")
                        continue

                # Convertir la distance en confiance (plus petite distance = meilleure confiance)
                confidence = min(100, max(0, min_dist / 100))

                # Convertir la confiance (plus petite = meilleure dans OpenCV)
                # à un format où plus grand = meilleur
                normalized_confidence = max(0, min(100, 100 - confidence)) / 100.0

                matches = []
                if normalized_confidence >= 0.5:  # Seuil de confiance
                    student_id = self.student_labels.get(str(label_id))
                    if student_id:
                        matches.append({
                            "student_id": student_id,
                            "confidence": normalized_confidence
                        })

                detection_results["faces"][i]["matches"] = matches

        return detection_results

    def check_liveness(self, image, face_location) -> bool:
        """
        Vérifie si un visage détecté est "vivant" (anti-spoofing).

        Args:
            image: Image contenant le visage
            face_location: Localisation du visage (top, right, bottom, left)

        Returns:
            True si le visage est considéré comme vivant, False sinon
        """
        if not self.liveness_enabled:
            return True

        # Extraction du visage
        if len(face_location) == 4:
            top, right, bottom, left = face_location
            face_image = image[top:bottom, left:right]
        else:
            x, y, w, h = face_location
            face_image = image[y:y+h, x:x+w]

        # Analyse de texture (détection d'impression/écran)
        if self.texture_analysis_enabled:
            # Convertir en niveaux de gris
            gray = cv2.cvtColor(face_image, cv2.COLOR_RGB2GRAY)

            # Appliquer un filtre de détection de bords
            edges = cv2.Canny(gray, 100, 200)

            # Calculer le pourcentage de pixels de bord
            edge_density = np.count_nonzero(edges) / (edges.shape[0] * edges.shape[1])

            # Si la densité de bords est trop faible ou trop élevée, c'est suspect
            if edge_density < 0.05 or edge_density > 0.3:
                return False

        # Détection de clignement (simplifié)
        if self.blink_detection_enabled and FACE_RECOGNITION_AVAILABLE:
            # Cette implémentation est simplifiée et ne fonctionne pas réellement
            # Une vraie implémentation nécessiterait plusieurs images ou une vidéo
            pass

        # Détection de mouvement (simplifié)
        if self.movement_detection_enabled:
            # Cette implémentation est simplifiée et ne fonctionne pas réellement
            # Une vraie implémentation nécessiterait plusieurs images ou une vidéo
            pass

        # Par défaut, considérer comme vivant
        return True

    def get_settings(self) -> Dict:
        """
        Récupère les paramètres actuels du module.

        Returns:
            Dictionnaire des paramètres
        """
        settings = {
            "face_detection_available": True,
            "face_recognition_available": FACE_RECOGNITION_AVAILABLE,
            "liveness_detection_enabled": self.liveness_enabled,
            "min_training_images": self.min_training_images
        }

        if FACE_RECOGNITION_AVAILABLE:
            settings.update({
                "face_detection_model": self.face_detection_model,
                "recognition_tolerance": self.recognition_tolerance
            })

        return settings

    def update_settings(self, settings: Dict) -> Tuple[bool, str]:
        """
        Met à jour les paramètres du module.

        Args:
            settings: Dictionnaire des nouveaux paramètres

        Returns:
            Tuple (succès, message)
        """
        try:
            if "liveness_detection_enabled" in settings:
                self.liveness_enabled = bool(settings["liveness_detection_enabled"])

            if "min_training_images" in settings:
                self.min_training_images = int(settings["min_training_images"])

            if FACE_RECOGNITION_AVAILABLE:
                if "face_detection_model" in settings:
                    model = settings["face_detection_model"]
                    if model in ["hog", "cnn"]:
                        self.face_detection_model = model

                if "recognition_tolerance" in settings:
                    tolerance = float(settings["recognition_tolerance"])
                    if 0.0 <= tolerance <= 1.0:
                        self.recognition_tolerance = tolerance

            return True, "Paramètres mis à jour avec succès."
        except Exception as e:
            return False, f"Erreur lors de la mise à jour des paramètres : {e}"
