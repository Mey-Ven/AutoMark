import sqlite3
import os
import pandas as pd
from datetime import datetime
import uuid

class DatabaseManager:
    """
    Gestionnaire de base de données pour l'application AutoMark.
    Gère la connexion à la base de données SQLite et fournit des méthodes
    pour interagir avec les données.
    """

    def __init__(self, db_path):
        """
        Initialise le gestionnaire de base de données.
        
        Args:
            db_path: Chemin vers le fichier de base de données SQLite
        """
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        
        # Créer le répertoire de la base de données s'il n'existe pas
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialiser la base de données
        self.connect()
        self.create_tables()
        self.disconnect()

    def connect(self):
        """Établit une connexion à la base de données."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # Pour accéder aux colonnes par nom
        self.cursor = self.connection.cursor()

    def disconnect(self):
        """Ferme la connexion à la base de données."""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None

    def create_tables(self):
        """Crée les tables nécessaires si elles n'existent pas déjà."""
        # Table des cours
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            instructor TEXT NOT NULL,
            group_name TEXT NOT NULL,
            schedule TEXT,
            created_at TEXT NOT NULL
        )
        ''')
        
        # Table des étudiants
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            group_name TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        ''')
        
        # Table des présences
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id TEXT PRIMARY KEY,
            course_id TEXT NOT NULL,
            student_id TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT NOT NULL,
            method TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            FOREIGN KEY (course_id) REFERENCES courses (id),
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
        ''')
        
        # Créer des index pour améliorer les performances des requêtes
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_attendance_course_id ON attendance (course_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_attendance_student_id ON attendance (student_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance (date)')
        
        self.connection.commit()

    # Méthodes pour les cours
    def get_all_courses(self):
        """
        Récupère tous les cours de la base de données.
        
        Returns:
            DataFrame pandas contenant tous les cours
        """
        self.connect()
        query = "SELECT * FROM courses ORDER BY name"
        df = pd.read_sql_query(query, self.connection)
        self.disconnect()
        return df

    def add_course(self, name, instructor, group_name, schedule):
        """
        Ajoute un nouveau cours à la base de données.
        
        Args:
            name: Nom du cours
            instructor: Nom de l'enseignant
            group_name: Nom du groupe
            schedule: Horaire du cours
            
        Returns:
            ID du cours ajouté
        """
        self.connect()
        
        # Vérifier si un cours avec le même nom existe déjà
        self.cursor.execute("SELECT id FROM courses WHERE name = ?", (name,))
        existing = self.cursor.fetchone()
        
        if existing:
            self.disconnect()
            return None
        
        # Générer un ID unique
        course_id = f"C{str(uuid.uuid4())[:6].upper()}"
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Insérer le nouveau cours
        self.cursor.execute(
            "INSERT INTO courses (id, name, instructor, group_name, schedule, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (course_id, name, instructor, group_name, schedule, created_at)
        )
        
        self.connection.commit()
        self.disconnect()
        
        return course_id

    def update_course(self, course_id, name, instructor, group_name, schedule):
        """
        Met à jour un cours existant.
        
        Args:
            course_id: ID du cours à mettre à jour
            name: Nouveau nom du cours
            instructor: Nouveau nom de l'enseignant
            group_name: Nouveau nom du groupe
            schedule: Nouvel horaire du cours
            
        Returns:
            True si la mise à jour a réussi, False sinon
        """
        self.connect()
        
        # Vérifier si le cours existe
        self.cursor.execute("SELECT id FROM courses WHERE id = ?", (course_id,))
        existing = self.cursor.fetchone()
        
        if not existing:
            self.disconnect()
            return False
        
        # Mettre à jour le cours
        self.cursor.execute(
            "UPDATE courses SET name = ?, instructor = ?, group_name = ?, schedule = ? WHERE id = ?",
            (name, instructor, group_name, schedule, course_id)
        )
        
        self.connection.commit()
        self.disconnect()
        
        return True

    def delete_course(self, course_id):
        """
        Supprime un cours de la base de données.
        
        Args:
            course_id: ID du cours à supprimer
            
        Returns:
            True si la suppression a réussi, False sinon
        """
        self.connect()
        
        # Vérifier si le cours existe
        self.cursor.execute("SELECT id FROM courses WHERE id = ?", (course_id,))
        existing = self.cursor.fetchone()
        
        if not existing:
            self.disconnect()
            return False
        
        # Supprimer les présences associées à ce cours
        self.cursor.execute("DELETE FROM attendance WHERE course_id = ?", (course_id,))
        
        # Supprimer le cours
        self.cursor.execute("DELETE FROM courses WHERE id = ?", (course_id,))
        
        self.connection.commit()
        self.disconnect()
        
        return True

    # Méthodes pour les étudiants
    def get_all_students(self):
        """
        Récupère tous les étudiants de la base de données.
        
        Returns:
            DataFrame pandas contenant tous les étudiants
        """
        self.connect()
        query = "SELECT * FROM students ORDER BY last_name, first_name"
        df = pd.read_sql_query(query, self.connection)
        self.disconnect()
        return df

    def add_student(self, first_name, last_name, group_name):
        """
        Ajoute un nouvel étudiant à la base de données.
        
        Args:
            first_name: Prénom de l'étudiant
            last_name: Nom de l'étudiant
            group_name: Nom du groupe
            
        Returns:
            ID de l'étudiant ajouté
        """
        self.connect()
        
        # Générer un ID unique
        student_id = f"S{str(uuid.uuid4())[:6].upper()}"
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Insérer le nouvel étudiant
        self.cursor.execute(
            "INSERT INTO students (id, first_name, last_name, group_name, created_at) VALUES (?, ?, ?, ?, ?)",
            (student_id, first_name, last_name, group_name, created_at)
        )
        
        self.connection.commit()
        self.disconnect()
        
        return student_id

    def update_student(self, student_id, first_name, last_name, group_name):
        """
        Met à jour un étudiant existant.
        
        Args:
            student_id: ID de l'étudiant à mettre à jour
            first_name: Nouveau prénom de l'étudiant
            last_name: Nouveau nom de l'étudiant
            group_name: Nouveau nom du groupe
            
        Returns:
            True si la mise à jour a réussi, False sinon
        """
        self.connect()
        
        # Vérifier si l'étudiant existe
        self.cursor.execute("SELECT id FROM students WHERE id = ?", (student_id,))
        existing = self.cursor.fetchone()
        
        if not existing:
            self.disconnect()
            return False
        
        # Mettre à jour l'étudiant
        self.cursor.execute(
            "UPDATE students SET first_name = ?, last_name = ?, group_name = ? WHERE id = ?",
            (first_name, last_name, group_name, student_id)
        )
        
        self.connection.commit()
        self.disconnect()
        
        return True

    def delete_student(self, student_id):
        """
        Supprime un étudiant de la base de données.
        
        Args:
            student_id: ID de l'étudiant à supprimer
            
        Returns:
            True si la suppression a réussi, False sinon
        """
        self.connect()
        
        # Vérifier si l'étudiant existe
        self.cursor.execute("SELECT id FROM students WHERE id = ?", (student_id,))
        existing = self.cursor.fetchone()
        
        if not existing:
            self.disconnect()
            return False
        
        # Supprimer les présences associées à cet étudiant
        self.cursor.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))
        
        # Supprimer l'étudiant
        self.cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        
        self.connection.commit()
        self.disconnect()
        
        return True

    # Méthodes pour les présences
    def get_all_attendance(self):
        """
        Récupère tous les enregistrements de présence de la base de données.
        
        Returns:
            DataFrame pandas contenant tous les enregistrements de présence
        """
        self.connect()
        query = """
        SELECT a.*, c.name as course_name, s.first_name, s.last_name
        FROM attendance a
        JOIN courses c ON a.course_id = c.id
        JOIN students s ON a.student_id = s.id
        ORDER BY a.date DESC, a.time DESC
        """
        df = pd.read_sql_query(query, self.connection)
        self.disconnect()
        return df

    def get_attendance_by_course(self, course_id):
        """
        Récupère les enregistrements de présence pour un cours spécifique.
        
        Args:
            course_id: ID du cours
            
        Returns:
            DataFrame pandas contenant les enregistrements de présence pour le cours spécifié
        """
        self.connect()
        query = """
        SELECT a.*, c.name as course_name, s.first_name, s.last_name
        FROM attendance a
        JOIN courses c ON a.course_id = c.id
        JOIN students s ON a.student_id = s.id
        WHERE a.course_id = ?
        ORDER BY a.date DESC, a.time DESC
        """
        df = pd.read_sql_query(query, self.connection, params=(course_id,))
        self.disconnect()
        return df

    def get_attendance_by_student(self, student_id):
        """
        Récupère les enregistrements de présence pour un étudiant spécifique.
        
        Args:
            student_id: ID de l'étudiant
            
        Returns:
            DataFrame pandas contenant les enregistrements de présence pour l'étudiant spécifié
        """
        self.connect()
        query = """
        SELECT a.*, c.name as course_name, s.first_name, s.last_name
        FROM attendance a
        JOIN courses c ON a.course_id = c.id
        JOIN students s ON a.student_id = s.id
        WHERE a.student_id = ?
        ORDER BY a.date DESC, a.time DESC
        """
        df = pd.read_sql_query(query, self.connection, params=(student_id,))
        self.disconnect()
        return df

    def get_attendance_by_date(self, date):
        """
        Récupère les enregistrements de présence pour une date spécifique.
        
        Args:
            date: Date au format YYYY-MM-DD
            
        Returns:
            DataFrame pandas contenant les enregistrements de présence pour la date spécifiée
        """
        self.connect()
        query = """
        SELECT a.*, c.name as course_name, s.first_name, s.last_name
        FROM attendance a
        JOIN courses c ON a.course_id = c.id
        JOIN students s ON a.student_id = s.id
        WHERE a.date = ?
        ORDER BY a.time DESC
        """
        df = pd.read_sql_query(query, self.connection, params=(date,))
        self.disconnect()
        return df

    def add_attendance(self, course_id, student_id, date, status, method="Manuel"):
        """
        Ajoute un nouvel enregistrement de présence à la base de données.
        
        Args:
            course_id: ID du cours
            student_id: ID de l'étudiant
            date: Date de présence au format YYYY-MM-DD
            status: Statut de présence ('present' ou 'absent')
            method: Méthode d'enregistrement
            
        Returns:
            ID de l'enregistrement ajouté ou None si un enregistrement existe déjà
        """
        self.connect()
        
        # Vérifier si un enregistrement existe déjà pour cet étudiant, ce cours et cette date
        self.cursor.execute(
            "SELECT id FROM attendance WHERE course_id = ? AND student_id = ? AND date = ?",
            (course_id, student_id, date)
        )
        existing = self.cursor.fetchone()
        
        if existing:
            self.disconnect()
            return None
        
        # Générer un ID unique
        attendance_id = f"A{str(uuid.uuid4())[:6].upper()}"
        time = datetime.now().strftime("%H:%M:%S")
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Insérer le nouvel enregistrement
        self.cursor.execute(
            """
            INSERT INTO attendance 
            (id, course_id, student_id, date, time, status, method, created_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (attendance_id, course_id, student_id, date, time, status, method, created_at)
        )
        
        self.connection.commit()
        self.disconnect()
        
        return attendance_id

    def update_attendance(self, attendance_id, status, method=None):
        """
        Met à jour un enregistrement de présence existant.
        
        Args:
            attendance_id: ID de l'enregistrement à mettre à jour
            status: Nouveau statut de présence ('present' ou 'absent')
            method: Nouvelle méthode d'enregistrement (optionnel)
            
        Returns:
            True si la mise à jour a réussi, False sinon
        """
        self.connect()
        
        # Vérifier si l'enregistrement existe
        self.cursor.execute("SELECT id FROM attendance WHERE id = ?", (attendance_id,))
        existing = self.cursor.fetchone()
        
        if not existing:
            self.disconnect()
            return False
        
        # Préparer la requête de mise à jour
        updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if method:
            self.cursor.execute(
                "UPDATE attendance SET status = ?, method = ?, updated_at = ? WHERE id = ?",
                (status, method, updated_at, attendance_id)
            )
        else:
            self.cursor.execute(
                "UPDATE attendance SET status = ?, updated_at = ? WHERE id = ?",
                (status, updated_at, attendance_id)
            )
        
        self.connection.commit()
        self.disconnect()
        
        return True

    def delete_attendance(self, attendance_id):
        """
        Supprime un enregistrement de présence de la base de données.
        
        Args:
            attendance_id: ID de l'enregistrement à supprimer
            
        Returns:
            True si la suppression a réussi, False sinon
        """
        self.connect()
        
        # Vérifier si l'enregistrement existe
        self.cursor.execute("SELECT id FROM attendance WHERE id = ?", (attendance_id,))
        existing = self.cursor.fetchone()
        
        if not existing:
            self.disconnect()
            return False
        
        # Supprimer l'enregistrement
        self.cursor.execute("DELETE FROM attendance WHERE id = ?", (attendance_id,))
        
        self.connection.commit()
        self.disconnect()
        
        return True

    def delete_attendance_by_filter(self, course_id=None, student_id=None, date=None):
        """
        Supprime des enregistrements de présence selon des critères de filtrage.
        
        Args:
            course_id: ID du cours (optionnel)
            student_id: ID de l'étudiant (optionnel)
            date: Date au format YYYY-MM-DD (optionnel)
            
        Returns:
            Nombre d'enregistrements supprimés
        """
        self.connect()
        
        # Construire la requête de suppression en fonction des filtres fournis
        query = "DELETE FROM attendance WHERE 1=1"
        params = []
        
        if course_id:
            query += " AND course_id = ?"
            params.append(course_id)
        
        if student_id:
            query += " AND student_id = ?"
            params.append(student_id)
        
        if date:
            query += " AND date = ?"
            params.append(date)
        
        # Exécuter la requête
        self.cursor.execute(query, params)
        deleted_count = self.cursor.rowcount
        
        self.connection.commit()
        self.disconnect()
        
        return deleted_count

    # Méthodes pour la migration des données
    def import_courses_from_csv(self, csv_file):
        """
        Importe les cours depuis un fichier CSV.
        
        Args:
            csv_file: Chemin vers le fichier CSV
            
        Returns:
            Nombre de cours importés
        """
        if not os.path.exists(csv_file):
            return 0
        
        # Charger les données du CSV
        df = pd.read_csv(csv_file)
        
        # Vérifier que les colonnes requises sont présentes
        required_columns = ['CourseID', 'CourseName', 'Instructor', 'Group', 'Schedule']
        if not all(col in df.columns for col in required_columns):
            return 0
        
        self.connect()
        
        # Importer chaque cours
        imported_count = 0
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for _, row in df.iterrows():
            # Vérifier si le cours existe déjà
            self.cursor.execute("SELECT id FROM courses WHERE id = ?", (row['CourseID'],))
            existing = self.cursor.fetchone()
            
            if not existing:
                # Insérer le nouveau cours
                self.cursor.execute(
                    "INSERT INTO courses (id, name, instructor, group_name, schedule, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (row['CourseID'], row['CourseName'], row['Instructor'], row['Group'], row['Schedule'], created_at)
                )
                imported_count += 1
        
        self.connection.commit()
        self.disconnect()
        
        return imported_count

    def import_students_from_csv(self, csv_file):
        """
        Importe les étudiants depuis un fichier CSV.
        
        Args:
            csv_file: Chemin vers le fichier CSV
            
        Returns:
            Nombre d'étudiants importés
        """
        if not os.path.exists(csv_file):
            return 0
        
        # Charger les données du CSV
        df = pd.read_csv(csv_file)
        
        # Vérifier que les colonnes requises sont présentes
        required_columns = ['StudentID', 'FirstName', 'LastName', 'Group']
        if not all(col in df.columns for col in required_columns):
            return 0
        
        self.connect()
        
        # Importer chaque étudiant
        imported_count = 0
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for _, row in df.iterrows():
            # Vérifier si l'étudiant existe déjà
            self.cursor.execute("SELECT id FROM students WHERE id = ?", (row['StudentID'],))
            existing = self.cursor.fetchone()
            
            if not existing:
                # Insérer le nouvel étudiant
                self.cursor.execute(
                    "INSERT INTO students (id, first_name, last_name, group_name, created_at) VALUES (?, ?, ?, ?, ?)",
                    (row['StudentID'], row['FirstName'], row['LastName'], row['Group'], created_at)
                )
                imported_count += 1
        
        self.connection.commit()
        self.disconnect()
        
        return imported_count

    def import_attendance_from_directory(self, attendance_dir):
        """
        Importe les enregistrements de présence depuis un répertoire contenant des fichiers CSV.
        
        Args:
            attendance_dir: Chemin vers le répertoire contenant les fichiers CSV
            
        Returns:
            Nombre d'enregistrements importés
        """
        if not os.path.exists(attendance_dir):
            return 0
        
        self.connect()
        
        # Importer chaque fichier CSV
        imported_count = 0
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for filename in os.listdir(attendance_dir):
            if filename.endswith('.csv'):
                # Extraire l'ID du cours et la date du nom de fichier
                parts = filename.split('_')
                if len(parts) >= 2:
                    course_id = parts[0]
                    date = parts[1].replace('.csv', '')
                    
                    file_path = os.path.join(attendance_dir, filename)
                    
                    try:
                        # Charger les données du fichier
                        df = pd.read_csv(file_path)
                        
                        # Vérifier que les colonnes requises sont présentes
                        if 'StudentID' not in df.columns:
                            continue
                        
                        for _, row in df.iterrows():
                            student_id = row['StudentID']
                            
                            # Déterminer le statut
                            status = 'present'
                            if 'Status' in row:
                                status = row['Status']
                            
                            # Déterminer la méthode
                            method = 'Manuel'
                            if 'Method' in row:
                                method = row['Method']
                            
                            # Déterminer l'heure
                            time = datetime.now().strftime("%H:%M:%S")
                            if 'Time' in row:
                                time = row['Time']
                            
                            # Vérifier si l'enregistrement existe déjà
                            self.cursor.execute(
                                "SELECT id FROM attendance WHERE course_id = ? AND student_id = ? AND date = ?",
                                (course_id, student_id, date)
                            )
                            existing = self.cursor.fetchone()
                            
                            if not existing:
                                # Générer un ID unique
                                attendance_id = f"A{str(uuid.uuid4())[:6].upper()}"
                                
                                # Insérer le nouvel enregistrement
                                self.cursor.execute(
                                    """
                                    INSERT INTO attendance 
                                    (id, course_id, student_id, date, time, status, method, created_at) 
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                    """,
                                    (attendance_id, course_id, student_id, date, time, status, method, created_at)
                                )
                                imported_count += 1
                    except Exception as e:
                        print(f"Erreur lors de l'importation du fichier {filename}: {e}")
        
        self.connection.commit()
        self.disconnect()
        
        return imported_count
