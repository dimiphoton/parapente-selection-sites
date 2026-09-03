# Changelog

## [Non publié]

- Cadastre : stats zonales à la parcelle (moyenne suitability ≥ 0,20),
  export capakey sans propriétaire. Tests tuile 4×4. `docs/cadastre.md`.
- Overlay pondéré : score 0–1 au pixel (pente 50 %, aspect 30 %,
  occupation 20 %), veto WALOUS, seuils documentés dans
  `docs/overlay.md`. Tests sur tuile synthétique.
- ETL Python intérim (FME reporté) : parcelles GeoJSON Ardenne sans
  propriétaires, raster2pgsql pour les GeoTIFF.
- Schéma PostGIS versionné (`parapente`) : rasters, parcelles,
  score, index GIST, pas de colonne propriétaire.
- Occupation du sol : WALOUS 2023, masque prairie/culture/sol nu ;
  forêt, eau et artificialisé exclus.
- MNT : pente et aspect (Horn 1981, numpy) testés sur une tuile
  synthétique ; pas de LiDAR commité.
- Socle : package `sites_parapente`, arborescence data/etl/qgis/sql,
  constantes CRS EPSG:3812.
- Cadrage : métier Géospatial, domaine Loisirs outdoor, stack Python /
  GeoPandas / PostGIS / Streamlit / FME. Webapp géolocalisée et filtre
  vent à 3 jours ajoutés à l'objectif. Propriétaires nominatifs exclus
  du dépôt public.
- Initialisation du projet à partir du template portfolio.
