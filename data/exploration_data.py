import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sqlite3
import config  # pour récupérer le chemin db_name et table_name

# --- Connexion à la base SQLite ---
con = sqlite3.connect(config.db_name)

# Charger toute la table cleanée dans un DataFrame
df = pd.read_sql_query(f"SELECT * FROM {config.table_name}", con)

con.close()

print(f"Données chargées depuis DB : {df.shape}")
print(df.info())

# --- Analyse variable 'tri' ---
print("\n Statistiques descriptives de 'tri' :")
print(df["tri"].describe())

tri_array = np.array(df["tri"].dropna())
print(f"Moyenne : {np.mean(tri_array):.2f}")
print(f"Médiane : {np.median(tri_array):.2f}")
print(f"Écart-type : {np.std(tri_array):.2f}")
print(f"Quantiles (25%, 50%, 75%) : {np.quantile(tri_array, [0.25, 0.5, 0.75])}")

# --- Distribution Matplotlib ---
plt.figure(figsize=(8, 4))
plt.hist(tri_array, bins=50, color="skyblue", edgecolor="black")
plt.title("Distribution de la variable 'tri'")
plt.xlabel("Valeur de tri")
plt.ylabel("Fréquence")
plt.grid(True)
plt.show()

# --- Niveau prioritaire ---
df["niveau_prioritaire_clean"] = df["Niveau prioritaire"].astype(str).str.extract(r"(\d)").astype(float)
print("\nDistribution du niveau prioritaire :")
print(df["niveau_prioritaire_clean"].value_counts(dropna=False))

# Moyenne et écart-type de 'tri' selon le niveau prioritaire
tri_by_priority = df.groupby("niveau_prioritaire_clean")["tri"].describe()
print("\nStatistiques de tri par niveau prioritaire :")
print(tri_by_priority)

# Boxplot
plt.figure(figsize=(6, 4))
sns.boxplot(x="niveau_prioritaire_clean", y="tri", data=df, palette="coolwarm")
plt.title("Distribution de 'tri' selon le niveau prioritaire")
plt.xlabel("Niveau prioritaire")
plt.ylabel("Tri")
plt.show()

# --- Tri moyen par pathologie ---
for level in ["patho_niv1", "patho_niv2", "patho_niv3"]:
    tri_patho = df.groupby(level)["tri"].mean().sort_values(ascending=False)
    print(f"\nTri moyen par {level} (top 10) :")
    print(tri_patho.head(10))
    
    plt.figure(figsize=(10, 6))
    sns.barplot(y=tri_patho.head(10).index, x=tri_patho.head(10).values, palette="viridis")
    plt.title(f"Top 10 pathologies avec tri moyen le plus élevé ({level})")
    plt.xlabel("Tri moyen")
    plt.ylabel("Pathologie")
    plt.show()

# --- Tri selon sexe et classe d’âge ---
plt.figure(figsize=(8, 4))
sns.boxplot(x="libelle_sexe", y="tri", data=df, palette="pastel")
plt.title("Distribution du tri selon le sexe")
plt.xlabel("Sexe")
plt.ylabel("Tri")
plt.show()

plt.figure(figsize=(10, 4))
sns.boxplot(x="libelle_classe_age", y="tri", data=df, palette="magma")
plt.title("Distribution du tri selon la classe d’âge")
plt.xlabel("Classe d’âge")
plt.ylabel("Tri")
plt.xticks(rotation=45)
plt.show()
