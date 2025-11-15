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

# =============================================
# Création de l'app Dash
# =============================================
app = Dash(__name__)
app.title = "Dashboard Pathologies Étendu"

# =============================================
# Layout
# =============================================
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

    html.H2("Histogrammes principaux"),
    dcc.Graph(id='graph-tri'),
    dcc.Graph(id='graph-ntop'),
    dcc.Graph(id='graph-prev'),

    html.H2("Analyses régionales & départementales"),
    dcc.Graph(id='graph-region'),
    dcc.Graph(id='graph-dept'),

    html.H2("Analyse : Prévalence ↔ Ntop"),
    dcc.Graph(id='graph-scatter'),

    html.H2("Boxplots"),
    dcc.Graph(id='graph-box-region'),
    dcc.Graph(id='graph-box-age'),
])

# =============================================
# Callback : mise à jour des graphiques
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
    Input('patho-dropdown', 'value'),
    Input('sexe-dropdown', 'value')
)
def update_graphs(selected_patho, selected_sexe):

    df_filtered = df[
        (df[config.COL_PATHO_NV1] == selected_patho) &
        (df[config.COL_SEXE] == selected_sexe)
    ].copy()

    if df_filtered.empty:
        empty_fig = go.Figure().update_layout(
            title="Aucune donnée pour cette sélection",
            xaxis={'visible': False},
            yaxis={'visible': False}
        )
        return tuple([empty_fig] * 8)

    # ----------------------
    # Histogrammes existants
    # ----------------------
    fig_tri = px.histogram(df_filtered, x='tri', nbins=30,
                           title="Distribution du tri")

    fig_ntop = px.histogram(df_filtered, x=config.COL_NTOP, nbins=30,
                            title="Distribution du Ntop")

    fig_prev = px.histogram(df_filtered, x=config.COL_PREV, nbins=30,
                            title="Distribution de la prévalence")

    # ----------------------
    # Répartition par région
    # ----------------------
    fig_region = px.histogram(
        df_filtered,
        x=config.COL_CODE_REGION,
        title="Répartition des cas par région"
    )

    # ----------------------
    # Répartition par département
    # ----------------------
    fig_dept = px.histogram(
        df_filtered,
        x=config.COL_CODE_DEPT,
        title="Répartition des cas par département"
    )

    # ----------------------
    # Scatterplot
    # ----------------------
    fig_scatter = px.scatter(
        df_filtered,
        x=config.COL_NTOP,
        y=config.COL_PREV,
        trendline="ols",
        title="Corrélation : Prévalence vs Ntop"
    )

    # ----------------------
    # Boxplot par région
    # ----------------------
    fig_box_region = px.box(
        df_filtered,
        x=config.COL_CODE_REGION,
        y=config.COL_PREV,
        title="Distribution de la prévalence par région"
    )

    # ----------------------
    # Boxplot par âge (si disponible)
    # ----------------------
    # if "age" in df_filtered.columns:
    fig_box_age = px.box(
        df_filtered,
        x=config.COL_AGE,
        y=config.COL_PREV,
        title="Prévalence en fonction de l'âge"
        )
    # else:
    #     fig_box_age = go.Figure()
    #     fig_box_age.update_layout(
    #         title="Aucune colonne 'age' dans la base"
    #     )

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
