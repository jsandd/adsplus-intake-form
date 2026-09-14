"""USGS 3DEP 1 arc-second (about 30 m) elevation. One GeoTIFF per 1°×1° tile,
downloaded once from the National Map's S3 bucket and cached in data/dem."""
import math
import os
import threading
import urllib.request

import numpy as np

from . import config

_lock = threading.Lock()
_open = {}
_status = {"downloading": None, "error": None}


def tile_name(lat, lon):
    n = int(math.floor(lat)) + 1
    w = int(math.ceil(-lon))
    return f"n{n:02d}w{w:03d}"


def tile_path(name):
    return os.path.join(config.DEM_DIR, f"USGS_1_{name}.tif")


def tile_url(name):
    return f"{config.TNM}Elevation/1/TIFF/current/{name}/USGS_1_{name}.tif"


def have_tile(name):
    p = tile_path(name)
    return os.path.exists(p) and os.path.getsize(p) > 1_000_000


def fetch_tile(name, log=None):
    os.makedirs(config.DEM_DIR, exist_ok=True)
    p = tile_path(name)
    if have_tile(name):
        return p
    tmp = p + ".part"
    _status["downloading"] = name
    try:
        if log:
            log(f"  elevation tile {name}: downloading (~50 MB)…")
        urllib.request.urlretrieve(tile_url(name), tmp)
        os.replace(tmp, p)
        _status["error"] = None
        return p
    except Exception as e:
        _status["error"] = f"{name}: {e}"
        if os.path.exists(tmp):
            os.remove(tmp)
        if log:
            log(f"  elevation tile {name}: FAILED ({e})")
        return None
    finally:
        _status["downloading"] = None


def tiles_for_bbox(bbox):
    lon0, lat0, lon1, lat1 = bbox
    out = []
    for lat in range(int(math.floor(lat0)), int(math.ceil(lat1))):
        for lon in range(int(math.floor(lon0)), int(math.ceil(lon1))):
            out.append(tile_name(lat + 0.5, lon + 0.5))
    return out


def fetch_state(state, log=None):
    if state not in config.STATES:
        raise SystemExit(f"unknown state {state}")
    names = tiles_for_bbox(config.STATES[state][1])
    if log:
        log(f"{state}: {len(names)} tiles, {len([n for n in names if have_tile(n)])} already here")
    for n in names:
        fetch_tile(n, log)


def coverage():
    out = {}
    for st, (name, bbox) in config.STATES.items():
        names = tiles_for_bbox(bbox)
        out[st] = {"tiles": len(names), "have": sum(1 for n in names if have_tile(n))}
    return {"states": out, "downloading": _status["downloading"], "error": _status["error"]}


def _dataset(name, allow_download=True):
    with _lock:
        if name in _open:
            return _open[name]
    if not have_tile(name):
        if not allow_download or not fetch_tile(name):
            return None
    import rasterio
    ds = rasterio.open(tile_path(name))
    with _lock:
        _open[name] = ds
    return ds


def sample(lat, lon, allow_download=True):
    """Return dict(elev_ft, slope_deg, aspect, tile) or None when no tile is available."""
    name = tile_name(lat, lon)
    ds = _dataset(name, allow_download)
    if ds is None:
        return None
    r, c = ds.index(lon, lat)
    r0, c0 = max(r - 1, 0), max(c - 1, 0)
    win = ((r0, min(r0 + 3, ds.height)), (c0, min(c0 + 3, ds.width)))
    a = ds.read(1, window=win).astype("float64")
    nod = ds.nodata
    if nod is not None:
        a[a == nod] = np.nan
    if a.shape != (3, 3) or np.isnan(a).any():
        z = a[min(r - r0, a.shape[0] - 1), min(c - c0, a.shape[1] - 1)]
        return {"elev_ft": None if np.isnan(z) else float(z) * 3.280839895, "slope_deg": None, "tile": name}
    dy_m = 30.87  # metres per arc-second of latitude
    dx_m = 30.87 * math.cos(math.radians(lat))
    dzdx = ((a[0, 2] + 2 * a[1, 2] + a[2, 2]) - (a[0, 0] + 2 * a[1, 0] + a[2, 0])) / (8 * dx_m)
    dzdy = ((a[2, 0] + 2 * a[2, 1] + a[2, 2]) - (a[0, 0] + 2 * a[0, 1] + a[0, 2])) / (8 * dy_m)
    slope = math.degrees(math.atan(math.hypot(dzdx, dzdy)))
    return {"elev_ft": float(a[1, 1]) * 3.280839895, "slope_deg": slope, "tile": name}


def window(bbox, max_cells=250_000):
    """Elevation (metres) and slope (degrees) grids for a lon/lat box, downsampled so
    the grid stays under max_cells. Returns (elev, slope, lons, lats) or None if a tile is missing."""
    lon0, lat0, lon1, lat1 = bbox
    names = tiles_for_bbox(bbox)
    for n in names:
        if _dataset(n) is None:
            return None
    step = 1 / 3600.0
    nx = int((lon1 - lon0) / step) + 1
    ny = int((lat1 - lat0) / step) + 1
    f = max(1, int(math.ceil(math.sqrt(nx * ny / max_cells))))
    lons = np.arange(lon0, lon1, step * f)
    lats = np.arange(lat1, lat0, -step * f)
    grid = np.full((len(lats), len(lons)), np.nan)
    for n in names:
        ds = _dataset(n)
        b = ds.bounds
        sel_x = (lons >= b.left) & (lons < b.right)
        sel_y = (lats >= b.bottom) & (lats < b.top)
        if not sel_x.any() or not sel_y.any():
            continue
        xs = lons[sel_x]; ys = lats[sel_y]
        from rasterio.transform import rowcol
        rows, cols = rowcol(ds.transform, np.repeat(xs[None, :], len(ys), 0).ravel(), np.repeat(ys[:, None], len(xs), 1).ravel())
        rows = np.clip(np.asarray(rows, dtype=int), 0, ds.height - 1); cols = np.clip(np.asarray(cols, dtype=int), 0, ds.width - 1)
        r0, r1, c0, c1 = rows.min(), rows.max() + 1, cols.min(), cols.max() + 1
        block = ds.read(1, window=((r0, r1), (c0, c1))).astype("float64")
        if ds.nodata is not None:
            block[block == ds.nodata] = np.nan
        vals = block[rows - r0, cols - c0].reshape(len(ys), len(xs))
        iy = np.where(sel_y)[0]; ix = np.where(sel_x)[0]
        grid[np.ix_(iy, ix)] = vals
    lat_mid = (lat0 + lat1) / 2
    dy = 30.87 * f; dx = 30.87 * f * math.cos(math.radians(lat_mid))
    gy, gx = np.gradient(grid, dy, dx)
    slope = np.degrees(np.arctan(np.hypot(gx, gy)))
    return grid, slope, lons, lats
