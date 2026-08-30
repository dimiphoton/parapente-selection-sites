"""Occupation du sol WALOUS : classes ouvertes au décollage.

Légende des 11 classes WAL_OCS (SPW / UCLouvain / ULB / ISSeP),
millésime cible **2023** (vue du ciel, un code par pixel, EPSG:3812,
maille 1 m). Le raster n'est pas dans le dépôt (volume) : on teste
sur une grille d'entiers.

Un décollage a besoin d'un sol **ouvert** (herbe, culture, sol nu).
Forêt, arbustes, eau et surfaces artificielles sont exclus. Corine
Land Cover n'est pas branché : maille 25 ha, trop grossière.
"""

from __future__ import annotations

import numpy as np

from sites_parapente.config import CRS_EPSG

# Codes officiels WAL_OCS (classes principales).
WALOUS_LABELS: dict[int, str] = {
    1: "Revêtement artificiel au sol",
    2: "Constructions artificielles hors sol",
    3: "Réseau ferroviaire",
    4: "Sols nus",
    5: "Eaux de surface",
    6: "Couvert herbacé en rotation (cultures)",
    7: "Couvert herbacé toute l'année (prairies)",
    8: "Résineux (> 3 m)",
    9: "Feuillus (> 3 m)",
    80: "Résineux (≤ 3 m)",
    90: "Feuillus (≤ 3 m)",
}

# Ouvert : prairie (idéal), culture, sol nu / roche.
ELIGIBLE_CODES: frozenset[int] = frozenset({4, 6, 7})

# Obstacle, eau, artificialisé — et tout code inconnu.
EXCLUDED_CODES: frozenset[int] = frozenset(
    set(WALOUS_LABELS) - set(ELIGIBLE_CODES)
)


def require_crs(epsg: int) -> None:
    """Refuse un raster qui n'est pas en Lambert 2008.

    Parameters
    ----------
    epsg :
        Code EPSG lu dans les métadonnées du raster.

    Raises
    ------
    ValueError
        Si ``epsg`` n'est pas ``CRS_EPSG`` (3812).
    """
    if epsg != CRS_EPSG:
        raise ValueError(
            f"occupation du sol attendue en EPSG:{CRS_EPSG}, reçu EPSG:{epsg}"
        )


def is_takeoff_eligible(code: int) -> bool:
    """Indique si le code WALOUS est un sol ouvert au décollage.

    Parameters
    ----------
    code :
        Valeur de pixel WAL_OCS (1, 2, 3, 4, 5, 6, 7, 8, 9, 80, 90).

    Returns
    -------
    bool
        ``True`` seulement pour sols nus, cultures et prairies.
    """
    return int(code) in ELIGIBLE_CODES


def landcover_mask(codes: np.ndarray) -> np.ndarray:
    """Masque booléen : True = pixel ouvert au décollage.

    Parameters
    ----------
    codes :
        Grille d'entiers WALOUS, forme (n_lignes, n_colonnes).

    Returns
    -------
    np.ndarray
        Booléen de même forme. Les codes inconnus sont exclus.
    """
    grid = np.asarray(codes)
    eligible = np.isin(grid, list(ELIGIBLE_CODES))
    return eligible
