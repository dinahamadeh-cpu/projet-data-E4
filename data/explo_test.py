# exploration_data_full_db.py
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
import sqlite3
import config  # pour récupérer db_name et table_name

# --- Créer le dossier outputs si inexistant ---
output_dir = os.path.join("data", "outputs")
os.makedirs(output_dir, exist_ok=True)

# --- Charger les données depuis la base SQLite ---
con = sqlite3.connect(config.db_name)
df = pd.read_sql_query(f"SELECT * FROM {config.table_name}", con)
con.close()

print(f"Données chargées depuis DB : {df.shape}")
print(df.dtypes)

# --- Nettoyage niveau_prioritaire pour l'analyse ---
df['niveau_prioritaire_clean'] = df['Niveau prioritaire'].astype(str).str.extract(r'(\d)').astype(float)

# --- Analyse de 'tri' ---
print("\nStatistiques descriptives de 'tri' :")
print(df['tri'].describe())

plt.figure(figsize=(10,6))
sns.histplot(df['tri'], bins=50, kde=True)
plt.title("Distribution de tri")
plt.savefig(os.path.join(output_dir, "hist_tri.png"))
plt.close()

plt.figure(figsize=(8,6))
sns.boxplot(x="niveau_prioritaire_clean", y="tri", data=df, palette="coolwarm")
plt.title("Tri par niveau prioritaire")
plt.savefig(os.path.join(output_dir, "boxplot_tri_niveau_prioritaire.png"))
plt.close()

# --- Tri moyen par pathologie ---
for col in ['patho_niv1', 'patho_niv2', 'patho_niv3']:
    tri_patho = df.groupby(col)['tri'].mean().sort_values(ascending=False)
    print(f"\nTri moyen par {col} (top 10) :\n{tri_patho.head(10)}")

    plt.figure(figsize=(10,6))
    sns.barplot(y=tri_patho.head(10).index, x=tri_patho.head(10).values, palette="viridis")
    plt.xlabel("Tri moyen")
    plt.ylabel(col)
    plt.title(f"Tri moyen par {col} (Top 10)")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"tri_{col}_top10.png"))
    plt.close()

# --- Tri selon sexe et classe d'âge ---
for col, palette in zip(['libelle_sexe', 'libelle_classe_age'], ['pastel', 'magma']):
    plt.figure(figsize=(8,6))
    sns.boxplot(x=col, y="tri", data=df, palette=palette)
    plt.title(f"Tri par {col}")
    plt.savefig(os.path.join(output_dir, f"boxplot_tri_{col}.png"))
    plt.close()
