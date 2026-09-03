"""Filtre vent : prévision Open-Meteo (3 jours) et parcelles face au vent.

Convention météo : la direction est **d'où vient** le vent (0° = nord,
90° = est). Convention terrain : l'aspect est la direction de l'aval
(même 0° = nord). Un versant **face au vent** a donc un aspect proche
de la direction météo — on décolle contre le flux, pas dos à la pente.

Le seuil ± 45° et l'horizon 3 jours sont des choix de cadrage
(``docs/decisions.md``, ``docs/wind.md``). Le rayon autour du point
utilisateur est réglable ; défaut 30 km.

Pas de clé API. ``urllib`` (stdlib) pour ne pas ajouter de dépendance.
Les tests injectent ``urlopen`` : aucun appel réseau dans pytest.
"""

from __future__ import annotations

import json
import math
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable

import numpy as np

# Horizon et géométrie du filtre (cadrage 2026-08-30).
FORECAST_DAYS = 3
ASPECT_TOLERANCE_DEG = 45.0
RADIUS_M_DEFAULT = 30_000.0
WIND_HEIGHT_M = 10
TIMEZONE = "Europe/Brussels"
OPEN_METEO_ENDPOINT = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT_S = 20
EARTH_RADIUS_M = 6_371_000.0
USER_AGENT = (
    "parapente-selection-sites/0.1 "
    "(https://github.com/dimiphoton/parapente-selection-sites)"
)

_OWNER_KEYS = frozenset(
    {"titulaire", "owner", "proprietaire", "propriétaire", "ownername"}
)

UrlOpen = Callable[..., Any]


class WindForecastError(Exception):
    """Échec de l'appel Open-Meteo ou JSON inattendu."""


@dataclass(frozen=True)
class HourlyWind:
    """Vent horaire à 10 m."""

    time: str
    speed_kmh: float
    direction_from_deg: float


@dataclass(frozen=True)
class DailyWind:
    """Vent dominant du jour (agrégat Open-Meteo)."""

    date: str
    speed_max_kmh: float
    direction_from_deg: float


@dataclass(frozen=True)
class WindForecast:
    """Prévision 3 jours au point WGS84 demandé."""

    latitude: float
    longitude: float
    hourly: tuple[HourlyWind, ...]
    daily: tuple[DailyWind, ...]


def circular_delta_deg(
    aspect_deg: float | np.ndarray,
    wind_from_deg: float | np.ndarray,
) -> np.ndarray:
    """Plus petit écart d'azimut, dans [0, 180].

    Parameters
    ----------
    aspect_deg, wind_from_deg :
        Angles en degrés. ``NaN`` propagé.

    Returns
    -------
    np.ndarray
        Écart circulaire en degrés.
    """
    a = np.asarray(aspect_deg, dtype=np.float64)
    b = np.asarray(wind_from_deg, dtype=np.float64)
    delta = np.abs(a - b) % 360.0
    return np.minimum(delta, 360.0 - delta)


def faces_wind(
    aspect_deg: float | np.ndarray,
    wind_from_deg: float | np.ndarray,
    *,
    tolerance_deg: float = ASPECT_TOLERANCE_DEG,
) -> np.ndarray:
    """True si l'aspect est face au vent, à ``tolerance_deg`` près.

    Un aspect indéfini (terrain plat, ``NaN``) n'est jamais face au vent.

    Parameters
    ----------
    aspect_deg :
        Direction de l'aval (0 = nord, horaire).
    wind_from_deg :
        Direction météo (d'où vient le vent).
    tolerance_deg :
        Demi-largeur de la fenêtre, défaut 45°.

    Returns
    -------
    np.ndarray
        Booléen de même forme que les angles broadcastés.
    """
    if tolerance_deg < 0.0:
        raise ValueError("tolerance_deg doit être positif")
    delta = circular_delta_deg(aspect_deg, wind_from_deg)
    return np.isfinite(delta) & (delta <= tolerance_deg)


def haversine_m(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """Distance orthodromique en mètres (WGS84, sphère 6371 km).

    Suffisant pour un rayon de trajet (10–50 km). L'erreur vs ellipsoïde
    est négligeable à cette maille. Pas de pyproj (pas de GeoPandas).

    Parameters
    ----------
    lat1, lon1, lat2, lon2 :
        Degrés décimaux WGS84.

    Returns
    -------
    float
        Distance en mètres.
    """
    rlat1, rlon1, rlat2, rlon2 = (
        math.radians(lat1),
        math.radians(lon1),
        math.radians(lat2),
        math.radians(lon2),
    )
    dlat = rlat2 - rlat1
    dlon = rlon2 - rlon1
    chord = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2.0) ** 2
    )
    return 2.0 * EARTH_RADIUS_M * math.asin(math.sqrt(min(1.0, chord)))


def _require_wgs84(latitude: float, longitude: float) -> None:
    if not math.isfinite(latitude) or not math.isfinite(longitude):
        raise ValueError("latitude et longitude doivent être finies")
    if not -90.0 <= latitude <= 90.0:
        raise ValueError("latitude hors [-90, 90]")
    if not -180.0 <= longitude <= 180.0:
        raise ValueError("longitude hors [-180, 180]")


def cardinal_from_deg(direction_from_deg: float) -> str:
    """Secteur de 45° en français (N, NE, E, SE, S, SO, O, NO)."""
    names = ("N", "NE", "E", "SE", "S", "SO", "O", "NO")
    idx = int((direction_from_deg % 360.0) / 45.0 + 0.5) % 8
    return names[idx]


def build_forecast_url(latitude: float, longitude: float) -> str:
    """URL Open-Meteo : 3 jours, vent 10 m, horaire + dominant journalier.

    Parameters
    ----------
    latitude, longitude :
        Point WGS84 (position utilisateur ou centroïde du rayon).

    Returns
    -------
    str
        GET https, sans clé.

    Raises
    ------
    ValueError
        Coordonnées hors WGS84.
    """
    _require_wgs84(latitude, longitude)
    query = urllib.parse.urlencode(
        {
            "latitude": f"{latitude:.5f}",
            "longitude": f"{longitude:.5f}",
            "hourly": "wind_speed_10m,wind_direction_10m",
            "daily": "wind_speed_10m_max,wind_direction_10m_dominant",
            "forecast_days": str(FORECAST_DAYS),
            "timezone": TIMEZONE,
            "wind_speed_unit": "kmh",
        }
    )
    return f"{OPEN_METEO_ENDPOINT}?{query}"


def _as_float_list(raw: Any, label: str) -> list[float]:
    if not isinstance(raw, list) or not raw:
        raise WindForecastError(f"Open-Meteo : {label} manquant ou vide")
    out: list[float] = []
    for value in raw:
        try:
            out.append(float(value))
        except (TypeError, ValueError) as exc:
            raise WindForecastError(
                f"Open-Meteo : {label} non numérique"
            ) from exc
    return out


def parse_forecast(payload: dict[str, Any]) -> WindForecast:
    """Valide un JSON Open-Meteo et le coupe à 3 jours.

    Parameters
    ----------
    payload :
        Corps JSON déjà décodé.

    Returns
    -------
    WindForecast
        Horaire (≤ 72 h) et journalier (≤ 3 jours).

    Raises
    ------
    WindForecastError
        Schéma inattendu, longueurs incohérentes.
    """
    try:
        latitude = float(payload["latitude"])
        longitude = float(payload["longitude"])
    except (KeyError, TypeError, ValueError) as exc:
        raise WindForecastError("Open-Meteo : latitude/longitude absentes") from exc

    hourly_raw = payload.get("hourly") or {}
    daily_raw = payload.get("daily") or {}
    times = hourly_raw.get("time") or []
    if not isinstance(times, list) or not times:
        raise WindForecastError("Open-Meteo : hourly.time manquant")
    speeds = _as_float_list(hourly_raw.get("wind_speed_10m"), "wind_speed_10m")
    dirs = _as_float_list(
        hourly_raw.get("wind_direction_10m"), "wind_direction_10m"
    )
    if not (len(times) == len(speeds) == len(dirs)):
        raise WindForecastError("Open-Meteo : séries horaires de longueurs différentes")

    max_hours = FORECAST_DAYS * 24
    hourly = tuple(
        HourlyWind(str(times[i]), speeds[i], dirs[i])
        for i in range(min(len(times), max_hours))
    )

    dates = daily_raw.get("time") or []
    if not isinstance(dates, list) or not dates:
        raise WindForecastError("Open-Meteo : daily.time manquant")
    daily_speed = _as_float_list(
        daily_raw.get("wind_speed_10m_max"), "wind_speed_10m_max"
    )
    daily_dir = _as_float_list(
        daily_raw.get("wind_direction_10m_dominant"),
        "wind_direction_10m_dominant",
    )
    if not (len(dates) == len(daily_speed) == len(daily_dir)):
        raise WindForecastError("Open-Meteo : séries journalières de longueurs différentes")

    daily = tuple(
        DailyWind(str(dates[i]), daily_speed[i], daily_dir[i])
        for i in range(min(len(dates), FORECAST_DAYS))
    )
    return WindForecast(latitude, longitude, hourly, daily)


def fetch_forecast(
    latitude: float,
    longitude: float,
    *,
    urlopen: UrlOpen | None = None,
) -> WindForecast:
    """Télécharge la prévision 3 jours au point donné.

    Parameters
    ----------
    latitude, longitude :
        WGS84.
    urlopen :
        Injectable pour les tests (signature de ``urllib.request.urlopen``).

    Returns
    -------
    WindForecast

    Raises
    ------
    ValueError
        Coordonnées invalides.
    WindForecastError
        HTTP, timeout, JSON ou schéma.
    """
    url = build_forecast_url(latitude, longitude)
    opener = urlopen or urllib.request.urlopen
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with opener(request, timeout=REQUEST_TIMEOUT_S) as response:
            raw = response.read()
    except urllib.error.URLError as exc:
        raise WindForecastError(f"Open-Meteo inaccessible : {exc}") from exc
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WindForecastError("Open-Meteo : réponse non JSON") from exc
    if not isinstance(payload, dict):
        raise WindForecastError("Open-Meteo : JSON racine inattendu")
    if payload.get("error"):
        raise WindForecastError(
            f"Open-Meteo : {payload.get('reason', 'erreur API')}"
        )
    return parse_forecast(payload)


def _strip_owner(row: dict[str, Any]) -> dict[str, Any]:
    """Copie sans clés nominatives (la webapp publique ne les verra pas)."""
    return {key: value for key, value in row.items() if key not in _OWNER_KEYS}


def _parcel_lat_lon(parcel: dict[str, Any]) -> tuple[float, float] | None:
    try:
        lat = float(parcel["lat"])
        lon = float(parcel["lon"])
    except (KeyError, TypeError, ValueError):
        return None
    try:
        _require_wgs84(lat, lon)
    except ValueError:
        return None
    return lat, lon


def filter_parcels(
    parcels: list[dict[str, Any]],
    *,
    origin_lat: float,
    origin_lon: float,
    wind_from_deg: float,
    radius_m: float = RADIUS_M_DEFAULT,
    tolerance_deg: float = ASPECT_TOLERANCE_DEG,
) -> list[dict[str, Any]]:
    """Garde les parcelles dans le rayon **et** face au vent.

    Chaque parcelle doit fournir ``lat``, ``lon`` (WGS84) et
    ``aspect_p50_deg`` (moyenne circulaire déjà calculée au cadastre).
    Les champs propriétaire sont jetés.

    Parameters
    ----------
    parcels :
        Lignes score (ou dicts minimaux lat/lon/aspect).
    origin_lat, origin_lon :
        Point utilisateur WGS84.
    wind_from_deg :
        Direction météo du créneau (dominant du jour, ou une heure).
    radius_m :
        Rayon de trajet, défaut 30 km.
    tolerance_deg :
        Fenêtre d'aspect, défaut 45°.

    Returns
    -------
    list of dict
        Copies enrichies de ``distance_m`` et ``aspect_delta_deg``,
        triées par distance. Sans titulaire.

    Raises
    ------
    ValueError
        Rayon ou coordonnées d'origine invalides.
    """
    _require_wgs84(origin_lat, origin_lon)
    if radius_m < 0.0:
        raise ValueError("radius_m doit être positif ou nul")
    if not math.isfinite(wind_from_deg):
        raise ValueError("wind_from_deg doit être fini")

    kept: list[dict[str, Any]] = []
    for parcel in parcels:
        coords = _parcel_lat_lon(parcel)
        if coords is None:
            continue
        plat, plon = coords
        try:
            aspect = float(parcel["aspect_p50_deg"])
        except (KeyError, TypeError, ValueError):
            continue
        if not math.isfinite(aspect):
            continue
        distance = haversine_m(origin_lat, origin_lon, plat, plon)
        if distance > radius_m:
            continue
        delta = float(circular_delta_deg(aspect, wind_from_deg))
        facing = bool(
            np.asarray(
                faces_wind(aspect, wind_from_deg, tolerance_deg=tolerance_deg)
            ).item()
        )
        if not facing:
            continue
        row = _strip_owner(parcel)
        row["distance_m"] = round(distance, 1)
        row["aspect_delta_deg"] = round(delta, 1)
        kept.append(row)
    kept.sort(key=lambda item: (item["distance_m"], -float(item.get("suitability") or 0.0)))
    return kept


def parcels_by_day(
    parcels: list[dict[str, Any]],
    forecast: WindForecast,
    *,
    origin_lat: float,
    origin_lon: float,
    radius_m: float = RADIUS_M_DEFAULT,
    tolerance_deg: float = ASPECT_TOLERANCE_DEG,
) -> list[dict[str, Any]]:
    """Pour chaque jour de la prévision, les parcelles encore face au vent.

    Parameters
    ----------
    parcels :
        Parcelles scorées (lat, lon, aspect_p50_deg).
    forecast :
        Sortie ``fetch_forecast`` / ``parse_forecast``.
    origin_lat, origin_lon, radius_m, tolerance_deg :
        Même sémantique que ``filter_parcels``.

    Returns
    -------
    list of dict
        Un dict par jour : ``date``, ``wind_from_deg``,
        ``wind_speed_max_kmh``, ``n_parcels``, ``parcels``.
    """
    days: list[dict[str, Any]] = []
    for day in forecast.daily[:FORECAST_DAYS]:
        kept = filter_parcels(
            parcels,
            origin_lat=origin_lat,
            origin_lon=origin_lon,
            wind_from_deg=day.direction_from_deg,
            radius_m=radius_m,
            tolerance_deg=tolerance_deg,
        )
        days.append(
            {
                "date": day.date,
                "wind_from_deg": day.direction_from_deg,
                "wind_speed_max_kmh": day.speed_max_kmh,
                "cardinal": cardinal_from_deg(day.direction_from_deg),
                "n_parcels": len(kept),
                "parcels": kept,
            }
        )
    return days


def wind_summary() -> str:
    """Résumé d'une ligne pour le CLI."""
    radius_km = RADIUS_M_DEFAULT / 1000.0
    return (
        f"Open-Meteo {FORECAST_DAYS} jours, vent {WIND_HEIGHT_M} m, "
        f"aspect face au vent ± {ASPECT_TOLERANCE_DEG:.0f}°, "
        f"rayon défaut {radius_km:.0f} km (WGS84, haversine)"
    )
