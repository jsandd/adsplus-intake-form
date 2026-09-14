"""Line and point layers in data/vectors.sqlite (EPSG:5070) with one R-tree.
Layers: road, trail, rail (USGS National Transportation Dataset, per state),
cemetery, cave, mine (USGS GNIS, per state), water (USGS NHD, per state, step 3),
building (USGS Structures or OSM, step 3)."""
import csv
import io
import json
import os
import sqlite3
import threading
import urllib.request
import zipfile

import shapely
from shapely import wkb as swkb
from shapely.geometry import Point

from . import config, geo

_lock = threading.Lock()
_conn = None
LAYERS = ["road", "trail", "rail", "cemetery", "cave", "mine", "building", "water"]
# USGS NTD road classes worth treating as passable by a low-clearance car. 'surface' is not in NTD; OSM adds it.
ROAD_CLASS = {"1": "controlled access", "2": "secondary highway", "3": "local connector", "4": "local road", "5": "ramp", "6": "4WD / high clearance", "7": "ferry", "8": "tunnel", "9": "other"}


def _db():
    global _conn
    with _lock:
        if _conn is None:
            os.makedirs(config.DATA, exist_ok=True)
            _conn = sqlite3.connect(config.VEC_DB, check_same_thread=False)
            _conn.execute("CREATE TABLE IF NOT EXISTS feat(id INTEGER PRIMARY KEY, layer TEXT, state TEXT, attrs TEXT, wkb BLOB)")
            _conn.execute("CREATE INDEX IF NOT EXISTS feat_layer ON feat(layer)")
            _conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS feat_rt USING rtree(id, minx, maxx, miny, maxy)")
            _conn.execute("CREATE TABLE IF NOT EXISTS loaded(layer TEXT, state TEXT, n INTEGER, source TEXT, PRIMARY KEY(layer, state))")
        return _conn


def coverage():
    c = _db()
    rows = c.execute("SELECT layer, state, n, source FROM loaded").fetchall()
    out = {}
    for layer, st, n, src in rows:
        out.setdefault(layer, {})[st] = {"n": n, "source": src}
    return out


def _insert(layer, state, rows, source):
    c = _db(); cur = c.cursor()
    cur.execute("DELETE FROM feat_rt WHERE id IN (SELECT id FROM feat WHERE layer=? AND state=?)", (layer, state))
    cur.execute("DELETE FROM feat WHERE layer=? AND state=?", (layer, state))
    for attrs, g in rows:
        b = g.bounds
        cur.execute("INSERT INTO feat(layer, state, attrs, wkb) VALUES (?,?,?,?)", (layer, state, json.dumps(attrs, default=str), shapely.to_wkb(g)))
        cur.execute("INSERT INTO feat_rt VALUES (?,?,?,?,?)", (cur.lastrowid, b[0], b[2], b[1], b[3]))
    cur.execute("INSERT OR REPLACE INTO loaded VALUES (?,?,?,?)", (layer, state, len(rows), source))
    c.commit()


def _download(url, dest, log):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.exists(dest) and os.path.getsize(dest) > 1000:
        return dest
    log(f"  downloading {os.path.basename(dest)}…")
    urllib.request.urlretrieve(url, dest + ".part")
    os.replace(dest + ".part", dest)
    return dest


def ingest_tran(state, log=print):
    """USGS National Transportation Dataset: roads, trails, railroads for one state."""
    from pyogrio.raw import read as _read
    name = config.STATES[state][0].split(" (")[0]
    url = f"{config.TNM}Tran/Shape/TRAN_{name.replace(' ', '_')}_State_Shape.zip"
    z = _download(url, os.path.join(config.DATA, "tran", f"TRAN_{state}.zip"), log)
    with zipfile.ZipFile(z) as zf:
        names = zf.namelist()
    from pyproj import Transformer, CRS
    import numpy as np
    def read(pattern):
        shp = [n for n in names if n.lower().endswith(".shp") and pattern in n]
        if not shp:
            return None
        meta, index, geoms, fields = _read(f"zip://{z}!{shp[0]}")
        src = CRS.from_user_input(meta["crs"]) if meta.get("crs") else CRS.from_epsg(4326)
        tf = None if src.to_epsg() == 5070 else Transformer.from_crs(src, "EPSG:5070", always_xy=True)
        return meta, geoms, fields, tf
    for layer, pattern, keep in [("road", "Trans_RoadSegment", ["tnmfrc", "name", "mtfcc_code", "tnmfrc_code"]), ("trail", "Trans_TrailSegment", ["name", "trailtype", "hikerpedestrian", "trail_type"]), ("rail", "Trans_RailFeature", ["name", "rail_type", "railroad_o"])]:
        log(f"  {state} {layer}: reading…")
        r = read(pattern)
        if r is None:
            log(f"    no {pattern} in the zip"); continue
        meta, geoms, fields, tf = r
        fnames = list(meta["fields"]); cols = [k for k in fnames if k.lower() in keep]
        rows = []
        for i in range(len(geoms)):
            if geoms[i] is None:
                continue
            g = shapely.from_wkb(geoms[i])
            if g is None or g.is_empty:
                continue
            if tf is not None:
                g = shapely.transform(g, lambda a: np.column_stack(tf.transform(a[:, 0], a[:, 1])))
            attrs = {}
            for k in cols:
                v = fields[fnames.index(k)][i]
                attrs[k.lower()] = None if v is None or (isinstance(v, float) and v != v) else (v.item() if hasattr(v, "item") else v)
            if layer == "road":
                frc = str(attrs.get("tnmfrc") or attrs.get("tnmfrc_code") or "")
                attrs["class"] = ROAD_CLASS.get(frc, frc)
                attrs["low_clearance"] = frc not in ("6", "7", "8")
            rows.append((attrs, g))
        _insert(layer, state, rows, "USGS NTD")
        log(f"    {len(rows)} features")


def ingest_gnis(state, log=print):
    """USGS GNIS domestic names: cemeteries, caves, mines as points."""
    url = f"{config.TNM}GeographicNames/DomesticNames/DomesticNames_{state}_Text.zip"
    z = _download(url, os.path.join(config.DATA, "gnis", f"GNIS_{state}.zip"), log)
    want = {"Cemetery": "cemetery", "Cave": "cave", "Mine": "mine"}
    rows = {v: [] for v in want.values()}
    with zipfile.ZipFile(z) as zf:
        txt = [n for n in zf.namelist() if n.lower().endswith(".txt")][0]
        with zf.open(txt) as f:
            rd = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8", errors="replace"), delimiter="|")
            for r in rd:
                cls = r.get("feature_class") or r.get("FEATURE_CLASS")
                if cls not in want:
                    continue
                try:
                    lat = float(r.get("prim_lat_dec") or r.get("PRIM_LAT_DEC")); lon = float(r.get("prim_long_dec") or r.get("PRIM_LONG_DEC"))
                except Exception:
                    continue
                x, y = geo.to_m(lon, lat)
                rows[want[cls]].append(({"name": r.get("feature_name") or r.get("FEATURE_NAME"), "class": cls}, Point(x, y)))
    for layer, rs in rows.items():
        _insert(layer, state, rs, "USGS GNIS")
        log(f"  {state} {layer}: {len(rs)} points")


def nearest(layer, lat, lon, max_m=8000, where=None):
    """Nearest feature of a layer within max_m metres: (distance_m, attrs) or (None, None)."""
    c = _db()
    x, y = geo.to_m(lon, lat)
    p = Point(x, y)
    best = (None, None)
    r = 500.0
    while r <= max_m:
        ids = c.execute("SELECT f.id, f.attrs, f.wkb FROM feat_rt r JOIN feat f ON f.id=r.id WHERE f.layer=? AND r.minx<=? AND r.maxx>=? AND r.miny<=? AND r.maxy>=?", (layer, x + r, x - r, y + r, y - r)).fetchall()
        for i, attrs, wkb in ids:
            a = json.loads(attrs)
            if where and not where(a):
                continue
            d = swkb.loads(wkb).distance(p)
            if best[0] is None or d < best[0]:
                best = (d, a)
        if best[0] is not None and best[0] <= r:
            return best
        r *= 3
    return best


def contains(layer, lat, lon):
    c = _db()
    x, y = geo.to_m(lon, lat); p = Point(x, y)
    for i, attrs, wkb in c.execute("SELECT f.id, f.attrs, f.wkb FROM feat_rt r JOIN feat f ON f.id=r.id WHERE f.layer=? AND r.minx<=? AND r.maxx>=? AND r.miny<=? AND r.maxy>=?", (layer, x, x, y, y)).fetchall():
        if swkb.loads(wkb).contains(p):
            return json.loads(attrs)
    return None


def features_in(layer, bbox_m):
    """Geometries of a layer intersecting a projected box (for regional render)."""
    c = _db()
    x0, y0, x1, y1 = bbox_m
    rows = c.execute("SELECT f.wkb, f.attrs FROM feat_rt r JOIN feat f ON f.id=r.id WHERE f.layer=? AND r.minx<=? AND r.maxx>=? AND r.miny<=? AND r.maxy>=?", (layer, x1, x0, y1, y0)).fetchall()
    return [(swkb.loads(w), json.loads(a)) for w, a in rows]


def states_for(lat, lon):
    """All state bboxes containing the point (bboxes overlap; PAD-US gives the exact state when loaded)."""
    return [st for st, (name, b) in config.STATES.items() if st not in ("CO", "OR") and b[0] <= lon <= b[2] and b[1] <= lat <= b[3]]


def state_for(lat, lon):
    s = states_for(lat, lon)
    return "/".join(s) if s else None


def loaded_here(layer, lat, lon):
    cov = coverage().get(layer, {})
    return any(st in cov for st in states_for(lat, lon))
