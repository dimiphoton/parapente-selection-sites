---
marp: true
theme: portfolio
paginate: true
---

<!-- _class: cover -->
<!-- _paginate: false -->

![bg brightness:0.40](../../pictures/presentations/photos/hero.png)

# How do we keep parcels that face
# the 3-day forecast wind without
# putting weather inside the overlay?

Geospatial · Outdoor recreation · Python / GeoPandas / PostGIS / Streamlit / FME

Ardennes · Open-Meteo 10 m · ± 45°

---

<!-- _class: split -->

![bg left:46%](../../pictures/presentations/photos/motivation.png)

# The terrain score
# says which slopes exist.
# Not which day they work.

A SW-biased overlay with no daily filter would leave parcels with their back to an easterly.

**The stake: one weekend, one radius, one azimuth.**

---

<!-- _class: split -->

![bg left:46%](../../pictures/presentations/photos/hero.png)

# Who consumes
# the filter.

The pilot (where to go on Saturday): Streamlit app, one click, one day. The club, by capakey.

Open-Meteo needs no key. Nothing nominative leaves the pipe.

---

<!-- _class: full -->

![bg brightness:0.38](../../pictures/presentations/photos/physique.png)

# Weather: where the wind comes from.
# Aspect: where the slope goes down.

Same 0° = north. Facing the wind ⇔ aspect ≈ meteorological direction. Takeoff is into the flow.

---

<!-- _class: split -->

![bg left:46%](../../pictures/presentations/photos/motivation.png)

# One GET, two grains,
# one radius.

Open-Meteo: hourly + daily dominant, `forecast_days=3`, 10 m wind, Brussels timezone.

Distance: WGS84 haversine. No pyproj. The app serves a WGS84 demo JSON; `ST_Transform` stays with PostGIS.

---

<!-- _class: split -->

![bg left:46%](../../pictures/presentations/photos/physique.png)

# Daily wind is isolated
# from the climatological weight.

The overlay still gives aspect 30 % around SW (how often a hillside “works”).

The filter cuts **this** flow, ± 45°, circular delta (350° / 10° = 20°).

---

<!-- _class: split -->

![bg left:46%](../../pictures/presentations/photos/hero.png)

# Three predicates,
# not a new score.

Inside the radius. Facing the wind. Already kept at cadastre (suitability ≥ 0.20).

Owner fields are stripped again, even if they leaked into the input JSON.

---

<!-- _class: dark -->

# Scope.

Three days, one point, an adjustable radius (default 30 km), direction only.

Not a briefing (no QNH, no thermals), not a speed threshold, not a nominative table.

---

<!-- _class: split -->

![bg left:46%](../../pictures/presentations/photos/physique.png)

# Ten metres,
# not eighty.

Takeoff is at wing height. 80 m wind describes the layer above.

No speed cutoff: out of scope, a pilot call.

---

<!-- _class: chart -->

Terrain is still a slope window: 0 outside 10–42°, a plateau at 1 between 16° and 28°. Wind stays out of that score.

![w:920](../../pictures/presentations/score-pente-en.png)

---

<!-- _class: full -->

![bg brightness:0.38](../../pictures/presentations/photos/physique.png)

# ± 45°, inclusive.
# Flat (NaN): out.

Exactly 45°: kept. 46°: dropped. A NE hillside survives the overlay and leaves as soon as the flow is westerly.

---

<!-- _class: chart -->

South-west climatological aspect scores 1. North-east stays at 0.25 — the daily filter takes over.

![w:920](../../pictures/presentations/score-aspect-en.png)

---

<!-- _class: split -->

![bg left:46%](../../pictures/presentations/photos/motivation.png)

# Robustness
# with no socket.

72 hours and 3 dominants in a JSON fixture. Injected `urlopen`. 0°/360° wrap tested.

The live GET is not in pytest.

---

<!-- _class: split -->

![bg left:40%](../../pictures/presentations/photos/hero.png)

# Why not
# climatology alone.

A yearly azimuth would hide the easterly day. Instant wind with no horizon does not say “Saturday”.

Three days, one dominant per day: enough to pick the slot.

---

<!-- _class: dark -->

# Where it breaks.

A daily dominant smooths a regime flip.

Spherical haversine, not ellipsoid.

Open-Meteo is not a TAF.

---

<!-- _class: cta -->

![bg brightness:0.30](../../pictures/presentations/photos/cta.png)

# Reproduce.

[Source code](https://github.com/dimiphoton/parapente-selection-sites)

`streamlit run webapp/app.py`

`python -m sites_parapente.cli --forecast 50.22 5.34`

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white) ![PostGIS](https://img.shields.io/badge/PostGIS-spatial-336791?logo=postgresql&logoColor=white) ![Streamlit](https://img.shields.io/badge/Streamlit-webapp-FF4B4B?logo=streamlit&logoColor=white)
