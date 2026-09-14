"""PAD-US (USGS Protected Areas Database) → data/padus.sqlite.
You download the GeoPackage yourself (the USGS host is not reachable from every network);
this reads the Fee, Designation and Easement layers into one table with an R-tree in EPSG:5070.

Fields used: Own_Type, Own_Name, Mang_Type, Mang_Name, Unit_Nm, Des_Tp, Pub_Access, GAP_Sts, State_Nm.
PAD-US has no entry-fee field. Fee status here is inferred: national parks and monuments run by NPS
are marked 'likely fee', state parks 'check', everything else 'no fee recorded'."""
import json
import os
import sqlite3
import threading

from shapely import wkb as swkb
from shapely.geometry import Point

from . import config, geo

_lock = threading.Lock()
_conn = None
KEEP = ["Own_Type", "Own_Name", "Mang_Type", "Mang_Name", "Unit_Nm", "Des_Tp", "Pub_Access", "GAP_Sts", "State_Nm", "Loc_Own", "Loc_Mang", "Category"]
DES = {"NP": "National Park", "NM": "National Monument", "NRA": "National Recreation Area", "NF": "National Forest", "NG": "National Grassland", "WA": "Wilderness Area", "WSA": "Wilderness Study Area", "NWR": "National Wildlife Refuge", "SP": "State Park", "SW": "State Wilderness", "SRMA": "Special Recreation Management Area", "ACEC": "Area of Critical Environmental Concern", "PUB": "Public Land (unknown designation)", "LP": "Local Park", "PROC": "Proclamation", "IRA": "Inventoried Roadless Area", "NLCS": "National Conservation Lands", "TRIBL": "Tribal land", "MIL": "Military", "ACC": "Access Area", "REC": "Recreation Area", "HCA": "Historic or Cultural Area", "CONE": "Conservation Easement", "OTHE": "Other", "UNK": "Unknown"}
OWN = {"FED": "Federal", "STAT": "State", "LOC": "Local government", "DIST": "Regional agency", "TRIB": "Tribal", "PVT": "Private", "NGO": "Non-profit", "JNT": "Joint", "UNK": "Unknown", "TERR": "Territorial", "UNKL": "Unknown local"}
ACCESS = {"OA": "Open access", "RA": "Restricted access", "XA": "Closed to public", "UK": "Unknown"}


def _db():
    global _conn
    with _lock:
        if _conn is None:
            os.makedirs(config.DATA, exist_ok=True)
            _conn = sqlite3.connect(config.PADUS_DB, check_same_thread=False)
            _conn.execute("CREATE TABLE IF NOT EXISTS units(id INTEGER PRIMARY KEY, layer TEXT, attrs TEXT, wkb BLOB)")
            _conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS units_rt USING rtree(id, minx, maxx, miny, maxy)")
            _conn.execute("CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT)")
        return _conn


def loaded():
    c = _db()
    n = c.execute("SELECT COUNT(*) FROM units").fetchone()[0]
    src = c.execute("SELECT v FROM meta WHERE k='source'").fetchone()
    return {"units": n, "source": src[0] if src else None}


def ingest(path, log=print):
    import pyogrio
    from pyogrio.raw import read as _read
    import shapely
    path = os.path.abspath(path)
    if not os.path.exists(path):
        cands = [f for f in os.listdir(config.DATA) if f.lower().endswith((".gpkg", ".zip", ".gdb"))] if os.path.isdir(config.DATA) else []
        raise RuntimeError(f"file not found: {path}. Save the PAD-US GeoPackage (or the .zip it came in) in the data folder as padus.gpkg. Files there now: {', '.join(cands) or 'none'}")
    if path.lower().endswith(".zip"):
        import zipfile
        inner = [n for n in zipfile.ZipFile(path).namelist() if n.lower().endswith(".gpkg")]
        if not inner:
            raise RuntimeError("that zip has no .gpkg inside it")
        path = f"zip://{path}!{inner[0]}"
        log(f"reading {inner[0]} inside the zip")
    try:
        layers = [l[0] for l in pyogrio.list_layers(path)]
    except Exception as e:
        raise RuntimeError(f"could not open {os.path.basename(path)} as a GeoPackage: {e}")
    log(f"PAD-US layers in {os.path.basename(path)}: {', '.join(layers)}")
    wanted = [l for l in layers if any(k in l for k in ("Fee", "Designation", "Easement")) and "Combined" not in l] or layers
    c = _db()
    c.execute("DELETE FROM units"); c.execute("DELETE FROM units_rt"); c.commit()
    lon0, lat0, lon1, lat1 = config.MAP_EXTENT
    n = 0
    from pyproj import Transformer, CRS
    for layer in wanted:
        log(f"  reading {layer} inside the map extent…")
        try:
            meta, index, geoms, fields = _read(path, layer=layer, bbox=(lon0, lat0, lon1, lat1))
        except Exception as e:
            log(f"    skipped ({e})"); continue
        names = list(meta["fields"]); cols = [k for k in KEEP if k in names]
        src = CRS.from_user_input(meta["crs"]) if meta.get("crs") else CRS.from_epsg(4326)
        tf = None if src.to_epsg() == 5070 else Transformer.from_crs(src, "EPSG:5070", always_xy=True)
        rows = []
        for i in range(len(geoms)):
            if geoms[i] is None:
                continue
            g = shapely.from_wkb(geoms[i])
            if g is None or g.is_empty:
                continue
            if tf is not None:
                g = shapely.transform(g, lambda a: __import__("numpy").column_stack(tf.transform(a[:, 0], a[:, 1])))
            attrs = {}
            for k in cols:
                v = fields[names.index(k)][i]
                attrs[k] = None if v is None or (isinstance(v, float) and v != v) else (v.item() if hasattr(v, "item") else v)
            b = g.bounds
            rows.append((layer, json.dumps(attrs, default=str), shapely.to_wkb(g), b))
        cur = c.cursor()
        for layer_, attrs, wkb, b in rows:
            cur.execute("INSERT INTO units(layer, attrs, wkb) VALUES (?,?,?)", (layer_, attrs, wkb))
            cur.execute("INSERT INTO units_rt VALUES (?,?,?,?,?)", (cur.lastrowid, b[0], b[2], b[1], b[3]))
        c.commit(); n += len(rows)
        log(f"    {len(rows)} units")
    c.execute("INSERT OR REPLACE INTO meta VALUES ('source', ?)", (os.path.basename(path),)); c.commit()
    log(f"PAD-US loaded: {n} units")


def query(lat, lon):
    """All PAD-US units containing the point, most specific first, plus a derived summary."""
    c = _db()
    x, y = geo.to_m(lon, lat)
    ids = c.execute("SELECT id FROM units_rt WHERE minx<=? AND maxx>=? AND miny<=? AND maxy>=?", (x, x, y, y)).fetchall()
    p = Point(x, y)
    hits = []
    for (i,) in ids:
        layer, attrs, wkb = c.execute("SELECT layer, attrs, wkb FROM units WHERE id=?", (i,)).fetchone()
        g = swkb.loads(wkb)
        if g.contains(p):
            a = json.loads(attrs); a["_layer"] = layer; a["_area_km2"] = g.area / 1e6
            hits.append(a)
    hits.sort(key=lambda a: a["_area_km2"])
    return hits, summarize(hits)


def summarize(hits):
    if not hits:
        return {"in_padus": False, "owner": "No PAD-US unit here (most such land is private)", "access": "unknown", "access_code": None, "fee": "unknown", "designation": None, "dogs": "unknown", "state": None}
    fee_units = [h for h in hits if "Fee" in h["_layer"]] or hits
    f = fee_units[0]
    des = [h for h in hits if h.get("Des_Tp")]
    des_codes = [h["Des_Tp"] for h in des]
    des_names = [f"{DES.get(h['Des_Tp'], h['Des_Tp'])}: {h.get('Unit_Nm') or ''}".strip(": ") for h in des]
    access_code = f.get("Pub_Access") or (des[0].get("Pub_Access") if des else None)
    nps = any((h.get("Mang_Name") == "NPS") or (h.get("Mang_Type") == "FED" and h.get("Des_Tp") in ("NP", "NM") and (h.get("Mang_Name") in ("NPS", None))) for h in hits)
    fee = "likely fee (NPS unit)" if nps else ("check: state park" if "SP" in des_codes else "no fee recorded")
    dogs = "usually barred from trails (NPS)" if nps else "allowed on most federal and state land (verify)"
    return {"in_padus": True, "owner": f"{OWN.get(f.get('Own_Type'), f.get('Own_Type'))} · {f.get('Own_Name') or f.get('Loc_Own') or ''}".strip(" ·"), "manager": f"{f.get('Mang_Name') or f.get('Loc_Mang') or ''}", "unit": f.get("Unit_Nm"), "access": ACCESS.get(access_code, "unknown"), "access_code": access_code, "fee": fee, "designation": "; ".join(des_names) if des_names else None, "dogs": dogs, "state": f.get("State_Nm"), "private": f.get("Own_Type") == "PVT"}
