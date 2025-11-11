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

# =============================
#  Tri moyen par département
# =============================
tri_dept = df.groupby("dept")["tri"].mean().sort_values(ascending=False)
plt.figure(figsize=(14, 6))
sns.barplot(x=tri_dept.index, y=tri_dept.values, palette="coolwarm")
plt.title("Tri moyen par département")
plt.xlabel("Département")
plt.ylabel("Tri moyen")
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "tri_moyen_par_dept.png"))
plt.close()

# =============================
#  Ntop moyen par département
# =============================
ntop_dept = df.groupby("dept")["Ntop"].mean().sort_values(ascending=False)
plt.figure(figsize=(14, 6))
sns.barplot(x=ntop_dept.index, y=ntop_dept.values, palette="magma")
plt.title("Effectif pris en charge (Ntop moyen) par département")
plt.xlabel("Département")
plt.ylabel("Ntop moyen")
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "ntop_moyen_par_dept.png"))
plt.close()

# =============================
# Prévalence moyenne par département
# =============================
prev_dept = df.groupby("dept")["prev"].mean().sort_values(ascending=False)
plt.figure(figsize=(14, 6))
sns.barplot(x=prev_dept.index, y=prev_dept.values, palette="viridis")
plt.title("Prévalence moyenne par département")
plt.xlabel("Département")
plt.ylabel("Prévalence (%)")
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "prev_moyenne_par_dept.png"))
plt.close()

# =============================
# Classe d'âge dominante par département
# =============================
age_dept = df.groupby("dept")["libelle_classe_age"].agg(lambda x: x.mode()[0] if not x.mode().empty else None)
age_dept = age_dept.dropna()

plt.figure(figsize=(14, 6))
sns.countplot(y="libelle_classe_age", data=df, order=df["libelle_classe_age"].value_counts().index, palette="Spectral")
plt.title("Répartition des classes d'âge (tous départements confondus)")
plt.xlabel("Nombre d’observations")
plt.ylabel("Classe d’âge")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "repartition_age_globale.png"))
plt.close()

# =============================
#  Pathologies les plus fréquentes par département
# =============================
patho_counts = (
    df.groupby(["dept", "patho_niv1"])
    .size()
    .reset_index(name="count")
)

top_patho = (
    patho_counts.groupby("dept")
    .apply(lambda x: x.nlargest(1, "count"))
    .reset_index(drop=True)
)

plt.figure(figsize=(14, 6))
sns.barplot(x="dept", y="count", hue="patho_niv1", data=top_patho, dodge=False, palette="tab20")
plt.title("Pathologie la plus fréquente par département")
plt.xlabel("Département")
plt.ylabel("Nombre de cas")
plt.xticks(rotation=90)
plt.legend(title="Pathologie", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "top_patho_par_dept.png"))
plt.close()

# =============================
#  Idées supplémentaires
# =============================
#  Tri moyen par sexe et département
tri_sexe_dept = df.groupby(["dept", "libelle_sexe"])["tri"].mean().reset_index()
plt.figure(figsize=(14, 6))
sns.barplot(x="dept", y="tri", hue="libelle_sexe", data=tri_sexe_dept, palette="pastel")
plt.title("Tri moyen par sexe et département")
plt.xlabel("Département")
plt.ylabel("Tri moyen")
plt.xticks(rotation=90)
plt.legend(title="Sexe")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "tri_par_sexe_et_dept.png"))
plt.close()

#  Tri moyen par classe d’âge et département
tri_age_dept = df.groupby(["dept", "libelle_classe_age"])["tri"].mean().reset_index()
plt.figure(figsize=(14, 6))
sns.lineplot(x="dept", y="tri", hue="libelle_classe_age", data=tri_age_dept, legend=False, alpha=0.5)
plt.title("Tri moyen par classe d’âge et département")
plt.xlabel("Département")
plt.ylabel("Tri moyen")
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "tri_par_age_et_dept.png"))
plt.close()

print(f"\n Tous les graphiques ont été enregistrés dans : {output_dir}")
# =============================