import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import requests

# =====================================================
# Chargement des données
# =====================================================

df_file = "C:\\Users\\achve\\OneDrive - ESIEE Paris\\Documents\\projet_data\\data\\cleaned\\data_patologies_cleaned.csv"

# Chargement du dataset
df = pd.read_csv(df_file, low_memory=False)

# Échantillon pour rapidité
df_sample = df.sample(50000, random_state=42)

# =====================================================
# 2️⃣ Téléchargement des cartes de France
# =====================================================

# GeoJSON des régions
geojson_regions = requests.get("https://france-geojson.gregoiredavid.fr/repo/regions.geojson").json()

# GeoJSON des départements
geojson_departements = requests.get("https://france-geojson.gregoiredavid.fr/repo/departements.geojson").json()

# =====================================================
# 3️⃣ Initialisation de l'application Dash
# =====================================================

app = Dash(__name__)

app.layout = html.Div([
    html.H1("🩺 Dashboard Pathologies France", style={'textAlign': 'center'}),

    html.Div([
        html.Div([
            html.Label("Choisir une pathologie :"),
            dcc.Dropdown(
                id='patho-dropdown',
                options=[{'label': p, 'value': p} for p in sorted(df_sample['patho_niv1'].dropna().unique())],
                value=df_sample['patho_niv1'].dropna().unique()[0],
                style={'width': '100%'}
            ),
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            html.Label("Choisir un niveau prioritaire :"),
            dcc.Dropdown(
                id='niveau-dropdown',
                options=[{'label': str(n), 'value': n} for n in sorted(df_sample['Niveau prioritaire'].dropna().unique())],
                value=df_sample['Niveau prioritaire'].dropna().unique()[0],
                style={'width': '100%'}
            ),
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),
    ]),

    html.Br(),

    # Graphique 1 : Distribution du tri
    dcc.Graph(id='graph-tri'),

    # Graphique 2 : Prévalence
    dcc.Graph(id='graph-prev'),

    # Graphique 3 : Carte France (régions et départements)
    dcc.RadioItems(
        id='geo-level',
        options=[
            {'label': 'Par région', 'value': 'region'},
            {'label': 'Par département', 'value': 'departement'}
        ],
        value='region',
        inline=True,
        style={'textAlign': 'center', 'marginBottom': '10px'}
    ),
    dcc.Graph(id='graph-map'),
])

# =====================================================
# 4️⃣ Callbacks
# =====================================================

@app.callback(
    Output('graph-tri', 'figure'),
    Output('graph-prev', 'figure'),
    Output('graph-map', 'figure'),
    Input('patho-dropdown', 'value'),
    Input('niveau-dropdown', 'value'),
    Input('geo-level', 'value')
)
def update_dashboard(selected_patho, selected_niveau, geo_level):
    # --- Filtrage ---
    df_filtered = df_sample[
        (df_sample['patho_niv1'] == selected_patho) &
        (df_sample['Niveau prioritaire'] == selected_niveau)
    ].copy()

    if df_filtered.empty:
        fig_empty = px.scatter(title="Aucune donnée disponible pour cette sélection")
        return fig_empty, fig_empty, fig_empty

    # --- Graphique 1 : Distribution du tri ---
    fig_tri = px.histogram(
        df_filtered,
        x='tri',
        nbins=30,
        title=f"Distribution du tri - {selected_patho} (niveau {selected_niveau})"
    )

    # --- Graphique 2 : Prévalence ---
    df_filtered['Ntop'] = pd.to_numeric(df_filtered['Ntop'], errors='coerce').fillna(0)
    df_filtered['Npop'] = pd.to_numeric(df_filtered['Npop'], errors='coerce').fillna(0)
    df_filtered['prev'] = pd.to_numeric(df_filtered['prev'], errors='coerce').fillna(0)

    fig_prev = px.scatter(
        df_filtered,
        x='Npop',
        y='prev',
        size='Ntop',
        color='libelle_sexe',
        title=f"Prévalence vs Population - {selected_patho} (niveau {selected_niveau})",
        hover_data=['region', 'departement', 'cla_age_5']
    )

    # --- Graphique 3 : Carte ---
    if geo_level == "region":
        df_geo = df_filtered.groupby('region', as_index=False)['tri'].mean()
        fig_map = px.choropleth(
            df_geo,
            geojson=geojson_regions,
            featureidkey="properties.nom",
            locations="region",
            color="tri",
            color_continuous_scale="Viridis",
            title=f"Tri moyen par région - {selected_patho} (niveau {selected_niveau})"
        )
    else:
        df_geo = df_filtered.groupby('departement', as_index=False)['tri'].mean()
        fig_map = px.choropleth(
            df_geo,
            geojson=geojson_departements,
            featureidkey="properties.nom",
            locations="departement",
            color="tri",
            color_continuous_scale="Plasma",
            title=f"Tri moyen par département - {selected_patho} (niveau {selected_niveau})"
        )

    fig_map.update_geos(fitbounds="locations", visible=False)

    return fig_tri, fig_prev, fig_map


# =====================================================
# 5️⃣ Lancement
# =====================================================
if __name__ == '__main__':
    app.run(debug=True)
