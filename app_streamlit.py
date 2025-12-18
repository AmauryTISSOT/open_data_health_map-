import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
from utils.data import load_data

# Configuration
st.set_page_config(page_title="HealthMap", layout="wide", page_icon="🏥")
st.title("🏥 HealthMap — Répartition des professionnels de santé en France")

# Chargement des données
df = load_data()

# Métrique globale
st.metric("Nombre total de professionnels de santé", f"{len(df):,}")

# --- Préparation des données pour la carte ---
# On regroupe par localisation (code_postal + coordonnées)
df_map = (
    df.groupby(["code_postal", "commune", "latitude", "longitude"])
    .agg(
        nombre_pros=("nom", "count"),
        # Gestion sécurisée des NaN dans profession
        professions_exemples=(
            "profession",
            lambda x: ", ".join(
                [str(p) for p in x.unique()[:3] if pd.notna(p)] or ["Aucune profession"]
            ),
        ),
    )
    .reset_index()
)

# Suppression des lignes sans coordonnées GPS
df_map = df_map.dropna(subset=["latitude", "longitude"])

# Vérification qu'il reste des données
if df_map.empty:
    st.error(
        "Aucune donnée avec coordonnées GPS valide. Vérifiez le merge avec les codes postaux."
    )
    st.stop()

# --- Carte interactive ---
st.subheader("🗺️ Carte de répartition des professionnels de santé")

fig_map = px.scatter_mapbox(
    df_map,
    lat="latitude",
    lon="longitude",
    size="nombre_pros",
    color="nombre_pros",
    hover_name="commune",
    hover_data={
        "code_postal": True,
        "nombre_pros": True,
        "professions_exemples": True,
        "latitude": False,
        "longitude": False,
    },
    zoom=5,
    height=700,
    color_continuous_scale=px.colors.sequential.Plasma,
    size_max=40,
    title="Professionnels de santé par localisation (France métropolitaine)",
)

fig_map.update_layout(
    mapbox_style="open-street-map",
    margin={"r": 0, "t": 50, "l": 0, "b": 0},
    coloraxis_colorbar=dict(title="Nb de pros"),
)

st.plotly_chart(fig_map, use_container_width=True)

# --- Bonus : Top 10 communes ---
st.markdown("---")
st.subheader("🏆 Top 10 des communes les plus dotées en professionnels de santé")

top_10 = df_map.nlargest(10, "nombre_pros")[
    ["commune", "code_postal", "nombre_pros", "professions_exemples"]
]
top_10 = top_10.reset_index(drop=True)
top_10.index += 1  # Numérotation à partir de 1
st.dataframe(top_10, use_container_width=True)


# --- Nouvelle carte : Répartition par région ---
st.markdown("---")
st.subheader("🗺️ Répartition des professionnels de santé par région")


# Fonction pour mapper code postal → région (via département)
def get_region_from_cp(cp: str):
    if pd.isna(cp) or not cp.isdigit() or len(cp) < 2:
        return "Inconnue"
    dept = cp[:2]
    region_map = {
        "01": "Auvergne-Rhône-Alpes",
        "03": "Auvergne-Rhône-Alpes",
        "07": "Auvergne-Rhône-Alpes",
        "15": "Auvergne-Rhône-Alpes",
        "26": "Auvergne-Rhône-Alpes",
        "38": "Auvergne-Rhône-Alpes",
        "42": "Auvergne-Rhône-Alpes",
        "43": "Auvergne-Rhône-Alpes",
        "63": "Auvergne-Rhône-Alpes",
        "69": "Auvergne-Rhône-Alpes",
        "73": "Auvergne-Rhône-Alpes",
        "74": "Auvergne-Rhône-Alpes",
        "02": "Hauts-de-France",
        "59": "Hauts-de-France",
        "60": "Hauts-de-France",
        "62": "Hauts-de-France",
        "80": "Hauts-de-France",
        "21": "Bourgogne-Franche-Comté",
        "25": "Bourgogne-Franche-Comté",
        "39": "Bourgogne-Franche-Comté",
        "58": "Bourgogne-Franche-Comté",
        "70": "Bourgogne-Franche-Comté",
        "71": "Bourgogne-Franche-Comté",
        "89": "Bourgogne-Franche-Comté",
        "90": "Bourgogne-Franche-Comté",
        "22": "Bretagne",
        "29": "Bretagne",
        "35": "Bretagne",
        "56": "Bretagne",
        "18": "Centre-Val de Loire",
        "28": "Centre-Val de Loire",
        "36": "Centre-Val de Loire",
        "37": "Centre-Val de Loire",
        "41": "Centre-Val de Loire",
        "45": "Centre-Val de Loire",
        "08": "Grand Est",
        "10": "Grand Est",
        "51": "Grand Est",
        "52": "Grand Est",
        "54": "Grand Est",
        "55": "Grand Est",
        "57": "Grand Est",
        "67": "Grand Est",
        "68": "Grand Est",
        "88": "Grand Est",
        "75": "Île-de-France",
        "77": "Île-de-France",
        "78": "Île-de-France",
        "91": "Île-de-France",
        "92": "Île-de-France",
        "93": "Île-de-France",
        "94": "Île-de-France",
        "95": "Île-de-France",
        "14": "Normandie",
        "27": "Normandie",
        "50": "Normandie",
        "61": "Normandie",
        "76": "Normandie",
        "16": "Nouvelle-Aquitaine",
        "17": "Nouvelle-Aquitaine",
        "19": "Nouvelle-Aquitaine",
        "23": "Nouvelle-Aquitaine",
        "24": "Nouvelle-Aquitaine",
        "33": "Nouvelle-Aquitaine",
        "40": "Nouvelle-Aquitaine",
        "47": "Nouvelle-Aquitaine",
        "64": "Nouvelle-Aquitaine",
        "79": "Nouvelle-Aquitaine",
        "86": "Nouvelle-Aquitaine",
        "87": "Nouvelle-Aquitaine",
        "09": "Occitanie",
        "11": "Occitanie",
        "12": "Occitanie",
        "30": "Occitanie",
        "31": "Occitanie",
        "32": "Occitanie",
        "34": "Occitanie",
        "46": "Occitanie",
        "48": "Occitanie",
        "65": "Occitanie",
        "66": "Occitanie",
        "81": "Occitanie",
        "82": "Occitanie",
        "44": "Pays de la Loire",
        "49": "Pays de la Loire",
        "53": "Pays de la Loire",
        "72": "Pays de la Loire",
        "85": "Pays de la Loire",
        "04": "Provence-Alpes-Côte d'Azur",
        "05": "Provence-Alpes-Côte d'Azur",
        "06": "Provence-Alpes-Côte d'Azur",
        "13": "Provence-Alpes-Côte d'Azur",
        "83": "Provence-Alpes-Côte d'Azur",
        "84": "Provence-Alpes-Côte d'Azur",
        "2A": "Corse",
        "2B": "Corse",
    }
    return region_map.get(dept, "Inconnue")


# Ajouter la colonne région
df["region"] = df["code_postal"].apply(get_region_from_cp)

# Compter le nombre de pros par région
df_region = df["region"].value_counts().reset_index()
df_region.columns = ["nom", "nombre_pros"]

# Charger le GeoJSON des régions (directement depuis URL)
geojson_url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/regions.geojson"
response = requests.get(geojson_url)
geojson_data = response.json()

# Carte choroplèthe
fig_region = px.choropleth_mapbox(
    df_region,
    geojson=geojson_data,
    locations="nom",
    featureidkey="properties.nom",  # Clé dans le GeoJSON
    color="nombre_pros",
    color_continuous_scale="Viridis",
    mapbox_style="open-street-map",
    zoom=4.5,
    center={"lat": 46.5, "lon": 2},
    opacity=0.6,
    hover_name="nom",
    hover_data={"nombre_pros": True},
    title="Nombre de professionnels de santé par région",
    height=700,
)

fig_region.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})
st.plotly_chart(fig_region, use_container_width=True)

# Bonus : Tableau des régions
st.subheader("📊 Tableau par région")
st.dataframe(
    df_region.sort_values("nombre_pros", ascending=False).reset_index(drop=True),
    use_container_width=True,
)

# --- Nouvelle carte : Répartition par département ---
st.markdown("---")
st.subheader("🗺️ Répartition des professionnels de santé par département")


# Fonction pour extraire le code département du code postal
def get_dept_from_cp(cp: str):
    if pd.isna(cp):
        return "Inconnu"
    cp_str = str(cp).strip()
    if len(cp_str) >= 2:
        dept = cp_str[:2]
        # Cas spécial Corse (2A/2B) et DOM (97x)
        if dept == "20":
            if cp_str.startswith("2A"):
                return "2A"
            elif cp_str.startswith("2B"):
                return "2B"
        if dept == "97":
            return cp_str[:3]  # 971, 972, etc.
        return dept
    return "Inconnu"


# Ajouter la colonne département
df["departement"] = df["code_postal"].apply(get_dept_from_cp)

# Compter le nombre de pros par département
df_dept = df["departement"].value_counts().reset_index()
df_dept.columns = ["code", "nombre_pros"]

# Ajouter le nom du département pour un affichage plus lisible (optionnel, mapping simple)
dept_names = {
    "01": "Ain",
    "02": "Aisne",
    "03": "Allier",
    "04": "Alpes-de-Haute-Provence",
    "05": "Hautes-Alpes",
    "06": "Alpes-Maritimes",
    "07": "Ardèche",
    "08": "Ardennes",
    "09": "Ariège",
    "10": "Aube",
    "11": "Aude",
    "12": "Aveyron",
    "13": "Bouches-du-Rhône",
    "14": "Calvados",
    "15": "Cantal",
    "16": "Charente",
    "17": "Charente-Maritime",
    "18": "Cher",
    "19": "Corrèze",
    "2A": "Corse-du-Sud",
    "2B": "Haute-Corse",
    "21": "Côte-d'Or",
    "22": "Côtes-d'Armor",
    "23": "Creuse",
    "24": "Dordogne",
    "25": "Doubs",
    "26": "Drôme",
    "27": "Eure",
    "28": "Eure-et-Loir",
    "29": "Finistère",
    "30": "Gard",
    "31": "Haute-Garonne",
    "32": "Gers",
    "33": "Gironde",
    "34": "Hérault",
    "35": "Ille-et-Vilaine",
    "36": "Indre",
    "37": "Indre-et-Loire",
    "38": "Isère",
    "39": "Jura",
    "40": "Landes",
    "41": "Loir-et-Cher",
    "42": "Loire",
    "43": "Haute-Loire",
    "44": "Loire-Atlantique",
    "45": "Loiret",
    "46": "Lot",
    "47": "Lot-et-Garonne",
    "48": "Lozère",
    "49": "Maine-et-Loire",
    "50": "Manche",
    "51": "Marne",
    "52": "Haute-Marne",
    "53": "Mayenne",
    "54": "Meurthe-et-Moselle",
    "55": "Meuse",
    "56": "Morbihan",
    "57": "Moselle",
    "58": "Nièvre",
    "59": "Nord",
    "60": "Oise",
    "61": "Orne",
    "62": "Pas-de-Calais",
    "63": "Puy-de-Dôme",
    "64": "Pyrénées-Atlantiques",
    "65": "Hautes-Pyrénées",
    "66": "Pyrénées-Orientales",
    "67": "Bas-Rhin",
    "68": "Haut-Rhin",
    "69": "Rhône",
    "70": "Haute-Saône",
    "71": "Saône-et-Loire",
    "72": "Sarthe",
    "73": "Savoie",
    "74": "Haute-Savoie",
    "75": "Paris",
    "76": "Seine-Maritime",
    "77": "Seine-et-Marne",
    "78": "Yvelines",
    "79": "Nièvre",
    "80": "Somme",
    "81": "Tarn",
    "82": "Tarn-et-Garonne",
    "83": "Var",
    "84": "Vaucluse",
    "85": "Vendée",
    "86": "Vienne",
    "87": "Haute-Vienne",
    "88": "Vosges",
    "89": "Yonne",
    "90": "Territoire de Belfort",
    "91": "Essonne",
    "92": "Hauts-de-Seine",
    "93": "Seine-Saint-Denis",
    "94": "Val-de-Marne",
    "95": "Val-d'Oise",
    "971": "Guadeloupe",
    "972": "Martinique",
    "973": "Guyane",
    "974": "La Réunion",
    "976": "Mayotte",
}
df_dept["nom"] = (
    df_dept["code"].map(dept_names).fillna("Département " + df_dept["code"])
)

# Charger le GeoJSON des départements
geojson_url_dept = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson"
response_dept = requests.get(geojson_url_dept)
geojson_dept = response_dept.json()

# Carte choroplèthe par département
fig_dept = px.choropleth_mapbox(
    df_dept,
    geojson=geojson_dept,
    locations="code",
    featureidkey="properties.code",  # Clé dans le GeoJSON : "code" pour les départements
    color="nombre_pros",
    color_continuous_scale="Viridis",
    mapbox_style="open-street-map",
    zoom=5,
    center={"lat": 46.5, "lon": 2},
    opacity=0.6,
    hover_name="nom",
    hover_data={"code": True, "nombre_pros": True},
    title="Nombre de professionnels de santé par département",
    height=700,
)

fig_dept.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})
st.plotly_chart(fig_dept, use_container_width=True)

# Bonus : Tableau des départements
st.subheader("📊 Tableau par département")
st.dataframe(
    df_dept.sort_values("nombre_pros", ascending=False).reset_index(drop=True),
    use_container_width=True,
)
