---
marp: true
theme: portfolio
paginate: true
---

<!-- _class: cover -->
<!-- _paginate: false -->

![bg brightness:0.40](../../pictures/presentations/photos/hero.png)

# Comment filtrer les parcelles
# face au vent prévu à 3 jours
# sans remettre la météo dans l'overlay ?

Géospatial · Loisirs outdoor · Python / GeoPandas / PostGIS / Streamlit / FME

Ardenne · Open-Meteo 10 m · ± 45°

---

<!-- _class: split -->

![bg left:46%](../../pictures/presentations/photos/motivation.png)

# Le score de terrain
# dit quels versants existent.
# Pas quel jour ils marchent.

Un overlay SW-biaisé sans filtre quotidien laisserait des parcelles dos au flux d'est.

**L'enjeu : un week-end, un rayon, un azimut.**

---

<!-- _class: split -->

![bg left:46%](../../pictures/presentations/photos/hero.png)

# Qui consomme
# le filtre.

Le pilote (où aller samedi) : webapp Streamlit, un clic, un jour. Le club, au capakey.

Open-Meteo n'a pas de clé. Rien de nominatif ne sort.

---

<!-- _class: full -->

![bg brightness:0.38](../../pictures/presentations/photos/physique.png)

# Météo : d'où vient le vent.
# Aspect : vers où descend la pente.

Même 0° = nord. Face au vent ⇔ aspect ≈ direction météo. On décolle contre le flux.

---

<!-- _class: split -->

![bg left:46%](../../pictures/presentations/photos/motivation.png)

# Un GET, deux grains,
# un rayon.

Open-Meteo : horaire + dominant journalier, `forecast_days=3`, vent 10 m, fuseau Bruxelles.

Distance : haversine WGS84. Pas de pyproj. La webapp sert un JSON démo déjà en GPS ; `ST_Transform` reste pour PostGIS.

---

<!-- _class: split -->

![bg left:46%](../../pictures/presentations/photos/physique.png)

# On isole le vent du jour
# du poids climatologique.

L'overlay garde 30 % d'aspect SW (combien de jours un versant « marche »).

Le filtre tranche **ce** flux, à ± 45°, écart circulaire (350° / 10° = 20°).

---

<!-- _class: split -->

![bg left:46%](../../pictures/presentations/photos/hero.png)

# Trois prédicats,
# pas un nouveau score.

Dans le rayon. Face au vent. Déjà retenue au cadastre (suitability ≥ 0,20).

Le titulaire est jeté à nouveau, même s'il a fuité dans le JSON d'entrée.

---

<!-- _class: dark -->

# Périmètre.

Trois jours, un point, un rayon réglable (défaut 30 km), direction seulement.

Pas un briefing (pas de QNH, pas de thermique), pas un seuil de vitesse, pas une table nominative.

---

<!-- _class: split -->

![bg left:46%](../../pictures/presentations/photos/physique.png)

# Dix mètres,
# pas quatre-vingts.

Le décollage se joue à hauteur d'aile. Le vent 80 m raconte la couche au-dessus.

Pas de seuil de vitesse : hors cadrage, jugement pilote.

---

<!-- _class: chart -->

Le terrain reste une fenêtre de pente : 0 hors de 10–42°, plateau à 1 entre 16° et 28°. Le vent n'y entre pas.

![w:920](../../pictures/presentations/score-pente.png)

---

<!-- _class: full -->

![bg brightness:0.38](../../pictures/presentations/photos/physique.png)

# ± 45°, inclus.
# Plat (NaN) : hors jeu.

Pile à 45° : gardé. 46° : jeté. Un versant NE survit à l'overlay et sort dès que le flux est d'ouest.

---

<!-- _class: chart -->

Face au sud-ouest le score d'aspect climatologique vaut 1. Face au nord-est il reste à 0,25 — le filtre quotidien s'en charge.

![w:920](../../pictures/presentations/score-aspect.png)

---

<!-- _class: split -->

![bg left:46%](../../pictures/presentations/photos/motivation.png)

# Robustesse
# sans socket.

72 h et 3 dominants dans un JSON-fixture. `urlopen` injecté. Wrap 0°/360° testé.

Le vrai GET n'est pas dans pytest.

---

<!-- _class: split -->

![bg left:40%](../../pictures/presentations/photos/hero.png)

# Pourquoi pas
# la climatologie seule.

Un azimut annuel cacherait le jour d'est. Un vent temps réel sans horizon ne dit pas « samedi ».

Trois jours, un dominant par jour : assez pour choisir le créneau.

---

<!-- _class: dark -->

# Où ça casse.

Un dominant journalier lisse une bascule de régime.

Haversine sphérique, pas ellipsoïde.

Open-Meteo n'est pas un TAF.

---

<!-- _class: cta -->

![bg brightness:0.30](../../pictures/presentations/photos/cta.png)

# Reproduire.

[Code source](https://github.com/dimiphoton/parapente-selection-sites)

`streamlit run webapp/app.py`

`python -m sites_parapente.cli --forecast 50.22 5.34`

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white) ![PostGIS](https://img.shields.io/badge/PostGIS-spatial-336791?logo=postgresql&logoColor=white) ![Streamlit](https://img.shields.io/badge/Streamlit-webapp-FF4B4B?logo=streamlit&logoColor=white)
