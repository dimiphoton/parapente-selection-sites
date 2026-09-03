"""Point d'entrée en ligne de commande : cadrage spatial et ETL."""

from __future__ import annotations

import argparse

from sites_parapente.config import CRS_EPSG, CRS_NAME, EXTENT_NAME, PROVINCES


def main() -> None:
    """Affiche le cadrage spatial ou l'aide du CLI."""
    parser = argparse.ArgumentParser(
        description="Sites de décollage parapente en Ardenne."
    )
    parser.add_argument(
        "--crs",
        action="store_true",
        help="Affiche le CRS et le périmètre du projet.",
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
    args = parser.parse_args()
    if args.crs:
        provinces = ", ".join(PROVINCES)
        print(f"EPSG:{CRS_EPSG} ({CRS_NAME}) - {EXTENT_NAME} ({provinces})")
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


if __name__ == "__main__":
    main()
