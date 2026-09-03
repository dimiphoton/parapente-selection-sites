-- Schéma PostGIS du projet parapente (Ardenne, Lambert 2008).
-- Source de vérité : ce fichier. L'ETL Python (intérim) ou FME plus
-- tard chargent rasters et parcelles.
--
-- Pas de nom de propriétaire ici (RGPD). Identifiant public = capakey.

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_raster;

CREATE SCHEMA IF NOT EXISTS parapente;

COMMENT ON SCHEMA parapente IS
  'Sites de décollage Ardenne. CRS unique EPSG:3812. Pas de données nominatives.';

-- ---------------------------------------------------------------------------
-- Métadonnées de couche (titre, résumé, emprise, CRS, date)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS parapente.layer_meta (
    layer_name  text PRIMARY KEY,
    title       text NOT NULL,
    summary     text NOT NULL,
    crs_epsg    integer NOT NULL DEFAULT 3812
                CHECK (crs_epsg = 3812),
    captured_on date,
    bbox        geometry(Polygon, 3812)
);

COMMENT ON TABLE parapente.layer_meta IS
  'Métadonnées minimales des couches produites (pas de PII).';

-- ---------------------------------------------------------------------------
-- Rasters d'entrée / dérivés (tuiles). Overlay Python, puis raster2pgsql.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS parapente.pente (
    rid  integer PRIMARY KEY,
    rast raster
);

CREATE TABLE IF NOT EXISTS parapente.aspect (
    rid  integer PRIMARY KEY,
    rast raster
);

CREATE TABLE IF NOT EXISTS parapente.occupation (
    rid  integer PRIMARY KEY,
    rast raster
);

CREATE TABLE IF NOT EXISTS parapente.suitability (
    rid  integer PRIMARY KEY,
    rast raster
);

COMMENT ON TABLE parapente.pente IS
  'Pente en degrés (Horn 1981), raster tuilé, SRID 3812.';
COMMENT ON TABLE parapente.aspect IS
  'Aspect en degrés depuis le nord (aval), raster tuilé, SRID 3812.';
COMMENT ON TABLE parapente.occupation IS
  'Codes WALOUS 2023 (1 m), raster tuilé, SRID 3812.';
COMMENT ON TABLE parapente.suitability IS
  'Overlay pondéré 0–1 (pente 50 %, aspect 30 %, sol 20 %), SRID 3812.';

CREATE INDEX IF NOT EXISTS pente_rast_gist
    ON parapente.pente USING GIST (ST_ConvexHull(rast));
CREATE INDEX IF NOT EXISTS aspect_rast_gist
    ON parapente.aspect USING GIST (ST_ConvexHull(rast));
CREATE INDEX IF NOT EXISTS occupation_rast_gist
    ON parapente.occupation USING GIST (ST_ConvexHull(rast));
CREATE INDEX IF NOT EXISTS suitability_rast_gist
    ON parapente.suitability USING GIST (ST_ConvexHull(rast));

-- ---------------------------------------------------------------------------
-- Parcelles cadastrales (plan CADGIS, sans propriétaire)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS parapente.parcelle (
    capakey       text PRIMARY KEY,
    commune       text NOT NULL,
    province      text NOT NULL
                  CHECK (province IN ('Namur', 'Luxembourg', 'Liège')),
    nature        text,
    superficie_m2 numeric,
    geom          geometry(MultiPolygon, 3812) NOT NULL
);

COMMENT ON TABLE parapente.parcelle IS
  'Plan parcellaire CADGIS : capakey, commune, nature, superficie. Pas de titulaire.';
COMMENT ON COLUMN parapente.parcelle.capakey IS
  'Identifiant cadastral officiel (ex. 21683D0265/02R020).';
COMMENT ON COLUMN parapente.parcelle.nature IS
  'Nature cadastrale du bien (pré, bois…), pas l''identité du propriétaire.';

CREATE INDEX IF NOT EXISTS parcelle_geom_gist
    ON parapente.parcelle USING GIST (geom);
CREATE INDEX IF NOT EXISTS parcelle_commune_idx
    ON parapente.parcelle (commune);

-- ---------------------------------------------------------------------------
-- Score d'overlay à la parcelle (rempli après l'overlay pondéré)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS parapente.score (
    capakey          text PRIMARY KEY
                     REFERENCES parapente.parcelle (capakey),
    slope_p50_deg    double precision,
    aspect_p50_deg   double precision,
    walous_majority  integer,
    landcover_open   boolean,
    suitability      double precision,
    geom             geometry(MultiPolygon, 3812) NOT NULL
);

COMMENT ON TABLE parapente.score IS
  'Zonal stats + score de suitability. geom recopié pour la carte (pas de jointure propriétaire).';

CREATE INDEX IF NOT EXISTS score_geom_gist
    ON parapente.score USING GIST (geom);
CREATE INDEX IF NOT EXISTS score_suitability_idx
    ON parapente.score (suitability DESC NULLS LAST);

-- Vue d'export public : rien de nominatif.
CREATE OR REPLACE VIEW parapente.v_parcelle_publique AS
SELECT
    s.capakey,
    p.commune,
    p.province,
    p.nature,
    p.superficie_m2,
    s.slope_p50_deg,
    s.aspect_p50_deg,
    s.walous_majority,
    s.landcover_open,
    s.suitability,
    s.geom
FROM parapente.score AS s
JOIN parapente.parcelle AS p ON p.capakey = s.capakey;

COMMENT ON VIEW parapente.v_parcelle_publique IS
  'Export CSV/GeoJSON / webapp. Aucune colonne nominative.';
