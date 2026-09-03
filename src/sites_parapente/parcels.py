"""Parcelles publiques WGS84 pour le filtre vent et la webapp.

JSON de dicts (lat, lon, aspect_p50_deg). Les clés nominatives sont
jetées à la lecture. Pas de GeoPandas, pas de Lambert 2008 ici : le
jeu démo est déjà en GPS.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Même liste que wind._OWNER_KEYS : la webapp ne doit jamais les servir.
_OWNER_KEYS = frozenset(
    {"titulaire", "owner", "proprietaire", "propriétaire", "ownername"}
)


def _strip_owner(row: dict[str, Any]) -> dict[str, Any]:
    """Copie sans clés nominatives."""
    return {key: value for key, value in row.items() if key not in _OWNER_KEYS}


def _as_rows(raw: Any) -> list[dict[str, Any]]:
    if isinstance(raw, list):
        return [item for item in raw if isinstance(item, dict)]
    if isinstance(raw, dict):
        parcels = raw.get("parcels")
        if isinstance(parcels, list):
            return [item for item in parcels if isinstance(item, dict)]
    raise ValueError("JSON de parcelles : liste ou objet {parcels: [...]} attendu")


def _valid_wgs84_aspect(row: dict[str, Any]) -> bool:
    try:
        lat = float(row["lat"])
        lon = float(row["lon"])
        aspect = float(row["aspect_p50_deg"])
    except (KeyError, TypeError, ValueError):
        return False
    if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
        return False
    return aspect == aspect  # False si NaN


def load_parcels_json(path: Path) -> list[dict[str, Any]]:
    """Charge un JSON de parcelles, sans propriétaires ni lignes invalides.

    Parameters
    ----------
    path :
        Fichier UTF-8. Liste de dicts, ou ``{"parcels": [...]}``.

    Returns
    -------
    list of dict
        Lignes avec ``lat``, ``lon``, ``aspect_p50_deg``. Sans titulaire.

    Raises
    ------
    ValueError
        Schéma JSON inattendu.
    OSError
        Fichier illisible.
    """
    raw = json.loads(path.read_text(encoding="utf-8"))
    kept: list[dict[str, Any]] = []
    for row in _as_rows(raw):
        clean = _strip_owner(row)
        if _valid_wgs84_aspect(clean):
            kept.append(clean)
    return kept
