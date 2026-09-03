# Journal de développement

## 2026-09-03 — Filtre vent

- Open-Meteo 3 jours (vent 10 m, dominant journalier), urllib sans clé.
  Parcelle gardée si haversine ≤ rayon (30 km défaut) et aspect face au
  vent ± 45° (écart circulaire). Tests sur JSON-fixture, pas de réseau.
  `docs/wind.md`.

## 2026-09-03 — Cadastre

- Intersection overlay × parcelles (centres de pixels, pas GeoPandas).
  Moyenne de suitability ≥ 0,20 pour retenir. Aspect en moyenne
  circulaire. Export public sans titulaire ; CSV `data/local/` optionnel.

## 2026-09-03 — Overlay pondéré

- Score au pixel 0–1 : pente 50 % (plateau 16–28°), aspect 30 %
  (préféré SW, plancher NE 0,25), occupation 20 % (prairie > sol nu >
  culture). Forêt / plat = veto. Vent du jour hors de ce score.
- `docs/overlay.md` + table raster `parapente.suitability`. Pas de
  LiDAR réel : tests sur tuile synthétique.

## 2026-09-03 — ETL Python (intérim)

- Alternative à FME (licence Form). `etl.py` : GeoJSON cadastre,
  filtre Ardenne, suppression des champs propriétaires, commandes
  raster2pgsql. FME reste une case ouverte.

## 2026-08-30 — Schéma PostGIS

- `sql/schema_postgis.sql` : schema `parapente`, rasters + parcelles
  (capakey) + score, index GIST, SRID 3812, vue publique sans nom.

## 2026-08-30 — Occupation du sol

- WALOUS 2023 : codes 4, 6, 7 ouverts (sol nu, culture, prairie) ;
  le reste exclu. CRS 3812 obligatoire. Tests sur tuile 3×3.

## 2026-08-30 — MNT et dérivés

- `terrain.slope_and_aspect` : Horn 1981, pente et aspect (aval, 0 =
  nord). 4 tests sur tuile synthétique 1 m. Pas de LiDAR dans le repo.

## 2026-08-30 — Socle

- Package `sites_parapente`, dossiers `data/`, `etl/`, `qgis/`, `sql/`.
- CRS et licences dans le README. CLI `--crs`. Tests de cadrage spatial.
- Hook Windows : `.cursor/hooks/autopilot-stop.cmd` (py/python), log
  local `last-stop.log`.

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
