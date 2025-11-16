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
                    dcc.Dropdown(
                        id='selecteur-annee',
                        options=[{'label': i, 'value': i} for i in config.ANNEE],
                        value=config.ANNEE[0],
                        clearable=False
                    ),
                ], style={'width': '24%', 'display': 'inline-block'}),
                html.Div([
                    html.Label("Sexe :"),
                    dcc.Dropdown(
                        id='selecteur-sexe',
                        options=[{'label': i, 'value': i} for i in config.SEXE],
                        value=config.SEXE[-1],
                        clearable=False
                    ),
                ], style={'width': '24%', 'display': 'inline-block'}),
                html.Div([
                    html.Label("Âge :"),
                    dcc.Dropdown(
                        id='selecteur-age',
                        options=[{'label': i, 'value': i} for i in config.AGE],
                        value=config.AGE[-1],
                        clearable=False
                    ),
                ], style={'width': '24%', 'display': 'inline-block'}),
            ], style={'padding': 10}),

            html.Div([
                html.Div([
                    html.Label("Pathologie - Niveau 1 :"),
                    dcc.Dropdown(
                        id='selecteur-patho-niv1',
                        options=[{'label': i, 'value': i} for i in NIV1_OPTIONS],
                        value=NIV1_OPTIONS[0] if NIV1_OPTIONS else None,
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

            # Titre dynamique au-dessus de la carte
            html.H3(id='titre-carte', style={'textAlign': 'center', 'marginTop': '10px'}),

            # Carte
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
            if not selected_niv1 or not isinstance(selected_niv1, str):
                return [], None
            if selected_niv1 in PATHOS_HIERARCHY:
                niv2_list = list(PATHOS_HIERARCHY[selected_niv1].keys())
                options = [{'label': i, 'value': i} for i in niv2_list]
                default_value = niv2_list[0] if niv2_list else None
                return options, default_value
            return [], None

        @app.callback(
            [Output('selecteur-patho-niv3', 'options'),
             Output('selecteur-patho-niv3', 'value')],
            [Input('selecteur-patho-niv1', 'value'),
             Input('selecteur-patho-niv2', 'value')]
        )
        def set_patho_niv3_options(selected_niv1, selected_niv2):
            if not selected_niv1 or not isinstance(selected_niv1, str) or \
               not selected_niv2 or not isinstance(selected_niv2, str):
                return [], None
            if selected_niv1 in PATHOS_HIERARCHY and selected_niv2 in PATHOS_HIERARCHY[selected_niv1]:
                niv3_list = PATHOS_HIERARCHY[selected_niv1][selected_niv2]
                options = [{'label': i, 'value': i} for i in niv3_list]
                default_value = niv3_list[0] if niv3_list else None
                return options, default_value
            return [], None

        @app.callback(
            [Output('titre-carte', 'children'),
             Output('carte-dynamique', 'srcDoc')],
            [Input('selecteur-carte', 'value'),
             Input('selecteur-annee', 'value'),
             Input('selecteur-patho-niv1', 'value'),
             Input('selecteur-patho-niv2', 'value'),
             Input('selecteur-patho-niv3', 'value'),
             Input('selecteur-sexe', 'value'),
             Input('selecteur-age', 'value')]
        )
        def mettre_a_jour_carte(carte, annee, patho_niv1, patho_niv2, patho_niv3, sexe, age):
            if patho_niv1 is None:
                return "", ""

            # Lecture BDD
            df_filtre = lecture_BDD_carte(carte, annee, patho_niv1, patho_niv2, patho_niv3, sexe, age)

            # Création du titre dynamique
            titre = f"Prévalence moyenne (%) - {patho_niv1} ({sexe}, {annee})"

            # Création de la carte
            carte_html = creation_carte(carte, df_filtre, titre_legende=titre)

            return titre, carte_html