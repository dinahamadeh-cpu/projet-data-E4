import os
import sqlite3
import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
# Importation de plotly.graph_objects (go) pour créer une figure vide sans erreur
import plotly.graph_objects as go
import config  # ton fichier config.py

# =====================================================
# 1️⃣ Connexion à la base SQLite et lecture des données
# =====================================================
db_path = config.db_name

# Vérification de l'existence du fichier
if not os.path.exists(db_path):
    # Il est préférable de gérer cette erreur en dehors de l'application Dash si possible,
    # ou de renvoyer un layout d'erreur si l'application doit démarrer sans les données.
    raise FileNotFoundError(f"Le fichier DB n'existe pas à cet emplacement : {db_path}")

# Connexion et lecture
conn = sqlite3.connect(db_path)
query = f"SELECT * FROM {config.table_name}"
df = pd.read_sql_query(query, conn)
conn.close()

print(f"✅ Données chargées depuis {db_path} ({df.shape[0]} lignes, {df.shape[1]} colonnes)")

# =====================================================
# 2️⃣ Initialisation de l’application Dash
# =====================================================
app = Dash(__name__)
app.title = "Dashboard Pathologies"

# =====================================================
# 3️⃣ Layout du dashboard
# =====================================================
app.layout = html.Div([
    html.H1("🩺 Dashboard Pathologies France", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Choisir une pathologie :"),
        dcc.Dropdown(
            id='patho-dropdown',
            options=[{'label': p, 'value': p} for p in sorted(df[config.COL_PATHO_NV1].dropna().unique())],
            value=df[config.COL_PATHO_NV1].dropna().unique()[0],
            style={'width': '50%'}
        ),
    ], style={'margin': '20px'}),

    html.Div([
        html.Label("Choisir le sexe :"),
        dcc.Dropdown(
            id='sexe-dropdown',
            options=[{'label': s, 'value': s} for s in sorted(df[config.COL_SEXE].dropna().unique())],
            value=df[config.COL_SEXE].dropna().unique()[0],
            style={'width': '50%'}
        ),
    ], style={'margin': '20px'}),

    html.Br(),

    # Histogrammes
    dcc.Graph(id='graph-tri'),
    dcc.Graph(id='graph-ntop'),
    dcc.Graph(id='graph-prev'),
])

# =====================================================
# 4️⃣ Callbacks : mise à jour des graphiques
# =====================================================
@app.callback(
    Output('graph-tri', 'figure'),
    Output('graph-ntop', 'figure'),
    Output('graph-prev', 'figure'),
    Input('patho-dropdown', 'value'),
    Input('sexe-dropdown', 'value')
)
def update_graphs(selected_patho, selected_sexe):
    # Filtrage selon pathologie et sexe
    df_filtered = df[
        (df[config.COL_PATHO_NV1] == selected_patho) &
        (df[config.COL_SEXE] == selected_sexe)
    ].copy()

    if df_filtered.empty:
        # Correction de l'erreur : plotly.express.histogram() sans DataFrame lève une TypeError.
        # Nous utilisons go.Figure() pour créer une figure vide et y ajouter le message d'erreur.
        fig_empty = go.Figure()
        fig_empty.update_layout(
            title_text="Aucune donnée pour cette sélection",
            # Rendre les axes invisibles pour un affichage plus propre
            xaxis={'visible': False},
            yaxis={'visible': False},
            height=300,
            # Afficher un message au centre de la figure
            annotations=[{
                'text': 'Veuillez ajuster les filtres.',
                'xref': 'paper', 'yref': 'paper',
                'showarrow': False,
                'font': {'size': 16}
            }]
        )
        return fig_empty, fig_empty, fig_empty

    # Histogramme du tri
    fig_tri = px.histogram(
        df_filtered,
        x='tri',
        nbins=30,
        title=f"Distribution du tri - {selected_patho} ({selected_sexe})",
        color_discrete_sequence=['skyblue']
    )

    # Histogramme du Ntop
    fig_ntop = px.histogram(
        df_filtered,
        x=config.COL_NTOP,
        nbins=30,
        title=f"Distribution du Ntop - {selected_patho} ({selected_sexe})",
        color_discrete_sequence=['salmon']
    )

    # Histogramme de la prévalence
    fig_prev = px.histogram(
        df_filtered,
        x=config.COL_PREV,
        nbins=30,
        title=f"Distribution de la prévalence - {selected_patho} ({selected_sexe})",
        color_discrete_sequence=['lightgreen']
    )

    return fig_tri, fig_ntop, fig_prev

# =====================================================
# 5️⃣ Lancement de l’application
# =====================================================
if __name__ == '__main__':
    app.run(debug=True)