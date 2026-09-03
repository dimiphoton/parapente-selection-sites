# Cadastre

Intersection du raster de suitability avec le plan parcellaire CADGIS.
Sortie : une ligne par parcelle **favorable**, identifiée par capakey,
sans nom de propriétaire.

Implémentation : `sites_parapente.cadastre` (GeoJSON + numpy, pas de
GeoPandas). Les parcelles arrivent déjà filtrées Ardenne et sans owner
via `etl.load_geojson_parcels`.

## Règle de rétention

Sur les pixels dont le centre tombe dans la parcelle :

- pente : médiane (`slope_p50_deg`)
- aspect : **moyenne circulaire** (colonne `aspect_p50_deg` du schéma :
  pas une médiane linéaire, qui casserait le 0°/360°)
- WALOUS : classe majoritaire ; `landcover_open` si 4, 6 ou 7
- suitability : **moyenne** des pixels finis

La parcelle est **gardée** si cette moyenne est **≥ 0,20**. Une forêt
avec une lisière herbeuse trop mince tombe en dessous. Une parcelle
moitié prairie / moitié bois (~ 0,5) passe : assez de terrain ouvert
pour un décollage, le score le dit.

Les parcelles hors emprise du raster, ou sans pixel fini, sont ignorées.

## Propriétaire

Le plan CADGIS ouvert n'a pas les noms. Un CSV local optionnel
`data/local/proprietaires.csv` (gitignoré) peut joindre un titulaire
**en mémoire** :

```text
capakey,titulaire
21683D0265/02R020,exemple
```

`public_record` / `to_public_geojson` enlèvent `titulaire`. Rien de
nominatif dans le dépôt, l'export, ni plus tard la webapp déployée.

## Limites

- Rasterisation par centre de pixel : un liseré de 1 m peut basculer.
- Pas de LiDAR ni de CADGIS réel dans git : les tests sont une tuile
  4×4.
- Ce n'est pas une autorisation d'accéder à la parcelle.

## Reproduire

```bash
pytest tests/test_cadastre.py
python -m sites_parapente.cli --cadastre
```
