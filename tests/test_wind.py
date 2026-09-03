"""Filtre vent : géométrie circulaire, parse Open-Meteo, pas de réseau."""

import json
from io import BytesIO

import numpy as np
import pytest

from sites_parapente.wind import (
    ASPECT_TOLERANCE_DEG,
    FORECAST_DAYS,
    RADIUS_M_DEFAULT,
    WindForecastError,
    build_forecast_url,
    cardinal_from_deg,
    circular_delta_deg,
    faces_wind,
    fetch_forecast,
    filter_parcels,
    haversine_m,
    parcels_by_day,
    parse_forecast,
    wind_summary,
)


def _payload() -> dict:
    """Réponse Open-Meteo minimale : 3 jours, 72 heures."""
    hours = FORECAST_DAYS * 24
    times = [f"2026-09-03T{h:02d}:00" for h in range(24)]
    times += [f"2026-09-04T{h:02d}:00" for h in range(24)]
    times += [f"2026-09-05T{h:02d}:00" for h in range(24)]
    assert len(times) == hours
    return {
        "latitude": 50.22,
        "longitude": 5.34,
        "hourly": {
            "time": times,
            "wind_speed_10m": [15.0] * hours,
            "wind_direction_10m": [225.0] * hours,
        },
        "daily": {
            "time": ["2026-09-03", "2026-09-04", "2026-09-05"],
            "wind_speed_10m_max": [25.0, 18.0, 12.0],
            "wind_direction_10m_dominant": [225.0, 45.0, 270.0],
        },
    }


class _FakeResponse:
    def __init__(self, body: str) -> None:
        self._buf = BytesIO(body.encode("utf-8"))

    def read(self) -> bytes:
        return self._buf.read()

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None


def test_circular_delta_wraps_around_zero() -> None:
    """350° et 10° : 20° d'écart, pas 340."""
    assert float(circular_delta_deg(350.0, 10.0)) == pytest.approx(20.0)
    assert float(circular_delta_deg(10.0, 350.0)) == pytest.approx(20.0)
    assert float(circular_delta_deg(0.0, 180.0)) == pytest.approx(180.0)


def test_faces_wind_inclusive_45_and_rejects_back() -> None:
    """Pile à 45° : gardé. Dos au vent : jeté. Plat : jeté."""
    assert bool(np.asarray(faces_wind(225.0, 270.0)).item())  # 45°
    assert not bool(np.asarray(faces_wind(225.0, 271.0)).item())
    assert bool(np.asarray(faces_wind(0.0, 350.0)).item())  # 10°, wrap
    assert not bool(np.asarray(faces_wind(0.0, 180.0)).item())
    assert not bool(np.asarray(faces_wind(np.nan, 225.0)).item())


def test_haversine_zero_and_one_degree_latitude() -> None:
    """Même point = 0. 1° de latitude ≈ 111,2 km."""
    assert haversine_m(50.0, 5.0, 50.0, 5.0) == pytest.approx(0.0)
    one_deg = haversine_m(50.0, 5.0, 51.0, 5.0)
    assert one_deg == pytest.approx(111_195.0, rel=0.01)


def test_filter_keeps_facing_parcel_inside_radius() -> None:
    """SO à 5 km gardé ; NE dans le rayon jeté ; SO hors rayon jeté."""
    origin = {"lat": 50.22, "lon": 5.34}
    parcels = [
        {
            "capakey": "NEAR_SW",
            "lat": 50.24,
            "lon": 5.34,
            "aspect_p50_deg": 225.0,
            "suitability": 0.9,
            "titulaire": "à jeter",
        },
        {
            "capakey": "NEAR_NE",
            "lat": 50.23,
            "lon": 5.34,
            "aspect_p50_deg": 45.0,
            "suitability": 0.8,
        },
        {
            "capakey": "FAR_SW",
            "lat": 51.00,
            "lon": 5.34,
            "aspect_p50_deg": 225.0,
            "suitability": 1.0,
        },
    ]
    kept = filter_parcels(
        parcels,
        origin_lat=origin["lat"],
        origin_lon=origin["lon"],
        wind_from_deg=225.0,
        radius_m=30_000.0,
    )
    assert [row["capakey"] for row in kept] == ["NEAR_SW"]
    assert "titulaire" not in kept[0]
    assert kept[0]["distance_m"] < 30_000.0
    assert kept[0]["aspect_delta_deg"] == pytest.approx(0.0)


def test_parse_forecast_truncates_to_three_days() -> None:
    """4e jour / heures au-delà de 72 h ignorés."""
    payload = _payload()
    payload["daily"]["time"].append("2026-09-06")
    payload["daily"]["wind_speed_10m_max"].append(9.0)
    payload["daily"]["wind_direction_10m_dominant"].append(90.0)
    extra = {
        "time": payload["hourly"]["time"] + ["2026-09-06T00:00"],
        "wind_speed_10m": payload["hourly"]["wind_speed_10m"] + [1.0],
        "wind_direction_10m": payload["hourly"]["wind_direction_10m"] + [90.0],
    }
    payload["hourly"] = extra
    forecast = parse_forecast(payload)
    assert len(forecast.daily) == FORECAST_DAYS
    assert len(forecast.hourly) == FORECAST_DAYS * 24
    assert forecast.daily[-1].date == "2026-09-05"


def test_parse_forecast_rejects_length_mismatch() -> None:
    payload = _payload()
    payload["hourly"]["wind_direction_10m"] = payload["hourly"]["wind_direction_10m"][:-1]
    with pytest.raises(WindForecastError, match="longueurs"):
        parse_forecast(payload)


def test_build_forecast_url_has_horizon_and_no_key() -> None:
    url = build_forecast_url(50.22, 5.34)
    assert "forecast_days=3" in url
    assert "wind_direction_10m" in url
    assert "wind_direction_10m_dominant" in url
    assert "api.open-meteo.com/v1/forecast" in url
    assert "key" not in url.lower()
    assert "timezone=Europe%2FBrussels" in url


def test_fetch_forecast_uses_injected_urlopen() -> None:
    """Aucun socket : urlopen de test renvoie le JSON-fixture."""
    body = json.dumps(_payload())
    seen: list[object] = []

    def fake_urlopen(request: object, timeout: int = 0) -> _FakeResponse:
        seen.append((request, timeout))
        return _FakeResponse(body)

    forecast = fetch_forecast(50.22, 5.34, urlopen=fake_urlopen)
    assert forecast.daily[0].direction_from_deg == pytest.approx(225.0)
    assert len(forecast.hourly) == 72
    assert seen and seen[0][1] == 20


def test_parcels_by_day_follows_dominant_wind() -> None:
    """Jour SO → parcelle SW ; jour NE → parcelle NE."""
    forecast = parse_forecast(_payload())
    parcels = [
        {
            "capakey": "SW",
            "lat": 50.22,
            "lon": 5.34,
            "aspect_p50_deg": 225.0,
        },
        {
            "capakey": "NE",
            "lat": 50.22,
            "lon": 5.34,
            "aspect_p50_deg": 45.0,
        },
    ]
    days = parcels_by_day(
        parcels,
        forecast,
        origin_lat=50.22,
        origin_lon=5.34,
        radius_m=RADIUS_M_DEFAULT,
    )
    assert [d["date"] for d in days] == ["2026-09-03", "2026-09-04", "2026-09-05"]
    assert [r["capakey"] for r in days[0]["parcels"]] == ["SW"]
    assert [r["capakey"] for r in days[1]["parcels"]] == ["NE"]
    assert days[0]["cardinal"] == "SO"


def test_cardinal_and_summary() -> None:
    assert cardinal_from_deg(225.0) == "SO"
    assert cardinal_from_deg(0.0) == "N"
    text = wind_summary()
    assert str(FORECAST_DAYS) in text
    assert f"{ASPECT_TOLERANCE_DEG:.0f}" in text
    assert "Open-Meteo" in text


def test_invalid_coordinates() -> None:
    with pytest.raises(ValueError, match="latitude"):
        build_forecast_url(100.0, 5.0)
    with pytest.raises(ValueError, match="radius"):
        filter_parcels(
            [],
            origin_lat=50.0,
            origin_lon=5.0,
            wind_from_deg=180.0,
            radius_m=-1.0,
        )
