---
marp: true
theme: portfolio
paginate: true
---

<!-- _class: cover -->
<!-- _paginate: false -->

![bg brightness:0.40](../../pictures/presentations/photos/hero.png)

# Où décoller en parapente
# en Ardenne, selon le terrain
# et le vent des trois prochains jours ?

Géospatial · Loisirs outdoor

Ardenne · MNT LiDAR 2021–2022 · parcelle cadastrale

---

<!-- _class: split -->

![bg left:46%](../../pictures/presentations/photos/motivation.png)

# Un week-end venté
# ne rattrape pas
# un mauvais versant.

Forêt, prairie trop plate, ou dos au vent : le trajet ne sert à rien.

**Le terrain décide avant la météo du jour.**

---

<!-- _class: split -->

![bg left:46%](../../pictures/presentations/photos/hero.png)

# Clubs, pilotes,
# communes.

Le club cherche un décollage herbeux. Le pilote autonome, un versant face au vent. La commune, des parcelles identifiables.

**La décision : quelles parcelles valent le détour.**

---

<!-- _class: full -->

![bg brightness:0.38](../../pictures/presentations/photos/physique.png)

# Pour quitter le sol,
# il faut une pente
# d'herbe, face au vent.

Trop plat, on court sans décoller. Trop d'arbres, la voile n'a pas la place. L'eau et le béton sont hors jeu.

---

<!-- _class: split -->

![bg left:46%](../../pictures/presentations/photos/motivation.png)

# On lit un pixel
# de un mètre.

Le LiDAR donne la pente et le versant. WALOUS dit prairie, culture, forêt.

On en fait un score de 0 à 1, pas une moyenne d'avis.

---

<!-- _class: dark -->

# Ce projet, ce n'est pas.

Pas un simulateur de vol, ni une autorisation de décoller.

Pas les noms des propriétaires.

**Un score de terrain en Ardenne, à la parcelle ensuite.**

---

<!-- _class: full -->

![bg brightness:0.38](../../pictures/presentations/photos/physique.png)

# Forêt pentue : zéro.
# Prairie plate : zéro.

Les trois conditions ensemble, ou rien.

---

<!-- _class: chart -->

La pente utile tient dans une fenêtre : trop plat ou trop raide, le score tombe.

![w:980](../../pictures/presentations/score-pente.png)

---

<!-- _class: chart -->

Parmi ce qui reste, la pente pèse la moitié. L'orientation, un tiers. Le type de sol ouvert, le reste.

![w:920](../../pictures/presentations/poids-overlay.png)

---

<!-- _class: split -->

![bg left:40%](../../pictures/presentations/photos/hero.png)

# Ce n'est pas
# un chiffre tiré au sort.

Seuils écrits, veto forêt, versant nord-est gardé pour les jours d'est.

Le vent des trois jours viendra **après**, pas dans ce score.

---

<!-- _class: actions -->

![bg right:38%](../../pictures/presentations/photos/action.png)

# Lundi.

**Pilote** — garder les versants herbeux entre 16° et 28°.

**Club** — traiter le score comme un filtre, pas comme un feu vert légal.

Le vent du jour n'est pas encore dans la carte.

---

<!-- _class: cta -->

![bg brightness:0.30](../../pictures/presentations/photos/cta.png)

# À vous.

[Code source](https://github.com/dimiphoton/parapente-selection-sites)

Webapp géolocalisée : prochaine étape après le cadastre.
