#!/usr/bin/env python3
"""
Script d'initialisation de la base de données SQLite pour AutoMark.
Ce script initialise la structure de la base de données et migre les données depuis les fichiers CSV.
"""

import os
import sys
import argparse
import logging

# Ajouter le répertoire parent au chemin de recherche des modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.database.db_manager import DBManager

def main():
    """Fonction principale du script."""
    # Configuration du logging
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('init_db')
    
    # Analyser les arguments de ligne de commande
    parser = argparse.ArgumentParser(description='Initialiser la base de données SQLite pour AutoMark')
    parser.add_argument('--data-dir', default='data', help='Chemin vers le répertoire de données')
    args = parser.parse_args()
    
    # Chemin absolu vers le répertoire de données
    data_dir = os.path.abspath(args.data_dir)
    if not os.path.exists(data_dir):
        logger.error(f"Le répertoire de données n'existe pas: {data_dir}")
        return 1
    
    logger.info(f"Initialisation de la base de données dans le répertoire: {data_dir}")
    
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
    return 0

if __name__ == '__main__':
    sys.exit(main())
