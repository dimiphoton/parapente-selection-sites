"""Overlay pondéré sur tuiles synthétiques (pas de LiDAR dans le repo)."""

import numpy as np
import pytest

from sites_parapente.landcover import ELIGIBLE_CODES
from sites_parapente.overlay import (
    ASPECT_FLOOR,
    LANDCOVER_SCORES,
    PREFERRED_ASPECT_DEG,
    WEIGHT_ASPECT,
    WEIGHT_LANDCOVER,
    WEIGHT_SLOPE,
    aspect_score,
    landcover_score,
    overlay_summary,
    slope_score,
    weighted_overlay,
)


def test_weights_sum_to_one() -> None:
    """Les trois poids forment une moyenne, pas une somme libre."""
    assert WEIGHT_SLOPE + WEIGHT_ASPECT + WEIGHT_LANDCOVER == pytest.approx(1.0)


def test_landcover_scores_cover_eligible_codes() -> None:
    """Chaque classe ouverte a un score ; le veto reste hors de ce dict."""
    assert set(LANDCOVER_SCORES) == set(ELIGIBLE_CODES)


def test_slope_plateau_and_bounds() -> None:
    """10° et 42° = 0 ; 16–28° = 1 ; interpolation de part et d'autre."""
    s = slope_score(np.array([5.0, 10.0, 13.0, 22.0, 35.0, 42.0, 50.0]))
    np.testing.assert_allclose(s[0], 0.0)
    np.testing.assert_allclose(s[1], 0.0)
    np.testing.assert_allclose(s[2], 0.5, atol=1e-9)  # milieu 10–16
    np.testing.assert_allclose(s[3], 1.0)
    np.testing.assert_allclose(s[4], 0.5, atol=1e-9)  # milieu 28–42
    np.testing.assert_allclose(s[5], 0.0)
    np.testing.assert_allclose(s[6], 0.0)


def test_slope_keeps_nan() -> None:
    """Les bords Horn (NaN) restent inconnus, pas nuls."""
    s = slope_score(np.array([np.nan, 22.0]))
    assert np.isnan(s[0])
    np.testing.assert_allclose(s[1], 1.0)


def test_aspect_sw_is_one_ne_is_floor() -> None:
    """Face au SW = 1 ; opposé (NE) = plancher, pas zéro."""
    sw = aspect_score(np.array([PREFERRED_ASPECT_DEG]))
    ne = aspect_score(np.array([45.0]))
    np.testing.assert_allclose(sw, 1.0)
    np.testing.assert_allclose(ne, ASPECT_FLOOR)
    nan_score = aspect_score(np.array([np.nan]))
    np.testing.assert_allclose(nan_score, 0.0)


def test_landcover_open_classes_and_veto() -> None:
    """Prairie > sol nu > culture > forêt/eau."""
    codes = np.array([7, 4, 6, 8, 5])
    scores = landcover_score(codes)
    assert scores[0] > scores[1] > scores[2] > scores[3]
    np.testing.assert_allclose(scores[0], 1.0)
    np.testing.assert_allclose(scores[3], 0.0)
    np.testing.assert_allclose(scores[4], 0.0)


def test_perfect_pixel_scores_one() -> None:
    """Prairie, 22°, face SW : suitability 1."""
    slope = np.array([[22.0]])
    aspect = np.array([[225.0]])
    codes = np.array([[7]])
    np.testing.assert_allclose(weighted_overlay(slope, aspect, codes), 1.0)


def test_forest_vetoes_even_with_perfect_relief() -> None:
    """Une forêt pentue face au SW reste à 0."""
    slope = np.array([[22.0]])
    aspect = np.array([[225.0]])
    codes = np.array([[8]])
    np.testing.assert_allclose(weighted_overlay(slope, aspect, codes), 0.0)


def test_flat_grass_is_zero() -> None:
    """Prairie sans pente : pas un décollage."""
    slope = np.array([[2.0]])
    aspect = np.array([[np.nan]])
    codes = np.array([[7]])
    np.testing.assert_allclose(weighted_overlay(slope, aspect, codes), 0.0)


def test_ne_aspect_stays_positive() -> None:
    """Un versant NE n'est pas exclu : le filtre vent pourra le retenir."""
    slope = np.array([[22.0]])
    aspect = np.array([[45.0]])
    codes = np.array([[7]])
    score = weighted_overlay(slope, aspect, codes)[0, 0]
    expected = WEIGHT_SLOPE * 1.0 + WEIGHT_ASPECT * ASPECT_FLOOR + WEIGHT_LANDCOVER * 1.0
    np.testing.assert_allclose(score, expected)
    assert score > 0.5


def test_crops_score_below_grass() -> None:
    """Même relief : la culture pèse moins que la prairie."""
    slope = np.array([[22.0, 22.0]])
    aspect = np.array([[225.0, 225.0]])
    codes = np.array([[7, 6]])
    out = weighted_overlay(slope, aspect, codes)
    assert out[0, 0] > out[0, 1]
    assert out[0, 1] > 0.8


def test_edge_nan_not_zeroed() -> None:
    """Pixel de bord (pente NaN) : suitability NaN, même en prairie."""
    slope = np.array([[np.nan]])
    aspect = np.array([[np.nan]])
    codes = np.array([[7]])
    assert np.isnan(weighted_overlay(slope, aspect, codes)).all()


def test_rejects_shape_mismatch() -> None:
    """Les trois rasters doivent être alignés."""
    with pytest.raises(ValueError, match="même forme"):
        weighted_overlay(np.zeros((2, 2)), np.zeros((2, 3)), np.zeros((2, 2)))


def test_synthetic_tile_matches_manual_mask() -> None:
    """Tuile 2×2 : un pixel parfait, un veto, un plat, un NE."""
    slope = np.array([[22.0, 22.0], [3.0, 22.0]])
    aspect = np.array([[225.0, 225.0], [np.nan, 45.0]])
    codes = np.array([[7, 9], [7, 7]])
    out = weighted_overlay(slope, aspect, codes)
    np.testing.assert_allclose(out[0, 0], 1.0)
    np.testing.assert_allclose(out[0, 1], 0.0)
    np.testing.assert_allclose(out[1, 0], 0.0)
    assert 0.5 < out[1, 1] < 0.85


def test_summary_mentions_weights_and_walous() -> None:
    """Le CLI doit pouvoir afficher le modèle sans ouvrir le markdown."""
    text = overlay_summary()
    assert "50%" in text
    assert "225" in text
    assert "4" in text and "6" in text and "7" in text
