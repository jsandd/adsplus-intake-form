"""Import the user's existing research database through mapping.json.

Input: an export from the Field HQ / Map's Edge Workbench artifact
(format "maps-edge-workbench/2" or "/3"), or the seed JSON kept in seed/.
Nothing is read until the mapping says where it goes. Fields not named in the
mapping are kept verbatim in a 'raw' slot on each record so nothing is dropped.
"""
import json
import os
import time

from . import store

DEFAULT_MAPPING_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mapping.json")

# The database's own confidence vocabulary → the tool's reliability tiers.
CONF_TO_TIER_DEFAULT = {
    "statement": {"confirmed": "confirmed", "likely": "reported", "unverified": "circulating", "disputed": "unverified"},
    "book": {"confirmed": "confirmed", "likely": "reported", "unverified": "circulating", "disputed": "unverified"},
    "map": {"confirmed": "reported", "likely": "reported", "unverified": "unverified", "disputed": "unverified"},
    "field": {"confirmed": "reported", "likely": "reported", "unverified": "unverified", "disputed": "unverified"},
    "community": {"confirmed": "reported", "likely": "circulating", "unverified": "circulating", "disputed": "unverified"},
    "speculation": {"confirmed": "fan", "likely": "fan", "unverified": "fan", "disputed": "unverified"},
    "objection": {"confirmed": "reported", "likely": "fan", "unverified": "fan", "disputed": "unverified"},
    "question": {"confirmed": "fan", "likely": "fan", "unverified": "fan", "disputed": "fan"},
    "math": {"confirmed": "reported", "likely": "fan", "unverified": "fan", "disputed": "unverified"},
}

DECLINE_WORDS = ["declin", "won't say", "wouldn't say", "refus", "no comment", "punt", "ambiguous", "didn't answer", "would not", "coy", "dodg", "wouldn't divulge", "won't divulge", "wouldn't confirm", "not going to"]


def load_mapping(path=None):
    with open(path or DEFAULT_MAPPING_PATH) as f:
        return json.load(f)


def _line_ref_map(export):
    """The export references lines by internal id (l01…); the tool uses S#L#."""
    out = {}
    lines = (export.get("poem") or {}).get("lines") or []
    counters = {}
    for l in lines:
        s = l.get("stanza", 1)
        counters[s] = counters.get(s, 0) + 1
        out[l["id"]] = f"S{s}L{counters[s]}"
    return out


def run_import(export, mapping=None, replace=True):
    mapping = mapping or load_mapping()
    refmap = _line_ref_map(export)
    report = {"statements": 0, "rumors": 0, "book": 0, "features": 0, "regions_notes": 0, "reference_solves": 0, "poem": False, "skipped": [], "unmapped_fields": set()}
    if replace:
        for t in ("statements", "rumors", "book"):
            store.run(f"DELETE FROM {t} WHERE origin='db'")
        store.run("DELETE FROM features WHERE origin='db'")
        for s in store.list_solves():
            if s["kind"] == "reference" and s.get("source", "").startswith("db:"):
                store.delete_solve(s["id"])
    # poem
    pm = mapping.get("poem", {})
    if pm.get("import") and export.get("poem", {}).get("raw") and not store.get_poem():
        store.save_poem(export["poem"].get("title") or "Poem", export["poem"]["raw"])
        report["poem"] = True
    # intel → statements / rumors / book
    im = mapping.get("intel", {})
    routes = im.get("route_by_kind", {})
    tiers = im.get("tier_by_kind_and_conf", CONF_TO_TIER_DEFAULT)
    for it in export.get("intel", []):
        kind = it.get("kind", "community")
        target = routes.get(kind, "rumors")
        tier = (tiers.get(kind) or {}).get(it.get("conf", "unverified"), "unverified")
        links = [{"ref": refmap.get(k.get("lineId"), k.get("lineId")), "stance": k.get("stance", "supports"), "why": k.get("why", "")} for k in it.get("links", [])]
        known = {"id", "text", "kind", "conf", "source", "when", "tags", "links", "created"}
        extra = {k: v for k, v in it.items() if k not in known}
        report["unmapped_fields"] |= set(extra.keys())
        raw = store.j(extra) if extra else None
        if target == "statements":
            low = (it.get("text") or "").lower()
            skind = "declined" if any(w in low for w in DECLINE_WORDS) else "answer"
            store.upsert("statements", {"id": it["id"], "text": it.get("text", ""), "date": it.get("when") or "", "venue": it.get("source") or "", "context": raw or "", "tier": tier, "kind": skind, "lines_json": store.j(links), "source": it.get("source") or "", "url": "", "tags_json": store.j(it.get("tags", [])), "origin": "db", "created": (it.get("created") or time.time() * 1000) / 1000})
            report["statements"] += 1
        elif target == "book":
            store.upsert("book", {"id": it["id"], "kind": "book", "title": (it.get("text") or "")[:80], "text": it.get("text", ""), "page": "", "chapter": "", "tags_json": store.j((it.get("tags") or []) + [l["ref"] for l in links]), "source": it.get("source") or "", "tier": tier, "origin": "db"})
            report["book"] += 1
        elif target == "skip":
            report["skipped"].append(it["id"])
        else:
            store.upsert("rumors", {"id": it["id"], "text": it.get("text", ""), "tier": tier, "source": it.get("source") or "", "date": it.get("when") or "", "region": "", "lines_json": store.j(links), "tags_json": store.j((it.get("tags") or []) + ([kind] if kind else [])), "origin": "db", "created": (it.get("created") or time.time() * 1000) / 1000})
            report["rumors"] += 1
    # candidates → features (as sites) + reference solves (from chain)
    cm = mapping.get("candidates", {})
    for c in export.get("candidates", []):
        lat = lon = None
        import re
        m = re.search(r"(-?\d{1,2}\.\d+)[,\s]+(-?\d{2,3}\.\d+)", c.get("coords") or "")
        if m:
            lat, lon = float(m.group(1)), float(m.group(2))
        if cm.get("to_features", True) and lat is not None:
            gates = c.get("gates") or {}
            flags = []
            if gates.get("g_public") == "fail":
                flags.append("private")
            if gates.get("g_free") == "fail":
                flags.append("fee")
            if gates.get("g_bldg") == "fail":
                flags.append("buildings")
            if gates.get("g_vehicle") == "fail":
                flags.append("high-clearance")
            if gates.get("g_notin") == "fail":
                flags.append("cave")
            elev = None
            m2 = re.search(r"([\d,]{3,6})\s*ft", c.get("elev") or "")
            if m2:
                elev = int(m2.group(1).replace(",", ""))
            store.upsert("features", {"id": "db_" + c["id"], "name": c.get("name", "").split("—")[0].strip(), "ftype": "site", "lat": lat, "lon": lon, "elev": elev, "state": (c.get("region") or "")[:2], "region": "", "owner": "", "access": "", "car": "", "rules_json": store.j(flags), "source": "your database: " + c.get("name", ""), "tier": cm.get("tier", "fan"), "aliases_json": store.j([]), "notes": (c.get("notes") or "")[:600], "keys_json": store.j([]), "gnis_verified": 0, "origin": "db"})
            report["features"] += 1
        if cm.get("to_reference_solves", True) and c.get("chain"):
            lines = {}
            for lid, s in c["chain"].items():
                ref = refmap.get(lid, lid)
                m3 = re.search(r"(-?\d{1,2}\.\d+)[,\s]+(-?\d{2,3}\.\d+)", s.get("coords") or "")
                v = (c.get("verdicts") or {}).get(lid)
                lines[ref] = {"text": s.get("place") or s.get("reading") or "", "rationale": s.get("reading") or "", "category": "literal" if m3 else "structural", "lat": float(m3.group(1)) if m3 else None, "lon": float(m3.group(2)) if m3 else None, "conf": int(s.get("conf") or 1), "tier": cm.get("tier", "fan"), "verdict": v, "ts": time.time()}
            if lines:
                gates = c.get("gates") or {}
                store.new_solve(c.get("name", "imported"), kind="reference", source="db:" + c["id"], state={"lines": lines, "history": [], "overrides": {}, "notes": {"_case": c.get("notes", ""), "_kill": c.get("kill", ""), "_test": c.get("test", ""), "_gates": gates}, "radius": {}, "hard_filter": False, "hide_violations": False})
                report["reference_solves"] += 1
    # map states → region status / eliminated
    mm = mapping.get("mapStates", {})
    if mm.get("import", True):
        for st, v in (export.get("mapStates") or {}).items():
            status = (v or {}).get("status")
            if status == "eliminated":
                # add to the states rule if not already there
                r = store.row("SELECT * FROM rules WHERE id='s_states'")
                if r and st not in r["code"]:
                    store.run("UPDATE rules SET code=? WHERE id='s_states'", (r["code"] + "," + st,))
            store.set_setting("mapstate_" + st, v)
            report["regions_notes"] += 1
    report["unmapped_fields"] = sorted(report["unmapped_fields"])
    store.set_setting("last_import", {"ts": time.time(), "report": report})
    return report
