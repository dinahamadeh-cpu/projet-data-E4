import sqlite3
import pandas as pd
import config
import os

def lecture_BDD_carte(carte_selectionnee,annee_selectionnee, patho_niveau1_selectionne, patho_niveau2_selectionne,patho_niveau3_selectionne, sexe_selectionne, age_selectionne):

    if carte_selectionnee == "region":
        col_code = config.COL_CODE_REGION
    if carte_selectionnee == "departement":
        col_code = config.COL_CODE_DEPT
    
    conn = sqlite3.connect(config.db_name)
    query = f"""
    SELECT 
        {col_code}, 
        SUM({config.COL_NTOP}) AS Ntop,
        SUM({config.COL_NPOP}) AS Npop,
        AVG({config.COL_PREV}) AS prev
    FROM {config.table_name}
    WHERE {config.COL_PATHO_NV1} = "{patho_niveau1_selectionne}"
        AND {config.COL_PATHO_NV2} = "{patho_niveau2_selectionne}"
        AND {config.COL_PATHO_NV3} = "{patho_niveau3_selectionne}"
        AND {config.COL_SEXE} = "{sexe_selectionne}"
        AND {config.COL_TRANCHE_AGE} = '{age_selectionne}' 
        AND {config.COL_ANNEE} = {annee_selectionnee}
    GROUP BY {col_code}
    """
    df_data= pd.read_sql_query(query, conn)
    conn.close()
    return df_data

def lecture_BDD_histo():
    db_path = config.db_name
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Base introuvable : {db_path}")

    conn = sqlite3.connect(db_path)
    query = f"SELECT * FROM {config.table_name}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df