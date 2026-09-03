# Paragliding takeoff sites in Wallonia

| | |
|---|---|
| **Role** | Geospatial |
| **Domain** | Outdoor recreation |
| **Stack** | ![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white) ![GeoPandas](https://img.shields.io/badge/GeoPandas-vector-green) ![PostGIS](https://img.shields.io/badge/PostGIS-spatial-336791?logo=postgresql&logoColor=white) ![Streamlit](https://img.shields.io/badge/Streamlit-webapp-FF4B4B?logo=streamlit&logoColor=white) ![FME](https://img.shields.io/badge/FME-ETL-orange) |
| **Level** | Intermediate |
| **Status** | In progress |

Geospatial · Outdoor recreation · Python / GeoPandas / PostGIS / Streamlit / FME

## Objective

Which Ardennes cadastral parcels have the slope and aspect for a
paragliding takeoff — and which of those still face the wind in the
next three days, within a radius of where you are?

The project builds a weighted overlay (LiDAR DEM, land cover, cadastre),
stores it in PostGIS, and serves a small Streamlit app: current
position (or a clicked point), adjustable radius, Open-Meteo 3-day
wind, parcels whose aspect faces that wind.

Terrain score (0–1) is `0.50 × slope + 0.30 × aspect + 0.20 × land
cover`, with a hard veto on forest / water / artificial surfaces.
Slope is usable between 10° and 42° (plateau 16–28°). Aspect prefers
south-west (prevailing Belgian wind) but does not zero-out the north-east.
Daily wind is a later filter, not a fourth weight. Details:
[`docs/overlay.md`](docs/overlay.md).

Owner names are **not** published. The public table identifies the
parcel (capakey, municipality, land nature, area, score). A local
optional file can join a lawful cadastral extract; it is never
committed.

## Data

- **DEM**: Wallonia LiDAR 2021–2022 (SPW, CC BY 4.0). Slope and aspect
  (Horn 1981) live in `sites_parapente.terrain`. Put a real GeoTIFF in
  `data/raw/` locally — it is not committed.
- **Land cover**: WALOUS 2023 (SPW, 1 m, EPSG:3812). Open for takeoff:
  grassland (7), annual crops (6), bare soil (4). Forest, shrubs,
  water and artificial surfaces are out. Corine is not used.
- **Cadastre**: CADGIS parcel plan (capakey, no owner names).
- **Wind**: Open-Meteo forecast, 3-day horizon, no API key.
- **Extent**: Ardennes (Namur, Luxembourg, Liège provinces). CRS:
  Lambert 2008, EPSG:3812.

Raw files stay in `data/raw/` (gitignored). A local optional owner
join lives in `data/local/` (also gitignored). See `brief/objectif.md`
and `docs/decisions.md`.

### Licences

| Layer | Source | Licence |
|---|---|---|
| LiDAR DEM 2021–2022 | SPW | CC BY 4.0 |
| WALOUS land cover | SPW | CC BY 4.0 (confirm on download) |
| CADGIS parcel plan | SPF Finances / SPW | open cadastral plan licence (no owner names) |
| Wind forecast | Open-Meteo | their terms (no key) |

Cite the source and date in metadata when a layer is ingested. Do not
commit owner names.

## Result

The pixel suitability raster is implemented and tested on synthetic
tiles. Ranked cadastral parcels and the wind-aware map come after the
cadastre intersection and the Streamlit app.

## Reproduce

TBD as the pipeline lands. Skeleton:

```bash
pip install -e ".[dev]"
pytest
python -m sites_parapente.cli --crs
python -m sites_parapente.cli --overlay
python -m sites_parapente.cli --etl-parcels data/processed/cadastre.geojson
python -m sites_parapente.cli --etl-raster pente.tif parapente.pente
# PostGIS (local): psql -d <db> -f sql/schema_postgis.sql
```

FME Form is **deferred** (licence). Python ETL is the current path.
PostGIS, `raster2pgsql` and QGIS 3.x are expected locally.

## Repo structure

```
src/sites_parapente/   # package (CRS EPSG:3812 in config.py)
data/raw/              # gitignored downloads
data/processed/        # regenerable layers
data/local/            # optional nominative join, gitignored
etl/                   # FME workspace later ; Python ETL is in src/
qgis/                  # QGIS project, relative paths
sql/schema_postgis.sql # schema parapente (EPSG:3812, no owner names)
docs/overlay.md        # weights and thresholds (FR)
webapp/                # Streamlit app (later)
```

See `ROADMAP.md` (French) for the feature sequence. `JOURNAL.md` tracks
what landed and why.

## Presentations

Two audiences × two languages (Marp theme `portfolio`, HTML on GitHub Pages).
The recruiter deck is a ~6-minute pitch; the technical deck is a ~12-minute
deep dive. They may diverge a lot — the bar is attractive and informative
for each audience, not a mirrored pair of slides.

- [Recruiter overview (EN)](docs/slides/presentation-recruteur-en.html)
- [Technical deep dive (EN)](docs/slides/presentation-technique-en.html)
- [Présentation grand public (FR)](docs/slides/presentation-recruteur-fr.html)
- [Présentation technique (FR)](docs/slides/presentation-technique-fr.html)
