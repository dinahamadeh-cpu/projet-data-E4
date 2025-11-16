import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import config

# =============================
#  Préparation des chemins
# =============================
output_dir = os.path.join("data", "outputs", "dept_analysis")
os.makedirs(output_dir, exist_ok=True)

# =============================
#  Chargement depuis la base SQLite
# =============================
print(f"Chargement des données depuis la base : {config.db_name}")
conn = sqlite3.connect(config.db_name)
df = pd.read_sql_query(f"SELECT * FROM {config.table_name}", conn)
conn.close()

print(f"Données chargées : {df.shape}")

# =============================
#  Vérifications de base
# =============================
if "dept" not in df.columns:
    raise ValueError("La colonne 'dept' est absente du jeu de données.")
if "tri" not in df.columns:
    raise ValueError("La colonne 'tri' est absente du jeu de données.")

# =============================
# Histogrammes simples
# =============================

plt.figure(figsize=(12, 6))
sns.histplot(df["dept"], bins=len(df["dept"].unique()), kde=False, color="skyblue")
plt.title("Répartition des observations par département")
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "repartition_dept.png"))
plt.close()

