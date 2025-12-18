import plotly.express as px
import pandas as pd
import plotly.graph_objects as go


def bar_professionals_by_departement(df_dept: pd.DataFrame):
    """
    Bar chart : nombre de professionnels par département.
    """
    return px.bar(
        df_dept,
        x="departement",
        y="nb_professionnels",
        title="Répartition des professionnels de santé par département",
        labels={
            "departement": "Département",
            "nb_professionnels": "Nombre de professionnels",
        },
    )


def create_map_chart(
    df: pd.DataFrame,
    lat: str = "latitude",
    lon: str = "longitude",
    size: str = "nb_professionnels",
    color: str = "nb_professionnels",
    hover_name: str = "ville",
    title: str = "Densité des professionnels de santé",
    zoom: int = 5,
) -> go.Figure:
    """
    Crée une carte interactive avec les positions des villes.

    Args:
        df: DataFrame contenant les données
        lat: Nom de la colonne latitude
        lon: Nom de la colonne longitude
        color: Colonne pour colorer les marqueurs (ex: température)
        hover_name: Colonne pour le nom au survol
        title: Titre de la carte
        size: Taille des marqueurs
        zoom: Niveau de zoom initial

    Returns:
        Figure Plotly
    """
    fig = px.scatter_mapbox(
        df,
        lat=lat,
        lon=lon,
        color=color,
        hover_name=hover_name,
        hover_data=["city", "summary_current_temp", "summary_current_apparent_temp"],
        zoom=zoom,
        height=600,
        title=title,
    )

    # Style gratuit (OpenStreetMap) – pas besoin de token !
    fig.update_layout(mapbox_style="open-street-map")

    # Marges propres et taille des marqueurs
    fig.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})
    fig.update_traces(marker=dict(size=size, opacity=0.9))

    # Barre de couleur plus claire
    fig.update_coloraxes(colorbar_title="Température (°C)")

    return fig
