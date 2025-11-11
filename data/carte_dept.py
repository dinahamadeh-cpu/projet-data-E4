import folium
import pandas as pd
import geopandas as gpd
import sqlite3
import config


def lecture_BDD_dept(annee_selectionnee, patho_niveau1, patho_niveau2, patho_niveau3, sexe_selectionne):
    """
    Récupère les données agrégées par département selon les filtres sélectionnés.
    """

    conn = sqlite3.connect(config.db_name)
    query = f"""
    SELECT 
        {config.COL_CODE_DEPT} AS dept,
        SUM({config.COL_NTOP}) AS Ntop,
        SUM({config.COL_NPOP}) AS Npop,
        AVG({config.COL_PREV}) AS prev
    FROM {config.table_name}
    WHERE {config.COL_PATHO_NV1} = "{patho_niveau1}"
        AND {config.COL_PATHO_NV2} = "{patho_niveau2}"
        AND {config.COL_PATHO_NV3} = "{patho_niveau3}"
        AND {config.COL_SEXE} = "{sexe_selectionne}"
        AND {config.COL_ANNEE} = {annee_selectionnee}
    GROUP BY {config.COL_CODE_DEPT}
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    print(f" Données récupérées : {df.shape[0]} départements")
    return df


def creation_carte_departement(df, titre_legende="Prévalence des pathologies par département"):
    """
    Crée une carte Folium des pathologies en fonction des départements.
    """

    # Chargement du fond de carte des départements (GeoJSON)
    gdf_dept = gpd.read_file(config.dept_geojson)

    # Jointure avec les données
    merged = gdf_dept.merge(df, left_on="code", right_on="dept", how="left")


    # Création de la carte centrée sur la France
    m = folium.Map(location=config.COORDS, zoom_start=config.MAP_ZOOM_START, tiles="CartoDB Positron")

    # Ajout de la couche choroplèthe (couleur selon Ntop)
    folium.Choropleth(
        geo_data=merged.to_json(),
        name="Pathologies par département",
        data=df,
        columns=["dept", "Ntop"],
        key_on="feature.properties.code",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=titre_legende,
    ).add_to(m)

    # Style & surbrillance pour les tooltips
    style_function = lambda x: {
        "fillColor": "#ffffff",
        "color": "#000000",
        "fillOpacity": 0.0,
        "weight": 0.3,
    }
    highlight_function = lambda x: {
        "fillColor": "#000000",
        "color": "#000000",
        "fillOpacity": 0.3,
        "weight": 0.1,
    }

    # Ajout des infobulles
    tooltip = folium.GeoJson(
        merged,
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=["nom", "Ntop", "Npop", "prev"],
            aliases=[
                "Département : ",
                "Total patients pris en charge : ",
                "Population totale : ",
                "Prévalence moyenne (%) : ",
            ],
            localize=True,
            sticky=False,
            labels=True,
            style=(
                "background-color: white; color: #333333; "
                "font-family: Arial; font-size: 12px; padding: 10px;"
            ),
        ),
    )
    m.add_child(tooltip)
    m.keep_in_front(tooltip)

    # Sauvegarde de la carte
    output_path = "data/outputs/map_patho_departement.html"
    m.save(output_path)
    print(f" Carte enregistrée dans : {output_path}")

    return m.get_root().render()


# Exemple d’exécution directe
# ===============================
if __name__ == "__main__":
    annee = 2022
    patho1 = "Hospitalisation pour Covid-19"
    patho2 = "Hospitalisation pour Covid-19"
    patho3 = "Hospitalisation pour Covid-19"
    sexe = "femmes"  #  attention, ta base contient "hommes" et "femmes" en minuscules

    df = lecture_BDD_dept(annee, patho1, patho2, patho3, sexe)

    if df.empty:
        print(" Aucune donnée trouvée pour cette combinaison. Essaie avec d’autres filtres.")
    else:
        creation_carte_departement(df, f"Prévalence de {patho3} ({annee}) chez les {sexe}")
        print(" Carte des pathologies par département générée avec succès.")