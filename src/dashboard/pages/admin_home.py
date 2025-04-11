import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

def render_admin_home(data_loader, auth_manager):
    """
    Affiche la page d'accueil pour les administrateurs.
    
    Args:
        data_loader: Chargeur de données
        auth_manager: Gestionnaire d'authentification
    """
    user = st.session_state.user
    
    st.title(f"Tableau de bord administrateur")
    
    # Afficher un message de bienvenue personnalisé
    st.markdown(f"""
    <div style='background-color: var(--card-background); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
        <h3>Bienvenue, {user['first_name']} {user['last_name']}</h3>
        <p>Dernière connexion : {user['last_login']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Créer un tableau de bord avec des statistiques
    col1, col2, col3 = st.columns(3)
    
    # Statistiques générales
    with col1:
        st.metric(
            label="Nombre d'étudiants",
            value=len(data_loader.get_students()),
            delta=None
        )
    
    with col2:
        st.metric(
            label="Nombre de cours",
            value=len(data_loader.get_courses()),
            delta=None
        )
    
    with col3:
        # Nombre d'utilisateurs par rôle
        users_by_role = auth_manager.users_df['Role'].value_counts()
        st.metric(
            label="Nombre d'utilisateurs",
            value=len(auth_manager.users_df),
            delta=None
        )
    
    # Graphiques et statistiques avancées
    st.subheader("Statistiques du système")
    
    tab1, tab2, tab3 = st.tabs(["Présences", "Utilisateurs", "Activité"])
    
    with tab1:
        # Statistiques de présence
        attendance_stats = data_loader.get_attendance_stats()
        
        # Présences par jour
        if attendance_stats['attendance_by_date']:
            dates = list(attendance_stats['attendance_by_date'].keys())
            counts = list(attendance_stats['attendance_by_date'].values())
            
            df_dates = pd.DataFrame({
                'Date': dates,
                'Présences': counts
            })
            
            fig = px.bar(
                df_dates, 
                x='Date', 
                y='Présences',
                title="Présences par jour",
                labels={'Date': 'Date', 'Présences': 'Nombre de présences'},
                color_discrete_sequence=['#FF4B4B']
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune donnée de présence disponible.")
        
        # Présences par cours
        if attendance_stats['attendance_by_course']:
            courses = list(attendance_stats['attendance_by_course'].keys())
            counts = list(attendance_stats['attendance_by_course'].values())
            
            # Récupérer les noms des cours
            course_names = {}
            for course_id in courses:
                course_info = data_loader.courses_df[data_loader.courses_df['CourseID'] == course_id]
                if len(course_info) > 0:
                    course_names[course_id] = course_info.iloc[0]['CourseName']
                else:
                    course_names[course_id] = course_id
            
            course_labels = [course_names.get(course_id, course_id) for course_id in courses]
            
            df_courses = pd.DataFrame({
                'Cours': course_labels,
                'Présences': counts
            })
            
            fig = px.pie(
                df_courses, 
                values='Présences', 
                names='Cours',
                title="Répartition des présences par cours",
                color_discrete_sequence=px.colors.sequential.Reds
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Statistiques des utilisateurs
        users_by_role = auth_manager.users_df['Role'].value_counts().reset_index()
        users_by_role.columns = ['Rôle', 'Nombre']
        
        # Traduire les rôles en français
        role_translations = {
            'admin': 'Administrateur',
            'teacher': 'Enseignant',
            'student': 'Étudiant'
        }
        
        users_by_role['Rôle'] = users_by_role['Rôle'].map(lambda x: role_translations.get(x, x))
        
        fig = px.pie(
            users_by_role, 
            values='Nombre', 
            names='Rôle',
            title="Répartition des utilisateurs par rôle",
            color_discrete_sequence=px.colors.sequential.Reds
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Liste des dernières connexions
        st.subheader("Dernières connexions")
        
        # Convertir les dates de dernière connexion en datetime
        auth_manager.users_df['LastLogin'] = pd.to_datetime(auth_manager.users_df['LastLogin'])
        
        # Trier par date de dernière connexion (plus récente en premier)
        recent_logins = auth_manager.users_df.sort_values('LastLogin', ascending=False).head(5)
        
        # Créer un DataFrame pour l'affichage
        login_data = []
        for _, user in recent_logins.iterrows():
            login_data.append({
                'Utilisateur': f"{user['FirstName']} {user['LastName']}",
                'Rôle': role_translations.get(user['Role'], user['Role']),
                'Dernière connexion': user['LastLogin'].strftime("%Y-%m-%d %H:%M:%S")
            })
        
        login_df = pd.DataFrame(login_data)
        st.dataframe(login_df, use_container_width=True)
    
    with tab3:
        # Simuler des données d'activité du système
        st.subheader("Activité du système")
        
        # Générer des données fictives pour l'activité du système
        today = datetime.now()
        dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
        dates.reverse()  # Du plus ancien au plus récent
        
        # Simuler différents types d'activités
        logins = [5, 8, 12, 7, 10, 15, 9]
        attendance_records = [20, 35, 42, 30, 38, 45, 25]
        face_recognitions = [15, 30, 38, 25, 32, 40, 20]
        
        # Créer un DataFrame pour le graphique
        activity_data = []
        for i, date in enumerate(dates):
            activity_data.append({'Date': date, 'Type': 'Connexions', 'Nombre': logins[i]})
            activity_data.append({'Date': date, 'Type': 'Enregistrements de présence', 'Nombre': attendance_records[i]})
            activity_data.append({'Date': date, 'Type': 'Reconnaissances faciales', 'Nombre': face_recognitions[i]})
        
        activity_df = pd.DataFrame(activity_data)
        
        fig = px.line(
            activity_df, 
            x='Date', 
            y='Nombre', 
            color='Type',
            title="Activité du système sur les 7 derniers jours",
            labels={'Date': 'Date', 'Nombre': 'Nombre d\'activités', 'Type': 'Type d\'activité'},
            color_discrete_sequence=['#FF4B4B', '#FF9E9E', '#FFD1D1']
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Section des actions rapides
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
        )

    # Section des notifications
    st.subheader("Notifications récentes")
    
    # Simuler quelques notifications
    notifications = [
        {"type": "info", "message": "Mise à jour du système effectuée avec succès.", "date": "Aujourd'hui, 10:30"},
        {"type": "warning", "message": "5 étudiants n'ont pas de photos d'entraînement pour la reconnaissance faciale.", "date": "Hier, 15:45"},
        {"type": "success", "message": "Nouvel utilisateur 'prof_leroy' créé avec succès.", "date": "2023-09-10, 09:15"}
    ]
    
    for notif in notifications:
        icon = "ℹ️" if notif["type"] == "info" else "⚠️" if notif["type"] == "warning" else "✅"
        st.markdown(f"""
        <div style='background-color: var(--card-background); padding: 0.5rem 1rem; border-radius: 5px; margin-bottom: 0.5rem; display: flex; align-items: center;'>
            <div style='font-size: 1.5rem; margin-right: 1rem;'>{icon}</div>
            <div style='flex-grow: 1;'>
                <p style='margin: 0;'>{notif["message"]}</p>
                <p style='margin: 0; font-size: 0.8rem; color: gray;'>{notif["date"]}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
