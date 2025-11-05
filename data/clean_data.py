import config
import pandas as pd
import sqlite3 
import zipfile
import io
import os

def load_data_from_zip(zip_path, csv_filename):
    print(f"Tentative de lecture du fichier à l'emplacement absolu: {os.path.abspath(zip_path)}")
    with zipfile.ZipFile(zip_path) as z:
        with z.open(csv_filename) as f:
            data=io.BytesIO(f.read())
            df=pd.read_csv(data, sep=";", dtype={'dept': str, 'region': str})
    return df


def clean_data(df):
    """
    Effectue toutes les étapes de nettoyage selon les nouvelles règles spécifiées.
    (La logique de reconstitution des effectifs Ntop/Npop est maintenue pour le secret statistique.)
    """
    if df.empty:
        return df

    Mapping_sexe = {1: 'hommes', 2: 'femmes', 9: 'tous sexes'}
    inv_sexe_mapping = {v: k for k, v in Mapping_sexe.items()}
    Mapping_Age = {'de 0 à 4 ans': '0-4', 'de 5 à 9 ans': '5-9', 'de 10 à 14 ans': '10-14',
                   'de 15 à 19 ans': '15-19', 'de 20 à 24 ans': '20-24', 'de 25 à 29 ans': '25-29',
                   'de 30 à 34 ans': '30-34', 'de 35 à 39 ans': '35-39', 'de 40 à 44 ans': '40-44',
                   'de 45 à 49 ans': '45-49', 'de 50 à 54 ans': '50-54', 'de 55 à 59 ans': '55-59',
                   'de 60 à 64 ans': '60-64', 'de 65 à 69 ans': '65-69', 'de 70 à 74 ans': '70-74',
                   'de 75 à 79 ans': '75-79', 'de 80 à 84 ans': '80-84', 'de 85 à 89 ans': '85-89', 
                   'de 90 à 94 ans': '90-94', 'plus de 95 ans': '95+', 'tous âges': 'tsage'}
    
    
    # Ntop, Npop en Int (avec support de NaN pour ne pas perdre les données valides)
    df['Ntop'] = pd.to_numeric(df['Ntop'], errors='coerce').astype('Int64')
    df['Npop'] = pd.to_numeric(df['Npop'], errors='coerce').astype('Int64')
    
    # prev en float
    df['prev'] = pd.to_numeric(df['prev'], errors='coerce').astype(float)
    
    # sexe en Int (force Int64 pour supporter NaN)
    df['sexe'] = pd.to_numeric(df['sexe'], errors='coerce').astype('Int64')
    
    # dept et région en string (déjà fait au chargement, on réassure)
    for col in ['dept', 'region']:
        df[col] = df[col].astype(str)
        
    # --- RÈGLES DE SUPPRESSION DES LIGNES (dropna) ---
    
    # Définition des colonnes critiques pour la suppression (règles combinées)
    
    # 1. Colonnes qui doivent être absolument présentes (année, patho_niv1, patho_niv2)
    critical_cols_1 = ['annee', 'patho_niv1', 'patho_niv2', 'dept', 'region']
    df_clean = df.dropna(subset=critical_cols_1).copy()
    
    # 2. Règle complexe : (Natop et prev) OU (Npop et Ntop) OU (prev et Npop) ne sont PAS vides
    # On garde les lignes où AU MOINS DEUX des trois mesures d'effectif/prévalence sont non-NaN.
    effectif_cols = ['Ntop', 'Npop', 'prev']
    
    # On compte le nombre de valeurs non-NaN par ligne dans ces trois colonnes.
    # On garde si le compte est >= 2.
    df_clean['effectif_count'] = df_clean[effectif_cols].notna().sum(axis=1)
    df_clean = df_clean[df_clean['effectif_count'] >= 2].drop(columns=['effectif_count']).copy()
    
    # 3. Suppression lorsque dept = 999
    df_clean = df_clean[df_clean['dept'] != '999'].copy()


    # --- RÈGLES DE COMPLÉMENTARITÉ ET RECONSTITUTION ---

    # Remplacer les pathologies manquantes par "Non défini" (important pour les filtres suivants)
    for col in ['patho_niv3', 'top']: # patho_niv1 et patho_niv2 sont gérées par dropna
        df_clean[col] = df_clean[col].fillna("Non défini").replace('', 'Non défini')
        
    # 1. classe d'âge = libelle age (Compléter si une des deux est manquante)
    mask_libelle_age_na = df_clean['libelle_classe_age'].isna() | (df_clean['libelle_classe_age'].astype(str).str.strip() == '')
    df_clean.loc[mask_libelle_age_na, 'libelle_classe_age'] = df_clean.loc[mask_libelle_age_na, 'cla_age_5'].map(Mapping_Age)
    
    mask_cla_age_na = df_clean['cla_age_5'].isna()
    df_clean.loc[mask_cla_age_na, 'cla_age_5'] = df_clean.loc[mask_cla_age_na, 'libelle_classe_age'].map({v: k for k, v in Mapping_Age.items()})
    
    # 2. sexe = libelle sex (Compléter si une des deux est manquante)
    # Compléter libelle_sexe si sexe est présent
    mask_libelle_na = df_clean['libelle_sexe'].isna() | (df_clean['libelle_sexe'].astype(str).str.strip() == '')
    df_clean.loc[mask_libelle_na, 'libelle_sexe'] = df_clean.loc[mask_libelle_na, 'sexe'].map(Mapping_sexe)

    # Compléter sexe si libelle_sexe est présent
    mask_sexe_na = df_clean['sexe'].isna()
    df_clean.loc[mask_sexe_na, 'sexe'] = df_clean.loc[mask_sexe_na, 'libelle_sexe'].map(inv_sexe_mapping).astype('Int64')
    
    # 3. prev = Ntop / Npop (Reconstitution en respectant le secret statistique)
    
    # Reconstitution de prev
    mask_prev = df_clean['prev'].isna() & df_clean['Ntop'].notna() & df_clean['Npop'].notna() & (df_clean['Ntop'] >= 11)
    df_clean.loc[mask_prev, 'prev'] = 100 * (df_clean.loc[mask_prev, 'Ntop'] / df_clean.loc[mask_prev, 'Npop'])
    
    # Reconstitution de Ntop et Npop (Maintien de la logique de robustesse statistique)
    Ntop_estim = (df_clean['prev'] * df_clean['Npop'] / 100)
    mask_Ntop = df_clean['Ntop'].isna() & df_clean['prev'].notna() & df_clean['Npop'].notna() & (Ntop_estim >= 11)
    df_clean.loc[mask_Ntop, 'Ntop'] = Ntop_estim[mask_Ntop].round().astype('Int64')

    mask_Npop = df_clean['Npop'].isna() & df_clean['Ntop'].notna() & df_clean['prev'].notna() & (df_clean['Ntop'] >= 11)
    df_clean.loc[mask_Npop, 'Npop'] = (df_clean.loc[mask_Npop, 'Ntop'] / (df_clean.loc[mask_Npop, 'prev'] / 100)).round().astype('Int64')


    # 4. Garder le premier caractère de la chaine Niveau prioritaire
    df_clean['Niveau prioritaire'] = df_clean['Niveau prioritaire'].astype(str).str.strip()
    # Applique str[0] uniquement si la chaîne n'est pas vide
    df_clean.loc[df_clean['Niveau prioritaire'].str.len() > 0, 'Niveau prioritaire'] = \
        df_clean.loc[df_clean['Niveau prioritaire'].str.len() > 0, 'Niveau prioritaire'].str[0]
    
    # --- FINALISATION ---
    
    # Suppression des doublons totaux (sur toutes les colonnes après nettoyage)
    df_clean.drop_duplicates(keep='first', inplace=True)
    
    # Remplissage final des chaînes de caractères qui pourraient être vides/NaN après les opérations
    categ_cols_final = ['Niveau prioritaire']
    for col in categ_cols_final:
        df_clean[col] = df_clean[col].fillna("Non défini").replace('', 'Non défini')
    
    return df_clean

def main():
    db_dir = os.path.dirname(config.db_name)
    
    #créer le dossier si non existant
    if db_dir: 
        os.makedirs(db_dir, exist_ok=True)
        print(f"Dossier de sortie vérifié/créé : {db_dir}")

    # connexion à la base de données 
    con= sqlite3.connect(config.db_name)

    try:
        df=load_data_from_zip(config.zip_file_name, config.csv_in_zip)
        df_cleaned=clean_data(df)
    except Exception as e:
        print(f"An error occurred: {e}")
        con.close()
        return
    
    df_cleaned.to_sql(config.table_name, con, if_exists='replace', index=False)
    print(f"Cleaned data saved to database at {config.db_name} in table {config.table_name}")
    con.close()

if __name__ == "__main__":
    main()