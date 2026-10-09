# FIGARO monetary emission factors

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23157020.svg)](https://doi.org/10.5281/zenodo.23157020)

Spend-based greenhouse gas emission factors for 31 European countries and 62 industries, computed
from Eurostat's FIGARO inter-country input-output tables and the emission accounts Eurostat uses
for its official footprints. Scopes 1, 2 and 3 upstream, in kgCO2e per thousand EUR of output, in
two views: the country of **supply** (where the goods or services are produced) and the country of
**demand** (the mix a country actually buys, domestic and imported), and the demand view converted to the
**purchaser prices** companies actually pay.

This repository holds the full calculation: scripts, input extracts, results and checks.
Maintained by [Ecodex](https://getecodex.com), where the factors are published within the source "Eurostat".

[Version française](README.fr.md)

## What you get

`results/figaro_emission_factors_26ed.csv`: 20,541 rows, one per year, country and NACE Rev. 2
industry (A64 level): 2014 to 2023 complete, 2024 provisional with scopes 1 + 2 only.

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

`results/figaro_demand_emission_factors_26ed.csv`: 18,465 rows, one per year, purchasing country and
product, 2014 to 2023. Same value columns, averaged over every country of origin, plus:

| Column | Meaning |
|---|---|
| `purchases_meur` | intermediate consumption of the product by the industries of the country, million EUR |
| `purchases_share_domestic`, `purchases_share_other_eu27`, `purchases_share_rest_of_world` | where those purchases come from |
| `total_share_domestic`, `total_share_other_eu27`, `total_share_rest_of_world` | place of emission of the total, seen from the purchasing country |

Rows with purchases below 50 million EUR are left out.

`results/figaro_final_demand_emission_factors_26ed.csv`: 17,709 rows, same layout as the demand table,
weighted by the **final** purchases of the country (household, government and NPISH consumption, gross
fixed capital formation; changes in inventories left out) instead of the intermediate consumption of
its industries. `purchases_meur` is then final purchases.

`results/figaro_supply_chain_details_26ed.csv`: 18,834 rows, one per row of the supply table, 2014 to 2023:

| Column | Meaning |
|---|---|
| `share_own_operations`, `share_tier_1`, `share_tier_2`, `share_tier_3_plus` | split of the total by supply-chain layer: the industry itself, its direct suppliers, their suppliers, and beyond |
| `total_with_aviation_rf` | total with the radiative forcing of aviation (direct CO2 of air transport x 1.7), optional |

`results/figaro_purchaser_price_factors_26ed.csv`: 13,495 rows, one per year, purchasing country and
product, 2014 to 2023, for the 26 countries that publish valuation matrices (see Purchaser prices).

| Column | Meaning |
|---|---|
| `total_purchaser_prices_with_margins` | factor of the country of demand per k EUR at purchaser prices, emissions of the trade and transport margins included: the factor to apply to an invoice amount excluding deductible VAT |
| `total_purchaser_prices_rebased` | same emissions as the basic-price factor, divided by the purchaser price (margins carry no emissions) |
| `total_basic_prices` | the factor of the demand table |
| `rebasing_ratio`, `margin_term` | to convert any basic-price factor of the product: `factor x rebasing_ratio + margin_term` |
| `share_basic_value`, `share_trade_transport_margins`, `share_taxes_less_subsidies` | split of the purchaser price paid by the industries of the country |
| `margin_factor`, `margins_transport_share` | factor of the margin services (mix of trade and transport of the country) and the transport part of that mix |
| `valuation_year`, `purchases_pp_meur` | year of the national tables used, and the purchases at purchaser prices that year (million EUR) |

## When to use these factors

A spend-based factor is a fallback: a physical factor (per kg, kWh, km) or supplier-specific data
is always better when the purchase can be described that way. When only an amount is known, the
right database depends on what was bought and where.

### Country of supply or country of demand

The supply factor of a country covers 1 k EUR of output produced in that country. The demand factor
covers 1 k EUR of what the industries of that country buy of the product, from every origin: it is
the average of the supply factors of all origins, weighted by the actual purchases.

Textiles, wearing apparel and leather (C13-15), 2023, kgCO2e per k EUR:

| | Factor | |
|---|---|---|
| France as country of supply | 205 | made in France |
| France as country of demand | 369 | 36% bought in France, 30% in the rest of the EU, 34% outside the EU |
| China as country of supply | 724 | |
| India as country of supply | 1,347 | |

- **Origin of the purchase known**: supply table, country of the supplier (or of the producer, for a
  reseller).
- **Origin unknown**: demand table, country of the purchasing company.
- **Business purchases or final purchases.** The demand table is weighted by what industries buy:
  use it for production inputs and services. For finished goods or equipment bought as such (clothing,
  vehicles, computers, furniture), whose origin mix follows consumer and investment purchases, the final
  demand table is closer. The two are within a few percent for most products (median ratio 1.00 for
  goods, 0.99 for services in 2023) and diverge for some imported finished goods: United Kingdom,
  textiles, 2023, 391 weighted by business purchases, 553 by final purchases.
- Retail trade (G47) is not a substitute: at basic prices it covers the trade margin only (shops,
  their energy and logistics), never the goods sold. A purchase at purchaser prices is the basic value
  of the goods (factor of the product) plus the trade and transport margins (factors of G and H) plus
  taxes: the purchaser-price table does that split for business purchases.

The two views are close for services, mostly bought locally (2023: median gap 3%, two thirds of the
pairs within 10%), and diverge for goods (median gap 11%, 42% within 10%), most of all for imported
ones: textiles, electronics, chemicals, metals, mining products.

### Which spend-based database for which purchase

| Your purchase | First choice | Why |
|---|---|---|
| Services, overheads or undetailed spend with a European supplier | **FIGARO** | Country-specific, recent, traceable to official statistics |
| A European purchase whose country of origin is unknown | **FIGARO**, country of demand | Average of every origin, weighted by what the country actually buys |
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
| **FIGARO** (this repository) | 31 European | 62 industries | 2014-2023, yearly (2024: scopes 1 + 2) | Basic; purchaser for business purchases in 26 countries | Eurostat inter-country tables and emission accounts |
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
- An invoice amount is at purchaser prices: with a basic-price factor it overstates emissions (goods:
  about 9% in median, more than 25% for one row in ten). Use the purchaser-price table, or `rebasing_ratio`
  and `margin_term` with a supply factor when the origin is known. Amounts including deductible VAT
  overstate in any case.
- Do not switch database for one spend category from one year to the next: the switch would show
  up as a change in emissions.

## Method

`figaro_core.py`, about 200 lines:

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

Country of demand, for a purchasing country s and a product p:

```
w(r | s, p)   = share of origin r in the intermediate purchases of p by the industries of s
                (FIGARO flows, domestic and imported)
demand(s, p)  = sum over origins r of w(r | s, p) x m(r, p)        same weights for every scope
```

The weights are business purchases (intermediate consumption), not household final demand. Every
origin enters them, including rows left out of the supply table. `build_factors.py` checks that the
demand factors times the purchases give back the emissions embodied in each country's purchases.

### Final purchases, supply-chain layers, aviation

- **Final purchases.** Same formula as the country of demand with the final purchases of s as weights:
  consumption of households, government and NPISH and gross fixed capital formation (`P3_S13`,
  `P3_S14`, `P3_S15`, `P51G`); changes in inventories (`P5M`) are left out, negative GFCF cells
  (disposals) set to 0. `build_factors.py` checks that the factors times
  the final purchases give back the emissions embodied in them.
- **Supply-chain layers.** `m = f + f A + f A^2 + ...`: the industry's own emissions (f), those of its
  direct suppliers (f A, scope 2 is part of it), of their suppliers (f A^2), and the rest. A process LCA
  that stops after a few tiers misses the last layer (37 to 40% of the total in median): the split shows
  where an input-output factor can complete it (hybrid LCA).
- **Aviation radiative forcing.** Off by default, as in the GHG Protocol and the air emissions accounts.
  `total_with_aviation_rf` multiplies the direct CO2 of air transport (H51) by 1.7, the central value of the
  [UK DESNZ 2026 methodology](https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting)
  (paragraphs 2.10 and 8.39 to 8.43, CO2 only), along the whole chain: `(1.7 - 1) x f_CO2,H51 (I - A)^-1`.
  The multiplier is indicative and uncertain (same source); report it separately, never instead of the
  total.

### Purchaser prices

The factors above are per EUR at basic prices. A company pays the basic value of the product plus the
trade and transport margins of its distributors plus taxes less subsidies on products. Eurostat
publishes, per country and year, the use tables at purchasers' prices and at basic prices and the two
valuation matrices between them, by product and by user. `build_purchaser_prices.py` takes them over the
intermediate consumption of all industries, for a purchasing country s and a product p:

```
PP           = BP + M + T                              national use tables, business purchases
FE_M(s)      = sum over margin services k of w_k x m(s, k)
               w_k = share of k (G45-G47, H49-H53) in the margins of the supply table of s
with margins = (BP x FE_BP + M x FE_M(s) + T x 0) / PP  = FE_BP x BP / PP + M / PP x FE_M(s)
rebased      = FE_BP x BP / PP
```

FE_BP is the factor of the country of demand. Business purchases, not total supply: French textiles in
2022 cost 1.41 times their basic value to the industries that buy them, 1.79 times on average over all
uses, households included (retail margins). Same approach as the US EPA factors with and without margins.

Textiles, wearing apparel and leather (C13-15) bought in France, 2023, kgCO2e per k EUR: 369 at basic
prices, 261 rebased, 295 with margins (valuation matrices of 2022: 71% basic value, 26% margins, 3% taxes).

- The margins matrix gives margins in total. Their split between trade and transport services is the
  one of the supply table of the country, the same for every product (transport is 6% of margins in
  median). Pricing all margins at wholesale trade instead changes the result by less than 2% for 96% of
  rows (validation 5).
- Taxes carry no emissions. They include non-deductible VAT: in France in 2022, the VAT-exempt
  industries (finance, insurance, public administration, education, health) pay taxes of 15% of the
  basic value on the IT services they buy, against 2.6% for all industries. The table averages all
  industries, so it slightly understates the factor for a fully VAT-deductible buyer (+0.4% in median,
  +3% at p90, without the VAT-exempt industries).
- Valuation matrices are compulsory every 5 years only: a year without them takes the nearest year of
  the same country within 5 years (`valuation_year`, 66% of rows use the same year). Germany, Spain,
  Bulgaria, Switzerland and the United Kingdom publish none (or not the margins and taxes): no rows.
- Margin services bought as such (wholesale fees, freight) carry no margin of their own. When the
  margins matrix is missing but the three other tables are published, margins = PP - BP - taxes; cells
  where the four tables disagree by more than 1% are dropped.

### Inputs

| Data | Eurostat source |
|---|---|
| Inter-country input-output table, industry by industry, 64 industries x 50 regions, 2026 edition | FIGARO, [CIRCABC public space](https://ec.europa.eu/eurostat/web/esa-supply-use-input-tables/database) (48 MB per year, downloaded by `fetch_eurostat.py --tables`) |
| Direct GHG and CO2 emissions by country and industry | `env_ac_ghgfp`, `env_ac_co2fp` with `c_dest=WORLD`, `na_item=TOTAL` |
| Checks: official footprints, air emissions accounts, national-accounts output, French symmetric IOT | `env_ac_ghgfp`, `env_ac_ainah_r2`, `nama_10_a64`, `naio_10_cp1700` |
| Purchaser prices: use tables at purchasers' and basic prices, trade and transport margins, taxes less subsidies, margins column of the supply table | `naio_10_cp16`, `naio_10_cp1610`, `naio_10_cp1620`, `naio_10_cp1630`, `naio_10_cp15` |
| Ground truth: electricity prices, emissions and output of public power and heat plants, steel exports | `nrg_pc_205`, `env_air_gge` (CRF 1.A.1.a), `nrg_bal_peh`, Comext `DS-045409` |
| Ground truth: CO2 intensity of crude steel, world | worldsteel, World Steel in Figures [2024](https://worldsteel.org/wp-content/uploads/World-Steel-in-Figures-2024.pdf) and [2025](https://worldsteel.org/wp-content/uploads/World-Steel-in-Figures-2025.pdf) (`data/worldsteel_co2_intensity.csv`) |
| Check: upstream GHG content of French products, table GES.501 | [SDES / Insee](https://www.statistiques.developpement-durable.gouv.fr/emissions-de-gaz-effet-de-serre-et-empreinte-carbone-de-la-france-une-baisse-significative-en-2023) |

Emissions of non-EU countries are the EDGAR-based estimates produced by Eurostat itself
("FIGARO - Greenhouse gas emission estimates", methodological note). No third-party emission
model is added. Albania, Montenegro, North Macedonia and Serbia are merged into the rest of the
world, as in the published emission accounts. Queries and Eurostat update dates of every extract
are logged in `data/SOURCES.csv`.

### Editions

Tables: 2026 edition (June 2026). Emissions: Eurostat release of January 2026, which stops at
2023; **2023 is therefore the latest complete year**. European air emissions accounts do not depend on
the FIGARO edition; the non-EU estimates were allocated by Eurostat with the 2025 edition. Moving
the tables from the 2025 to the 2026 edition changes the 2022-2023 European factors by a median
of +0.3%, with 56% of them within 5% and 9% beyond 20% (national accounts revisions).

### Provisional year 2024

The world emission accounts stop at 2023, so the total and scope 3 upstream cannot be computed
for 2024. Scopes 1 + 2 can: the air emissions accounts of the EU27 and Norway for 2024 were
published in August 2026 (`env_ac_ainah_r2`), and the 2024 table exists. Scope 1 is accounts /
FIGARO output; scope 2 uses the 2024 direct intensity of the electricity, gas and steam suppliers,
with the 2023 intensity for suppliers outside these 28 countries (0.7% of scopes 1 + 2 in median).
The 2024 rows will be replaced by complete ones when Eurostat releases the next emission accounts.

## Checks

Reports in `results/<edition>/validation/`.

1. **Eurostat official footprints.** Applied to FIGARO final demand, the multipliers reproduce the
   footprint Eurostat publishes for each country: with the 2025 edition, the one Eurostat used,
   median ratio 1.0000, 96% of the 46 regions within 1%, largest gap 2.1% (`results/25ed`). The
   2025 edition tables are no longer distributed, so this check cannot be rerun from public files;
   with the 2026 tables the match is no longer exact (35 to 52% of regions within 1%).
2. **Scope 1.** Emissions equal the air emissions accounts for 95 to 98% of rows; the direct
   intensity is within 5% of accounts / national-accounts output for 96 to 100% of rows depending
   on the year, median 1.000.
3. **France against SDES / Insee GES.501**, the values ADEME publishes as monetary ratios:
   - these factors: median ratio 0.82 to 0.88 depending on the year (2019 to 2023);
   - FIGARO import contents combined with the French national input-output table, which
     approximates the method of the SDES: median 0.94 to 0.96, 54 to 79% of industries within 10% (2019 to 2022).

4. **Country of demand.** Against the supply factor of the same country and product: median ratio
   1.04 to 1.05 depending on the year, 10% of pairs below 0.93-0.95, 10% above 1.37-1.45. Highest
   for imported goods (textiles 1.39, mining products 1.59 in 2023).
5. **Purchaser prices.** Basic value + margins + taxes = purchaser price for 97.1% of the cells where
   the four tables are published (the others are dropped). With margins, the purchaser-price factor of
   goods is 0.91 to 0.92 times the basic-price factor in median (10% of rows below 0.79-0.80), 0.98 for
   services; the rebasing alone gives 0.85-0.86 for goods. Coverage by year and the two sensitivities are
   in the report.
6. **Variants.** Final against business purchases: median ratio 1.00-1.01 for goods (10% of pairs above
   1.11-1.14), 0.99 for services. Supply-chain layers in median: own operations 10-11%, tier 1 22-24%,
   tier 2 21-22%, tier 3 and beyond 35-40%. Aviation radiative forcing in 2023: +51% in median on air
   transport, +1% in median on the other industries (business travel), at most +46% (travel agencies).
7. **Ground truth from outside the model**, reported as measured (the model is not tuned to it):
   - **Electricity (D35)** against grid intensity / price, i.e. inventory emissions of public power and
     heat plants (CRF 1.A.1.a) per kWh produced, divided by the non-household electricity price
     excluding taxes, 2021 to 2023 (26 to 27 countries): the direct factor is 0.55 to 0.59 times that
     value in median, the total factor 0.97 to 1.15. D35 output covers more than electricity sold to
     businesses: electricity traded within the industry, sales
     to households at higher prices, gas distribution and steam. A D35 monetary factor is therefore a
     poor proxy for an electricity bill: use a factor per kWh.
   - **Basic metals (C24)** against the worldsteel world CO2 intensity of crude steel (1.91 and 1.92 t
     per t in 2022 and 2023) divided by the unit value of EU steel exports (Comext, HS 72: 1,193 and
     1,005 EUR/t): the C24 total of the 21 EU countries above 1 billion EUR of output is 0.58 and 0.46
     times that value in median (range 539 to 1,661 kgCO2e/kEUR). Expected to be below: C24 also covers
     non-ferrous metals and foundries, and the worldsteel figure is a world average while the route
     and fuel mix of steelmaking differ by country. For steel bought by weight, a factor per tonne is
     better.

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
python build_purchaser_prices.py              # results/26ed/figaro_purchaser_prices_26ed.csv
python validate.py                            # results/26ed/validation/
python build_results.py                       # results/figaro_emission_factors_26ed.csv, figaro_demand_emission_factors_26ed.csv,
                                              # figaro_final_demand_emission_factors_26ed.csv,
                                              # figaro_supply_chain_details_26ed.csv, figaro_purchaser_price_factors_26ed.csv
```

About 5 minutes and 4 GB of memory once the tables are downloaded. Eurostat overwrites its datasets
in place: rerunning `fetch_eurostat.py` later may return revised data; the extracts committed in
`data/` are the ones behind the published results.

## Limits

- 64 industries, average technology of each industry in each country.
- Tables and emission estimates come from two consecutive FIGARO editions (see Editions).
- Small countries and small industries give unstable ratios despite the 50 million EUR threshold.
- Only CO2 against other gases can be separated along the whole chain.
- Scope 2 is location-based and first tier; D35 pools electricity, gas and steam.
- Country of demand: the origin mix is FIGARO's, which under-represents the imported goods of French
  industries (see above), so French demand factors of goods are probably on the low side. The rest of
  the world is one block with one factor per industry. The mix of a given company can differ from
  the average of its country.
- Purchaser prices: national averages over all buying industries, split of margins between trade and
  transport the same for every product, nearest year when the valuation matrices are not annual. The
  margin services are priced with the factors of the purchasing country (they are produced there).

## Licence and attribution

Code: MIT, see `LICENSE`. Results and documentation: CC BY 4.0, see `DATA_LICENSE.md`, which also
lists the attribution owed to Eurostat and SDES / Insee for the inputs.

To cite: see `CITATION.cff`. Archived on Zenodo: all versions https://doi.org/10.5281/zenodo.23157020, one DOI per release listed on that page.
