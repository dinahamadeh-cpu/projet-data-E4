import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from utils.hierarchiepatho import get_patho_hierarchy
from src.layout.layout_cartes import LayoutCartes


# 1. Initialisation et chargement des options statiques
app = dash.Dash(__name__)
PATHOS_HIERARCHY, NIV1_OPTIONS = get_patho_hierarchy()

MAP_LAYOUT = LayoutCartes.create_layout(NIV1_OPTIONS)
LayoutCartes.register_callbacks(app, PATHOS_HIERARCHY)

@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/cartes':
        return MAP_LAYOUT
    else:
        return html.Div("404 - Page non trouvée")