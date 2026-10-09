# Data licence and attribution

## Results and documentation

From version 2026.5 onwards, the files in `results/` and the documentation of this repository are
made available by Ecodex under the Creative Commons Attribution-ShareAlike 4.0 International licence
(CC BY-SA 4.0, https://creativecommons.org/licenses/by-sa/4.0/).

Versions 2026.1 to 2026.4 were released under CC BY 4.0 and remain available under that licence.

The code is under the MIT licence, see `LICENSE`.

### Attribution is required

Any use of the factors, whole or in part, modified or not, must credit Ecodex as follows:

> FIGARO monetary emission factors, Ecodex (https://getecodex.com), version X, DOI 10.5281/zenodo.23157020,
> licence CC BY-SA 4.0. Computed from Eurostat data.

Replace X with the version used. The credit goes where the sources of the data are listed in the
medium concerned, for example:

- a report, study or carbon footprint: in the list of sources or the methodology section;
- a software product, platform or API: in the documentation of the data and in the list of sources
  that the end users can consult;
- a dataset or database: in its metadata or documentation.

If the factors were changed (converted, aggregated, recalculated, combined with other data), say so
next to the credit. A changed factor must not be presented as an Ecodex factor, and the use of the
factors must not suggest that Ecodex endorses the user or the use.

### ShareAlike, in short

- Using the factors to compute a footprint, a report or a client deliverable: credit as above.
- Publishing or distributing an adapted version of the factors (modified values, or a database into
  which a substantial part of them is extracted): the adapted version must be shared under CC BY-SA
  4.0 or a compatible licence, with the same credit.

The legal code of the licence prevails over this summary.

### Other licence

To integrate the factors into a product or database without the ShareAlike obligation, they are
available through Ecodex Connect under a commercial licence: https://getecodex.com.

### Disclaimer

The results are computed by Ecodex. They are not produced, endorsed or verified by Eurostat.

## Inputs

- `data/env_ac_*.csv`, `data/env_air_gge_public_power.csv`, `data/nama_10_a64_p1.csv`,
  `data/naio_10_*.csv`, `data/nrg_*.csv`, `data/comext_steel_exports.csv`: extracts of Eurostat
  datasets, source Eurostat, reused under the Eurostat reuse policy
  (https://ec.europa.eu/eurostat/help/copyright-notice, CC BY 4.0). Dataset codes, queries and
  update dates are listed in `data/SOURCES.csv`. Extracts are reformatted to CSV, values unchanged.
- FIGARO inter-country input-output tables: source Eurostat, same policy. They are downloaded by
  `fetch_eurostat.py` and not redistributed here.
- `data/sdes_t_ghg_501_contenu_amont_produits.xlsx`: table GES.501, source SDES / Insee, "Emissions
  de gaz à effet de serre et empreinte carbone de la France", reused under the French Licence
  Ouverte / Open Licence 2.0 (https://www.etalab.gouv.fr/licence-ouverte-open-licence/). File unchanged.
- `data/worldsteel_co2_intensity.csv`: two published figures quoted from worldsteel, "World Steel in
  Figures" 2024 and 2025 (links in the file), used for a check only. They are not covered by the
  licence of this repository.
- `data/nace_a64.csv`, `data/countries.csv`: NACE Rev. 2 labels and country names, compiled by Ecodex.
