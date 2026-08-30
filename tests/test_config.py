"""Vérifie les constantes de cadrage spatial."""

from sites_parapente.config import (
    CRS_EPSG,
    CRS_NAME,
    DATA_LOCAL,
    DATA_PROCESSED,
    DATA_RAW,
    ETL_DIR,
    PROVINCES,
    QGIS_DIR,
    SQL_DIR,
)


def test_crs_is_lambert_2008() -> None:
    """Le projet est entièrement en Lambert 2008."""
    assert CRS_EPSG == 3812
    assert CRS_NAME == "Lambert 2008"


def test_extent_is_three_ardennes_provinces() -> None:
    """Le périmètre v1 est Namur, Luxembourg et Liège."""
    assert PROVINCES == ("Namur", "Luxembourg", "Liège")


def test_layout_directories_exist() -> None:
    """Les dossiers socle sont présents (gitkeep), même vides."""
    for path in (DATA_RAW, DATA_PROCESSED, DATA_LOCAL, ETL_DIR, QGIS_DIR, SQL_DIR):
        assert path.is_dir(), f"dossier manquant : {path}"
