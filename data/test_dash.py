import os
import sqlite3
import pandas as pd
import geopandas as gpd
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
# Initialisation du Dashboard
# =============================================
app = Dash(__name__)
app.title = "Dashboard Pathologies France"

# Styles CSS
MAIN_STYLE = {'fontFamily': 'Roboto, Arial, sans-serif', 'backgroundColor': '#f5f7fa', 'padding': '20px'}
HEADER_STYLE = {'textAlign': 'center', 'color': '#1E3A8A', 'padding': '10px 0', 'fontSize': '2.5rem',
                'borderBottom': '3px solid #E5E7EB', 'marginBottom': '20px'}
CONTROLS_CONTAINER_STYLE = {'display': 'flex', 'flexWrap': 'wrap', 'gap': '20px', 'padding': '20px',
                            'marginBottom': '30px', 'backgroundColor': '#FFFFFF', 'borderRadius': '12px',
                            'boxShadow': '0 4px 12px rgba(0, 0, 0, 0.08)'}
CONTROL_ITEM_STYLE = {'flexGrow': 1, 'minWidth': '250px'}
GRAPH_CARD_STYLE = {'backgroundColor': '#FFFFFF', 'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.08)',
                    'padding': '15px', 'marginBottom': '25px'}
SECTION_TITLE_STYLE = {'color': '#374151', 'borderLeft': '4px solid #3B82F6', 'paddingLeft': '10px',
                       'marginTop': '40px', 'marginBottom': '20px', 'fontSize': '1.8rem'}

# =============================================
# Layout du Dashboard
# =============================================
app.layout = html.Div(style=MAIN_STYLE, children=[
    html.H1("Dashboard Pathologies France", style=HEADER_STYLE),

    # Dropdowns
    html.Div(style=CONTROLS_CONTAINER_STYLE, children=[
        html.Div(style=CONTROL_ITEM_STYLE, children=[
            html.Label("Choisir une pathologie (Niveau 1):", style={'fontWeight': 'bold', 'color': '#4B5563'}),
            dcc.Dropdown(
                id='patho-dropdown',
                options=[{'label': p, 'value': p} for p in sorted(df['patho_niv1'].dropna().unique())],
                value=sorted(df['patho_niv1'].dropna().unique())[0],
                clearable=False
            ),
        ]),
        html.Div(style=CONTROL_ITEM_STYLE, children=[
            html.Label("Choisir le sexe :", style={'fontWeight': 'bold', 'color': '#4B5563'}),
            dcc.Dropdown(
                id='sexe-dropdown',
                options=[{'label': s, 'value': s} for s in sorted(df['sexe'].dropna().unique())],
                value=sorted(df['sexe'].dropna().unique())[0],
                clearable=False
            ),
        ]),
        html.Div(style=CONTROL_ITEM_STYLE, children=[
            html.Label("Choisir l'année :", style={'fontWeight': 'bold', 'color': '#4B5563'}),
            dcc.Dropdown(
                id='annee-dropdown',
                options=[{'label': y, 'value': y} for y in sorted(df['annee'].dropna().unique())],
                value=sorted(df['annee'].dropna().unique())[0],
                clearable=False
            ),
        ]),
        html.Div(style=CONTROL_ITEM_STYLE, children=[
            html.Label("Niveau géographique :", style={'fontWeight': 'bold', 'color': '#4B5563'}),
            dcc.Dropdown(
                id='geo-level-dropdown',
                options=[
                    {'label': 'Région', 'value': 'region'},
                    {'label': 'Département', 'value': 'dept'}
                ],
                value='dept', clearable=False
            )
        ])
    ]),

    # Histogrammes
    html.H2("Distributions de base", style=SECTION_TITLE_STYLE),
    html.Div(style=GRAPH_CARD_STYLE, children=[dcc.Graph(id='graph-tri')]),
    html.Div(style=GRAPH_CARD_STYLE, children=[dcc.Graph(id='graph-ntop')]),
    html.Div(style=GRAPH_CARD_STYLE, children=[dcc.Graph(id='graph-prev')]),

    # Graphiques Région/Département
    html.H2("Analyses régionales & départementales", style=SECTION_TITLE_STYLE),
    html.Div(style=GRAPH_CARD_STYLE, children=[dcc.Graph(id='graph-region')]),
    html.Div(style=GRAPH_CARD_STYLE, children=[dcc.Graph(id='graph-dept')]),

    # Scatterplot et boxplots
    html.H2("Corrélations et Analyses Catégorielles", style=SECTION_TITLE_STYLE),
    html.Div(style=GRAPH_CARD_STYLE, children=[dcc.Graph(id='graph-scatter')]),
    html.Div(style=GRAPH_CARD_STYLE, children=[dcc.Graph(id='graph-priority')]),
    html.Div(style={'display': 'flex', 'gap': '20px'}, children=[
        html.Div(style={**GRAPH_CARD_STYLE, 'flex': 1}, children=[dcc.Graph(id='graph-box-region')]),
        html.Div(style={**GRAPH_CARD_STYLE, 'flex': 1}, children=[dcc.Graph(id='graph-box-age')]),
    ]),

    # Série temporelle
    html.H2("Évolution dans le temps", style=SECTION_TITLE_STYLE),
    html.Div(style=GRAPH_CARD_STYLE, children=[dcc.Graph(id='graph-time-series')]),

    # Carte interactive
    html.H2("Carte interactive", style=SECTION_TITLE_STYLE),
    html.Div(style=GRAPH_CARD_STYLE, children=[dcc.Graph(id='graph-map')]),
])

# =============================================
# Callback pour tous les graphiques
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
    Output('graph-time-series', 'figure'),
    Output('graph-priority', 'figure'),
    Output('graph-map', 'figure'),
    Input('patho-dropdown', 'value'),
    Input('sexe-dropdown', 'value'),
    Input('annee-dropdown', 'value'),
    Input('geo-level-dropdown', 'value')
)
def update_all(selected_patho, selected_sexe, selected_annee, geo_level):
    # Filtrage
    df_filtered = df[
        (df['patho_niv1'] == selected_patho) &
        (df['sexe'] == selected_sexe) &
        (df['annee'] == selected_annee)
    ].copy()

    def empty_fig(title="Aucune donnée"):
        fig = go.Figure()
        fig.update_layout(title=title, xaxis={'visible': False}, yaxis={'visible': False})
        return fig

    if df_filtered.empty:
        return tuple([empty_fig()] * 11)

    # Histogrammes
    fig_tri = px.histogram(df_filtered, x='tri', nbins=30, title='Distribution du tri', color_discrete_sequence=['#3B82F6'])
    fig_ntop = px.histogram(df_filtered, x='Ntop', nbins=30, title='Distribution du Ntop', color_discrete_sequence=['#F59E0B'])
    fig_prev = px.histogram(df_filtered, x='prev', nbins=30, title='Distribution de la prévalence', color_discrete_sequence=['#10B981'])

    # Histogrammes région/dept
    fig_region = px.histogram(df_filtered, x='region', title='Cas par région', color_discrete_sequence=['#6366F1'])
    fig_dept = px.histogram(df_filtered, x='dept', title='Cas par département', color_discrete_sequence=['#A855F7'])

    # Scatter
    fig_scatter = px.scatter(df_filtered, x='Ntop', y='prev', trendline='ols', title='Corrélation Ntop vs Prévalence')

    # Boxplots
    fig_box_region = px.box(df_filtered, x='region', y='prev', title='Prévalence par région', color_discrete_sequence=['#4C7C9E'])
    fig_box_age = px.box(df_filtered, x='libelle_classe_age', y='prev', title="Prévalence par âge", color_discrete_sequence=['#4C7C9E'])

    # Série temporelle
    df_time = df_filtered.groupby('annee', as_index=False).agg(mean_prev=('prev', 'mean'))
    fig_time_series = px.line(df_time, x='annee', y='mean_prev', markers=True, title='Évolution de la prévalence')

    # Priorité
    if 'Niveau prioritaire' in df_filtered.columns:
        fig_priority = px.box(df_filtered, x='Niveau prioritaire', y='prev', title='Prévalence par Niveau Prioritaire')
    else:
        fig_priority = empty_fig("Analyse prioritaire non disponible")

    # Carte interactive
    geojson_path = config.dept_geojson if geo_level == 'dept' else config.region_geojson
    gdf = gpd.read_file(geojson_path)
    merged = gdf.merge(df_filtered.groupby(geo_level)['prev'].mean().reset_index(), left_on='code', right_on=geo_level, how='left')
    fig_map = px.choropleth(
        merged,
        geojson=merged.geometry,
        locations=merged.index,
        color='prev',
        hover_name=geo_level,
        hover_data={'prev': True},
        color_continuous_scale="YlOrRd"
    )
    fig_map.update_geos(fitbounds="locations", visible=False)
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, title=f"Carte : {geo_level}")

    return fig_tri, fig_ntop, fig_prev, fig_region, fig_dept, fig_scatter, fig_box_region, fig_box_age, fig_time_series, fig_priority, fig_map

# =============================================
# Run app
# =============================================
if __name__ == '__main__':
    app.run(debug=True)
