zip_file_name="data/rawdata/raw.zip"
csv_in_zip = "effectifs.csv"
db_name="data/clean/cleaned_Data.db"
table_name="effectifs"
output_csv_path="data/clean/effectifs_cleaned.csv"

# --- Colonnes principales de la BDD ---
COL_CODE_REGION = "region"          
COL_CODE_DEPT = "dept"              
COL_PATHO_NV1 = "patho_niv1"
COL_PATHO_NV2 = "patho_niv2"
COL_PATHO_NV3 = "patho_niv3"
COL_NTOP = "Ntop"
COL_NPOP = "Npop"
COL_PREV = "prev"
COL_SEXE = "libelle_sexe"
COL_ANNEE = "annee"

# --- Fichiers géographiques ---
region_geojson = "data/geo/regions.geojson"
dept_geojson = "data/geo/departement.geojson"

# --- Coordonnées carte ---
COORDS = [46.603354, 1.888334]  # centre de la France
MAP_ZOOM_START = 6
