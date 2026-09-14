"""Measure everything mappable at a point. Fast: only local lookups (plus a one-time tile download)."""
import time

from . import config, dem, geo, padus, vectors


def measure(lat, lon, allow_download=True):
    t0 = time.time()
    m = {"lat": lat, "lon": lon}
    st = vectors.state_for(lat, lon)
    m["state_code"] = st
    if geo.point_in_poly(lon, lat, config.COLORADO):
        m["in_co_or"] = "Colorado"
    elif geo.point_in_poly(lon, lat, config.OREGON):
        m["in_co_or"] = "Oregon"
    d = dem.sample(lat, lon, allow_download)
    if d:
        m.update(d)
    else:
        m["dem_note"] = dem._status.get("error") or "tile not downloaded"
    if padus.loaded()["units"]:
        hits, summ = padus.query(lat, lon)
        m["padus"] = summ; m["padus_hits"] = hits[:6]
        if summ.get("state"):
            m["state_code"] = summ["state"]
    def have(layer):
        return vectors.loaded_here(layer, lat, lon)
    if have("road"):
        m["road_m_have"] = True
        dd, a = vectors.nearest("road", lat, lon, max_m=8100, where=lambda a: a.get("low_clearance", True))
        m["road_m"] = dd; m["road_m_note"] = f"{(a or {}).get('name') or 'unnamed'} · {(a or {}).get('class', '')}" if a else ""
        m["road_any_m_have"] = True
        d2, a2 = vectors.nearest("road", lat, lon, max_m=8100)
        m["road_any_m"] = d2; m["road_any_m_note"] = f"{(a2 or {}).get('name') or 'unnamed'} · {(a2 or {}).get('class', '')}" if a2 else ""
    if have("trail"):
        m["trail_m_have"] = True
        dd, a = vectors.nearest("trail", lat, lon, max_m=8100)
        m["trail_m"] = dd; m["trail_m_note"] = (a or {}).get("name") or ""
    if have("rail"):
        m["rail_m_have"] = True
        dd, a = vectors.nearest("rail", lat, lon, max_m=8100)
        m["rail_m"] = dd; m["rail_m_note"] = (a or {}).get("name") or ""
    if have("cemetery"):
        m["cemetery_m_have"] = True
        dd, a = vectors.nearest("cemetery", lat, lon, max_m=8100)
        m["cemetery_m"] = dd; m["cemetery_m_note"] = (a or {}).get("name") or ""
    if have("cave"):
        m["cave_m_have"] = True
        for layer in ("cave", "mine"):
            dd, a = vectors.nearest(layer, lat, lon, max_m=8100)
            m[layer + "_m"] = dd; m[layer + "_name"] = (a or {}).get("name")
    if have("building"):
        m["building_m_have"] = True
        dd, a = vectors.nearest("building", lat, lon, max_m=8100)
        m["building_m"] = dd; m["building_m_note"] = (a or {}).get("name") or ""
    if have("water"):
        m["water_have"] = True
        w = vectors.contains("water", lat, lon)
        m["in_water"] = bool(w); m["water_name"] = (w or {}).get("name")
    best = None
    for name, la, lo in config.FENN_SITES:
        dmi = geo.haversine_mi((lat, lon), (la, lo))
        if best is None or dmi < best[0]:
            best = (dmi, name)
    m["fenn_mi"], m["fenn_site"] = best
    m["ms"] = int((time.time() - t0) * 1000)
    return m
