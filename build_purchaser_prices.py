"""Purchaser-price factors for business purchases, from the national supply and use tables.

    python build_purchaser_prices.py [edition]      (after build_factors.py, default 26ed)

The FIGARO factors are per EUR at basic prices. A company pays purchaser prices: the basic value of the
product, plus the trade and transport margins of the distributors, plus taxes less subsidies on products.
Eurostat publishes, per country and year, the use table at purchasers' prices (naio_10_cp16), at basic
prices (naio_10_cp1610) and the two valuation matrices between them (naio_10_cp1620 margins,
naio_10_cp1630 taxes), by product and by user. This script takes them over the intermediate consumption
of all industries (business purchases; total supply would mix in the retail margins paid by households).

Per (purchasing country s, product p, year):
  PP = BP + M + T                               national use tables, intermediate consumption
  rebasing ratio            = BP / PP           same emissions, purchaser-price denominator
  margin factor  FE_M(s)    = sum over margin services k of w_k(s) x m(s, k)
                              w_k = share of k in the trade and transport margins of the supply table
                              (naio_10_cp15, column OTTM), m = supply factor of country s
  with margins   FE_PP      = (BP x FE_BP + M x FE_M(s) + T x 0) / PP
                            = FE_BP x BP / PP + margin term,   margin term = M / PP x FE_M(s)
FE_BP is the factor of the country of demand (origin unknown). For a known origin r, the same two numbers
apply to the supply factor: FE_PP = m(r, p) x rebasing ratio + margin term.

Rules
- Margin services bought directly (G45-G47, H49-H53) carry negative entries in the margins matrix (the
  margins they earn on goods are moved to the goods): for them the margins are set to 0, PP = BP + T.
- When the margins matrix is not published but the three other tables are, M = PP - BP - T. Cells
  where PP differs from BP + M + T by more than 1% are dropped.
- Valuation matrices are compulsory every 5 years only: a year without them takes the nearest year of
  the same country within 5 years (the earlier one on a tie), reported in valuation_year.

Writes results/<edition>/figaro_purchaser_prices_<edition>.csv.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
DATA = HERE / "data"
EDITION = sys.argv[1] if len(sys.argv) > 1 else "26ed"
OUT = HERE / "results" / EDITION
SUT_CODES = {"C10-12": "C10T12", "C13-15": "C13T15", "D": "D35", "E37-39": "E37T39", "N80-82": "N80T82",
             "R90-92": "R90T92", "O": "O84", "P": "P85", "L68A": "L", "L68B": "L"}
GEO = {"EL": "GR", "UK": "GB"}
MARGIN_SERVICES = ("G45", "G46", "G47", "H49", "H50", "H51", "H52", "H53")
MAX_CARRY = 5
IDENTITY_TOL = 0.01


SECTORS = set(pd.read_csv(DATA / "nace_a64.csv").code)
VAT_EXEMPT_USERS = ("K64", "K65", "K66", "O", "P", "Q86", "Q87_88")
TABLES = (("pp", "cp16_purchasers"), ("bp", "cp1610_basic"), ("m", "cp1620_margins"), ("t", "cp1630_taxes"))


def sut(name: str, users=("TOTAL",)) -> pd.Series:
    """Values (M EUR) by (geo, year, FIGARO product), summed over the given users (NaN if one is missing)."""
    df = pd.read_csv(DATA / f"{name}.csv")
    prd = [c for c in df.columns if c.startswith(("prd", "cpa"))][0]
    df = df[df.ind_use.isin(users)]
    df["sector"] = df[prd].str.replace("CPA_", "", regex=False).replace(SUT_CODES)
    df = df[df.sector.isin(SECTORS)]
    df["geo"] = df.geo.replace(GEO)
    g = df.groupby(["geo", "time", "sector"])
    return g.value.sum().where(g.ind_use.nunique() == len(users))


def components(users=("TOTAL",)) -> pd.DataFrame:
    """PP, BP, margins and taxes (M EUR) of the intermediate consumption of the given users."""
    return pd.DataFrame({k: sut(f"naio_10_{n}", users) for k, n in TABLES})


def valuation(v: pd.DataFrame) -> pd.DataFrame:
    """Apply the rules of the module docstring; observed years only."""
    v = v.dropna(subset=["pp", "bp", "t"]).copy()
    v["margins_derived"] = v.m.isna()
    v["m"] = v.m.fillna(v.pp - v.bp - v.t)
    service = v.index.get_level_values("sector").isin(MARGIN_SERVICES) & (v.m < 0)
    v.loc[service, "pp"] = v.bp[service] + v.t[service]
    v.loc[service, "m"] = 0.0
    v["identity_gap"] = (v.pp - v.bp - v.m - v.t) / v.pp
    return v[(v.pp > 0) & (v.bp > 0) & (v.m >= 0) & (v.identity_gap.abs() <= IDENTITY_TOL)]


def nearest(available: dict, geo: str, year: int):
    years = sorted(available.get(geo, ()), key=lambda v: (abs(v - year), v))
    return years[0] if years and abs(years[0] - year) <= MAX_CARRY else None


def margin_mix() -> pd.DataFrame:
    """Share of each margin service in the trade and transport margins, by (geo, year)."""
    s = pd.read_csv(DATA / "naio_10_cp15_margins_supply.csv")
    s["sector"] = s.prd_amo.str.replace("CPA_", "", regex=False)
    s["geo"] = s.geo.replace(GEO)
    s = s[s.sector.isin(MARGIN_SERVICES) & (s.value < 0)]
    w = (-s.set_index(["geo", "time", "sector"]).value).unstack("sector").fillna(0.0)
    return w.div(w.sum(axis=1), axis=0)


def years_of(df: pd.DataFrame) -> dict:
    idx = df.index.droplevel([n for n in df.index.names if n not in ("geo", "time")]).unique()
    out = {}
    for g, t in idx:
        out.setdefault(g, set()).add(t)
    return out


def price_factors(dem: pd.DataFrame, fac: pd.DataFrame, val: pd.DataFrame, mix: pd.DataFrame) -> pd.DataFrame:
    """One row per (year, purchasing country, product) of `dem` with valuation data within MAX_CARRY years.
    fac: complete supply factors indexed by (year, geo, sector), kgCO2e per k EUR."""
    val_years, mix_years = years_of(val), years_of(mix)
    rows = []
    for (year, geo), d in dem.groupby(["year", "geo"]):
        vy, my = nearest(val_years, geo, year), nearest(mix_years, geo, year)
        if vy is None or my is None:
            continue
        v = val.loc[(geo, vy)].reindex(d.sector)
        w = mix.loc[(geo, my)]
        m_margin = sum(w[k] * fac.total.get((year, geo, k), np.nan) for k in w.index if w[k] > 0)
        rows.append(pd.DataFrame({
            "year": year, "geo": geo, "sector": d.sector.to_numpy(), "valuation_year": vy, "margin_mix_year": my,
            "pp_meur": v.pp.to_numpy(), "share_basic": (v.bp / v.pp).to_numpy(), "share_margins": (v.m / v.pp).to_numpy(),
            "share_taxes": (v.t / v.pp).to_numpy(), "margins_derived": v.margins_derived.to_numpy(),
            "margin_mix_transport": float(w[[k for k in w.index if k.startswith("H")]].sum()),
            "margin_factor": m_margin, "demand_total": d.total.to_numpy(),
        }).dropna(subset=["pp_meur"]))
    res = pd.concat(rows, ignore_index=True)
    res["rebasing_ratio"] = res.share_basic
    res["margin_term"] = res.share_margins * res.margin_factor
    res["demand_total_pp_rebased"] = res.demand_total * res.rebasing_ratio
    res["demand_total_pp_with_margins"] = res.demand_total_pp_rebased + res.margin_term
    # basic value + margins + taxes = purchaser price (taxes may be negative: subsidies)
    assert np.allclose(res.share_basic + res.share_margins + res.share_taxes, 1, atol=IDENTITY_TOL)
    return res


def load_factors(edition: str = EDITION) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = HERE / "results" / edition
    fac = pd.read_csv(out / f"figaro_factors_{edition}.csv")
    return (fac[fac.total.notna()].set_index(["year", "geo", "sector"]),
            pd.read_csv(out / f"figaro_demand_factors_{edition}.csv"))


if __name__ == "__main__":
    fac, dem = load_factors()
    res = price_factors(dem, fac, valuation(components()), margin_mix())
    res.to_csv(OUT / f"figaro_purchaser_prices_{EDITION}.csv", index=False)
    print(f"figaro_purchaser_prices_{EDITION}.csv", len(res), "rows |", res.geo.nunique(), "countries |",
          f"{(res.valuation_year == res.year).mean():.0%} with valuation matrices of the same year")
