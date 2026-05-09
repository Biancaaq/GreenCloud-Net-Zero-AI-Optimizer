import pandas as pd
import math
from pathlib import Path
from shapely.geometry import Point, Polygon, LineString
from shapely.ops import nearest_points
from typing import List, Dict, Union, Any

BASE_DIR = Path(__file__).resolve().parent

CITY_GPS = {
    "Alba": (46.07, 23.57), "Arad": (46.18, 21.31), "Arges": (44.86, 24.87),
    "Bacau": (46.57, 26.91), "Bihor": (47.05, 21.92), "Bistrita-Nasaud": (47.13, 24.49),
    "Botosani": (47.74, 26.66), "Braila": (45.27, 27.97), "Brasov": (45.65, 25.61),
    "Bucuresti": (44.43, 26.10), "Buzau": (45.15, 26.82), "Calarasi": (44.20, 27.33),
    "Caras-Severin": (45.29, 21.89), "Cluj": (46.77, 23.60), "Constanta": (44.17, 28.63),
    "Covasna": (45.86, 25.79), "Dambovita": (44.93, 25.45), "Dolj": (44.32, 23.80),
    "Galati": (45.43, 28.03), "Giurgiu": (43.90, 25.96), "Gorj": (45.04, 23.27),
    "Harghita": (46.36, 25.80), "Hunedoara": (45.88, 22.91), "Ialomita": (44.56, 27.37),
    "Iasi": (47.16, 27.58), "Ilfov": (44.53, 26.13), "Maramures": (47.66, 23.58),
    "Mehedinti": (44.63, 22.65), "Mures": (46.54, 24.56), "Neamt": (46.93, 26.37),
    "Olt": (44.43, 24.37), "Prahova": (44.94, 26.02), "Salaj": (47.18, 23.06),
    "Satu Mare": (47.79, 22.88), "Sibiu": (45.79, 24.15), "Suceava": (47.64, 26.25),
    "Teleorman": (43.97, 25.33), "Timis": (45.75, 21.23), "Tulcea": (45.18, 28.80),
    "Valcea": (45.10, 24.37), "Vaslui": (46.64, 27.73), "Vrancea": (45.70, 27.18)
}

CARPATHIANS_SHAPE = Polygon([
    (47.8, 23.5), (47.9, 25.5), (47.0, 26.5), (45.8, 26.8), 
    (45.4, 26.0), (45.3, 24.5), (45.1, 23.0), (44.8, 22.4), 
    (45.5, 22.0), (46.5, 22.2), (46.8, 23.0), (46.5, 23.5),
    (45.8, 24.0), (46.0, 25.5), (47.0, 25.0), (47.5, 24.0)
])

DELTA_POLY = Polygon([(45.15, 28.80), (45.50, 28.80), (45.50, 29.70), (45.15, 29.70)])

WATER_WAYS = {
    "Danube": LineString([(44.0, 22.8), (43.8, 24.0), (43.7, 25.5), (44.2, 27.5), (45.3, 28.1), (45.2, 29.5)]),
    "Olt": LineString([(45.8, 24.3), (44.5, 24.3), (43.8, 24.8)]),
    "Mures": LineString([(46.6, 25.5), (46.0, 23.5), (46.2, 21.3)]),
    "Siret": LineString([(47.9, 26.0), (46.5, 26.9), (45.4, 28.0)])
}


class MissingDataException(Exception):
    """Raised when required datasets are not found."""
    pass


class AnalysisEngine:
    _cached_df: pd.DataFrame = None

    @staticmethod
    def normalize(series: pd.Series, reverse: bool = False) -> pd.Series:
        min_v, max_v = series.min(), series.max()
        if max_v == min_v: 
            return series.apply(lambda x: 100.0)
        norm = (series - min_v) / (max_v - min_v) * 100
        return 100 - norm if reverse else norm

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate the great-circle distance between two points on the Earth surface in km."""
        R = 6371.0 # Earth radius in kilometers
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    @classmethod
    def get_distance_to_water(cls, lat: float, lon: float) -> float:
        p = Point(lat, lon)
        distances = []
        for line in WATER_WAYS.values():
            closest_pt = nearest_points(p, line)[1]
            dist = cls.haversine_distance(lat, lon, closest_pt.x, closest_pt.y)
            distances.append(dist)
        return min(distances)

    @classmethod
    def load_and_cache_data(cls) -> pd.DataFrame:
        if cls._cached_df is not None:
            return cls._cached_df.copy()

        path1 = BASE_DIR / "dataset1.csv"
        path2 = BASE_DIR / "dataset2.csv"
        if not path1.exists() or not path2.exists():
            raise MissingDataException("Datasets missing in services folder")
        
        df1 = pd.read_csv(path1)
        df2 = pd.read_csv(path2)
        
        # ETL Phase: Standardize column names before merge
        df2 = df2.rename(columns={'judet': 'county'})
        df = pd.merge(df1, df2.fillna(0), on='county', how='inner')
        df = df.rename(columns={
            'pib_mlrdron': 'gdp_billion_ron',
            'capacitate_total_instalata_mw': 'total_installed_capacity_mw'
        })
        
        # Calculate base metrics
        df['gdp_per_capita'] = (df['gdp_billion_ron'] * 1000) / df['population'].replace(0, 1)

        # Pre-compute expensive geospatial metrics to avoid per-request calculation
        def compute_geo_modifiers(row):
            lat, lon = CITY_GPS.get(row['county'], (45.0, 25.0))
            p = Point(lat, lon)
            mountain_mult = 1.8 if CARPATHIANS_SHAPE.contains(p) else 1.0
            dist = cls.get_distance_to_water(lat, lon)
            water_bonus = 0.80 if dist < 20 else 1.0
            return pd.Series([
                row['average_price_sqm'] * mountain_mult, 
                row['water_price'] * water_bonus
            ])

        df[['adj_land', 'adj_water']] = df.apply(compute_geo_modifiers, axis=1)

        # Pre-calculate normalized base metrics (since they don't depend on user weights)
        df['n1'] = cls.normalize(df['adj_land'], reverse=True)
        df['n2'] = cls.normalize(df['adj_water'], reverse=True)
        df['n3'] = cls.normalize(df['avg_temp'], reverse=True)
        df['n4'] = cls.normalize(df['green_energy'], reverse=True)
        df['n5'] = cls.normalize(df['total_installed_capacity_mw'])
        df['n6'] = cls.normalize(df['gdp_per_capita'])

        cls._cached_df = df
        return cls._cached_df.copy()

    @classmethod
    def process_ranking(cls, weights: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Calculates top locations based on provided user weights.
        :param weights: dict containing land, water, climate, green, capacity, gdp weights
        :return: list of top 3 counties with their scores and box coordinates
        """
        df = cls.load_and_cache_data()

        # Vectorized scoring using pre-normalized columns
        df['score'] = (
            df['n1'] * weights.get('land', 0.05) +
            df['n2'] * weights.get('water', 0.05) +
            df['n3'] * weights.get('climate', 0.1) +
            df['n4'] * weights.get('green', 0.2) +
            df['n5'] * weights.get('capacity', 0.5) +
            df['n6'] * weights.get('gdp', 0.1)
        )

        top_df = df.sort_values(by='score', ascending=False).head(3)
        results = []
        for i, row in enumerate(top_df.itertuples()):
            lat, lon = CITY_GPS.get(row.county, (45.0, 25.0))
            p = Point(lat, lon)
            s_lat, s_lon = (lat - 0.12, lon - 0.12) if DELTA_POLY.contains(p) else (lat + 0.05, lon + 0.05)
            results.append({
                "rank": i + 1,
                "county": row.county,
                "score": round(row.score, 2),
                "center": [lat, lon],
                "box_bounds": [
                    [s_lat - 0.03, s_lon - 0.04], 
                    [s_lat + 0.03, s_lon + 0.04]
                ]
            })
        return results