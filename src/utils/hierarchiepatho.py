import pandas as pd
import sqlite3
import config

def get_patho_hierarchy():
    """Extrait la hiérarchie complète et les options pour les menus chaînés."""
    conn = sqlite3.connect(config.db_name)
    query = f"""
    SELECT DISTINCT {config.COL_PATHO_NV1}, {config.COL_PATHO_NV2}, {config.COL_PATHO_NV3} 
    FROM {config.table_name}
    ORDER BY {config.COL_PATHO_NV1}, {config.COL_PATHO_NV2}, {config.COL_PATHO_NV3};
    """
    df_hierarchy = pd.read_sql_query(query, conn)
    conn.close()
    
    PATHO_HIERARCHY = {}

    NIV1_OPTIONS = df_hierarchy[config.COL_PATHO_NV1].dropna().unique().tolist()
    for niv1 in NIV1_OPTIONS:
        PATHO_HIERARCHY[niv1] = {}
        df_niv2 = df_hierarchy[df_hierarchy[config.COL_PATHO_NV1] == niv1]

        for niv2 in df_niv2[config.COL_PATHO_NV2].dropna().unique(): 
            nv3_list = df_niv2[df_niv2[config.COL_PATHO_NV2] == niv2][config.COL_PATHO_NV3].dropna().unique().tolist() 
            PATHO_HIERARCHY[niv1][niv2] = nv3_list
    return PATHO_HIERARCHY, NIV1_OPTIONS