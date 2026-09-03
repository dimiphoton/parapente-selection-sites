# Roadmap

Projet **géospatial** : overlay pondéré (pente, aspect, occupation du
sol) × cadastre ardennais, webapp Streamlit géolocalisée, filtre vent
Open-Meteo à 3 jours. ETL d'intégration dans FME ; PostGIS pour le
modèle ; QGIS pour les cartes de restitution.

- [x] **Cadrage** — identité (Géospatial · Loisirs outdoor), objectif
  (webapp + parcelles + vent 3 jours), décisions (CRS 3812, WALOUS,
  propriétaires nominatifs hors dépôt public), README et covers.
- [x] **Socle** — package `sites_parapente`, `data/raw|processed|local`,
  `etl/`, `qgis/`, `sql/`, CRS et licences dans le README.
- [x] **MNT et dérivés** — pente et aspect (Horn 1981, numpy) testés
  sur une tuile synthétique 1 m. Le MNT LiDAR SPW n'est pas commité
  (volume) ; lecture GeoTIFF (rasterio) à l'ingestion.
- [x] **Occupation du sol** — WALOUS 2023 (11 classes, EPSG:3812) :
  ouverts = prairie / culture / sol nu ; exclus = forêt, arbustes,
  eau, artificialisé. Corine écarté. Tests sur tuile synthétique.
- [x] **Schéma PostGIS** — `sql/schema_postgis.sql` : rasters pente /
  aspect / occupation, parcelles (capakey, pas de propriétaire),
  score, index GIST, EPSG:3812.
- [x] **ETL Python** *(intérim, FME plus tard)* — parcelles GeoJSON
  (Ardenne, sans propriétaires) + commandes ``raster2pgsql`` vers
  PostGIS. Pas de GeoPandas.
- [ ] **ETL FME** — `etl/workspace.fmw` quand la licence Form sera
  activée (même schéma PostGIS).
- [x] **Overlay pondéré** — seuils et poids justifiés (pente 50 %,
  aspect 30 %, sol 20 %), veto WALOUS, raster 0–1, `docs/overlay.md`.
- [x] **Cadastre** — intersection overlay × CADGIS (moyenne ≥ 0,20),
  capakey / commune / nature / superficie. Titulaire seulement via
  `data/local/` (non commité).
- [x] **Filtre vent** — Open-Meteo (prévision 3 jours), rayon réglable
  autour d'un point, parcelles dont l'aspect est face au vent (± 45°).
- [ ] **Webapp** — Streamlit : géoloc ou clic carte, rayon, horizon
  vent, liste et carte des parcelles. Rien de nominatif en public.
- [ ] **Restitution QGIS** — projet `.qgz` (chemins relatifs), export
  CSV/GeoJSON des parcelles, présentations à jour.
