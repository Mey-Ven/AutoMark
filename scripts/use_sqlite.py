#!/usr/bin/env python3
"""
Script pour utiliser l'adaptateur SQLite dans l'application AutoMark.
"""

import os
import sys
import argparse
import logging
import streamlit as st

# Ajouter le répertoire courant au chemin de recherche des modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.database.data_adapter import SQLiteDataAdapter

def main():
    """Fonction principale du script."""
    # Configuration du logging
    logging.basicConfig(level=logging.INFO, 
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger = logging.getLogger("use_sqlite")
    
    # Analyser les arguments de ligne de commande
    parser = argparse.ArgumentParser(description="Utiliser l'adaptateur SQLite dans l'application AutoMark")
    parser.add_argument("--data-dir", default="data", help="Chemin vers le répertoire de données")
    parser.add_argument("--init-db", action="store_true", help="Initialiser la base de données")
    args = parser.parse_args()
    
    # Chemin absolu vers le répertoire de données
    data_dir = os.path.abspath(args.data_dir)
    if not os.path.exists(data_dir):
        logger.error(f"Le répertoire de données n'existe pas: {data_dir}")
        return 1
    
    # Initialiser la base de données si demandé
    if args.init_db:
        logger.info(f"Initialisation de la base de données dans le répertoire: {data_dir}")
        
        # Importer le module d'initialisation de la base de données
        from src.database.db_manager import DBManager
        
        # Initialiser le gestionnaire de base de données
        db_manager = DBManager(data_dir)
        
        # Initialiser la structure de la base de données
        if not db_manager.initialize_database():
            logger.error("Échec de l'initialisation de la structure de la base de données")
            return 1
        
        # Migrer les données depuis les fichiers CSV
        if not db_manager.migrate_data_from_csv():
            logger.error("Échec de la migration des données depuis les fichiers CSV")
            return 1
        
        logger.info("Initialisation de la base de données terminée avec succès")
    
    # Créer l'adaptateur de données SQLite
    logger.info("Création de l'adaptateur de données SQLite")
    adapter = SQLiteDataAdapter(data_dir)
    
    # Lancer l'application avec l'adaptateur SQLite
    logger.info("Lancement de l'application avec l'adaptateur SQLite")
    
    # Définir l'adaptateur comme chargeur de données global pour Streamlit
    st.session_state["data_loader"] = adapter
    
    # Exécuter le script dashboard.py
    os.system("streamlit run dashboard.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
