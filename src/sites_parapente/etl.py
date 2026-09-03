"""ETL Python vers PostGIS — intérim tant que FME n'est pas licencié.

Pas de GeoPandas : GeoJSON (stdlib) pour les parcelles, commandes
``raster2pgsql`` pour les rasters. Aucun champ propriétaire n'est
recopié. FME reprendra le même schéma plus tard.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

from sites_parapente.config import CRS_EPSG, PROVINCES

# Noms de champs nominatifs à jeter (après normalisation).
_OWNER_KEYS = frozenset(
    {
        "proprietaire",
        "owner",
        "ownername",
        "nomproprietaire",
        "titulaire",
        "naam",
        "eigenaar",
    }
)

_CAPAKEY_KEYS = ("capakey", "capake", "cakey")
_COMMUNE_KEYS = ("commune", "nom_comm", "municipality", "nisname")
_PROVINCE_KEYS = ("province", "prov", "provincienaam")
_NATURE_KEYS = ("nature", "typ_nat", "nafc", "landuse")
_AREA_KEYS = ("superficie_m2", "shape_area", "oppervl", "area")

_PROVINCE_ALIASES = {
    "namur": "Namur",
    "namen": "Namur",
    "luxembourg": "Luxembourg",
    "luxemburg": "Luxembourg",
    "liege": "Liège",
    "liège": "Liège",
    "luik": "Liège",
}


def _fold(text: str) -> str:
    """Minuscule, sans accents, sans séparateurs — pour matcher les clés."""
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_only = "".join(ch for ch in nfkd if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "", ascii_only.casefold())


def drop_owner_fields(properties: dict[str, Any]) -> dict[str, Any]:
    """Retire les clés nominatives d'un dict de propriétés.

    Parameters
    ----------
    properties :
        Attributs d'une entité cadastrale (noms bruts).

    Returns
    -------
    dict
        Copie sans propriétaire / owner / titulaire.
    """
    kept: dict[str, Any] = {}
    for key, value in properties.items():
        if _fold(str(key)) in _OWNER_KEYS:
            continue
        kept[key] = value
    return kept


def normalize_province(raw: Any) -> str | None:
    """Ramène une étiquette province aux trois valeurs Ardenne, ou None."""
    if raw is None:
        return None
    folded = _fold(str(raw))
    return _PROVINCE_ALIASES.get(folded)


def _first_alias(properties: dict[str, Any], aliases: tuple[str, ...]) -> Any:
    folded_map = {_fold(k): v for k, v in properties.items()}
    for alias in aliases:
        folded_alias = _fold(alias)
        if folded_alias in folded_map and folded_map[folded_alias] not in (None, ""):
            return folded_map[folded_alias]
    return None


def normalize_parcel(
    properties: dict[str, Any],
    geometry: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Mappe une entité vers le schéma ``parcelle``, ou None si hors périmètre.

    Parameters
    ----------
    properties :
        Attributs bruts (owner déjà à jeter via ``drop_owner_fields``).
    geometry :
        Géométrie GeoJSON (Polygon / MultiPolygon).

    Returns
    -------
    dict or None
        Clés ``capakey``, ``commune``, ``province``, ``nature``,
        ``superficie_m2``, ``geometry``. None si capakey, geom ou
        province Ardenne manquent.
    """
    clean = drop_owner_fields(properties)
    capakey = _first_alias(clean, _CAPAKEY_KEYS)
    commune = _first_alias(clean, _COMMUNE_KEYS)
    province = normalize_province(_first_alias(clean, _PROVINCE_KEYS))
    if not capakey or geometry is None or province not in PROVINCES:
        return None
    area = _first_alias(clean, _AREA_KEYS)
    try:
        superficie = float(area) if area is not None else None
    except (TypeError, ValueError):
        superficie = None
    nature = _first_alias(clean, _NATURE_KEYS)
    return {
        "capakey": str(capakey).strip(),
        "commune": str(commune).strip() if commune else "",
        "province": province,
        "nature": str(nature).strip() if nature else None,
        "superficie_m2": superficie,
        "geometry": geometry,
    }


def geojson_epsg(document: dict[str, Any]) -> int | None:
    """Lit un CRS GeoJSON « named » du type ``urn:ogc:def:crs:EPSG::3812``."""
    crs = document.get("crs") or {}
    props = crs.get("properties") or {}
    name = str(props.get("name") or "")
    match = re.search(r"EPSG::?(\d+)", name, flags=re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def load_geojson_parcels(path: Path, *, expected_epsg: int = CRS_EPSG) -> list[dict[str, Any]]:
    """Charge un GeoJSON de parcelles, filtre Ardenne, jette les owners.

    Parameters
    ----------
    path :
        Fichier FeatureCollection.
    expected_epsg :
        CRS attendu (3812). Si le GeoJSON déclare un autre EPSG, erreur.

    Returns
    -------
    list of dict
        Parcelles normalisées.

    Raises
    ------
    ValueError
        CRS déclaré différent de ``expected_epsg``, ou JSON invalide.
    """
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    declared = geojson_epsg(document)
    if declared is not None and declared != expected_epsg:
        raise ValueError(
            f"GeoJSON en EPSG:{declared}, attendu EPSG:{expected_epsg}"
        )
    features = document.get("features") or []
    rows: list[dict[str, Any]] = []
    for feature in features:
        if not isinstance(feature, dict):
            continue
        props = feature.get("properties") or {}
        geom = feature.get("geometry")
        row = normalize_parcel(props if isinstance(props, dict) else {}, geom)
        if row is not None:
            rows.append(row)
    return rows


def raster2pgsql_command(
    geotiff: Path,
    table: str,
    *,
    srid: int = CRS_EPSG,
) -> list[str]:
    """Construit la commande raster2pgsql (à piper vers psql).

    Parameters
    ----------
    geotiff :
        GeoTIFF local (pente, aspect ou WALOUS).
    table :
        Table cible, ex. ``parapente.pente``.
    srid :
        SRID PostGIS.

    Returns
    -------
    list of str
        Argv, sans mot de passe.
    """
    return [
        "raster2pgsql",
        "-s",
        str(srid),
        "-I",
        "-C",
        "-M",
        "-t",
        "256x256",
        str(geotiff),
        table,
    ]
