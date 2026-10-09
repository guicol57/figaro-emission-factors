"""Publishable table of European monetary emission factors, from results/<edition>/figaro_factors_<edition>.csv.

    python build_results.py [edition]        (default 26ed)

Writes results/figaro_emission_factors_<edition>.csv: one row per (year, country, NACE A64 industry),
kgCO2e per thousand EUR of output at basic prices (current prices).

Selection rules
- 31 European countries: EU27, Norway, Switzerland, United Kingdom, Turkey;
- industries T (households as employers, no inputs) and U (no output) are left out;
- rows with an output below 50 million EUR are left out (unstable ratios on tiny industries).

The last year is provisional: scopes 1 + 2 only (total and scope 3 upstream are empty), for the
countries whose air emissions accounts are already published.

Also writes, complete years only:
- results/figaro_demand_emission_factors_<edition>.csv: the factors of the country of demand, weighted by
  business purchases, one row per (year, purchasing country, product);
- results/figaro_final_demand_emission_factors_<edition>.csv: the same, weighted by final purchases;
- results/figaro_supply_chain_details_<edition>.csv: supply-chain layers and aviation radiative forcing;
- results/figaro_purchaser_price_factors_<edition>.csv: the demand factors at purchaser prices.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
EDITION = sys.argv[1] if len(sys.argv) > 1 else "26ed"
MIN_OUTPUT_MEUR = 50.0
EXCLUDED_SECTORS = {"T", "U"}

fac = pd.read_csv(HERE / "results" / EDITION / f"figaro_factors_{EDITION}.csv")
geo = pd.read_csv(HERE / "data" / "countries.csv").set_index("code")
nace = pd.read_csv(HERE / "data" / "nace_a64.csv").set_index("code")
f = fac[fac.geo.isin(geo.index) & (fac.output_meur >= MIN_OUTPUT_MEUR) & ((fac.total > 0) | fac.total.isna())
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
full = out.total_scopes_1_2_3_upstream.notna()
assert (out.total_co2[full] <= out.total_scopes_1_2_3_upstream[full] + 0.01).all()
assert (out.scopes_1_2 > 0).all()
path = HERE / "results" / f"figaro_emission_factors_{EDITION}.csv"
out.sort_values(["year", "country_code", "nace_code"]).to_csv(path, index=False)
print(path.name, len(out), "rows |", out.country_code.nunique(), "countries |", out.nace_code.nunique(),
      "industries |", sorted(out.year.unique()))

# ---------------------------------------------------------------- country of demand
# Same selection rules, the 50 million EUR threshold applying to the purchases of the country.
# Every origin enters the weights, including the rows left out of the table above.
def demand_table(kind: str) -> pd.DataFrame:
    """kind = "demand" (intermediate consumption of the industries) or "final_demand" (consumption and
    gross fixed capital formation)."""
    dem = pd.read_csv(HERE / "results" / EDITION / f"figaro_{kind}_factors_{EDITION}.csv")
    d = dem[dem.geo.isin(geo.index) & (dem.purchases_meur >= MIN_OUTPUT_MEUR) & (dem.total > 0)
            & ~dem.sector.isin(EXCLUDED_SECTORS)].copy()
    d_s12, d_s12_co2 = d.scope1 + d.scope2, d.scope1_co2 + d.scope2_co2
    dout = pd.DataFrame({
        "year": d.year, "country_code": d.geo, "country": d.geo.map(geo.name_en),
        "nace_code": d.sector, "product": d.sector.map(nace.name_en),
        # purchases of the product by the country (intermediate or final), and where they come from
        "purchases_meur": d.purchases_meur.round(1),
        "purchases_share_domestic": d.purchases_share_domestic,
        "purchases_share_other_eu27": d.purchases_share_other_eu27,
        "purchases_share_rest_of_world": 1 - d.purchases_share_domestic - d.purchases_share_other_eu27,
        # kgCO2e per thousand EUR, purchase-weighted average of the supply factors of every origin
        "total_scopes_1_2_3_upstream": d.total, "scopes_1_2": d_s12, "scope_3_upstream": d.scope3_upstream,
        "scope_1": d.scope1, "scope_2": d.scope2,
        "total_co2": d.total_co2, "scopes_1_2_co2": d_s12_co2, "scope_3_upstream_co2": d.total_co2 - d_s12_co2,
        # place of emission of the total, seen from the purchasing country
        "total_share_domestic": d.total_dom / d.total, "total_share_other_eu27": d.total_eu / d.total,
        "total_share_rest_of_world": 1 - (d.total_dom + d.total_eu) / d.total,
    })
    value_cols = [c for c in dout.columns if c.startswith(("total_s", "scope", "total_co2"))]
    dout[value_cols] = dout[value_cols].clip(lower=0).round(2)
    share_cols = [c for c in dout.columns if "share" in c]
    dout[share_cols] = dout[share_cols].clip(0, 1).round(3)
    assert not dout.duplicated(["year", "country_code", "nace_code"]).any()
    assert (dout.total_co2 <= dout.total_scopes_1_2_3_upstream + 0.01).all()
    name = {"demand": "demand", "final_demand": "final_demand"}[kind]
    path = HERE / "results" / f"figaro_{name}_emission_factors_{EDITION}.csv"
    dout.sort_values(["year", "country_code", "nace_code"]).to_csv(path, index=False)
    print(path.name, len(dout), "rows |", dout.country_code.nunique(), "countries |", dout.nace_code.nunique(),
          "products |", sorted(dout.year.unique()))
    return dout


dout = demand_table("demand")
demand_table("final_demand")

# ---------------------------------------------------------------- supply chain details
# Rows of the supply table, complete years: supply-chain layers of the total (for hybrid LCA and
# truncation checks) and the total with the radiative forcing of aviation (optional, default without).
full_rows = f[f.total.notna()]
det = pd.DataFrame({
    "year": full_rows.year, "country_code": full_rows.geo, "nace_code": full_rows.sector,
    "total_scopes_1_2_3_upstream": full_rows.total.round(2),
    "share_own_operations": full_rows.tier0 / full_rows.total, "share_tier_1": full_rows.tier1 / full_rows.total,
    "share_tier_2": full_rows.tier2 / full_rows.total, "share_tier_3_plus": full_rows.tier3_plus / full_rows.total,
    # kgCO2e per thousand EUR, direct CO2 of air transport (H51) x 1.7 along the whole chain
    "total_with_aviation_rf": (full_rows.total + full_rows.aviation_rf_extra).round(2),
})
det[[c for c in det.columns if c.startswith("share")]] = det[[c for c in det.columns if c.startswith("share")]].round(4)
assert np.allclose(det.filter(like="share").sum(axis=1), 1, atol=1e-3)
assert (det.total_with_aviation_rf >= det.total_scopes_1_2_3_upstream).all()
path = HERE / "results" / f"figaro_supply_chain_details_{EDITION}.csv"
det.sort_values(["year", "country_code", "nace_code"]).to_csv(path, index=False)
print(path.name, len(det), "rows |", sorted(det.year.unique()))

# ---------------------------------------------------------------- purchaser prices
# Rows of the country-of-demand table above whose purchasing country publishes valuation matrices (within
# 5 years), see build_purchaser_prices.py. Purchases at purchaser prices above 50 million EUR as well.
pp = pd.read_csv(HERE / "results" / EDITION / f"figaro_purchaser_prices_{EDITION}.csv")
pp = pp.merge(dout[["year", "country_code", "nace_code"]], left_on=["year", "geo", "sector"],
              right_on=["year", "country_code", "nace_code"])
pp = pp[pp.pp_meur >= MIN_OUTPUT_MEUR]
pout = pd.DataFrame({
    "year": pp.year, "country_code": pp.geo, "country": pp.geo.map(geo.name_en),
    "nace_code": pp.sector, "product": pp.sector.map(nace.name_en),
    # national use tables: intermediate consumption of all industries
    "valuation_year": pp.valuation_year, "purchases_pp_meur": pp.pp_meur.round(1),
    "share_basic_value": pp.share_basic, "share_trade_transport_margins": pp.share_margins,
    "share_taxes_less_subsidies": pp.share_taxes, "margins_transport_share": pp.margin_mix_transport,
    # FE_PP = FE_BP x rebasing_ratio + margin_term (any basic-price factor of the product: demand, or supply of the origin)
    "rebasing_ratio": pp.rebasing_ratio, "margin_factor": pp.margin_factor, "margin_term": pp.margin_term,
    # kgCO2e per thousand EUR, country of demand, total scopes 1-3 upstream
    "total_basic_prices": pp.demand_total, "total_purchaser_prices_rebased": pp.demand_total_pp_rebased,
    "total_purchaser_prices_with_margins": pp.demand_total_pp_with_margins,
})
pout[["share_basic_value", "share_trade_transport_margins", "share_taxes_less_subsidies", "margins_transport_share",
      "rebasing_ratio"]] = pout[["share_basic_value", "share_trade_transport_margins", "share_taxes_less_subsidies",
                                 "margins_transport_share", "rebasing_ratio"]].round(4)
value_cols = ["margin_factor", "margin_term", "total_basic_prices", "total_purchaser_prices_rebased",
              "total_purchaser_prices_with_margins"]
pout[value_cols] = pout[value_cols].round(2)
assert not pout.duplicated(["year", "country_code", "nace_code"]).any()
path = HERE / "results" / f"figaro_purchaser_price_factors_{EDITION}.csv"
pout.sort_values(["year", "country_code", "nace_code"]).to_csv(path, index=False)
print(path.name, len(pout), "rows |", pout.country_code.nunique(), "countries |", sorted(pout.year.unique()))
