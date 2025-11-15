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
# (Assure-toi que config.COL_PATHO_NV1, NV2, NV3 sont correctement définis)
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

# =============================================
# Layout (Ajout du dropdown pour le Niveau de Pathologie)
# =============================================
app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif'}, children=[
    html.H1("🩺 Dashboard Pathologies France", style={'textAlign': 'center', 'color': '#1E3A8A', 'padding': '20px'}),

    html.Div([
        # SÉLECTEUR DE NIVEAU DE PATHOLOGIE
        html.Div([
            html.Label("Choisir le niveau de pathologie :", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='patho-level-dropdown',
                options=PATHO_LEVEL_OPTIONS,
                value=config.COL_PATHO_NV1, # Niveau 1 par défaut
                clearable=False,
                style={'backgroundColor': '#F3F4F6'}
            ),
        ], style={'width': '31%', 'display': 'inline-block', 'marginRight': '3%'}),

        # SÉLECTEUR DE PATHOLOGIE (Dynamique)
        html.Div([
            html.Label("Choisir une pathologie :", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='patho-dropdown',
                # Les options et la valeur initiale seront définies par le callback
                style={'backgroundColor': '#F3F4F6'}
            ),
        ], style={'width': '31%', 'display': 'inline-block', 'marginRight': '3%'}),
        
        # SÉLECTEUR DE SEXE
        html.Div([
            html.Label("Choisir le sexe :", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='sexe-dropdown',
                options=[{'label': s, 'value': s} for s in sorted(df[config.COL_SEXE].dropna().unique())],
                value=df[config.COL_SEXE].dropna().unique()[0],
                clearable=False,
                style={'backgroundColor': '#F3F4F6'}
            ),
        ], style={'width': '31%', 'display': 'inline-block'}),

    ], style={'margin': '20px', 'padding': '10px', 'border': '1px solid #E5E7EB', 'borderRadius': '8px', 'backgroundColor': '#FFFFFF'}),

    html.Br(),

    html.H2("Histogrammes principaux", style={'textAlign': 'left', 'color': '#4B5563', 'marginTop': '30px'}),
    dcc.Graph(id='graph-tri', style={'marginBottom': '20px'}),
    dcc.Graph(id='graph-ntop', style={'marginBottom': '20px'}),
    dcc.Graph(id='graph-prev', style={'marginBottom': '20px'}),

    html.H2("Analyses régionales & départementales", style={'textAlign': 'left', 'color': '#4B5563', 'marginTop': '30px'}),
    dcc.Graph(id='graph-region', style={'marginBottom': '20px'}),
    dcc.Graph(id='graph-dept', style={'marginBottom': '20px'}),

    html.H2("Analyse : Prévalence ↔ Ntop", style={'textAlign': 'left', 'color': '#4B5563', 'marginTop': '30px'}),
    dcc.Graph(id='graph-scatter', style={'marginBottom': '20px'}),

    html.H2("Boxplots", style={'textAlign': 'left', 'color': '#4B5563', 'marginTop': '30px'}),
    dcc.Graph(id='graph-box-region', style={'marginBottom': '20px'}),
    dcc.Graph(id='graph-box-age', style={'marginBottom': '20px'}),
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
        # En cas d'erreur de configuration (nom de colonne invalide)
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
    # Input des niveaux pour le filtrage
    Input('patho-level-dropdown', 'value'), 
    Input('patho-dropdown', 'value'),
    Input('sexe-dropdown', 'value')
)
def update_graphs(selected_level_col_name, selected_patho, selected_sexe):
    
    # S'assurer qu'une pathologie et un sexe sont sélectionnés pour éviter les erreurs de filtrage
    if selected_patho is None or selected_sexe is None:
        return tuple([go.Figure()] * 8)

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
                'text': 'Veuillez ajuster les filtres.',
                'xref': 'paper', 'yref': 'paper',
                'showarrow': False,
                'font': {'size': 16, 'color': '#EF4444'}
            }]
        )
        return fig

    if df_filtered.empty:
        empty_fig = create_empty_figure("Aucune donnée pour cette sélection")
        return tuple([empty_fig] * 8)

    # ----------------------
    # 1. Histogrammes
    # ----------------------
    fig_tri = px.histogram(df_filtered, x='tri', nbins=30,
                           title=f"Distribution du tri - {base_title}",
                           color_discrete_sequence=['#3B82F6'])

    fig_ntop = px.histogram(df_filtered, x=config.COL_NTOP, nbins=30,
                            title=f"Distribution du Ntop - {base_title}",
                            color_discrete_sequence=['#F59E0B'])

    fig_prev = px.histogram(df_filtered, x=config.COL_PREV, nbins=30,
                            title=f"Distribution de la prévalence - {base_title}",
                            color_discrete_sequence=['#10B981'])

    # ----------------------
    # 2. Répartition régionale/départementale
    # ----------------------
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

    # ----------------------
    # 3. Scatterplot (Corrélation)
    # ----------------------
    fig_scatter = px.scatter(
        df_filtered,
        x=config.COL_NTOP,
        y=config.COL_PREV,
        trendline="ols",
        title=f"Corrélation : Prévalence vs Ntop - {base_title}"
    )

    # ----------------------
    # 4. Boxplots
    # ----------------------
    fig_box_region = px.box(
        df_filtered,
        x=config.COL_CODE_REGION,
        y=config.COL_PREV,
        title=f"Distribution de la prévalence par région - {base_title}"
    )

    # Boxplot par âge
    COL_AGE = config.COL_AGE
    
    if COL_AGE in df_filtered.columns:
        fig_box_age = px.box(
            df_filtered,
            x=COL_AGE, 
            y=config.COL_PREV,
            title=f"Prévalence en fonction de l'âge - {base_title}"
        )
    else:
        print(f" Avertissement : La colonne '{COL_AGE}' n'existe pas. Vérifiez la définition de config.COL_AGE.")
        fig_box_age = create_empty_figure(f"Boxplot de l'âge : Colonne '{COL_AGE}' introuvable")


    return (
        fig_tri,
        fig_ntop,
        fig_prev,
        fig_region,
        fig_dept,
        fig_scatter,
        fig_box_region,
        fig_box_age
    )


# =============================================
# Run app
# =============================================
if __name__ == '__main__':
    app.run(debug=True)