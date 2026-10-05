"""FIGARO environmentally-extended Leontief model - core functions.

Inputs
- FIGARO inter-country input-output table (Eurostat, CC BY 4.0), "matrix" or "flatfile" CSV,
  industry-by-industry or product-by-product, 64 positions x 50 regions (2025 edition).
- Direct GHG emissions by country x NACE A64 industry: Eurostat dataset env_ac_ghgfp
  (na_item=TOTAL, c_dest=WORLD), i.e. the air emissions accounts (EU) and the EDGAR-based
  estimates (non-EU) that Eurostat itself uses as the FIGARO environmental extension.

Model
  x   = total output per (region, sector)            [M EUR, basic prices]
  A   = Z / x (column-wise technical coefficients)
  f   = E / x direct intensity                       [kt / M EUR = kg / EUR]
  m   = f (I - A)^-1 total upstream intensity        [kgCO2e / EUR]
Scope split of m for sector j:
  scope 1        = f_j
  scope 2        = sum over regions r of f_(r,D35) * A[(r,D35), j]
                   (direct emissions of the electricity, gas, steam suppliers, first tier)
  scope 3 upstream = m_j - scope 1 - scope 2
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# Regions present in the 2025 edition IOT but not in the published emission accounts:
# they are folded into the rest-of-world block, as in the emission dataset (WRL_REST).
FOLD_INTO_ROW = {"AL", "ME", "MK", "RS"}
ROW = "FIGW1"
ENERGY = "D35"

# Eurostat dissemination codes -> FIGARO codes
GEO_MAP = {"EL": "GR", "UK": "GB", "WRL_REST": ROW}
NACE_MAP = {
    "C10-C12": "C10T12", "C13-C15": "C13T15", "C31_C32": "C31_32", "D": "D35",
    "E37-E39": "E37T39", "J59_J60": "J59_60", "J62_J63": "J62_63", "M69_M70": "M69_70",
    "M74_M75": "M74_75", "N80-N82": "N80T82", "Q87_Q88": "Q87_88", "R90-R92": "R90T92",
    "F": "F", "I": "I", "L": "L", "O": "O84", "P": "P85",
}
FINAL_DEMAND = ("P3_S13", "P3_S14", "P3_S15", "P51G", "P5M")


def _split(code: str) -> tuple[str, str]:
    geo, sec = code.split("_", 1)
    return geo, sec.replace("CPA_", "")


def load_iot(path: str, flat: bool = False) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """Return (Z, x, Y): intermediate flows, total output and final demand by country of
    final use, indexed by (region, sector), with AL/ME/MK/RS folded into the rest-of-world block."""
    if flat:
        ff = pd.read_csv(path, usecols=[0, 1, 6], dtype={0: str, 1: str})
        ff.columns = ["row", "col", "v"]
        m = ff.pivot(index="row", columns="col", values="v").fillna(0.0)
    else:
        m = pd.read_csv(path, index_col=0)
    rows = [r for r in m.index if not r.startswith("W2_")]
    cols_z = [c for c in m.columns if not c.endswith(FINAL_DEMAND)]
    assert set(rows) == set(cols_z), "IOT is not square"
    m = m.loc[rows]
    x = m.sum(axis=1)  # total uses = total output at basic prices
    z = m[rows]

    def key(code):
        geo, sec = _split(code)
        return (ROW if geo in FOLD_INTO_ROW else geo, sec)

    idx = pd.MultiIndex.from_tuples([key(c) for c in rows], names=["geo", "sector"])
    z.index = idx
    z.columns = idx
    x.index = idx
    y = m[[c for c in m.columns if c.endswith(FINAL_DEMAND)]]
    y.index = idx
    y.columns = pd.Index([key(c)[0] for c in y.columns])
    y = y.T.groupby(level=0).sum().T.groupby(level=[0, 1], sort=False).sum()
    z = z.T.groupby(level=[0, 1], sort=False).sum().T.groupby(level=[0, 1], sort=False).sum()
    x = x.groupby(level=[0, 1], sort=False).sum()
    return z, x.loc[z.index], y.loc[z.index]


def load_emissions(path: str, year: int) -> pd.Series:
    """Direct emissions (kt CO2e) by (region, A64 sector) for one year."""
    df = pd.read_csv(path, dtype={"time": int})
    df = df[df.time == year].copy()
    df["geo"] = df.c_orig.replace(GEO_MAP)
    df["sector"] = df.nace_r2.replace(NACE_MAP)
    return df.set_index(["geo", "sector"]).value


EU27 = {"AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES", "FI", "FR", "GR", "HR", "HU", "IE", "IT", "LT",
        "LU", "LV", "MT", "NL", "PL", "PT", "RO", "SE", "SI", "SK"}


def leontief(z: pd.DataFrame, x: pd.Series, e: pd.Series, e_co2: pd.Series | None = None) -> pd.DataFrame:
    """Total, scope 1, scope 2 and scope 3 upstream intensities (kgCO2e/EUR), with
    - the CO2-only part of each (when e_co2 is given),
    - the part emitted in the producing country (_dom) and in the other EU27 countries (_eu) for the
      total and for scopes 1 + 2 (the remainder is emitted outside the EU)."""
    e = e.reindex(z.index)
    missing = e[e.isna()]
    assert missing.empty, f"no emissions for {list(missing.index[:5])}"
    n = len(x)
    xv = x.to_numpy(float)
    inv_x = np.divide(1.0, xv, out=np.zeros_like(xv), where=xv > 0)
    a = z.to_numpy(float) * inv_x[None, :]
    f = e.to_numpy(float) * inv_x
    linv = np.linalg.inv(np.eye(n) - a)
    m = f @ linv
    geo = z.index.get_level_values("geo").to_numpy()
    is_energy = (z.index.get_level_values("sector") == ENERGY)
    fe = f * is_energy
    s2 = fe @ a
    out = pd.DataFrame({"output_meur": xv, "emissions_kt": e.to_numpy(float), "scope1": f,
                        "scope2": s2, "scope3_upstream": m - f - s2, "total": m}, index=z.index)
    if e_co2 is not None:
        fc = np.minimum(e_co2.reindex(z.index).fillna(0.0).to_numpy(float), e.to_numpy(float)) * inv_x
        out["scope1_co2"], out["scope2_co2"], out["total_co2"] = fc, (fc * is_energy) @ a, fc @ linv
    # origin of emissions: same country / other EU27 / rest of the world
    codes, inverse = np.unique(geo, return_inverse=True)
    same = np.zeros((len(codes), n))
    same[inverse, np.arange(n)] = 1.0                      # same[c, i] = 1 if row i belongs to country c
    in_eu = np.isin(geo, list(EU27)).astype(float)
    fl = f[:, None] * linv                                   # emissions of row i per unit output of column j
    dom_total = (same @ fl)[inverse, np.arange(n)]
    fa = fe[:, None] * a
    dom_s2 = (same @ fa)[inverse, np.arange(n)]
    out["total_dom"] = dom_total
    out["total_eu"] = in_eu @ fl - dom_total * in_eu         # other EU27 countries
    out["s12_dom"] = f + dom_s2
    out["s12_eu"] = in_eu @ fa - dom_s2 * in_eu
    return out
