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
│   ├── face_encodings.pkl  # Encodages des visages pour la reconnaissance faciale
│   └── face_model.yml  # Modèle entraîné pour la reconnaissance faciale
├── src/
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
├── dashboard.py  # Point d'entrée pour le dashboard
└── README.md  # Documentation du projet
```

## Technologies utilisées

- Python avec OpenCV pour la détection et reconnaissance faciale
- Pandas pour l'analyse et la manipulation des données
- Streamlit pour créer le dashboard interactif
- Plotly pour les visualisations avancées
- JSON pour le stockage des données
- SQLite/MySQL pour la gestion de base de données (optionnel)

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
