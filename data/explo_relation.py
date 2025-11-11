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

# =============================
# Évolution temporelle du tri moyen par pathologie
# =============================
tri_by_year = df.groupby(["annee", "patho_niv1"])["tri"].mean().reset_index()

plt.figure(figsize=(12, 6))
sns.lineplot(data=tri_by_year, x="annee", y="tri", hue="patho_niv1", linewidth=2.0)
plt.title("Évolution du tri moyen par pathologie dans le temps")
plt.xlabel("Année")
plt.ylabel("Tri moyen")
plt.legend(title="Pathologie", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "evolution_tri_par_patho.png"))
plt.close()

# =============================
#  Évolution de la prévalence moyenne par pathologie
# =============================
prev_by_year = df.groupby(["annee", "patho_niv1"])["prev"].mean().reset_index()

plt.figure(figsize=(12, 6))
sns.lineplot(data=prev_by_year, x="annee", y="prev", hue="patho_niv1", linewidth=2.0)
plt.title("Évolution de la prévalence moyenne par pathologie")
plt.xlabel("Année")
plt.ylabel("Prévalence moyenne (%)")
plt.legend(title="Pathologie", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "evolution_prev_par_patho.png"))
plt.close()

# =============================
# Boxplot du tri selon la pathologie
# =============================
plt.figure(figsize=(12, 6))
sns.boxplot(data=df, x="patho_niv1", y="tri", palette="coolwarm")
plt.title("Distribution du tri selon la pathologie")
plt.xlabel("Pathologie")
plt.ylabel("Tri")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "boxplot_tri_par_patho.png"))
plt.close()

# =============================
# Corrélation entre variables quantitatives
# =============================
quant_vars = ["Ntop", "Npop", "prev", "tri"]
corr = df[quant_vars].corr()

plt.figure(figsize=(6, 5))
sns.heatmap(corr, annot=True, cmap="RdBu_r", center=0)
plt.title("Corrélation entre les variables numériques")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "correlation_heatmap.png"))
plt.close()

# =============================
#  Scatterplot : Ntop vs tri
# =============================
plt.figure(figsize=(8, 6))
sns.scatterplot(data=df, x="Ntop", y="tri", hue="patho_niv1", alpha=0.7, palette="tab10")
plt.title("Relation entre effectif pris en charge (Ntop) et tri, selon la pathologie")
plt.xlabel("Ntop")
plt.ylabel("Tri")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "scatter_ntop_vs_tri.png"))
plt.close()

# =============================
#  Prévalence vs Tri selon le sexe
# =============================
plt.figure(figsize=(8, 6))
sns.scatterplot(data=df, x="prev", y="tri", hue="libelle_sexe", alpha=0.7, palette="pastel")
plt.title("Relation entre prévalence et tri selon le sexe")
plt.xlabel("Prévalence (%)")
plt.ylabel("Tri")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "scatter_prev_vs_tri_par_sexe.png"))
plt.close()

print(f"\n Tous les graphiques relationnels ont été enregistrés dans : {output_dir}")

