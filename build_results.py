"""Publishable table of European monetary emission factors, from results/<edition>/figaro_factors_<edition>.csv.

    python build_results.py [edition]        (default 26ed)

Writes results/figaro_emission_factors_<edition>.csv: one row per (year, country, NACE A64 industry),
kgCO2e per thousand EUR of output at basic prices (current prices).

Selection rules
- 31 European countries: EU27, Norway, Switzerland, United Kingdom, Turkey;
- industries T (households as employers, no inputs) and U (no output) are left out;
- rows with an output below 50 million EUR are left out (unstable ratios on tiny industries).
"""
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
EDITION = sys.argv[1] if len(sys.argv) > 1 else "26ed"
MIN_OUTPUT_MEUR = 50.0
EXCLUDED_SECTORS = {"T", "U"}

fac = pd.read_csv(HERE / "results" / EDITION / f"figaro_factors_{EDITION}.csv")
geo = pd.read_csv(HERE / "data" / "countries.csv").set_index("code")
nace = pd.read_csv(HERE / "data" / "nace_a64.csv").set_index("code")
f = fac[fac.geo.isin(geo.index) & (fac.output_meur >= MIN_OUTPUT_MEUR) & (fac.total > 0)
        & ~fac.sector.isin(EXCLUDED_SECTORS)].copy()

s12 = f.scope1 + f.scope2
s12_co2 = f.scope1_co2 + f.scope2_co2
out = pd.DataFrame({
    "year": f.year, "country_code": f.geo, "country": f.geo.map(geo.name_en),
    "nace_code": f.sector, "industry": f.sector.map(nace.name_en),
    "output_meur": f.output_meur.round(1),
    # kgCO2e per thousand EUR
    "total_scopes_1_2_3_upstream": f.total, "scopes_1_2": s12, "scope_3_upstream": f.scope3_upstream,
    "scope_1": f.scope1, "scope_2": f.scope2,
    # CO2-only part of the three perimeters (the rest is CH4, N2O and fluorinated gases)
    "total_co2": f.total_co2, "scopes_1_2_co2": s12_co2, "scope_3_upstream_co2": f.total_co2 - s12_co2,
    # place of emission of the total: producing country / other EU27 countries / rest of the world
    "total_share_domestic": f.total_dom / f.total, "total_share_other_eu27": f.total_eu / f.total,
    "total_share_rest_of_world": 1 - (f.total_dom + f.total_eu) / f.total,
})
value_cols = [c for c in out.columns if c.startswith(("total_s", "scope", "total_co2"))]
out[value_cols] = out[value_cols].clip(lower=0).round(2)
share_cols = [c for c in out.columns if "share" in c]
out[share_cols] = out[share_cols].clip(0, 1).round(3)
assert not out.duplicated(["year", "country_code", "nace_code"]).any()
assert (out.total_co2 <= out.total_scopes_1_2_3_upstream + 0.01).all()
path = HERE / "results" / f"figaro_emission_factors_{EDITION}.csv"
out.sort_values(["year", "country_code", "nace_code"]).to_csv(path, index=False)
print(path.name, len(out), "rows |", out.country_code.nunique(), "countries |", out.nace_code.nunique(),
      "industries |", sorted(out.year.unique()))
