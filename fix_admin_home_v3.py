#!/usr/bin/env python3
import sys
import re

# Lire le fichier admin_home.py
with open('src/dashboard/pages/admin_home.py', 'r') as file:
    content = file.read()

# Remplacer st.experimental_rerun() par st.rerun()
content = content.replace('st.experimental_rerun()', 'st.rerun()')

# Écrire le contenu modifié dans le fichier
with open('src/dashboard/pages/admin_home.py', 'w') as file:
    file.write(content)
print("Le fichier admin_home.py a été corrigé avec succès.")
