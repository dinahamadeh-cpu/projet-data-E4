import folium
import geopandas as gpd
import config


def creation_carte(carte, df, titre_legende="Prévalence moyenne (en %) des pathologies"):
    if carte not in ["departement", "region"]:
        raise ValueError("Le type de carte doit être 'departement' ou 'region'.")

    if carte == "region":
        gdf = gpd.read_file(config.region_geojson)
        RO = config.COL_CODE_REGION

        # Agrégation par région
        df_agg = df.groupby(RO, as_index=False).agg(
            Ntop=("Ntop", "sum"),
            Npop=("Npop", "sum"),
            prev=("prev", "mean"),
        )

        tooltip_label = "Région : "

    elif carte == "departement":
        gdf = gpd.read_file(config.dept_geojson)
        RO = config.COL_CODE_DEPT
        df_agg = df.copy()  # pas d'agrégation

        tooltip_label = "Département : "

    merged = gdf.merge(df_agg, left_on="code", right_on=RO, how="left")

    m = folium.Map(location=config.COORDS, zoom_start=config.MAP_ZOOM_START, tiles="CartoDB Positron")

    folium.Choropleth(
        geo_data=merged.to_json(),
        name="Pathologies",
        data=df_agg,
        columns=[RO, "prev"],
        key_on="feature.properties.code",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=titre_legende,
    ).add_to(m)

    style_function = lambda x: {"fillColor": "#ffffff", "color": "#000000", "fillOpacity": 0.0, "weight": 0.3}
    highlight_function = lambda x: {"fillColor": "#000000", "color": "#000000", "fillOpacity": 0.3, "weight": 0.1}

    # Infobulles dynamiques
    tooltip_fields = ["nom", "Ntop", "Npop", "prev"]
    tooltip_aliases = [
        tooltip_label,
        "Total patients pris en charge : ",
        "Population totale : ",
        "Prévalence moyenne (%) : "
    ]

    tooltip = folium.GeoJson(
        merged,
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=tooltip_fields,
            aliases=tooltip_aliases,
            localize=True,
            sticky=False,
            labels=True,
            style=("background-color: white; color: #333333; "
                   "font-family: Arial; font-size: 12px; padding: 10px;"),
        ),
    )
    m.add_child(tooltip)
    m.keep_in_front(tooltip)

    return m.get_root().render()