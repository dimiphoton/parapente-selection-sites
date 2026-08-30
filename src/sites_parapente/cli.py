"""Point d'entrée en ligne de commande du projet."""

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
    args = parser.parse_args()
    if args.crs:
        provinces = ", ".join(PROVINCES)
        print(f"EPSG:{CRS_EPSG} ({CRS_NAME}) - {EXTENT_NAME} ({provinces})")


if __name__ == "__main__":
    main()
