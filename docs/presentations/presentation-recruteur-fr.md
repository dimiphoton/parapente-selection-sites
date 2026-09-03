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

**La décision : quelles parcelles valent le détour, ce week-end.**

---

<!-- _class: full -->

![bg brightness:0.38](../../pictures/presentations/photos/physique.png)

# On décolle contre le vent,
# sur une pente qui le regarde.

Le vent vient de l'ouest : il faut un versant ouest. Dos au flux, la voile n'avance pas.

---

<!-- _class: split -->

![bg left:46%](../../pictures/presentations/photos/motivation.png)

# Deux lectures,
# pas un mélange.

Le LiDAR et WALOUS notent le terrain, une fois. Open-Meteo dit d'où souffle le vent, trois jours.

On ne met pas la météo dans le score de pente.

---

<!-- _class: dark -->

# Ce projet, ce n'est pas.

Pas un briefing de vol, ni une autorisation de décoller.

Pas les noms des propriétaires.

**Un filtre : parcelle herbeuse, dans un rayon, face au vent prévu.**

---

<!-- _class: split -->

![bg left:40%](../../pictures/presentations/photos/hero.png)

# On nomme la parcelle.
# Pas la personne.

Capakey, commune, nature, score. Le propriétaire reste hors dépôt.

---

<!-- _class: full -->

![bg brightness:0.38](../../pictures/presentations/photos/physique.png)

# Face au vent,
# à quarante-cinq degrés près.

Trois jours de prévision. Un rayon de trente kilomètres, réglable. Pas plus large : on ne retient pas le dos de la colline.

---

<!-- _class: chart -->

La pente utile tient dans une fenêtre : trop plat ou trop raide, le score tombe — avant même de regarder le vent.

![w:980](../../pictures/presentations/score-pente.png)

---

<!-- _class: split -->

![bg left:40%](../../pictures/presentations/photos/hero.png)

# Ce n'est pas
# une flèche inventée.

Open-Meteo, sans clé. Le versant vient du LiDAR. La parcelle a un capakey, pas un nom de famille.

---

<!-- _class: actions -->

![bg right:38%](../../pictures/presentations/photos/action.png)

# Lundi.

**Pilote** — choisir un jour, un rayon, garder les parcelles face au vent.

**Club** — travailler au capakey, jamais au nom du titulaire.

La carte cliquable arrive avec la webapp.

---

<!-- _class: cta -->

![bg brightness:0.30](../../pictures/presentations/photos/cta.png)

# À vous.

[Code source](https://github.com/dimiphoton/parapente-selection-sites)

`python -m sites_parapente.cli --wind`
