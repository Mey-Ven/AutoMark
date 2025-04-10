import plotly.io as pio
import plotly.graph_objects as go

# Configuration française pour Plotly
fr_layout = dict(
    font=dict(family="Arial, sans-serif"),
    title=dict(font=dict(family="Arial, sans-serif")),
    xaxis=dict(
        title=dict(font=dict(family="Arial, sans-serif")),
        tickfont=dict(family="Arial, sans-serif")
    ),
    yaxis=dict(
        title=dict(font=dict(family="Arial, sans-serif")),
        tickfont=dict(family="Arial, sans-serif")
    ),
    legend=dict(
        title=dict(font=dict(family="Arial, sans-serif")),
        font=dict(family="Arial, sans-serif")
    ),
    coloraxis_colorbar=dict(
        title=dict(font=dict(family="Arial, sans-serif")),
        tickfont=dict(family="Arial, sans-serif")
    )
)

# Créer un template personnalisé pour les graphiques en français
pio.templates["fr_template"] = go.layout.Template(layout=fr_layout)

# Définir le template par défaut
pio.templates.default = "fr_template"

# Dictionnaire de traduction pour les éléments communs
translations = {
    "Count": "Nombre",
    "Date": "Date",
    "Course": "Cours",
    "Student": "Étudiant",
    "Attendance": "Présence",
    "Group": "Groupe",
    "Value": "Valeur",
    "Heatmap": "Carte de chaleur",
    "Bar Chart": "Graphique à barres",
    "Pie Chart": "Graphique circulaire",
    "Line Chart": "Graphique linéaire"
}

def apply_french_layout(fig):
    """
    Applique une mise en page française à une figure Plotly.
    
    Args:
        fig: Figure Plotly à modifier.
        
    Returns:
        Figure Plotly modifiée.
    """
    # Appliquer le template français
    fig.update_layout(template="fr_template")
    
    # Traduire les titres des axes si nécessaire
    if fig.layout.xaxis and fig.layout.xaxis.title and fig.layout.xaxis.title.text in translations:
        fig.update_xaxes(title_text=translations[fig.layout.xaxis.title.text])
    
    if fig.layout.yaxis and fig.layout.yaxis.title and fig.layout.yaxis.title.text in translations:
        fig.update_yaxes(title_text=translations[fig.layout.yaxis.title.text])
    
    # Traduire le titre de la barre de couleur si nécessaire
    if fig.layout.coloraxis and fig.layout.coloraxis.colorbar and fig.layout.coloraxis.colorbar.title and fig.layout.coloraxis.colorbar.title.text in translations:
        fig.update_coloraxes(colorbar_title_text=translations[fig.layout.coloraxis.colorbar.title.text])
    
    return fig
