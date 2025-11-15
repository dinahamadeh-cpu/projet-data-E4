from dash import dcc, html
from dash.dependencies import Input, Output
import config
from src.page.cartes import creation_carte
from src.utils.lecture_BDD import lecture_BDD_carte

class LayoutCartes:
    @staticmethod
    def create_layout(NIV1_OPTIONS):

        layout = html.Div([
            html.H1("Dashboard de Prévalence Hiérarchique", style={'textAlign': 'center'}),
                html.Div([
                    html.Label("Type de Carte :"),
                    dcc.Dropdown(
                        id='selecteur-carte',
                        options=[
                            {'label': 'Carte par Région', 'value': 'region'},
                            {'label': 'Carte par Département', 'value': 'departement'}
                        ],
                        value='region',
                        clearable=False
                    ),
                ], style={'width': '24%', 'display': 'inline-block', 'padding': 10}),
            
            html.Div([
                html.Div([
                    html.Label("Année :"),
                    dcc.Dropdown(id='selecteur-annee', 
                                options=[{'label':i, 'value': i}for i in config.ANNEE],
                                value= config.ANNEE[0],
                                clearable=False ),
                ], style={'width': '24%', 'display': 'inline-block'}),
                html.Div([
                    html.Label("Sexe :"),
                    dcc.Dropdown(id='selecteur-sexe', 
                                options=[{'label':i, 'value': i}for i in config.SEXE],
                                value= config.SEXE[-1],
                                clearable=False ),
                    ], style={'width': '24%', 'display': 'inline-block'}),
                html.Div([
                    html.Label("Âge :"),
                    dcc.Dropdown(id='selecteur-age', 
                                options=[{'label':i, 'value': i}for i in config.AGE],
                                value= config.AGE[-1],
                                clearable=False ),
                ], style={'width': '24%', 'display': 'inline-block'}),
            ], style={'padding': 10}),
            html.Div([
                html.Div([
                    html.Label("Pathologie - Niveau 1 :"),
                    dcc.Dropdown(
                        id='selecteur-patho-niv1',
                        options=[{'label': i, 'value': i} for i in NIV1_OPTIONS],
                        value=NIV1_OPTIONS,
                        clearable=False
                    ),
                ], style={'width': '24%', 'display': 'inline-block'}),
                
                
                html.Div([
                    html.Label("Pathologie - Niveau 2 :"),
                    dcc.Dropdown(
                        id='selecteur-patho-niv2',
                        clearable=False
                    ),
                ], style={'width': '24%', 'display': 'inline-block'}),

                
                html.Div([
                    html.Label("Pathologie - Niveau 3 :"),
                    dcc.Dropdown(
                        id='selecteur-patho-niv3',
                        clearable=False
                    ),
                ], style={'width': '24%', 'display': 'inline-block'}),
            ], style={'padding': 10}),

            html.Iframe(id='carte-dynamique', style={"width": "100%", "height": "650px", "border": "none"})
        ])

        return layout
    
    @staticmethod
    def register_callback(app, PATHOS_HIERARCHY):
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
        [Input('selecteur-carte', 'value'),
        Input('selecteur-annee', 'value'),
        Input('selecteur-patho-niv1', 'value'),
        Input('selecteur-patho-niv2', 'value'),
        Input('selecteur-patho-niv3', 'value'),
        Input('selecteur-sexe', 'value'),
        Input('selecteur-age', 'value')]
        )
        def mettre_a_jour_carte(carte,annee, patho_niv1, patho_niv2, patho_niv3, sexe, age): 
            if patho_niv1 is None:
                return "" 
            
            # Lecture BDD
            df_filtre = lecture_BDD_carte(carte, annee, patho_niv1,  patho_niv2, patho_niv3,sexe,age )
            
            # Création du titre et de la carte
            titre = f"Total Patients ({sexe}, {patho_niv1}, {annee})"
            return creation_carte(carte,df_filtre, titre)

