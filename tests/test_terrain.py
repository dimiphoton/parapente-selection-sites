"""Pente et aspect sur une tuile synthétique (Horn 1981)."""

import numpy as np
import pytest

from sites_parapente.terrain import slope_and_aspect


def _interior(arr: np.ndarray) -> np.ndarray:
    """Centre 3×3 d'une grille 5×5 (bords exclus par Horn)."""
    return arr[1:-1, 1:-1]


def test_east_rising_ramp_faces_west() -> None:
    """Si ça monte vers l'est, l'aval est à l'ouest (aspect ~ 270°)."""
    # z = colonne * 1 m, pixel 1 m → pente 45°.
    z = np.tile(np.arange(5, dtype=float), (5, 1))
    slope, aspect = slope_and_aspect(z, cellsize=1.0)
    np.testing.assert_allclose(_interior(slope), 45.0, atol=0.5)
    np.testing.assert_allclose(_interior(aspect), 270.0, atol=1.0)


def test_north_rising_ramp_faces_south() -> None:
    """Si ça monte vers le nord (ligne 0), l'aval est au sud (~ 180°)."""
    z = np.tile(np.arange(5, 0, -1, dtype=float).reshape(-1, 1), (1, 5))
    slope, aspect = slope_and_aspect(z, cellsize=1.0)
    np.testing.assert_allclose(_interior(slope), 45.0, atol=0.5)
    np.testing.assert_allclose(_interior(aspect), 180.0, atol=1.0)


def test_flat_has_zero_slope_and_nan_aspect() -> None:
    """Terrain plat : pente nulle, pas d'orientation."""
    z = np.ones((5, 5))
    slope, aspect = slope_and_aspect(z, cellsize=1.0)
    np.testing.assert_allclose(_interior(slope), 0.0, atol=1e-9)
    assert np.isnan(_interior(aspect)).all()


def test_rejects_tiny_grid() -> None:
    """Horn a besoin d'une fenêtre 3×3."""
    with pytest.raises(ValueError, match="3x3"):
        slope_and_aspect(np.zeros((2, 2)), cellsize=1.0)
