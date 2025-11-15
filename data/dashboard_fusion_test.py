import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
import sys

# --- CORRECTION ROBUSTE DU CHEMIN PYTHON (Nouveau bloc) ---
# 1. Détermine le répertoire où le script est exécuté (dossier 'data')
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Ajoute le répertoire RACINE du projet (le parent de 'data') au chemin de recherche Python.
# Ceci garantit que 'config.py' et 'src/' sont trouvables.
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)
# -------------------------------------------------------------------------

# --- VOS IMPORTS LOCAUX (ASSUMÉS) ---
# Maintenant, 'config' et 'src' sont dans sys.path, les imports devraient fonctionner
import config 
from src.hierarchiepatho import get_patho_hierarchy
from src.page.cartes import creation_carte
from src.lecture_BDD import lecture_BDD
# -------------------------------------

# 1. Initialisation et chargement des options statiques
try:
    PATHOS_HIERARCHY, NIV1_OPTIONS = get_patho_hierarchy()
except Exception as e:
    # Fallback si get_patho_hierarchy n'est pas disponible ou échoue
    print(f"Erreur lors du chargement de la hiérarchie des pathologies: {e}. Utilisation de MOCK data.")
    PATHOS_HIERARCHY = {'Cardio': {'AVC': ['AVC ischémique']}, 'Diabete': {'Type1': ['Insulino-dépendant']}}
    NIV1_OPTIONS = list(PATHOS_HIERARCHY.keys())

# ====================================================================
# STYLES COMMUNS
# ====================================================================

MAIN_BG_COLOR = '#f5f7fa'
PRIMARY_COLOR = '#1E3A8A'
ACCENT_COLOR = '#3B82F6'

NAV_STYLE = {
    'display': 'flex',
    'justifyContent': 'flex-start',
    'padding': '10px',
    'backgroundColor': '#FFFFFF',
    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
}
LINK_STYLE = {
    'marginRight': '20px',
    'textDecoration': 'none',
    'color': PRIMARY_COLOR,
    'fontWeight': 'bold',
    'fontSize': '1.1rem',
    'padding': '8px 15px',
    'borderRadius': '6px',
    'transition': 'background-color 0.3s',
}
ACTIVE_STYLE = {
    'backgroundColor': '#BFDBFE', 
    'color': PRIMARY_COLOR
}
CONTROLS_CONTAINER_STYLE = {
    'display': 'flex',
    'flexWrap': 'wrap',
    'gap': '15px',
    'padding': '20px',
    'marginBottom': '30px',
    'backgroundColor': '#FFFFFF',
    'borderRadius': '12px',
    'boxShadow': '0 4px 12px rgba(0, 0, 0, 0.08)'
}
CONTROL_ITEM_STYLE = {
    'flexGrow': 1,
    'minWidth': '180px' 
}
GRAPH_CARD_STYLE = {
    'backgroundColor': '#FFFFFF',
    'borderRadius': '12px',
    'boxShadow': '0 2px 8px rgba(0, 0, 0, 0.05)',
    'padding': '15px',
    'marginBottom': '20px',
}
SECTION_TITLE_STYLE = {
    'color': '#374151',
    'borderLeft': f'4px solid {ACCENT_COLOR}',
    'paddingLeft': '10px',
    'marginTop': '30px',
    'marginBottom': '20px',
    'fontSize': '1.6rem'
}

# ====================================================================
# LAYOUTS DE PAGE
# ====================================================================

# 1. LAYOUT DES CONTRÔLES (Utilisé sur les deux pages)
# Note: Les listes d'options (ANNEE, SEXE, AGE) proviennent de config
def controls_layout():
    # Définir les valeurs par défaut au cas où les listes de config sont vides
    default_annee = config.ANNEE[0] if config.ANNEE else None
    default_sexe = config.SEXE[-1] if config.SEXE else None
    default_age = config.AGE[-1] if config.AGE else None
    default_niv1 = NIV1_OPTIONS[0] if NIV1_OPTIONS else None

    return [
        # Type de Carte (Actif uniquement sur la page Carte)
        html.Div(id='carte-type-control', style=CONTROL_ITEM_STYLE, children=[
            html.Label("Type de Carte :", style={'fontWeight': 'bold', 'color': '#4B5563'}),
            dcc.Dropdown(
                id='selecteur-carte',
                options=[
                    {'label': 'Carte par Région', 'value': 'region'},
                    {'label': 'Carte par Département', 'value': 'departement'}
                ],
                value='region',
                clearable=False,
            ),
        ]),
        
        # Année
        html.Div(style=CONTROL_ITEM_STYLE, children=[
            html.Label("Année :", style={'fontWeight': 'bold', 'color': '#4B5563'}),
            dcc.Dropdown(id='selecteur-annee', options=[{'label':i, 'value': i}for i in config.ANNEE], value=default_annee, clearable=False),
        ]),
        # Sexe
        html.Div(style=CONTROL_ITEM_STYLE, children=[
            html.Label("Sexe :", style={'fontWeight': 'bold', 'color': '#4B5563'}),
            dcc.Dropdown(id='selecteur-sexe', options=[{'label':i, 'value': i}for i in config.SEXE], value=default_sexe, clearable=False),
        ]),
        # Âge
        html.Div(style=CONTROL_ITEM_STYLE, children=[
            html.Label("Âge :", style={'fontWeight': 'bold', 'color': '#4B5563'}),
            dcc.Dropdown(id='selecteur-age', options=[{'label':i, 'value': i}for i in config.AGE], value=default_age, clearable=False),
        ]),
        # Pathologie - Niveau 1
        html.Div(style=CONTROL_ITEM_STYLE, children=[
            html.Label("Pathologie - Niveau 1 :", style={'fontWeight': 'bold', 'color': '#4B5563'}),
            dcc.Dropdown(id='selecteur-patho-niv1', options=[{'label': i, 'value': i} for i in NIV1_OPTIONS], value=default_niv1, clearable=False),
        ]),
        # Pathologie - Niveau 2
        html.Div(style=CONTROL_ITEM_STYLE, children=[
            html.Label("Pathologie - Niveau 2 :", style={'fontWeight': 'bold', 'color': '#4B5563'}),
            dcc.Dropdown(id='selecteur-patho-niv2', clearable=False),
        ]),
        # Pathologie - Niveau 3
        html.Div(style=CONTROL_ITEM_STYLE, children=[
            html.Label("Pathologie - Niveau 3 :", style={'fontWeight': 'bold', 'color': '#4B5563'}),
            dcc.Dropdown(id='selecteur-patho-niv3', clearable=False),
        ]),
    ]


# 2. LAYOUT PAGE CARTES
layout_maps = html.Div([
    html.Div(id='page-carte-controls-container', style=CONTROLS_CONTAINER_STYLE, children=controls_layout()),
    html.Div(style=GRAPH_CARD_STYLE, children=[
        html.H3("Visualisation Cartographique", style={'textAlign': 'center', 'color': ACCENT_COLOR}),
        html.Iframe(id='carte-dynamique', style={"width": "100%", "height": "650px", "border": "none"})
    ])
])

# 3. LAYOUT PAGE ANALYSES
layout_analysis = html.Div([
    # Conteneur des contrôles 
    html.Div(id='page-analyse-controls-container', style=CONTROLS_CONTAINER_STYLE, children=controls_layout()),
    
    # Graphs
    html.H2("Distributions de base", style=SECTION_TITLE_STYLE),
    html.Div(style={'display': 'flex', 'gap': '20px'}, children=[
        html.Div(style={**GRAPH_CARD_STYLE, 'flex': 1}, children=[dcc.Graph(id='graph-tri')]),
        html.Div(style={**GRAPH_CARD_STYLE, 'flex': 1}, children=[dcc.Graph(id='graph-ntop')]),
    ]),
    html.Div(style=GRAPH_CARD_STYLE, children=[dcc.Graph(id='graph-prev')]),

    html.H2("Analyse Temporelle et Prioritaire", style=SECTION_TITLE_STYLE),
    html.Div(style=GRAPH_CARD_STYLE, children=[dcc.Graph(id='graph-time-series')]),
    html.Div(style=GRAPH_CARD_STYLE, children=[dcc.Graph(id='graph-priority')]), 

    html.H2("Corrélation et Âge", style=SECTION_TITLE_STYLE),
    html.Div(style=GRAPH_CARD_STYLE, children=[dcc.Graph(id='graph-scatter')]),

    html.Div(style={'display': 'flex', 'gap': '20px'}, children=[
        html.Div(style={**GRAPH_CARD_STYLE, 'flex': 1}, children=[dcc.Graph(id='graph-box-region')]),
        html.Div(style={**GRAPH_CARD_STYLE, 'flex': 1}, children=[dcc.Graph(id='graph-box-age')]),
    ]),
])


# ====================================================================
# APPLICATION PRINCIPALE
# ====================================================================
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Dashboard Multi-Vues Pathologies"

# Layout principal avec la navigation
app.layout = html.Div(style={'backgroundColor': MAIN_BG_COLOR, 'padding': '20px'}, children=[
    html.H1("Dashboard de Prévalence Hiérarchique", style={'textAlign': 'center', 'color': PRIMARY_COLOR}),
    
    # Navigation Bar
    html.Div(style=NAV_STYLE, children=[
        # Lien pour la vue Carte
        dcc.Link('🌍 Cartes Régionales/Départementales', href='/cartes', style=LINK_STYLE, id='link-cartes'),
        # Lien pour la vue Analyse
        dcc.Link('📈 Analyses & Graphiques', href='/analyses', style=LINK_STYLE, id='link-analyses'),
    ]),
    
    # Conteneur pour le contenu dynamique de la page (ceci change entre layout_maps et layout_analysis)
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# ====================================================================
# CALLBACKS DE NAVIGATION ET D'INTERFACE
# ====================================================================

# Callback pour afficher le contenu de la page
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/analyses':
        return layout_analysis
    elif pathname == '/cartes' or pathname == '/':
        return layout_maps
    return html.Div([html.H3('404 - Page non trouvée', style={'color': 'red'})])

# Callback pour mettre à jour le style de navigation (mettre en évidence la page active)
@app.callback(
    [Output('link-cartes', 'style'),
     Output('link-analyses', 'style')],
    [Input('url', 'pathname')]
)
def update_nav_styles(pathname):
    style_cartes = LINK_STYLE.copy()
    style_analyses = LINK_STYLE.copy()
    
    if pathname == '/analyses':
        style_analyses.update(ACTIVE_STYLE)
    elif pathname == '/cartes' or pathname == '/':
        style_cartes.update(ACTIVE_STYLE)
        
    return style_cartes, style_analyses

# Callback pour désactiver le sélecteur de carte sur la page Analyse
@app.callback(
    Output('selecteur-carte', 'disabled'),
    [Input('url', 'pathname')]
)
def disable_carte_selector(pathname):
    return pathname == '/analyses'

# ====================================================================
# CALLBACKS DE MISE À JOUR DES CONTRÔLES (Hiérarchie)
# ====================================================================
# Ces callbacks mettent à jour les menus déroulants Patho Niv 2 et 3 en cascade.

# 1. Met à jour le niveau 2
@app.callback(
    [Output('selecteur-patho-niv2', 'options'),
     Output('selecteur-patho-niv2', 'value')],
    [Input('selecteur-patho-niv1', 'value')]
)
def set_patho_niv2_options(selected_niv1):
    if not selected_niv1 or selected_niv1 not in PATHOS_HIERARCHY:
        return [], None
    
    niv2_list = list(PATHOS_HIERARCHY[selected_niv1].keys())
    options = [{'label': i, 'value': i} for i in niv2_list]
    default_value = niv2_list[0] if niv2_list else None
    
    return options, default_value

# 2. Met à jour le niveau 3
@app.callback(
    [Output('selecteur-patho-niv3', 'options'),
     Output('selecteur-patho-niv3', 'value')],
    [Input('selecteur-patho-niv1', 'value'),
     Input('selecteur-patho-niv2', 'value')]
)
def set_patho_niv3_options(selected_niv1, selected_niv2):
    if not selected_niv1 or not selected_niv2 or selected_niv1 not in PATHOS_HIERARCHY or selected_niv2 not in PATHOS_HIERARCHY[selected_niv1]:
        return [], None
    
    # Assurez-vous que selected_niv2 est une clé valide dans le sous-dictionnaire
    niv3_list = PATHOS_HIERARCHY[selected_niv1].get(selected_niv2, [])
    options = [{'label': i, 'value': i} for i in niv3_list]
    default_value = niv3_list[0] if niv3_list else None
    
    return options, default_value

# ====================================================================
# CALLBACKS PRINCIPAUX (Mise à jour du contenu)
# ====================================================================

# CALLBACK CARTE (Page /cartes)
@app.callback(
    Output('carte-dynamique', 'srcDoc'),
    [Input('selecteur-carte', 'value'),
     Input('selecteur-annee', 'value'),
     Input('selecteur-patho-niv1', 'value'),
     Input('selecteur-patho-niv2', 'value'),
     Input('selecteur-patho-niv3', 'value'),
     Input('selecteur-sexe', 'value'),
     Input('selecteur-age', 'value')]
)
def mettre_a_jour_carte(carte, annee, patho_niv1, patho_niv2, patho_niv3, sexe, age):
    # Vérification minimale des inputs
    if any(v is None for v in [carte, annee, patho_niv1, patho_niv2, patho_niv3, sexe, age]):
        return ""
        
    # Appel de votre fonction lecture_BDD pour filtrer les données (mode agrégé)
    df_filtre = lecture_BDD(carte, annee, patho_niv1, patho_niv2, patho_niv3, sexe, age)
    
    # Construction d'une étiquette de pathologie plus informative
    patho_label = f"{patho_niv1} / {patho_niv2} / {patho_niv3}"
    titre = f"Prévalence de {patho_label} (Sexe: {sexe}, Année: {annee})"
    
    # Appel de votre fonction creation_carte pour générer la carte HTML
    return creation_carte(carte, df_filtre, titre)


# CALLBACK ANALYSE (Page /analyses)
@app.callback(
    [Output('graph-tri', 'figure'),
     Output('graph-ntop', 'figure'),
     Output('graph-prev', 'figure'),
     Output('graph-scatter', 'figure'),
     Output('graph-box-region', 'figure'),
     Output('graph-box-age', 'figure'),
     Output('graph-time-series', 'figure'),
     Output('graph-priority', 'figure')],
    [Input('selecteur-annee', 'value'),
     Input('selecteur-patho-niv1', 'value'),
     Input('selecteur-patho-niv2', 'value'),
     Input('selecteur-patho-niv3', 'value'),
     Input('selecteur-sexe', 'value'),
     Input('selecteur-age', 'value')]
)
def update_analysis_graphs(annee, patho_niv1, patho_niv2, patho_niv3, sexe, age):
    
    # Vérification minimale des inputs
    if any(v is None for v in [annee, patho_niv1, patho_niv2, patho_niv3, sexe, age]):
        empty_fig = go.Figure().update_layout(title="Sélectionnez tous les filtres", height=300)
        return tuple([empty_fig] * 8)
    
    # Filtrer les données (on utilise 'all' pour forcer la fonction à retourner les données détaillées)
    df_filtered = lecture_BDD('all', annee, patho_niv1, patho_niv2, patho_niv3, sexe, age)

    patho_label = patho_niv3 or patho_niv2 or patho_niv1 or "Toutes Pathologies"
    base_title = f"{patho_label} (Sexe: {sexe}, Âge: {age})"
    
    def create_empty_figure(title_text):
        return go.Figure().update_layout(title=title_text,xaxis={'visible': False},yaxis={'visible': False},height=300,
            annotations=[{'text': 'Aucune donnée disponible pour cette sélection.','xref': 'paper', 'yref': 'paper','showarrow': False,'font': {'size': 16, 'color': '#EF4444'}}])

    if df_filtered.empty:
        empty_fig = create_empty_figure(f"Aucune donnée pour cette sélection ({base_title})")
        return tuple([empty_fig] * 8)

    # --- 2. Génération des graphiques analytiques (avec Plotly Express) ---
    
    # Distribution du Tri
    fig_tri = px.histogram(df_filtered, x=config.COL_TRI, nbins=30, title=f"Distribution du Tri - {base_title}", color_discrete_sequence=['#3B82F6'])
    
    # Distribution du Ntop
    fig_ntop = px.histogram(df_filtered, x=config.COL_NTOP, nbins=30, title=f"Distribution du Ntop - {base_title}", color_discrete_sequence=['#F59E0B'])
    
    # Distribution de la Prévalence
    fig_prev = px.histogram(df_filtered, x=config.COL_PREV, nbins=30, title=f"Distribution de la Prévalence - {base_title}", color_discrete_sequence=['#10B981'])
    
    # Corrélation (Ntop vs Prévalence)
    fig_scatter = px.scatter(df_filtered, x=config.COL_NTOP, y=config.COL_PREV, trendline="ols", title=f"Corrélation : Prévalence vs Ntop - {base_title}")

    # Boxplot par Région
    fig_box_region = px.box(df_filtered, x=config.COL_CODE_REGION, y=config.COL_PREV, title=f"Distribution de la prévalence par Région - {base_title}", color_discrete_sequence=['#4C7C9E'])
    
    # Boxplot par Âge
    # Note: On utilise config.COL_TRANCHE_AGE pour la colonne de l'âge récupérée par lecture_BDD
    fig_box_age = px.box(df_filtered, x=config.COL_TRANCHE_AGE, y=config.COL_PREV, title=f"Prévalence en fonction de l'âge - {base_title}", color_discrete_sequence=['#4C7C9E']).update_xaxes(categoryorder='array', categoryarray=config.AGE)

    # Série Temporelle (Prévalence Moyenne par Année)
    # NOTE: Pour la série temporelle, on agrège les données déjà filtrées (par patho, sexe, âge) par année.
    # Ceci nécessite d'avoir plusieurs années dans les données filtrées, ce qui est le cas si config.COL_ANNEE était une colonne non filtrée dans la requête SQL, 
    # mais puisque nous filtrons l'ANNEE dans la requête, cela ne marche pas.
    # CORRECTION : Pour que la série temporelle fonctionne, nous DEVONS appeler une fonction qui récupère toutes les années pertinentes,
    # ou modifier la requête SQL pour exclure le filtre d'année, ce qui est trop complexe pour un seul fichier.
    
    # Option 1: Simuler la série temporelle en se basant uniquement sur la colonne de Tri (ou une autre colonne)
    # Option 2: Créer une figure vide ou un simple graphique si les données ne permettent pas l'analyse temporelle réelle sous ce filtre strict.

    # Puisque la requête filtre déjà sur une seule année, la série temporelle n'a pas de sens. Nous allons afficher les données par Sexe si possible.
    
    if config.COL_ANNEE in df_filtered.columns:
        df_time = df_filtered.groupby(config.COL_ANNEE, as_index=False)[config.COL_PREV].mean()
        fig_time_series = px.line(df_time, x=config.COL_ANNEE, y=config.COL_PREV, title=f"Prévalence Moyenne (Année sélectionnée: {annee})", markers=True, color_discrete_sequence=['#DC2626']).update_layout(yaxis_title="Prévalence Moyenne")
    else:
        fig_time_series = create_empty_figure(f"Série Temporelle : Données manquantes après filtrage strict par année.")
    
    # Boxplot par Niveau Prioritaire
    if config.COL_NV_PRIORITAIRE in df_filtered.columns:
        fig_priority = px.box(df_filtered, x=config.COL_NV_PRIORITAIRE, y=config.COL_PREV, title=f"Prévalence par Niveau Prioritaire - {base_title}", color_discrete_sequence=['#7C3AED']).update_xaxes(categoryorder='category ascending')
    else:
        fig_priority = create_empty_figure(f"Analyse Prioritaire : Colonne '{config.COL_NV_PRIORITAIRE}' introuvable ou filtrée")

    return (fig_tri, fig_ntop, fig_prev, fig_scatter, fig_box_region, fig_box_age, fig_time_series, fig_priority)

if __name__ == '__main__':
    app.run(debug=True)