import numpy as np
import pandas as pd


"""
def haversine_distance(lat1, lon1, lat2, lon2) -> float:
    Distance en km entre deux points GPS.
    R = 6371  # rayon Terre
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)

    a = (
            np.sin(dphi / 2) ** 2
            + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2) ** 2
    )
    return 2 * R * np.arcsin(np.sqrt(a))


def nearest_professional(
        df: pd.DataFrame, lat: float, lon: float
) -> pd.Series:
    Retourne le professionnel le plus proche.
    distances = haversine_distance(
        lat, lon, df["latitude"], df["longitude"]
    )
    idx = distances.idxmin()
    result = df.loc[idx].copy()
    result["distance_km"] = distances.loc[idx]
    return result

"""
def estimate_travel_time(distance_km: float, speed_kmh: float = 40) -> float:
    """Temps d'accès estimé en minutes."""
    return (distance_km / speed_kmh) * 60
