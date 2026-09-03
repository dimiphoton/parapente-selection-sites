"""Webapp Streamlit : un clic, un jour, des parcelles face au vent.

Jeu de démonstration (capakey fictifs). Rayon 30 km. Pas de GPS,
pas de PostGIS : JSON WGS84 + Open-Meteo.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import folium
import streamlit as st
from streamlit_folium import st_folium

from sites_parapente.parcels import load_parcels_json
from sites_parapente.wind import (
    RADIUS_M_DEFAULT,
    WindForecastError,
    cardinal_from_deg,
    fetch_forecast,
    filter_parcels,
)

DEMO_JSON = Path(__file__).resolve().parent / "demo_parcels.json"
# Centre Ardenne (Marche-en-Famenne), assez central pour le premier rendu.
DEFAULT_LAT = 50.227
DEFAULT_LON = 5.344

st.set_page_config(
    page_title="Décos Ardenne",
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_data(ttl=1800)
def _forecast(lat: float, lon: float):
    """Prévision cachée 30 min ; arrondi ~100 m pour limiter les appels."""
    return fetch_forecast(round(lat, 3), round(lon, 3))


@st.cache_data
def _parcels() -> list[dict]:
    return load_parcels_json(DEMO_JSON)


def _apply_click(folium_out: dict | None) -> None:
    """Si la carte a été cliquée, ce clic devient l'origine."""
    if not folium_out:
        return
    clicked = folium_out.get("last_clicked")
    if not clicked:
        return
    lat = float(clicked["lat"])
    lon = float(clicked["lng"])
    prev = st.session_state.origin
    if abs(lat - prev["lat"]) < 1e-5 and abs(lon - prev["lon"]) < 1e-5:
        return
    st.session_state.origin = {"lat": lat, "lon": lon}
    st.rerun()


def main() -> None:
    if "origin" not in st.session_state:
        st.session_state.origin = {"lat": DEFAULT_LAT, "lon": DEFAULT_LON}

    st.title("Où décoller ces trois jours")
    st.caption(
        "Jeu de démonstration — capakey fictifs. Un clic sur la carte, "
        "un jour, les parcelles dans 30 km face au vent. "
        "Ce n'est pas une autorisation d'accéder au terrain."
    )

    origin = st.session_state.origin
    parcels = _parcels()

    try:
        forecast = _forecast(origin["lat"], origin["lon"])
    except WindForecastError as exc:
        st.error(f"Prévision indisponible : {exc}")
        forecast = None

    day_index = 0
    if forecast is not None and forecast.daily:
        labels = []
        for i, day in enumerate(forecast.daily):
            card = cardinal_from_deg(day.direction_from_deg)
            labels.append(
                f"J+{i}  {day.date}  ·  {card} {day.speed_max_kmh:.0f} km/h"
            )
        day_index = st.radio(
            "Jour",
            options=list(range(len(forecast.daily))),
            format_func=lambda i: labels[i],
            horizontal=True,
            label_visibility="collapsed",
        )
        chosen = forecast.daily[day_index]
        kept = filter_parcels(
            parcels,
            origin_lat=origin["lat"],
            origin_lon=origin["lon"],
            wind_from_deg=chosen.direction_from_deg,
            radius_m=RADIUS_M_DEFAULT,
        )
        st.write(
            f"**{len(kept)} parcelle(s)** à moins de 30 km, "
            f"face au vent {cardinal_from_deg(chosen.direction_from_deg)} "
            f"({chosen.direction_from_deg:.0f}°)."
        )
    else:
        kept = []

    fmap = folium.Map(
        location=[origin["lat"], origin["lon"]],
        zoom_start=9,
        tiles="OpenStreetMap",
    )
    folium.Marker(
        [origin["lat"], origin["lon"]],
        tooltip="Votre point",
        icon=folium.Icon(color="red", icon="flag"),
    ).add_to(fmap)
    folium.Circle(
        [origin["lat"], origin["lon"]],
        radius=RADIUS_M_DEFAULT,
        color="#c0392b",
        weight=2,
        fill=False,
    ).add_to(fmap)
    for row in kept:
        dist_km = float(row["distance_m"]) / 1000.0
        score = row.get("suitability")
        score_txt = f"{float(score):.2f}" if score is not None else "—"
        popup = (
            f"{row.get('commune', '')}<br>"
            f"{row.get('capakey', '')}<br>"
            f"{dist_km:.1f} km · score {score_txt}"
        )
        folium.CircleMarker(
            [float(row["lat"]), float(row["lon"])],
            radius=8,
            color="#1f6aa5",
            fill=True,
            fill_opacity=0.85,
            popup=folium.Popup(popup, max_width=220),
            tooltip=row.get("commune", ""),
        ).add_to(fmap)

    folium_out = st_folium(
        fmap,
        height=360,
        use_container_width=True,
        returned_objects=["last_clicked"],
        key="carte",
    )
    _apply_click(folium_out)

    if kept:
        table = [
            {
                "km": round(float(row["distance_m"]) / 1000.0, 1),
                "commune": row.get("commune", ""),
                "score": row.get("suitability"),
                "capakey": row.get("capakey", ""),
                "écart °": row.get("aspect_delta_deg"),
            }
            for row in kept
        ]
        st.dataframe(table, hide_index=True, use_container_width=True)
        st.caption(
            "Le capakey identifie la parcelle au cadastre. "
            "C'est ce code qu'on donne à un club — pas un nom de propriétaire."
        )
    elif forecast is not None:
        st.info("Aucune parcelle démo dans ce rayon face au vent de ce jour. Cliquez ailleurs.")


main()
