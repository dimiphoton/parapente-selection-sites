"""Pente et orientation (aspect) à partir d'une grille d'altitude.

On utilise la formule de Horn (1981), la même famille que GDAL/QGIS
``gdaldem slope`` / ``aspect`` : fenêtre 3×3, 8 voisins.

- **Pente** : angle avec l'horizontale, en degrés (0 = plat).
- **Aspect** : direction vers laquelle la pente est tournée (sens de
  l'aval), en degrés depuis le nord, sens horaire (90 = est, 180 =
  sud, 270 = ouest). Les cellules plates ont un aspect ``NaN``.

La grille est nord en haut (ligne 0 = nord), comme un GeoTIFF
nord-up. Le MNT LiDAR réel n'est pas dans le dépôt (volume) : les
tests passent sur une tuile synthétique 1 m.
"""

from __future__ import annotations

import numpy as np

# En dessous de ce seuil, on ne calcule pas d'aspect (terrain plat).
FLAT_SLOPE_DEG = 0.5


def slope_and_aspect(
    elevation: np.ndarray,
    cellsize: float,
    *,
    flat_slope_deg: float = FLAT_SLOPE_DEG,
) -> tuple[np.ndarray, np.ndarray]:
    """Calcule pente et aspect (Horn 1981) sur une grille d'altitude.

    Parameters
    ----------
    elevation :
        Altitude en mètres, forme (n_lignes, n_colonnes), nord en haut.
    cellsize :
        Taille de pixel en mètres (carré). Le MNT SPW est en 0,5 m ou 1 m.
    flat_slope_deg :
        Seuil sous lequel l'aspect est indéfini (``NaN``).

    Returns
    -------
    slope_deg, aspect_deg :
        Tableaux de même forme que ``elevation``. Bords et plats en
        ``NaN`` pour l'aspect ; bords en ``NaN`` pour la pente.

    Raises
    ------
    ValueError
        Si la grille a moins de 3×3 cellules ou si ``cellsize`` ≤ 0.
    """
    z = np.asarray(elevation, dtype=np.float64)
    if z.ndim != 2 or min(z.shape) < 3:
        raise ValueError("la grille doit faire au moins 3x3")
    if cellsize <= 0:
        raise ValueError("cellsize doit être strictement positif")

    # Fenêtre Horn (a b c / d e f / g h i), a = nord-ouest.
    a, b, c = z[:-2, :-2], z[:-2, 1:-1], z[:-2, 2:]
    d, f = z[1:-1, :-2], z[1:-1, 2:]
    g, h, i = z[2:, :-2], z[2:, 1:-1], z[2:, 2:]

    dz_dx = ((c + 2.0 * f + i) - (a + 2.0 * d + g)) / (8.0 * cellsize)
    # Ligne 0 = nord : augmenter l'indice de ligne va vers le sud.
    dz_dy = ((g + 2.0 * h + i) - (a + 2.0 * b + c)) / (8.0 * cellsize)

    slope_rad = np.arctan(np.hypot(dz_dx, dz_dy))
    slope_deg = np.degrees(slope_rad)

    # Aspect = direction de l'aval (0 = nord, horaire). On inverse dz_dx
    # parce que la ligne 0 est le nord : +x (est plus haut) doit donner
    # l'ouest (270°), pas l'est.
    aspect_deg = np.degrees(np.arctan2(-dz_dx, dz_dy))
    aspect_deg = np.where(aspect_deg < 0.0, aspect_deg + 360.0, aspect_deg)
    aspect_deg = np.where(slope_deg < flat_slope_deg, np.nan, aspect_deg)

    slope_out = np.full(z.shape, np.nan, dtype=np.float64)
    aspect_out = np.full(z.shape, np.nan, dtype=np.float64)
    slope_out[1:-1, 1:-1] = slope_deg
    aspect_out[1:-1, 1:-1] = aspect_deg
    return slope_out, aspect_out
