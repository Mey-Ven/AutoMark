#!/usr/bin/env python3
import sys
import re

# Lire le fichier admin_home.py
with open('src/dashboard/pages/admin_home.py', 'r') as file:
    content = file.read()

# Définir le nouveau code pour les actions rapides
new_code = """    # Section des actions rapides
    st.subheader("Actions rapides")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            "<div style='background-color: var(--card-background); padding: 1rem; border-radius: 10px; height: 120px;'>"
            "<h4>Gestion des utilisateurs</h4>"
            "<p>Ajouter, modifier ou supprimer des utilisateurs du système.</p>"
            "</div>",
            unsafe_allow_html=True
        )
        # Utiliser un bouton qui modifie directement la variable de session
        if st.button("Gérer les utilisateurs", key="btn_users", use_container_width=True):
            # Définir la page à afficher dans la session
            st.session_state["admin_action"] = "Administration"
    
    with col2:
        st.markdown(
            "<div style='background-color: var(--card-background); padding: 1rem; border-radius: 10px; height: 120px;'>"
            "<h4>Gestion des cours</h4>"
            "<p>Ajouter, modifier ou supprimer des cours du système.</p>"
            "</div>",
            unsafe_allow_html=True
        )
        if st.button("Gérer les cours", key="btn_courses", use_container_width=True):
            # Définir la page à afficher dans la session
            st.session_state["admin_action"] = "Administration"
    
    with col3:
        st.markdown(
            "<div style='background-color: var(--card-background); padding: 1rem; border-radius: 10px; height: 120px;'>"
            "<h4>Rapports système</h4>"
            "<p>Générer des rapports sur l'utilisation du système.</p>"
            "</div>",
            unsafe_allow_html=True
        )
        if st.button("Générer des rapports", key="btn_reports", use_container_width=True):
            # Définir la page à afficher dans la session
            st.session_state["admin_action"] = "Rapports"
    
    # Vérifier si une action a été demandée
    if "admin_action" in st.session_state:
        # Récupérer l'action demandée
        action = st.session_state["admin_action"]
        # Supprimer l'action de la session pour éviter les redirections en boucle
        del st.session_state["admin_action"]
        # Mettre à jour la sélection de page
        st.session_state.page_selection = action
        # Recharger la page
        st.experimental_rerun()"""

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
