import pandas as pd
import sqlite3 
import zipfile
import io
import os
import config  

#fonction de chargement de données depuis un fichier zip
def load_data_from_zip(zip_path, csv_filename):    
    print(f"Tentative de lecture du fichier à l'emplacement absolu: {os.path.abspath(zip_path)}")
    with zipfile.ZipFile(zip_path) as z:
        with z.open(csv_filename) as f:
            data = io.BytesIO(f.read())
            # Forcer dept et region en string à la lecture pour éviter les problèmes avec '999'
            df = pd.read_csv(data, sep=";", dtype={'dept': str, 'region': str}, low_memory=False)
    return df


def clean_data(df):
    
    if df.empty:
        return df

    # Mappings pour sexe
    Mapping_sexe = {1: 'hommes', 2: 'femmes', 9: 'tous sexes'}
    inv_sexe_mapping = {v: k for k, v in Mapping_sexe.items()}
    
    # Mapping Âge 
    Mapping_Age = {'de 0 à 4 ans': '0-4', 'de 5 à 9 ans': '5-9', 'de 10 à 14 ans': '10-14',
                   'de 15 à 19 ans': '15-19', 'de 20 à 24 ans': '20-24', 'de 25 à 29 ans': '25-29',
                   'de 30 à 34 ans': '30-34', 'de 35 à 39 ans': '35-39', 'de 40 à 44 ans': '40-44',
                   'de 45 à 49 ans': '45-49', 'de 50 à 54 ans': '50-54', 'de 55 à 59 ans': '55-59',
                   'de 60 à 64 ans': '60-64', 'de 65 à 69 ans': '65-69', 'de 70 à 74 ans': '70-74',
                   'de 75 à 79 ans': '75-79', 'de 80 à 84 ans': '80-84', 'de 85 à 89 ans': '85-89', 
                   'de 90 à 94 ans': '90-94', 'plus de 95 ans': '95+', 'tous âges': 'tsage'}
    inv_age_mapping = {v: k for k, v in Mapping_Age.items()} 

    df['Ntop'] = pd.to_numeric(df['Ntop'], errors='coerce').astype('Int64')
    df['Npop'] = pd.to_numeric(df['Npop'], errors='coerce').astype('Int64')
    df['prev'] = pd.to_numeric(df['prev'], errors='coerce').astype(float)
    df['sexe'] = pd.to_numeric(df['sexe'], errors='coerce').astype('Int64')
    

    # Suppression si colonnes année, patho_niv1/2, dept/region sont vides
    critical_cols_1 = ['annee', 'patho_niv1', 'patho_niv2', 'dept', 'region']
    df_clean = df.dropna(subset=critical_cols_1).copy()
    
    # On garde les lignes où AU MOINS DEUX des trois mesures d'effectif/prévalence sont non-NaN
    effectif_cols = ['Ntop', 'Npop', 'prev']
    df_clean['effectif_count'] = df_clean[effectif_cols].notna().sum(axis=1)
    df_clean = df_clean[df_clean['effectif_count'] >= 2].drop(columns=['effectif_count']).copy()
    
    # Suppression lorsque dept = 999 car signifie erreur 
    df_clean = df_clean[df_clean['dept'] != '999'].copy()

    # Remplacer les pathologies manquantes par "Non défini"
    for col in ['patho_niv3', 'top']:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].fillna("Non défini").replace('', 'Non défini')
            
    # Classe d'âge / Libellé âge 
    mask_libelle_age_na = df_clean['libelle_classe_age'].isna() | (df_clean['libelle_classe_age'].astype(str).str.strip() == '')
    df_clean.loc[mask_libelle_age_na, 'libelle_classe_age'] = df_clean.loc[mask_libelle_age_na, 'cla_age_5'].map(inv_age_mapping)
    
    mask_cla_age_na = df_clean['cla_age_5'].isna()
    df_clean.loc[mask_cla_age_na, 'cla_age_5'] = df_clean.loc[mask_cla_age_na, 'libelle_classe_age'].map(Mapping_Age)
    
    # Sexe / Libellé Sexe
    mask_libelle_na = df_clean['libelle_sexe'].isna() | (df_clean['libelle_sexe'].astype(str).str.strip() == '')
    df_clean.loc[mask_libelle_na, 'libelle_sexe'] = df_clean.loc[mask_libelle_na, 'sexe'].map(Mapping_sexe)

    mask_sexe_na = df_clean['sexe'].isna()
    df_clean.loc[mask_sexe_na, 'sexe'] = df_clean.loc[mask_sexe_na, 'libelle_sexe'].map(inv_sexe_mapping).astype('Int64')
    
    # Reconstitution des effectifs (Ntop >= 11)
    mask_prev = df_clean['prev'].isna() & df_clean['Ntop'].notna() & df_clean['Npop'].notna() & (df_clean['Ntop'] >= 11)
    df_clean.loc[mask_prev, 'prev'] = 100 * (df_clean.loc[mask_prev, 'Ntop'] / df_clean.loc[mask_prev, 'Npop'])
    
    # Reconstitution de Ntop et Npop si manquantes
    Ntop_estim = (df_clean['prev'] * df_clean['Npop'] / 100)
    mask_Ntop = df_clean['Ntop'].isna() & df_clean['prev'].notna() & df_clean['Npop'].notna() & (Ntop_estim >= 11)
    df_clean.loc[mask_Ntop, 'Ntop'] = Ntop_estim[mask_Ntop].round().astype('Int64')

    mask_Npop = df_clean['Npop'].isna() & df_clean['Ntop'].notna() & df_clean['prev'].notna() & (df_clean['Ntop'] >= 11)
    df_clean.loc[mask_Npop, 'Npop'] = (df_clean.loc[mask_Npop, 'Ntop'] / (df_clean.loc[mask_Npop, 'prev'] / 100)).round().astype('Int64')


    # Garder le premier caractère de la chaine Niveau prioritaire
    if 'Niveau prioritaire' in df_clean.columns:
        df_clean['Niveau prioritaire'] = df_clean['Niveau prioritaire'].astype(str).str.strip()
        df_clean.loc[df_clean['Niveau prioritaire'].str.len() > 0, 'Niveau prioritaire'] = \
            df_clean.loc[df_clean['Niveau prioritaire'].str.len() > 0, 'Niveau prioritaire'].str[0]
    
    df_clean.drop_duplicates(keep='first', inplace=True)
    
    categ_cols_final = ['Niveau prioritaire']
    for col in categ_cols_final:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].fillna("Non défini").replace('', 'Non défini')
        
    return df_clean


def main():
    db_dir = os.path.dirname(config.db_name)
    if db_dir: 
        os.makedirs(db_dir, exist_ok=True)
        print(f"Dossier de sortie vérifié/créé : {db_dir}")

    # Connexion à la base de données 
    con = sqlite3.connect(config.db_name)

    try:
        df = load_data_from_zip(config.zip_file_name, config.csv_in_zip)
        df_cleaned = clean_data(df)
        if df_cleaned.empty:
            print("Attention : Le DataFrame est vide après le nettoyage. Aucune donnée à enregistrer.")
            return

    except Exception as e:
        print(f"Une erreur critique est survenue dans le processus de nettoyage : {e}")
        con.close()
        return
    
    con = sqlite3.connect(config.db_name)
    try:
        df_cleaned.to_sql(config.table_name, con, if_exists='replace', index=False)
        print(f"Cleaned data saved to database at {config.db_name} in table {config.table_name}")
    except Exception as e:
        print(f"Erreur lors de l'enregistrement dans la base de données : {e}")
    finally:
        con.close()

if __name__ == "__main__":
    main()