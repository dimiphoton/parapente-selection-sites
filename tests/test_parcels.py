"""Chargement JSON public : WGS84, pas de titulaire."""

from pathlib import Path

import pytest

from sites_parapente.parcels import load_parcels_json

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "webapp" / "demo_parcels.json"


def test_load_strips_owner_and_keeps_capakey(tmp_path: Path) -> None:
    path = tmp_path / "parcels.json"
    path.write_text(
        '[{"capakey": "X", "lat": 50.2, "lon": 5.3, '
        '"aspect_p50_deg": 225, "titulaire": "secret"}]',
        encoding="utf-8",
    )
    rows = load_parcels_json(path)
    assert len(rows) == 1
    assert rows[0]["capakey"] == "X"
    assert "titulaire" not in rows[0]


def test_load_skips_invalid_and_accepts_wrapped_object(tmp_path: Path) -> None:
    path = tmp_path / "parcels.json"
    path.write_text(
        '{"parcels": ['
        '{"lat": 50.2, "lon": 5.3, "aspect_p50_deg": 90},'
        '{"lat": 999, "lon": 5.3, "aspect_p50_deg": 90},'
        '{"commune": "nulle part"}'
        "]}",
        encoding="utf-8",
    )
    rows = load_parcels_json(path)
    assert len(rows) == 1
    assert rows[0]["aspect_p50_deg"] == 90


def test_load_rejects_unknown_schema(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text('{"foo": 1}', encoding="utf-8")
    with pytest.raises(ValueError, match="liste"):
        load_parcels_json(path)


def test_demo_file_is_wgs84_public() -> None:
    rows = load_parcels_json(DEMO)
    assert len(rows) >= 20
    for row in rows:
        assert "titulaire" not in row
        assert -90.0 <= float(row["lat"]) <= 90.0
        assert "capakey" in row
        assert "commune" in row
