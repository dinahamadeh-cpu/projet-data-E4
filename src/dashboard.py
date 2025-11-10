import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import config
from src.hierarchiepatho import get_patho_hierarchy
from src.carte_departements import lecture_BDD, creation_carte_region

# 1. Initialisation et chargement des options statiques
app = dash.Dash(__name__)
PATHOS_HIERARCHY, NIV1_OPTIONS = get_patho_hierarchy()

# 2. Layout (mise en page)
# ... (Le code du Layout avec les 4 menus déroulants : Année, Niv1, Niv2, Niv3) ...
# C'est la structure que nous avons définie à l'étape 2 précédente.
# ... (Imports et initialisation de app) ...

# MISE EN PAGE (LAYOUT)
app.layout = html.Div([
    html.H1("Dashboard de Prévalence Hiérarchique", style={'textAlign': 'center'}),
    
    html.Div([
        # Sélecteur d'Année (inchangé)
        html.Div([
            html.Label("Année :"),
            dcc.Dropdown(id='selecteur-annee', 
                         options=[{'label':i, 'value': i}for i in config.ANNEE],
                          value= config.ANNEE[0],
                           clearable=False ), # Configuration inchangée
        ], style={'width': '24%', 'display': 'inline-block'}),
        html.Div([
            html.Label("Sexe :"),
            dcc.Dropdown(id='selecteur-sexe', 
                         options=[{'label':i, 'value': i}for i in config.SEXE],
                          value= config.SEXE[-1],
                           clearable=False ), # Configuration inchangée
            ], style={'width': '24%', 'display': 'inline-block'}),
        
        # NOUVEAU : Sélecteur Patho_Niv1
        html.Div([
            html.Label("Pathologie - Niveau 1 :"),
            dcc.Dropdown(
                id='selecteur-patho-niv1',
                options=[{'label': i, 'value': i} for i in NIV1_OPTIONS], # Utilise les options extraites
                value=NIV1_OPTIONS[0],
                clearable=False
            ),
        ], style={'width': '24%', 'display': 'inline-block'}),
        
        # NOUVEAU : Sélecteur Patho_Niv2 (sera mis à jour par Niv1)
        html.Div([
            html.Label("Pathologie - Niveau 2 :"),
            dcc.Dropdown(
                id='selecteur-patho-niv2',
                # Les options initiales seront définies par le premier callback
                clearable=False
            ),
        ], style={'width': '24%', 'display': 'inline-block'}),

        # NOUVEAU : Sélecteur Patho_Niv3 (sera mis à jour par Niv2)
        html.Div([
            html.Label("Pathologie - Niveau 3 :"),
            dcc.Dropdown(
                id='selecteur-patho-niv3',
                # Les options initiales seront définies par le second callback
                clearable=False
            ),
        ], style={'width': '24%', 'float': 'right', 'display': 'inline-block'}),

    ], style={'padding': 10}),
    
    html.Iframe(id='carte-dynamique', style={"width": "100%", "height": "650px", "border": "none"})
])

# 3. Callbacks Chaînés (Logique des menus)
# @app.callback(Output Niv2, Input Niv1)
# ... (Code du callback pour mettre à jour Niv2 en fonction de Niv1) ...
@app.callback(
    [Output('selecteur-patho-niv2', 'options'),
     Output('selecteur-patho-niv2', 'value')],
    [Input('selecteur-patho-niv1', 'value')]
)
def set_patho_niv2_options(selected_niv1):
    if not selected_niv1:
        return [], None
    
    # Récupère les clés de niveau 2 pour le niveau 1 sélectionné
    niv2_list = list(PATHOS_HIERARCHY[selected_niv1].keys())
    options = [{'label': i, 'value': i} for i in niv2_list]
    
    # Définit la première option comme valeur par défaut
    default_value = niv2_list[0] if niv2_list else None
    
    return options, default_value

@app.callback(
    [Output('selecteur-patho-niv3', 'options'),
     Output('selecteur-patho-niv3', 'value')],
    [Input('selecteur-patho-niv1', 'value'),
     Input('selecteur-patho-niv2', 'value')]
)
def set_patho_niv3_options(selected_niv1, selected_niv2):
    # Nécessite Niv1 et Niv2 pour trouver les options Niv3
    if not selected_niv1 or not selected_niv2:
        return [], None
    
    # Récupère la liste de niveau 3
    niv3_list = PATHOS_HIERARCHY[selected_niv1][selected_niv2]
    options = [{'label': i, 'value': i} for i in niv3_list]
    
    # Définit la première option comme valeur par défaut
    default_value = niv3_list[0] if niv3_list else None
    
    return options, default_value


# 4. Callback Principal (Mise à jour de la carte)
@app.callback(
    Output('carte-dynamique', 'srcDoc'),
    [Input('selecteur-annee', 'value'),
    Input('selecteur-patho-niv1', 'value'),
    Input('selecteur-patho-niv2', 'value'),
     Input('selecteur-patho-niv3', 'value'),
     Input('selecteur-sexe', 'value')]
)
def mettre_a_jour_carte(annee, patho_niv1, patho_niv2, patho_niv3, sexe ):
    if patho_niv1 is None:
        return "" 
    
    # Lecture BDD
    df_filtre = lecture_BDD(annee, patho_niv1,  patho_niv2, patho_niv3,sexe )
    
    # Création du titre et de la carte
    titre = f"Total Patients ({sexe}, {patho_niv1}, {annee})"
    return creation_carte_region(df_filtre, titre)
