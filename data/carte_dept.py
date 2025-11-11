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
        {config.COL_CODE_DEPT} AS code_dept,
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

