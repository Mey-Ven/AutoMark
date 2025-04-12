"""
Module de gestion de la base de données SQLite pour AutoMark.
"""

import os
import sqlite3
import pandas as pd
import logging
import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("db_manager")

class DBManager:
    """Gestionnaire de base de données SQLite pour AutoMark."""

    def __init__(self, data_dir):
        """Initialise le gestionnaire de base de données."""
        self.data_dir = data_dir
        self.db_path = os.path.join(data_dir, "automark.db")
        self.conn = None
        self.cursor = None

    def connect(self):
        """Établit une connexion à la base de données SQLite."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            logger.info(f"Connexion établie à la base de données: {self.db_path}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la connexion à la base de données: {e}")
            return False

    def disconnect(self):
        """Ferme la connexion à la base de données."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
            logger.info("Connexion à la base de données fermée")

    def initialize_database(self):
        """Initialise la structure de la base de données."""
        if not self.connect():
            return False

        try:
            # Création des tables principales
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT,
                group_name TEXT,
                photo_path TEXT
            )
            """)

            # Créer des index pour améliorer les performances des requêtes
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_student_id ON students(student_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_group ON students(group_name)")

            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id TEXT UNIQUE NOT NULL,
                course_name TEXT NOT NULL,
                instructor TEXT,
                group_name TEXT,
                schedule TEXT
            )
            """)

            # Créer des index pour la table courses
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_courses_course_id ON courses(course_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_courses_group ON courses(group_name)")

            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                time TEXT,
                status TEXT NOT NULL DEFAULT 'present',
                FOREIGN KEY (student_id) REFERENCES students(id),
                FOREIGN KEY (course_id) REFERENCES courses(id),
                UNIQUE(student_id, course_id, date)
            )
            """)

            # Créer des index pour la table attendance
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_student ON attendance(student_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_course ON attendance(course_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_attendance_status ON attendance(status)")

            # Création de la table des utilisateurs
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
            """)

            # Créer des index pour la table users
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)")

            # Vérifier si la table users est vide et ajouter un utilisateur admin par défaut
            self.cursor.execute("SELECT COUNT(*) FROM users")
            count = self.cursor.fetchone()[0]

            if count == 0:
                # Ajouter un utilisateur admin par défaut
                import hashlib
                password_hash = hashlib.sha256("admin".encode()).hexdigest()

                self.cursor.execute("""
                INSERT INTO users (username, password_hash, role, first_name, last_name, email)
                VALUES (?, ?, ?, ?, ?, ?)
                """, ("admin", password_hash, "admin", "Admin", "System", "admin@automark.com"))

                logger.info("Utilisateur admin par défaut créé")

            self.conn.commit()
            logger.info("Structure de la base de données initialisée avec succès")
            return True
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
            self.conn.rollback()
            return False
        finally:
            self.disconnect()

    def migrate_data_from_csv(self):
        """Migre les données des fichiers CSV vers la base de données SQLite."""
        if not self.connect():
            return False

        try:
            # Migration des étudiants
            students_csv_path = os.path.join(self.data_dir, "students.csv")
            if os.path.exists(students_csv_path):
                df_students = pd.read_csv(students_csv_path)
                for _, row in df_students.iterrows():
                    self.cursor.execute("""
                    INSERT OR IGNORE INTO students (student_id, first_name, last_name, group_name)
                    VALUES (?, ?, ?, ?)
                    """, (
                        row["StudentID"],
                        row["FirstName"],
                        row["LastName"],
                        row.get("Group", "")
                    ))
                logger.info(f"Données étudiants migrées depuis {students_csv_path}")

            # Migration des cours
            courses_csv_path = os.path.join(self.data_dir, "courses.csv")
            if os.path.exists(courses_csv_path):
                df_courses = pd.read_csv(courses_csv_path)
                for _, row in df_courses.iterrows():
                    self.cursor.execute("""
                    INSERT OR IGNORE INTO courses (course_id, course_name, instructor, group_name, schedule)
                    VALUES (?, ?, ?, ?, ?)
                    """, (
                        row["CourseID"],
                        row["CourseName"],
                        row.get("Instructor", ""),
                        row.get("Group", ""),
                        row.get("Schedule", "")
                    ))
                logger.info(f"Données cours migrées depuis {courses_csv_path}")

            # Migration des présences
            attendance_dir = os.path.join(self.data_dir, "attendance")
            if os.path.exists(attendance_dir):
                for filename in os.listdir(attendance_dir):
                    if filename.endswith(".csv"):
                        parts = filename.replace(".csv", "").split("_")
                        if len(parts) >= 2:
                            course_id = parts[0]
                            date = parts[1]

                            # Récupérer l'ID du cours
                            self.cursor.execute("SELECT id FROM courses WHERE course_id = ?", (course_id,))
                            course_result = self.cursor.fetchone()
                            if course_result:
                                course_db_id = course_result["id"]

                                # Lire le fichier de présence
                                attendance_path = os.path.join(attendance_dir, filename)
                                df_attendance = pd.read_csv(attendance_path)

                                for _, row in df_attendance.iterrows():
                                    student_id = row["StudentID"]
                                    time = row.get("Time", "")

                                    # Récupérer l'ID de l'étudiant
                                    self.cursor.execute("SELECT id FROM students WHERE student_id = ?", (student_id,))
                                    student_result = self.cursor.fetchone()

                                    if student_result:
                                        student_db_id = student_result["id"]

                                        # Insérer la présence
                                        self.cursor.execute("""
                                        INSERT OR REPLACE INTO attendance (student_id, course_id, date, time, status)
                                        VALUES (?, ?, ?, ?, ?)
                                        """, (student_db_id, course_db_id, date, time, "present"))

                                logger.info(f"Données de présence migrées depuis {attendance_path}")

            self.conn.commit()
            logger.info("Migration des données CSV vers SQLite terminée avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la migration des données: {e}")
            self.conn.rollback()
            return False
        finally:
            self.disconnect()

    def get_students(self):
        """
        Récupère la liste de tous les étudiants.

        Returns:
            list: Liste des étudiants sous forme de dictionnaires
        """
        if not self.connect():
            return []

        try:
            self.cursor.execute('SELECT * FROM students')
            students = [dict(row) for row in self.cursor.fetchall()]
            return students
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la récupération des étudiants: {e}")
            return []
        finally:
            self.disconnect()

    def get_courses(self):
        """
        Récupère la liste de tous les cours.

        Returns:
            list: Liste des cours sous forme de dictionnaires
        """
        if not self.connect():
            return []

        try:
            self.cursor.execute('SELECT * FROM courses')
            courses = [dict(row) for row in self.cursor.fetchall()]
            return courses
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la récupération des cours: {e}")
            return []
        finally:
            self.disconnect()

    def get_attendance(self, course_id=None, date=None, student_id=None):
        """
        Récupère les données de présence avec filtrage optionnel.

        Args:
            course_id (int, optional): ID du cours pour filtrer
            date (str, optional): Date pour filtrer (format YYYY-MM-DD)
            student_id (int, optional): ID de l'étudiant pour filtrer

        Returns:
            list: Liste des présences sous forme de dictionnaires
        """
        if not self.connect():
            return []

        try:
            query = '''
            SELECT a.*, s.first_name, s.last_name, s.student_id as student_code,
                   c.course_name, c.course_id as course_code
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            JOIN courses c ON a.course_id = c.id
            WHERE 1=1
            '''
            params = []

            if course_id:
                query += ' AND a.course_id = ?'
                params.append(course_id)

            if date:
                query += ' AND a.date = ?'
                params.append(date)

            if student_id:
                query += ' AND a.student_id = ?'
                params.append(student_id)

            self.cursor.execute(query, params)
            attendance = [dict(row) for row in self.cursor.fetchall()]
            return attendance
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la récupération des présences: {e}")
            return []
        finally:
            self.disconnect()

    # Fonctions de gestion des utilisateurs

    def get_users(self):
        """
        Récupère la liste de tous les utilisateurs.

        Returns:
            list: Liste des utilisateurs sous forme de dictionnaires
        """
        if not self.connect():
            return []

        try:
            self.cursor.execute('''
            SELECT id, username, role, created_at, last_login
            FROM users
            ORDER BY username
            ''')
            users = [dict(row) for row in self.cursor.fetchall()]
            return users
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la récupération des utilisateurs: {e}")
            return []
        finally:
            self.disconnect()

    def get_user_by_id(self, user_id):
        """
        Récupère un utilisateur par son ID.

        Args:
            user_id (int): ID de l'utilisateur

        Returns:
            dict: Informations de l'utilisateur, None si non trouvé
        """
        if not self.connect():
            return None

        try:
            self.cursor.execute('''
            SELECT id, username, role, created_at, last_login
            FROM users
            WHERE id = ?
            ''', (user_id,))
            user = self.cursor.fetchone()
            return dict(user) if user else None
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la récupération de l'utilisateur: {e}")
            return None
        finally:
            self.disconnect()

    def get_user_by_username(self, username):
        """
        Récupère un utilisateur par son nom d'utilisateur.

        Args:
            username (str): Nom d'utilisateur

        Returns:
            dict: Informations de l'utilisateur, None si non trouvé
        """
        if not self.connect():
            return None

        try:
            self.cursor.execute('''
            SELECT id, username, role, created_at, last_login
            FROM users
            WHERE username = ?
            ''', (username,))
            user = self.cursor.fetchone()
            return dict(user) if user else None
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la récupération de l'utilisateur: {e}")
            return None
        finally:
            self.disconnect()

    def add_user(self, user_data):
        """
        Ajoute un nouvel utilisateur à la base de données.

        Args:
            user_data (dict): Données de l'utilisateur avec les clés:
                - username: Nom d'utilisateur
                - password: Mot de passe en clair
                - role: Rôle de l'utilisateur (admin, teacher, student)
                - student_id: ID de l'étudiant (si role=student)
                - courses: Liste des IDs de cours (si role=teacher)

        Returns:
            bool: True si l'ajout a réussi, False sinon
        """
        if not self.connect():
            return False

        try:
            # Vérifier si l'utilisateur existe déjà
            self.cursor.execute("SELECT id FROM users WHERE username = ?", (user_data['username'],))
            if self.cursor.fetchone():
                logger.error(f"L'utilisateur {user_data['username']} existe déjà")
                return False

            # Hacher le mot de passe
            import hashlib
            password_hash = hashlib.sha256(user_data['password'].encode()).hexdigest()

            # Insérer l'utilisateur
            self.cursor.execute('''
            INSERT INTO users (username, password_hash, role)
            VALUES (?, ?, ?)
            ''', (
                user_data['username'],
                password_hash,
                user_data['role']
            ))

            user_id = self.cursor.lastrowid

            # Si c'est un enseignant, associer aux cours
            if user_data['role'] == 'teacher' and 'courses' in user_data:
                for course_id in user_data['courses']:
                    self.cursor.execute('''
                    UPDATE courses
                    SET teacher_id = ?
                    WHERE course_id = ?
                    ''', (user_id, course_id))

            # Si c'est un étudiant, associer au profil étudiant
            if user_data['role'] == 'student' and 'student_id' in user_data:
                self.cursor.execute('''
                UPDATE students
                SET user_id = ?
                WHERE student_id = ?
                ''', (user_id, user_data['student_id']))

            self.conn.commit()
            logger.info(f"Utilisateur ajouté avec succès: {user_data['username']}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de l'ajout de l'utilisateur: {e}")
            self.conn.rollback()
            return False
        finally:
            self.disconnect()

    def update_user(self, user_id, user_data):
        """
        Met à jour un utilisateur existant.

        Args:
            user_id (int): ID de l'utilisateur à mettre à jour
            user_data (dict): Données de l'utilisateur à mettre à jour

        Returns:
            bool: True si la mise à jour a réussi, False sinon
        """
        if not self.connect():
            return False

        try:
            # Vérifier si l'utilisateur existe
            self.cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
            if not self.cursor.fetchone():
                logger.error(f"L'utilisateur avec l'ID {user_id} n'existe pas")
                return False

            # Construire la requête de mise à jour
            update_fields = []
            params = []

            if 'username' in user_data:
                update_fields.append("username = ?")
                params.append(user_data['username'])

            if 'password' in user_data:
                import hashlib
                password_hash = hashlib.sha256(user_data['password'].encode()).hexdigest()
                update_fields.append("password_hash = ?")
                params.append(password_hash)

            if 'role' in user_data:
                update_fields.append("role = ?")
                params.append(user_data['role'])

            if not update_fields:
                logger.warning("Aucun champ à mettre à jour")
                return True

            # Mettre à jour l'utilisateur
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
            params.append(user_id)

            self.cursor.execute(query, params)

            # Si c'est un enseignant, mettre à jour les cours associés
            if user_data.get('role') == 'teacher' and 'courses' in user_data:
                # Supprimer les associations existantes
                self.cursor.execute("UPDATE courses SET teacher_id = NULL WHERE teacher_id = ?", (user_id,))

                # Ajouter les nouvelles associations
                for course_id in user_data['courses']:
                    self.cursor.execute('''
                    UPDATE courses
                    SET teacher_id = ?
                    WHERE course_id = ?
                    ''', (user_id, course_id))

            # Si c'est un étudiant, mettre à jour le profil étudiant associé
            if user_data.get('role') == 'student' and 'student_id' in user_data:
                # Supprimer les associations existantes
                self.cursor.execute("UPDATE students SET user_id = NULL WHERE user_id = ?", (user_id,))

                # Ajouter la nouvelle association
                self.cursor.execute('''
                UPDATE students
                SET user_id = ?
                WHERE student_id = ?
                ''', (user_id, user_data['student_id']))

            self.conn.commit()
            logger.info(f"Utilisateur mis à jour avec succès: ID {user_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la mise à jour de l'utilisateur: {e}")
            self.conn.rollback()
            return False
        finally:
            self.disconnect()

    def delete_user(self, user_id):
        """
        Supprime un utilisateur de la base de données.

        Args:
            user_id (int): ID de l'utilisateur à supprimer

        Returns:
            bool: True si la suppression a réussi, False sinon
        """
        if not self.connect():
            return False

        try:
            # Vérifier si l'utilisateur existe
            self.cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
            if not self.cursor.fetchone():
                logger.error(f"L'utilisateur avec l'ID {user_id} n'existe pas")
                return False

            # Supprimer les associations avec les cours (si enseignant)
            self.cursor.execute("UPDATE courses SET teacher_id = NULL WHERE teacher_id = ?", (user_id,))

            # Supprimer les associations avec les étudiants (si étudiant)
            self.cursor.execute("UPDATE students SET user_id = NULL WHERE user_id = ?", (user_id,))

            # Supprimer l'utilisateur
            self.cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))

            self.conn.commit()
            logger.info(f"Utilisateur supprimé avec succès: ID {user_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la suppression de l'utilisateur: {e}")
            self.conn.rollback()
            return False
        finally:
            self.disconnect()

    def change_password(self, user_id, new_password):
        """
        Change le mot de passe d'un utilisateur.

        Args:
            user_id (int): ID de l'utilisateur
            new_password (str): Nouveau mot de passe

        Returns:
            bool: True si le changement a réussi, False sinon
        """
        if not self.connect():
            return False

        try:
            # Vérifier si l'utilisateur existe
            self.cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
            if not self.cursor.fetchone():
                logger.error(f"L'utilisateur avec l'ID {user_id} n'existe pas")
                return False

            # Hacher le nouveau mot de passe
            import hashlib
            password_hash = hashlib.sha256(new_password.encode()).hexdigest()

            # Mettre à jour le mot de passe
            self.cursor.execute('''
            UPDATE users
            SET password_hash = ?
            WHERE id = ?
            ''', (password_hash, user_id))

            self.conn.commit()
            logger.info(f"Mot de passe changé avec succès pour l'utilisateur ID {user_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Erreur lors du changement de mot de passe: {e}")
            self.conn.rollback()
            return False
        finally:
            self.disconnect()

    def backup_database(self, backup_dir=None):
        """
        Crée une sauvegarde de la base de données.

        Args:
            backup_dir (str, optional): Répertoire où stocker la sauvegarde. Par défaut, utilise un sous-répertoire 'backups' dans le répertoire de données.

        Returns:
            bool: True si la sauvegarde a réussi, False sinon
        """
        if not backup_dir:
            backup_dir = os.path.join(self.data_dir, 'backups')

        # Créer le répertoire de sauvegarde s'il n'existe pas
        os.makedirs(backup_dir, exist_ok=True)

        # Générer un nom de fichier avec la date et l'heure
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"automark_backup_{timestamp}.db")

        if not self.connect():
            return False

        try:
            # Créer une sauvegarde en utilisant la commande VACUUM INTO
            self.cursor.execute(f"VACUUM INTO '{backup_file}'")
            logger.info(f"Sauvegarde de la base de données créée avec succès: {backup_file}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la sauvegarde de la base de données: {e}")

            # Essayer une méthode alternative si VACUUM INTO n'est pas supporté
            try:
                # Fermer la connexion actuelle
                self.disconnect()

                # Copier le fichier de base de données
                import shutil
                shutil.copy2(self.db_path, backup_file)
                logger.info(f"Sauvegarde de la base de données créée avec succès (méthode alternative): {backup_file}")
                return True
            except Exception as e2:
                logger.error(f"Erreur lors de la sauvegarde alternative: {e2}")
                return False
        finally:
            self.disconnect()

    def restore_database(self, backup_file):
        """
        Restaure la base de données à partir d'une sauvegarde.

        Args:
            backup_file (str): Chemin vers le fichier de sauvegarde

        Returns:
            bool: True si la restauration a réussi, False sinon
        """
        if not os.path.exists(backup_file):
            logger.error(f"Le fichier de sauvegarde {backup_file} n'existe pas")
            return False

        # Fermer toute connexion existante
        self.disconnect()

        try:
            # Sauvegarder le fichier actuel avant de le remplacer
            import shutil
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            current_backup = f"{self.db_path}.{timestamp}.bak"
            shutil.copy2(self.db_path, current_backup)
            logger.info(f"Base de données actuelle sauvegardée: {current_backup}")

            # Remplacer la base de données actuelle par la sauvegarde
            shutil.copy2(backup_file, self.db_path)
            logger.info(f"Base de données restaurée à partir de: {backup_file}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la restauration de la base de données: {e}")
            return False
