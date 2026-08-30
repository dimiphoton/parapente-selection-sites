"""Classes WALOUS retenues / exclues pour un décollage."""

import numpy as np
import pytest

from sites_parapente.config import CRS_EPSG
from sites_parapente.landcover import (
    ELIGIBLE_CODES,
    EXCLUDED_CODES,
    WALOUS_LABELS,
    is_takeoff_eligible,
    landcover_mask,
    require_crs,
)


def test_walous_has_eleven_principal_classes() -> None:
    """Les 11 classes WAL_OCS sont documentées."""
    assert len(WALOUS_LABELS) == 11
    assert ELIGIBLE_CODES.isdisjoint(EXCLUDED_CODES)
    assert ELIGIBLE_CODES | EXCLUDED_CODES == frozenset(WALOUS_LABELS)


def test_prairie_and_crops_are_open() -> None:
    """Prairie, culture et sol nu : ouverts au décollage."""
    assert is_takeoff_eligible(7)
    assert is_takeoff_eligible(6)
    assert is_takeoff_eligible(4)


def test_forest_water_and_buildings_are_closed() -> None:
    """Forêt, arbustes, eau et artificialisé : exclus."""
    for code in (1, 2, 3, 5, 8, 9, 80, 90):
        assert not is_takeoff_eligible(code)


def test_unknown_code_is_excluded() -> None:
    """Un code hors légende n'est pas traité comme ouvert."""
    assert not is_takeoff_eligible(99)


def test_mask_on_synthetic_tile() -> None:
    """Tuile 3×3 : prairie et culture True, forêt et eau False."""
    codes = np.array(
        [
            [7, 8, 5],
            [6, 4, 1],
            [9, 80, 2],
        ]
    )
    mask = landcover_mask(codes)
    expected = np.array(
        [
            [True, False, False],
            [True, True, False],
            [False, False, False],
        ]
    )
    np.testing.assert_array_equal(mask, expected)


def test_crs_must_be_lambert_2008() -> None:
    """WALOUS est déjà en EPSG:3812 ; on refuse un autre CRS."""
    require_crs(CRS_EPSG)
    with pytest.raises(ValueError, match="3812"):
        require_crs(31370)
