# Journal de développement

## 2026-08-30 — Cadrage

- Identité : Géospatial · Loisirs outdoor · Python / GeoPandas /
  PostGIS / Streamlit / FME. Périmètre Ardenne, CRS EPSG:3812.
- Objectif : overlay pondéré + table de parcelles (capakey) + webapp
  géolocalisée + filtre vent Open-Meteo 3 jours.
- Propriétaires cadastraux nominatifs : hors dépôt et hors Pages
  (RGPD ; CADGIS ouvert sans noms). Fichier local optionnel.
- FME pas encore installé : l'étape ETL écrira `autopilot.pause` si
  besoin. Hook `stop` en place, sans `autopilot.off`.

## 2026-08-30 — Initialisation du projet

- Repo créé à partir du template portfolio.
