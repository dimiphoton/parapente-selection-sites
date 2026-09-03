# Overlay pondéré

Score de **suitability** au pixel, dans `[0, 1]`. Trois critères issus du
MNT (pente, aspect) et de WALOUS (occupation du sol). Ce n'est pas un
modèle statistique : pas d'apprentissage, pas d'échantillon de sites
labellisés. Les poids sont des choix d'expertise, documentés ici.

Le vent prévu (Open-Meteo, 3 jours) **n'entre pas** dans ce score. C'est
un filtre ultérieur : on gardera les parcelles dont l'aspect est face au
vent du jour (± 45°). Mélanger les deux recompterait l'orientation.

Implémentation : `sites_parapente.overlay.weighted_overlay`.

## Formule

1. Recoder chaque critère en `[0, 1]`.
2. Moyenne pondérée.
3. **Veto** : occupation fermée **ou** pente hors plage utile → `0`.
4. Pente `NaN` (bords Horn) → `NaN` (inconnu, pas « inapte »).

```
suitability = 0,50 × score_pente
            + 0,30 × score_aspect
            + 0,20 × score_sol
```

| Critère | Poids | Pourquoi ce poids |
|---|---|---|
| Pente | 50 % | Sans pente de décollage, l'herbe et l'azimut ne servent à rien. |
| Aspect | 30 % | En Belgique le flux d'ouest / sud-ouest domine : un versant SW « marche » plus souvent. Un versant NE n'est pas à zéro (jours d'est). |
| Occupation | 20 % | Le vrai tri est le veto (forêt / eau / artificialisé). Parmi les sols **ouverts**, prairie > sol nu > culture. |

## Pente (Horn, degrés)

Le MNT donne un angle avec l'horizontale, pas une pente en %.
Rappel : 10° ≈ 18 %, 16° ≈ 29 %, 28° ≈ 53 %, 42° ≈ 90 %.

| Seuil | Score | Justification |
|---|---|---|
| < 10° | 0 | Plus assez de pente pour convertir une course en décollage (trop long, trop plat). |
| 10° → 16° | 0 → 1 | Pente d'école / début de site. |
| 16° → 28° | 1 | Plage classique d'un décollage en pente herbeuse (club, autonome). |
| 28° → 42° | 1 → 0 | De plus en plus technique ; encore une parcelle, plus un cliff. |
| > 42° | 0 | Hors ciblage v1 (falaise, carrière verticale). |

On ne vise pas le speedflying ni le décollage de falaise.

## Aspect (aval, 0° = nord)

Direction vers laquelle la pente **descend** (même convention que
`terrain.slope_and_aspect`).

- Azimut préféré : **225° (sud-ouest)**.
- Score : `0,25 + 0,75 × (½ + ½ cos(écart))`.
- Face au SW → 1. Face au NE → 0,25. Terrain plat (`NaN`) → 0.

Le plancher 0,25 évite d'éliminer les versants est, utiles par vent
d'est ou régime anticyclonique. Le filtre vent quotidien s'en chargera.

## Occupation du sol (WALOUS 2023)

Veto d'abord (déjà dans `landcover.py`) : seuls les codes **4, 6, 7**
sont ouverts. Ensuite un score de qualité :

| Code | Classe | Score | Pourquoi |
|---|---|---|---|
| 7 | Prairie | 1,00 | Herbe permanente, surface de décollage typique. |
| 4 | Sol nu | 0,80 | Ouvert, mais abrasif et rare en Ardenne hors roche / chantier. |
| 6 | Culture | 0,55 | Ouvert physiquement ; usage saisonnier (semis, chaume, accès). |
| autres | Forêt, arbustes, eau, artificialisé | 0 (veto) | Obstacle, plan d'eau, ou sol construit. |

## Ce que ce score n'est pas

- Pas un classement de parcelles (ça vient à l'intersection cadastre).
- Pas une autorisation de voler : accès, règlement, convention de club.
- Pas une validation terrain : aucun levé de site réel dans le dépôt.
- Pas un substitut au vent du jour.

## Reproduire (tuile synthétique)

```bash
pytest tests/test_overlay.py
python -m sites_parapente.cli --overlay
```
