import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os


file_path = "C:\\Users\\achve\\OneDrive - ESIEE Paris\\Documents\\projet_data\\data\\cleaned\\data_patologies_cleaned.csv"
df = pd.read_csv(file_path, low_memory=False)

print(f"Données chargées : {df.shape}")
print(df.info())

#  Analyse de la variable 'tri'
print("\n Statistiques descriptives de 'tri' :")
print(df["tri"].describe())

# Section NumPy : calculs "manuels"
tri_array = np.array(df["tri"].dropna())
print("\n Statistiques via NumPy :")
print(f"Moyenne : {np.mean(tri_array):.2f}")
print(f"Médiane : {np.median(tri_array):.2f}")
print(f"Écart-type : {np.std(tri_array):.2f}")
print(f"Quantiles (25%, 50%, 75%) : {np.quantile(tri_array, [0.25, 0.5, 0.75])}")

# Visualisation brute Matplotlib
plt.figure(figsize=(8, 4))
plt.hist(tri_array, bins=50, color="skyblue", edgecolor="black")
plt.title("Distribution de la variable 'tri'")
plt.xlabel("Valeur de tri")
plt.ylabel("Fréquence")
plt.grid(True)
plt.show()


# Relation entre 'tri' et le niveau prioritaire


# Nettoyage du champ "Niveau prioritaire"
df["niveau_prioritaire_clean"] = df["Niveau prioritaire"].astype(str).str.extract(r"(\d)").astype(float)

print("\n Distribution du niveau prioritaire :")
print(df["niveau_prioritaire_clean"].value_counts(dropna=False))

# Moyenne et écart-type de 'tri' selon le niveau prioritaire
tri_by_priority = df.groupby("niveau_prioritaire_clean")["tri"].describe()
print("\n Statistiques de tri par niveau prioritaire :")
print(tri_by_priority)

# Boxplot (Seaborn)
plt.figure(figsize=(6, 4))
sns.boxplot(x="niveau_prioritaire_clean", y="tri", data=df, palette="coolwarm")
plt.title("Distribution de 'tri' selon le niveau prioritaire")
plt.xlabel("Niveau prioritaire")
plt.ylabel("Tri")
plt.show()


#Moyenne de tri par pathologie

#pathologie 1
tri_patho = df.groupby("patho_niv1")["tri"].mean().sort_values(ascending=False)
print("\n Tri moyen par pathologie 1(top 10) :")
print(tri_patho.head(10))

plt.figure(figsize=(10, 6))
sns.barplot(y=tri_patho.head(10).index, x=tri_patho.head(10).values, palette="viridis")
plt.title("Top 10 pathologies avec le tri moyen le plus élevé")
plt.xlabel("Tri moyen")
plt.ylabel("Pathologie")
plt.show()

#pathologie 2

tri_patho = df.groupby("patho_niv2")["tri"].mean().sort_values(ascending=False)
print("\n Tri moyen par pathologie 2 (top 10) :")
print(tri_patho.head(10))

plt.figure(figsize=(10, 6))
sns.barplot(y=tri_patho.head(10).index, x=tri_patho.head(10).values, palette="viridis")
plt.title("Top 10 pathologies avec le tri moyen le plus élevé")
plt.xlabel("Tri moyen")
plt.ylabel("Pathologie")
plt.show()

#pathologie 3
tri_patho = df.groupby("patho_niv3")["tri"].mean().sort_values(ascending=False)
print("\n Tri moyen par pathologie 3 (top 10) :")
print(tri_patho.head(10))

plt.figure(figsize=(10, 6))
sns.barplot(y=tri_patho.head(10).index, x=tri_patho.head(10).values, palette="viridis")
plt.title("Top 10 pathologies avec le tri moyen le plus élevé") 
plt.xlabel("Tri moyen")
plt.ylabel("Pathologie")
plt.show()

# Tri selon le sexe et la classe d’âge

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

# Corrélation avec les variables numériques

num_cols = ["Ntop", "Npop", "prev", "tri"]
corr_matrix = df[num_cols].corr()
print("\n Matrice de corrélation :")
print(corr_matrix)

plt.figure(figsize=(6, 4))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Corrélation entre les variables numériques")
plt.show()


# Sauvegarde d’un résumé synthétique

summary_text = f"""
SYNTHÈSE EXPLORATION DES DONNÉES
===================================

Nombre total de lignes : {df.shape[0]:,}
Nombre total de colonnes : {df.shape[1]}

🔹 Variable tri :
- Moyenne (Pandas) : {df['tri'].mean():.2f}
- Médiane (NumPy) : {np.median(tri_array):.2f}
- Écart-type : {df['tri'].std():.2f}
- Valeurs min/max : {df['tri'].min()} / {df['tri'].max()}

🔹 Niveau prioritaire :
{df['niveau_prioritaire_clean'].value_counts()}

🔹 Top pathologies (tri moyen élevé) :
{tri_patho.head(5).to_string()}

🔹 Corrélation principales :
{corr_matrix.to_string()}

"""

output_dir = "C:\\Users\\achve\\OneDrive - ESIEE Paris\\Documents\\projet_data\\outputs"
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "exploration_summary.txt")

with open(output_file, "w", encoding="utf-8") as f:
    f.write(summary_text)

print(f"\n Rapport exploratoire sauvegardé dans : {output_file}")


#à tester
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
# import os

# # 🔹 Créer les dossiers outputs et plots si nécessaire
# os.makedirs("outputs", exist_ok=True)
# os.makedirs("outputs/plots", exist_ok=True)

# # 🔹 Charger les données
# file_path = "C:\\Users\\achve\\OneDrive - ESIEE Paris\\Documents\\projet_data\\data\\cleaned\\data_patologies_cleaned.csv"
# df = pd.read_csv(file_path)
# print(f" Données chargées : {df.shape}")

# # 🔹 Extraire niveau prioritaire numérique pour analyse
# df['niveau_prioritaire_clean'] = df['Niveau prioritaire'].astype(str).str.extract(r'(\d)').astype(float)

# # 🔹 Analyse de tri
# tri_stats = df['tri'].describe()
# print("\nStatistiques de 'tri' :")
# print(tri_stats)

# # 🔹 Tri par niveau prioritaire
# tri_by_niveau = df.groupby('niveau_prioritaire_clean')['tri'].describe()
# print("\nTri par niveau prioritaire :")
# print(tri_by_niveau)

# # 🔹 Boxplot tri par niveau prioritaire
# plt.figure(figsize=(8,5))
# sns.boxplot(x="niveau_prioritaire_clean", y="tri", data=df,
#             hue="niveau_prioritaire_clean", palette="coolwarm", legend=False)
# plt.title("Distribution de tri selon le niveau prioritaire")
# plt.savefig("outputs/plots/tri_par_niveau_prioritaire.png")
# plt.close()

# # 🔹 Top 10 pathologies par niveau de tri
# for level in ['patho_niv1','patho_niv2','patho_niv3']:
#     tri_patho = df.groupby(level)['tri'].mean().sort_values(ascending=False)
#     print(f"\nTop 10 tri moyen pour {level} :")
#     print(tri_patho.head(10))
    
#     plt.figure(figsize=(8,6))
#     sns.barplot(y=tri_patho.head(10).index, x=tri_patho.head(10).values,
#                 palette="viridis")
#     plt.title(f"Top 10 tri moyen pour {level}")
#     plt.xlabel("Tri moyen")
#     plt.ylabel(level)
#     plt.tight_layout()
#     plt.savefig(f"outputs/plots/top10_tri_{level}.png")
#     plt.close()

# # 🔹 Tri par sexe et âge
# plt.figure(figsize=(10,5))
# sns.boxplot(x="libelle_sexe", y="tri", data=df, palette="pastel")
# plt.title("Tri selon le sexe")
# plt.savefig("outputs/plots/tri_sexe.png")
# plt.close()

# plt.figure(figsize=(12,5))
# sns.boxplot(x="libelle_classe_age", y="tri", data=df, palette="magma")
# plt.title("Tri selon la classe d'âge")
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.savefig("outputs/plots/tri_age.png")
# plt.close()

# # 🔹 Tri par région et département
# plt.figure(figsize=(10,5))
# sns.boxplot(x="region", y="tri", data=df, palette="cool")
# plt.title("Tri selon la région")
# plt.savefig("outputs/plots/tri_region.png")
# plt.close()

# plt.figure(figsize=(12,5))
# top_dept = df['dept'].value_counts().nlargest(20).index
# sns.boxplot(x="dept", y="tri", data=df[df['dept'].isin(top_dept)], palette="cool")
# plt.title("Tri pour les 20 départements les plus fréquents")
# plt.xticks(rotation=90)
# plt.tight_layout()
# plt.savefig("outputs/plots/tri_dept.png")
# plt.close()

# # 🔹 Heatmap tri moyen par pathologie × sexe
# patho_sexe = df.pivot_table(index='patho_niv1', columns='libelle_sexe', values='tri', aggfunc='mean')
# plt.figure(figsize=(12,8))
# sns.heatmap(patho_sexe, cmap="YlGnBu", annot=False)
# plt.title("Tri moyen par pathologie N1 et sexe")
# plt.tight_layout()
# plt.savefig("outputs/plots/tri_patho_sexe.png")
# plt.close()

# # 🔹 Heatmap tri moyen par pathologie × âge
# patho_age = df.pivot_table(index='patho_niv1', columns='libelle_classe_age', values='tri', aggfunc='mean')
# plt.figure(figsize=(14,10))
# sns.heatmap(patho_age, cmap="YlOrBr", annot=False)
# plt.title("Tri moyen par pathologie N1 et classe d'âge")
# plt.tight_layout()
# plt.savefig("outputs/plots/tri_patho_age.png")
# plt.close()

# # 🔹 Corrélations
# corr = df[['Ntop','Npop','prev','tri']].corr()
# plt.figure(figsize=(6,5))
# sns.heatmap(corr, annot=True, cmap="coolwarm")
# plt.title("Corrélations entre Ntop, Npop, prev et tri")
# plt.savefig("outputs/plots/corr_matrix.png")
# plt.close()
# print("\nMatrice de corrélation :")
# print(corr)

# # 🔹 Scatter plots Ntop/Npop vs prev
# plt.figure(figsize=(6,5))
# sns.scatterplot(x='Npop', y='prev', data=df.sample(5000))
# plt.title("prev vs Npop")
# plt.savefig("outputs/plots/prev_vs_Npop.png")
# plt.close()

# plt.figure(figsize=(6,5))
# sns.scatterplot(x='Ntop', y='prev', data=df.sample(5000))
# plt.title("prev vs Ntop")
# plt.savefig("outputs/plots/prev_vs_Ntop.png")
# plt.close()

# # 🔹 Export résumé textuel
# summary_text = []
# summary_text.append(f"Données : {df.shape}")
# summary_text.append(f"Colonnes : {df.columns.tolist()}")
# summary_text.append("\nTri par niveau prioritaire :")
# summary_text.append(tri_by_niveau.to_string())
# summary_text.append("\nTop 10 patho_niv1 par tri :")
# summary_text.append(tri_patho.head(10).to_string())
# summary_text.append("\nMatrice de corrélation :")
# summary_text.append(corr.to_string())

# output_summary_file = "outputs/exploration_summary.txt"
# with open(output_summary_file, "w", encoding="utf-8") as f:
#     f.write("\n".join(summary_text))

# print(f"\n Résumé exploratoire et plots sauvegardés dans outputs/")
