---
marp: true
theme: portfolio
paginate: true
---

<!-- _class: cover -->
<!-- _paginate: false -->

![bg brightness:0.40](../../pictures/presentations/photos/hero.png)

# How do we recode slope, aspect
# and WALOUS into a 0–1 score
# without fitting a model?

Geospatial · Outdoor recreation · Python / GeoPandas / PostGIS / Streamlit / FME

Ardennes · LiDAR DEM 2021–2022 · cadastral parcel

---

<!-- _class: split -->

![bg left:46%](../../pictures/presentations/photos/motivation.png)

# Weighted overlay is
# the founding GIS
# exercise.

Without justified weights it is just a pretty map.

**Here a rejected pixel must be explainable in one sentence.**

---

<!-- _class: split -->

![bg left:46%](../../pictures/presentations/photos/hero.png)

# Who consumes
# the raster.

The club, later the webapp, and a recruiter who opens the repo.

This step's deliverable: a 0–1 raster, not yet a capakey list.

---

<!-- _class: full -->

![bg brightness:0.38](../../pictures/presentations/photos/physique.png)

# Horn gives slope.
# Downslope gives aspect.

Takeoff turns a run into lift on grass. Forest blocks it. A flat cell has no aspect.

---

<!-- _class: split -->

![bg left:46%](../../pictures/presentations/photos/motivation.png)

# Three grids,
# one metre, EPSG:3812.

Slope and aspect from the DEM. WALOUS already in Lambert 2008.

We recode and weight. We do not zonal-stat to parcels yet.

---

<!-- _class: split -->

![bg left:46%](../../pictures/presentations/photos/physique.png)

# Terrain is isolated
# from today's wind.

Climatological aspect (SW) weighs 30 %. The 3-day Open-Meteo wind is a filter **afterwards**.

Not both in the same sum.

---

<!-- _class: dark -->

# Scope.

We score suitability at the pixel, Ardennes, one CRS.

We are not a fitted model, not a map of certified sites, and not a nominative table.

---

<!-- _class: chart -->

Usable slope is a window: 0 outside 10–42°, a plateau at 1 between 16° and 28°.

![w:920](../../pictures/presentations/score-pente-en.png)

---

<!-- _class: full -->

![bg brightness:0.38](../../pictures/presentations/photos/physique.png)

# 0.50 slope + 0.30 aspect
# + 0.20 land cover. Else veto.

Forest, water, artificial ground, or slope outside the window: the pixel is 0.

---

<!-- _class: chart -->

South-west aspect scores 1. North-east stays at 0.25 — easterly days do happen.

![w:920](../../pictures/presentations/score-aspect-en.png)

---

<!-- _class: split -->

![bg left:46%](../../pictures/presentations/photos/motivation.png)

# WALOUS is not
# a weight like the others.

Grassland 1, bare soil 0.80, crops 0.55.

Everything else is a veto, not a soft penalty.

---

<!-- _class: split -->

![bg left:40%](../../pictures/presentations/photos/hero.png)

# Robustness
# on a synthetic tile.

Same shape, edge NaNs kept, steep forest at 0, NE still above 0.5.

No LiDAR in the repo: the volume stays off git.

---

<!-- _class: chart -->

Why not a classifier? There is no labelled takeoff sample. An overlay can be read and challenged.

![w:880](../../pictures/presentations/poids-overlay-en.png)

---

<!-- _class: dark -->

# Where it breaks.

No field validation.

A 1 m WALOUS cell is not a takeoff strip.

Climatological SW is not Saturday's wind.

---

<!-- _class: cta -->

![bg brightness:0.30](../../pictures/presentations/photos/cta.png)

# Reproduce.

[Source code](https://github.com/dimiphoton/parapente-selection-sites)

`pytest`

`python -m sites_parapente.cli --overlay`

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white) ![PostGIS](https://img.shields.io/badge/PostGIS-spatial-336791?logo=postgresql&logoColor=white) ![Streamlit](https://img.shields.io/badge/Streamlit-webapp-FF4B4B?logo=streamlit&logoColor=white)
