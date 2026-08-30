"""Le schéma PostGIS versionné : CRS, index, pas de propriétaire."""

from pathlib import Path

from sites_parapente.config import CRS_EPSG, SQL_DIR

SCHEMA = SQL_DIR / "schema_postgis.sql"


def _sql() -> str:
    return Path(SCHEMA).read_text(encoding="utf-8")


def test_schema_file_exists() -> None:
    """sql/schema_postgis.sql est le livrable, pas une capture d'écran."""
    assert SCHEMA.is_file()


def test_schema_uses_lambert_2008_and_postgis() -> None:
    """Extensions PostGIS + SRID 3812 partout."""
    text = _sql()
    assert "CREATE EXTENSION IF NOT EXISTS postgis" in text
    assert "postgis_raster" in text
    assert str(CRS_EPSG) in text
    assert "geometry(MultiPolygon, 3812)" in text


def test_schema_has_required_tables_and_gist_indexes() -> None:
    """Pente, aspect, occupation, parcelle, score + index GIST."""
    text = _sql()
    for name in ("pente", "aspect", "occupation", "parcelle", "score"):
        assert f"parapente.{name}" in text
    assert text.count("USING GIST") >= 5


def test_schema_has_capakey_and_no_owner_column() -> None:
    """Identifiant cadastral public ; pas de colonne nominative."""
    text = _sql()
    lowered = text.lower()
    assert "capakey" in lowered
    assert "nom_proprietaire" not in lowered
    assert "owner_name" not in lowered
    assert "pas de titulaire" in lowered
