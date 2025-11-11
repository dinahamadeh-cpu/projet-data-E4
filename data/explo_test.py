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

