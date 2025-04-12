# AutoMark - Système intelligent de reconnaissance faciale pour la gestion automatisée de la présence des étudiants

## Description

AutoMark est un système de reconnaissance faciale en temps réel capable de détecter automatiquement les visages des étudiants lorsqu'ils entrent en classe. Une fois détectés, leurs présences sont enregistrées automatiquement dans un fichier CSV dédié à chaque matière (cours).

Le système inclut également un dashboard interactif pour les administrateurs, professeurs ou responsables pédagogiques, permettant de :
- Afficher les statistiques de présence par matière, par classe et par groupe
- Voir, pour chaque étudiant, son nombre total d'absences et les séances manquées
- Générer des rapports automatisés et exportables (ex : CSV, PDF)
- Avoir un système de filtrage par date, matière, groupe, etc.

## Fonctionnalités principales

1. Reconnaissance faciale automatique à l'entrée de la classe
2. Enregistrement automatique de la présence dans un fichier CSV par matière
3. Détection des absences par comparaison avec la liste des inscrits
4. Dashboard de suivi :
   - Vue globale des présences
   - Filtres par matière, groupe, étudiant
   - Affichage du taux de présence
   - Nom de l'étudiant + nombre de séances manquées
5. Gestion multi-groupes et multi-classes
6. Gestion complète des cours, étudiants et présences via l'interface d'administration
7. Enregistrement des présences ET des absences dans les fichiers d'assiduité
8. Module avancé de reconnaissance faciale
9. Système d'authentification avec différents rôles (administrateur, enseignant, étudiant)
10. Interfaces spécifiques adaptées à chaque type d'utilisateur

## Installation

1. Cloner le dépôt :
```
git clone https://github.com/votre-utilisateur/AutoMark.git
cd AutoMark
```

2. Installer les dépendances :
```
pip install -r requirements.txt
```

## Utilisation



# Mise à jour importante : Migration vers SQLite



# Mise à jour pour la compatibilité avec les versions récentes de Streamlit

## Compatibilité avec Streamlit

L'application a été mise à jour pour être compatible avec les versions récentes de Streamlit. Les modifications suivantes ont été apportées :

1. Remplacement de `st.experimental_rerun()` par `st.rerun()` :
   - La fonction `st.experimental_rerun()` est obsolète dans les versions récentes de Streamlit et a été remplacée par `st.rerun()`.
   - Toutes les occurrences de `st.experimental_rerun()` ont été remplacées par `st.rerun()` dans les fichiers suivants :
     - `dashboard_sqlite.py`
     - `src/dashboard/pages/admin_sqlite.py`

### Version minimale de Streamlit

L'application nécessite désormais Streamlit 1.10.0 ou supérieur. Pour vérifier votre version de Streamlit, exécutez la commande suivante :

```bash
streamlit --version
```

Si vous avez une version antérieure, mettez à jour Streamlit avec la commande suivante :

```bash
pip install --upgrade streamlit
```


## Nouvelle version avec base de données SQLite

Une nouvelle version de l'application a été développée pour utiliser une base de données SQLite au lieu des fichiers CSV. Cette version offre de meilleures performances, une meilleure intégrité des données et une interface d'administration améliorée.

### Comment exécuter la nouvelle version

Pour exécuter la version SQLite de l'application, utilisez la commande suivante :

```bash
streamlit run dashboard_sqlite.py
```

### Avantages de la version SQLite

1. **Meilleures performances** : Les bases de données sont optimisées pour les opérations de lecture et d'écriture, ce qui améliore les performances de l'application.

2. **Meilleure intégrité des données** : Les bases de données offrent des fonctionnalités comme les contraintes d'intégrité référentielle, ce qui garantit que les données sont cohérentes.

3. **Requêtes plus flexibles** : Les bases de données permettent d'effectuer des requêtes complexes pour récupérer des données spécifiques.

4. **Transactions** : Les bases de données prennent en charge les transactions, ce qui garantit que les opérations sont atomiques.

5. **Évolutivité** : Les bases de données sont conçues pour gérer de grandes quantités de données, ce qui permet à l'application de s'adapter à la croissance.

6. **Sécurité** : Les bases de données offrent des fonctionnalités de sécurité comme l'authentification et l'autorisation.

### Structure de la base de données SQLite

La base de données SQLite contient trois tables principales :

1. **courses** : Stocke les informations sur les cours
   - id : Identifiant unique du cours
   - name : Nom du cours
   - instructor : Nom de l'enseignant
   - group_name : Nom du groupe
   - schedule : Horaire du cours
   - created_at : Date de création

2. **students** : Stocke les informations sur les étudiants
   - id : Identifiant unique de l'étudiant
   - first_name : Prénom de l'étudiant
   - last_name : Nom de l'étudiant
   - group_name : Nom du groupe
   - created_at : Date de création

3. **attendance** : Stocke les enregistrements de présence
   - id : Identifiant unique de l'enregistrement
   - course_id : Identifiant du cours
   - student_id : Identifiant de l'étudiant
   - date : Date de présence
   - time : Heure de présence
   - status : Statut de présence ('present' ou 'absent')
   - method : Méthode d'enregistrement
   - created_at : Date de création
   - updated_at : Date de mise à jour

### Initialisation de la base de données

Pour initialiser la base de données SQLite avec les données existantes des fichiers CSV, exécutez le script suivant :

```bash
python init_database.py
```

Ce script crée la base de données SQLite et importe les données des fichiers CSV.

### Modifications apportées

1. **Nouvelle interface d'administration** : L'interface d'administration a été simplifiée et améliorée pour faciliter la gestion des cours, des étudiants et des présences.

2. **Nouveau chargeur de données** : Un nouveau chargeur de données a été créé pour utiliser la base de données SQLite au lieu des fichiers CSV.

3. **Nouveau gestionnaire de base de données** : Un nouveau gestionnaire de base de données a été créé pour interagir avec la base de données SQLite.

4. **Nouveau fichier principal** : Un nouveau fichier principal (`dashboard_sqlite.py`) a été créé pour utiliser la base de données SQLite.

### Fichiers obsolètes

Les fichiers suivants sont désormais obsolètes et ne sont conservés que pour référence :

- `dashboard.py` : Version originale qui utilise les fichiers CSV
- `src/dashboard/pages/admin.py` : Interface d'administration originale
- `src/dashboard/pages/admin_improved.py` : Interface d'administration améliorée pour les fichiers CSV

### Nouveaux fichiers

Les fichiers suivants ont été ajoutés pour la version SQLite :

- `dashboard_sqlite.py` : Point d'entrée principal de l'application (version SQLite)
- `src/dashboard/pages/admin_sqlite.py` : Interface d'administration pour la version SQLite
- `src/database/db_manager_v2.py` : Gestionnaire de base de données SQLite
- `src/dashboard/utils/db_data_loader.py` : Chargeur de données pour la version SQLite
- `init_database.py` : Script d'initialisation de la base de données SQLite

## Utilisation de l'application

### Lancement de l'application

Pour lancer la version SQLite de l'application (recommandée) :

```bash
streamlit run dashboard_sqlite.py
```

Pour lancer la version CSV de l'application (obsolète) :

```bash
streamlit run dashboard.py
```

### Authentification

L'application utilise un système d'authentification simple avec trois types d'utilisateurs :

1. **Administrateur** : Accès complet à toutes les fonctionnalités
   - Nom d'utilisateur : admin
   - Mot de passe : admin

2. **Enseignant** : Accès aux fonctionnalités de prise de présence et de rapports
   - Nom d'utilisateur : teacher
   - Mot de passe : teacher

3. **Étudiant** : Accès aux informations de présence personnelles
   - Nom d'utilisateur : student
   - Mot de passe : student



# Mise à jour du système d'authentification

## Nouveau module d'authentification pour SQLite

Un nouveau module d'authentification a été créé pour la version SQLite de l'application. Ce module fournit des fonctions simples pour l'authentification des utilisateurs.

### Utilisateurs par défaut

L'application est préconfigurée avec trois utilisateurs par défaut :

1. **Administrateur** :
   - Nom d'utilisateur : admin
   - Mot de passe : admin
   - Rôle : admin

2. **Enseignant** :
   - Nom d'utilisateur : teacher
   - Mot de passe : teacher
   - Rôle : teacher

3. **Étudiant** :
   - Nom d'utilisateur : student
   - Mot de passe : student
   - Rôle : student

### Fonctionnalités d'authentification

Le module d'authentification fournit les fonctionnalités suivantes :

1. **Authentification** : Vérifie les identifiants de l'utilisateur et stocke les informations utilisateur dans la session.

2. **Vérification de l'authentification** : Vérifie si l'utilisateur est authentifié.

3. **Récupération du rôle** : Récupère le rôle de l'utilisateur authentifié.

4. **Déconnexion** : Déconnecte l'utilisateur en effaçant les données de session.

### Comment se connecter

1. Lancez l'application :
   ```bash
   streamlit run dashboard_sqlite.py
   ```

2. Entrez vos identifiants dans le formulaire de connexion :
   - Nom d'utilisateur : admin, teacher ou student
   - Mot de passe : admin, teacher ou student (respectivement)

3. Cliquez sur "Se connecter".

4. Une fois connecté, vous serez redirigé vers la page d'accueil correspondant à votre rôle.

### Accès aux fonctionnalités selon le rôle

1. **Administrateur** :
   - Accès à toutes les fonctionnalités
   - Interface d'administration pour gérer les cours, les étudiants et les présences
   - Module de reconnaissance faciale
   - Rapports

2. **Enseignant** :
   - Accès aux fonctionnalités de prise de présence
   - Module de reconnaissance faciale
   - Rapports

3. **Étudiant** :
   - Accès aux informations de présence personnelles


### Interface d'administration

L'interface d'administration permet de :

- Gérer les cours (ajouter, modifier, supprimer)
- Gérer les étudiants (ajouter, modifier, supprimer)
- Gérer les présences (ajouter, supprimer)

Pour accéder à l'interface d'administration, connectez-vous avec un compte administrateur et cliquez sur "Administration" dans le menu de navigation.


### Lancement de l'application

Pour lancer le dashboard complet :
```
streamlit run dashboard.py
```

### Module de reconnaissance faciale

Pour utiliser le module de reconnaissance faciale, accédez à l'onglet "Reconnaissance Faciale" dans le dashboard.

## Structure du projet

```
AutoMark/
├── data/
│   ├── photos/  # Dossier contenant les photos des étudiants
│   ├── training_photos/  # Dossier contenant les images d'entraînement pour la reconnaissance faciale
│   ├── attendance/  # Dossier contenant les fichiers CSV de présence par cours et par date
│   ├── courses.csv  # Informations sur les cours
│   ├── students.csv  # Informations sur les étudiants
│   ├── users.csv  # Informations sur les utilisateurs (authentification)
│   ├── user_roles.csv  # Définition des rôles et permissions
│   ├── user_mappings.csv  # Associations entre utilisateurs et entités (cours, étudiants)
│   ├── automark.db  # Base de données SQLite pour le stockage des données
│   ├── face_encodings.pkl  # Encodages des visages pour la reconnaissance faciale
│   └── face_model.yml  # Modèle entraîné pour la reconnaissance faciale
├── src/
│   ├── __init__.py
│   ├── auth/  # Module d'authentification et de gestion des utilisateurs
│   │   ├── __init__.py
│   │   └── auth_manager.py  # Gestionnaire d'authentification
│   ├── dashboard/  # Module pour le tableau de bord
│   │   ├── pages/  # Pages du dashboard
│   │   │   ├── home.py  # Page d'accueil générale
│   │   │   ├── login.py  # Page de connexion
│   │   │   ├── admin_home.py  # Tableau de bord administrateur
│   │   │   ├── teacher_home.py  # Tableau de bord enseignant
│   │   │   ├── student_home.py  # Tableau de bord étudiant
│   │   │   ├── attendance_stats.py  # Statistiques de présence
│   │   │   ├── student_details.py  # Détails des étudiants
│   │   │   ├── reports.py  # Rapports
│   │   │   ├── admin.py  # Administration
│   │   │   └── face_recognition.py  # Interface de reconnaissance faciale
│   │   └── utils/  # Utilitaires pour le dashboard
│   ├── face_recognition_module/  # Module de reconnaissance faciale
│   │   ├── __init__.py
│   │   └── face_recognition_module.py  # Implémentation du module
│   └── utils/  # Utilitaires généraux
├── scripts/  # Scripts utilitaires
│   ├── __init__.py
│   ├── admin_home.py  # Script pour le tableau de bord administrateur
│   ├── fix_dashboard.py  # Script pour corriger des problèmes du dashboard
│   └── use_sqlite.py  # Script pour la gestion de la base de données SQLite
├── tests/  # Tests unitaires et d'intégration
│   ├── __init__.py
│   ├── test_adapter.py  # Tests pour les adaptateurs de données
│   ├── test_cv2_face.py  # Tests pour la détection de visage avec OpenCV
│   ├── test_face_module.py  # Tests pour le module de reconnaissance faciale
│   └── test_face_module_attributes.py  # Tests pour les attributs du module de reconnaissance faciale
├── static/  # Fichiers statiques (images, CSS, JS)
├── dashboard.py  # Point d'entrée pour le dashboard
├── main.py  # Point d'entrée principal de l'application
├── requirements.txt  # Dépendances du projet
├── DOCUMENTATION.md  # Documentation détaillée
└── README.md  # Documentation du projet
```

## Technologies utilisées

- Python avec OpenCV pour la détection et reconnaissance faciale
- Pandas pour l'analyse et la manipulation des données
- Streamlit pour créer le dashboard interactif
- Plotly pour les visualisations avancées
- SQLite pour la gestion de base de données
- JSON et CSV pour le stockage et l'échange de données

## Fonctionnalités détaillées

### 1. Module d'administration

L'interface d'administration permet de gérer :

- **Cours** : Ajout, modification et suppression des cours avec leurs informations (nom, code, horaire, description)
- **Étudiants** : Gestion complète des étudiants (informations personnelles, inscription aux cours, photos)
- **Présences** : Enregistrement manuel ou automatique des présences, avec distinction entre présents et absents

### 2. Gestion des présences/absences

- Enregistrement des étudiants présents ET absents dans les fichiers d'assiduité
- Génération de feuilles de présence complètes pour tous les étudiants d'un cours
- Exportation des données de présence en CSV avec filtrage par cours et période

### 3. Module de reconnaissance faciale avancée

- **Entraînement avec plusieurs photos** : Possibilité d'utiliser plusieurs photos par étudiant pour améliorer la précision
- **Interface d'entraînement** : Upload de photos, visualisation des images existantes, suppression d'images
- **Détection de liveness** : Vérification que la personne est réellement présente (pas une photo)
- **Reconnaissance par lots** : Capacité de reconnaître plusieurs étudiants dans une seule image
- **Paramètres configurables** : Ajustement des seuils de confiance, choix des algorithmes de détection

### 4. Dashboard interactif

- Interface utilisateur intuitive en français
- Navigation simplifiée avec menu latéral
- Visualisations interactives des données de présence
- Filtres dynamiques pour l'analyse des données
- Mode sombre/clair pour une meilleure expérience utilisateur

### 5. Système d'authentification et contrôle d'accès

- Authentification sécurisée avec gestion des sessions utilisateur
- Trois types de profils utilisateurs avec interfaces dédiées :
  - **Administrateur** : Accès complet à toutes les fonctionnalités, gestion des utilisateurs, statistiques système
  - **Enseignant** : Gestion des cours enseignés, prise de présence, suivi des étudiants à risque
  - **Étudiant** : Consultation de son emploi du temps, historique de présence, statistiques personnelles
- Contrôle d'accès basé sur les rôles et permissions
- Tableau de bord personnalisé selon le profil de l'utilisateur connecté
- Déconnexion sécurisée

#### Création des comptes utilisateurs

Le système permet de créer trois types de comptes utilisateurs :

1. **Compte Administrateur** :
   - Accédez à l'interface d'administration via le menu "Administration"
   - Cliquez sur "Gestion des utilisateurs" puis "Ajouter un utilisateur"
   - Remplissez le formulaire en sélectionnant le rôle "Administrateur"
   - Définissez un nom d'utilisateur et un mot de passe sécurisé
   - Attribuez les permissions appropriées
   - Cliquez sur "Enregistrer"

2. **Compte Enseignant** :
   - Accédez à l'interface d'administration via le menu "Administration"
   - Cliquez sur "Gestion des utilisateurs" puis "Ajouter un utilisateur"
   - Remplissez le formulaire en sélectionnant le rôle "Enseignant"
   - Définissez un nom d'utilisateur et un mot de passe
   - Associez l'enseignant aux cours qu'il enseigne via la section "Cours associés"
   - Cliquez sur "Enregistrer"

3. **Compte Étudiant** :
   - Accédez à l'interface d'administration via le menu "Administration"
   - Cliquez sur "Gestion des utilisateurs" puis "Ajouter un utilisateur"
   - Remplissez le formulaire en sélectionnant le rôle "Étudiant"
   - Définissez un nom d'utilisateur et un mot de passe
   - Associez l'étudiant à son profil étudiant existant via la section "Profil étudiant"
   - Sélectionnez les cours auxquels l'étudiant est inscrit
   - Cliquez sur "Enregistrer"

**Note** : Seuls les utilisateurs avec le rôle "Administrateur" peuvent créer de nouveaux comptes. Le système est préconfiguré avec un compte administrateur par défaut (nom d'utilisateur : "admin", mot de passe : "admin"). Il est fortement recommandé de modifier ce mot de passe après la première connexion.

## Licence

Ce projet est sous licence MIT.
