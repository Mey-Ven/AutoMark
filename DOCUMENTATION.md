# Documentation du projet AutoMark

Ce document explique la structure et le fonctionnement de chaque fichier du projet AutoMark.

## Structure générale du projet

Le projet AutoMark est organisé en plusieurs modules :

- **Module principal** : Point d'entrée de l'application
- **Module d'authentification** : Gestion des utilisateurs et des permissions
- **Module de tableau de bord** : Interface utilisateur et visualisations
- **Module de base de données** : Gestion des données avec SQLite
- **Module de reconnaissance faciale** : Détection et reconnaissance des visages

## Fichiers principaux

### Fichiers racine

| Fichier | Description |
|---------|-------------|
| `dashboard.py` | Point d'entrée principal de l'application. Lance l'interface Streamlit et gère la navigation entre les différentes pages. |
| `main.py` | Script alternatif pour lancer l'application (moins utilisé). |
| `use_sqlite.py` | Script pour utiliser l'adaptateur SQLite dans l'application. Initialise la base de données si nécessaire. |
| `requirements.txt` | Liste des dépendances Python nécessaires au fonctionnement de l'application. |
| `README.md` | Documentation générale du projet. |
| `DOCUMENTATION.md` | Ce fichier, qui explique en détail chaque fichier du projet. |

### Répertoire `src`

Le répertoire `src` contient le code source de l'application, organisé en sous-modules.

#### Module d'authentification (`src/auth`)

| Fichier | Description |
|---------|-------------|
| `__init__.py` | Initialise le module d'authentification et expose les classes principales. |
| `auth_manager.py` | Classe `AuthManager` qui gère l'authentification des utilisateurs, les sessions et les permissions. |

#### Module de tableau de bord (`src/dashboard`)

| Fichier | Description |
|---------|-------------|
| `__init__.py` | Initialise le module de tableau de bord. |
| `app.py` | Configuration générale de l'application Streamlit. |

##### Pages du tableau de bord (`src/dashboard/pages`)

| Fichier | Description |
|---------|-------------|
| `__init__.py` | Initialise le module des pages. |
| `login.py` | Page de connexion avec formulaire d'authentification. |
| `home.py` | Page d'accueil générale. |
| `admin_home.py` | Tableau de bord pour les administrateurs. |
| `teacher_home.py` | Tableau de bord pour les enseignants. |
| `student_home.py` | Tableau de bord pour les étudiants. |
| `attendance_stats.py` | Page de statistiques de présence. |
| `student_details.py` | Page de détails des étudiants. |
| `reports.py` | Page de génération de rapports. |
| `admin.py` | Page d'administration générale. |
| `face_recognition.py` | Interface pour la reconnaissance faciale. |
| `user_management.py` | Page de gestion des utilisateurs (ajout, modification, suppression). |

##### Utilitaires du tableau de bord (`src/dashboard/utils`)

| Fichier | Description |
|---------|-------------|
| `__init__.py` | Initialise le module des utilitaires. |
| `data_loader.py` | Classe pour charger les données depuis les fichiers CSV. |
| `plotly_config.py` | Configuration des graphiques Plotly. |
| `visualizations.py` | Fonctions pour créer des visualisations de données. |
| `menu_style.css` | Styles CSS pour le menu de navigation. |
| `style.css` | Styles CSS généraux pour l'application. |

#### Module de base de données (`src/database`)

| Fichier | Description |
|---------|-------------|
| `__init__.py` | Initialise le module de base de données. |
| `db_manager.py` | Classe `DBManager` qui gère la connexion à la base de données SQLite et les opérations CRUD. |
| `data_adapter.py` | Classe `SQLiteDataAdapter` qui fournit une interface compatible avec le chargeur de données existant. |
| `init_db.py` | Script pour initialiser la structure de la base de données et migrer les données depuis les fichiers CSV. |

#### Module de reconnaissance faciale (`src/face_recognition_module`)

| Fichier | Description |
|---------|-------------|
| `__init__.py` | Initialise le module de reconnaissance faciale. |
| `face_recognition_module.py` | Classe principale pour la reconnaissance faciale. |
| `face_detector.py` | Classe pour détecter les visages dans une image. |
| `attendance_recorder.py` | Classe pour enregistrer les présences à partir des résultats de reconnaissance faciale. |

#### Utilitaires généraux (`src/utils`)

| Fichier | Description |
|---------|-------------|
| `__init__.py` | Initialise le module des utilitaires généraux. |
| `file_operations.py` | Fonctions pour manipuler les fichiers (lecture, écriture, etc.). |

### Répertoire `data`

Le répertoire `data` contient les données de l'application.

| Fichier/Dossier | Description |
|-----------------|-------------|
| `automark.db` | Base de données SQLite contenant toutes les données de l'application. |
| `students.csv` | Fichier CSV contenant les informations sur les étudiants (utilisé pour l'importation). |
| `courses.csv` | Fichier CSV contenant les informations sur les cours (utilisé pour l'importation). |
| `users.csv` | Fichier CSV contenant les informations sur les utilisateurs (utilisé pour l'importation). |
| `user_roles.csv` | Fichier CSV définissant les rôles et permissions (utilisé pour l'importation). |
| `user_mappings.csv` | Fichier CSV associant les utilisateurs aux entités (utilisé pour l'importation). |
| `attendance/` | Dossier contenant les fichiers CSV de présence par cours et par date (utilisé pour l'importation). |

## Flux de données

1. L'utilisateur se connecte via la page de connexion (`login.py`).
2. Selon son rôle, il est redirigé vers le tableau de bord approprié (`admin_home.py`, `teacher_home.py` ou `student_home.py`).
3. Les données sont chargées depuis la base de données SQLite via l'adaptateur (`data_adapter.py`).
4. Les pages du tableau de bord affichent les données et permettent d'interagir avec elles.
5. Les modifications sont enregistrées dans la base de données via le gestionnaire de base de données (`db_manager.py`).

## Fonctionnalités principales

### Authentification et gestion des utilisateurs

- **Connexion** : Les utilisateurs se connectent avec leur nom d'utilisateur et mot de passe.
- **Gestion des utilisateurs** : Les administrateurs peuvent ajouter, modifier et supprimer des utilisateurs.
- **Contrôle d'accès** : Les fonctionnalités sont accessibles selon le rôle de l'utilisateur.

### Gestion des cours et des étudiants

- **Gestion des cours** : Ajout, modification et suppression des cours.
- **Gestion des étudiants** : Ajout, modification et suppression des étudiants.
- **Association** : Association des étudiants aux cours et des enseignants aux cours.

### Prise de présence

- **Prise de présence manuelle** : Enregistrement manuel des présences.
- **Reconnaissance faciale** : Prise de présence automatique par reconnaissance faciale.
- **Historique** : Consultation de l'historique des présences.

### Statistiques et rapports

- **Statistiques de présence** : Visualisation des taux de présence par cours, par étudiant, etc.
- **Rapports** : Génération de rapports détaillés sur les présences.
- **Exportation** : Exportation des données au format CSV.

## Base de données SQLite

La base de données SQLite (`data/automark.db`) contient les tables suivantes :

- **students** : Informations sur les étudiants (ID, nom, prénom, email, groupe, photo).
- **courses** : Informations sur les cours (ID, nom, enseignant, groupe, horaire).
- **attendance** : Enregistrements de présence (ID étudiant, ID cours, date, heure, statut).
- **users** : Comptes utilisateurs (nom d'utilisateur, mot de passe hashé, rôle, informations personnelles).

## Utilisation de l'application

### Lancement de l'application

Pour lancer l'application avec la base de données SQLite :

```bash
python use_sqlite.py --init-db
```

Pour lancer l'application sans réinitialiser la base de données :

```bash
python use_sqlite.py
```

Ou directement avec Streamlit :

```bash
streamlit run dashboard.py
```

### Connexion

- **Administrateur** : Nom d'utilisateur `admin`, mot de passe `admin`
- **Enseignant** : Nom d'utilisateur `prof_dupont`, mot de passe `123`
- **Étudiant** : Nom d'utilisateur `jean_dupont`, mot de passe `123`

## Personnalisation et extension

### Ajout d'une nouvelle page

1. Créer un nouveau fichier dans `src/dashboard/pages/`
2. Définir une fonction `render_page(data_loader)` qui affiche la page
3. Ajouter la page au dictionnaire `pages` dans `dashboard.py`

### Modification de la base de données

1. Modifier le schéma dans `src/database/db_manager.py`
2. Mettre à jour les fonctions d'accès aux données dans `src/database/data_adapter.py`
3. Réinitialiser la base de données avec `python use_sqlite.py --init-db`

### Ajout d'une nouvelle fonctionnalité de reconnaissance faciale

1. Ajouter les nouvelles fonctions dans `src/face_recognition_module/`
2. Mettre à jour l'interface dans `src/dashboard/pages/face_recognition.py`
