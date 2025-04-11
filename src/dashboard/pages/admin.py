import streamlit as st
import pandas as pd
import os
import json
import uuid
from datetime import datetime, timedelta

def render_admin_page(data_loader):
    st.title("Administration")

    # Créer des onglets pour les différentes sections d'administration
    tabs = st.tabs(["Cours", "Étudiants", "Présences"])

    # Onglet Cours
    with tabs[0]:
        manage_courses(data_loader)

    # Onglet Étudiants
    with tabs[1]:
        manage_students(data_loader)

    # Onglet Présences
    with tabs[2]:
        manage_attendance(data_loader)

def manage_courses(data_loader):
    st.header("Gestion des Cours")

    # Charger les données des cours
    courses_file = os.path.join(data_loader.data_dir, 'courses.json')
    if os.path.exists(courses_file):
        with open(courses_file, 'r') as f:
            courses = json.load(f)
    else:
        courses = []

    # Afficher les cours existants
    if courses:
        st.subheader("Cours existants")
        courses_df = pd.DataFrame(courses)
        st.dataframe(courses_df)

    # Formulaire pour ajouter un nouveau cours
    with st.expander("Ajouter un nouveau cours", expanded=False):
        with st.form("add_course_form"):
            course_id = str(uuid.uuid4())[:8]  # Générer un ID unique
            course_name = st.text_input("Nom du cours")
            course_code = st.text_input("Code du cours")
            course_schedule = st.text_input("Horaire (ex: Lundi 10h-12h)")
            course_description = st.text_area("Description")

            submitted = st.form_submit_button("Ajouter")
            if submitted and course_name and course_code:
                new_course = {
                    "id": course_id,
                    "name": course_name,
                    "code": course_code,
                    "schedule": course_schedule,
                    "description": course_description,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                courses.append(new_course)

                # Sauvegarder les données
                with open(courses_file, 'w') as f:
                    json.dump(courses, f, indent=4)

                st.success(f"Cours '{course_name}' ajouté avec succès!")
                st.experimental_rerun()

    # Formulaire pour modifier un cours existant
    if courses:
        with st.expander("Modifier un cours", expanded=False):
            course_to_edit = st.selectbox(
                "Sélectionner un cours à modifier",
                options=[c["name"] for c in courses],
                key="edit_course_select"
            )

            selected_course = next((c for c in courses if c["name"] == course_to_edit), None)

            if selected_course:
                with st.form("edit_course_form"):
                    edit_name = st.text_input("Nom du cours", value=selected_course["name"])
                    edit_code = st.text_input("Code du cours", value=selected_course["code"])
                    edit_schedule = st.text_input("Horaire", value=selected_course["schedule"])
                    edit_description = st.text_area("Description", value=selected_course["description"])

                    update_submitted = st.form_submit_button("Mettre à jour")
                    if update_submitted:
                        # Mettre à jour le cours
                        for i, course in enumerate(courses):
                            if course["id"] == selected_course["id"]:
                                courses[i]["name"] = edit_name
                                courses[i]["code"] = edit_code
                                courses[i]["schedule"] = edit_schedule
                                courses[i]["description"] = edit_description
                                courses[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                break

                        # Sauvegarder les données
                        with open(courses_file, 'w') as f:
                            json.dump(courses, f, indent=4)

                        st.success(f"Cours '{edit_name}' mis à jour avec succès!")
                        st.experimental_rerun()

    # Formulaire pour supprimer un cours
    if courses:
        with st.expander("Supprimer un cours", expanded=False):
            course_to_delete = st.selectbox(
                "Sélectionner un cours à supprimer",
                options=[c["name"] for c in courses],
                key="delete_course_select"
            )

            if st.button("Supprimer", key="delete_course_button"):
                # Confirmation
                confirm = st.checkbox("Je confirme vouloir supprimer ce cours", key="confirm_delete_course")
                if confirm:
                    # Supprimer le cours
                    courses = [c for c in courses if c["name"] != course_to_delete]

                    # Sauvegarder les données
                    with open(courses_file, 'w') as f:
                        json.dump(courses, f, indent=4)

                    st.success(f"Cours '{course_to_delete}' supprimé avec succès!")
                    st.experimental_rerun()
                else:
                    st.warning("Veuillez confirmer la suppression.")

def manage_students(data_loader):
    st.header("Gestion des Étudiants")

    # Charger les données des étudiants
    students_file = os.path.join(data_loader.data_dir, 'students.json')
    if os.path.exists(students_file):
        with open(students_file, 'r') as f:
            students = json.load(f)
    else:
        students = []

    # Charger les données des cours pour l'association
    courses_file = os.path.join(data_loader.data_dir, 'courses.json')
    if os.path.exists(courses_file):
        with open(courses_file, 'r') as f:
            courses = json.load(f)
    else:
        courses = []

    # Afficher les étudiants existants
    if students:
        st.subheader("Étudiants existants")
        students_df = pd.DataFrame(students)
        st.dataframe(students_df)

    # Formulaire pour ajouter un nouvel étudiant
    with st.expander("Ajouter un nouvel étudiant", expanded=False):
        with st.form("add_student_form"):
            student_id = str(uuid.uuid4())[:8]  # Générer un ID unique
            first_name = st.text_input("Prénom")
            last_name = st.text_input("Nom")
            email = st.text_input("Email")
            student_number = st.text_input("Numéro d'étudiant")

            # Sélection des cours
            if courses:
                selected_courses = st.multiselect(
                    "Cours inscrits",
                    options=[c["name"] for c in courses]
                )
                course_ids = [next(c["id"] for c in courses if c["name"] == course_name) for course_name in selected_courses]
            else:
                course_ids = []
                st.warning("Aucun cours disponible. Veuillez d'abord ajouter des cours.")

            # Upload de photo
            photo = st.file_uploader("Photo de l'étudiant", type=["jpg", "jpeg", "png"])

            submitted = st.form_submit_button("Ajouter")
            if submitted and first_name and last_name and email:
                # Sauvegarder la photo si elle existe
                photo_path = None
                if photo:
                    photos_dir = os.path.join(data_loader.data_dir, 'photos')
                    os.makedirs(photos_dir, exist_ok=True)
                    photo_path = os.path.join(photos_dir, f"{student_id}.jpg")
                    with open(photo_path, "wb") as f:
                        f.write(photo.getbuffer())
                    photo_path = f"photos/{student_id}.jpg"

                new_student = {
                    "id": student_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "student_number": student_number,
                    "courses": course_ids,
                    "photo": photo_path,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                students.append(new_student)

                # Sauvegarder les données
                with open(students_file, 'w') as f:
                    json.dump(students, f, indent=4)

                st.success(f"Étudiant '{first_name} {last_name}' ajouté avec succès!")
                st.experimental_rerun()

    # Formulaire pour modifier un étudiant existant
    if students:
        with st.expander("Modifier un étudiant", expanded=False):
            student_to_edit = st.selectbox(
                "Sélectionner un étudiant à modifier",
                options=[f"{s['first_name']} {s['last_name']}" for s in students],
                key="edit_student_select"
            )

            selected_name = student_to_edit.split(" ", 1)
            selected_student = next((s for s in students if s["first_name"] == selected_name[0] and s["last_name"] == selected_name[1]), None)

            if selected_student:
                with st.form("edit_student_form"):
                    edit_first_name = st.text_input("Prénom", value=selected_student["first_name"])
                    edit_last_name = st.text_input("Nom", value=selected_student["last_name"])
                    edit_email = st.text_input("Email", value=selected_student["email"])
                    edit_student_number = st.text_input("Numéro d'étudiant", value=selected_student["student_number"])

                    # Sélection des cours
                    if courses:
                        current_course_ids = selected_student.get("courses", [])
                        current_course_names = [next((c["name"] for c in courses if c["id"] == course_id), "") for course_id in current_course_ids]

                        edit_courses = st.multiselect(
                            "Cours inscrits",
                            options=[c["name"] for c in courses],
                            default=current_course_names
                        )
                        edit_course_ids = [next(c["id"] for c in courses if c["name"] == course_name) for course_name in edit_courses]
                    else:
                        edit_course_ids = []

                    # Upload de nouvelle photo
                    new_photo = st.file_uploader("Nouvelle photo (laisser vide pour conserver l'actuelle)", type=["jpg", "jpeg", "png"])

                    update_submitted = st.form_submit_button("Mettre à jour")
                    if update_submitted:
                        # Mettre à jour la photo si une nouvelle est fournie
                        photo_path = selected_student.get("photo")
                        if new_photo:
                            photos_dir = os.path.join(data_loader.data_dir, 'photos')
                            os.makedirs(photos_dir, exist_ok=True)
                            photo_path = os.path.join(photos_dir, f"{selected_student['id']}.jpg")
                            with open(photo_path, "wb") as f:
                                f.write(new_photo.getbuffer())
                            photo_path = f"photos/{selected_student['id']}.jpg"

                        # Mettre à jour l'étudiant
                        for i, student in enumerate(students):
                            if student["id"] == selected_student["id"]:
                                students[i]["first_name"] = edit_first_name
                                students[i]["last_name"] = edit_last_name
                                students[i]["email"] = edit_email
                                students[i]["student_number"] = edit_student_number
                                students[i]["courses"] = edit_course_ids
                                students[i]["photo"] = photo_path
                                students[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                break

                        # Sauvegarder les données
                        with open(students_file, 'w') as f:
                            json.dump(students, f, indent=4)

                        st.success(f"Étudiant '{edit_first_name} {edit_last_name}' mis à jour avec succès!")
                        st.experimental_rerun()

    # Formulaire pour supprimer un étudiant
    if students:
        with st.expander("Supprimer un étudiant", expanded=False):
            student_to_delete = st.selectbox(
                "Sélectionner un étudiant à supprimer",
                options=[f"{s['first_name']} {s['last_name']}" for s in students],
                key="delete_student_select"
            )

            if st.button("Supprimer", key="delete_student_button"):
                # Confirmation
                confirm = st.checkbox("Je confirme vouloir supprimer cet étudiant", key="confirm_delete_student")
                if confirm:
                    # Trouver l'étudiant à supprimer
                    selected_name = student_to_delete.split(" ", 1)
                    student_to_remove = next((s for s in students if s["first_name"] == selected_name[0] and s["last_name"] == selected_name[1]), None)

                    if student_to_remove:
                        # Supprimer la photo si elle existe
                        if student_to_remove.get("photo"):
                            photo_path = os.path.join(data_loader.data_dir, student_to_remove["photo"])
                            if os.path.exists(photo_path):
                                os.remove(photo_path)

                        # Supprimer l'étudiant
                        students = [s for s in students if not (s["first_name"] == selected_name[0] and s["last_name"] == selected_name[1])]

                        # Sauvegarder les données
                        with open(students_file, 'w') as f:
                            json.dump(students, f, indent=4)

                        st.success(f"Étudiant '{student_to_delete}' supprimé avec succès!")
                        st.experimental_rerun()
                else:
                    st.warning("Veuillez confirmer la suppression.")

def manage_attendance(data_loader):
    st.header("Gestion des Présences")

    # Charger les données des présences
    attendance_file = os.path.join(data_loader.data_dir, 'attendance.json')
    if os.path.exists(attendance_file):
        with open(attendance_file, 'r') as f:
            attendance_records = json.load(f)
    else:
        attendance_records = []

    # Charger les données des cours
    courses_file = os.path.join(data_loader.data_dir, 'courses.json')
    if os.path.exists(courses_file):
        with open(courses_file, 'r') as f:
            courses = json.load(f)
    else:
        courses = []

    # Charger les données des étudiants
    students_file = os.path.join(data_loader.data_dir, 'students.json')
    if os.path.exists(students_file):
        with open(students_file, 'r') as f:
            students = json.load(f)
    else:
        students = []

    # Afficher les enregistrements de présence existants
    if attendance_records:
        st.subheader("Enregistrements de présence existants")

        # Préparer les données pour l'affichage
        display_records = []
        for record in attendance_records:
            course_name = next((c["name"] for c in courses if c["id"] == record["course_id"]), "Inconnu")
            student_name = next((f"{s['first_name']} {s['last_name']}" for s in students if s["id"] == record["student_id"]), "Inconnu")

            display_records.append({
                "ID": record["id"],
                "Date": record["date"],
                "Cours": course_name,
                "Étudiant": student_name,
                "Présent": "Oui" if record["present"] else "Non",
                "Méthode": record["method"]
            })

        attendance_df = pd.DataFrame(display_records)
        st.dataframe(attendance_df)

    # Formulaire pour ajouter un nouvel enregistrement de présence individuel
    with st.expander("Ajouter un enregistrement de présence individuel", expanded=False):
        with st.form("add_attendance_form"):
            attendance_id = str(uuid.uuid4())[:8]  # Générer un ID unique

            # Sélection du cours
            if courses:
                selected_course = st.selectbox(
                    "Cours",
                    options=[c["name"] for c in courses],
                    key="add_attendance_course"
                )
                course_id = next(c["id"] for c in courses if c["name"] == selected_course)
            else:
                course_id = None
                st.warning("Aucun cours disponible. Veuillez d'abord ajouter des cours.")

            # Sélection de l'étudiant
            if students:
                selected_student = st.selectbox(
                    "Étudiant",
                    options=[f"{s['first_name']} {s['last_name']}" for s in students],
                    key="add_attendance_student"
                )
                selected_name = selected_student.split(" ", 1)
                student_id = next(s["id"] for s in students if s["first_name"] == selected_name[0] and s["last_name"] == selected_name[1])
            else:
                student_id = None
                st.warning("Aucun étudiant disponible. Veuillez d'abord ajouter des étudiants.")

            # Date et statut
            attendance_date = st.date_input("Date", datetime.now())
            is_present = st.checkbox("Présent", value=True)
            method = st.selectbox("Méthode d'enregistrement", ["Manuel", "Reconnaissance faciale", "Autre"])

            submitted = st.form_submit_button("Ajouter")
            if submitted and course_id and student_id:
                new_attendance = {
                    "id": attendance_id,
                    "course_id": course_id,
                    "student_id": student_id,
                    "date": attendance_date.strftime("%Y-%m-%d"),
                    "present": is_present,
                    "method": method,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                attendance_records.append(new_attendance)

                # Sauvegarder les données
                with open(attendance_file, 'w') as f:
                    json.dump(attendance_records, f, indent=4)

                st.success("Enregistrement de présence ajouté avec succès!")
                st.experimental_rerun()

    # Formulaire pour générer une feuille de présence complète (présents ET absents)
    with st.expander("Générer une feuille de présence complète", expanded=False):
        st.write("Cette option génère une feuille de présence pour tous les étudiants inscrits à un cours, en marquant leur statut (présent ou absent).")

        # Sélection du cours
        if courses:
            selected_course_for_sheet = st.selectbox(
                "Cours",
                options=[c["name"] for c in courses],
                key="sheet_course"
            )
            selected_course_id = next(c["id"] for c in courses if c["name"] == selected_course_for_sheet)
            selected_course_obj = next(c for c in courses if c["id"] == selected_course_id)

            # Trouver tous les étudiants inscrits à ce cours
            enrolled_students = [s for s in students if "courses" in s and selected_course_id in s["courses"]]

            if enrolled_students:
                # Date de la feuille de présence
                sheet_date = st.date_input("Date de la séance", datetime.now(), key="sheet_date")
                sheet_date_str = sheet_date.strftime("%Y-%m-%d")

                # Méthode d'enregistrement
                sheet_method = st.selectbox(
                    "Méthode d'enregistrement",
                    ["Manuel", "Reconnaissance faciale", "Autre"],
                    key="sheet_method"
                )

                # Vérifier si des enregistrements existent déjà pour cette date et ce cours
                existing_records = [r for r in attendance_records
                                  if r["course_id"] == selected_course_id and r["date"] == sheet_date_str]

                existing_student_ids = [r["student_id"] for r in existing_records]

                # Afficher la liste des étudiants avec des cases à cocher pour la présence
                st.subheader("Liste des étudiants")

                # Créer un DataFrame pour l'affichage et la sélection
                student_list = []
                for student in enrolled_students:
                    # Vérifier si l'étudiant a déjà un enregistrement pour cette date
                    is_already_recorded = student["id"] in existing_student_ids
                    is_present = next((r["present"] for r in existing_records if r["student_id"] == student["id"]), False)

                    student_list.append({
                        "id": student["id"],
                        "name": f"{student['first_name']} {student['last_name']}",
                        "already_recorded": is_already_recorded,
                        "present": is_present
                    })

                # Créer un formulaire pour la feuille de présence
                with st.form("attendance_sheet_form"):
                    # Afficher les étudiants avec des cases à cocher
                    student_presence = {}
                    for student in student_list:
                        default_value = student["present"] if student["already_recorded"] else False
                        student_presence[student["id"]] = st.checkbox(
                            f"{student['name']} {' (déjà enregistré)' if student['already_recorded'] else ''}",
                            value=default_value,
                            key=f"presence_{student['id']}"
                        )

                    # Bouton pour enregistrer la feuille de présence
                    submit_sheet = st.form_submit_button("Enregistrer la feuille de présence")

                    if submit_sheet:
                        # Créer ou mettre à jour les enregistrements de présence
                        updated_count = 0
                        new_count = 0

                        for student_id, is_present in student_presence.items():
                            # Vérifier si un enregistrement existe déjà
                            existing_record = next((r for r in attendance_records
                                                if r["course_id"] == selected_course_id
                                                and r["student_id"] == student_id
                                                and r["date"] == sheet_date_str), None)

                            if existing_record:
                                # Mettre à jour l'enregistrement existant
                                existing_record["present"] = is_present
                                existing_record["method"] = sheet_method
                                existing_record["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                updated_count += 1
                            else:
                                # Créer un nouvel enregistrement
                                new_record = {
                                    "id": str(uuid.uuid4())[:8],
                                    "course_id": selected_course_id,
                                    "student_id": student_id,
                                    "date": sheet_date_str,
                                    "present": is_present,
                                    "method": sheet_method,
                                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }
                                attendance_records.append(new_record)
                                new_count += 1

                        # Sauvegarder les données
                        with open(attendance_file, 'w') as f:
                            json.dump(attendance_records, f, indent=4)

                        # Afficher un message de succès
                        st.success(f"Feuille de présence enregistrée avec succès! {new_count} nouveaux enregistrements, {updated_count} enregistrements mis à jour.")
                        st.experimental_rerun()
            else:
                st.warning(f"Aucun étudiant n'est inscrit au cours '{selected_course_for_sheet}'. Veuillez d'abord inscrire des étudiants à ce cours.")
        else:
            st.warning("Aucun cours disponible. Veuillez d'abord ajouter des cours.")

    # Exporter les données de présence en CSV
    with st.expander("Exporter les données de présence", expanded=False):
        st.write("Exportez les données de présence pour un cours spécifique ou pour tous les cours.")

        # Sélection du cours pour l'exportation
        export_course_options = ["Tous les cours"] + [c["name"] for c in courses]
        export_course = st.selectbox(
            "Cours à exporter",
            options=export_course_options,
            key="export_course"
        )

        # Sélection de la période
        export_period_options = ["Toutes les dates", "Période spécifique"]
        export_period = st.selectbox(
            "Période",
            options=export_period_options,
            key="export_period"
        )

        if export_period == "Période spécifique":
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Date de début", datetime.now() - timedelta(days=30), key="export_start_date")
            with col2:
                end_date = st.date_input("Date de fin", datetime.now(), key="export_end_date")

        if st.button("Générer le rapport CSV"):
            # Filtrer les données selon les critères
            filtered_records = attendance_records.copy()

            # Filtrer par cours
            if export_course != "Tous les cours":
                course_id = next(c["id"] for c in courses if c["name"] == export_course)
                filtered_records = [r for r in filtered_records if r["course_id"] == course_id]

            # Filtrer par période
            if export_period == "Période spécifique":
                start_date_str = start_date.strftime("%Y-%m-%d")
                end_date_str = end_date.strftime("%Y-%m-%d")
                filtered_records = [r for r in filtered_records if start_date_str <= r["date"] <= end_date_str]

            if filtered_records:
                # Préparer les données pour l'exportation
                export_data = []
                for record in filtered_records:
                    course_name = next((c["name"] for c in courses if c["id"] == record["course_id"]), "Inconnu")
                    student = next((s for s in students if s["id"] == record["student_id"]), None)
                    student_name = f"{student['first_name']} {student['last_name']}" if student else "Inconnu"

                    export_data.append({
                        "Date": record["date"],
                        "Cours": course_name,
                        "Numéro d'étudiant": student["student_number"] if student else "Inconnu",
                        "Nom": student["last_name"] if student else "Inconnu",
                        "Prénom": student["first_name"] if student else "Inconnu",
                        "Présent": "Oui" if record["present"] else "Non",
                        "Méthode": record["method"]
                    })

                # Créer un DataFrame et le convertir en CSV
                export_df = pd.DataFrame(export_data)
                csv = export_df.to_csv(index=False)

                # Créer un lien de téléchargement
                current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"presence_{current_time}.csv"

                st.download_button(
                    label="Télécharger le CSV",
                    data=csv,
                    file_name=filename,
                    mime="text/csv"
                )

                # Afficher un aperçu
                st.subheader("Aperçu du rapport")
                st.dataframe(export_df)
            else:
                st.warning("Aucune donnée ne correspond aux critères sélectionnés.")

    # Formulaire pour modifier un enregistrement de présence
    if attendance_records:
        with st.expander("Modifier un enregistrement de présence", expanded=False):
            # Préparer les options pour la sélection
            attendance_options = []
            for record in attendance_records:
                course_name = next((c["name"] for c in courses if c["id"] == record["course_id"]), "Inconnu")
                student_name = next((f"{s['first_name']} {s['last_name']}" for s in students if s["id"] == record["student_id"]), "Inconnu")
                attendance_options.append(f"{record['date']} - {course_name} - {student_name}")

            selected_attendance_str = st.selectbox(
                "Sélectionner un enregistrement à modifier",
                options=attendance_options,
                key="edit_attendance_select"
            )

            selected_index = attendance_options.index(selected_attendance_str)
            selected_attendance = attendance_records[selected_index]

            with st.form("edit_attendance_form"):
                # Sélection du cours
                current_course_name = next((c["name"] for c in courses if c["id"] == selected_attendance["course_id"]), "")
                edit_course = st.selectbox(
                    "Cours",
                    options=[c["name"] for c in courses],
                    index=[c["name"] for c in courses].index(current_course_name) if current_course_name in [c["name"] for c in courses] else 0
                )
                edit_course_id = next(c["id"] for c in courses if c["name"] == edit_course)

                # Sélection de l'étudiant
                current_student = next((s for s in students if s["id"] == selected_attendance["student_id"]), None)
                current_student_name = f"{current_student['first_name']} {current_student['last_name']}" if current_student else ""

                edit_student = st.selectbox(
                    "Étudiant",
                    options=[f"{s['first_name']} {s['last_name']}" for s in students],
                    index=[f"{s['first_name']} {s['last_name']}" for s in students].index(current_student_name) if current_student_name in [f"{s['first_name']} {s['last_name']}" for s in students] else 0
                )
                edit_student_name = edit_student.split(" ", 1)
                edit_student_id = next(s["id"] for s in students if s["first_name"] == edit_student_name[0] and s["last_name"] == edit_student_name[1])

                # Date et statut
                edit_date = st.date_input("Date", datetime.strptime(selected_attendance["date"], "%Y-%m-%d"))
                edit_present = st.checkbox("Présent", value=selected_attendance["present"])
                edit_method = st.selectbox(
                    "Méthode d'enregistrement",
                    ["Manuel", "Reconnaissance faciale", "Autre"],
                    index=["Manuel", "Reconnaissance faciale", "Autre"].index(selected_attendance["method"]) if selected_attendance["method"] in ["Manuel", "Reconnaissance faciale", "Autre"] else 0
                )

                update_submitted = st.form_submit_button("Mettre à jour")
                if update_submitted:
                    # Mettre à jour l'enregistrement
                    attendance_records[selected_index]["course_id"] = edit_course_id
                    attendance_records[selected_index]["student_id"] = edit_student_id
                    attendance_records[selected_index]["date"] = edit_date.strftime("%Y-%m-%d")
                    attendance_records[selected_index]["present"] = edit_present
                    attendance_records[selected_index]["method"] = edit_method
                    attendance_records[selected_index]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # Sauvegarder les données
                    with open(attendance_file, 'w') as f:
                        json.dump(attendance_records, f, indent=4)

                    st.success("Enregistrement de présence mis à jour avec succès!")
                    st.experimental_rerun()

    # Formulaire pour supprimer un enregistrement de présence
    if attendance_records:
        with st.expander("Supprimer un enregistrement de présence", expanded=False):
            # Préparer les options pour la sélection
            attendance_options = []
            for record in attendance_records:
                course_name = next((c["name"] for c in courses if c["id"] == record["course_id"]), "Inconnu")
                student_name = next((f"{s['first_name']} {s['last_name']}" for s in students if s["id"] == record["student_id"]), "Inconnu")
                attendance_options.append(f"{record['date']} - {course_name} - {student_name}")

            selected_attendance_str = st.selectbox(
                "Sélectionner un enregistrement à supprimer",
                options=attendance_options,
                key="delete_attendance_select"
            )

            if st.button("Supprimer", key="delete_attendance_button"):
                # Confirmation
                confirm = st.checkbox("Je confirme vouloir supprimer cet enregistrement", key="confirm_delete_attendance")
                if confirm:
                    selected_index = attendance_options.index(selected_attendance_str)

                    # Supprimer l'enregistrement
                    del attendance_records[selected_index]

                    # Sauvegarder les données
                    with open(attendance_file, 'w') as f:
                        json.dump(attendance_records, f, indent=4)

                    st.success("Enregistrement de présence supprimé avec succès!")
                    st.experimental_rerun()
                else:
                    st.warning("Veuillez confirmer la suppression.")
