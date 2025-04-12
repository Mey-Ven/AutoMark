#!/usr/bin/env python3
import sys

# Lire le fichier dashboard.py
with open('dashboard.py', 'r') as file:
    content = file.read()

# Remplacer le code problématique
old_code = """# Si aucun bouton n'est cliqué, utiliser la page d'accueil par défaut
if selection is None:
    selection = "Accueil\""""

new_code = """# Si aucun bouton n'est cliqué, utiliser la première page du menu comme page par défaut
if selection is None:
    # Sélectionner la première page du dictionnaire en fonction du rôle
    selection = list(pages.keys())[0]"""

# Effectuer le remplacement
if old_code in content:
    content = content.replace(old_code, new_code)
    # Écrire le contenu modifié dans le fichier
    with open('dashboard.py', 'w') as file:
        file.write(content)
    print("Le fichier dashboard.py a été corrigé avec succès.")
else:
    print("Le code à remplacer n'a pas été trouvé. Vérifiez le fichier dashboard.py.")
    sys.exit(1)
