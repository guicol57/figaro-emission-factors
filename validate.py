"""Three independent checks of the FIGARO factors. Writes results/<edition>/validation/.

    python validate.py [edition]      (after build_factors.py, default 26ed)

 1. Eurostat official footprints: our multipliers applied to FIGARO final demand must reproduce the
    GHG footprint by country published by Eurostat (env_ac_ghgfp) - checks the Leontief model itself.
 2. Scope 1: direct intensity must equal air emissions accounts / national-accounts output
    (env_ac_ainah_r2 / nama_10_a64, i.e. Eurostat's env_ac_aeint_r2 indicator).
 3. France, scopes 1-3 upstream: comparison with SDES/Insee table GES.501 (the values published as
    monetary ratios in ADEME Base Carbone), (a) pure FIGARO, (b) FIGARO import contents combined with
    the French national symmetric IOT, which approximates the 'simplified SNAC' method of the SDES.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from figaro_core import GEO_MAP, NACE_MAP

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

(VAL / "validation_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
print("\n".join(report))
