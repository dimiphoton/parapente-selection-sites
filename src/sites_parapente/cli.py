"""Point d'entrée en ligne de commande : cadrage, overlay, ETL, vent."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from sites_parapente.config import CRS_EPSG, CRS_NAME, EXTENT_NAME, PROVINCES


def main() -> None:
    """Affiche le cadrage, l'overlay, le cadastre, le vent, ou lance l'ETL."""
    parser = argparse.ArgumentParser(
        description="Sites de décollage parapente en Ardenne."
    )
    parser.add_argument(
        "--crs",
        action="store_true",
        help="Affiche le CRS et le périmètre du projet.",
    )
    parser.add_argument(
        "--overlay",
        action="store_true",
        help="Affiche les poids et seuils de l'overlay pondéré.",
    )
    parser.add_argument(
        "--cadastre",
        action="store_true",
        help="Affiche la règle d'intersection overlay × parcelles.",
    )
    parser.add_argument(
        "--etl-parcels",
        metavar="GEOJSON",
        help="Charge un GeoJSON cadastral (Ardenne, sans propriétaires).",
    )
    parser.add_argument(
        "--etl-raster",
        nargs=2,
        metavar=("GEOTIFF", "TABLE"),
        help="Affiche la commande raster2pgsql (ex. pente.tif parapente.pente).",
    )
    parser.add_argument(
        "--wind",
        action="store_true",
        help="Affiche la règle du filtre vent (3 jours, ± 45°, rayon).",
    )
    parser.add_argument(
        "--forecast",
        nargs=2,
        metavar=("LAT", "LON"),
        help="Prévision Open-Meteo 3 jours au point WGS84 (réseau).",
    )
    parser.add_argument(
        "--filtre-vent",
        metavar="JSON",
        help="Filtre un JSON de parcelles (lat, lon, aspect_p50_deg) au vent du jour 0.",
    )
    parser.add_argument(
        "--lat",
        type=float,
        help="Latitude WGS84 (origine du rayon, avec --filtre-vent).",
    )
    parser.add_argument(
        "--lon",
        type=float,
        help="Longitude WGS84 (origine du rayon, avec --filtre-vent).",
    )
    parser.add_argument(
        "--radius-m",
        type=float,
        default=None,
        help="Rayon en mètres (défaut 30000).",
    )
    parser.add_argument(
        "--day",
        type=int,
        default=0,
        help="Jour de prévision 0–2 (avec --filtre-vent, défaut 0 = aujourd'hui).",
    )
    args = parser.parse_args()
    if args.crs:
        provinces = ", ".join(PROVINCES)
        print(f"EPSG:{CRS_EPSG} ({CRS_NAME}) - {EXTENT_NAME} ({provinces})")
        return
    if args.overlay:
        from sites_parapente.overlay import overlay_summary

        print(overlay_summary())
        return
    if args.cadastre:
        from sites_parapente.cadastre import cadastre_summary

        print(cadastre_summary())
        return
    if args.etl_parcels:
        from pathlib import Path

        from sites_parapente.etl import load_geojson_parcels

        rows = load_geojson_parcels(Path(args.etl_parcels))
        print(f"{len(rows)} parcelles Ardenne (owners exclus)")
        return
    if args.etl_raster:
        from pathlib import Path

        from sites_parapente.etl import raster2pgsql_command

        geotiff, table = args.etl_raster
        print(" ".join(raster2pgsql_command(Path(geotiff), table)))
        return
    if args.wind:
        from sites_parapente.wind import wind_summary

        print(wind_summary())
        return
    if args.forecast:
        from sites_parapente.wind import cardinal_from_deg, fetch_forecast

        lat, lon = float(args.forecast[0]), float(args.forecast[1])
        forecast = fetch_forecast(lat, lon)
        for day in forecast.daily:
            card = cardinal_from_deg(day.direction_from_deg)
            print(
                f"{day.date}  {card} {day.direction_from_deg:.0f}°  "
                f"{day.speed_max_kmh:.0f} km/h max"
            )
        return
    if args.filtre_vent:
        from sites_parapente.wind import (
            RADIUS_M_DEFAULT,
            fetch_forecast,
            parcels_by_day,
        )

        if args.lat is None or args.lon is None:
            parser.error("--filtre-vent exige --lat et --lon")
        raw = json.loads(Path(args.filtre_vent).read_text(encoding="utf-8"))
        if isinstance(raw, dict) and "features" in raw:
            parcels = []
            for feat in raw["features"]:
                props = dict(feat.get("properties") or {})
                parcels.append(props)
        else:
            parcels = list(raw)
        forecast = fetch_forecast(args.lat, args.lon)
        days = parcels_by_day(
            parcels,
            forecast,
            origin_lat=args.lat,
            origin_lon=args.lon,
            radius_m=args.radius_m if args.radius_m is not None else RADIUS_M_DEFAULT,
        )
        if not 0 <= args.day < len(days):
            parser.error(f"--day doit être entre 0 et {len(days) - 1}")
        chosen = days[args.day]
        print(
            f"{chosen['date']}  {chosen['cardinal']} "
            f"{chosen['wind_from_deg']:.0f}°  "
            f"{chosen['n_parcels']} parcelles"
        )
        for row in chosen["parcels"]:
            capakey = row.get("capakey", "?")
            dist_km = float(row["distance_m"]) / 1000.0
            print(f"{capakey}  {dist_km:.1f} km  Δ{row['aspect_delta_deg']:.0f}°")
        return


if __name__ == "__main__":
    main()
