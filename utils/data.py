from pathlib import Path
import pandas as pd
import duckdb

DATA_PATH = Path("data/professionnels_sante.parquet")


def load_data() -> pd.DataFrame:
    """
    Charge les données et enrichit avec la colonne 'departement'
    dérivée du code postal.
    """
    if not DATA_PATH.exists():
        raise FileNotFoundError("Fichier parquet introuvable")

    con = duckdb.connect()
    df = con.execute(
        f"SELECT * FROM read_parquet('{DATA_PATH.as_posix()}')"
    ).df()
    con.close()

    # Nettoyage du code postal
    if "code_postal" not in df.columns:
        raise ValueError("La colonne 'code_postal' est absente du dataset")

    df["code_postal"] = df["code_postal"].astype(str).str.zfill(5)

    df["departement"] = df["code_postal"].apply(code_postal_to_departement)

    return df


def code_postal_to_departement(cp: str) -> str:
    """
    Convertit un code postal français en département.
    """
    if cp.startswith("20"):
        # Corse
        return "2A/2B"
    if cp.startswith(("97", "98")):
        # DOM-TOM
        return cp[:3]
    return cp[:2]
