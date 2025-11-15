import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
from src.utils.hierarchiepatho import get_patho_hierarchy
from src.utils.lecture_BDD import lecture_BDD_histo
from src.layout.layout_cartes import LayoutCartes
import config
from src.layout.layout_histo import LayoutHistogrammes


# 1. Initialisation et chargement des options statiques
df = lecture_BDD_histo()
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP] ,suppress_callback_exceptions=True)
app.title = "Dashboard Pathologies France"

PATHOS_HIERARCHY, NIV1_OPTIONS = get_patho_hierarchy()
PATHO_LEVEL_OPTIONS = [{'label': 'Niveau 1', 'value': 'patho_niv1'},
                           {'label': 'Niveau 2', 'value': 'patho_niv2'},
                           {'label': 'Niveau 3', 'value': 'patho_niv3'}]

MAP_LAYOUT = LayoutCartes.create_layout(NIV1_OPTIONS)
HISTO_LAYOUT=LayoutHistogrammes.create_layout(df, PATHO_LEVEL_OPTIONS)

LayoutCartes.register_callback(app, PATHOS_HIERARCHY)
LayoutHistogrammes.register_callbacks(app, df, PATHOS_HIERARCHY,config)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    
    # Barre de navigation simple
    html.Div([
        dcc.Link('Cartes Régionales', href='/cartes', style={'marginRight': '20px'}),
        dcc.Link('Analyses & Histogrammes', href='/histogrammes'),
    ], style={'padding': '10px', 'borderBottom': '1px solid #ccc', 'backgroundColor': '#f0f0f0'}),
    
    # Contenu de la page
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/cartes':
        return MAP_LAYOUT
    if pathname == '/histogrammes':
        return HISTO_LAYOUT
    else:
        return html.Div([
            html.H1("Bienvenue sur le Dashboard d'Analyse des Pathologies", style={'color': '#1E3A8A'}),
            html.P("Veuillez sélectionner une section ci-dessus pour commencer l'analyse.", style={'fontSize': '1.2rem'})
        ], style={'textAlign': 'center', 'marginTop': '100px', 'padding': '20px', 'backgroundColor': '#fff', 'borderRadius': '8px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.1)'})