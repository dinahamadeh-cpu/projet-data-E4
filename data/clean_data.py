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
            df=pd.read_csv(data,sep=";")
    return df


def clean_data(df):
    #forçage des valeurs numériques sur Ntop et npop si elles ne le sont pas déjà
    df['Ntop'] = pd.to_numeric(df['Ntop'], errors='coerce')
    df['Npop'] = pd.to_numeric(df['Npop'], errors='coerce')
    #s'assurer que dpt est une string
    df['dept']=df['dept'].astype(str)

    df.drop_duplicates(inplace=True)
    return df

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
        df=clean_data(df)
    except Exception as e:
        print(f"An error occurred: {e}")
        return
    
    df.to_sql(config.table_name, con, if_exists='replace', index=False)

    cleaning_query=f"""
        SELECT
            * FROM {config.table_name}
        WHERE
            dept <> '999'
            AND annee IS NOT NULL
            AND region IS NOT NULL
            AND dept IS NOT NULL
            AND patho_niv1 IS NOT NULL
            AND patho_niv2 IS NOT NULL
            AND Ntop IS NOT NULL
            AND Npop IS NOT NULL
            AND prev IS NOT NULL
            AND cla_age_5 IS NOT NULL
            AND libelle_sexe IS NOT NULL
            AND libelle_classe_age IS NOT NULL
        """
    df_cleaned=pd.read_sql_query(cleaning_query, con)

    output_csv_path="data/clean/effectifs_cleaned.csv"
    df_cleaned.to_csv(output_csv_path, index=False, sep=';')
    con.close()

if __name__ == "__main__":
    main()