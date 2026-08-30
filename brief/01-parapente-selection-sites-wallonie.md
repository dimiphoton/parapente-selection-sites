# Sélection de sites de parapente en Wallonie — analyse multicritère

## Contexte et problématique

Le choix d'un site de décollage de parapente répond à des critères précis : une pente suffisante et orientée face au vent, un terrain dégagé, et un accès légal à la parcelle. Ces critères sont dispersés entre plusieurs sources : modèle de terrain, données météo, cadastre. Une analyse géomatique multicritère — le "weighted overlay", exercice fondateur de la discipline — permet de les croiser systématiquement plutôt que de les évaluer site par site à l'œil.

Ce projet répond à la question :

> Quelles parcelles wallonnes réunissent objectivement les conditions de terrain (pente, orientation) favorables à la pratique du parapente, et lesquelles restent viables selon les conditions de vent du moment ?

## Objectif

Construire une analyse multicritère (overlay pondéré) combinant modèle numérique de terrain, occupation du sol et cadastre, pour produire une liste de parcelles wallonnes éligibles à la pratique du parapente — assortie d'une couche dynamique optionnelle de filtrage selon le vent en temps réel.

## Compétences démontrées

- Analyse de terrain (calcul de pente et d'exposition à partir d'un MNT)
- Analyse multicritère / overlay pondéré
- Intégration de sources hétérogènes (raster MNT, vecteur cadastre, API météo)
- Base de données spatiale (PostGIS, requêtes spatiales)
- ETL géospatial (FME — obligatoire, pas de contournement en script)
- Cartographie et restitution (QGIS)
- Respect des données personnelles (traitement du cadastre sans données de propriété)

## Approche et choix techniques

- **Périmètre initial** : Ardenne (provinces de Namur, Luxembourg, Liège), où le relief est significatif — extension à la Wallonie entière possible ensuite. Restreindre le périmètre limite le volume de données LiDAR à traiter sans dénaturer l'exercice.
- **Couche terrain** : MNT LiDAR 2021-2022 de la Wallonie (résolution 0,5 m ou 1 m, SPW, licence CC BY 4.0) — calcul de pente et d'orientation (aspect) via QGIS/GDAL.
- **Couche cadastre** : plan parcellaire CADGIS (SPW / SPF Finances) — utilisé uniquement pour les références de parcelle, jamais pour l'identité des propriétaires. Ce point n'est pas une option : c'est une limite volontaire du projet, pour des raisons de vie privée et de faisabilité.
- **Couche occupation du sol** : à déterminer selon la donnée wallonne la plus fine disponible ; à défaut, Corine Land Cover en dépannage, en connaissant sa limite de résolution (maille minimale de 25 ha, grossière pour un usage parcellaire).
- **ETL** : l'intégration des sources (MNT raster, cadastre vecteur, occupation du sol, éventuellement l'API météo) est construite dans FME, pas en scripts Python de contournement — c'est explicitement l'objectif de montée en compétence outil de ce projet.
- **Overlay pondéré** : combinaison des couches (pente, orientation, occupation du sol) en un score de suitability, avec seuils et pondérations justifiés et documentés — pas de pondération arbitraire non expliquée.
- **Intersection avec le cadastre** : les zones jugées favorables sont croisées avec les parcelles pour produire une liste finale avec référence cadastrale, commune, province — jamais de coordonnées de propriétaire.
- **Couche dynamique (bonus)** : intégration de l'API Open-Meteo (gratuite, sans clé, données de vent horaires) pour filtrer, à une date/heure donnée, les sites dont l'orientation correspond à la direction du vent réel.

## Livrables attendus

1. Scripts de calcul des couches dérivées du MNT (pente, orientation).
2. Modèle de données PostGIS documenté (schéma, index spatiaux).
3. Workspace FME (.fmw) versionné réalisant l'intégration des sources, documenté et exécutable.
4. Overlay pondéré avec justification explicite des poids et seuils.
5. Table finale des parcelles éligibles (référence cadastrale, commune, score de suitability) — export CSV/GeoJSON.
6. Carte(s) QGIS de restitution (sites candidats sur fond MNT/hillshade).
7. Script optionnel de filtrage dynamique par vent (Open-Meteo).
8. README complet : sources, méthodologie, pondérations, limites.

## Structure de repo attendue

```
projet-parapente-wallonie/
├── README.md
├── data/
│   ├── raw/            # non commité — voir .gitignore
│   └── processed/
├── src/
│   ├── terrain_analysis.py
│   ├── overlay.py
│   ├── cadastre_join.py
│   └── wind_filter.py
├── etl/
│   └── workspace.fmw    # workspace FME versionné — obligatoire
├── qgis/
│   └── projet.qgz
├── sql/
│   └── schema_postgis.sql
└── requirements.txt
```

## Règles strictes de professionnalisme

- CRS explicite et cohérent dans tout le projet (Lambert 2008, EPSG:3812, ou Lambert 72, EPSG:31370), documenté dans le README.
- Chaque source de données citée avec sa licence et sa date de mise à jour.
- Aucune donnée personnelle (identité de propriétaire) traitée, stockée ou publiée — uniquement des références cadastrales officielles.
- Métadonnées minimales pour chaque couche produite : titre, résumé, emprise, CRS, date.
- Projet QGIS reproductible : chemins relatifs uniquement, jamais de chemin absolu codé en dur.
- Le fichier `.fmw` du workspace FME est versionné dans le repo et exécutable — jamais une simple capture d'écran sans le fichier source.
- Environnement Python figé (`requirements.txt`).
- Commits atomiques avec messages conventionnels.
- Toute limite méthodologique explicitée dans le README (résolution des données, incertitude sur l'occupation du sol, absence de validation terrain).

## Amendements au cadrage (2026-08-30)

Validés avec l'utilisateur, détaillés dans `brief/objectif.md` et
`docs/decisions.md` :

- **Webapp utilisable** (Streamlit) : position actuelle (géoloc ou
  clic), rayon réglable, carte des parcelles candidates.
- **Vent** : prévision Open-Meteo sur **3 jours** (option), algorithme
  simple — ne retenir que les parcelles dont l'aspect est face au vent
  (± 45°).
- **Parcelles cadastrales** : identification publique par capakey,
  commune, nature, superficie et score.
- **Propriétaire** : demandé au cadrage, **pas publié**. Le plan CADGIS
  ouvert n'a pas les noms ; la matrice nominative n'est pas de l'open
  data. Jointure locale optionnelle via `data/local/proprietaires.csv`
  (non versionné). Rien de nominatif dans le repo ni sur GitHub Pages.
- **FME** : toujours obligatoire pour l'ETL ; installation prévue plus
  tard. L'autopilot se met en pause si FME manque à cette étape.

## Pour aller plus loin (optionnel)

- Extension du périmètre à la Wallonie entière.
- Analyse de l'accessibilité (distance à un parking, à une route) comme critère additionnel.
- Climatologie du vent (historique Open-Meteo) pour une carte de fiabilité saisonnière par site, en complément du filtrage temps réel.
- Ré-exporter le raster pente/exposition en Cloud-Optimized GeoTIFF (COG) avec des métadonnées STAC minimales — pratique directe de la pile cloud géospatial « classique » restée non couverte par ailleurs dans le parcours de compétences.
- Traiter le nuage de points LiDAR brut (LAS/LAZ, via PDAL ou laspy) pour classifier soi-même les points sol et produire le MNT, plutôt que consommer un MNT déjà dérivé.
