# Data licence and attribution

## Results and documentation

The files in `results/` and the documentation of this repository are made available by Ecodex under
the Creative Commons Attribution 4.0 International licence (CC BY 4.0,
https://creativecommons.org/licenses/by/4.0/).

Suggested attribution: "FIGARO monetary emission factors, Ecodex, computed from Eurostat data
(FIGARO tables, 2026 edition; emission accounts released in January 2026)".

The results are computed by Ecodex. They are not produced, endorsed or verified by Eurostat.

## Inputs

- `data/env_ac_*.csv`, `data/nama_10_a64_p1.csv`, `data/naio_10_cp1700_FR.csv`: extracts of
  Eurostat datasets, source Eurostat, reused under the Eurostat reuse policy
  (https://ec.europa.eu/eurostat/help/copyright-notice, CC BY 4.0). Dataset codes, queries and
  update dates are listed in `data/SOURCES.csv`. Extracts are reformatted to CSV, values unchanged.
- FIGARO inter-country input-output tables: source Eurostat, same policy. They are downloaded by
  `fetch_eurostat.py` and not redistributed here.
- `data/sdes_t_ghg_501_contenu_amont_produits.xlsx`: table GES.501, source SDES / Insee, "Emissions
  de gaz à effet de serre et empreinte carbone de la France", reused under the French Licence
  Ouverte / Open Licence 2.0 (https://www.etalab.gouv.fr/licence-ouverte-open-licence/). File unchanged.
- `data/nace_a64.csv`, `data/countries.csv`: NACE Rev. 2 labels and country names, compiled by Ecodex.
