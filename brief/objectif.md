# Objectif du projet

- **But** : produire une liste de parcelles ardennaises favorables au
  décollage en parapente (pente, orientation, occupation du sol), les
  identifier au cadastre, et les filtrer dans une webapp selon la
  position de l'utilisateur, un rayon réglable, et le vent prévu sur
  trois jours.
- **Origine** : brief portfolio
  `brief/01-parapente-selection-sites-wallonie.md`, amendé au cadrage
  du 2026-08-30 (webapp géolocalisée, vent à 3 jours, parcelles
  cadastrales). Travail solo, pas de PR.
- **Contraintes de départ** :
  - Périmètre v1 : Ardenne (provinces de Namur, Luxembourg, Liège),
    pas la Wallonie entière.
  - CRS unique : Lambert 2008, EPSG:3812.
  - ETL d'intégration : **Python** (intérim) — GeoJSON cadastre +
    ``raster2pgsql``. **FME reporté** (licence Form trop lourde pour
    maintenant) ; le `.fmw` reviendra plus tard sur le même schéma
    PostGIS.
  - Calculs de pente / aspect : GDAL / GeoPandas à partir du MNT
    LiDAR SPW 2021–2022.
  - Occupation du sol : WALOUS (SPW) en priorité ; Corine seulement
    en dépannage (maille 25 ha, trop grossière à la parcelle).
  - Cadastre CADGIS : références de parcelle (capakey, commune,
    nature, superficie). **Pas de nom de propriétaire dans le dépôt
    ni dans GitHub Pages** — voir `docs/decisions.md`.
  - Webapp Streamlit utilisable : géolocalisation (position actuelle
    ou point cliqué), rayon réglable, carte des parcelles, filtre
    vent Open-Meteo (prévision 3 jours, parcelles face au vent).
  - QGIS pour les cartes de restitution (chemins relatifs).
  - Aucune donnée brute volumineuse committée (`data/raw/` ignoré).
