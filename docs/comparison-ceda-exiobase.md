# Comparison with CEDA and EXIOBASE (outside France)

Done on 2026-10-03 in the Ecodex database, on cradle-to-gate factors in kgCO2e per k EUR, European
countries except France. Ratio = FIGARO / other source. Unlike the rest of this repository, this
comparison cannot be rerun from the files here: it uses the CEDA and EXIOBASE factors as stored in
Ecodex.

## Result

| | CEDA 2025 (year 2023) | EXIOBASE v3.8.2 (2019) |
|---|---|---|
| FIGARO year compared | 2023 | 2020 |
| Country x industry pairs | 1,830 (30 countries, 61 industries) | 410 (10 countries, 41 industries) |
| Median ratio | 0.90 | 1.04 |
| Quartiles of the ratio | 0.66 - 1.19 | 0.75 - 1.40 |
| Within 25% | 44% | 43% |
| Within 50% | 76% | 71% |
| Within a factor of 2 | 83% | 82% |
| Correlation of logarithms | 0.83 | 0.81 |

The three sources rank industries the same way and FIGARO shows no bias in one direction. Row by
row, agreement is moderate: fewer than one pair in two within 25%.

## How the pairs were built

- CEDA: 400 BEA sectors per country, mapped to the 64 NACE industries by the prefix of the BEA
  code, then the **unweighted median** of the BEA sectors of each industry. 49% of the FIGARO
  values fall inside the min-max range of the CEDA sectors of the industry.
- EXIOBASE: 41 products whose label maps to one NACE industry without ambiguity, 10 countries
  (DE, IT, ES, NL, PL, BE, SE, AT, IE, DK).

## Where the gaps come from

1. **Aggregation**, the first factor against CEDA. An unweighted median does not represent a
   heterogeneous industry: agriculture (ratio 2.9, livestock weighs in FIGARO), non-metallic
   minerals (2.05, cement), food (1.6). Homogeneous industries agree: textiles (1.05, 77% within
   25%), plastics (1.06, 87%), construction (1.06, 73%), accommodation and food services (1.04,
   77%), basic metals (1.00), refining (0.99).
2. **Price basis**: CEDA is at purchaser prices, FIGARO and EXIOBASE at basic prices.
3. **Services**: FIGARO is lower than both on business services, finance and IT (ratios 0.45 to
   0.75), the same direction as the gap with Base Carbone for France.
4. **Vintage and model**: CEDA 2025 relies on one emission model (base year 2023, AR6 GWP)
   reindexed by year; EXIOBASE 2019 is compared with FIGARO 2020, a Covid year (air transport and
   accommodation at 1.6 and 2.0).
5. **Countries**: median ratios against CEDA range from 0.70 to 1.19, except Malta (0.41) and
   Turkey (0.59).

## Median ratio by industry, FIGARO / CEDA (share within 25%)

A01 2.89 (0) · A02 0.89 (41) · A03 1.34 (31) · B 0.86 (38) · C10T12 1.61 (17) · C13T15 1.05 (77) ·
C16 1.12 (62) · C17 0.80 (66) · C18 0.66 (30) · C19 0.99 (52) · C20 1.28 (41) · C21 1.15 (41) ·
C22 1.06 (87) · C23 2.05 (7) · C24 1.00 (61) · C25 0.76 (53) · C26 0.90 (69) · C27 0.92 (70) ·
C28 0.81 (63) · C29 0.73 (41) · C30 0.56 (7) · C31_32 1.06 (57) · C33 1.10 (53) · D35 0.90 (47) ·
E36 0.33 (10) · E37T39 0.87 (43) · F 1.06 (73) · G45 1.02 (53) · G46 1.03 (57) · G47 0.83 (57) ·
H49 0.98 (60) · H50 0.57 (27) · H51 1.09 (43) · H52 0.95 (73) · H53 1.22 (43) · I 1.04 (77) ·
J58 0.56 (23) · J59_60 0.63 (27) · J61 0.73 (43) · J62_63 0.52 (13) · K64 0.45 (17) · K65 0.98 (30) ·
K66 0.73 (33) · L 0.76 (33) · M69_70 0.69 (43) · M71 0.71 (43) · M72 0.74 (31) · M73 0.75 (40) ·
M74_75 0.81 (47) · N77 0.85 (37) · N78 0.43 (17) · N79 1.62 (20) · N80T82 0.78 (43) · O84 1.12 (63) ·
P85 0.74 (43) · Q86 0.87 (67) · Q87_88 0.71 (40) · R90T92 0.99 (60) · R93 0.86 (60) · S94 0.87 (43) ·
S95 0.88 (56) · S96 0.98 (57)
