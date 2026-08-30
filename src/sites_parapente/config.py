"""Constantes de cadrage : CRS, périmètre, chemins de données.

Les poids de l'overlay et les chemins des rasters bruts arriveront
aux étapes MNT / occupation du sol — pas ici.
"""

from pathlib import Path

# Lambert 2008, standard SPW pour les couches wallonnes récentes.
CRS_EPSG = 3812
CRS_NAME = "Lambert 2008"

EXTENT_NAME = "Ardenne"
PROVINCES: tuple[str, ...] = ("Namur", "Luxembourg", "Liège")

ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
DATA_LOCAL = ROOT / "data" / "local"
ETL_DIR = ROOT / "etl"
QGIS_DIR = ROOT / "qgis"
SQL_DIR = ROOT / "sql"
