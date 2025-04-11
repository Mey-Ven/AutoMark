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
        # Simuler un clic sur le bouton de navigation "Administration"
        if st.button("Gérer les utilisateurs", key="btn_users_action", use_container_width=True):
            # Cliquer directement sur le bouton de navigation "Administration"
            js = f'''
            <script>
                function simulateClick() {{
                    // Trouver le bouton "Administration" dans la barre latérale
                    const buttons = window.parent.document.querySelectorAll('[data-testid="stSidebar"] button');
                    for (let button of buttons) {{
                        if (button.innerText.includes("Administration")) {{
                            button.click();
                            break;
                        }}
                    }}
                }}
                // Exécuter après le chargement de la page
                window.addEventListener('load', simulateClick);
            </script>
            '''
            st.components.v1.html(js, height=0)
    
    with col2:
        st.markdown(
            "<div style='background-color: var(--card-background); padding: 1rem; border-radius: 10px; height: 120px;'>"
            "<h4>Gestion des cours</h4>"
            "<p>Ajouter, modifier ou supprimer des cours du système.</p>"
            "</div>",
            unsafe_allow_html=True
        )
        # Simuler un clic sur le bouton de navigation "Administration"
        if st.button("Gérer les cours", key="btn_courses_action", use_container_width=True):
            # Cliquer directement sur le bouton de navigation "Administration"
            js = f'''
            <script>
                function simulateClick() {{
                    // Trouver le bouton "Administration" dans la barre latérale
                    const buttons = window.parent.document.querySelectorAll('[data-testid="stSidebar"] button');
                    for (let button of buttons) {{
                        if (button.innerText.includes("Administration")) {{
                            button.click();
                            break;
                        }}
                    }}
                }}
                // Exécuter après le chargement de la page
                window.addEventListener('load', simulateClick);
            </script>
            '''
            st.components.v1.html(js, height=0)
    
    with col3:
        st.markdown(
            "<div style='background-color: var(--card-background); padding: 1rem; border-radius: 10px; height: 120px;'>"
            "<h4>Rapports système</h4>"
            "<p>Générer des rapports sur l'utilisation du système.</p>"
            "</div>",
            unsafe_allow_html=True
        )
        # Simuler un clic sur le bouton de navigation "Rapports"
        if st.button("Générer des rapports", key="btn_reports_action", use_container_width=True):
            # Cliquer directement sur le bouton de navigation "Rapports"
            js = f'''
            <script>
                function simulateClick() {{
                    // Trouver le bouton "Rapports" dans la barre latérale
                    const buttons = window.parent.document.querySelectorAll('[data-testid="stSidebar"] button');
                    for (let button of buttons) {{
                        if (button.innerText.includes("Rapports")) {{
                            button.click();
                            break;
                        }}
                    }}
                }}
                // Exécuter après le chargement de la page
                window.addEventListener('load', simulateClick);
            </script>
            '''
            st.components.v1.html(js, height=0)"""

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
