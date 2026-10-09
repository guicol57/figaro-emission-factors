"""Checks of the FIGARO factors. Writes results/<edition>/validation/.

    python validate.py [edition]      (after build_factors.py, default 26ed)

 1. Eurostat official footprints: our multipliers applied to FIGARO final demand must reproduce the
    GHG footprint by country published by Eurostat (env_ac_ghgfp) - checks the Leontief model itself.
 2. Scope 1: direct intensity must equal air emissions accounts / national-accounts output
    (env_ac_ainah_r2 / nama_10_a64, i.e. Eurostat's env_ac_aeint_r2 indicator).
 3. France, scopes 1-3 upstream: comparison with SDES/Insee table GES.501 (the values published as
    monetary ratios in ADEME Base Carbone), (a) pure FIGARO, (b) FIGARO import contents combined with
    the French national symmetric IOT, which approximates the 'simplified SNAC' method of the SDES.
 4. Country of demand: how far the demand factors move from the supply factors of the same country.
 5. Purchaser prices: coverage of the valuation matrices, accounting identity, size of the price wedge, and
    the sensitivity to the two approximations (margin services mix, VAT of exempt buyers).
 6. Variants: country of demand weighted by final purchases, supply-chain layers, aviation radiative forcing.
 7. Ground truth from outside the model: D35 against grid intensity / electricity price, C24 against steel
    intensity / steel price. Reported as measured, the model is not tuned to them.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from figaro_core import EU27, GEO_MAP, NACE_MAP

HERE = Path(__file__).parent
DATA = HERE / "data"
sys.stdout.reconfigure(encoding="utf-8")
SIOT_CODES = {"C10-12": "C10T12", "C13-15": "C13T15", "D": "D35", "E37-39": "E37T39", "N80-82": "N80T82",
              "R90-92": "R90T92", "O": "O84", "P": "P85", "L68A": "L", "L68B": "L"}

EDITION = sys.argv[1] if len(sys.argv) > 1 else "26ed"
OUT = HERE / "results" / EDITION
VAL = OUT / "validation"
VAL.mkdir(exist_ok=True)
fac = pd.read_csv(OUT / f"figaro_factors_{EDITION}.csv").set_index(["year", "geo", "sector"])
provisional = set(fac[fac.total.isna()].index.get_level_values("year"))   # scopes 1 + 2 only
years = sorted(set(fac.index.get_level_values("year")) - provisional)
report = [f"# FIGARO factors ({EDITION}) - validation report", ""]


def share(q, tol):
    return f"{(abs(q - 1) <= tol).mean():.0%}"


def eurostat(name):
    df = pd.read_csv(DATA / f"{name}.csv")
    geo_col = "geo" if "geo" in df else "c_dest"
    df["geo"] = df[geo_col].replace(GEO_MAP)
    if "nace_r2" in df:
        df["sector"] = df.nace_r2.replace(NACE_MAP)
        return df.groupby(["time", "geo", "sector"]).value.first()
    return df.groupby(["time", "geo"]).value.first()


# ---------------------------------------------------------------- 1. official footprints
report += ["## 1. Eurostat official footprints by country of final use", "",
           "| year | countries | median ratio | max abs gap | within 1% |", "|---|---|---|---|---|"]
official = eurostat("env_ac_ghgfp_footprint_by_dest")
for y in years:
    fd = pd.read_csv(OUT / f"final_demand_{y}.csv", index_col=[0, 1])
    mine = fd.mul(fac.loc[y].total.reindex(fd.index) / 1000.0, axis=0).sum()
    c = pd.DataFrame({"eurostat_kt": official.loc[y], "recomputed_kt": mine}).dropna()
    c["ratio"] = c.recomputed_kt / c.eurostat_kt
    c.to_csv(VAL / f"1_footprints_{y}.csv")
    report.append(f"| {y} | {len(c)} | {c.ratio.median():.4f} | {abs(c.ratio - 1).max():.2%} | {share(c.ratio, .01)} |")

# ---------------------------------------------------------------- 2. scope 1
report += ["", "## 2. Scope 1 vs air emissions accounts / national-accounts output", "",
           "Sectors with output above 50 MEUR, countries reporting AEA to Eurostat.", "",
           "| year | n | countries | emissions equal (1%) | output equal (5%) | intensity median ratio | within 5% | within 10% | within 5%, output-weighted |",
           "|---|---|---|---|---|---|---|---|---|"]
aea, p1 = eurostat("env_ac_ainah_r2_ghg"), eurostat("nama_10_a64_p1")
for y in years:
    f = fac.loc[y]
    c = pd.DataFrame({"e_figaro": f.emissions_kt, "e_aea": aea.loc[y], "x_figaro": f.output_meur, "x_nama": p1.loc[y],
                      "s1_figaro": f.scope1}).dropna()
    c = c[(c.e_aea > 0) & (c.x_figaro > 50) & (c.x_nama > 0)]
    c["s1_eurostat"] = c.e_aea / c.x_nama * 1000.0
    c["ratio"] = c.s1_figaro / c.s1_eurostat
    c.to_csv(VAL / f"2_scope1_{y}.csv")
    w = c.x_figaro[abs(c.ratio - 1) <= .05].sum() / c.x_figaro.sum()
    report.append(f"| {y} | {len(c)} | {c.index.get_level_values(0).nunique()} | {share(c.e_figaro / c.e_aea, .01)} | "
                  f"{share(c.x_figaro / c.x_nama, .05)} | {c.ratio.median():.3f} | {share(c.ratio, .05)} | {share(c.ratio, .10)} | {w:.0%} |")

# ---------------------------------------------------------------- 3. France vs SDES GES.501
report += ["", "## 3. France, total upstream content vs SDES/Insee GES.501 (= ADEME Base Carbone monetary ratios)", "",
           "| year | variant | n | median ratio | within 5% | within 10% | within 20% |", "|---|---|---|---|---|---|---|"]
sdes = pd.read_excel(DATA / "sdes_t_ghg_501_contenu_amont_produits.xlsx", sheet_name="Serie_longue", header=3)
sdes = sdes.dropna(subset=["final_product"]).set_index("final_product")
sdes.columns = [str(c) for c in sdes.columns]
siot = pd.read_csv(DATA / "naio_10_cp1700_FR.csv")
siot["r"] = siot.prd_ava.str.replace("CPA_", "").replace(SIOT_CODES)
siot["c"] = siot.prd_use.str.replace("CPA_", "").replace(SIOT_CODES)
for y in years:
    if str(y) not in sdes.columns:      # GES.501 starts in 2019
        continue
    f = fac.loc[y]
    fr = f.loc["FR"]
    secs = list(fr.index)
    t = pd.DataFrame({"sdes": sdes[str(y)].reindex(secs) * 1000.0, "figaro": fr.total, "scope1": fr.scope1})
    n = siot[siot.time == y]
    if len(n):
        dom = n[n.stk_flow == "DOM"].groupby(["r", "c"]).value.sum().unstack().reindex(index=secs).fillna(0.0)
        imp = n[n.stk_flow == "IMP"].groupby(["r", "c"]).value.sum().unstack().reindex(index=secs).fillna(0.0)
        x = dom["TU"].to_numpy()
        inv = np.divide(1.0, x, out=np.zeros_like(x), where=x > 0)
        a_dom = dom.reindex(columns=secs).fillna(0).to_numpy() * inv
        a_imp = imp.reindex(columns=secs).fillna(0).to_numpy() * inv
        direct = fr.emissions_kt.to_numpy() * inv * 1000.0
        mix = pd.read_csv(OUT / f"import_mix_FR_{y}.csv", index_col=[0, 1]).meur
        content = f.total.reindex(mix.index)
        c_imp = ((mix * content).groupby(level="sector").sum() / mix.groupby(level="sector").sum()).reindex(secs).fillna(0).to_numpy()
        t["snac_approx"] = (direct + c_imp @ a_imp) @ np.linalg.inv(np.eye(len(secs)) - a_dom)
        t["imports_ci_national_meur"] = imp.reindex(columns=secs).fillna(0).sum(axis=0).to_numpy()
    t = t[(t.sdes > 0) & (t.figaro > 0)]
    for col, label in (("figaro", "pure FIGARO"), ("snac_approx", "FIGARO imports + French national IOT (SNAC approx.)")):
        if col in t:
            q = t[col] / t.sdes
            t[f"ratio_{col}"] = q
            report.append(f"| {y} | {label} | {len(q)} | {q.median():.3f} | {share(q, .05)} | {share(q, .10)} | {share(q, .20)} |")
    t.to_csv(VAL / f"3_france_sdes_{y}.csv")

# ---------------------------------------------------------------- 4. country of demand
# The weighting identity (demand factors x purchases = emissions embodied in each region's intermediate
# purchases) is asserted in build_factors.py; here, how far the demand view moves from the supply view.
report += ["", "## 4. Country of demand vs country of supply (31 published countries, purchases above 50 MEUR)", "",
           "Ratio = demand factor / supply factor of the same country and product, total scopes 1-3 upstream.", "",
           "| year | n | median ratio | p10 | p90 | within 10% | median domestic share of purchases |",
           "|---|---|---|---|---|---|---|"]
dem = pd.read_csv(OUT / f"figaro_demand_factors_{EDITION}.csv").set_index(["year", "geo", "sector"])
published = set(pd.read_csv(DATA / "countries.csv").code)
for y in years:
    d = dem.loc[y]
    d = d[d.index.get_level_values("geo").isin(published) & (d.purchases_meur >= 50) & (d.total > 0)]
    s = fac.loc[y].total.reindex(d.index)
    ok = (s > 0) & (fac.loc[y].output_meur.reindex(d.index) >= 50)
    q = (d.total / s)[ok]
    pd.DataFrame({"demand": d.total, "supply": s, "ratio": d.total / s,
                  "purchases_share_domestic": d.purchases_share_domestic}).to_csv(VAL / f"4_demand_vs_supply_{y}.csv")
    report.append(f"| {y} | {len(q)} | {q.median():.3f} | {q.quantile(.1):.2f} | {q.quantile(.9):.2f} | "
                  f"{share(q, .10)} | {d.purchases_share_domestic.median():.0%} |")

# ---------------------------------------------------------------- 5. purchaser prices
import build_purchaser_prices as bpp

pp = pd.read_csv(OUT / f"figaro_purchaser_prices_{EDITION}.csv")
report += ["", "## 5. Purchaser prices (business purchases, national use tables)", "",
           "Coverage of the 31 published countries by year: valuation matrices of the same year / nearest year "
           f"within {bpp.MAX_CARRY} years / none.", "",
           "| year | same year | carried | none | countries without valuation data |", "|---|---|---|---|---|"]
for y in years:
    vy = pp[pp.year == y].groupby("geo").valuation_year.first()
    vy = vy[vy.index.isin(published)]
    report.append(f"| {y} | {(vy == y).sum()} | {(vy != y).sum()} | {len(published) - len(vy)} | "
                  f"{', '.join(sorted(published - set(vy.index)))} |")
raw = bpp.components()
raw = raw.dropna(subset=["pp", "bp", "t", "m"])
raw = raw[~raw.index.get_level_values("sector").isin(bpp.MARGIN_SERVICES) & (raw.pp > 0)]
gap = ((raw.pp - raw.bp - raw.m - raw.t) / raw.pp).abs()
report += ["", f"Accounting identity PP = BP + margins + taxes, cells with all four tables published: {len(gap)}, "
           f"{(gap <= bpp.IDENTITY_TOL).mean():.1%} within 1% (the others are dropped). Margins derived as "
           f"PP - BP - taxes (margins matrix not published): {pp.margins_derived.mean():.1%} of rows.", ""]
pub = pp[pp.geo.isin(published) & (pp.pp_meur >= 50) & (pp.demand_total > 0) & ~pp.sector.isin(["T", "U"])].copy()
goods = pub.sector.str[0].isin(list("ABC"))
pub["with_margins_vs_basic"] = pub.demand_total_pp_with_margins / pub.demand_total
report += ["Purchaser-price factor of the country of demand vs the basic-price factor, published rows (purchases above 50 MEUR):", "",
           "| year | n | goods: rebasing ratio, median | goods: with margins / basic, median (p10-p90) | services: with margins / basic, median (p10-p90) |",
           "|---|---|---|---|---|"]
for y in years:
    g, sv = pub[(pub.year == y) & goods], pub[(pub.year == y) & ~goods]
    report.append(f"| {y} | {len(g) + len(sv)} | {g.rebasing_ratio.median():.3f} | {g.with_margins_vs_basic.median():.3f} "
                  f"({g.with_margins_vs_basic.quantile(.1):.2f}-{g.with_margins_vs_basic.quantile(.9):.2f}) | "
                  f"{sv.with_margins_vs_basic.median():.3f} ({sv.with_margins_vs_basic.quantile(.1):.2f}-"
                  f"{sv.with_margins_vs_basic.quantile(.9):.2f}) |")
pub.to_csv(VAL / "5_purchaser_prices.csv", index=False)

# sensitivity 1: margins priced with the national mix of margin services vs all at wholesale trade (G46)
fac_full, dem_raw = bpp.load_factors(EDITION)
g46 = fac_full.total.xs("G46", level="sector")
alt = pub.margin_term / pub.margin_factor * pd.Series(list(zip(pub.year, pub.geo))).map(g46).to_numpy()
d1 = (pub.demand_total_pp_rebased + alt) / pub.demand_total_pp_with_margins - 1
# sensitivity 2: tax wedge of all industries vs industries other than the VAT-exempt ones
comp = bpp.components()
exempt = bpp.components(bpp.VAT_EXEMPT_USERS)
taxable = bpp.valuation((comp - exempt).dropna(subset=["pp", "bp", "t"]))
alt2 = bpp.price_factors(dem_raw, fac_full, taxable, bpp.margin_mix())
alt2 = pub.merge(alt2[["year", "geo", "sector", "demand_total_pp_with_margins"]], on=["year", "geo", "sector"],
                 suffixes=("", "_taxable"))
d2 = alt2.demand_total_pp_with_margins_taxable / alt2.demand_total_pp_with_margins - 1
tax_all = comp.t / comp.bp
tax_ex = (exempt.t / exempt.bp).reindex(tax_all.index)
fr = ("FR", 2022, "J62_63")
report += ["", "Sensitivity of the factor with margins (published rows, all years):", "",
           "| variant | n | median change | p10 | p90 | within 2% |", "|---|---|---|---|---|---|",
           f"| margins all priced at wholesale trade (G46) instead of the national mix of margin services | {d1.notna().sum()} | "
           f"{d1.median():+.1%} | {d1.quantile(.1):+.1%} | {d1.quantile(.9):+.1%} | {(d1.abs() <= .02).mean():.0%} |",
           f"| taxes of the industries other than the VAT-exempt ones (K, O, P, Q) | {d2.notna().sum()} | "
           f"{d2.median():+.1%} | {d2.quantile(.1):+.1%} | {d2.quantile(.9):+.1%} | {(d2.abs() <= .02).mean():.0%} |",
           "", f"Non-deductible VAT sits in the taxes: France 2022, taxes on IT services (J62-63) bought by all industries "
           f"{tax_all.get(fr):.1%} of the basic value, by the VAT-exempt ones {tax_ex.get(fr):.1%} (VAT rate 20%)."]

# ---------------------------------------------------------------- 6. variants
fin = pd.read_csv(OUT / f"figaro_final_demand_factors_{EDITION}.csv").set_index(["year", "geo", "sector"])
report += ["", "## 6. Variants", "", "### 6a. Country of demand weighted by final purchases vs by business purchases", "",
           "Same countries and products, both above 50 MEUR of purchases. Ratio = final / intermediate, total scopes 1-3 upstream.", "",
           "| year | n | goods median (p10-p90) | services median (p10-p90) |", "|---|---|---|---|"]
for y in years:
    d = dem.loc[y]
    f6 = fin.loc[y]
    keep = (d.index.get_level_values("geo").isin(published) & (d.purchases_meur >= 50) & (d.total > 0))
    j = pd.DataFrame({"inter": d.total[keep], "final": f6.total, "final_purchases": f6.purchases_meur}).dropna()
    j = j[(j.final_purchases >= 50) & (j.final > 0)]
    q = j.final / j.inter
    g = q.index.get_level_values("sector").str[0].isin(list("ABC"))
    report.append(f"| {y} | {len(q)} | {q[g].median():.2f} ({q[g].quantile(.1):.2f}-{q[g].quantile(.9):.2f}) | "
                  f"{q[~g].median():.2f} ({q[~g].quantile(.1):.2f}-{q[~g].quantile(.9):.2f}) |")
    j.assign(ratio=q).to_csv(VAL / f"6a_final_vs_intermediate_{y}.csv")
last = years[-1]
gb = [fac.loc[(last, "GB", "C13T15")].total, dem.loc[(last, "GB", "C13T15")].total, fin.loc[(last, "GB", "C13T15")].total]
report += ["", f"United Kingdom, textiles (C13-15), {last}: supply {gb[0]:.0f}, demand weighted by business purchases "
           f"{gb[1]:.0f}, by final purchases {gb[2]:.0f} kgCO2e/kEUR.", "",
           "### 6b. Supply-chain layers (supply table rows, output above 50 MEUR)", "",
           "Median share of the total: own operations f, tier 1 suppliers f A, tier 2 f A^2, tier 3 and beyond.", "",
           "| year | n | own operations | tier 1 | tier 2 | tier 3+ | rows with tier 3+ above 25% |", "|---|---|---|---|---|---|---|"]
for y in years:
    t = fac.loc[y]
    t = t[t.index.get_level_values("geo").isin(published) & (t.output_meur >= 50) & (t.total > 0)]
    sh = t[["tier0", "tier1", "tier2", "tier3_plus"]].div(t.total, axis=0)
    report.append(f"| {y} | {len(sh)} | {sh.tier0.median():.0%} | {sh.tier1.median():.0%} | {sh.tier2.median():.0%} | "
                  f"{sh.tier3_plus.median():.0%} | {(sh.tier3_plus > .25).mean():.0%} |")
t = fac.loc[last]
t = t[t.index.get_level_values("geo").isin(published) & (t.output_meur >= 50) & (t.total > 0)]
up = t.aviation_rf_extra / t.total
air = t.index.get_level_values("sector") == "H51"
report += ["", f"### 6c. Aviation radiative forcing ({last}, x1.7 on the direct CO2 of air transport H51)", "",
           f"- Air transport (H51), {air.sum()} countries: total +{up[air].median():.0%} in median "
           f"({up[air].min():.0%} to {up[air].max():.0%}).",
           f"- Other industries: +{up[~air].median():.2%} in median, {(up[~air] > .01).mean():.1%} of rows above +1%, "
           f"largest +{up[~air].max():.1%} ({up[~air].idxmax()[1]}, {up[~air].idxmax()[0]})."]

# ---------------------------------------------------------------- 7. ground truth
GEO_E = {"EL": "GR", "UK": "GB"}
price = pd.read_csv(DATA / "nrg_pc_205_non_household.csv")
price["year"], price["geo"] = price.time.str[:4].astype(int), price.geo.replace(GEO_E)
price = price.groupby(["geo", "year"]).value.mean()                      # EUR/kWh, mean of the two half-years
peh = pd.read_csv(DATA / "nrg_bal_peh_main_activity.csv")
peh["geo"] = peh.geo.replace(GEO_E)
elec = peh[(peh.unit == "GWH") & peh.nrg_bal.str.startswith("GEP")].groupby(["geo", "time"]).value.sum()
heat = peh[(peh.unit == "TJ") & peh.nrg_bal.str.startswith("GHP")].groupby(["geo", "time"]).value.sum() / 3.6
gge = pd.read_csv(DATA / "env_air_gge_public_power.csv")
gge["geo"] = gge.geo.replace(GEO_E)
grid = gge.set_index(["geo", "time"]).value / (elec + heat.reindex(elec.index).fillna(0.0))   # kt/GWh = kg/kWh
grid.index.names = ["geo", "year"]
d35 = fac.xs("D35", level="sector").swaplevel().sort_index()
c = pd.DataFrame({"scope1": d35.scope1, "total": d35.total, "grid_kg_kwh": grid, "price_eur_kwh": price}).dropna()
c = c[c.index.get_level_values("geo").isin(published) & c.index.get_level_values("year").isin(years)]
c["expected"] = c.grid_kg_kwh / c.price_eur_kwh * 1000.0
c["ratio_scope1"], c["ratio_total"] = c.scope1 / c.expected, c.total / c.expected
c.to_csv(VAL / "7_d35_electricity.csv")
report += ["", "## 7. Ground truth from outside the model", "",
           "### 7a. Electricity, gas, steam (D35) against grid intensity / electricity price", "",
           "Expected kgCO2e per kEUR = emissions of public electricity and heat production (national inventories, "
           "CRF 1.A.1.a, env_air_gge) / electricity and heat output of main-activity producers (nrg_bal_peh) / "
           "non-household electricity price excluding taxes, all bands (nrg_pc_205, mean of the two half-years; "
           "published for most countries from 2021).", "",
           "| year | countries | direct factor / expected, median (min-max) | total factor / expected, median (min-max) |",
           "|---|---|---|---|"]
for y in sorted(set(c.index.get_level_values("year"))):
    k = c.xs(y, level="year")
    if len(k) < 10:
        continue
    report.append(f"| {y} | {len(k)} | {k.ratio_scope1.median():.2f} ({k.ratio_scope1.min():.2f}-{k.ratio_scope1.max():.2f}) | "
                  f"{k.ratio_total.median():.2f} ({k.ratio_total.min():.2f}-{k.ratio_total.max():.2f}) |")
ws = pd.read_csv(DATA / "worldsteel_co2_intensity.csv").set_index("year").t_co2_per_t_crude_steel
cx = pd.read_csv(DATA / "comext_steel_exports.csv", dtype={"product": str})
cx = cx.pivot_table(index=["product", "time"], columns="indicators", values="value", aggfunc="sum")
unit_value = cx.VALUE_IN_EUROS / (cx.QUANTITY_IN_100KG / 10.0)          # EUR per tonne, EU exports to the world
c24 = fac.xs("C24", level="sector")
report += ["", "### 7b. Basic metals (C24) against steel intensity / steel price", "",
           "Expected kgCO2 per kEUR = worldsteel world CO2 intensity of crude steel / unit value of EU steel exports "
           "(Comext, all EU reporters, to all partners): iron and steel (HS 72) or hot-rolled flat products (HS 7208). "
           "FIGARO total of C24, EU countries with a C24 output above 1 billion EUR.", "",
           "| year | tCO2/t | EUR/t HS 72 | EUR/t HS 7208 | expected (HS 72 / HS 7208) | countries | FIGARO total, median (min-max) | ratio to HS 72, median |",
           "|---|---|---|---|---|---|---|---|"]
rows7 = []
for y in ws.index:
    if y not in years:
        continue
    e72, e08 = ws[y] * 1e6 / unit_value[("72", y)], ws[y] * 1e6 / unit_value[("7208", y)]
    k = c24.loc[y]
    k = k[k.index.isin(EU27) & (k.output_meur >= 1000)]
    rows7.append(pd.DataFrame({"year": y, "figaro_total": k.total, "expected_hs72": e72, "expected_hs7208": e08}))
    report.append(f"| {y} | {ws[y]} | {unit_value[('72', y)]:.0f} | {unit_value[('7208', y)]:.0f} | {e72:.0f} / {e08:.0f} | "
                  f"{len(k)} | {k.total.median():.0f} ({k.total.min():.0f}-{k.total.max():.0f}) | {(k.total / e72).median():.2f} |")
pd.concat(rows7).to_csv(VAL / "7_c24_steel.csv")

(VAL / "validation_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
print("\n".join(report))
