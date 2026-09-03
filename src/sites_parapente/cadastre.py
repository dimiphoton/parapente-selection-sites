"""Intersection overlay × cadastre : stats zonales à la parcelle.

Pas de GeoPandas : GeoJSON déjà normalisé (ETL) + numpy. Un pixel est
dans la parcelle si son centre tombe dans le polygone (ray-casting).

Le score public identifie la parcelle (capakey, commune, nature,
superficie, suitability). Un fichier local optionnel
``data/local/proprietaires.csv`` peut joindre un titulaire en mémoire ;
il n'est jamais recopié dans l'export public.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import numpy as np

from sites_parapente.config import DATA_LOCAL
from sites_parapente.landcover import ELIGIBLE_CODES

# Moyenne de suitability sous laquelle la parcelle n'est pas retenue.
# 0,20 = assez de pixels favorables pour ne pas garder une forêt avec
# trois mètres de prairie au bord.
SUITABILITY_MIN = 0.20

OWNERS_FILENAME = "proprietaires.csv"
PUBLIC_KEYS: tuple[str, ...] = (
    "capakey",
    "commune",
    "province",
    "nature",
    "superficie_m2",
    "slope_p50_deg",
    "aspect_p50_deg",
    "walous_majority",
    "landcover_open",
    "suitability",
    "geometry",
)


def _point_in_ring(x: float, y: float, ring: list[Any]) -> bool:
    """Ray-casting even-odd. ``ring`` est une liste de [x, y]."""
    inside = False
    n = len(ring)
    if n < 3:
        return False
    j = n - 1
    for i in range(n):
        xi, yi = float(ring[i][0]), float(ring[i][1])
        xj, yj = float(ring[j][0]), float(ring[j][1])
        intersects = (yi > y) != (yj > y)
        if intersects and (yj - yi) != 0.0:
            x_hit = (xj - xi) * (y - yi) / (yj - yi) + xi
            if x < x_hit:
                inside = not inside
        j = i
    return inside


def point_in_polygon(x: float, y: float, rings: list[Any]) -> bool:
    """True si le point est dans l'extérieur et hors des trous."""
    if not rings:
        return False
    if not _point_in_ring(x, y, rings[0]):
        return False
    for hole in rings[1:]:
        if _point_in_ring(x, y, hole):
            return False
    return True


def _polygons(geometry: dict[str, Any]) -> list[list[Any]]:
    gtype = geometry.get("type")
    coords = geometry.get("coordinates") or []
    if gtype == "Polygon":
        return [coords]
    if gtype == "MultiPolygon":
        return list(coords)
    return []


def rasterize_geometry(
    geometry: dict[str, Any],
    shape: tuple[int, int],
    *,
    origin_x: float,
    origin_y: float,
    cellsize: float,
) -> np.ndarray:
    """Masque booléen : True si le centre du pixel est dans la géométrie.

    Grille nord-up (ligne 0 = nord), comme ``terrain.slope_and_aspect``.
    ``origin_x`` = bord ouest, ``origin_y`` = bord nord, en mètres.

    Parameters
    ----------
    geometry :
        GeoJSON Polygon ou MultiPolygon.
    shape :
        (n_lignes, n_colonnes).
    origin_x, origin_y, cellsize :
        Géoréférencement de la tuile (Lambert 2008).

    Returns
    -------
    np.ndarray
        Booléen de ``shape``.

    Raises
    ------
    ValueError
        Si ``cellsize`` ≤ 0.
    """
    if cellsize <= 0:
        raise ValueError("cellsize doit être strictement positif")
    n_rows, n_cols = shape
    mask = np.zeros(shape, dtype=bool)
    polygons = _polygons(geometry)
    if not polygons:
        return mask

    xs: list[float] = []
    ys: list[float] = []
    for rings in polygons:
        for ring in rings:
            for pt in ring:
                xs.append(float(pt[0]))
                ys.append(float(pt[1]))
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    # Indices de colonnes/lignes qui peuvent intersecter le bbox.
    col0 = max(0, int(np.floor((min_x - origin_x) / cellsize)))
    col1 = min(n_cols, int(np.ceil((max_x - origin_x) / cellsize)))
    row0 = max(0, int(np.floor((origin_y - max_y) / cellsize)))
    row1 = min(n_rows, int(np.ceil((origin_y - min_y) / cellsize)))

    for row in range(row0, row1):
        y = origin_y - (row + 0.5) * cellsize
        for col in range(col0, col1):
            x = origin_x + (col + 0.5) * cellsize
            if any(point_in_polygon(x, y, rings) for rings in polygons):
                mask[row, col] = True
    return mask


def _circular_mean_deg(angles: np.ndarray) -> float:
    """Moyenne circulaire en degrés (0–360)."""
    rad = np.deg2rad(angles.astype(np.float64))
    mean = np.arctan2(np.mean(np.sin(rad)), np.mean(np.cos(rad)))
    return float(np.rad2deg(mean) % 360.0)


def zonal_stats(
    mask: np.ndarray,
    slope_deg: np.ndarray,
    aspect_deg: np.ndarray,
    walous_codes: np.ndarray,
    suitability: np.ndarray,
) -> dict[str, Any] | None:
    """Agrège les rasters sous le masque parcelle.

    Parameters
    ----------
    mask :
        Pixels de la parcelle.
    slope_deg, aspect_deg, walous_codes, suitability :
        Grilles alignées.

    Returns
    -------
    dict or None
        ``slope_p50_deg``, ``aspect_p50_deg`` (moyenne circulaire),
        ``walous_majority``, ``landcover_open``, ``suitability``
        (moyenne), ``n_pixels``. None si aucun pixel fini.
    """
    if mask.shape != slope_deg.shape:
        raise ValueError("masque et rasters doivent avoir la même forme")
    if not mask.any():
        return None
    suit = np.asarray(suitability, dtype=np.float64)[mask]
    finite = np.isfinite(suit)
    if not np.any(finite):
        return None
    slope = np.asarray(slope_deg, dtype=np.float64)[mask]
    aspect = np.asarray(aspect_deg, dtype=np.float64)[mask]
    codes = np.asarray(walous_codes)[mask]
    slope_ok = slope[np.isfinite(slope)]
    aspect_ok = aspect[np.isfinite(aspect)]
    codes_ok = codes[finite]
    majority = int(np.bincount(codes_ok.astype(np.int64)).argmax())
    return {
        "slope_p50_deg": float(np.median(slope_ok)) if slope_ok.size else None,
        "aspect_p50_deg": (
            _circular_mean_deg(aspect_ok) if aspect_ok.size else None
        ),
        "walous_majority": majority,
        "landcover_open": majority in ELIGIBLE_CODES,
        "suitability": float(np.mean(suit[finite])),
        "n_pixels": int(np.count_nonzero(finite)),
    }


def score_parcel(
    parcel: dict[str, Any],
    slope_deg: np.ndarray,
    aspect_deg: np.ndarray,
    walous_codes: np.ndarray,
    suitability: np.ndarray,
    *,
    origin_x: float,
    origin_y: float,
    cellsize: float,
    min_suitability: float = SUITABILITY_MIN,
) -> dict[str, Any] | None:
    """Score une parcelle, ou None si hors zone favorable.

    Parameters
    ----------
    parcel :
        Ligne normalisée (``capakey``, ``geometry``, …).
    slope_deg, aspect_deg, walous_codes, suitability :
        Tuile overlay alignée.
    origin_x, origin_y, cellsize :
        Géoréférencement.
    min_suitability :
        Seuil sur la moyenne de suitability.

    Returns
    -------
    dict or None
        Ligne ``parapente.score`` + attributs parcelle. None si pas
        assez favorable.
    """
    geom = parcel.get("geometry")
    if not isinstance(geom, dict):
        return None
    mask = rasterize_geometry(
        geom,
        slope_deg.shape,
        origin_x=origin_x,
        origin_y=origin_y,
        cellsize=cellsize,
    )
    stats = zonal_stats(mask, slope_deg, aspect_deg, walous_codes, suitability)
    if stats is None:
        return None
    if stats["suitability"] < min_suitability:
        return None
    return {
        "capakey": parcel["capakey"],
        "commune": parcel.get("commune", ""),
        "province": parcel.get("province", ""),
        "nature": parcel.get("nature"),
        "superficie_m2": parcel.get("superficie_m2"),
        "geometry": geom,
        **stats,
    }


def score_parcels(
    parcels: list[dict[str, Any]],
    slope_deg: np.ndarray,
    aspect_deg: np.ndarray,
    walous_codes: np.ndarray,
    suitability: np.ndarray,
    *,
    origin_x: float,
    origin_y: float,
    cellsize: float,
    min_suitability: float = SUITABILITY_MIN,
) -> list[dict[str, Any]]:
    """Score une liste de parcelles ; ignore celles sous le seuil."""
    rows: list[dict[str, Any]] = []
    for parcel in parcels:
        scored = score_parcel(
            parcel,
            slope_deg,
            aspect_deg,
            walous_codes,
            suitability,
            origin_x=origin_x,
            origin_y=origin_y,
            cellsize=cellsize,
            min_suitability=min_suitability,
        )
        if scored is not None:
            rows.append(scored)
    rows.sort(key=lambda r: r["suitability"], reverse=True)
    return rows


def load_owners_csv(path: Path) -> dict[str, str]:
    """Lit ``capakey,titulaire`` (ou owner / proprietaire).

    Parameters
    ----------
    path :
        CSV local, typiquement ``data/local/proprietaires.csv``.

    Returns
    -------
    dict
        capakey → nom. Fichier absent → dict vide.
    """
    if not path.is_file():
        return {}
    mapping: dict[str, str] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return {}
        fields = {name.casefold(): name for name in reader.fieldnames}
        key_col = (
            fields.get("capakey")
            or fields.get("capa_key")
            or reader.fieldnames[0]
        )
        name_col = (
            fields.get("titulaire")
            or fields.get("proprietaire")
            or fields.get("propriétaire")
            or fields.get("owner")
        )
        if name_col is None:
            return {}
        for row in reader:
            capakey = str(row.get(key_col) or "").strip()
            name = str(row.get(name_col) or "").strip()
            if capakey and name:
                mapping[capakey] = name
    return mapping


def attach_owners(
    rows: list[dict[str, Any]],
    owners: dict[str, str],
) -> list[dict[str, Any]]:
    """Ajoute ``titulaire`` en mémoire seulement (jamais pour l'export)."""
    out: list[dict[str, Any]] = []
    for row in rows:
        copy = dict(row)
        name = owners.get(str(copy.get("capakey") or ""))
        if name:
            copy["titulaire"] = name
        out.append(copy)
    return out


def public_record(row: dict[str, Any]) -> dict[str, Any]:
    """Copie sans titulaire / owner — schéma de la vue publique."""
    return {key: row[key] for key in PUBLIC_KEYS if key in row}


def to_public_geojson(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """FeatureCollection sans aucune propriété nominative."""
    features = []
    for row in rows:
        public = public_record(row)
        geom = public.pop("geometry", None)
        features.append(
            {
                "type": "Feature",
                "properties": public,
                "geometry": geom,
            }
        )
    return {"type": "FeatureCollection", "features": features}


def default_owners_path() -> Path:
    """Chemin gitignoré du CSV nominatif optionnel."""
    return DATA_LOCAL / OWNERS_FILENAME


def cadastre_summary() -> str:
    """Résumé d'une ligne pour le CLI."""
    return (
        f"intersection overlay x CADGIS : moyenne suitability "
        f">= {SUITABILITY_MIN:.2f}, capakey public, "
        f"titulaire seulement via data/local/{OWNERS_FILENAME}"
    )
