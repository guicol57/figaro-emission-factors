"""Download the small Eurostat extracts used by the FIGARO pipeline (dissemination API, JSON-stat).

    python fetch_eurostat.py

    python fetch_eurostat.py --tables <folder>     also download the FIGARO tables (48 MB per year)

    python fetch_eurostat.py --only <name>[,<name>...]   refresh some extracts only, keep the others as committed

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

# intermediate consumption of all industries, and of the industries whose sales are mostly exempt from VAT
PRICE_USERS = ("TOTAL", "K64", "K65", "K66", "O", "P", "Q86", "Q87_88")

EXTRACTS = {
    # direct emissions by emitting country x industry (environmental extension of FIGARO)
    "env_ac_ghgfp_direct_emissions": ("env_ac_ghgfp?c_dest=WORLD&na_item=TOTAL", ["c_orig", "nace_r2", "time"]),
    # same for CO2 alone (CO2 / other GHG split)
    "env_ac_co2fp_direct_emissions": ("env_ac_co2fp?c_dest=WORLD&na_item=TOTAL", ["c_orig", "nace_r2", "time"]),
    # official Eurostat footprints by country of final use (validation 1)
    "env_ac_ghgfp_footprint_by_dest": ("env_ac_ghgfp?c_orig=WORLD&nace_r2=TOTAL&na_item=TOTAL&sinceTimePeriod=2014", ["c_dest", "time"]),
    # official air emissions accounts and national-accounts output (validation 2, scope 1)
    "env_ac_ainah_r2_ghg": ("env_ac_ainah_r2?airpol=GHG&unit=THS_T&sinceTimePeriod=2014", ["geo", "nace_r2", "time"]),
    # CO2 alone, used for the provisional year (scopes 1 + 2 only)
    "env_ac_ainah_r2_co2": ("env_ac_ainah_r2?airpol=CO2&unit=THS_T&sinceTimePeriod=2023", ["geo", "nace_r2", "time"]),
    "nama_10_a64_p1": ("nama_10_a64?na_item=P1&unit=CP_MEUR&sinceTimePeriod=2014", ["geo", "nace_r2", "time"]),
    # French national symmetric input-output table, domestic and imports (validation 3, SNAC)
    "naio_10_cp1700_FR": ("naio_10_cp1700?geo=FR&unit=MIO_EUR&sinceTimePeriod=2014", ["stk_flow", "prd_ava", "prd_use", "time"]),
    # purchaser prices (build_purchaser_prices.py): national use tables by product, for the intermediate
    # consumption of all industries (TOTAL) and of the VAT-exempt ones (validation of the tax wedge),
    # at purchasers' prices, at basic prices, and the two valuation matrices between them
    **{name: (f"{ds}?unit=MIO_EUR{extra}&sinceTimePeriod=2014&" + "&".join(f"ind_use={u}" for u in PRICE_USERS),
              ["geo", prd, "ind_use", "time"])
       for name, ds, prd, extra in (
           ("naio_10_cp16_purchasers", "naio_10_cp16", "prd_ava", ""),
           ("naio_10_cp1610_basic", "naio_10_cp1610", "prd_ava", "&stk_flow=TOTAL"),
           ("naio_10_cp1620_margins", "naio_10_cp1620", "cpa2_1", ""),
           ("naio_10_cp1630_taxes", "naio_10_cp1630", "cpa2_1", ""))},
    # trade and transport margins column of the supply table: which margin services the margins pay for
    "naio_10_cp15_margins_supply": ("naio_10_cp15?unit=MIO_EUR&ind_impv=OTTM&sinceTimePeriod=2014", ["geo", "prd_amo", "time"]),
}


CIRCABC = "https://circabc.europa.eu/rest/download/"
# CIRCABC node ids of matrix_eu-ic-io_ind-by-ind_26ed_<year>.csv (folder listed 2026-10-03)
TABLES_26ED = {
    2014: "85d3f6de-3510-45ff-96c9-11da9f1e325a", 2015: "e989cc76-52f5-4cd9-ba8c-5764fafde13a",
    2016: "2e7bc8e5-ee0c-4e57-a082-60a9fb59ee73", 2017: "0bd4147b-d06b-4800-87e4-c479352e88ba",
    2018: "40c2349e-1ba7-48b5-b4a3-4f00b78f2283", 2019: "ba9d7f3a-a381-49f2-998d-64fec81c3d35",
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
    only = set(sys.argv[sys.argv.index("--only") + 1].split(",")) if "--only" in sys.argv else set(EXTRACTS)
    assert only <= set(EXTRACTS), f"unknown extract {only - set(EXTRACTS)}"
    sources = DATA / "SOURCES.csv"
    previous = {line.split(",", 1)[0]: line for line in sources.read_text(encoding="utf-8").splitlines()[1:]} if sources.exists() else {}
    log = []
    for name, (query, keep) in EXTRACTS.items():
        if name not in only:
            if f"{name}.csv" in previous:
                log.append(previous[f"{name}.csv"])
            continue
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
    sources.write_text("file,api_query,eurostat_last_update,rows\n" + "\n".join(log) + "\n", encoding="utf-8")
