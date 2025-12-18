import pandas as pd
import json

# 1. Charger le fichier Parquet
df_prof = pd.read_parquet(
    "./data/professionnels_sante.parquet"
)  # Remplace par ton chemin

# Normaliser code_postal comme string 5 chiffres
df_prof["code_postal"] = df_prof["code_postal"].astype(str).str.zfill(5)

# 2. Charger le JSON
with open("./data/communes-france-avec-polygon-2025.json", "r", encoding="utf-8") as f:
    data = json.load(f)

df_communes = pd.DataFrame(data["data"])

# Sélectionner seulement les colonnes utiles
df_communes = df_communes[
    ["code_postal", "latitude_mairie", "longitude_mairie", "nom_standard"]
]

# Normaliser code_postal
df_communes["code_postal"] = df_communes["code_postal"].astype(str).str.zfill(5)

# Optionnel : renommer pour plus de clarté
df_communes = df_communes.rename(
    columns={"latitude_mairie": "latitude", "longitude_mairie": "longitude"}
)

# 3. Merge (left pour garder tous les professionnels)
df_merged = df_prof.merge(
    df_communes[["code_postal", "latitude", "longitude"]], on="code_postal", how="left"
)

# 4. Vérifier les manquants (pour debug)
manquants = df_merged[df_merged["latitude"].isna()]
if not manquants.empty:
    print(f"{len(manquants)} lignes sans coordonnées trouvées.")
    print("Exemples de communes/code_postal concernés :")
    print(manquants[["code_postal", "commune"]].drop_duplicates().head(20))
    # Tu pourras ensuite corriger manuellement ou avec une autre source si besoin

# 5. Sauvegarder le nouveau fichier
df_merged.to_parquet("./data/fichier_professionnels_avec_coords.parquet", index=False)

print("Fusion terminée !")
print(df_merged[["code_postal", "commune", "latitude", "longitude"]].head(10))
