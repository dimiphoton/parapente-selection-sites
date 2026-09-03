"""ETL parcelles : owners jetés, Ardenne seulement, CRS 3812."""

import json
from pathlib import Path

import pytest

from sites_parapente.etl import (
    drop_owner_fields,
    load_geojson_parcels,
    normalize_parcel,
    raster2pgsql_command,
)


def test_drop_owner_fields_is_case_and_accent_insensitive() -> None:
    """propriétaire / OWNER / titulaire ne passent pas."""
    raw = {
        "CaPaKey": "21683D0265/02R020",
        "Propriétaire": "Jean Dupont",
        "OWNER": "secret",
        "titulaire": "x",
        "commune": "Rochefort",
    }
    clean = drop_owner_fields(raw)
    assert "commune" in clean
    assert "CaPaKey" in clean
    assert all("dupont" not in str(v).lower() for v in clean.values())
    assert "Propriétaire" not in clean
    assert "OWNER" not in clean


def test_hainaut_parcel_is_dropped() -> None:
    """Hors Namur / Luxembourg / Liège : pas dans PostGIS."""
    row = normalize_parcel(
        {
            "capakey": "AAA",
            "commune": "Mons",
            "province": "Hainaut",
        },
        {"type": "Polygon", "coordinates": []},
    )
    assert row is None


def test_namur_parcel_is_kept_without_owner() -> None:
    """Namur + capakey + geom → ligne schéma, sans owner."""
    row = normalize_parcel(
        {
            "capakey": "91000A0001/00A000",
            "commune": "Gedinne",
            "province": "Namur",
            "propriétaire": "à jeter",
            "nature": "pré",
            "shape_area": "1200.5",
        },
        {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 0]]]},
    )
    assert row is not None
    assert row["province"] == "Namur"
    assert row["superficie_m2"] == 1200.5
    assert "propriétaire" not in row


def test_load_geojson_rejects_wrong_crs(tmp_path: Path) -> None:
    """Un GeoJSON déclaré en 31370 n'est pas chargé."""
    path = tmp_path / "bad.geojson"
    path.write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "crs": {
                    "type": "name",
                    "properties": {"name": "urn:ogc:def:crs:EPSG::31370"},
                },
                "features": [],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="31370"):
        load_geojson_parcels(path)


def test_load_geojson_filters_and_strips(tmp_path: Path) -> None:
    """Liège gardé, Brabant jeté, owner absent du résultat."""
    path = tmp_path / "mix.geojson"
    geom = {
        "type": "Polygon",
        "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 0]]],
    }
    path.write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {
                            "capakey": "OK1",
                            "commune": "Stavelot",
                            "province": "Liège",
                            "owner": "secret",
                        },
                        "geometry": geom,
                    },
                    {
                        "type": "Feature",
                        "properties": {
                            "capakey": "NO",
                            "commune": "Wavre",
                            "province": "Brabant wallon",
                        },
                        "geometry": geom,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    rows = load_geojson_parcels(path)
    assert len(rows) == 1
    assert rows[0]["capakey"] == "OK1"
    dump = json.dumps(rows)
    assert "secret" not in dump
    assert "owner" not in dump


def test_raster2pgsql_command_is_3812_and_has_no_password() -> None:
    """Commande raster2pgsql : SRID 3812, pas de secret."""
    argv = raster2pgsql_command(Path("pente.tif"), "parapente.pente")
    joined = " ".join(argv)
    assert "-s 3812" in joined
    assert "parapente.pente" in joined
    assert "password" not in joined.lower()
    assert "PGPASSWORD" not in joined
