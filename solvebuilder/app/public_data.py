"""Public data: download, cache locally, query offline.

What each source gives you (plain language):
  GNIS      The federal list of every officially named place — creeks, springs,
            arches, passes, summits — with a type, county and coordinates. This is
            the record a feature has to appear in before it counts as real here.
  EPQS      USGS elevation for a single point (feet).
  PAD-US    The federal protected-areas database: who manages a piece of land and
            whether the public may enter. Answers "public or private?" for a point.
  OSM       OpenStreetMap roads and trails near a point, with surface and track
            grade where mapped — a proxy for "does a normal car get close?".
  TopoView  Links into the USGS historical topographic map archive for a point, so
            you can see what a feature was called on the 1900–1960 sheets.
  MVUM      Forest Service and BLM travel maps (road class / seasonal closures).
            Too large to download blind; the tool gives you the exact link.

Everything fetched is cached in SQLite so it works in the field without signal.
"""
import csv
import io
import json
import re
import time
import urllib.parse
import urllib.request
import zipfile

from . import geo, store

UA = {"User-Agent": "solvebuilder/1.0 (personal research tool)"}
GNIS_URL = "https://prd-tnm.s3.amazonaws.com/StagedProducts/GeographicNames/DomesticNames/DomesticNames_{st}_Text.zip"
EPQS_URL = "https://epqs.nationalmap.gov/v1/json?x={lon}&y={lat}&units=Feet&wkid=4326&includeDate=false"
PADUS_URL = "https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/PADUS4_0_Fee_Designation_Easement/FeatureServer/0/query"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
TOPOVIEW = "https://ngmdb.usgs.gov/topoview/viewer/#12/{lat}/{lon}"
MVUM_LINKS = {"Forest Service Interactive Visitor Map": "https://www.fs.usda.gov/ivm/", "FS MVUM data (EDW)": "https://data.fs.usda.gov/geodata/edw/datasets.php?xmlKeyword=Motor+Vehicle+Use+Map", "BLM Travel & Transportation": "https://www.blm.gov/programs/recreation/travel-and-transportation-management"}

store.db().executescript("""
CREATE TABLE IF NOT EXISTS gnis (feature_id TEXT PRIMARY KEY, name TEXT, fclass TEXT, state TEXT, county TEXT, lat REAL, lon REAL, map_name TEXT, elev INTEGER);
CREATE INDEX IF NOT EXISTS gnis_state ON gnis(state);
CREATE INDEX IF NOT EXISTS gnis_class ON gnis(fclass);
CREATE INDEX IF NOT EXISTS gnis_name ON gnis(name);
""")
store.db().commit()


def _get(url, timeout=60, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def cached(key, ttl_days=365):
    r = store.row("SELECT value, ts FROM cache WHERE key=?", (key,))
    if r and time.time() - r["ts"] < ttl_days * 86400:
        return store.unj(r["value"])
    return None


def put_cache(key, value):
    store.upsert("cache", {"key": key, "value": store.j(value), "ts": time.time()})


# ---------------------------------------------------------------- GNIS

def fetch_gnis(state, progress=print):
    st = state.upper()
    url = GNIS_URL.format(st=st)
    progress(f"GNIS {st}: downloading {url}")
    blob = _get(url, timeout=300)
    z = zipfile.ZipFile(io.BytesIO(blob))
    name = next(n for n in z.namelist() if n.lower().endswith(".txt"))
    text = z.read(name).decode("utf-8", "replace")
    rdr = csv.reader(io.StringIO(text), delimiter="|")
    header = [h.strip().lower() for h in next(rdr)]

    def col(*names):
        for n in names:
            if n in header:
                return header.index(n)
        return None
    ci, cn, cc, cst, cco, clat, clon, cmap, celev = col("feature_id"), col("feature_name"), col("feature_class"), col("state_name", "state_alpha"), col("county_name"), col("prim_lat_dec"), col("prim_long_dec"), col("map_name"), col("elev_in_ft")
    if None in (ci, cn, cc, clat, clon):
        raise RuntimeError(f"GNIS file layout not recognised; header was {header[:12]}")
    rows_ = []
    for r in rdr:
        try:
            lat, lon = float(r[clat]), float(r[clon])
        except Exception:
            continue
        elev = None
        if celev is not None:
            try:
                elev = int(float(r[celev]))
            except Exception:
                pass
        rows_.append((r[ci], r[cn], r[cc], st, r[cco] if cco is not None else "", lat, lon, r[cmap] if cmap is not None else "", elev))
    store.run("DELETE FROM gnis WHERE state=?", (st,))
    store.runmany("INSERT OR REPLACE INTO gnis VALUES (?,?,?,?,?,?,?,?,?)", rows_)
    put_cache("gnis_" + st, {"count": len(rows_), "ts": time.time()})
    progress(f"GNIS {st}: {len(rows_)} named features stored")
    return len(rows_)


def gnis_status():
    return {r["state"]: r["n"] for r in store.rows("SELECT state, COUNT(*) n FROM gnis GROUP BY state")}


# GNIS classes that answer the poem's feature questions
CLASS_FOR = {
    "arch": ["Arch"], "waterfall": ["Falls"], "hotspring": ["Spring"], "spring": ["Spring"], "rock": ["Pillar", "Ridge", "Cliff", "Summit", "Rock"], "cirque": ["Basin", "Valley", "Cirque"],
    "pass": ["Gap"], "gate": ["Gap", "Canyon"], "bend": ["Bend"], "confluence": ["Stream"], "face": ["Summit"], "pool": ["Lake", "Reservoir"], "hole": ["Basin", "Valley", "Bay", "Arch", "Cave"], "peak": ["Summit"], "lake": ["Lake"], "river": ["Stream"], "pair": ["Summit", "Lake", "Pillar"],
}


def gnis_query(state=None, fclass=None, name_like=None, center=None, radius_mi=None, limit=300):
    sql, args = "SELECT * FROM gnis WHERE 1=1", []
    if state:
        sql += " AND state=?"
        args.append(state.upper())
    if fclass:
        cls = CLASS_FOR.get(fclass, [fclass])
        sql += " AND (" + " OR ".join("fclass=?" for _ in cls) + ")"
        args += cls
    if name_like:
        sql += " AND lower(name) LIKE ?"
        args.append(f"%{name_like.lower()}%")
    if center and radius_mi:
        dlat = radius_mi / 69.0
        dlon = radius_mi / (69.0 * max(0.2, abs(__import__('math').cos(__import__('math').radians(center[0])))))
        sql += " AND lat BETWEEN ? AND ? AND lon BETWEEN ? AND ?"
        args += [center[0] - dlat, center[0] + dlat, center[1] - dlon, center[1] + dlon]
    out = store.rows(sql + " LIMIT ?", args + [limit * 3])
    if center:
        for r in out:
            r["dist_mi"] = round(geo.haversine(center, (r["lat"], r["lon"])), 1)
        out = [r for r in out if radius_mi is None or r["dist_mi"] <= radius_mi]
        out.sort(key=lambda r: r["dist_mi"])
    return out[:limit]


def verify_features(progress=print):
    """Mark built-in and imported features as GNIS-verified when a same-named
    feature exists within 3 miles in the cached GNIS for that state."""
    have = gnis_status()
    n_ok = n_missing = n_skipped = 0
    for f in store.rows("SELECT * FROM features"):
        if f["state"] not in have:
            n_skipped += 1
            continue
        base = re.sub(r"\s*\(.*?\)", "", f["name"]).strip()
        cands = gnis_query(state=f["state"], name_like=base.split(",")[0][:24], center=(f["lat"], f["lon"]), radius_mi=3, limit=5)
        if cands:
            store.run("UPDATE features SET gnis_verified=1, tier=CASE WHEN tier='unverified' THEN 'reported' ELSE tier END WHERE id=?", (f["id"],))
            n_ok += 1
        else:
            store.run("UPDATE features SET gnis_verified=-1 WHERE id=?", (f["id"],))
            n_missing += 1
    progress(f"verify: {n_ok} found in GNIS, {n_missing} NOT found (shown as gaps), {n_skipped} skipped (state not downloaded)")
    return {"verified": n_ok, "missing": n_missing, "skipped": n_skipped}


# ---------------------------------------------------------------- per-point lookups (cached)

def elevation(lat, lon):
    key = f"elev_{lat:.4f}_{lon:.4f}"
    c = cached(key)
    if c is not None:
        return c
    try:
        d = json.loads(_get(EPQS_URL.format(lat=lat, lon=lon), timeout=20))
        v = d.get("value")
        out = {"feet": round(float(v)) if v not in (None, "-1000000") else None, "source": "USGS EPQS", "ts": time.time()}
    except Exception as e:
        out = {"feet": None, "error": str(e)[:120], "source": "USGS EPQS (failed)"}
        return out
    put_cache(key, out)
    return out


def land_owner(lat, lon):
    key = f"padus_{lat:.4f}_{lon:.4f}"
    c = cached(key)
    if c is not None:
        return c
    q = {"geometry": f"{lon},{lat}", "geometryType": "esriGeometryPoint", "inSR": "4326", "spatialRel": "esriSpatialRelIntersects", "outFields": "Mang_Name,Mang_Type,Unit_Nm,Pub_Access,Des_Tp,Own_Type", "returnGeometry": "false", "f": "json"}
    try:
        d = json.loads(_get(PADUS_URL + "?" + urllib.parse.urlencode(q), timeout=30))
        feats = d.get("features") or []
        if not feats:
            out = {"owner": "not in PAD-US (likely private or unrecorded)", "public_access": "unknown", "units": [], "source": "PAD-US 4.0", "ts": time.time()}
        else:
            a = feats[0]["attributes"]
            out = {"owner": a.get("Mang_Name") or a.get("Own_Type"), "type": a.get("Mang_Type"), "unit": a.get("Unit_Nm"), "designation": a.get("Des_Tp"), "public_access": a.get("Pub_Access"), "units": [f["attributes"].get("Unit_Nm") for f in feats], "source": "PAD-US 4.0", "ts": time.time()}
    except Exception as e:
        return {"owner": None, "error": str(e)[:160], "source": "PAD-US (failed — service URL may have changed; edit PADUS_URL in public_data.py)"}
    put_cache(key, out)
    return out


def osm_nearby(lat, lon, radius_m=1600):
    key = f"osm_{lat:.3f}_{lon:.3f}_{radius_m}"
    c = cached(key)
    if c is not None:
        return c
    ql = f"""[out:json][timeout:40];(way(around:{radius_m},{lat},{lon})[highway];node(around:{radius_m},{lat},{lon})[natural~"^(waterfall|spring|hot_spring|arch|saddle|peak|cave_entrance|rock|stone)$"];);out tags center;"""
    try:
        d = json.loads(_get(OVERPASS_URL, timeout=60, data=urllib.parse.urlencode({"data": ql}).encode()))
        roads, feats = [], []
        for el in d.get("elements", []):
            t = el.get("tags", {})
            if "highway" in t:
                roads.append({"highway": t.get("highway"), "name": t.get("name"), "surface": t.get("surface"), "tracktype": t.get("tracktype"), "smoothness": t.get("smoothness"), "access": t.get("access")})
            elif "natural" in t:
                feats.append({"natural": t.get("natural"), "name": t.get("name"), "lat": el.get("lat"), "lon": el.get("lon")})
        car = "paved or good gravel road within a mile" if any(r["highway"] in ("primary", "secondary", "tertiary", "residential", "unclassified") or r.get("surface") in ("asphalt", "paved", "gravel", "compacted") for r in roads) else ("track only — check tracktype" if roads else "no mapped road within a mile")
        out = {"roads": roads[:40], "features": feats[:40], "car": car, "source": "OpenStreetMap via Overpass", "ts": time.time()}
    except Exception as e:
        return {"roads": [], "features": [], "car": "unknown", "error": str(e)[:160], "source": "OSM (failed)"}
    put_cache(key, out)
    return out


def point_report(lat, lon):
    return {"elevation": elevation(lat, lon), "land": land_owner(lat, lon), "osm": osm_nearby(lat, lon), "topoview": TOPOVIEW.format(lat=lat, lon=lon), "mvum": MVUM_LINKS, "gnis_nearby": gnis_query(center=(lat, lon), radius_mi=2, limit=40)}


def fetch_all(states, progress=print):
    out = {}
    for st in states:
        try:
            out[st] = fetch_gnis(st, progress)
        except Exception as e:
            out[st] = f"failed: {e}"
            progress(f"GNIS {st}: FAILED — {e}")
    out["verify"] = verify_features(progress)
    return out
