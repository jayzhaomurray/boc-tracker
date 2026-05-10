"""
Housing deep-dive data-source probe — 2026-05-09

Confirms:
  1. BoC Valet keys for CREA sales/SNLR and 5-year mortgage rate
  2. StatsCan Table 34-10-0158 vectors for under construction + regional starts

Writes report to analyses/housing_deepdive_probe_results_2026_05_09.md
"""

import json
import requests
import pandas as pd
from pathlib import Path

OUT = Path(__file__).parent / "housing_deepdive_probe_results_2026_05_09.md"
lines = []

def log(s=""):
    try:
        print(s)
    except UnicodeEncodeError:
        print(s.encode("ascii", errors="replace").decode("ascii"))
    lines.append(s)


# ── 1. Probe specific Valet keys directly ─────────────────────────────────────

log("# Housing Deep-Dive Data-Source Probe — 2026-05-09")
log()
log("## 1. BoC Valet direct key probes")
log()

PROBE_KEYS = [
    # 5-year fixed mortgage rate candidates
    "BD.CDN.5YR.MTG.DQ.YLD",
    "BD.CDN.5YR.MTG.WK.YLD",   # weekly variant
    "BD.CDN.5YR.MTG.MO.YLD",   # monthly variant
    "V122514",
    # CREA sales / SNLR (FVI series)
    "FVI_CREA_SALES_CANADA",
    "FVI_CREA_SNLR_CANADA",
    "FVI_CREA_MLS_SNLR",
    "FVI_CREA_MLS_SNLR_CANADA",
    "FVI_CREA_SNLR",
    "FVI_CREA_SALES",
    "FVI_CREA_MLS_SALES",
    "FVI_CREA_MLS_SALES_CANADA",
    # broker / posted rate
    "BROKER_AVERAGE_5YR_VRM",
    "V80691335",   # possible posted rate StatsCan via Valet
]

for key in PROBE_KEYS:
    url = f"https://www.bankofcanada.ca/valet/observations/{key}/json"
    try:
        r = requests.get(url, params={"start_date": "2020-01-01"}, timeout=15)
        if r.status_code == 200:
            payload = r.json()
            obs = payload.get("observations", [])
            if obs:
                latest = obs[-1]
                # value may be nested under key name or "v"
                raw_val = latest.get(key, {})
                if isinstance(raw_val, dict):
                    val = raw_val.get("v", "?")
                else:
                    val = raw_val
                log(f"  OK  {key}: SUCCESS -- {len(obs)} obs, latest={latest.get('d','?')} val={val}")
            else:
                log(f"  ~~  {key}: 200 OK but 0 observations")
        else:
            log(f"  XX  {key}: HTTP {r.status_code}")
    except Exception as e:
        log(f"  XX  {key}: ERROR {e}")

log()


# ── 2. BoC Valet series list — filter for FVI_CREA and BD.CDN.*MTG* ──────────

log("## 2. Valet series list — FVI_CREA* and *MTG* keys only")
log()

try:
    r = requests.get("https://www.bankofcanada.ca/valet/lists/series/json", timeout=30)
    r.raise_for_status()
    valet_list = r.json()
    series_dict = valet_list.get("series", {})

    # FVI_CREA* keys
    fvi_crea = {k: v for k, v in series_dict.items() if k.startswith("FVI_CREA")}
    log(f"FVI_CREA* keys ({len(fvi_crea)} found):")
    for k in sorted(fvi_crea.keys()):
        v = fvi_crea[k]
        label = v.get("label", str(v)[:80]) if isinstance(v, dict) else str(v)[:80]
        log(f"  {k}: {label}")
    log()

    # BD.CDN.*MTG* keys
    mtg_keys = {k: v for k, v in series_dict.items()
                if "MTG" in k.upper() and k.upper().startswith("BD.CDN")}
    log(f"BD.CDN.*MTG* keys ({len(mtg_keys)} found):")
    for k in sorted(mtg_keys.keys()):
        v = mtg_keys[k]
        label = v.get("label", str(v)[:80]) if isinstance(v, dict) else str(v)[:80]
        log(f"  {k}: {label}")
    log()

    # Broker / posted rate keys
    broker_keys = {k: v for k, v in series_dict.items() if "BROKER" in k.upper() or "POSTED" in k.upper()}
    log(f"BROKER/POSTED keys ({len(broker_keys)} found):")
    for k in sorted(broker_keys.keys()):
        v = broker_keys[k]
        label = v.get("label", str(v)[:80]) if isinstance(v, dict) else str(v)[:80]
        log(f"  {k}: {label}")
    log()

except Exception as e:
    log(f"ERROR: {e}")
    log()


# ── 3. StatsCan Table 34-10-0158 cube metadata ────────────────────────────────

log("## 3. StatsCan Table 34-10-0158 — getCubeMetadata")
log()

PRODUCT_ID = 3410015801

try:
    url = f"https://www150.statcan.gc.ca/t1/wds/rest/getCubeMetadata/{PRODUCT_ID}"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    meta = r.json()

    if meta.get("status") != "SUCCESS":
        log(f"status: {meta.get('status')}")
        log(json.dumps(meta, indent=2)[:3000])
    else:
        cube_obj = meta.get("object", {})
        dimensions = cube_obj.get("dimension", [])
        log(f"Dimensions ({len(dimensions)}):")
        for i, dim in enumerate(dimensions):
            dim_name = dim.get("dimensionNameEn", "?")
            members = dim.get("member", [])
            log(f"\n  Dim {i+1}: {dim_name}")
            for m in members:
                log(f"    [{m.get('memberId','?')}] {m.get('memberNameEn','?')}")

except Exception as e:
    log(f"ERROR: {e}")
log()


# ── 4. getSeriesInfoFromVector for key structural vectors ─────────────────────

log("## 4. getSeriesInfoFromVector — housing_starts + nearby vectors")
log()

# We know v52300157 = Canada total starts
# Check neighboring vectors to find under-construction and CMA starts
VIDS = list(range(52300157, 52300200))

for vid in VIDS:
    try:
        url = f"https://www150.statcan.gc.ca/t1/wds/rest/getSeriesInfoFromVector/{vid}"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            payload = r.json()
            if isinstance(payload, list) and payload:
                status = payload[0].get("status", "?")
                obj = payload[0].get("object", {})
            else:
                status, obj = "?", {}
            title = obj.get("SeriesTitleEn") or obj.get("seriesTitleEn") or "?"
            if status == "SUCCESS":
                log(f"  v{vid}: {title}")
            else:
                log(f"  v{vid}: status={status}")
        else:
            log(f"  v{vid}: HTTP {r.status_code}")
    except Exception as e:
        log(f"  v{vid}: ERROR {e}")
log()


# ── 5. getSeriesInfoFromCubePidCoord — probe under-construction coords ────────

log("## 5. getSeriesInfoFromCubePidCoord — probe specific member coords")
log()

# Table 34-10-0158 typical structure (based on CMHC/StatsCan docs):
#   Dim 1: Variable type (1=Starts, 2=Under construction, 3=Completions)
#   Dim 2: Housing type (1=Total, 2=Single, 3=Semi, 4=Row, 5=Apartment/other)
#   Dim 3: Geography (depends on table; Canada=1 typically)

# Try a set of plausible coordinate combos
coords_to_try = [
    # (coord_string, label)
    ("1.1.1",  "var1 type1 geo1"),
    ("2.1.1",  "var2 type1 geo1"),
    ("3.1.1",  "var3 type1 geo1"),
    ("1.2.1",  "var1 type2 geo1"),
    ("2.2.1",  "var2 type2 geo1"),
    # swap dim order: type first
    ("1.1.1",  "type1 var1 geo1"),
]

# Actually, let me use the dimension member IDs from the metadata retrieved above
# (we'll parse them from the earlier call if possible)
# For now, try getCubeMembers approach
try:
    url2 = f"https://www150.statcan.gc.ca/t1/wds/rest/getCubeMetadata/{PRODUCT_ID}"
    r2 = requests.get(url2, timeout=60)
    r2.raise_for_status()
    meta2 = r2.json()
    if meta2.get("status") == "SUCCESS":
        cube_obj2 = meta2["object"]
        dims2 = cube_obj2.get("dimension", [])

        # Build a map: dim_index -> [(memberId, name), ...]
        dim_map = {}
        for i, dim in enumerate(dims2):
            members = dim.get("member", [])
            dim_map[i] = [(str(m.get("memberId", "")), m.get("memberNameEn", "")) for m in members]

        # Find geography dimension — look for Canada, Toronto, Vancouver, Calgary
        geo_dim_idx = None
        for i, members in dim_map.items():
            names = [n.lower() for _, n in members]
            if any("canada" in n or "toronto" in n or "vancouver" in n for n in names):
                geo_dim_idx = i
                break

        # Find variable dimension — look for starts, under construction, completions
        var_dim_idx = None
        for i, members in dim_map.items():
            names = [n.lower() for _, n in members]
            if any("starts" in n or "under construction" in n or "completion" in n for n in names):
                var_dim_idx = i
                break

        log(f"Geo dimension index: {geo_dim_idx}")
        if geo_dim_idx is not None:
            log("Geography members:")
            for mid, name in dim_map[geo_dim_idx]:
                log(f"  [{mid}] {name}")
        log()
        log(f"Variable dimension index: {var_dim_idx}")
        if var_dim_idx is not None:
            log("Variable members:")
            for mid, name in dim_map[var_dim_idx]:
                log(f"  [{mid}] {name}")
        log()

        # Now probe getSeriesInfoFromCubePidCoord for key combos
        # Get all dimension member ID sets for building coordinates
        # Coord string format: memberId_dim1.memberId_dim2. ... (one per dimension in order)
        # For under construction (all Canada) + regional starts
        if geo_dim_idx is not None and var_dim_idx is not None:
            geo_members = dim_map[geo_dim_idx]
            var_members = dim_map[var_dim_idx]

            # Find Canada geo member
            canada_id = next((mid for mid, nm in geo_members if "canada" in nm.lower() and "outside" not in nm.lower()), None)
            toronto_id = next((mid for mid, nm in geo_members if "toronto" in nm.lower()), None)
            vancouver_id = next((mid for mid, nm in geo_members if "vancouver" in nm.lower()), None)
            calgary_id = next((mid for mid, nm in geo_members if "calgary" in nm.lower()), None)

            # Find under-construction and starts variable members
            starts_id = next((mid for mid, nm in var_members if "starts" in nm.lower()), None)
            uc_id = next((mid for mid, nm in var_members if "under construction" in nm.lower()), None)

            log(f"canada_id={canada_id}, toronto_id={toronto_id}, vancouver_id={vancouver_id}, calgary_id={calgary_id}")
            log(f"starts_id={starts_id}, uc_id={uc_id}")
            log()

            # Probe with these IDs — need to fill in all dimension member IDs
            # Get "Total" for any type dimension
            type_dim_members = [(i, dim_map[i]) for i in dim_map if i != geo_dim_idx and i != var_dim_idx]
            log("Other dimensions:")
            for i, members in type_dim_members:
                nm = dims2[i].get("dimensionNameEn", f"dim{i}")
                log(f"  Dim {i+1} ({nm}):")
                for mid, name in members:
                    log(f"    [{mid}] {name}")
            log()

            # Build full coordinate vectors for probe
            # Coord order: dim1_memberId.dim2_memberId.dim3_memberId
            num_dims = len(dims2)
            probe_combos = []

            # For each "other" dimension, pick the first member (often "Total")
            default_others = {}
            for i in range(num_dims):
                if i not in (geo_dim_idx, var_dim_idx):
                    default_others[i] = dim_map[i][0][0]  # first member

            # Build coord strings for: Canada starts, Canada under-construction, CMA starts
            target_specs = [
                (canada_id, starts_id, "Canada starts"),
                (canada_id, uc_id, "Canada under-construction"),
                (toronto_id, starts_id, "Toronto starts"),
                (vancouver_id, starts_id, "Vancouver starts"),
                (calgary_id, starts_id, "Calgary starts"),
            ]

            for geo_id, var_id, label in target_specs:
                if not geo_id or not var_id:
                    log(f"  SKIP {label}: missing member ID (geo={geo_id}, var={var_id})")
                    continue
                coords = {}
                coords[geo_dim_idx] = geo_id
                coords[var_dim_idx] = var_id
                coords.update(default_others)
                coord_str = ".".join(coords[i] for i in range(num_dims))
                probe_url = f"https://www150.statcan.gc.ca/t1/wds/rest/getSeriesInfoFromCubePidCoord/{PRODUCT_ID}/{coord_str}"
                try:
                    pr = requests.get(probe_url, timeout=15)
                    if pr.status_code == 200:
                        presp = pr.json()
                        if isinstance(presp, list) and presp:
                            pobj = presp[0].get("object", {})
                            pvid = pobj.get("vectorId") or pobj.get("VectorId")
                            ptitle = pobj.get("SeriesTitleEn") or pobj.get("seriesTitleEn") or "?"
                        elif isinstance(presp, dict):
                            pobj = presp.get("object", {})
                            pvid = pobj.get("vectorId") or pobj.get("VectorId")
                            ptitle = pobj.get("SeriesTitleEn") or pobj.get("seriesTitleEn") or "?"
                        else:
                            pvid, ptitle = "?", "?"
                        log(f"  {label}: coord={coord_str} → v{pvid}: {ptitle}")
                    else:
                        log(f"  {label}: HTTP {pr.status_code} for coord={coord_str}")
                except Exception as e:
                    log(f"  {label}: ERROR {e}")

except Exception as e:
    log(f"ERROR in coord probe: {e}")
log()


# ── Write report ────────────────────────────────────────────────────────────────

report = "\n".join(lines)
OUT.write_text(report, encoding="utf-8")
print(f"\nReport written to {OUT}")
