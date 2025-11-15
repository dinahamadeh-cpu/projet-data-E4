import os
import sqlite3
import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import config

# =============================================
# Connexion à la base SQLite
# =============================================
db_path = config.db_name
if not os.path.exists(db_path):
    raise FileNotFoundError(f"Base introuvable : {db_path}")

conn = sqlite3.connect(db_path)
query = f"SELECT * FROM {config.table_name}"
df = pd.read_sql_query(query, conn)
conn.close()

print(f" Données chargées depuis {db_path} ({df.shape[0]} lignes, {df.shape[1]} colonnes)")

# =============================================
# Mappage des niveaux de pathologie aux colonnes
# =============================================
PATHO_LEVEL_OPTIONS = [
    {'label': 'Niveau 1', 'value': config.COL_PATHO_NV1},
    {'label': 'Niveau 2', 'value': config.COL_PATHO_NV2},
    {'label': 'Niveau 3', 'value': config.COL_PATHO_NV3},
]

# =============================================
# Création de l'app Dash
# =============================================
app = Dash(__name__)
app.title = "Dashboard Pathologies Étendu"

# Styles CSS pour une interface moderne
MAIN_STYLE = {
    'fontFamily': 'Roboto, Arial, sans-serif',
    'backgroundColor': '#f5f7fa', # Arrière-plan très clair
    'padding': '20px'
}

HEADER_STYLE = {
    'textAlign': 'center', 
    'color': '#1E3A8A', 
    'padding': '10px 0',
    'fontSize': '2.5rem',
    'borderBottom': '3px solid #E5E7EB',
    'marginBottom': '20px'
}

CONTROLS_CONTAINER_STYLE = {
    'display': 'flex',
    'flexWrap': 'wrap',
    'gap': '20px',
    'padding': '20px',
    'marginBottom': '30px',
    'backgroundColor': '#FFFFFF',
    'borderRadius': '12px',
    'boxShadow': '0 4px 12px rgba(0, 0, 0, 0.08)'
}

CONTROL_ITEM_STYLE = {
    'flexGrow': 1,
    'minWidth': '250px' 
}

GRAPH_CARD_STYLE = {
    'backgroundColor': '#FFFFFF',
    'borderRadius': '12px',
    'boxShadow': '0 4px 12px rgba(0, 0, 0, 0.08)',
    'padding': '15px',
    'marginBottom': '25px',
}

SECTION_TITLE_STYLE = {
    'color': '#374151',
    'borderLeft': '4px solid #3B82F6',
    'paddingLeft': '10px',
    'marginTop': '40px',
    'marginBottom': '20px',
    'fontSize': '1.8rem'
}

# =============================================
# Layout (avec les nouveaux graphiques)
# =============================================
app.layout = html.Div(style=MAIN_STYLE, children=[
    html.H1(" Dashboard Pathologies France", style=HEADER_STYLE),

    # CONTROLES D'UTILISATEUR
    html.Div(style=CONTROLS_CONTAINER_STYLE, children=[
        # SÉLECTEUR DE NIVEAU DE PATHOLOGIE
        html.Div(style=CONTROL_ITEM_STYLE, children=[
            html.Label("Niveau de pathologie :", style={'fontWeight': 'bold', 'color': '#4B5563'}),
            dcc.Dropdown(
                id='patho-level-dropdown',
                options=PATHO_LEVEL_OPTIONS,
                value=config.COL_PATHO_NV1, # Niveau 1 par défaut
                clearable=False,
            ),
        ]),

        # SÉLECTEUR DE PATHOLOGIE (Dynamique)
        html.Div(style=CONTROL_ITEM_STYLE, children=[
            html.Label("Choisir une pathologie :", style={'fontWeight': 'bold', 'color': '#4B5563'}),
            dcc.Dropdown(
                id='patho-dropdown',
                style={'width': '100%'}
            ),
        ]),
        
        # SÉLECTEUR DE SEXE
        html.Div(style=CONTROL_ITEM_STYLE, children=[
            html.Label("Choisir le sexe :", style={'fontWeight': 'bold', 'color': '#4B5563'}),
            dcc.Dropdown(
                id='sexe-dropdown',
                options=[{'label': s, 'value': s} for s in sorted(df[config.COL_SEXE].dropna().unique())],
                value=df[config.COL_SEXE].dropna().unique()[0],
                clearable=False,
            ),
        ]),
    ]), # Fin CONTROLS_CONTAINER_STYLE

    # SECTION 1: Histogrammes
    html.H2("Distributions de base", style=SECTION_TITLE_STYLE),
    html.Div(style=GRAPH_CARD_STYLE, children=[dcc.Graph(id='graph-tri')]),
    html.Div(style=GRAPH_CARD_STYLE, children=[dcc.Graph(id='graph-ntop')]),
    html.Div(style=GRAPH_CARD_STYLE, children=[dcc.Graph(id='graph-prev')]),
    
    # NOUVELLE SECTION : Analyse Temporelle
    html.H2("Analyse Temporelle", style=SECTION_TITLE_STYLE),
    html.Div(style=GRAPH_CARD_STYLE, children=[dcc.Graph(id='graph-time-series')]), # Nouveau graphique

    # SECTION 2: Analyses régionales
    html.H2("Analyses régionales & départementales", style=SECTION_TITLE_STYLE),
    html.Div(style=GRAPH_CARD_STYLE, children=[dcc.Graph(id='graph-region')]),
    html.Div(style=GRAPH_CARD_STYLE, children=[dcc.Graph(id='graph-dept')]),

    # SECTION 3: Corrélation, Boxplots et Priorité
    html.H2("Corrélations et Analyses Catégorielles", style=SECTION_TITLE_STYLE),
    
    # Scatterplot
    html.Div(style=GRAPH_CARD_STYLE, children=[dcc.Graph(id='graph-scatter')]),
    
    # NOUVEAU GRAPHIQUE : Niveau Prioritaire
    html.Div(style=GRAPH_CARD_STYLE, children=[dcc.Graph(id='graph-priority')]), 

    # Boxplots
    html.Div(style={'display': 'flex', 'gap': '20px'}, children=[
        html.Div(style={**GRAPH_CARD_STYLE, 'flex': 1}, children=[dcc.Graph(id='graph-box-region')]),
        html.Div(style={**GRAPH_CARD_STYLE, 'flex': 1}, children=[dcc.Graph(id='graph-box-age')]),
    ]),
])

# =============================================
# 1er Callback : Met à jour le dropdown de pathologie en fonction du niveau choisi
# =============================================
@app.callback(
    Output('patho-dropdown', 'options'),
    Output('patho-dropdown', 'value'),
    Input('patho-level-dropdown', 'value')
)
def update_patho_dropdown(selected_level_col_name):
    # 'selected_level_col_name' est le nom de la colonne (ex: 'patho_niv1')
    
    if selected_level_col_name not in df.columns:
        print(f" Erreur: Colonne {selected_level_col_name} introuvable dans le DataFrame.")
        return [], None
    
    # Récupérer les valeurs uniques pour la colonne sélectionnée
    unique_pathos = sorted(df[selected_level_col_name].dropna().unique())
    options = [{'label': p, 'value': p} for p in unique_pathos]
    
    # Définir une valeur par défaut (la première de la liste, ou None si vide)
    initial_value = unique_pathos[0] if unique_pathos else None
    
    return options, initial_value


# =============================================
# 2ème Callback : mise à jour des graphiques
# =============================================
@app.callback(
    Output('graph-tri', 'figure'),
    Output('graph-ntop', 'figure'),
    Output('graph-prev', 'figure'),
    Output('graph-region', 'figure'),
    Output('graph-dept', 'figure'),
    Output('graph-scatter', 'figure'),
    Output('graph-box-region', 'figure'),
    Output('graph-box-age', 'figure'),
    Output('graph-time-series', 'figure'),  # Nouvelle sortie
    Output('graph-priority', 'figure'),      # Nouvelle sortie
    Input('patho-level-dropdown', 'value'), 
    Input('patho-dropdown', 'value'),
    Input('sexe-dropdown', 'value')
)
def update_graphs(selected_level_col_name, selected_patho, selected_sexe):
    
    # S'assurer qu'une pathologie et un sexe sont sélectionnés pour éviter les erreurs de filtrage
    if selected_patho is None or selected_sexe is None:
        # Retourne 10 figures vides (8 anciennes + 2 nouvelles)
        return tuple([go.Figure()] * 10)

    # ----------------------------------------------------
    # Filtrage du DataFrame basé sur la colonne de niveau dynamique
    # ----------------------------------------------------
    df_filtered = df[
        (df[selected_level_col_name] == selected_patho) &
        (df[config.COL_SEXE] == selected_sexe)
    ].copy()

    # Titre de base pour les figures
    level_name = next(
        (item['label'] for item in PATHO_LEVEL_OPTIONS if item['value'] == selected_level_col_name), 
        "Niveau Inconnu"
    )
    base_title = f"{selected_patho} ({level_name}, {selected_sexe})"

    # Fonction utilitaire pour créer une figure d'erreur (si df est vide)
    def create_empty_figure(title_text):
        fig = go.Figure().update_layout(
            title=title_text,
            xaxis={'visible': False},
            yaxis={'visible': False},
            height=300,
            annotations=[{
                'text': 'Aucune donnée disponible pour cette sélection.',
                'xref': 'paper', 'yref': 'paper',
                'showarrow': False,
                'font': {'size': 16, 'color': '#EF4444'}
            }]
        )
        return fig

    if df_filtered.empty:
        empty_fig = create_empty_figure("Aucune donnée pour cette sélection")
        # Retourne 10 figures vides (8 anciennes + 2 nouvelles)
        return tuple([empty_fig] * 10)

    # ==========================================================
    # GÉNÉRATION DES GRAPHIQUES EXISTANTS
    # ==========================================================

    # 1. Histogrammes
    fig_tri = px.histogram(df_filtered, x='tri', nbins=30,
                           title=f"Distribution du tri - {base_title}",
                           color_discrete_sequence=['#3B82F6'])

    fig_ntop = px.histogram(df_filtered, x=config.COL_NTOP, nbins=30,
                            title=f"Distribution du Ntop - {base_title}",
                            color_discrete_sequence=['#F59E0B'])

    fig_prev = px.histogram(df_filtered, x=config.COL_PREV, nbins=30,
                            title=f"Distribution de la prévalence - {base_title}",
                            color_discrete_sequence=['#10B981'])

    # 2. Répartition régionale/départementale
    fig_region = px.histogram(
        df_filtered,
        x=config.COL_CODE_REGION,
        title=f"Répartition des cas par région - {base_title}",
        color_discrete_sequence=['#6366F1']
    )

    fig_dept = px.histogram(
        df_filtered,
        x=config.COL_CODE_DEPT,
        title=f"Répartition des cas par département - {base_title}",
        color_discrete_sequence=['#A855F7']
    )

    # 3. Scatterplot (Corrélation)
    fig_scatter = px.scatter(
        df_filtered,
        x=config.COL_NTOP,
        y=config.COL_PREV,
        trendline="ols",
        title=f"Corrélation : Prévalence vs Ntop - {base_title}"
    )

    # 4. Boxplot par région
    fig_box_region = px.box(
        df_filtered,
        x=config.COL_CODE_REGION,
        y=config.COL_PREV,
        title=f"Distribution de la prévalence par région - {base_title}",
        color_discrete_sequence=['#4C7C9E']
    )

    # 5. Boxplot par âge
    COL_AGE = config.COL_AGE
    if COL_AGE in df_filtered.columns:
        fig_box_age = px.box(
            df_filtered,
            x=COL_AGE, 
            y=config.COL_PREV,
            title=f"Prévalence en fonction de l'âge - {base_title}",
            color_discrete_sequence=['#4C7C9E']
        )
    else:
        fig_box_age = create_empty_figure(f"Boxplot de l'âge : Colonne '{COL_AGE}' introuvable")

    # ==========================================================
    # NOUVEAUX GRAPHIQUES
    # ==========================================================
    
    # 6. Série Temporelle (annee)
    df_time = df_filtered.groupby('annee', as_index=False).agg(
        mean_prev=(config.COL_PREV, 'mean'),
        total_ntop=(config.COL_NTOP, 'sum')
    )
    
    # Utiliser la prévalence moyenne au fil du temps
    fig_time_series = px.line(
        df_time,
        x='annee',
        y='mean_prev',
        title=f"Évolution de la Prévalence Moyenne (Année) - {base_title}",
        markers=True,
        color_discrete_sequence=['#DC2626'] # Rouge pour le temps
    ).update_layout(yaxis_title="Prévalence Moyenne")


    # 7. Analyse par Niveau Prioritaire
    # Utilisation d'un boxplot pour visualiser la distribution de la prévalence par niveau
    if 'Niveau prioritaire' in df_filtered.columns:
        fig_priority = px.box(
            df_filtered,
            x='Niveau prioritaire',
            y=config.COL_PREV,
            title=f"Prévalence par Niveau Prioritaire - {base_title}",
            color_discrete_sequence=['#7C3AED'] # Violet
        ).update_xaxes(categoryorder='category ascending')
    else:
        fig_priority = create_empty_figure("Analyse Prioritaire : Colonne 'Niveau prioritaire' introuvable")


    # ==========================================================
    # RETOURNER TOUTES LES FIGURES (10 au total)
    # ==========================================================
    return (
        fig_tri,
        fig_ntop,
        fig_prev,
        fig_region,
        fig_dept,
        fig_scatter,
        fig_box_region,
        fig_box_age,
        fig_time_series, 
        fig_priority    
    )


# =============================================
# Run app
# =============================================
if __name__ == '__main__':
    app.run(debug=True)