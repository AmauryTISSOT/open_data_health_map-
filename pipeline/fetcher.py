import pandas as pd
import json

# 1. Charger le fichier Parquet des professionnels
df_prof = pd.read_parquet("./data/professionnels_sante.parquet")

# Normaliser code_postal comme string 5 chiffres
df_prof["code_postal"] = df_prof["code_postal"].astype(str).str.zfill(5)

# 2. Charger le JSON des communes
with open("./data/communes-france-avec-polygon-2025.json", "r", encoding="utf-8") as f:
    data = json.load(f)

df_communes = pd.DataFrame(data["data"])

# Sélectionner les colonnes utiles
df_communes = df_communes[
    ["code_postal", "latitude_mairie", "longitude_mairie", "nom_standard"]
]

# Normaliser code_postal
df_communes["code_postal"] = df_communes["code_postal"].astype(str).str.zfill(5)

# Renommer pour plus de clarté
df_communes = df_communes.rename(
    columns={"latitude_mairie": "latitude", "longitude_mairie": "longitude"}
)

# === CORRECTION : Dédupliquer pour avoir UNE SEULE coordonnée par code postal ===
# keep="first" garde la première commune rencontrée (souvent la principale)
df_communes_unique = df_communes.drop_duplicates(subset="code_postal", keep="first")

print(
    f"Nombre de codes postaux uniques après déduplication : {len(df_communes_unique)}"
)
# (Comparaison : avant déduplication il y en avait probablement plus)

# 3. Merge avec les coordonnées uniques
df_merged = df_prof.merge(
    df_communes_unique[["code_postal", "latitude", "longitude"]],
    on="code_postal",
    how="left",
)

# 4. Vérifier les manquants
manquants = df_merged[df_merged["latitude"].isna()]
if not manquants.empty:
    print(f"\n{len(manquants)} lignes sans coordonnées trouvées.")
    print("Exemples de codes postaux/communes concernés :")
    print(manquants[["code_postal", "commune"]].drop_duplicates().head(20))
else:
    print("\nAucune coordonnée manquante !")

# 5. Sauvegarder le fichier final
output_path = "./data/fichier_professionnels_avec_coords.parquet"
df_merged.to_parquet(output_path, index=False)

print("\nFusion terminée avec succès !")
print(f"Fichier sauvegardé : {output_path}")
print("\nAperçu des 10 premières lignes :")
print(
    df_merged[
        [
            "code_postal",
            "commune",
            "profession",
            "nom",
            "prenom",
            "latitude",
            "longitude",
        ]
    ].head(10)
)
