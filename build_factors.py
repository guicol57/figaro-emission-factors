"""Compute FIGARO monetary emission factors (scopes 1, 2, 3 upstream) for every region x industry.

    python build_factors.py --figaro-dir <folder with the FIGARO CSV files> [--years 2020 2021 2022 2023] [--edition 26ed]

Reads the industry-by-industry inter-country IOT (matrix or flat CSV) and the direct
emissions extract (data/env_ac_ghgfp_direct_emissions.csv). Writes, per year:
  results/<edition>/figaro_factors_<edition>.csv   all 46 regions, kgCO2e per thousand EUR of output
                                                  (basic prices, current prices) - not committed
  results/<edition>/final_demand_<year>.csv       final demand by country of final use (validate.py)
  results/<edition>/import_mix_FR_<year>.csv      origin mix of French intermediate imports (validate.py)
"""
import argparse
from pathlib import Path

import pandas as pd

from figaro_core import leontief, load_emissions, load_iot

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
    ap.add_argument("--years", nargs="+", type=int, default=[2020, 2021, 2022, 2023])
    ap.add_argument("--edition", default="26ed")
    a = ap.parse_args()
    out = HERE / "results" / a.edition
    out.mkdir(parents=True, exist_ok=True)
    frames = []
    for year in a.years:
        path, flat = find_table(Path(a.figaro_dir), year, a.edition)
        z, x, y = load_iot(str(path), flat)
        e = load_emissions(str(HERE / "data" / "env_ac_ghgfp_direct_emissions.csv"), year)
        e_co2 = load_emissions(str(HERE / "data" / "env_ac_co2fp_direct_emissions.csv"), year)
        res = leontief(z, x, e, e_co2)
        # accounting identity: emissions embodied in world final demand == world direct emissions
        embodied = float((y.sum(axis=1) * res.total).sum())
        assert abs(embodied / res.emissions_kt.sum() - 1) < 1e-6, "Leontief identity broken"
        y.to_csv(out / f"final_demand_{year}.csv")
        fr = z.columns.get_level_values("geo") == "FR"
        z.loc[z.index.get_level_values("geo") != "FR", fr].sum(axis=1).rename("meur").to_csv(out / f"import_mix_FR_{year}.csv")
        for c in res.columns.drop(["output_meur", "emissions_kt"]):
            res[c] *= 1000.0  # kg/EUR -> kg/kEUR
        res.insert(0, "year", year)
        frames.append(res.reset_index())
        print(year, path.name, f"world emissions {res.emissions_kt.sum()/1e6:.2f} Gt, identity ok")
    pd.concat(frames).to_csv(out / f"figaro_factors_{a.edition}.csv", index=False)
