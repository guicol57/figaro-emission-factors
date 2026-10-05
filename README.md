# FIGARO monetary emission factors

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23157020.svg)](https://doi.org/10.5281/zenodo.23157020)

Spend-based greenhouse gas emission factors for 31 European countries and 62 industries, computed
from Eurostat's FIGARO inter-country input-output tables and the emission accounts Eurostat uses
for its official footprints. Scopes 1, 2 and 3 upstream, in kgCO2e per thousand EUR of output.

This repository holds the full calculation: scripts, input extracts, results and checks.
Maintained by [Ecodex](https://getecodex.com), where the factors are published as the source "FIGARO".

[Version française](README.fr.md)

## What you get

`results/figaro_emission_factors_26ed.csv`: 7,551 rows, one per year (2020 to 2023), country and
NACE Rev. 2 industry (A64 level).

| Column | Meaning |
|---|---|
| `total_scopes_1_2_3_upstream` | cradle-to-gate content of 1 k EUR of output: the factor to apply to a purchase amount |
| `scopes_1_2` | direct emissions of the industry and of its direct electricity, gas and steam suppliers |
| `scope_3_upstream` | rest of the supply chain, domestic and imported |
| `scope_1`, `scope_2` | the two parts of `scopes_1_2` |
| `total_co2`, `scopes_1_2_co2`, `scope_3_upstream_co2` | CO2-only part; the remainder is CH4, N2O and fluorinated gases |
| `total_share_domestic`, `total_share_other_eu27`, `total_share_rest_of_world` | where the emissions of the total occur |
| `output_meur` | output of the industry in FIGARO, million EUR |

Conventions: basic prices (no taxes on products, no trade or transport margins), current euros of
the year, residence principle, intermediate consumption only (capital goods excluded), GWP of the
European air emissions accounts (CH4 = 28, N2O = 265).

Countries: EU27, Norway, Switzerland, United Kingdom, Turkey. Industries T and U and rows with an
output below 50 million EUR are left out.

## When to use these factors

A spend-based factor is a fallback: a physical factor (per kg, kWh, km) or supplier-specific data
is always better when the purchase can be described that way. When only an amount is known, the
right database depends on what was bought and where.

### Which spend-based database for which purchase

| Your purchase | First choice | Why |
|---|---|---|
| Services, overheads or undetailed spend with a European supplier | **FIGARO** | Country-specific, recent, traceable to official statistics |
| You need scopes 1 + 2 separated from scope 3 upstream, or the share emitted outside the EU | **FIGARO** | The only one of these databases giving both splits |
| A specific manufactured, agricultural or chemical product, any country | **CEDA** | 400 sectors: cement, cattle or steel are not diluted in a broad industry |
| Supplier outside Europe (Asia, Americas, Africa, Middle East) | **CEDA** | 149 countries |
| Supplier in the United States | **EPA Supply Chain** | 1,016 commodities, national model |
| Supplier in Canada | **OpenIO-Canada** | 13 provinces and territories, national model |
| Supplier in Japan | **MOE Japan** | National reference |
| France, regulatory GHG reporting | **Base Carbone** monetary ratios | National reference published by ADEME |
| Energy products or waste treatment bought as such | **EXIOBASE** | Products detailed by fuel and by treatment route, data year 2019 |

A national model, when one exists for the supplier's country, is usually the better starting
point; FIGARO and CEDA are the two options that cover many countries with one consistent method.

### How the databases differ

As available in Ecodex in October 2026.

| Database | Countries | Sectors | Years | Price basis | Method in one line |
|---|---|---|---|---|---|
| **FIGARO** (this repository) | 31 European | 62 industries | 2020-2023, yearly | Basic | Eurostat inter-country tables and emission accounts |
| CEDA (Watershed) | 149 | 400 sectors | 2021-2024 | Purchaser | Global model, one emission base year reindexed by year |
| EXIOBASE v3.8.2 | 48 countries and regions | 184 products | 2019 | Basic | Global multi-regional model, academic consortium |
| EPA Supply Chain v1.4 | United States | 1,016 commodities | 2024 USD | Purchaser | USEEIO national model |
| OpenIO-Canada | Canada, 13 provinces and territories | 472 products | 2022 | see source | National model, capital goods included |
| Base Carbone monetary ratios | France | 56 products | 2019-2023 | Basic | FIGARO import contents with Insee national accounts (SDES) |
| MOE Japan | Japan | about 540 items | up to 2020 | see source | National reference |

Three differences explain most of the gaps between two factors for the "same" purchase:

- **Price basis.** Basic prices exclude taxes on products and trade and transport margins;
  purchaser prices include them. The same emissions divided by a larger amount give a lower factor.
- **Sector detail.** With 62 industries, one factor pools cement with glass, or cattle with cereals.
- **Scope of the model.** Some models include capital goods, most do not; years and emission
  inventories differ.

### Rules of thumb for FIGARO

- Good fit: services and undetailed spend in a European country, when a factor traceable to
  official statistics is wanted.
- Poor fit: a specific industrial or agricultural product (see the table above).
- France: the Base Carbone ratios are about 15% higher than these factors, for a documented
  reason (see Checks).
- Purchase amounts including VAT or retail margins overstate emissions with basic-price factors.
- Do not switch database for one spend category from one year to the next: the switch would show
  up as a change in emissions.

## Method

`figaro_core.py`, about 100 lines:

```
x  total output per (country, industry)            million EUR
A  = Z / x        technical coefficients
f  = E / x        direct emission intensity         scope 1
m  = f (I - A)^-1 total upstream intensity          scopes 1 + 2 + 3 upstream
scope 2          = direct emissions of the D35 suppliers (electricity, gas, steam) per unit of
                   their direct sales to the industry, all countries of origin (location-based)
scope 3 upstream = m - scope 1 - scope 2
```

The CO2 part is the same calculation with CO2 emissions alone. The place of emission groups the
rows of `f (I - A)^-1` by emitting country.

### Inputs

| Data | Eurostat source |
|---|---|
| Inter-country input-output table, industry by industry, 64 industries x 50 regions, 2026 edition | FIGARO, [CIRCABC public space](https://ec.europa.eu/eurostat/web/esa-supply-use-input-tables/database) (48 MB per year, downloaded by `fetch_eurostat.py --tables`) |
| Direct GHG and CO2 emissions by country and industry | `env_ac_ghgfp`, `env_ac_co2fp` with `c_dest=WORLD`, `na_item=TOTAL` |
| Checks: official footprints, air emissions accounts, national-accounts output, French symmetric IOT | `env_ac_ghgfp`, `env_ac_ainah_r2`, `nama_10_a64`, `naio_10_cp1700` |
| Check: upstream GHG content of French products, table GES.501 | [SDES / Insee](https://www.statistiques.developpement-durable.gouv.fr/emissions-de-gaz-effet-de-serre-et-empreinte-carbone-de-la-france-une-baisse-significative-en-2023) |

Emissions of non-EU countries are the EDGAR-based estimates produced by Eurostat itself
("FIGARO - Greenhouse gas emission estimates", methodological note). No third-party emission
model is added. Albania, Montenegro, North Macedonia and Serbia are merged into the rest of the
world, as in the published emission accounts. Queries and Eurostat update dates of every extract
are logged in `data/SOURCES.csv`.

### Editions

Tables: 2026 edition (June 2026). Emissions: Eurostat release of January 2026, which stops at
2023; **2023 is therefore the latest year**. European air emissions accounts do not depend on
the FIGARO edition; the non-EU estimates were allocated by Eurostat with the 2025 edition. Moving
the tables from the 2025 to the 2026 edition changes the 2022-2023 European factors by a median
of +0.3%, with 56% of them within 5% and 9% beyond 20% (national accounts revisions).

## Checks

Reports in `results/<edition>/validation/`.

1. **Eurostat official footprints.** Applied to FIGARO final demand, the multipliers reproduce the
   footprint Eurostat publishes for each country: with the 2025 edition, the one Eurostat used,
   median ratio 1.0000, 96% of the 46 regions within 1%, largest gap 2.1% (`results/25ed`). The
   2025 edition tables are no longer distributed, so this check cannot be rerun from public files;
   with the 2026 tables the match is no longer exact (35 to 48% of regions within 1%).
2. **Scope 1.** Emissions equal the air emissions accounts for 95 to 97% of rows; the direct
   intensity is within 5% of accounts / national-accounts output for 96 to 99% of rows, median 1.000.
3. **France against SDES / Insee GES.501**, the values ADEME publishes as monetary ratios:
   - these factors: median ratio 0.82 to 0.87 depending on the year;
   - FIGARO import contents combined with the French national input-output table, which
     approximates the method of the SDES: median 0.94 to 0.96, 70 to 79% of industries within 10%.

### Why France is about 15% below Base Carbone

Direct French emissions are the same on both sides. The SDES replaces the French block of FIGARO
with Insee's national accounts and keeps FIGARO only for the content of imported products.
Imported goods used by French industries are lower in FIGARO than in the national accounts (60 to
80% of the amount depending on the product in 2022), because FIGARO reconciles the asymmetries of
international trade statistics. National tables of that kind exist for about a dozen countries per
year, so the same adjustment cannot be applied consistently across Europe; these factors stay on
FIGARO alone.

A comparison with CEDA and EXIOBASE is in [docs/comparison-ceda-exiobase.md](docs/comparison-ceda-exiobase.md).

## Reproduce

```
pip install -r requirements.txt
python fetch_eurostat.py --tables tables      # Eurostat extracts into data/, FIGARO tables into tables/
python build_factors.py --figaro-dir tables   # results/26ed/ (all 46 regions, not committed)
python validate.py                            # results/26ed/validation/
python build_results.py                       # results/figaro_emission_factors_26ed.csv
```

About 2 minutes and 4 GB of memory once the tables are downloaded. Eurostat overwrites its datasets
in place: rerunning `fetch_eurostat.py` later may return revised data; the extracts committed in
`data/` are the ones behind the published results.

## Limits

- 64 industries, average technology of each industry in each country.
- Tables and emission estimates come from two consecutive FIGARO editions (see Editions).
- Small countries and small industries give unstable ratios despite the 50 million EUR threshold.
- Only CO2 against other gases can be separated along the whole chain.
- Scope 2 is location-based and first tier; D35 pools electricity, gas and steam.

## Licence and attribution

Code: MIT, see `LICENSE`. Results and documentation: CC BY 4.0, see `DATA_LICENSE.md`, which also
lists the attribution owed to Eurostat and SDES / Insee for the inputs.

To cite: see `CITATION.cff`. Archived on Zenodo: all versions https://doi.org/10.5281/zenodo.23157020, version 2026.1 https://doi.org/10.5281/zenodo.23157021.
