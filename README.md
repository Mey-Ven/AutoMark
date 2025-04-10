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

### Module de reconnaissance faciale

Pour lancer le système de reconnaissance faciale :
```
python main.py
```

### Dashboard

Pour lancer le dashboard :
```
streamlit run src/dashboard/app.py
```

## Structure du projet

```
AutoMark/
├── data/
│   ├── students/  # Dossier contenant les images des étudiants pour l'entraînement
│   ├── attendance/  # Dossier contenant les fichiers CSV de présence
│   └── courses.csv  # Liste des cours avec leurs informations
├── src/
│   ├── face_recognition_module/  # Module de reconnaissance faciale
│   ├── dashboard/  # Module pour le tableau de bord
│   └── utils/  # Utilitaires généraux
├── requirements.txt  # Dépendances du projet
├── main.py  # Point d'entrée pour le système de reconnaissance faciale
└── README.md  # Documentation du projet
```

## Technologies utilisées

- Python avec OpenCV et face_recognition pour la détection faciale
- Pandas pour gérer les fichiers CSV
- Streamlit pour créer le dashboard
- Plotly pour les visualisations

## Licence

Ce projet est sous licence MIT.
