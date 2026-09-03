# Filtre vent

Les parcelles déjà scorées (overlay × cadastre) sont filtrées selon
**où l'on est** et **d'où souffle le vent prévu**. Ce n'est pas un
quatrième poids de l'overlay : on ne recompte pas l'orientation.

Implémentation : `sites_parapente.wind`. Client HTTP : `urllib`
(stdlib), pas de clé. Les tests injectent `urlopen`.

## Physique

- **Direction météo** (Open-Meteo) : azimut **d'où vient** le vent
  (0° = nord, 90° = est).
- **Aspect** (Horn) : azimut de l'**aval**, même origine nord.
- **Face au vent** : on décolle contre le flux, sur un versant qui
  regarde d'où vient le vent → `aspect ≈ wind_from`, à ± 45°.

L'écart est **circulaire** : 350° et 10° font 20°, pas 340°. Un aspect
`NaN` (plat) n'est jamais face au vent.

## Données

| Paramètre | Valeur | Pourquoi |
|---|---|---|
| API | `https://api.open-meteo.com/v1/forecast` | Gratuit, sans clé, horaire. |
| Horizon | **3 jours** (`forecast_days=3`) | Cadrage : « où aller ce week-end », pas l'instant T. |
| Hauteur | vent à **10 m** | Hauteur de décollage, pas le vent 80 m / 120 m. |
| Journalier | `wind_direction_10m_dominant` + `wind_speed_10m_max` | Un azimut par jour pour trier les parcelles. |
| Horaire | direction + vitesse 10 m | Conservé pour la webapp (créneau dans la journée). |
| Fuseau | `Europe/Brussels` | Obligatoire dès qu'on demande du `daily`. |
| Rayon | **30 km** par défaut, réglable | Trajet raisonnable ; haversine WGS84 (GPS = Open-Meteo). |
| Tolérance | **± 45°** | Fenêtre simple, inclusive, documentée. |

Pas de seuil de vitesse : le cadrage ne porte que sur la **direction**.
Un vent trop faible ou trop fort reste un jugement pilote.

## Algorithme

1. Prévision au point utilisateur (WGS84).
2. Pour chaque jour : azimut dominant.
3. Distance haversine ≤ rayon.
4. `circular_delta(aspect_p50_deg, wind_from) ≤ 45°`.
5. Tri par distance. Aucun champ propriétaire n'est recopié.

Les parcelles doivent déjà porter `lat`, `lon` (WGS84) et
`aspect_p50_deg`. La webapp Streamlit sert un JSON démo déjà en GPS.
Le passage Lambert 2008 → WGS84 pour un export CADGIS réel reste un
`ST_Transform` PostGIS — pas de pyproj dans le package.

## Limites

- Une direction dominante par jour lisse les bascules de régime.
- Haversine sphérique, pas ellipsoïde : largement assez à 30 km.
- Open-Meteo n'est pas un briefing de vol (pas de QNH, pas de thermique).
- Ce n'est pas une autorisation d'accès à la parcelle.

## Reproduire

```bash
pytest tests/test_wind.py
python -m sites_parapente.cli --wind
python -m sites_parapente.cli --forecast 50.22 5.34
```
