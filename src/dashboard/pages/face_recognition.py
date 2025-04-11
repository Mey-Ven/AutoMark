import streamlit as st
import os
import pandas as pd
from datetime import datetime
import time
import base64
from io import BytesIO
import sys

# Vérifier si OpenCV est installé
def check_opencv():
    try:
        import cv2
        import numpy as np
        from PIL import Image
        print("OpenCV importé avec succès, version:", cv2.__version__)
        return True
    except ImportError as e:
        print("Erreur d'importation OpenCV:", str(e))
        return False

def render_face_recognition_page(data_loader):
    st.title("Reconnaissance Faciale Avancée")

    # Vérifier si OpenCV est disponible
    opencv_available = check_opencv()
    if not opencv_available:
        st.error("La bibliothèque OpenCV n'est pas installée. Cette fonctionnalité nécessite OpenCV pour fonctionner.")
        st.info("Pour installer OpenCV, exécutez la commande suivante dans votre terminal : `pip install opencv-python`")
        st.info("Après l'installation, redémarrez l'application pour accéder à cette fonctionnalité.")

        # Informations de débogage
        st.code(f"Python version: {sys.version}")
        st.code(f"Python path: {sys.executable}")
        st.code(f"Modules installés: {', '.join([k for k in sys.modules.keys() if not k.startswith('_')][:50])}")
        return

    try:
        # Importer le module de reconnaissance faciale
        from src.face_recognition_module import FaceRecognitionModule

        # Afficher un avertissement si face_recognition n'est pas disponible
        try:
            import face_recognition
            has_face_recognition = True
        except ImportError:
            has_face_recognition = False
            st.info("La bibliothèque face_recognition n'est pas installée. Le système utilise une alternative basée sur OpenCV.")
            st.info("Pour une meilleure précision, vous pouvez installer face_recognition : `pip install face_recognition`")

        try:
            # Initialiser le module de reconnaissance faciale
            face_module = FaceRecognitionModule(data_loader.data_dir)

            # Créer des onglets pour les différentes fonctionnalités
            tabs = st.tabs(["Entraînement", "Reconnaissance", "Paramètres"])

            # Onglet Entraînement
            with tabs[0]:
                render_training_tab(face_module, data_loader)

            # Onglet Reconnaissance
            with tabs[1]:
                render_recognition_tab(face_module, data_loader)

            # Onglet Paramètres
            with tabs[2]:
                render_settings_tab(face_module)
        except Exception as e:
            st.error(f"Erreur lors de l'initialisation du module de reconnaissance faciale : {str(e)}")
            st.info("Vérifiez que toutes les dépendances sont installées correctement.")
            import traceback
            st.code(traceback.format_exc())
    except ImportError as e:
        st.error(f"Le module de reconnaissance faciale n'a pas pu être chargé : {str(e)}")
        st.info("Assurez-vous que toutes les dépendances sont installées correctement.")
        st.code("pip install opencv-python numpy pillow")
        import traceback
        st.code(traceback.format_exc())

def render_training_tab(face_module, data_loader):
    st.header("Entraînement du modèle")

    # Importer les dépendances nécessaires
    import cv2
    import numpy as np
    from PIL import Image

    # Charger les données des étudiants
    students_file = os.path.join(data_loader.data_dir, 'students.json')
    if os.path.exists(students_file):
        with open(students_file, 'r') as f:
            import json
            students = json.load(f)
    else:
        students = []

    if not students:
        st.warning("Aucun étudiant n'est enregistré. Veuillez d'abord ajouter des étudiants dans la section Administration.")
        return

    # Sélectionner un étudiant pour l'entraînement
    student_options = [f"{s['first_name']} {s['last_name']} (ID: {s['id']})" for s in students]
    selected_student = st.selectbox("Sélectionner un étudiant", student_options)

    # Extraire l'ID de l'étudiant sélectionné
    student_id = selected_student.split("(ID: ")[1].split(")")[0]
    selected_student_obj = next((s for s in students if s['id'] == student_id), None)

    if selected_student_obj:
        st.subheader(f"Entraînement pour {selected_student_obj['first_name']} {selected_student_obj['last_name']}")

        # Afficher les informations d'entraînement actuelles
        training_info = face_module.get_student_training_info(student_id)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Images d'entraînement", training_info.get("num_training_images", 0))
        with col2:
            st.metric("Encodages", training_info.get("num_encodings", 0))
        with col3:
            st.metric("Statut", "Entraîné" if training_info.get("is_trained", False) else "Non entraîné")

        # Afficher les images d'entraînement existantes
        if training_info.get("training_images", []):
            st.subheader("Images d'entraînement existantes")

            # Organiser les images en grille
            cols = st.columns(3)
            for i, img_file in enumerate(training_info["training_images"]):
                img_path = os.path.join(face_module.training_dir, student_id, img_file)

                if os.path.exists(img_path):
                    with cols[i % 3]:
                        st.image(img_path, caption=f"Image {i+1}", width=150)
                        if st.button(f"Supprimer", key=f"del_{img_file}"):
                            if face_module.delete_training_image(student_id, img_file):
                                st.success(f"Image supprimée")
                                st.experimental_rerun()
                            else:
                                st.error("Erreur lors de la suppression de l'image")

        # Options pour ajouter de nouvelles images d'entraînement
        st.subheader("Ajouter de nouvelles images d'entraînement")

        add_method = st.radio("Méthode d'ajout", ["Télécharger des images", "Utiliser la webcam"])

        if add_method == "Télécharger des images":
            uploaded_files = st.file_uploader("Télécharger des images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

            if uploaded_files:
                for uploaded_file in uploaded_files:
                    # Convertir le fichier en image
                    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
                    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                    # Ajouter l'image d'entraînement
                    success, message = face_module.add_training_image(student_id, image)

                    if success:
                        st.success(message)
                    else:
                        st.error(message)

                # Recharger la page pour afficher les nouvelles images
                if st.button("Actualiser"):
                    st.experimental_rerun()

        elif add_method == "Utiliser la webcam":
            st.warning("Note: L'accès à la webcam nécessite d'autoriser l'accès à la caméra dans votre navigateur.")

            if st.button("Capturer des images avec la webcam"):
                # Cette fonctionnalité nécessite une interaction JavaScript qui n'est pas directement
                # disponible dans Streamlit. Dans une application réelle, vous pourriez utiliser
                # streamlit-webrtc ou une autre solution pour accéder à la webcam.
                st.info("Fonctionnalité de capture par webcam en cours de développement...")
                st.info("Pour l'instant, veuillez télécharger des images manuellement.")

        # Bouton pour entraîner le modèle
        st.subheader("Entraîner le modèle")

        min_images = face_module.min_training_images
        if training_info.get("num_training_images", 0) < min_images:
            st.warning(f"Vous avez besoin d'au moins {min_images} images pour entraîner le modèle.")

        if st.button("Entraîner le modèle avec les images existantes"):
            if training_info.get("num_training_images", 0) >= min_images:
                with st.spinner("Entraînement en cours..."):
                    success, message = face_module.train_student(student_id)

                if success:
                    st.success(message)
                    st.experimental_rerun()
                else:
                    st.error(message)
            else:
                st.error(f"Pas assez d'images d'entraînement. Minimum requis : {min_images}")

        # Option pour supprimer toutes les données d'entraînement
        st.subheader("Supprimer les données d'entraînement")

        if st.button("Supprimer toutes les données d'entraînement", type="primary", help="Cette action est irréversible"):
            confirm = st.checkbox("Je confirme vouloir supprimer toutes les données d'entraînement pour cet étudiant")

            if confirm:
                if face_module.delete_all_training_data(student_id):
                    st.success("Toutes les données d'entraînement ont été supprimées")
                    st.experimental_rerun()
                else:
                    st.error("Erreur lors de la suppression des données d'entraînement")

def render_recognition_tab(face_module, data_loader):
    st.header("Reconnaissance faciale")

    # Importer les dépendances nécessaires
    import cv2
    import numpy as np
    from PIL import Image

    # Charger les données des étudiants
    students_file = os.path.join(data_loader.data_dir, 'students.json')
    if os.path.exists(students_file):
        with open(students_file, 'r') as f:
            import json
            students = json.load(f)
    else:
        students = []

    # Charger les données des cours
    courses_file = os.path.join(data_loader.data_dir, 'courses.json')
    if os.path.exists(courses_file):
        with open(courses_file, 'r') as f:
            import json
            courses = json.load(f)
    else:
        courses = []

    # Options de reconnaissance
    st.subheader("Options de reconnaissance")

    recognition_method = st.radio("Méthode de reconnaissance", ["Télécharger une image", "Utiliser la webcam"])

    # Sélection du cours pour l'enregistrement de présence
    if courses:
        selected_course = st.selectbox(
            "Cours (pour l'enregistrement de présence)",
            options=[c["name"] for c in courses]
        )
        course_id = next(c["id"] for c in courses if c["name"] == selected_course)
    else:
        st.warning("Aucun cours disponible. Veuillez d'abord ajouter des cours dans la section Administration.")
        course_id = None

    # Date de présence
    attendance_date = st.date_input("Date de présence", datetime.now())

    if recognition_method == "Télécharger une image":
        uploaded_file = st.file_uploader("Télécharger une image", type=["jpg", "jpeg", "png"])

        if uploaded_file:
            # Convertir le fichier en image
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Afficher l'image
            st.image(image, caption="Image téléchargée", use_column_width=True)

            # Bouton pour lancer la reconnaissance
            if st.button("Lancer la reconnaissance"):
                with st.spinner("Reconnaissance en cours..."):
                    # Reconnaître les visages
                    results = face_module.recognize_batch(image)

                # Afficher les résultats
                display_recognition_results(results, students, face_module, image, data_loader, course_id, attendance_date)

    elif recognition_method == "Utiliser la webcam":
        st.warning("Note: L'accès à la webcam nécessite d'autoriser l'accès à la caméra dans votre navigateur.")
        st.info("Fonctionnalité de capture par webcam en cours de développement...")
        st.info("Pour l'instant, veuillez télécharger des images manuellement.")

def display_recognition_results(results, students, face_module, image, data_loader, course_id, attendance_date):
    st.subheader("Résultats de la reconnaissance")

    # Importer les dépendances nécessaires
    import cv2
    import numpy as np

    if results["faces_detected"] == 0:
        st.warning("Aucun visage détecté dans l'image")
        return

    st.write(f"Nombre de visages détectés : {results['faces_detected']}")
    st.write(f"Temps de traitement : {results['processing_time']:.2f} secondes")

    # Créer une copie de l'image pour y dessiner les résultats
    result_image = image.copy()

    # Pour chaque visage détecté
    recognized_students = []

    for face_result in results["results"]:
        face_location = face_result["location"]
        top, right, bottom, left = face_location

        # Dessiner un rectangle autour du visage
        color = (0, 255, 0) if face_result["is_live"] else (255, 0, 0)  # Vert si vivant, rouge sinon
        cv2.rectangle(result_image, (left, top), (right, bottom), color, 2)

        # Afficher les informations sur le visage
        if face_result["matches"]:
            best_match = face_result["matches"][0]
            student_id = best_match["student_id"]
            confidence = best_match["confidence"]

            # Trouver les informations de l'étudiant
            student = next((s for s in students if s["id"] == student_id), None)

            if student:
                student_name = f"{student['first_name']} {student['last_name']}"

                # Ajouter le nom au-dessus du rectangle
                cv2.putText(result_image, student_name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                # Ajouter à la liste des étudiants reconnus
                recognized_students.append({
                    "student_id": student_id,
                    "name": student_name,
                    "confidence": confidence,
                    "is_live": face_result["is_live"]
                })
        else:
            # Aucune correspondance trouvée
            cv2.putText(result_image, "Inconnu", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # Afficher l'image avec les résultats
    st.image(result_image, caption="Résultats de la reconnaissance", use_column_width=True)

    # Afficher la liste des étudiants reconnus
    if recognized_students:
        st.subheader("Étudiants reconnus")

        recognition_df = pd.DataFrame(recognized_students)
        recognition_df["confidence"] = recognition_df["confidence"].apply(lambda x: f"{x:.2%}")
        recognition_df["is_live"] = recognition_df["is_live"].apply(lambda x: "Oui" if x else "Non (possible photo)")
        recognition_df.columns = ["ID", "Nom", "Confiance", "Personne réelle"]

        st.dataframe(recognition_df)

        # Option pour enregistrer les présences
        if course_id:
            st.subheader("Enregistrer les présences")

            # Créer des cases à cocher pour chaque étudiant reconnu
            attendance_records = {}

            for student in recognized_students:
                # Ne proposer que les étudiants détectés comme réels (pas des photos)
                if student["is_live"]:
                    attendance_records[student["student_id"]] = st.checkbox(
                        f"Marquer {student['name']} comme présent",
                        value=True,
                        key=f"attendance_{student['student_id']}"
                    )

            if st.button("Enregistrer les présences"):
                # Charger les données de présence existantes
                attendance_file = os.path.join(data_loader.data_dir, 'attendance.json')
                if os.path.exists(attendance_file):
                    with open(attendance_file, 'r') as f:
                        import json
                        attendance_records_data = json.load(f)
                else:
                    attendance_records_data = []

                # Formater la date
                attendance_date_str = attendance_date.strftime("%Y-%m-%d")

                # Compter les enregistrements ajoutés
                added_count = 0

                # Pour chaque étudiant reconnu
                for student_id, is_present in attendance_records.items():
                    # Vérifier si un enregistrement existe déjà pour cet étudiant, ce cours et cette date
                    existing_record = next(
                        (r for r in attendance_records_data
                         if r["student_id"] == student_id
                         and r["course_id"] == course_id
                         and r["date"] == attendance_date_str),
                        None
                    )

                    if existing_record:
                        # Mettre à jour l'enregistrement existant
                        existing_record["present"] = is_present
                        existing_record["method"] = "Reconnaissance faciale"
                        existing_record["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        # Créer un nouvel enregistrement
                        import uuid
                        new_record = {
                            "id": str(uuid.uuid4())[:8],
                            "course_id": course_id,
                            "student_id": student_id,
                            "date": attendance_date_str,
                            "present": is_present,
                            "method": "Reconnaissance faciale",
                            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        attendance_records_data.append(new_record)
                        added_count += 1

                # Sauvegarder les données
                with open(attendance_file, 'w') as f:
                    import json
                    json.dump(attendance_records_data, f, indent=4)

                st.success(f"Présences enregistrées avec succès ! {added_count} nouveaux enregistrements.")

def render_settings_tab(face_module):
    st.header("Paramètres de reconnaissance faciale")

    # Paramètres généraux
    st.subheader("Paramètres généraux")

    # Modèle de détection
    detection_model = st.selectbox(
        "Modèle de détection de visage",
        options=["hog", "cnn"],
        index=0 if face_module.face_detection_model == "hog" else 1,
        help="HOG est plus rapide mais moins précis. CNN est plus précis mais nécessite plus de ressources."
    )

    # Tolérance de reconnaissance
    recognition_tolerance = st.slider(
        "Tolérance de reconnaissance",
        min_value=0.0,
        max_value=1.0,
        value=face_module.recognition_tolerance,
        step=0.05,
        help="Plus la valeur est basse, plus la reconnaissance est stricte. Valeur recommandée : 0.6"
    )

    # Nombre minimum d'images d'entraînement
    min_training_images = st.number_input(
        "Nombre minimum d'images d'entraînement",
        min_value=1,
        max_value=10,
        value=face_module.min_training_images,
        help="Nombre minimum d'images nécessaires pour entraîner le modèle pour un étudiant."
    )

    # Paramètres de détection de liveness
    st.subheader("Détection de liveness (anti-spoofing)")

    liveness_enabled = st.checkbox(
        "Activer la détection de liveness",
        value=face_module.liveness_enabled,
        help="Détecte si le visage appartient à une personne réelle ou à une photo/vidéo."
    )

    if liveness_enabled:
        blink_detection = st.checkbox(
            "Détection de clignement des yeux",
            value=face_module.blink_detection_enabled,
            help="Détecte le clignement des yeux pour confirmer qu'il s'agit d'une personne réelle."
        )

        movement_detection = st.checkbox(
            "Détection de mouvements",
            value=face_module.movement_detection_enabled,
            help="Détecte les mouvements du visage pour confirmer qu'il s'agit d'une personne réelle."
        )

        texture_analysis = st.checkbox(
            "Analyse de texture",
            value=face_module.texture_analysis_enabled,
            help="Analyse la texture de l'image pour détecter s'il s'agit d'une photo imprimée."
        )

    # Bouton pour appliquer les paramètres
    if st.button("Appliquer les paramètres"):
        # Mettre à jour les paramètres
        face_module.face_detection_model = detection_model
        face_module.recognition_tolerance = recognition_tolerance
        face_module.min_training_images = min_training_images
        face_module.liveness_enabled = liveness_enabled

        if liveness_enabled:
            face_module.blink_detection_enabled = blink_detection
            face_module.movement_detection_enabled = movement_detection
            face_module.texture_analysis_enabled = texture_analysis

        st.success("Paramètres appliqués avec succès !")

        # Note: Dans une implémentation réelle, vous voudriez sauvegarder ces paramètres
        # dans un fichier de configuration pour les conserver entre les sessions.
