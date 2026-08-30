# Décisions

| Date | Décision | Alternative envisagée | Raison |
|---|---|---|---|
| 2026-08-30 | Métier **Géospatial**, domaine **Loisirs outdoor** | Mobilité ; stats publiques | Un recruteur coche « geospatial / GIS », pas un poste transport ou open-data générique. Le secteur est la pratique outdoor, pas le territoire wallon. |
| 2026-08-30 | Stack **Python / GeoPandas / PostGIS / Streamlit / FME** | DuckDB spatial à la place de PostGIS ; Folium seul sans Streamlit | Le brief impose PostGIS et FME. La webapp géolocalisée justifie Streamlit (5ᵉ badge). DuckDB spatial ne remplace pas le modèle PostGIS demandé. |
| 2026-08-30 | CRS **EPSG:3812** (Lambert 2008) | Lambert 72 EPSG:31370 | Standard SPW actuel pour les couches wallonnes récentes (MNT LiDAR, WALOUS, CADGIS). Un seul CRS partout. |
| 2026-08-30 | Périmètre **Ardenne** (Namur, Luxembourg, Liège) | Wallonie entière dès v1 | Volume LiDAR 0,5–1 m ; l'Ardenne a le relief utile. Extension wallonne = stretch, pas v1. |
| 2026-08-30 | Occupation du sol : **WALOUS** en priorité | Corine Land Cover d'emblée | Corine a une maille minimale de 25 ha, trop grossière pour juger une parcelle de décollage. |
| 2026-08-30 | **Pas de nom de propriétaire** dans le repo, les exports publics, ni la webapp déployée | Publier l'identité cadastrale dans la table finale | Le plan CADGIS ouvert n'a pas les noms. La matrice cadastrale nominative n'est pas de l'open data (RGPD). Usage local optionnel : fichier non versionné `data/local/proprietaires.csv` (capakey → titulaire), jamais commité, jamais servi sur GitHub Pages. La table publique identifie la parcelle (capakey, commune, nature, superficie, score). |
| 2026-08-30 | Filtre vent : **prévision Open-Meteo 3 jours**, rayon réglable, parcelles dont l'aspect est face au vent (± 45°) | Vent climatologique annuel uniquement ; vent temps réel sans horizon | Demande de cadrage : utile pour « où aller dans les 3 prochains jours », pas seulement l'instant T. Seuil ± 45° = règle simple, documentée, ajustable. |
| 2026-08-30 | Pente / aspect : **Horn 1981 en numpy**, tuile de test synthétique | Appeler GDAL `gdaldem` ou rasterio dès cette étape | Pas d'install GDAL/rasterio à valider pour l'algo. Le MNT LiDAR 0,5 m de l'Ardenne est trop gros pour le repo. La lecture GeoTIFF viendra à l'ingestion (une tuile réelle dans `data/raw/`, non commitée). |
