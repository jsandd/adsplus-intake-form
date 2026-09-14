"""Rules engine. A rule config: id, name, source, tag (CONFIRMED|SAID), type (include|exclude),
severity (kill|flag), on, param, unit. Verdicts: pass | fail | unknown, with the measured value."""
import copy
import math

from . import config, geo


def defaults():
    return copy.deepcopy(config.DEFAULT_RULES)


def merged(overrides):
    out = defaults()
    by = {r["id"]: r for r in out}
    for rid, o in (overrides or {}).items():
        if rid in by:
            for k in ("on", "param", "severity", "tag"):
                if k in o and o[k] is not None:
                    by[rid][k] = o[k]
    return out


def _v(status, value, note="", measured=None):
    return {"status": status, "value": value, "note": note, "measured": measured}


def evaluate(rules, m):
    """m = measurements from scorer.measure(). Returns {rule_id: verdict} and a summary."""
    out = {}
    P = {r["id"]: r for r in rules}
    ft = geo.FT

    def dist_rule(rid, key, mode):
        r = P[rid]
        d = m.get(key)  # metres or None
        have = m.get(key + "_have", False)
        if not have:
            out[rid] = _v("unknown", "layer not loaded", "load the layer for this state in the Data panel"); return
        if d is None:
            out[rid] = _v("pass" if mode == "min" else "fail", "none within 5 mi", "" if mode == "min" else "no road within the search radius", None); return
        val = d * ft
        lim = float(r["param"]) * (geo.MI * ft if r["unit"] == "mi" else 1)
        if mode == "min":
            out[rid] = _v("pass" if val >= lim else "fail", f"{val:,.0f} ft", m.get(key + "_note", ""), val)
        else:
            out[rid] = _v("pass" if val <= lim else "fail", f"{val / (geo.MI * ft):.2f} mi", m.get(key + "_note", ""), val)

    # state
    st = m.get("state_code")
    if m.get("in_co_or"):
        out["r_state"] = _v("fail", m["in_co_or"], "eliminated entirely")
    else:
        out["r_state"] = _v("pass", st or "outside the eleven states", "")
    lon0, lat0, lon1, lat1 = config.MAP_EXTENT
    out["r_map"] = _v("pass" if lon0 <= m["lon"] <= lon1 and lat0 <= m["lat"] <= lat1 else "fail", f"{m['lat']:.4f}, {m['lon']:.4f}", "")
    # elevation, slope
    e = m.get("elev_ft")
    if e is None:
        out["r_elev"] = _v("unknown", "no elevation tile", m.get("dem_note", "download the tile"))
        out["r_slope"] = _v("unknown", "no elevation tile", "")
    else:
        out["r_elev"] = _v("pass" if e < float(P["r_elev"]["param"]) else "fail", f"{e:,.0f} ft", "", e)
        s = m.get("slope_deg")
        out["r_slope"] = _v("unknown", "edge of tile", "") if s is None else _v("pass" if s <= float(P["r_slope"]["param"]) else "fail", f"{s:.0f}°", "30 m grid; local cliffs can hide inside a cell", s)
    # land
    pd = m.get("padus")
    if pd is None:
        for rid in ("r_public", "r_free", "r_dog"):
            out[rid] = _v("unknown", "PAD-US not loaded", "load the GeoPackage in the Data panel")
    else:
        if not pd["in_padus"]:
            out["r_public"] = _v("fail", "no public unit", "PAD-US has nothing here; most unmapped land is private. Verify on a county parcel map before trusting this.")
        elif pd.get("private"):
            out["r_public"] = _v("fail", pd["owner"], "private owner in PAD-US")
        elif pd["access_code"] == "XA":
            out["r_public"] = _v("fail", pd["access"], pd["owner"])
        elif pd["access_code"] == "RA":
            out["r_public"] = _v("unknown", pd["access"], pd["owner"] + " · restricted: check the unit's rules")
        else:
            out["r_public"] = _v("pass", pd["owner"], pd.get("designation") or "")
        fee = pd["fee"]
        out["r_free"] = _v("fail" if fee.startswith("likely fee") else "unknown" if fee.startswith("check") or fee == "unknown" else "pass", fee, "PAD-US carries no fee field; NPS units are assumed to charge")
        dg = pd["dogs"]
        out["r_dog"] = _v("fail" if dg.startswith("usually barred") else "unknown" if dg == "unknown" else "pass", dg, "")
    # distances
    dist_rule("r_road_max", "road_m", "max")
    dist_rule("r_road_min", "road_any_m", "min")
    dist_rule("r_trail", "trail_m", "min")
    dist_rule("r_bldg", "building_m", "min")
    dist_rule("r_grave", "cemetery_m", "min")
    dist_rule("r_rail", "rail_m", "min")
    # cave / mine: nearest point feature
    cm = [x for x in (m.get("cave_m"), m.get("mine_m")) if x is not None]
    if not m.get("cave_m_have"):
        out["r_cave"] = _v("unknown", "GNIS not loaded", "")
    elif not cm:
        out["r_cave"] = _v("pass", "none within 5 mi", "")
    else:
        d = min(cm) * ft
        out["r_cave"] = _v("pass" if d >= float(P["r_cave"]["param"]) else "fail", f"{d:,.0f} ft to {m.get('cave_name') or m.get('mine_name') or 'a cave or mine'}", "named caves and mines only; unnamed adits are not in GNIS", d)
    # water
    if not m.get("water_have"):
        out["r_water"] = _v("unknown", "NHD not loaded", "step 3")
    else:
        out["r_water"] = _v("fail" if m.get("in_water") else "pass", m.get("water_name") or "dry land", "")
    # fenn
    f = m.get("fenn_mi")
    out["r_fenn"] = _v("pass" if f is not None and f <= float(P["r_fenn"]["param"]) else "fail", f"{f:.0f} mi to {m.get('fenn_site')}" if f is not None else "—", "soft: he walked this back", f)

    # summary
    kills, flags, unknown = [], [], []
    for r in rules:
        v = out.get(r["id"])
        if not v or not r["on"]:
            continue
        if v["status"] == "fail":
            (kills if r["severity"] == "kill" else flags).append(r["id"])
        elif v["status"] == "unknown":
            unknown.append(r["id"])
    verdict = "KILLED" if kills else ("FLAGGED" if flags else ("OPEN" if unknown else "SURVIVES"))
    return out, {"verdict": verdict, "kills": kills, "flags": flags, "unknown": unknown}
