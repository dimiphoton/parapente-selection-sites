# Roadmap

Projet **géospatial** : overlay pondéré (pente, aspect, occupation du
sol) × cadastre ardennais, webapp Streamlit géolocalisée, filtre vent
Open-Meteo à 3 jours. ETL d'intégration dans FME ; PostGIS pour le
modèle ; QGIS pour les cartes de restitution.

- [x] **Cadrage** — identité (Géospatial · Loisirs outdoor), objectif
  (webapp + parcelles + vent 3 jours), décisions (CRS 3812, WALOUS,
  propriétaires nominatifs hors dépôt public), README et covers.
- [ ] **Socle** — package `sites_parapente`, `data/raw|processed|local`,
  `etl/`, `qgis/`, `sql/`, CRS et licences dans le README, `init-project`.
- [ ] **MNT et dérivés** — emprise Ardenne, pente et aspect depuis le
  MNT LiDAR SPW 2021–2022 (GDAL/GeoPandas), tests sur une tuile.
- [ ] **Occupation du sol** — WALOUS (Corine seulement si WALOUS
  indisponible), alignement CRS, classes retenues / exclues.
- [ ] **Schéma PostGIS** — `sql/schema_postgis.sql`, index spatiaux,
  tables pente / aspect / occupation / parcelles / score.
- [ ] **ETL FME** — `etl/workspace.fmw` versionné : intégration MNT,
  occupation, cadastre vers PostGIS. Pause si FME n'est pas installé.
- [ ] **Overlay pondéré** — seuils et poids justifiés (pente, aspect,
  occupation), raster de suitability, documentation dans `docs/`.
- [ ] **Cadastre** — intersection des zones favorables avec CADGIS
  (capakey, commune, nature, superficie). Jointure propriétaire
  uniquement via `data/local/` (non commité).
- [ ] **Filtre vent** — Open-Meteo (prévision 3 jours), rayon réglable
  autour d'un point, parcelles dont l'aspect est face au vent (± 45°).
- [ ] **Webapp** — Streamlit : géoloc ou clic carte, rayon, horizon
  vent, liste et carte des parcelles. Rien de nominatif en public.
- [ ] **Restitution QGIS** — projet `.qgz` (chemins relatifs), export
  CSV/GeoJSON des parcelles, présentations à jour.
