"""Regional render: rasterize a lon/lat box at ~30 m (downsampled to stay under a cell cap),
apply every enabled rule, paint an RGBA PNG and count surviving square miles."""
import base64
import io
import struct
import zlib

import numpy as np
import shapely
from shapely.strtree import STRtree

from . import config, dem, geo, padus, vectors


def _png(rgba):
    h, w, _ = rgba.shape
    raw = b"".join(b"\x00" + rgba[y].tobytes() for y in range(h))
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b"")


def render(bbox, rules, max_cells=250_000):
    lon0, lat0, lon1, lat1 = bbox
    P = {r["id"]: r for r in rules if r["on"]}
    dw = dem.window(bbox, max_cells)
    if dw is None:
        return {"error": "elevation tiles for this box are not downloaded yet; use the Data panel or click inside the box once"}
    elev, slope, lons, lats = dw
    H, W = elev.shape
    ft = geo.FT
    # cell centres in metres
    LON, LAT = np.meshgrid(lons, lats)
    X, Y = geo._to5070.transform(LON.ravel(), LAT.ravel())
    X = np.asarray(X); Y = np.asarray(Y)
    pts = shapely.points(X, Y)
    kill = np.zeros(H * W, bool); flag = np.zeros(H * W, bool); unknown = np.zeros(H * W, bool)
    counts = {}
    def apply(rid, failed, unk=None):
        if rid not in P:
            return
        f = failed.ravel() if hasattr(failed, "ravel") else failed
        counts[rid] = int(f.sum())
        if P[rid]["severity"] == "kill":
            kill[:] |= f
        else:
            flag[:] |= f
        if unk is not None:
            unknown[:] |= unk
    e_ft = elev * ft
    apply("r_elev", e_ft.ravel() >= float(P.get("r_elev", {"param": 1e9})["param"]))
    apply("r_slope", np.nan_to_num(slope.ravel(), nan=0) > float(P.get("r_slope", {"param": 90})["param"]))
    # state elimination
    co = np.array([geo.point_in_poly(a, b, config.COLORADO) or geo.point_in_poly(a, b, config.OREGON) for a, b in zip(LON.ravel(), LAT.ravel())])
    apply("r_state", co)
    # PAD-US
    bm = (X.min(), Y.min(), X.max(), Y.max())
    if padus.loaded()["units"] and ("r_public" in P or "r_free" in P or "r_dog" in P):
        c = padus._db()
        rows = c.execute("SELECT f.wkb, f.attrs FROM units_rt r JOIN units f ON f.id=r.id WHERE r.minx<=? AND r.maxx>=? AND r.miny<=? AND r.maxy>=?", (bm[2], bm[0], bm[3], bm[1])).fetchall()
        import json
        geoms = [shapely.from_wkb(w) for w, _ in rows]; attrs = [json.loads(a) for _, a in rows]
        public = np.zeros(H * W, bool); closed = np.zeros(H * W, bool); nps = np.zeros(H * W, bool); private = np.zeros(H * W, bool)
        for g, a in zip(geoms, attrs):
            inside = shapely.contains_xy(g, X, Y)
            if a.get("Own_Type") == "PVT":
                private |= inside
            elif a.get("Pub_Access") == "XA":
                closed |= inside
            else:
                public |= inside
            if a.get("Mang_Name") == "NPS" or (a.get("Des_Tp") in ("NP", "NM") and a.get("Mang_Type") == "FED"):
                nps |= inside
        apply("r_public", (~public) | closed | private)
        apply("r_free", nps)
        apply("r_dog", nps)
    else:
        for rid in ("r_public", "r_free", "r_dog"):
            if rid in P:
                unknown[:] = True
    # distance layers
    def dist_layer(layer, where=None):
        feats = vectors.features_in(layer, (bm[0] - 3000, bm[1] - 3000, bm[2] + 3000, bm[3] + 3000))
        gs = [g for g, a in feats if where is None or where(a)]
        if not gs:
            return None
        tree = STRtree(gs)
        idx, d = tree.query_nearest(pts, return_distance=True, all_matches=False)
        out = np.full(H * W, np.inf)
        out[idx[0]] = d
        return out
    have = lambda layer: vectors.loaded_here(layer, (lat0 + lat1) / 2, (lon0 + lon1) / 2)
    if have("road"):
        dr = dist_layer("road", lambda a: a.get("low_clearance", True))
        da = dist_layer("road")
        if dr is not None and "r_road_max" in P:
            apply("r_road_max", dr * ft > float(P["r_road_max"]["param"]) * geo.MI * ft)
        if da is not None and "r_road_min" in P:
            apply("r_road_min", da * ft < float(P["r_road_min"]["param"]))
    else:
        for rid in ("r_road_max", "r_road_min"):
            if rid in P: unknown[:] = True
    for layer, rid in (("trail", "r_trail"), ("rail", "r_rail"), ("cemetery", "r_grave"), ("building", "r_bldg")):
        if have(layer):
            d = dist_layer(layer)
            if d is not None and rid in P:
                apply(rid, d * ft < float(P[rid]["param"]))
        elif rid in P:
            unknown[:] = True
    if have("cave") and "r_cave" in P:
        dc = dist_layer("cave"); dm = dist_layer("mine")
        d = np.minimum(dc if dc is not None else np.inf, dm if dm is not None else np.inf)
        if np.isfinite(d).any():
            apply("r_cave", d * ft < float(P["r_cave"]["param"]))
    elif "r_cave" in P:
        unknown[:] = True
    if have("water") and "r_water" in P:
        feats = vectors.features_in("water", bm)
        inw = np.zeros(H * W, bool)
        for g, a in feats:
            inw |= shapely.contains_xy(g, X, Y)
        apply("r_water", inw)
    if "r_fenn" in P:
        best = np.full(H * W, np.inf)
        for name, la, lo in config.FENN_SITES:
            fx, fy = geo.to_m(lo, la)
            best = np.minimum(best, np.hypot(X - fx, Y - fy))
        apply("r_fenn", best > float(P["r_fenn"]["param"]) * geo.MI)
    nod = np.isnan(elev.ravel())
    surv = ~kill & ~flag & ~nod
    flagged = ~kill & flag & ~nod
    rgba = np.zeros((H * W, 4), np.uint8)
    rgba[kill & ~nod] = [242, 109, 109, 150]
    rgba[flagged] = [240, 149, 90, 120]
    rgba[surv] = [76, 197, 143, 90]
    rgba = rgba.reshape(H, W, 4)
    lat_mid = (lat0 + lat1) / 2
    cell_m2 = (30.87 * (lons[1] - lons[0]) * 3600 * np.cos(np.radians(lat_mid))) * (30.87 * abs(lats[0] - lats[1]) * 3600)
    sqmi = lambda n: n * cell_m2 / 2_589_988.11
    png = _png(rgba)
    return {"png": "data:image/png;base64," + base64.b64encode(png).decode(), "bounds": [[lats.min(), lons.min()], [lats.max(), lons.max()]], "cells": int(H * W), "cell_m": round(float(np.sqrt(cell_m2)), 1), "surviving_sqmi": round(sqmi(int(surv.sum())), 2), "flagged_sqmi": round(sqmi(int(flagged.sum())), 2), "killed_sqmi": round(sqmi(int((kill & ~nod).sum())), 2), "total_sqmi": round(sqmi(int((~nod).sum())), 2), "unknown_rules": [r for r in P if unknown.any() and r in ("r_public", "r_free", "r_dog", "r_road_max", "r_road_min", "r_trail", "r_rail", "r_grave", "r_bldg", "r_cave", "r_water") and r not in counts], "fail_counts": {k: round(sqmi(v), 2) for k, v in counts.items()}}
