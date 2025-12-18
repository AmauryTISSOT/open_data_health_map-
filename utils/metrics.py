import pandas as pd


def professionals_by_departement(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nombre de professionnels de santé par département.
    """
    if "departement" not in df.columns:
        raise ValueError("Colonne 'departement' absente")

    agg = (
        df.groupby("departement")
        .size()
        .reset_index(name="nb_professionnels")
        .sort_values("nb_professionnels", ascending=False)
    )

    return agg
