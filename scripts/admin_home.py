#!/usr/bin/env python3
import sys
import re

# Lire le fichier admin_home.py
with open('src/dashboard/pages/admin_home.py', 'r') as file:
    content = file.read()

# Définir le nouveau code pour les actions rapides
new_code = """    # Section des actions rapides
    st.subheader("Actions rapides")
    
    # Créer une ligne pour les actions rapides
    action_cols = st.columns(3)
    
    # Action 1: Gestion des utilisateurs
    with action_cols[0]:
        st.markdown(
            "<div style='background-color: var(--card-background); padding: 1rem; border-radius: 10px;'>"
            "<h4>Gestion des utilisateurs</h4>"
            "<p>Ajouter, modifier ou supprimer des utilisateurs du système.</p>"
            "<p style='color: #FF4B4B;'><strong>Comment y accéder :</strong></p>"
            "<p>Cliquez sur <strong>Administration</strong> dans le menu de navigation à gauche.</p>"
            "</div>",
            unsafe_allow_html=True
        )
    
    # Action 2: Gestion des cours
    with action_cols[1]:
        st.markdown(
            "<div style='background-color: var(--card-background); padding: 1rem; border-radius: 10px;'>"
            "<h4>Gestion des cours</h4>"
            "<p>Ajouter, modifier ou supprimer des cours du système.</p>"
            "<p style='color: #FF4B4B;'><strong>Comment y accéder :</strong></p>"
            "<p>Cliquez sur <strong>Administration</strong> dans le menu de navigation à gauche.</p>"
            "</div>",
            unsafe_allow_html=True
        )
    
    # Action 3: Rapports système
    with action_cols[2]:
        st.markdown(
            "<div style='background-color: var(--card-background); padding: 1rem; border-radius: 10px;'>"
            "<h4>Rapports système</h4>"
            "<p>Générer des rapports sur l'utilisation du système.</p>"
            "<p style='color: #FF4B4B;'><strong>Comment y accéder :</strong></p>"
            "<p>Cliquez sur <strong>Rapports</strong> dans le menu de navigation à gauche.</p>"
            "</div>",
            unsafe_allow_html=True
        )"""

# Utiliser une expression régulière pour trouver et remplacer la section des actions rapides
pattern = r'    # Section des actions rapides\s+st\.subheader\("Actions rapides"\).*?st\.subheader\("Notifications récentes"\)'
match = re.search(pattern, content, re.DOTALL)

if match:
    # Remplacer la section trouvée par le nouveau code
    new_content = content.replace(match.group(0), new_code + '\n\n    # Section des notifications\n    st.subheader("Notifications récentes")')
    
    # Écrire le contenu modifié dans le fichier
    with open('src/dashboard/pages/admin_home.py', 'w') as file:
        file.write(new_content)
    print("Le fichier admin_home.py a été corrigé avec succès.")
else:
    print("La section à remplacer n'a pas été trouvée. Vérifiez le fichier admin_home.py.")
    sys.exit(1)
