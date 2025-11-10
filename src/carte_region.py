import folium
import pandas as pd
import geopandas as gpd
import sqlite3
import config
from src.hierarchiepatho import get_patho_hierarchy


def lecture_BDD(annee_selectionnee, patho_niveau1_selectionne, patho_niveau2_selectionne,patho_niveau3_selectionne, sexe_selectionne):

    

    conn = sqlite3.connect(config.db_name)
    query = f"""
    SELECT 
        {config.COL_CODE_REGION}, 
        SUM({config.COL_NTOP}) AS Ntop,
        SUM({config.COL_NPOP}) AS Npop,
        AVG({config.COL_PREV}) AS prev
    FROM {config.table_name}
    WHERE {config.COL_PATHO_NV1} = "{patho_niveau1_selectionne}"
        AND {config.COL_PATHO_NV2} = "{patho_niveau2_selectionne}"
        AND {config.COL_PATHO_NV3} = "{patho_niveau3_selectionne}"
        AND {config.COL_SEXE} = "{sexe_selectionne}"
        AND {config.COL_ANNEE} = {annee_selectionnee}
    GROUP BY {config.COL_CODE_REGION}
    """
    df_data= pd.read_sql_query(query, conn)
    conn.close()
    return df_data

def creation_carte_region(df, titre_legende):

    gdf_region = gpd.read_file(config.region_geojson)

    #jointure entre le GeoDataFrame des régions et les données
    merged = gdf_region.merge( df, left_on='code', right_on=config.COL_CODE_REGION, how='left')

    # création de la carte
    m = folium.Map(location=config.COORDS, zoom_start=config.MAP_ZOOM_START, tiles='CartoDB Positron')

    folium.Choropleth(
        geo_data=merged.to_json(),
        name='Données par Region',
        data= df,
        columns=[config.COL_CODE_REGION,'Ntop'],
        key_on='feature.properties.code',  # Assurez-vous que cela correspond à la structure de votre GeoJSON
        fill_color='YlGn',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=titre_legende,
    ).add_to(m)

    style_function = lambda x: {'fillColor': '#ffffff', 
                                      'color':'#000000',
                                        'fillOpacity': 0.0,
                                        'weight': 0.0}
    highlight_function = lambda x: {'fillColor': '#000000', 
                                          'color':'#000000',
                                           'fillOpacity': 0.50,
                                           'weight': 0.1}
   
    tooltip_content=folium.features.GeoJsonTooltip(
            fields=['nom', 'Ntop', 'Npop','prev'],
            aliases=['Région : ', 'Total patient prit en charge : ', 'Total Patients : ','Prévalence Moyenne (%) : '],
            style=("background-color: white; color: #333333; font-family: Arial; font-size: 12px; padding: 10px;")
    )
     
    tooltip = folium.features.GeoJson(
        merged,
        style_function=style_function,
        control=False,
        highlight_function=highlight_function,
        tooltip=tooltip_content
    )

    m.add_child(tooltip)
    m.keep_in_front(tooltip)
    m.save('map.html')
    
    return m.get_root().render()