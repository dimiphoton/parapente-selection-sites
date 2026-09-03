---
marp: true
theme: portfolio
paginate: true
---

<!-- _class: cover -->
<!-- _paginate: false -->

![bg brightness:0.40](../../pictures/presentations/photos/hero.png)

# Where can you take off
# in the Ardennes, given the terrain
# and the wind over the next three days?

Geospatial · Outdoor recreation

Ardennes · LiDAR DEM 2021–2022 · cadastral parcel

---

<!-- _class: split -->

![bg left:46%](../../pictures/presentations/photos/motivation.png)

# A windy weekend
# will not save
# the wrong hillside.

Forest, a meadow that is too flat, or a slope with its back to the wind: the drive is wasted.

**Terrain comes before today's forecast.**

---

<!-- _class: split -->

![bg left:46%](../../pictures/presentations/photos/hero.png)

# Clubs, pilots,
# municipalities.

The club wants a grassy takeoff. The independent pilot wants a slope that faces the wind. The municipality wants parcels you can name.

**The call: which parcels are worth the trip this weekend.**

---

<!-- _class: full -->

![bg brightness:0.38](../../pictures/presentations/photos/physique.png)

# You take off into the wind,
# on a slope that faces it.

Wind from the west means a west-facing hillside. Back to the flow, the wing does not climb.

---

<!-- _class: split -->

![bg left:46%](../../pictures/presentations/photos/motivation.png)

# Two readings,
# not a blend.

LiDAR and WALOUS score the terrain once. Open-Meteo says where the wind comes from, for three days.

Weather does not go into the slope score.

---

<!-- _class: dark -->

# This project is not.

Not a flight briefing, and not a permit to take off.

Not the names of landowners.

**A filter: grassy parcel, inside a radius, facing the forecast wind.**

---

<!-- _class: split -->

![bg left:40%](../../pictures/presentations/photos/hero.png)

# We name the parcel.
# Not the person.

Capakey, municipality, land nature, score. The owner stays off the repo.

---

<!-- _class: full -->

![bg brightness:0.38](../../pictures/presentations/photos/physique.png)

# Facing the wind,
# within forty-five degrees.

Three days of forecast. A thirty-kilometre radius, adjustable. No wider: the back of the hill is out.

---

<!-- _class: chart -->

Usable slope lives in a window: too flat or too steep, the score drops — before anyone looks at the wind.

![w:980](../../pictures/presentations/score-pente-en.png)

---

<!-- _class: split -->

![bg left:40%](../../pictures/presentations/photos/hero.png)

# This is not
# a made-up arrow.

Open-Meteo, no API key. Aspect comes from LiDAR. The parcel has a capakey, not a family name.

---

<!-- _class: actions -->

![bg right:38%](../../pictures/presentations/photos/action.png)

# Monday.

**Pilot** — click a point, pick a day, read the parcels that face the wind.

**Club** — work with the capakey, never the owner's name.

The map lives in the Streamlit app (`streamlit run webapp/app.py`).

---

<!-- _class: cta -->

![bg brightness:0.30](../../pictures/presentations/photos/cta.png)

# Your turn.

[Source code](https://github.com/dimiphoton/parapente-selection-sites)

`streamlit run webapp/app.py`
