"""Overlay pondéré : score de suitability au pixel (0–1).

Trois critères, chacun recodé en 0–1, puis moyenne pondérée. L'occupation
du sol est aussi un **veto** : forêt, eau, artificialisé → 0, quel que
soit le relief. Les poids et seuils sont justifiés dans ``docs/overlay.md``.

Ce score décrit le **terrain**. Le vent du jour (Open-Meteo) est un
filtre ultérieur, pas un quatrième poids ici.
"""

from __future__ import annotations

import numpy as np

from sites_parapente.landcover import ELIGIBLE_CODES

# --- Pente (Horn, degrés) -------------------------------------------------
# En dessous de 10° (~18 %) on n'a plus de pente de décollage : le pilote
# court trop longtemps. Au-dessus de 42° (~90 %) on est sur du cliff,
# hors ciblage « parcelle herbeuse ». Le plateau 16–28° couvre les pentes
# de décollage classiques (école / site de club).
SLOPE_MIN_DEG = 10.0
SLOPE_OPT_LO_DEG = 16.0
SLOPE_OPT_HI_DEG = 28.0
SLOPE_MAX_DEG = 42.0

# --- Aspect (aval, 0 = nord, horaire) -------------------------------------
# Flux atlantique dominant en Belgique : sud-ouest. Un pixel face au NE
# n'est pas exclu (jours d'est) : plancher 0,25, le filtre vent tranchera.
PREFERRED_ASPECT_DEG = 225.0
ASPECT_FLOOR = 0.25

# --- Occupation du sol (parmi les codes ouverts WALOUS) -------------------
# Prairie = référence. Sol nu = ouvert mais abrasif / rare en Ardenne.
# Culture = ouvert physiquement, usage saisonnier (semis, récolte).
LANDCOVER_SCORES: dict[int, float] = {
    7: 1.00,  # prairie
    4: 0.80,  # sol nu
    6: 0.55,  # culture
}

# --- Poids (somme = 1) ----------------------------------------------------
# Sans pente, on ne décolle pas → 50 %. L'orientation fixe combien de
# jours le site « marche » au vent dominant → 30 %. Parmi les sols
# ouverts, la qualité change peu par rapport au veto forêt → 20 %.
WEIGHT_SLOPE = 0.50
WEIGHT_ASPECT = 0.30
WEIGHT_LANDCOVER = 0.20


def slope_score(slope_deg: np.ndarray) -> np.ndarray:
    """Recode la pente (degrés) en score 0–1, plateau 16–28°.

    Parameters
    ----------
    slope_deg :
        Pente Horn en degrés. ``NaN`` conservé (bords de tuile).

    Returns
    -------
    np.ndarray
        Score de même forme. 0 hors [10°, 42°], 1 dans [16°, 28°].
    """
    slope = np.asarray(slope_deg, dtype=np.float64)
    score = np.full(slope.shape, np.nan, dtype=np.float64)
    valid = np.isfinite(slope)
    x = slope[valid]
    y = np.zeros_like(x)
    rising = (x >= SLOPE_MIN_DEG) & (x < SLOPE_OPT_LO_DEG)
    y[rising] = (x[rising] - SLOPE_MIN_DEG) / (
        SLOPE_OPT_LO_DEG - SLOPE_MIN_DEG
    )
    plateau = (x >= SLOPE_OPT_LO_DEG) & (x <= SLOPE_OPT_HI_DEG)
    y[plateau] = 1.0
    falling = (x > SLOPE_OPT_HI_DEG) & (x <= SLOPE_MAX_DEG)
    y[falling] = (SLOPE_MAX_DEG - x[falling]) / (
        SLOPE_MAX_DEG - SLOPE_OPT_HI_DEG
    )
    score[valid] = y
    return score


def aspect_score(
    aspect_deg: np.ndarray,
    *,
    preferred_deg: float = PREFERRED_ASPECT_DEG,
    floor: float = ASPECT_FLOOR,
) -> np.ndarray:
    """Score circulaire autour de l'azimut préféré (sud-ouest).

    ``cos(écart)`` ramène 1 face au SW et ``floor`` face au NE. Un aspect
    indéfini (terrain plat, ``NaN``) donne 0 : pas d'orientation utile.

    Parameters
    ----------
    aspect_deg :
        Direction de l'aval en degrés (0 = nord, horaire).
    preferred_deg :
        Azimut visé, défaut 225° (sud-ouest).
    floor :
        Score minimum (jours de vent contraire). Doit être dans [0, 1].

    Returns
    -------
    np.ndarray
        Score de même forme, dans [floor, 1] si l'aspect est défini.
    """
    aspect = np.asarray(aspect_deg, dtype=np.float64)
    delta_rad = np.radians(aspect - preferred_deg)
    cosine = 0.5 + 0.5 * np.cos(delta_rad)
    score = floor + (1.0 - floor) * cosine
    return np.where(np.isfinite(aspect), score, 0.0)


def landcover_score(codes: np.ndarray) -> np.ndarray:
    """Score 0–1 selon le code WALOUS ; 0 = veto (non ouvert).

    Parameters
    ----------
    codes :
        Grille d'entiers WAL_OCS.

    Returns
    -------
    np.ndarray
        Float64 de même forme. Prairie 1, sol nu 0,80, culture 0,55.
    """
    grid = np.asarray(codes)
    out = np.zeros(grid.shape, dtype=np.float64)
    for code, value in LANDCOVER_SCORES.items():
        out[grid == code] = value
    return out


def weighted_overlay(
    slope_deg: np.ndarray,
    aspect_deg: np.ndarray,
    walous_codes: np.ndarray,
) -> np.ndarray:
    """Combine pente, aspect et occupation en un raster 0–1.

    Les trois grilles doivent avoir la même forme (pixels alignés,
    même CRS). Occupation nulle → 0. Pente ``NaN`` (bords Horn) →
    ``NaN``. Pente hors seuils → 0.

    Parameters
    ----------
    slope_deg :
        Pente en degrés.
    aspect_deg :
        Aspect en degrés (aval).
    walous_codes :
        Codes WALOUS.

    Returns
    -------
    np.ndarray
        Suitability, même forme. Plage [0, 1] hors ``NaN``.

    Raises
    ------
    ValueError
        Si les formes ne coincident pas, ou si les poids ne somment
        plus à 1 (constantes corrompues).
    """
    slope = np.asarray(slope_deg, dtype=np.float64)
    aspect = np.asarray(aspect_deg, dtype=np.float64)
    codes = np.asarray(walous_codes)
    if slope.shape != aspect.shape or slope.shape != codes.shape:
        raise ValueError(
            "pente, aspect et occupation doivent avoir la même forme"
        )
    weight_sum = WEIGHT_SLOPE + WEIGHT_ASPECT + WEIGHT_LANDCOVER
    if abs(weight_sum - 1.0) > 1e-9:
        raise ValueError("les poids de l'overlay doivent sommer à 1")

    s_slope = slope_score(slope)
    s_aspect = aspect_score(aspect)
    s_land = landcover_score(codes)

    combined = (
        WEIGHT_SLOPE * s_slope
        + WEIGHT_ASPECT * s_aspect
        + WEIGHT_LANDCOVER * s_land
    )
    # Veto sol fermé, et pente hors plage utile (score 0).
    veto = (s_land <= 0.0) | (np.isfinite(s_slope) & (s_slope <= 0.0))
    suitability = np.where(veto, 0.0, combined)
    # Bords Horn : on ne sait pas, on ne met pas 0.
    suitability = np.where(np.isnan(s_slope), np.nan, suitability)
    return suitability.astype(np.float64)


def overlay_summary() -> str:
    """Résumé d'une ligne pour le CLI et la doc."""
    codes = ", ".join(str(c) for c in sorted(ELIGIBLE_CODES))
    return (
        f"pente {WEIGHT_SLOPE:.0%} (10–42°, plateau 16–28°) · "
        f"aspect {WEIGHT_ASPECT:.0%} (préféré {PREFERRED_ASPECT_DEG:.0f}° SW) · "
        f"sol {WEIGHT_LANDCOVER:.0%} (WALOUS {codes}, veto sinon)"
    )
