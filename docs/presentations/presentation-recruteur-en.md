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

**The call: which parcels are worth the trip.**

---

<!-- _class: full -->

![bg brightness:0.38](../../pictures/presentations/photos/physique.png)

# To leave the ground
# you need a grass slope
# facing the wind.

Too flat, you run and never lift. Too many trees, the wing has no room. Water and concrete are out.

---

<!-- _class: split -->

![bg left:46%](../../pictures/presentations/photos/motivation.png)

# We read a
# one-metre pixel.

LiDAR gives slope and aspect. WALOUS says grassland, crops, or forest.

That becomes a score from 0 to 1 — not an average of opinions.

---

<!-- _class: dark -->

# This project is not.

Not a flight simulator, and not a permit to take off.

Not the names of landowners.

**A terrain score in the Ardennes, then a parcel list.**

---

<!-- _class: full -->

![bg brightness:0.38](../../pictures/presentations/photos/physique.png)

# Steep forest: zero.
# Flat meadow: zero.

All three conditions, or none.

---

<!-- _class: chart -->

Usable slope lives in a window: too flat or too steep, the score drops.

![w:980](../../pictures/presentations/score-pente-en.png)

---

<!-- _class: chart -->

Of what remains, slope takes half the weight. Aspect takes a third. Open-soil type takes the rest.

![w:920](../../pictures/presentations/poids-overlay-en.png)

---

<!-- _class: split -->

![bg left:40%](../../pictures/presentations/photos/hero.png)

# This is not
# a number pulled from a hat.

Written thresholds, a forest veto, north-east slopes kept for easterly days.

The three-day wind comes **later**, not inside this score.

---

<!-- _class: actions -->

![bg right:38%](../../pictures/presentations/photos/action.png)

# Monday.

**Pilot** — keep grassy slopes between 16° and 28°.

**Club** — treat the score as a filter, not a legal green light.

Today's wind is not on the map yet.

---

<!-- _class: cta -->

![bg brightness:0.30](../../pictures/presentations/photos/cta.png)

# Your turn.

[Source code](https://github.com/dimiphoton/parapente-selection-sites)

Location-aware webapp: after the cadastre join.
