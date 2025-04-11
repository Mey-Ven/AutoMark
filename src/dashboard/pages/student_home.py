import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

def render_student_home(data_loader, auth_manager):
    """
    Affiche la page d'accueil pour les étudiants.
    
    Args:
        data_loader: Chargeur de données
        auth_manager: Gestionnaire d'authentification
    """
    user = st.session_state.user
    
    st.title(f"Tableau de bord étudiant")
    
    # Récupérer l'ID étudiant associé à cet utilisateur
    student_id = None
    if 'entities' in user and 'student' in user['entities']:
        student_id = user['entities']['student'][0] if user['entities']['student'] else None
    
    # Si aucun ID étudiant n'est associé, afficher un message d'erreur
    if not student_id:
        st.error("Aucun profil étudiant n'est associé à votre compte. Veuillez contacter l'administrateur.")
        return
    
    # Récupérer les informations de l'étudiant
    student_info = data_loader.students_df[data_loader.students_df['StudentID'] == student_id]
    if len(student_info) == 0:
        st.error(f"Impossible de trouver les informations de l'étudiant (ID: {student_id}).")
        return
    
    student = student_info.iloc[0]
    group = student['Group']
    
    # Afficher un message de bienvenue personnalisé
    st.markdown(f"""
    <div style='background-color: var(--card-background); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
        <h3>Bienvenue, {user['first_name']} {user['last_name']}</h3>
        <p>Groupe: {group}</p>
        <p>Dernière connexion: {user['last_login']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Récupérer les cours de l'étudiant (basés sur son groupe)
    student_courses = data_loader.courses_df[data_loader.courses_df['Group'] == group]
    
    # Récupérer les présences de l'étudiant
    student_attendance = data_loader.get_attendance_by_student(student_id)
    
    # Calculer le taux de présence global
    attendance_rate = data_loader.get_student_attendance_rate(student_id) * 100
    
    # Afficher les statistiques de présence
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Taux de présence global",
            value=f"{attendance_rate:.1f}%",
            delta=None
        )
    
    with col2:
        st.metric(
            label="Cours suivis",
            value=len(student_courses),
            delta=None
        )
    
    with col3:
        # Calculer le nombre de séances manquées
        total_sessions = len(student_courses) * 10  # Supposons 10 séances par cours
        attended_sessions = len(student_attendance)
        missed_sessions = total_sessions - attended_sessions
        
        st.metric(
            label="Séances manquées",
            value=missed_sessions,
            delta=None
        )
    
    # Afficher un graphique des présences par cours
    st.subheader("Taux de présence par cours")
    
    # Préparer les données pour le graphique
    course_data = []
    
    for _, course in student_courses.iterrows():
        course_id = course['CourseID']
        course_name = course['CourseName']
        
        # Calculer le taux de présence pour ce cours
        course_attendance = student_attendance[student_attendance['CourseID'] == course_id]
        course_attendance_rate = len(course_attendance) / 10 * 100  # Supposons 10 séances par cours
        
        course_data.append({
            'Cours': course_name,
            'Taux de présence': course_attendance_rate
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
    
    # Afficher l'emploi du temps de la semaine
    st.subheader("Emploi du temps de la semaine")
    
    # Créer un tableau pour l'emploi du temps
    weekdays = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
    timetable = pd.DataFrame(index=weekdays, columns=["Matin", "Après-midi"])
    
    # Remplir l'emploi du temps avec les cours de l'étudiant
    for _, course in student_courses.iterrows():
        schedule_parts = course['Schedule'].split(' ')
        day = schedule_parts[0]
        time = schedule_parts[1]
        
        # Déterminer si c'est le matin ou l'après-midi
        hour = int(time.split(':')[0])
        period = "Matin" if hour < 12 else "Après-midi"
        
        # Ajouter le cours à l'emploi du temps
        if day in weekdays:
            if pd.isna(timetable.loc[day, period]) or timetable.loc[day, period] == "":
                timetable.loc[day, period] = course['CourseName']
            else:
                timetable.loc[day, period] += f", {course['CourseName']}"
    
    # Remplacer les valeurs NaN par des chaînes vides
    timetable = timetable.fillna("")
    
    # Styliser le tableau
    st.dataframe(
        timetable,
        use_container_width=True,
        height=250
    )
    
    # Afficher les prochains cours
    st.subheader("Prochains cours")
    
    # Déterminer le jour de la semaine actuel
    today = datetime.now()
    weekday = today.weekday()
    current_weekday = weekdays[weekday] if weekday < 5 else None
    
    upcoming_courses = []
    
    for _, course in student_courses.iterrows():
        # Extraire le jour et l'heure du cours
        schedule_parts = course['Schedule'].split(' ')
        course_day = schedule_parts[0]
        course_time = schedule_parts[1]
        
        # Déterminer le jour de la semaine du cours (0 = Lundi, 4 = Vendredi)
        course_weekday = weekdays.index(course_day) if course_day in weekdays else None
        
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
                'course_id': course['CourseID'],
                'course_name': course['CourseName'],
                'date': next_course_date.strftime("%Y-%m-%d"),
                'day': weekdays[next_course_date.weekday()],
                'time': course_time,
                'days_until': days_until_course
            })
    
    # Trier les cours par date (le plus proche en premier)
    upcoming_courses.sort(key=lambda x: x['days_until'])
    
    if upcoming_courses:
        # Afficher les 3 prochains cours
        for i, course in enumerate(upcoming_courses[:3]):
            # Déterminer le style en fonction de la proximité du cours
            if course['days_until'] == 0:
                border_color = "#FF4B4B"  # Rouge pour aujourd'hui
                label = "Aujourd'hui"
            elif course['days_until'] == 1:
                border_color = "#FFA500"  # Orange pour demain
                label = "Demain"
            else:
                border_color = "#4CAF50"  # Vert pour les jours suivants
                label = f"Dans {course['days_until']} jours"
            
            # Vérifier si l'étudiant a déjà été marqué présent pour ce cours
            is_present = False
            if course['days_until'] == 0:  # Seulement pour les cours d'aujourd'hui
                course_attendance = student_attendance[
                    (student_attendance['CourseID'] == course['course_id']) & 
                    (student_attendance['Date'] == today.strftime("%Y-%m-%d"))
                ]
                is_present = len(course_attendance) > 0
            
            # Ajouter un badge de présence si applicable
            presence_badge = ""
            if course['days_until'] == 0:
                if is_present:
                    presence_badge = "<span style='background-color: #4CAF50; color: white; padding: 0.2rem 0.4rem; border-radius: 3px; margin-left: 0.5rem;'>Présent</span>"
                else:
                    presence_badge = "<span style='background-color: #FF4B4B; color: white; padding: 0.2rem 0.4rem; border-radius: 3px; margin-left: 0.5rem;'>Non marqué</span>"
            
            st.markdown(f"""
            <div style='background-color: var(--card-background); padding: 1rem; border-radius: 10px; margin-bottom: 0.5rem; border-left: 4px solid {border_color};'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <h4 style='margin: 0;'>{course['course_name']} {presence_badge}</h4>
                        <p style='margin: 0;'>{course['day']} {course['time']}</p>
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
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style='background-color: var(--card-background); padding: 1rem; border-radius: 10px; height: 150px;'>
            <h4>Voir mon historique de présence</h4>
            <p>Consulter l'historique complet de vos présences.</p>
            <button style='background-color: #FF4B4B; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer;'>Voir l'historique</button>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background-color: var(--card-background); padding: 1rem; border-radius: 10px; height: 150px;'>
            <h4>Télécharger mon attestation</h4>
            <p>Générer une attestation de présence pour vos cours.</p>
            <button style='background-color: #FF4B4B; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer;'>Télécharger</button>
        </div>
        """, unsafe_allow_html=True)
    
    # Afficher un graphique de l'évolution de la présence
    st.subheader("Évolution de votre présence")
    
    # Simuler des données d'évolution de présence
    today = datetime.now()
    dates = [(today - timedelta(days=i*7)).strftime("%Y-%m-%d") for i in range(10)]
    dates.reverse()  # Du plus ancien au plus récent
    
    attendance_rates = [65, 70, 68, 75, 80, 78, 85, 82, 88, 90]  # Simuler une amélioration progressive
    
    evolution_df = pd.DataFrame({
        'Date': dates,
        'Taux de présence': attendance_rates
    })
    
    fig = px.line(
        evolution_df, 
        x='Date', 
        y='Taux de présence',
        title="Évolution de votre taux de présence",
        labels={'Date': 'Date', 'Taux de présence': 'Taux de présence (%)'},
        color_discrete_sequence=['#FF4B4B']
    )
    
    fig.update_layout(yaxis_range=[0, 100])
    
    st.plotly_chart(fig, use_container_width=True)
