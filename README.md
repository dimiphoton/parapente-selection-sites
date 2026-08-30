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

Owner names are **not** published. The public table identifies the
parcel (capakey, municipality, land nature, area, score). A local
optional file can join a lawful cadastral extract; it is never
committed.

## Data

- **DEM**: Wallonia LiDAR 2021–2022 (SPW, CC BY 4.0), slope and aspect.
- **Land cover**: WALOUS (SPW) in priority; Corine Land Cover only as
  fallback (25 ha minimum mapping unit — too coarse for a parcel).
- **Cadastre**: CADGIS parcel plan (capakey, no owner names).
- **Wind**: Open-Meteo forecast, 3-day horizon, no API key.
- **Extent**: Ardennes (Namur, Luxembourg, Liège provinces). CRS:
  Lambert 2008, EPSG:3812.

Raw files stay in `data/raw/` (gitignored). See `brief/objectif.md`
and `docs/decisions.md`.

## Result

TBD — first ranked parcel list and a usable map, after the overlay
and the wind filter.

## Reproduce

TBD as the pipeline lands. Skeleton:

```bash
pip install -e ".[dev]"
pytest
python -m mon_projet.cli --help
```

FME Form is required for the integration workspace (`etl/workspace.fmw`).
PostGIS and QGIS 3.x are expected locally.

## Repo structure

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
