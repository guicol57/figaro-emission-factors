# Countries outside Europe

FIGARO is a world model. Its tables cover 50 regions; with Albania, Montenegro, North Macedonia and
Serbia merged into the rest of the world, as in the emission accounts, `build_factors.py` computes
factors for 46: the EU27, 18 other countries and a rest of the world. The published results stop at 31
European countries (EU27, Norway, Switzerland, United Kingdom, Turkey). This note explains why, and
what a check of the other countries shows.

Done on 2026-10-16. In short: **the reason is the licence of the inputs, not missing data.** On
quality, most large economies would hold up about as well as the European countries.

## Why they are not published

Two conditions on the inputs rule out a publication under CC BY-SA 4.0, which allows commercial use:

- **Eurostat.** The [copyright notice](https://ec.europa.eu/eurostat/help/copyright-notice) puts
  Eurostat data under CC BY 4.0, with exceptions that may be reused for non-commercial purposes only.
  One of them is data for countries other than the EU Member States, the EFTA countries and the
  official acceding and candidate countries (the notice gives the United States, Japan and China as
  examples). These data must be removed before any commercial reuse. FIGARO's tables and emission
  estimates for those countries fall under this exception.
- **EDGAR.** The emissions of non-EU countries are Eurostat's EDGAR-based estimates. The
  [EDGAR GHG datasets](https://edgar.jrc.ec.europa.eu/dataset_ghg2025) are under CC BY 4.0, except
  the fossil CO2 component (IEA-EDGAR CO2), which is under CC BY-NC-ND 4.0. Fossil CO2 is most of
  the emissions of the large non-EU economies.

For the countries published here:

- Norway and Switzerland (EFTA) and Turkey (candidate country) are covered by Eurostat's general
  licence.
- The United Kingdom is neither an EU Member State (since 2020), an EFTA country nor a candidate. Its
  status, including for the years when it was a Member State, is being clarified with Eurostat. This
  note will be updated with the answer.

The factors of European countries include, in their scope 3 upstream, the share of emissions that
occurs outside the EU, aggregated over all origins (columns `total_share_rest_of_world`). They are
statistics on European countries, of the same kind as the official footprints that Eurostat
publishes.

The extracts committed in `data/` (`env_ac_ghgfp_*`, `env_ac_co2fp_*`) and the footprint checks in
`results/<edition>/validation/1_footprints_*.csv` contain rows for non-EU countries, kept so the
results can be reproduced and checked. These rows remain under Eurostat's non-commercial condition and
are not covered by the licence of this repository (see `DATA_LICENSE.md`).

### Computing them for non-commercial use

Nothing prevents a non-commercial user from producing the factors of the other regions:
`python build_factors.py --figaro-dir tables` writes all 46 regions to
`results/26ed/figaro_factors_26ed.csv` (not committed). Eurostat's conditions then apply to the
output.

## How they compare with other databases

A check against CEDA 2025, done in the Ecodex database, same method as
[comparison-ceda-exiobase.md](comparison-ceda-exiobase.md): 400 BEA sectors per country mapped to
the 64 NACE industries by the prefix of the BEA code (mapping below), unweighted median of the BEA
sectors of each industry, cradle-to-gate factors in kgCO2e per k EUR, year 2023, rows of at least
50 million EUR. Ratio = FIGARO / CEDA. Only ratios are shown here, not the factors.

The mapping reproduces the earlier European comparison: Germany 0.83 (0.86 in October), Italy 0.87
(0.88), Poland 0.91 (0.93).

| Country | Pairs | Median ratio | Quartiles | Within 25% | Within 50% | Within x2 | Correlation of logs |
|---|---|---|---|---|---|---|---|
| United States | 62 | 0.86 | 0.68 - 1.10 | 50% | 85% | 89% | 0.87 |
| South Korea | 61 | 0.79 | 0.65 - 1.05 | 51% | 84% | 87% | 0.78 |
| Mexico | 62 | 0.98 | 0.83 - 1.28 | 55% | 79% | 84% | 0.83 |
| Canada | 61 | 0.82 | 0.64 - 1.09 | 41% | 75% | 84% | 0.85 |
| Australia | 61 | 0.93 | 0.71 - 1.31 | 38% | 79% | 89% | 0.85 |
| Russia | 62 | 1.12 | 0.86 - 1.40 | 48% | 74% | 85% | 0.90 |
| Japan | 62 | 1.19 | 0.96 - 1.55 | 44% | 66% | 82% | 0.86 |
| China | 62 | 0.77 | 0.53 - 1.09 | 40% | 73% | 79% | 0.80 |
| Argentina | 62 | 1.03 | 0.78 - 1.64 | 44% | 65% | 79% | 0.81 |
| Indonesia | 61 | 1.20 | 0.70 - 2.02 | 25% | 48% | 61% | 0.73 |
| India | 61 | 1.30 | 0.96 - 1.89 | 23% | 54% | 70% | 0.71 |
| South Africa | 61 | 1.34 | 0.97 - 1.92 | 30% | 61% | 77% | 0.81 |
| Brazil | 62 | 1.50 | 1.01 - 2.22 | 32% | 52% | 69% | 0.78 |
| Saudi Arabia | 62 | 0.36 | 0.18 - 0.76 | 13% | 31% | 34% | 0.62 |
| *30 European countries (October)* | *1,830* | *0.90* | *0.66 - 1.19* | *44%* | *76%* | *83%* | *0.83* |

The rest-of-world block is left out: it groups every country FIGARO does not model and has no
counterpart in CEDA.

National check, United States against EPA Supply Chain v1.4 (1,016 NAICS commodities, kgCO2e per
2024 USD, brought to 2023 EUR with a 1.024 deflator and 1.0813 USD per EUR, same prefix mapping):
median ratio 1.14 against the factors without margins (quartiles 0.78 - 1.49, 43% within 25%, 89%
within a factor of 2), 1.06 against the factors with margins, correlation of logarithms 0.88.

### Reading

- **Nine countries agree with CEDA as well as the European ones do**: United States, South Korea,
  Mexico, Canada, Australia, Russia, Japan, China, Argentina. Median ratios between 0.77 and 1.19,
  with the same pattern by industry as in Europe: agriculture and cement higher in FIGARO (a broad
  industry against an unweighted median of CEDA sectors), business services lower.
- **India, Indonesia, South Africa and Brazil** are higher in FIGARO and more dispersed. In Brazil,
  agriculture (x7) and food (x4.8) carry the weight of cattle; research and development (x11) is
  harder to explain.
- **Saudi Arabia** does not agree: FIGARO's services are 7 to 14 times below CEDA (engineering,
  telecommunications, land transport). We could not tell which is closer to reality.
- **Waste management (E37T39)** reaches 17,000 to 26,000 kgCO2e per k EUR in Mexico, Saudi Arabia,
  Indonesia and India: landfill methane over a small monetary output, partly informal.
- **Year to year**, factors move as much as in Europe (median change 8% a year), more in Saudi
  Arabia, Argentina and Russia, where the exchange rate to the euro weighs on factors expressed in
  current euros.

## What to use outside Europe

The guide in the [README](../README.md#which-spend-based-database-for-which-purchase) is unchanged:
for a supplier outside Europe, CEDA (149 countries) or the national model of the supplier's country
(EPA Supply Chain for the United States, OpenIO-Canada, MOE Japan) come first.

## BEA to NACE mapping used

Longest prefix wins. BEA codes not listed (customs duties, special industries) are left out.

A01 111, 112, 115 · A02 113 · A03 114 · B 21 · C10T12 311, 312 · C13T15 313 to 316 · C16 321 ·
C17 322 · C18 323 · C19 324 · C20 325 · C21 3254 · C22 326 · C23 327 · C24 331 · C25 332 · C26 334 ·
C27 335 · C28 333 · C29 3361 to 3363 · C30 3364 to 3366, 3369 · C31_32 337, 339 · C33 8113 ·
D35 2211, 2212 · E36 2213 · E37T39 562 · F 23 · G45 441, 8111 · G46 423, 424, 425 ·
G47 444 to 448, 452, 454, 4B · H49 482, 484, 485, 486 · H50 483 · H51 481 · H52 48A, 493 ·
H53 491, 492 · I 721, 722 · J58 5111, 5112 · J59_60 5121, 5122, 515 · J61 517 ·
J62_63 518, 519, 5415 · K64 52A, 522, 525 · K65 524 · K66 523, 5242 · L 531 · M69_70 5411, 5412, 5416, 55 ·
M71 5413 · M72 5417 · M73 5418 · M74_75 5414, 5419 · N77 532, 533 · N78 5613 · N79 5615 ·
N80T82 561 · O84 GSLGO · P85 611, GSLGE · Q86 621, 622, GSLGH · Q87_88 623, 624 · R90T92 711, 712 ·
R93 713 · S94 813 · S95 8112, 8114 · S96 812.

For EPA (NAICS codes), the same table plus 442, 443, 451, 453 to G47, 487 to H49, 488 to H52 and 521 to
K64.
