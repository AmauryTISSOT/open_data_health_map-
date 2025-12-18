import plotly.express as px
import pandas as pd


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
