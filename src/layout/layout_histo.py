from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
from dash import dcc, html
import config
import pandas as pd

class LayoutHistogrammes:

    MAIN_STYLE = {
        'fontFamily': 'Roboto, Arial, sans-serif',
        'backgroundColor': '#f5f7fa',
        'padding': '20px'
    }

    HEADER_STYLE = {
        'textAlign': 'center',
        'color': '#1E3A8A',
        'padding': '10px 0',
        'fontSize': '2.5rem',
        'borderBottom': '3px solid #E5E7EB',
        'marginBottom': '20px'
    }

    CONTROLS_CONTAINER_STYLE = {
        'display': 'flex',
        'flexWrap': 'wrap',
        'gap': '20px',
        'padding': '20px',
        'marginBottom': '30px',
        'backgroundColor': '#FFFFFF',
        'borderRadius': '12px',
        'boxShadow': '0 4px 12px rgba(0, 0, 0, 0.08)'
    }

    CONTROL_ITEM_STYLE = {
        'flexGrow': 1,
        'minWidth': '250px'
    }

    GRAPH_CARD_STYLE = {
        'backgroundColor': '#FFFFFF',
        'borderRadius': '12px',
        'boxShadow': '0 4px 12px rgba(0, 0, 0, 0.08)',
        'padding': '15px',
        'marginBottom': '25px',
    }

    SECTION_TITLE_STYLE = {
        'color': '#374151',
        'borderLeft': '4px solid #3B82F6',
        'paddingLeft': '10px',
        'marginTop': '40px',
        'marginBottom': '20px',
        'fontSize': '1.8rem'
    }

    @staticmethod
    def create_layout(df, PATHO_LEVEL_OPTIONS):
        SEXE_OPTIONS = sorted(df[config.COL_SEXE].dropna().unique()) if config.COL_SEXE in df.columns else []

        return html.Div(style=LayoutHistogrammes.MAIN_STYLE, children=[
            html.H1("Dashboard Pathologies : Analyses Détaillées", style=LayoutHistogrammes.HEADER_STYLE),

            # CONTROLES D'UTILISATEUR
            html.Div(style=LayoutHistogrammes.CONTROLS_CONTAINER_STYLE, children=[
                html.Div(style=LayoutHistogrammes.CONTROL_ITEM_STYLE, children=[
                    html.Label("Niveau de pathologie :", style={'fontWeight': 'bold', 'color': '#4B5563'}),
                    dcc.Dropdown(
                        id='patho-level-dropdown',
                        options=PATHO_LEVEL_OPTIONS,
                        value=config.COL_PATHO_NV1,
                        clearable=False,
                    ),
                ]),
                html.Div(style=LayoutHistogrammes.CONTROL_ITEM_STYLE, children=[
                    html.Label("Choisir une pathologie :", style={'fontWeight': 'bold', 'color': '#4B5563'}),
                    dcc.Dropdown(id='patho-dropdown', style={'width': '100%'}),
                ]),
                html.Div(style=LayoutHistogrammes.CONTROL_ITEM_STYLE, children=[
                    html.Label("Choisir le sexe :", style={'fontWeight': 'bold', 'color': '#4B5563'}),
                    dcc.Dropdown(
                        id='sexe-dropdown',
                        options=[{'label': s, 'value': s} for s in SEXE_OPTIONS],
                        value=SEXE_OPTIONS[0] if SEXE_OPTIONS else None,
                        clearable=False,
                    ),
                ]),
            ]),

            # SECTION 1: Histogrammes
            html.H2("Distributions de base", style=LayoutHistogrammes.SECTION_TITLE_STYLE),
            html.Div(style=LayoutHistogrammes.GRAPH_CARD_STYLE, children=[dcc.Graph(id='graph-tri')]),
            html.Div(style=LayoutHistogrammes.GRAPH_CARD_STYLE, children=[dcc.Graph(id='graph-ntop')]),
            html.Div(style=LayoutHistogrammes.GRAPH_CARD_STYLE, children=[dcc.Graph(id='graph-prev')]),

            # ANALYSE TEMPORELLE
            html.H2("Analyse Temporelle", style=LayoutHistogrammes.SECTION_TITLE_STYLE),
            html.Div(style=LayoutHistogrammes.GRAPH_CARD_STYLE, children=[dcc.Graph(id='graph-time-series')]),

            # SECTION 3: Corrélations
            html.H2("Corrélations et Priorité", style=LayoutHistogrammes.SECTION_TITLE_STYLE),
            html.Div(style=LayoutHistogrammes.GRAPH_CARD_STYLE, children=[dcc.Graph(id='graph-scatter')]),
            html.Div(style=LayoutHistogrammes.GRAPH_CARD_STYLE, children=[dcc.Graph(id='graph-priority')]),

            # ANALYSES COMPLÉMENTAIRES
            html.H2("Analyses complémentaires", style=LayoutHistogrammes.SECTION_TITLE_STYLE),
            html.Div(style=LayoutHistogrammes.GRAPH_CARD_STYLE, children=[dcc.Graph(id='graph-treemap-region')]),
            html.Div(style=LayoutHistogrammes.GRAPH_CARD_STYLE, children=[dcc.Graph(id='graph-heatmap-age-sexe')]),
            #html.Div(style=LayoutHistogrammes.GRAPH_CARD_STYLE, children=[dcc.Graph(id='graph-density-prev-ntop')]),
            html.Div(style=LayoutHistogrammes.GRAPH_CARD_STYLE, children=[dcc.Graph(id='graph-corr-matrix')]),
        ])

    @staticmethod
    def register_callbacks(app, df, PATHO_LEVEL_OPTIONS, config):
        def create_empty_figure(title_text):
            fig = go.Figure().update_layout(
                title=title_text,
                xaxis={'visible': False},
                yaxis={'visible': False},
                height=300,
                annotations=[{
                    'text': 'Aucune donnée disponible pour cette sélection.',
                    'xref': 'paper', 'yref': 'paper',
                    'showarrow': False,
                    'font': {'size': 16, 'color': '#EF4444'}
                }]
            )
            return fig

        # Dropdown pathologie
        @app.callback(
            Output('patho-dropdown', 'options'),
            Output('patho-dropdown', 'value'),
            Input('patho-level-dropdown', 'value')
        )
        def update_patho_dropdown(selected_level_col_name):
            if selected_level_col_name not in df.columns:
                return [], None
            unique_pathos = sorted(df[selected_level_col_name].dropna().unique())
            options = [{'label': p, 'value': p} for p in unique_pathos]
            initial_value = unique_pathos[0] if unique_pathos else None
            return options, initial_value

        # Callback graphiques
        @app.callback(
            Output('graph-tri', 'figure'),
            Output('graph-ntop', 'figure'),
            Output('graph-prev', 'figure'),
            Output('graph-scatter', 'figure'),
            Output('graph-time-series', 'figure'),
            Output('graph-priority', 'figure'),
            Output('graph-treemap-region', 'figure'),
            Output('graph-heatmap-age-sexe', 'figure'),
            #Output('graph-density-prev-ntop', 'figure'),
            Output('graph-corr-matrix', 'figure'),
            Input('patho-level-dropdown', 'value'),
            Input('patho-dropdown', 'value'),
            Input('sexe-dropdown', 'value')
        )
        def update_graphs(selected_level_col_name, selected_patho, selected_sexe):
            if selected_patho is None or selected_sexe is None:
                return tuple([create_empty_figure("Sélectionnez une pathologie et un sexe")] * 10)

            df_filtered = df[
                (df[selected_level_col_name] == selected_patho) &
                (df[config.COL_SEXE] == selected_sexe)
            ].copy()

            level_name = next(
                (item['label'] for item in PATHO_LEVEL_OPTIONS if isinstance(item, dict) and item.get('value') == selected_level_col_name),
                selected_level_col_name
            )
            base_title = f"{selected_patho} ({level_name}, {selected_sexe})"

            if df_filtered.empty:
                empty_fig = create_empty_figure("Aucune donnée pour cette sélection")
                return tuple([empty_fig] * 10)

            # Histogrammes
            fig_tri = px.histogram(df_filtered, x='tri', nbins=30, title=f"Distribution du tri - {base_title}", color_discrete_sequence=['#3B82F6'])
            fig_ntop = px.histogram(df_filtered, x=config.COL_NTOP, nbins=30, title=f"Distribution du Ntop - {base_title}", color_discrete_sequence=['#F59E0B'])
            fig_prev = px.histogram(df_filtered, x=config.COL_PREV, nbins=30, title=f"Distribution de la prévalence - {base_title}", color_discrete_sequence=['#10B981'])

            # Scatter Ntop vs Prev
            fig_scatter = px.scatter(df_filtered, x=config.COL_NTOP, y=config.COL_PREV, trendline="ols", title=f"Corrélation : Prévalence vs Ntop - {base_title}")

            # Série temporelle
            COL_ANNEE = 'annee'
            if COL_ANNEE in df_filtered.columns:
                df_time = df_filtered.groupby(COL_ANNEE, as_index=False).agg(
                    mean_prev=(config.COL_PREV, 'mean'),
                    total_ntop=(config.COL_NTOP, 'sum')
                )
                fig_time_series = px.line(df_time, x=COL_ANNEE, y='mean_prev', title=f"Évolution de la Prévalence Moyenne (Année) - {base_title}", markers=True, color_discrete_sequence=['#DC2626']).update_layout(yaxis_title="Prévalence Moyenne")
            else:
                fig_time_series = create_empty_figure("Série Temporelle : Colonne 'annee' introuvable")

            # Niveau Prioritaire
            COL_NV_PRIORITAIRE = getattr(config, 'COL_NV_PRIORITAIRE', 'Niveau prioritaire')
            if COL_NV_PRIORITAIRE in df_filtered.columns:
                fig_priority = px.box(df_filtered, x=COL_NV_PRIORITAIRE, y=config.COL_PREV, title=f"Prévalence par Niveau Prioritaire - {base_title}", color_discrete_sequence=['#7C3AED']).update_xaxes(categoryorder='category ascending')
            else:
                fig_priority = create_empty_figure(f"Analyse Prioritaire : Colonne '{COL_NV_PRIORITAIRE}' introuvable")

            # Treemap régions
            if config.COL_CODE_REGION in df_filtered.columns:
                df_region_avg = df_filtered.groupby(config.COL_CODE_REGION, as_index=False)[config.COL_PREV].mean()
                fig_treemap = px.treemap(df_region_avg, path=[config.COL_CODE_REGION], values=config.COL_PREV,
                                         color=config.COL_PREV, color_continuous_scale='Viridis',
                                         title=f"Treemap prévalence par région - {base_title}")
            else:
                fig_treemap = create_empty_figure("Colonne région introuvable")

            # Heatmap âge x sexe
            if config.COL_SEXE in df_filtered.columns and 'libelle_classe_age' in df_filtered.columns:
                df_heat = df_filtered.groupby(['libelle_classe_age', config.COL_SEXE], as_index=False)[config.COL_PREV].mean()
                fig_heatmap = px.density_heatmap(df_heat, x='libelle_classe_age', y=config.COL_SEXE, z=config.COL_PREV,
                                                 color_continuous_scale='Cividis', title=f"Heatmap Prévalence par âge et sexe - {base_title}")
            else:
                fig_heatmap = create_empty_figure("Colonnes âge ou sexe introuvables")

            # Density plot Prev vs Ntop
            #fig_density = px.density_contour(df_filtered, x=config.COL_NTOP, y=config.COL_PREV, title=f"Densité Prévalence vs Ntop - {base_title}")

            # Matrice de corrélation
            corr_cols = [config.COL_NTOP, 'Npop', config.COL_PREV, 'tri']
            df_corr = df_filtered[corr_cols].corr()
            fig_corr_matrix = go.Figure(data=go.Heatmap(z=df_corr.values, x=corr_cols, y=corr_cols, colorscale='Viridis'))
            fig_corr_matrix.update_layout(title=f"Matrice de corrélation - {base_title}")

            return (
                fig_tri,
                fig_ntop,
                fig_prev,
                fig_scatter,
                fig_time_series,
                fig_priority,
                fig_treemap,
                fig_heatmap,
                #fig_density,
                fig_corr_matrix
            )