"""Download the small Eurostat extracts used by the FIGARO pipeline (dissemination API, JSON-stat).

    python fetch_eurostat.py

    python fetch_eurostat.py --tables <folder>     also download the FIGARO tables (48 MB per year)

Writes CSV files in data/. The FIGARO industry-by-industry tables (matrix CSV, 2026 edition) come
from the public FIGARO space on CIRCABC (guest access), linked from
https://ec.europa.eu/eurostat/web/esa-supply-use-input-tables/database
"""
import sys
import json
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

API = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
DATA = Path(__file__).parent / "data"

EXTRACTS = {
    # direct emissions by emitting country x industry (environmental extension of FIGARO)
    "env_ac_ghgfp_direct_emissions": ("env_ac_ghgfp?c_dest=WORLD&na_item=TOTAL", ["c_orig", "nace_r2", "time"]),
    # same for CO2 alone (CO2 / other GHG split)
    "env_ac_co2fp_direct_emissions": ("env_ac_co2fp?c_dest=WORLD&na_item=TOTAL", ["c_orig", "nace_r2", "time"]),
    # official Eurostat footprints by country of final use (validation 1)
    "env_ac_ghgfp_footprint_by_dest": ("env_ac_ghgfp?c_orig=WORLD&nace_r2=TOTAL&na_item=TOTAL&sinceTimePeriod=2020", ["c_dest", "time"]),
    # official air emissions accounts and national-accounts output (validation 2, scope 1)
    "env_ac_ainah_r2_ghg": ("env_ac_ainah_r2?airpol=GHG&unit=THS_T&sinceTimePeriod=2020", ["geo", "nace_r2", "time"]),
    "nama_10_a64_p1": ("nama_10_a64?na_item=P1&unit=CP_MEUR&sinceTimePeriod=2020", ["geo", "nace_r2", "time"]),
    # French national symmetric input-output table, domestic and imports (validation 3, SNAC)
    "naio_10_cp1700_FR": ("naio_10_cp1700?geo=FR&unit=MIO_EUR&sinceTimePeriod=2020", ["stk_flow", "prd_ava", "prd_use", "time"]),
}


CIRCABC = "https://circabc.europa.eu/rest/download/"
# CIRCABC node ids of matrix_eu-ic-io_ind-by-ind_26ed_<year>.csv (folder listed 2026-10-03)
TABLES_26ED = {
    2020: "28d77fbf-50c2-475c-8ba6-c97b02a69039", 2021: "57fd3555-51db-4f03-b765-3cb7fcfe3007",
    2022: "f1330ee5-2841-4f3a-949c-20f36d068714", 2023: "836a0346-bdb5-4d8a-bbea-b3bd583a53c9",
    2024: "8ac7da34-911e-4a91-ab1c-8aec1a574381",
}


def fetch(query: str, keep: list[str]) -> tuple[pd.DataFrame, str]:
    sep = "&" if "?" in query else "?"
    with urllib.request.urlopen(f"{API}{query}{sep}format=JSON&lang=EN") as r:
        d = json.load(r)
    ids, size = d["id"], d["size"]
    cats = [list(d["dimension"][i]["category"]["index"]) for i in ids]
    strides = np.cumprod([1] + size[::-1])[:-1][::-1]
    rows = [[cats[i][(int(k) // s) % n] for i, (s, n) in enumerate(zip(strides, size))] + [v]
            for k, v in d["value"].items()]
    return pd.DataFrame(rows, columns=ids + ["value"])[keep + ["value"]], d["updated"]


if __name__ == "__main__":
    DATA.mkdir(exist_ok=True)
    log = []
    for name, (query, keep) in EXTRACTS.items():
        df, updated = fetch(query, keep)
        df.to_csv(DATA / f"{name}.csv", index=False)
        log.append(f"{name}.csv,{query},{updated},{len(df)}")
        print(log[-1])
    if "--tables" in sys.argv:
        folder = Path(sys.argv[sys.argv.index("--tables") + 1])
        folder.mkdir(parents=True, exist_ok=True)
        for year, node in TABLES_26ED.items():
            target = folder / f"matrix_eu-ic-io_ind-by-ind_26ed_{year}.csv"
            if not target.exists():
                urllib.request.urlretrieve(CIRCABC + node, target)
            print(target.name, target.stat().st_size)
    (DATA / "SOURCES.csv").write_text("file,api_query,eurostat_last_update,rows\n" + "\n".join(log) + "\n", encoding="utf-8")
