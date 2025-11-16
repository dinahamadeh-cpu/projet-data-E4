import sqlite3
import pandas as pd
import config
import os
import ast


def _format_sql_value(value):
    """
    Analyse un filtre pouvant être :
    - un string simple
    - une liste réelle
    - un string représentant une liste (cas fréquent avec Dash)

    Retourne une condition SQL du type :
        = 'Valeur'
    ou :
        IN ('v1','v2','v3')
    """

    # --- 1) Si value est une liste Python → OK
    if isinstance(value, list):
        values = value

    # --- 2) Si value est une chaîne représentant une liste → on la convertit
    elif isinstance(value, str) and value.startswith("[") and value.endswith("]"):
        try:
            values = ast.literal_eval(value)
        except Exception:
            values = [value]  # fallback
    else:
        values = [value]

    # Nettoyage + échappement des apostrophes
    cleaned = []
    for v in values:
        if v is None:
            continue
        v = str(v).replace("'", "''")  # échappement SQL
        cleaned.append(v)

    # Une seule valeur → =
    if len(cleaned) == 1:
        return f"= '{cleaned[0]}'"

    # Plusieurs valeurs → IN (...)
    values_sql = ", ".join([f"'{v}'" for v in cleaned])
    return f"IN ({values_sql})"


def lecture_BDD_carte(carte_selectionnee, annee_selectionnee,
                      patho_niveau1_selectionne, patho_niveau2_selectionne,
                      patho_niveau3_selectionne, sexe_selectionne, age_selectionne):

    if carte_selectionnee == "region":
        col_code = config.COL_CODE_REGION
    if carte_selectionnee == "departement":
        col_code = config.COL_CODE_DEPT

    # Construire les conditions SQL
    cond_nv1 = _format_sql_value(patho_niveau1_selectionne)
    cond_nv2 = _format_sql_value(patho_niveau2_selectionne)
    cond_nv3 = _format_sql_value(patho_niveau3_selectionne)
    cond_sexe = _format_sql_value(sexe_selectionne)
    cond_age = _format_sql_value(age_selectionne)

    conn = sqlite3.connect(config.db_name)

    query = f"""
        SELECT 
            {col_code}, 
            SUM({config.COL_NTOP}) AS Ntop,
            SUM({config.COL_NPOP}) AS Npop,
            AVG({config.COL_PREV}) AS prev
        FROM {config.table_name}
        WHERE {config.COL_PATHO_NV1} {cond_nv1}
          AND {config.COL_PATHO_NV2} {cond_nv2}
          AND {config.COL_PATHO_NV3} {cond_nv3}
          AND {config.COL_SEXE} {cond_sexe}
          AND {config.COL_TRANCHE_AGE} {cond_age}
          AND {config.COL_ANNEE} = {annee_selectionnee}
        GROUP BY {col_code}
    """

    df_data = pd.read_sql_query(query, conn)
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
