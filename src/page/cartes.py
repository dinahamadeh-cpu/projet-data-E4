import folium
import geopandas as gpd
import config


def creation_carte(carte,df, titre_legende="Prévalence des pathologies par département"):
    if carte not in ["departement", "region"]:
        raise ValueError("Le type de carte doit être 'departement' ou 'region'.")
    if carte == "region":
        gdf = gpd.read_file(config.region_geojson)
        RO = config.COL_CODE_REGION
    if carte == "departement":
        gdf = gpd.read_file(config.dept_geojson)
        RO = config.COL_CODE_DEPT

    merged = gdf.merge(df, left_on="code", right_on=RO, how="left")

    m = folium.Map(location=config.COORDS, zoom_start=config.MAP_ZOOM_START, tiles="CartoDB Positron")

    # Ajout de la couche choroplèthe (couleur selon Ntop)
    folium.Choropleth(
        geo_data=merged.to_json(),
        name="Pathologies par département",
        data=df,
        columns=[RO, "Ntop"],
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

    return m.get_root().render()
