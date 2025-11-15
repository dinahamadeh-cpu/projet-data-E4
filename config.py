# nom des dossiers et fichiers utilisés dans le projet
zip_file_name="data/rawdata/raw.zip"
csv_in_zip = "effectifs.csv"
db_name="data/clean/cleaned_Data.db"
table_name="effectifs"
output_csv_path="data/clean/effectifs_cleaned.csv"
dept_geojson="data/geojson/departement.geojson"
region_geojson="data/geojson/region.geojson"

#nom des colonnes de la base de données
COL_ANNEE = 'annee'
COL_CODE_DEPT = 'dept'    #colonne code département
COL_CODE_REGION = 'region' #colonne code région
COL_NPOP = 'Npop'       
COL_NTOP = 'Ntop'
COL_PREV = 'prev'
COL_NV_PRIORITAIRE = 'Niveau prioritaire'
COL_SEXE = 'libelle_sexe'
COL_TRANCHE_AGE = 'cla_age_5'
COL_PATHO_NV1 = 'patho_niv1'
COL_PATHO_NV2 = 'patho_niv2'
COL_PATHO_NV3 = 'patho_niv3'
COL_TRI = 'tri'
COL_TOP = 'top'

ANNEE= [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
SEXE = ['hommes', 'femmes', 'tous sexes']
AGE=['0-4', '5-9', '10-14','15-19', '20-24', '25-29','30-34', '35-39', '40-44','45-49','50-54','55-59','60-64','65-69','70-74','75-79', '80-84','85-89','90-94', '95+', 'tsage']

#valeurs pour la cartographie
COORDS = (48.7453229, 2.5073644) #centre de la france
MAP_ZOOM_START = 6
