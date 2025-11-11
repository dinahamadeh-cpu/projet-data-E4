import os
import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import config

# =============================
#  Préparation des chemins
# =============================
output_dir = os.path.join("data", "outputs", "relations")
os.makedirs(output_dir, exist_ok=True)

# =============================
#  Chargement des données
# =============================
print(f"Chargement des données depuis la base : {config.db_name}")
conn = sqlite3.connect(config.db_name)
df = pd.read_sql_query(f"SELECT * FROM {config.table_name}", conn)
conn.close()

print(f"Données chargées : {df.shape}")

# =============================
#  Nettoyage léger
# =============================
# On garde les colonnes utiles pour les analyses relationnelles
cols = ["annee", "patho_niv1", "libelle_classe_age", "libelle_sexe", "region", "tri", "prev", "Ntop", "Npop"]
df = df[[c for c in cols if c in df.columns]].dropna()

# =============================
# Pathologie en fonction de la classe d'âge
# =============================
plt.figure(figsize=(12, 6))
sns.countplot(data=df, x="libelle_classe_age", hue="patho_niv1", palette="tab20")
plt.title("Répartition des pathologies en fonction de la classe d'âge")
plt.xlabel("Classe d'âge")
plt.ylabel("Nombre de cas")
plt.legend(title="Pathologie", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "patho_par_classe_age.png"))
plt.close()

#  Pathologie en fonction du sexe
# =============================
plt.figure(figsize=(10, 6))
sns.countplot(data=df, x="libelle_sexe", hue="patho_niv1", palette="Paired")
plt.title("Répartition des pathologies selon le sexe")
plt.xlabel("Sexe")
plt.ylabel("Nombre de cas")
plt.legend(title="Pathologie", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "patho_par_sexe.png"))
plt.close()



