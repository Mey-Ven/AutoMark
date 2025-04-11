import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

def render_teacher_home(data_loader, auth_manager):
    """
    Affiche la page d'accueil pour les enseignants.
    
    Args:
        data_loader: Chargeur de données
        auth_manager: Gestionnaire d'authentification
    """
    user = st.session_state.user
    
    st.title(f"Tableau de bord enseignant")
    
    # Afficher un message de bienvenue personnalisé
    st.markdown(f"""
    <div style='background-color: var(--card-background); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
        <h3>Bienvenue, {user['first_name']} {user['last_name']}</h3>
        <p>Dernière connexion : {user['last_login']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Récupérer les cours de l'enseignant
    teacher_courses = []
    if 'entities' in user and 'course' in user['entities']:
        course_ids = user['entities']['course']
        for course_id in course_ids:
            course_info = data_loader.courses_df[data_loader.courses_df['CourseID'] == course_id]
            if len(course_info) > 0:
                teacher_courses.append({
                    'id': course_id,
                    'name': course_info.iloc[0]['CourseName'],
                    'group': course_info.iloc[0]['Group'],
                    'schedule': course_info.iloc[0]['Schedule']
                })
    
    # Afficher les statistiques des cours de l'enseignant
    if teacher_courses:
        st.subheader("Vos cours")
        
        # Créer des colonnes pour afficher les métriques des cours
        cols = st.columns(min(3, len(teacher_courses)))
        
        for i, course in enumerate(teacher_courses[:3]):  # Limiter à 3 cours pour l'affichage
            with cols[i % 3]:
                # Calculer le taux de présence pour ce cours
                attendance_rate = data_loader.get_course_attendance_rate(course['id']) * 100
                
                st.metric(
                    label=course['name'],
                    value=f"{attendance_rate:.1f}%",
                    delta=None,
                    help=f"Groupe: {course['group']}, Horaire: {course['schedule']}"
                )
        
        # Si l'enseignant a plus de 3 cours, afficher un bouton pour voir tous les cours
        if len(teacher_courses) > 3:
            st.markdown("<div style='text-align: center;'><a href='#' style='color: var(--text-color);'>Voir tous les cours</a></div>", unsafe_allow_html=True)
        
        # Afficher un graphique des présences pour les cours de l'enseignant
        st.subheader("Taux de présence par cours")
        
        # Préparer les données pour le graphique
        course_data = []
        for course in teacher_courses:
            attendance_rate = data_loader.get_course_attendance_rate(course['id']) * 100
            course_data.append({
                'Cours': course['name'],
                'Taux de présence': attendance_rate
            })
        
        course_df = pd.DataFrame(course_data)
        
        fig = px.bar(
            course_df, 
            x='Cours', 
            y='Taux de présence',
            title="Taux de présence par cours",
            labels={'Cours': 'Cours', 'Taux de présence': 'Taux de présence (%)'},
            color_discrete_sequence=['#FF4B4B'],
            text_auto='.1f'
        )
        
        fig.update_layout(yaxis_range=[0, 100])
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Vous n'avez pas encore de cours assignés.")
    
    # Afficher les prochains cours
    st.subheader("Prochains cours")
    
    # Simuler des données pour les prochains cours
    today = datetime.now()
    weekday = today.weekday()
    
    # Mapping des jours de la semaine en français
    weekday_map = {
        0: "Lundi",
        1: "Mardi",
        2: "Mercredi",
        3: "Jeudi",
        4: "Vendredi",
        5: "Samedi",
        6: "Dimanche"
    }
    
    upcoming_courses = []
    
    for course in teacher_courses:
        # Extraire le jour et l'heure du cours
        schedule_parts = course['schedule'].split(' ')
        course_day = schedule_parts[0]
        course_time = schedule_parts[1]
        
        # Déterminer le jour de la semaine du cours
        course_weekday = None
        for day_num, day_name in weekday_map.items():
            if course_day.lower() == day_name.lower():
                course_weekday = day_num
                break
        
        if course_weekday is not None:
            # Calculer le nombre de jours jusqu'au prochain cours
            days_until_course = (course_weekday - weekday) % 7
            
            # Si le cours est aujourd'hui, vérifier si l'heure est passée
            if days_until_course == 0:
                course_hour = int(course_time.split(':')[0])
                if course_hour < today.hour:
                    days_until_course = 7  # Le cours est déjà passé aujourd'hui, prendre celui de la semaine prochaine
            
            # Calculer la date du prochain cours
            next_course_date = today + timedelta(days=days_until_course)
            
            upcoming_courses.append({
                'course': course,
                'date': next_course_date.strftime("%Y-%m-%d"),
                'day': weekday_map[next_course_date.weekday()],
                'time': course_time,
                'days_until': days_until_course
            })
    
    # Trier les cours par date (le plus proche en premier)
    upcoming_courses.sort(key=lambda x: x['days_until'])
    
    if upcoming_courses:
        # Afficher les 3 prochains cours
        for i, course_info in enumerate(upcoming_courses[:3]):
            course = course_info['course']
            
            # Déterminer le style en fonction de la proximité du cours
            if course_info['days_until'] == 0:
                border_color = "#FF4B4B"  # Rouge pour aujourd'hui
                label = "Aujourd'hui"
            elif course_info['days_until'] == 1:
                border_color = "#FFA500"  # Orange pour demain
                label = "Demain"
            else:
                border_color = "#4CAF50"  # Vert pour les jours suivants
                label = f"Dans {course_info['days_until']} jours"
            
            st.markdown(f"""
            <div style='background-color: var(--card-background); padding: 1rem; border-radius: 10px; margin-bottom: 0.5rem; border-left: 4px solid {border_color};'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <h4 style='margin: 0;'>{course['name']}</h4>
                        <p style='margin: 0;'>Groupe: {course['group']}</p>
                        <p style='margin: 0;'>{course_info['day']} {course_info['time']}</p>
                    </div>
                    <div style='background-color: {border_color}; color: white; padding: 0.3rem 0.6rem; border-radius: 5px;'>
                        {label}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Aucun cours à venir.")
    
    # Section des actions rapides
    st.subheader("Actions rapides")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='background-color: var(--card-background); padding: 1rem; border-radius: 10px; height: 150px;'>
            <h4>Prendre les présences</h4>
            <p>Enregistrer les présences pour un cours.</p>
            <button style='background-color: #FF4B4B; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer;'>Prendre les présences</button>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background-color: var(--card-background); padding: 1rem; border-radius: 10px; height: 150px;'>
            <h4>Reconnaissance faciale</h4>
            <p>Utiliser la reconnaissance faciale pour l'identification.</p>
            <button style='background-color: #FF4B4B; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer;'>Reconnaissance faciale</button>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background-color: var(--card-background); padding: 1rem; border-radius: 10px; height: 150px;'>
            <h4>Rapports de présence</h4>
            <p>Générer des rapports de présence pour vos cours.</p>
            <button style='background-color: #FF4B4B; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer;'>Générer des rapports</button>
        </div>
        """, unsafe_allow_html=True)
    
    # Section des étudiants à risque
    st.subheader("Étudiants à risque")
    
    # Simuler des données pour les étudiants à risque
    at_risk_students = []
    
    # Pour chaque cours de l'enseignant, identifier les étudiants avec un faible taux de présence
    for course in teacher_courses:
        course_id = course['id']
        group = course['group']
        
        # Récupérer tous les étudiants du groupe
        group_students = data_loader.students_df[data_loader.students_df['Group'] == group]
        
        for _, student in group_students.iterrows():
            student_id = student['StudentID']
            
            # Calculer le taux de présence de l'étudiant pour ce cours
            student_attendance = data_loader.attendance_df[
                (data_loader.attendance_df['StudentID'] == student_id) & 
                (data_loader.attendance_df['CourseID'] == course_id)
            ]
            
            # Simuler un taux de présence (dans un système réel, cela serait calculé à partir des données réelles)
            attendance_rate = len(student_attendance) / 10  # Supposons 10 séances au total
            
            if attendance_rate < 0.7:  # Moins de 70% de présence
                at_risk_students.append({
                    'student_id': student_id,
                    'first_name': student['FirstName'],
                    'last_name': student['LastName'],
                    'course_name': course['name'],
                    'attendance_rate': attendance_rate * 100
                })
    
    # Trier les étudiants par taux de présence (le plus faible en premier)
    at_risk_students.sort(key=lambda x: x['attendance_rate'])
    
    if at_risk_students:
        # Afficher les étudiants à risque
        for student in at_risk_students[:5]:  # Limiter à 5 étudiants
            # Déterminer la couleur en fonction du taux de présence
            if student['attendance_rate'] < 50:
                color = "#FF4B4B"  # Rouge pour moins de 50%
            else:
                color = "#FFA500"  # Orange pour 50-70%
            
            st.markdown(f"""
            <div style='background-color: var(--card-background); padding: 0.5rem 1rem; border-radius: 5px; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <p style='margin: 0; font-weight: bold;'>{student['first_name']} {student['last_name']}</p>
                    <p style='margin: 0;'>{student['course_name']}</p>
                </div>
                <div style='background-color: {color}; color: white; padding: 0.3rem 0.6rem; border-radius: 5px;'>
                    {student['attendance_rate']:.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Si plus de 5 étudiants à risque, afficher un lien pour voir tous les étudiants
        if len(at_risk_students) > 5:
            st.markdown(f"<div style='text-align: center;'><a href='#' style='color: var(--text-color);'>Voir tous les étudiants à risque ({len(at_risk_students)})</a></div>", unsafe_allow_html=True)
    else:
        st.success("Aucun étudiant à risque identifié.")
