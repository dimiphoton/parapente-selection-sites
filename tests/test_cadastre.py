"""Intersection cadastre × overlay sur une tuile synthétique."""

import json
from pathlib import Path

import numpy as np
import pytest

from sites_parapente.cadastre import (
    SUITABILITY_MIN,
    attach_owners,
    cadastre_summary,
    load_owners_csv,
    point_in_polygon,
    public_record,
    rasterize_geometry,
    score_parcels,
    to_public_geojson,
    zonal_stats,
)


def _square(x0: float, y0: float, x1: float, y1: float) -> dict:
    return {
        "type": "Polygon",
        "coordinates": [[[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]],
    }


def _tile() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """4×4 : gauche prairie parfaite, droite forêt (même pente)."""
    slope = np.full((4, 4), 22.0)
    aspect = np.full((4, 4), 225.0)
    codes = np.array(
        [
            [7, 7, 8, 8],
            [7, 7, 8, 8],
            [7, 7, 8, 8],
            [7, 7, 8, 8],
        ]
    )
    suit = np.where(codes == 7, 1.0, 0.0)
    return slope, aspect, codes, suit


def test_point_in_square_and_hole() -> None:
    """Centre dedans, hors du trou, et hors du carré."""
    rings = [
        [[0, 0], [4, 0], [4, 4], [0, 4], [0, 0]],
        [[1, 1], [3, 1], [3, 3], [1, 3], [1, 1]],
    ]
    assert point_in_polygon(0.5, 0.5, rings)
    assert not point_in_polygon(2.0, 2.0, rings)
    assert not point_in_polygon(5.0, 5.0, rings)


def test_rasterize_covers_left_half() -> None:
    """Carré [0,2]×[0,4] sur tuile 1 m origine nord : deux colonnes ouest."""
    geom = _square(0, 0, 2, 4)
    mask = rasterize_geometry(
        geom, (4, 4), origin_x=0.0, origin_y=4.0, cellsize=1.0
    )
    assert mask[:, :2].all()
    assert not mask[:, 2:].any()


def test_grass_parcel_is_kept_forest_is_dropped() -> None:
    """Prairie à l'ouest retenue ; forêt à l'est sous le seuil."""
    slope, aspect, codes, suit = _tile()
    parcels = [
        {
            "capakey": "GRASS",
            "commune": "Gedinne",
            "province": "Namur",
            "nature": "pré",
            "superficie_m2": 8.0,
            "geometry": _square(0, 0, 2, 4),
        },
        {
            "capakey": "WOOD",
            "commune": "Gedinne",
            "province": "Namur",
            "nature": "bois",
            "superficie_m2": 8.0,
            "geometry": _square(2, 0, 4, 4),
        },
    ]
    rows = score_parcels(
        parcels,
        slope,
        aspect,
        codes,
        suit,
        origin_x=0.0,
        origin_y=4.0,
        cellsize=1.0,
    )
    keys = [r["capakey"] for r in rows]
    assert keys == ["GRASS"]
    assert rows[0]["suitability"] == pytest.approx(1.0)
    assert rows[0]["landcover_open"] is True
    assert rows[0]["walous_majority"] == 7
    assert rows[0]["slope_p50_deg"] == pytest.approx(22.0)
    assert rows[0]["aspect_p50_deg"] == pytest.approx(225.0, abs=0.5)


def test_mixed_parcel_mean_can_pass_threshold() -> None:
    """Moitié prairie / moitié forêt : moyenne 0,5, encore au-dessus de 0,20."""
    slope, aspect, codes, suit = _tile()
    rows = score_parcels(
        [
            {
                "capakey": "MIX",
                "commune": "Stavelot",
                "province": "Liège",
                "geometry": _square(0, 0, 4, 4),
            }
        ],
        slope,
        aspect,
        codes,
        suit,
        origin_x=0.0,
        origin_y=4.0,
        cellsize=1.0,
    )
    assert len(rows) == 1
    assert rows[0]["suitability"] == pytest.approx(0.5)


def test_public_export_drops_owner_after_join(tmp_path: Path) -> None:
    """Le CSV local joint en mémoire ; GeoJSON et record public sans nom."""
    csv_path = tmp_path / "proprietaires.csv"
    csv_path.write_text(
        "capakey,titulaire\nGRASS,Jean Dupont\n",
        encoding="utf-8",
    )
    slope, aspect, codes, suit = _tile()
    rows = score_parcels(
        [
            {
                "capakey": "GRASS",
                "commune": "Gedinne",
                "province": "Namur",
                "geometry": _square(0, 0, 2, 4),
            }
        ],
        slope,
        aspect,
        codes,
        suit,
        origin_x=0.0,
        origin_y=4.0,
        cellsize=1.0,
    )
    with_owner = attach_owners(rows, load_owners_csv(csv_path))
    assert with_owner[0]["titulaire"] == "Jean Dupont"
    public = public_record(with_owner[0])
    assert "titulaire" not in public
    geojson = to_public_geojson(with_owner)
    dump = json.dumps(geojson)
    assert "Dupont" not in dump
    assert "titulaire" not in dump
    assert geojson["features"][0]["properties"]["capakey"] == "GRASS"


def test_missing_owners_file_is_empty(tmp_path: Path) -> None:
    """Pas de CSV → pas de jointure, pas d'erreur."""
    assert load_owners_csv(tmp_path / "absent.csv") == {}


def test_zonal_stats_none_if_empty_mask() -> None:
    """Masque vide : pas de ligne score."""
    z = np.ones((2, 2))
    assert zonal_stats(np.zeros((2, 2), dtype=bool), z, z, z.astype(int), z) is None


def test_summary_mentions_threshold_and_rgpd() -> None:
    text = cadastre_summary()
    assert f"{SUITABILITY_MIN:.2f}" in text
    assert "capakey" in text
    assert "titulaire" in text
