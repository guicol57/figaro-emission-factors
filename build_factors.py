"""Compute FIGARO monetary emission factors (scopes 1, 2, 3 upstream) for every region x industry.

    python build_factors.py --figaro-dir <folder with the FIGARO CSV files> [--years 2014 ... 2023] [--edition 26ed]

Reads the industry-by-industry inter-country IOT (matrix or flat CSV) and the direct
emissions extract (data/env_ac_ghgfp_direct_emissions.csv). Writes, per year:
  results/<edition>/figaro_factors_<edition>.csv   all 46 regions, kgCO2e per thousand EUR of output
                                                  (basic prices, current prices) - not committed
  results/<edition>/figaro_demand_factors_<edition>.csv  factors of the country of demand: supply factors
                                                  weighted by the origin of each region's intermediate
                                                  purchases (complete years only) - not committed
  results/<edition>/final_demand_<year>.csv       final demand by country of final use (validate.py)
  results/<edition>/import_mix_FR_<year>.csv      origin mix of French intermediate imports (validate.py)
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from figaro_core import demand_factors, leontief, load_aea, load_emissions, load_iot

HERE = Path(__file__).parent


def find_table(folder: Path, year: int, EDITION: str) -> tuple[Path, bool]:
    name = f"eu-ic-io_ind-by-ind_{EDITION}_{year}"
    for cand, flat in ((folder / f"matrix_{name}.csv", False), (folder / f"flatfile_{name}.csv", True),
                       (folder / f"flatfile_{name}" / f"flatfile_{name}.csv", True)):
        if cand.exists():
            return cand, flat
    raise FileNotFoundError(f"no FIGARO ind-by-ind table for {year} in {folder}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--figaro-dir", required=True)
    ap.add_argument("--years", nargs="+", type=int, default=list(range(2014, 2024)))
    ap.add_argument("--edition", default="26ed")
    ap.add_argument("--provisional-year", type=int, default=2024,
                    help="year after the last one: scopes 1 + 2 only, from the air emissions accounts")
    a = ap.parse_args()
    out = HERE / "results" / a.edition
    out.mkdir(parents=True, exist_ok=True)
    frames, demand = [], []
    for year in a.years:
        path, flat = find_table(Path(a.figaro_dir), year, a.edition)
        z, x, y = load_iot(str(path), flat)
        e = load_emissions(str(HERE / "data" / "env_ac_ghgfp_direct_emissions.csv"), year)
        e_co2 = load_emissions(str(HERE / "data" / "env_ac_co2fp_direct_emissions.csv"), year)
        res, by_geo = leontief(z, x, e, e_co2, origin=True)
        # accounting identity: emissions embodied in world final demand == world direct emissions
        embodied = float((y.sum(axis=1) * res.total).sum())
        assert abs(embodied / res.emissions_kt.sum() - 1) < 1e-6, "Leontief identity broken"
        y.to_csv(out / f"final_demand_{year}.csv")
        fr = z.columns.get_level_values("geo") == "FR"
        z.loc[z.index.get_level_values("geo") != "FR", fr].sum(axis=1).rename("meur").to_csv(out / f"import_mix_FR_{year}.csv")
        dem = demand_factors(z, res, by_geo, list(dict.fromkeys(z.columns.get_level_values("geo"))))
        # identity: demand factors x purchases == emissions embodied in each region's intermediate purchases
        embodied_ci = z.T.groupby(level="geo").sum().T.mul(res.total, axis=0).sum()
        weighted = (dem.total * dem.purchases_meur).groupby(dem.geo).sum().reindex(embodied_ci.index)
        assert np.allclose(weighted, embodied_ci, rtol=1e-9), "demand weighting broken"
        origin_sum = (dem.total_dom + dem.total_eu) <= dem.total * (1 + 1e-9)
        assert origin_sum.all(), "place of emission exceeds the total"
        for c in res.columns.drop(["output_meur", "emissions_kt"]):
            res[c] *= 1000.0  # kg/EUR -> kg/kEUR
        for c in [c for c in dem.columns if c.startswith(("scope", "total"))]:
            dem[c] *= 1000.0
        dem.insert(0, "year", year)
        demand.append(dem)
        res.insert(0, "year", year)
        frames.append(res.reset_index())
        print(year, path.name, f"world emissions {res.emissions_kt.sum()/1e6:.2f} Gt, identity ok")
    # Provisional year: world emission accounts are not published yet, so the total and scope 3 upstream
    # cannot be computed. Scopes 1 + 2 can: the air emissions accounts of European countries are already
    # available. Regions and industries without accounts keep their intensity of the previous year (they
    # only enter scope 2 through electricity, gas and steam bought from them).
    py = a.provisional_year
    try:
        path, flat = find_table(Path(a.figaro_dir), py, a.edition) if py else (None, None)
    except FileNotFoundError:
        path = None
    if path is not None and frames and int(frames[-1].year.iloc[0]) == py - 1:
        prev = frames[-1].set_index(["geo", "sector"])
        z, x, _ = load_iot(str(path), flat)
        prev = prev.reindex(z.index)
        e, e_co2 = [(prev[col].fillna(0.0) / 1000.0 * x) for col in ("scope1", "scope1_co2")]
        observed = pd.Series(False, index=z.index)
        for vec, name in ((e, "env_ac_ainah_r2_ghg.csv"), (e_co2, "env_ac_ainah_r2_co2.csv")):
            aea = load_aea(str(HERE / "data" / name), py).reindex(z.index)
            vec[aea.notna()] = aea[aea.notna()]
            if vec is e:
                observed = aea.notna()
        res = leontief(z, x, e, e_co2)
        for c in res.columns.drop(["output_meur", "emissions_kt"]):
            res[c] *= 1000.0
        res[["scope3_upstream", "total", "total_co2", "total_dom", "total_eu"]] = float("nan")
        res = res[observed.to_numpy()]            # only rows whose scope 1 comes from published accounts
        res.insert(0, "year", py)
        frames.append(res.reset_index())
        print(py, path.name, f"provisional, scopes 1 + 2 only, {len(res)} rows with published accounts")
    pd.concat(frames).to_csv(out / f"figaro_factors_{a.edition}.csv", index=False)
    pd.concat(demand).to_csv(out / f"figaro_demand_factors_{a.edition}.csv", index=False)
