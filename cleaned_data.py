import pandas as pd
import os

os.makedirs("data/cleaned", exist_ok=True)

# Chemin du fichier brut
file_path = "C:\\Users\\achve\\OneDrive - ESIEE Paris\\Documents\\projet_data\\data\\raw\\effectifs.csv"

# Lire le CSV correctement
df = pd.read_csv(file_path, sep=";", quotechar='"', on_bad_lines='skip', low_memory=False)

# Supprimer les lignes où l'année est manquante
df = df[df['annee'].notna()]

#Remplacer les pathologies manquantes par "Non défini"
for col in ['patho_niv1', 'patho_niv2', 'patho_niv3', 'top']:
    df[col] = df[col].fillna("Non défini")
    df[col] = df[col].replace('', 'Non défini')


# Compléter classe et libellé si une des deux est manquante
df['cla_age_5'] = df['cla_age_5'].fillna(df['libelle_classe_age'])
df['libelle_classe_age'] = df['libelle_classe_age'].fillna(df['cla_age_5'])

#Remplacer NaN ou chaînes vides dans les variables catégorielles
categ_cols = ['sexe', 'libelle_sexe', 'libelle_classe_age', 'region', 'dept']
for col in categ_cols:
    df[col] = df[col].fillna("Non défini")
    df[col] = df[col].replace('', 'Non défini')
    

# Condition secret statistique : ne pas recalculer si Ntop < 11 car prev= Ntop/Npop 
mask_prev = df['prev'].isna() & df['Ntop'].notna() & df['Npop'].notna() & (df['Ntop'] >= 11)
df.loc[mask_prev, 'prev'] = 100 * (df.loc[mask_prev, 'Ntop'] / df.loc[mask_prev, 'Npop'])

# Recalculer Ntop si manquant
mask_Ntop = df['Ntop'].isna() & df['prev'].notna() & df['Npop'].notna() & ((df['prev'] * df['Npop'] / 100) >= 11)
df.loc[mask_Ntop, 'Ntop'] = (df.loc[mask_Ntop, 'prev'] * df.loc[mask_Ntop, 'Npop'] / 100).round().astype('Int64')

# Recalculer Npop si manquant
mask_Npop = df['Npop'].isna() & df['Ntop'].notna() & df['prev'].notna() & (df['Ntop'] >= 11)
df.loc[mask_Npop, 'Npop'] = (df.loc[mask_Npop, 'Ntop'] / (df.loc[mask_Npop, 'prev'] / 100)).round().astype('Int64')

# Remplacer les NaN ou chaînes vides dans 'Niveau prioritaire' et 'tri'
df['Niveau prioritaire'] = df['Niveau prioritaire'].fillna('Non défini').replace('', 'Non défini')
df['tri'] = df['tri'].fillna(-1)

# 6. Sauvegarde
output_file = "C:\\Users\\achve\\OneDrive - ESIEE Paris\\Documents\\projet_data\\data\\cleaned\\data_patologies_cleaned.csv"
df.to_csv(output_file, index=False)
print(f"\n Données nettoyées sauvegardées dans : {output_file}")