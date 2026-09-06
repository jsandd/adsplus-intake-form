"""The reasoning engine: suggestions, cascading constraints, rules, contradictions,
scoring, reactions, weakest links, seed dependence, auto search, reverse mode.

Everything here is deterministic and runs offline. ai.py adds the parts that need
a language model on top of these results.
"""
import itertools
import math
import re
import time
from collections import Counter, defaultdict

from . import geo, knowledge, store

CATEGORIES = [
    ("literal", "Literal place"), ("feature_class", "Feature class"), ("direction", "Direction / action"), ("wordplay", "Wordplay"),
    ("naming", "Naming & culture"), ("numeric", "Numeric / cipher"), ("personal", "Personal to Posey"), ("structural", "Structural"),
]
CAT_WEIGHT = {"literal": 1.0, "feature_class": 0.7, "naming": 0.9, "direction": 0.8, "wordplay": 0.6, "numeric": 0.5, "personal": 0.5, "structural": 0.4}
TIERS = ["confirmed", "reported", "circulating", "fan", "unverified"]
TIER_LABEL = {"confirmed": "Confirmed — Posey said it, dated source", "reported": "Reported — named searcher, firsthand", "circulating": "Circulating — forum/social consensus, no clear origin", "fan": "Fan analysis — analysis site or compiled notes", "unverified": "Unverified — could not be traced to a source"}
TIER_WEIGHT = {"confirmed": 1.0, "reported": 0.8, "circulating": 0.55, "fan": 0.5, "unverified": 0.4}
STOP = set("a an the and or but if of to in on at by for with from as is are was were be been it its this that these those i me my we our you your he she they them there here not no yes do does did have has had will would can could should so than then when where which who what how why all any some more most other into out about over under again once very just also too only own same".split())
HIDDEN_WORDS = {"ursa": ["USA", "sur"], "realm": ["real", "elm", "ream"], "bride": ["ride", "bid", "rid"], "gates": ["gate", "age", "sage", "east"], "granite": ["grant", "gran", "rant", "ranite"], "shadowed": ["shad", "shadow", "owed", "how"], "wisdom": ["wis", "dom"], "measured": ["measure", "sure", "ease"], "flowing": ["owing", "low", "wing"], "hole": ["ole", "whole"], "pole": ["Pole", "Polaris?", "ole"], "bend": ["ben", "end"], "twenty": ["went", "ten", "tent"], "degree": ["deg", "tree?"], "return": ["turn", "urn", "ret"], "double": ["dou", "ble", "doubt?"], "arcs": ["arc", "cars", "scar"], "wonder": ["won", "onder", "under"], "sacred": ["scared", "cedar"], "truth": ["ruth", "rut"], "tangled": ["angle", "tang", "led"], "twisted": ["twist", "wisted"], "waters": ["water", "aters", "wa"], "silent": ["listen", "tinsel", "enlist", "lent"], "flight": ["light", "fight"], "hope": ["ope", "hop"], "surges": ["urge", "surge"]}
HOMOPHONES = {"ursa": "Ursa (Major/Minor) — the Bear; also 'USA'", "pole": "pole / Pole (north pole, pole star) / poll", "hole": "hole / whole", "bride": "bride / bridle / Bridal (Veil)", "east": "east / yeast / 'his realm awaits' → he-realm", "gates": "gates / gaits", "arcs": "arcs / arks / Ark", "bold": "bold / bowled", "hold": "hold / holed", "race": "race / raise", "flow": "flow / floe", "know": "know / no", "rhyme": "rhyme / rime (ice)", "sight": "sight / site / cite", "right": "right / write / rite", "waits": "waits / weights", "foot": "foot (measure) / foot (base)", "three": "three / tree", "degree": "degree (angle / temperature / academic)", "reach": "reach (a stretch of river)", "cast": "cast (fishing) / cast (shadow) / cast (compass rose points)", "bend": "bend (river) / Bend (town)", "hope": "Hope (many towns)"}


def words(text):
    return [w for w in re.findall(r"[A-Za-z']+", text.lower())]


def content_words(text):
    return [w.strip("'") for w in words(text) if w.strip("'") not in STOP and len(w) > 2]


# ---------------------------------------------------------------- knowledge bootstrap

def ensure_knowledge():
    if not store.row("SELECT 1 FROM features LIMIT 1"):
        for f in knowledge.F:
            store.upsert("features", {"id": store.uid("f"), "name": f["name"], "ftype": f["ftype"], "lat": f["lat"], "lon": f["lon"], "elev": f["elev"], "state": f["state"], "region": f["region"], "owner": f["owner"], "access": f["access"], "car": f["car"], "rules_json": store.j(f["flags"]), "source": "built-in (Claude, general knowledge)", "tier": "unverified", "aliases_json": store.j(f["aliases"]), "notes": f["notes"], "keys_json": store.j(f["keys"]), "gnis_verified": 0, "origin": "builtin"})
    if not store.row("SELECT 1 FROM regions LIMIT 1"):
        for r in knowledge.REGIONS:
            store.upsert("regions", {"id": r["id"], "name": r["name"], "states": r["states"], "bbox_json": store.j(r["bbox"]), "dossier_json": store.j(r["dossier"]), "status": r["status"], "origin": "builtin"})
    if not store.row("SELECT 1 FROM rules LIMIT 1"):
        for rid, text, code in knowledge.HARD_RULES:
            store.upsert("rules", {"id": rid, "text": text, "kind": "hard", "enabled": 1, "code": code, "note": "", "source": "treasure.quest rules"})
        for rid, text, code in knowledge.SOFT_RULES:
            store.upsert("rules", {"id": rid, "text": text, "kind": "soft", "enabled": 1, "code": code, "note": "", "source": "interviews / Q&A"})
    if not store.row("SELECT 1 FROM solves WHERE kind='reference' LIMIT 1"):
        for rs in knowledge.REFERENCE_SOLVES:
            lines = {}
            for ref, c in rs["lines"].items():
                lines[ref] = {"text": c["text"], "category": c["category"], "lat": c.get("lat"), "lon": c.get("lon"), "conf": c.get("conf", 1), "tier": "circulating", "rationale": "community reading", "source": rs["source"], "ts": time.time()}
            store.new_solve(rs["name"], kind="reference", source=rs["source"], state={"lines": lines, "history": [], "overrides": {}, "notes": {}, "radius": {}, "hard_filter": False, "hide_violations": False})


def features(state_filter=None):
    fs = store.rows("SELECT * FROM features")
    out = []
    for f in fs:
        f["flags"] = store.unj(f.pop("rules_json"), [])
        f["aliases"] = store.unj(f.pop("aliases_json"), [])
        f["keys"] = store.unj(f.pop("keys_json"), [])
        if state_filter and f["state"] not in state_filter:
            continue
        out.append(f)
    return out


def regions():
    out = []
    for r in store.rows("SELECT * FROM regions"):
        r["bbox"] = store.unj(r.pop("bbox_json"), None)
        r["dossier"] = store.unj(r.pop("dossier_json"), {})
        out.append(r)
    return out


def region_of(lat, lon):
    for r in regions():
        if r["bbox"] and geo.in_bbox(lat, lon, r["bbox"]):
            return r
    return None


def rules(kind=None):
    rs = store.rows("SELECT * FROM rules" + (" WHERE kind=?" if kind else ""), (kind,) if kind else ())
    return rs


def eliminated_states():
    out = set()
    for r in rules("soft"):
        if r["enabled"] and r["code"].startswith("check:states:"):
            out |= set(r["code"].split(":")[2].split(","))
    for r in store.rows("SELECT * FROM regions WHERE status='eliminated'"):
        out |= set(r["states"].split(","))
    return out


def statements_for(ref=None):
    out = []
    for s in store.rows("SELECT * FROM statements"):
        s["lines"] = store.unj(s.pop("lines_json"), [])
        s["tags"] = store.unj(s.pop("tags_json"), [])
        if ref is None or any(l.get("ref") == ref for l in s["lines"]):
            out.append(s)
    return out


# ---------------------------------------------------------------- constraint state

def poem_lines():
    p = store.get_poem()
    return p["lines"] if p else []


def line_index(ref):
    for i, l in enumerate(poem_lines()):
        if l["ref"] == ref:
            return i
    return -1


def committed(solve):
    """Committed lines in poem order: [(ref, commit)]."""
    lines = solve["state"].get("lines", {})
    return [(l["ref"], lines[l["ref"]]) for l in poem_lines() if l["ref"] in lines]


def pinned(solve):
    return [(ref, c) for ref, c in committed(solve) if c.get("lat") is not None and c.get("lon") is not None]


def seed_info(solve):
    seed = solve["state"].get("seed") or {}
    info = {"states": set(seed.get("states") or []), "region": None, "bbox": None, "point": None, "endpoint": None, "label": ""}
    if seed.get("region"):
        r = store.row("SELECT * FROM regions WHERE id=?", (seed["region"],))
        if r:
            info["region"] = r["id"]
            info["bbox"] = store.unj(r["bbox_json"])
            info["states"] |= set(r["states"].split(","))
            info["label"] = r["name"]
    if seed.get("feature") and seed["feature"].get("lat") is not None:
        info["point"] = [seed["feature"]["lat"], seed["feature"]["lon"]]
        info["label"] = (info["label"] + " · " if info["label"] else "") + seed["feature"].get("name", "pinned feature")
    if seed.get("endpoint") and seed["endpoint"].get("lat") is not None:
        info["endpoint"] = [seed["endpoint"]["lat"], seed["endpoint"]["lon"]]
        info["label"] = (info["label"] + " · " if info["label"] else "") + "endpoint " + seed["endpoint"].get("name", "")
    if info["states"] and not info["label"]:
        info["label"] = ", ".join(sorted(info["states"]))
    return info


def constraint_state(solve, ref=None):
    """Running constraints up to (not including) `ref`, plus what lies after it."""
    lines = poem_lines()
    idx = line_index(ref) if ref else len(lines)
    seed = seed_info(solve)
    st = {"states": set(seed["states"]), "eliminated": sorted(eliminated_states()), "bbox": seed["bbox"], "point": None, "point_ref": None, "next_point": None, "next_ref": None, "bearing": None, "bearing_ref": None, "elev": None, "owner": None, "distance": 0.0, "legs": [], "seed": seed["label"], "manmade": []}
    pts = []
    for i, l in enumerate(lines):
        c = solve["state"].get("lines", {}).get(l["ref"])
        if not c:
            continue
        if c.get("lat") is not None:
            if pts:
                d = geo.haversine(pts[-1][1], (c["lat"], c["lon"]))
                st["legs"].append({"from": pts[-1][0], "to": l["ref"], "mi": round(d, 1), "bearing": round(geo.bearing(pts[-1][1], (c["lat"], c["lon"])))})
                if i < idx:
                    st["distance"] += d
            pts.append((l["ref"], (c["lat"], c["lon"])))
            s = geo.state_of(c["lat"], c["lon"])
            if s and i < idx:
                st["states"].add(s)
            if i < idx:
                st["point"] = [c["lat"], c["lon"]]
                st["point_ref"] = l["ref"]
                if c.get("elev"):
                    st["elev"] = c["elev"]
                if c.get("owner"):
                    st["owner"] = c["owner"]
            elif st["next_point"] is None and i > idx:
                st["next_point"] = [c["lat"], c["lon"]]
                st["next_ref"] = l["ref"]
        if c.get("bearing") is not None and i < idx:
            st["bearing"] = c["bearing"]
            st["bearing_ref"] = l["ref"]
        if c.get("manmade"):
            st["manmade"].append(l["ref"])
    if st["point"] is None and seed["point"] is not None:
        st["point"] = seed["point"]
        st["point_ref"] = "seed"
    if st["next_point"] is None and seed["endpoint"] is not None:
        st["next_point"] = seed["endpoint"]
        st["next_ref"] = "endpoint"
    if st["bbox"] is None and len(pts) >= 2:
        b = geo.bbox_of([p[1] for p in pts])
        st["bbox"] = [b[0] - 0.5, b[1] - 0.6, b[2] + 0.5, b[3] + 0.6]
    st["states"] = sorted(st["states"])
    st["distance"] = round(st["distance"], 1)
    st["region"] = (region_of(*st["point"]) or {}).get("name") if st["point"] else None
    return st


# ---------------------------------------------------------------- rules on a candidate

def rule_flags(cand):
    """Return [(rule_id, text, kind)] for rules a candidate trips."""
    out = []
    flags = set(cand.get("flags") or [])
    for r in rules():
        if not r["enabled"]:
            continue
        code = r["code"] or ""
        if code.startswith("flag:") or code.startswith("check:flag:"):
            want = set(code.split("flag:")[1].split(","))
            hit = flags & want
            if hit:
                out.append({"rule": r["id"], "text": r["text"], "kind": r["kind"], "why": ", ".join(sorted(hit))})
        elif code.startswith("check:states:") and cand.get("state") in code.split(":")[2].split(","):
            out.append({"rule": r["id"], "text": r["text"], "kind": r["kind"], "why": cand.get("state")})
        elif code == "check:map" and cand.get("lat") is not None and not geo.in_bbox(cand["lat"], cand["lon"], knowledge.FENN_MAP_BBOX):
            out.append({"rule": r["id"], "text": r["text"], "kind": r["kind"], "why": "outside the Fenn-map bounding box"})
        elif code.startswith("check:fenn:") and cand.get("lat") is not None:
            lim = float(code.split(":")[2])
            d = min(geo.haversine((cand["lat"], cand["lon"]), (f[1], f[2])) for f in knowledge.FENN_SITES)
            if d > lim:
                out.append({"rule": r["id"], "text": r["text"], "kind": r["kind"], "why": f"{d:.0f} mi from the nearest documented Fenn search"})
    if cand.get("elev") and cand["elev"] > 5280 * 2:
        out.append({"rule": "elev", "text": "Very high (above 10,560 ft) — hard to reach within a mile of a car", "kind": "soft", "why": f"{cand['elev']} ft"})
    return out


# ---------------------------------------------------------------- suggestions

def _line(ref):
    for l in poem_lines():
        if l["ref"] == ref:
            return l
    return None


def _hint_types(text):
    types = set()
    matched = []
    for w in content_words(text):
        stem = w.rstrip("s")
        for key, ts in knowledge.LINE_HINTS.items():
            if w == key or stem == key or w.startswith(key):
                types |= set(ts)
                matched.append(key)
    return types, matched


def _name_matches(text):
    """Which name-pattern ideas does this line invoke?"""
    ideas = []
    ws = set(content_words(text))
    idea_words = {"bear": {"ursa", "bear"}, "north star / polaris": {"ursa", "pole", "star", "north"}, "wisdom": {"wisdom"}, "hole": {"hole"}, "bride / wedding": {"bride", "her", "face"}, "gold": {"secrets", "treasure"}, "needle": {"pole"}, "crown": {"realm", "guard"}, "three": {"three"}, "twenty": {"twenty"}, "silence": {"silent", "rests"}, "shadow": {"shadowed", "shadow"}, "light": {"bright", "clear", "sight"}, "two / pair": {"double", "arcs"}, "time": {"time", "ancient", "past"}, "face": {"face", "sight", "his", "her"}}
    for idea, iw in idea_words.items():
        if ws & iw:
            ideas.append(idea)
    return ideas


def _feature_idea_hits(f, ideas):
    names = [f["name"].lower()] + [a.lower() for a in f.get("aliases", [])]
    hits = []
    for idea in ideas:
        for pat in knowledge.NAME_PATTERNS.get(idea, []):
            if any(pat in n for n in names):
                hits.append(idea)
                break
    return hits


def _tier_label(t):
    return TIER_LABEL.get(t, t)


def suggestions(solve, ref, radius_mi=None, hard_filter=None, hide_violations=None, extra=None):
    line = _line(ref)
    if not line:
        return {"error": "no such line"}
    st = constraint_state(solve, ref)
    seed = seed_info(solve)
    state = solve["state"]
    radius = radius_mi if radius_mi is not None else state.get("radius", {}).get(ref, 30 if st["point"] else 400)
    hard = state.get("hard_filter", False) if hard_filter is None else hard_filter
    hide = state.get("hide_violations", False) if hide_violations is None else hide_violations
    elim = set(st["eliminated"])
    hint_types, hint_words = _hint_types(line["text"])
    ideas = _name_matches(line["text"])
    stmts = statements_for(ref)
    out = []

    def support_for(text):
        toks = set(content_words(text))
        sup, con = [], []
        for s in stmts:
            for l in s["lines"]:
                if l.get("ref") != ref:
                    continue
                overlap = toks & set(content_words(s["text"]))
                item = {"id": s["id"], "text": s["text"][:220], "tier": s["tier"], "date": s.get("date"), "kind": s.get("kind")}
                (con if l.get("stance") == "contradicts" else sup).append(item) if overlap or len(sup) + len(con) < 2 else None
        return sup[:4], con[:4]

    def add(c):
        c.setdefault("category", "literal")
        c.setdefault("tier", "unverified")
        c.setdefault("conf", 1)
        c.setdefault("flags", [])
        c["rules"] = rule_flags(c)
        c["hard_violation"] = any(r["kind"] == "hard" for r in c["rules"])
        c["seed_match"] = False
        if c.get("lat") is not None:
            if c.get("state") is None:
                c["state"] = geo.state_of(c["lat"], c["lon"])
            if st["point"]:
                c["dist_active"] = round(geo.haversine(st["point"], (c["lat"], c["lon"])), 1)
            if st["next_point"]:
                c["dist_next"] = round(geo.haversine(st["next_point"], (c["lat"], c["lon"])), 1)
            if seed["point"]:
                c["dist_seed"] = round(geo.haversine(seed["point"], (c["lat"], c["lon"])), 1)
            elif seed["bbox"]:
                c["dist_seed"] = 0 if geo.in_bbox(c["lat"], c["lon"], seed["bbox"]) else round(geo.haversine(geo.bbox_center(seed["bbox"]), (c["lat"], c["lon"])), 1)
            if seed["states"] and c["state"] in seed["states"]:
                c["seed_match"] = True
            if seed["bbox"] and geo.in_bbox(c["lat"], c["lon"], seed["bbox"]):
                c["seed_match"] = True
            if seed["point"] and c.get("dist_seed", 999) <= 40:
                c["seed_match"] = True
            if c["state"] in elim:
                c["eliminated"] = True
        sup, con = support_for(c.get("text", "") + " " + c.get("rationale", ""))
        c["support"], c["contradict"] = sup, con
        # score
        base = CAT_WEIGHT.get(c["category"], .5) * TIER_WEIGHT.get(c["tier"], .4) * (0.6 + 0.2 * c["conf"])
        if c.get("dist_active") is not None:
            if c["dist_active"] <= radius:
                base += 0.6 * (1 - c["dist_active"] / max(radius, 1))
            else:
                base -= min(1.0, (c["dist_active"] - radius) / 100)
        if c.get("dist_next") is not None and c["dist_next"] <= radius:
            base += 0.3
        if c["seed_match"]:
            base += 0.35
        base += 0.15 * len(sup) - 0.2 * len(con)
        base -= 0.25 * len([r for r in c["rules"] if r["kind"] == "soft"])
        if c["hard_violation"]:
            base -= 1.0
        if c.get("eliminated"):
            base -= 2.0
        if c.get("idea_hits"):
            base += 0.2 * len(c["idea_hits"])
        c["score"] = round(base, 2)
        out.append(c)

    # 1. literal places from the inventory
    for f in features():
        hits = _feature_idea_hits(f, ideas)
        type_hit = f["ftype"] in hint_types
        key_hit = bool(set(f.get("keys", [])) & set(hint_words) | set(f.get("keys", [])) & set(content_words(line["text"])))
        if not (hits or type_hit or key_hit):
            continue
        why = []
        if hits:
            why.append("name carries " + ", ".join(hits))
        if type_hit:
            why.append(f"a {f['ftype']} — the line's words point at that class")
        if key_hit and not hits:
            why.append("keyword match on " + ", ".join(sorted(set(f.get("keys", [])) & (set(hint_words) | set(content_words(line["text"]))))))
        add({"id": f["id"], "category": "naming" if hits and not type_hit else "literal", "text": f["name"], "rationale": "; ".join(why) + (". " + f["notes"] if f["notes"] else ""), "lat": f["lat"], "lon": f["lon"], "elev": f["elev"], "state": f["state"], "region": f["region"], "owner": f["owner"], "access": f["access"], "car": f["car"], "ftype": f["ftype"], "flags": f["flags"], "tier": f["tier"], "source": f["source"] + ("" if f.get("gnis_verified") else " · NOT yet verified in GNIS"), "aliases": f.get("aliases", []), "idea_hits": hits, "conf": 2 if hits else 1, "gnis": bool(f.get("gnis_verified")), "manmade": "man-made" in f["flags"] or f["ftype"] in ("monument", "historic")})
    # 2. feature classes
    for t in sorted(hint_types):
        near = [f for f in features() if f["ftype"] == t and (not st["point"] or geo.haversine(st["point"], (f["lat"], f["lon"])) <= radius) and f["state"] not in elim]
        add({"id": f"class_{t}", "category": "feature_class", "text": f"Any {t}" + (f" within {radius:.0f} mi" if st["point"] else " still in play"), "rationale": f"{len(near)} known {t}{'s' if len(near) != 1 else ''} in the built-in inventory meet the current constraints" + ("; run fetch-data for the full GNIS list" if len(near) < 5 else ""), "count": len(near), "members": [{"name": f["name"], "lat": f["lat"], "lon": f["lon"], "id": f["id"]} for f in near[:30]], "tier": "unverified", "conf": 1})
    # 3. direction / action
    txt = line["text"].lower()
    nums = re.findall(r"\b(twenty|three|two|one|ten|forty|\d+)\b", txt)
    numval = {"one": 1, "two": 2, "three": 3, "ten": 10, "twenty": 20, "forty": 40}
    for n in nums:
        v = numval.get(n, int(n) if n.isdigit() else None)
        if v is not None and v <= 360:
            add({"id": f"dir_{v}", "category": "direction", "text": f"Bearing {v}° (and back bearing {geo.back_bearing(v):.0f}°)", "rationale": f"'{n}' read as a compass bearing; 'return' would make it {geo.back_bearing(v):.0f}°", "bearing": v, "conf": 2 if "degree" in txt else 1, "tier": "unverified"})
            add({"id": f"dist_{v}", "category": "direction", "text": f"Distance {v} (miles, feet, paces or minutes)", "rationale": "the number as a distance element — Posey said a distance element exists", "conf": 1, "tier": "unverified"})
    for verb, meaning in [("walk", "walk along the water — the line is a leg on foot"), ("round", "follow the river round the bend — direction of travel"), ("cast", "cast = throw a line, or cast a shadow / a bearing"), ("return", "turn around — back bearing from the previous heading"), ("east", "head east (90°) or 'in the east' — look east"), ("wait", "stop here — the checkpoint or the treasure waits"), ("guard", "stand guard = face outward; use her facing as the bearing"), ("foot", "start at the foot (base) of the feature"), ("beyond", "go past the limit — outside the map edge, past the marked trail"), ("find", "the endpoint verb — this line names where you finish")]:
        if verb in txt:
            add({"id": f"act_{verb}", "category": "direction", "text": meaning.split(" — ")[0].capitalize(), "rationale": meaning, "conf": 1, "tier": "unverified"})
    if "shadow" in txt or "sight" in txt:
        add({"id": "act_shadow", "category": "direction", "text": "Use a shadow or a sightline", "rationale": "shadow at a given time and date gives a bearing; 'sight' suggests a line of sight from a fixed point", "conf": 1, "tier": "unverified"})
    # 4. wordplay
    for w in content_words(line["text"]):
        if w in HIDDEN_WORDS:
            add({"id": f"hid_{w}", "category": "wordplay", "text": f"'{w}' hides: {', '.join(HIDDEN_WORDS[w])}", "rationale": "letters inside the word, in order or as an anagram", "conf": 1, "tier": "unverified"})
        if w in HOMOPHONES:
            add({"id": f"hom_{w}", "category": "wordplay", "text": HOMOPHONES[w], "rationale": "homophone / double meaning", "conf": 1, "tier": "unverified"})
    caps = re.findall(r"\b([A-Z][a-z]+)\b", line["text"][1:])
    for c in caps:
        add({"id": f"cap_{c}", "category": "wordplay", "text": f"'{c}' is capitalised mid-line — a proper noun", "rationale": "Posey said the Hole is a proper noun; capitals mid-line are deliberate", "conf": 2, "tier": "confirmed" if c.lower() == "hole" else "unverified"})
    # 5. naming & culture from aliases of nearby features
    for f in features():
        if not f.get("aliases"):
            continue
        if st["point"] and geo.haversine(st["point"], (f["lat"], f["lon"])) > max(radius, 60):
            continue
        for a in f["aliases"]:
            if any(idea_word in a.lower() for idea in ideas for idea_word in knowledge.NAME_PATTERNS.get(idea, [])) or any(k in a.lower() for k in hint_words):
                add({"id": f"alias_{f['id']}", "category": "naming", "text": f"{f['name']} — {a}", "rationale": "historical or indigenous name; translation commonly cited — verify with a tribal or historical source", "lat": f["lat"], "lon": f["lon"], "elev": f["elev"], "state": f["state"], "region": f["region"], "flags": f["flags"], "owner": f["owner"], "ftype": f["ftype"], "tier": "unverified", "conf": 1, "source": f["source"]})
    # 6. numeric
    idx = line_index(ref)
    before = sum(len(words(l["text"])) for l in poem_lines()[:idx])
    lw = words(line["text"])
    letters = re.sub(r"[^A-Za-z]", "", line["text"])
    add({"id": "num_pos", "category": "numeric", "text": f"Line {idx + 1} of {len(poem_lines())}; words {before + 1}–{before + len(lw)} of the poem; {len(letters)} letters", "rationale": "positions usable as page numbers, degrees or coordinates fragments", "conf": 1, "tier": "unverified"})
    lsum = sum(ord(ch) - 96 for ch in letters.lower())
    add({"id": "num_sum", "category": "numeric", "text": f"Letter-position sum {lsum}; word count {len(lw)}; first letters '{''.join(w[0] for w in lw)}'", "rationale": "A=1…Z=26 sum, acrostic; feed into the cipher scratchpad", "conf": 1, "tier": "unverified"})
    if idx + 1 in (20, 42) or before + 1 <= 42 <= before + len(lw):
        add({"id": "num_42", "category": "numeric", "text": "Word 42 of the poem falls in this line ('Hole' is the 42nd word)", "rationale": "42 = the parallel that is the Idaho–Utah and Oregon–California line; the community's '42' thread", "conf": 1, "tier": "circulating"})
    # 7. personal
    for hook in knowledge.PERSONAL:
        hk = set(content_words(hook))
        if hk & set(content_words(line["text"])) or any(k in hook.lower() for k in hint_words):
            add({"id": "pers_" + str(abs(hash(hook)) % 10000), "category": "personal", "text": hook.split(" — ")[0], "rationale": hook, "conf": 1, "tier": "unverified"})
    # 8. structural
    stage = {1: "framing / how to read", 2: "approach", 3: "construction (solvable from home)", 4: "site (boots on the ground)", 5: "warning / register"}.get(line["stanza"], "")
    add({"id": "struct", "category": "structural", "text": f"Not geography: stanza {line['stanza']} is {stage}", "rationale": "Posey said stanzas 1–3 are solvable from home and the poem opens with method; this line may instruct rather than locate", "conf": 2 if line["stanza"] in (1, 5) else 1, "tier": "confirmed" if line["stanza"] in (1, 5) else "unverified"})
    # 9. readings from other solves and imported records
    for s in store.list_solves():
        if s["id"] == solve["id"]:
            continue
        c = s["state"].get("lines", {}).get(ref)
        if c:
            add({"id": f"solve_{s['id']}", "category": c.get("category", "literal"), "text": c.get("text", ""), "rationale": f"{'Reference' if s['kind'] == 'reference' else 'Your'} solve “{s['name']}” reads it this way" + (f" — {c.get('rationale')}" if c.get("rationale") else ""), "lat": c.get("lat"), "lon": c.get("lon"), "elev": c.get("elev"), "conf": c.get("conf", 1), "tier": c.get("tier", "fan" if s["kind"] == "reference" else "reported"), "source": s.get("source") or s["name"], "flags": c.get("flags", [])})
    for r in store.rows("SELECT * FROM rumors"):
        ls = store.unj(r["lines_json"], [])
        if any(l.get("ref") == ref for l in ls):
            add({"id": r["id"], "category": "literal" if r["tier"] in ("reported",) else "personal" if "posey" in (r["text"] or "").lower()[:40] else "literal", "text": (r["text"] or "")[:160], "rationale": f"{TIER_LABEL.get(r['tier'], r['tier'])}; source: {r.get('source') or 'unknown'}" + (f" ({r['date']})" if r.get("date") else ""), "tier": r["tier"], "conf": 1, "source": r.get("source"), "origin": r.get("origin")})
    for b in store.rows("SELECT * FROM book"):
        tags = store.unj(b["tags_json"], [])
        if ref in tags or any(k in (b["text"] or "").lower() for k in hint_words):
            add({"id": b["id"], "category": "personal", "text": (b["title"] or b["text"] or "")[:120], "rationale": (b["text"] or "")[:220] + (f" (p. {b['page']})" if b.get("page") else ""), "tier": b.get("tier") or "fan", "conf": 1, "source": b.get("source")})
    if extra:
        for e in extra:
            add(e)
    # de-duplicate by id, keep highest score
    best = {}
    for c in out:
        if c["id"] not in best or c["score"] > best[c["id"]]["score"]:
            best[c["id"]] = c
    res = sorted(best.values(), key=lambda c: -c["score"])
    total = len(res)
    if hard and (seed["states"] or seed["bbox"] or seed["point"]):
        res = [c for c in res if c["seed_match"] or c.get("lat") is None]
    if hide:
        res = [c for c in res if not c["hard_violation"] and not c.get("eliminated")]
    # rarity: how uncommon is each literal's type inside the active radius vs the state
    for c in res:
        if c.get("ftype") and c.get("lat") is not None:
            same_state = [f for f in features() if f["ftype"] == c["ftype"] and f["state"] == c.get("state")]
            near = [f for f in same_state if st["point"] and geo.haversine(st["point"], (f["lat"], f["lon"])) <= radius] if st["point"] else []
            if len(same_state) <= 3:
                c["rarity"] = f"only {len(same_state)} known {c['ftype']}{'s' if len(same_state) != 1 else ''} in {c.get('state')} in the inventory" + (f", {len(near)} inside your radius" if st["point"] else "")
    byidea = {i: len([c for c in res if i in (c.get("idea_hits") or [])]) for i in ideas}
    return {"ref": ref, "line": line, "constraints": st, "radius": radius, "hard_filter": hard, "hide_violations": hide, "ideas": ideas, "idea_counts": byidea, "hint_types": sorted(hint_types), "shown": len(res), "total": total, "statements": [{"id": s["id"], "text": s["text"], "tier": s["tier"], "date": s.get("date"), "kind": s.get("kind"), "venue": s.get("venue"), "stance": next((l.get("stance") for l in s["lines"] if l.get("ref") == ref), "supports")} for s in stmts], "suggestions": res[:120], "categories": CATEGORIES}


# ---------------------------------------------------------------- scoring

def score(solve, ignore_seed=False):
    seed = seed_info(solve)
    lines = solve["state"].get("lines", {})
    per = {}
    poem_part, seed_part = 0.0, 0.0
    for ref, c in lines.items():
        w = CAT_WEIGHT.get(c.get("category", "literal"), .5) * TIER_WEIGHT.get(c.get("tier", "unverified"), .4) * (0.6 + 0.2 * (c.get("conf") or 1))
        sb = 0.0
        if not ignore_seed and c.get("lat") is not None:
            st = geo.state_of(c["lat"], c["lon"])
            if (seed["states"] and st in seed["states"]) or (seed["bbox"] and geo.in_bbox(c["lat"], c["lon"], seed["bbox"])) or (seed["point"] and geo.haversine(seed["point"], (c["lat"], c["lon"])) <= 40):
                sb = 0.35 * (0.6 + 0.2 * (c.get("conf") or 1))
        per[ref] = {"poem": round(w, 2), "seed": round(sb, 2)}
        poem_part += w
        seed_part += sb
    pen = 0.0
    for x in contradictions(solve):
        if not x.get("overridden"):
            pen += 1.0 if x["severity"] == "hard" else 0.4
    total = poem_part + seed_part - pen
    return {"total": round(total, 2), "poem": round(poem_part, 2), "seed": round(seed_part, 2), "penalty": round(pen, 2), "seed_share": round(seed_part / (poem_part + seed_part) * 100) if (poem_part + seed_part) else 0, "per_line": per, "lines": len(lines)}


def seed_dependence(solve):
    with_seed = score(solve)
    without = score(solve, ignore_seed=True)
    # unconstrained rank: compare against all user solves scored without seeds
    ranks = sorted([(score(s, ignore_seed=True)["total"], s["id"]) for s in store.list_solves() if s["kind"] != "reference"], reverse=True)
    rank = next((i + 1 for i, (t, sid) in enumerate(ranks) if sid == solve["id"]), None)
    return {"with_seed": with_seed, "without_seed": without, "unconstrained_rank": rank, "of": len(ranks), "verdict": ("The seed is doing most of the work — this solve has not proved anything yet." if with_seed["seed_share"] >= 40 else "The poem is carrying the score; the seed is a preference, not a crutch.") if with_seed["seed"] else "No seed — the score is all poem."}


# ---------------------------------------------------------------- contradictions

def contradictions(solve):
    out = []
    lines = poem_lines()
    st_lines = solve["state"].get("lines", {})
    overrides = solve["state"].get("overrides", {})
    active_rules = {r["id"]: r for r in rules() if r["enabled"]}
    pins = pinned(solve)
    elim = eliminated_states()

    def add(code, severity, refs, text, rule=None):
        o = overrides.get(code)
        out.append({"code": code, "severity": severity, "refs": refs, "text": text, "rule": rule, "overridden": bool(o), "note": (o or {}).get("note", "")})

    # consecutive pinned lines far apart
    for (r1, c1), (r2, c2) in zip(pins, pins[1:]):
        d = geo.haversine((c1["lat"], c1["lon"]), (c2["lat"], c2["lon"]))
        i1, i2 = line_index(r1), line_index(r2)
        s1, s2 = _line(r1)["stanza"], _line(r2)["stanza"]
        if s1 == 2 and s2 == 2 and d > 3 and "s_walk" in active_rules:
            add(f"walk_{r1}_{r2}", "soft", [r1, r2], f"{r1} → {r2} is {d:.1f} mi; stanza 2 reads as a walk (Posey: walking distance between the S2L2 and S2L3 clues).", "s_walk")
        elif d > 60 and i2 - i1 <= 2 and "s_order" in active_rules:
            add(f"gap_{r1}_{r2}", "soft", [r1, r2], f"{r1} → {r2} is {d:.0f} mi apart on consecutive clues; the poem implies a compact route ('not a great distance').", "s_order")
        elif s2 == 4 and d > 1.5 and "s_mile" in active_rules and s1 == 4:
            add(f"hike_{r1}_{r2}", "soft", [r1, r2], f"{r1} → {r2} is {d:.1f} mi inside stanza 4; no more than about a mile of hiking to determine the location.", "s_mile")
    # doubling back
    for a, b, c in zip(pins, pins[1:], pins[2:]):
        b1 = geo.bearing((a[1]["lat"], a[1]["lon"]), (b[1]["lat"], b[1]["lon"]))
        b2 = geo.bearing((b[1]["lat"], b[1]["lon"]), (c[1]["lat"], c[1]["lon"]))
        d1 = geo.haversine((a[1]["lat"], a[1]["lon"]), (b[1]["lat"], b[1]["lon"]))
        d2 = geo.haversine((b[1]["lat"], b[1]["lon"]), (c[1]["lat"], c[1]["lon"]))
        turn = abs((b2 - b1 + 180) % 360 - 180)
        if turn > 150 and d1 > 5 and d2 > 5 and "s_order" in active_rules:
            add(f"back_{a[0]}_{c[0]}", "soft", [a[0], b[0], c[0]], f"The route doubles back at {b[0]} ({turn:.0f}° turn over {d1:.0f} and {d2:.0f} mi) — hard to square with consecutive clues.", "s_order")
    # field presence before stanza 4
    if "s_botg" in active_rules:
        for ref, c in st_lines.items():
            if _line(ref) and _line(ref)["stanza"] <= 3 and c.get("field"):
                add(f"field_{ref}", "soft", [ref], f"{ref} is marked as needing you on the ground, but stanzas 1–3 are solvable from home.", "s_botg")
    # private / hard flags on pinned points
    for ref, c in st_lines.items():
        for r in rule_flags(c):
            if r["kind"] == "hard":
                add(f"rule_{r['rule']}_{ref}", "hard", [ref], f"{ref} “{c.get('text', '')}” trips a hard rule: {r['text']} ({r['why']}).", r["rule"])
        if c.get("lat") is not None and geo.state_of(c["lat"], c["lon"]) in elim:
            add(f"elim_{ref}", "hard", [ref], f"{ref} sits in an eliminated state ({geo.state_of(c['lat'], c['lon'])}).", "s_states")
    # man-made count
    mm = [ref for ref, c in st_lines.items() if c.get("manmade")]
    if len(mm) > 1 and "s_manmade" in active_rules:
        add("manmade", "soft", mm, f"{len(mm)} lines carry a man-made implication ({', '.join(mm)}); Posey said one clue does, and only one.", "s_manmade")
    # distance element present?
    if len(st_lines) >= 8 and "s_distance" in active_rules and not any(c.get("category") == "direction" and re.search(r"\d", c.get("text", "")) for c in st_lines.values()):
        add("nodistance", "soft", [], "Eight or more lines committed and none carries a distance element; Posey said one exists.", "s_distance")
    # elevation jumps
    for (r1, c1), (r2, c2) in zip(pins, pins[1:]):
        if c1.get("elev") and c2.get("elev") and abs(c1["elev"] - c2["elev"]) > 3000 and _line(r2)["stanza"] >= 2:
            add(f"elev_{r1}_{r2}", "soft", [r1, r2], f"{r1} → {r2} climbs or drops {abs(c1['elev'] - c2['elev']):,} ft between consecutive clues.", None)
    # backward propagation: a later pin constrains an earlier one
    for i in range(len(pins) - 1, 0, -1):
        r2, c2 = pins[i]
        for j in range(i - 1, -1, -1):
            r1, c1 = pins[j]
            d = geo.haversine((c1["lat"], c1["lon"]), (c2["lat"], c2["lon"]))
            if d > 120 and _line(r2)["stanza"] >= 3 and _line(r1)["stanza"] >= 2 and st_lines[r1].get("locked"):
                add(f"backprop_{r1}_{r2}", "soft", [r1, r2], f"Your later choice at {r2} is {d:.0f} mi from locked {r1}; if {r2} holds, {r1} cannot.", "s_order")
                break
    return out


# ---------------------------------------------------------------- reactions to a commit

def _survivors(solve, ref):
    s = suggestions(solve, ref)
    lits = [c for c in s["suggestions"] if c.get("lat") is not None and not c["hard_violation"] and not c.get("eliminated")]
    st = s["constraints"]
    if st["point"]:
        lits = [c for c in lits if c.get("dist_active", 0) <= s["radius"]]
    return len(lits), max([c["score"] for c in s["suggestions"]] or [0])


def react(solve_before, solve_after, ref):
    """Compare downstream and upstream health before/after one commit."""
    lines = poem_lines()
    idx = line_index(ref)
    changes = []
    for l in lines:
        if l["ref"] == ref or l["ref"] in solve_after["state"].get("lines", {}):
            continue
        nb, _ = _survivors(solve_before, l["ref"])
        na, _ = _survivors(solve_after, l["ref"])
        if nb != na:
            verdict = "nearly impossible" if na <= 1 else "tight" if na <= 4 else "open"
            changes.append({"ref": l["ref"], "before": nb, "after": na, "text": f"{l['ref']}: {nb} → {na} literal candidates survive ({verdict})", "direction": "down" if na < nb else "up"})
    cb = {c["code"] for c in contradictions(solve_before)}
    ca = contradictions(solve_after)
    new_conf = [c for c in ca if c["code"] not in cb]
    sb, sa = score(solve_before), score(solve_after)
    return {"ref": ref, "changes": changes, "new_conflicts": new_conf, "score_before": sb["total"], "score_after": sa["total"], "summary": _react_summary(ref, changes, new_conf, sb, sa)}


def _react_summary(ref, changes, conflicts, sb, sa):
    parts = []
    downs = [c for c in changes if c["direction"] == "down" and c["after"] <= 1]
    ups = [c for c in changes if c["direction"] == "up"]
    if downs:
        parts.append(f"Committing {ref} pushed {', '.join(c['ref'] for c in downs)} from plausible to nearly impossible.")
    tight = [c for c in changes if c["direction"] == "down" and 1 < c["after"] <= 4]
    if tight:
        parts.append(f"It narrowed {', '.join(c['ref'] for c in tight)} to a handful of candidates.")
    if ups:
        parts.append(f"It strengthened {', '.join(c['ref'] for c in ups)}.")
    for x in conflicts:
        parts.append("New conflict: " + x["text"])
    parts.append(f"Score {sb['total']} → {sa['total']}.")
    return " ".join(parts)


# ---------------------------------------------------------------- weakest links, assumptions, blind spots

def weakest_links(solve):
    com = committed(solve)
    pins_ = pinned(solve)
    out = []
    for i, (ref, c) in enumerate(com):
        load = 0
        if c.get("lat") is not None:
            # downstream pins within 60 mi depend on this as the active point
            for ref2, c2 in pins_:
                if line_index(ref2) > line_index(ref) and geo.haversine((c["lat"], c["lon"]), (c2["lat"], c2["lon"])) <= 60:
                    load += 1
        load += max(0, len(com) - i - 1) * 0.15
        conf = (c.get("conf") or 1) / 3
        gap = round(load / max(1, len(com)) * 3 - conf * 3, 2)
        out.append({"ref": ref, "text": c.get("text", ""), "load": round(load, 2), "conf": c.get("conf") or 1, "gap": gap, "locked": bool(c.get("locked"))})
    out.sort(key=lambda x: -x["gap"])
    return out


def assumptions(solve):
    out = []
    for w in weakest_links(solve):
        c = solve["state"]["lines"][w["ref"]]
        cheap = 1
        test = "Re-read the line against the text; write down what would have to be true."
        if c.get("lat") is not None:
            cheap = 1
            test = f"Map check: does '{c.get('text')}' exist at {c['lat']:.4f}, {c['lon']:.4f} in GNIS, and does the land record show public access? (desk, minutes)"
            if not c.get("gnis"):
                test = "GNIS existence check first — this name is not yet verified in federal records. " + test
        elif c.get("category") in ("wordplay", "numeric"):
            cheap = 2
            test = "Does the reading produce a specific place or bearing? If it does not narrow anything, it is decoration, not a clue."
        elif c.get("category") == "direction" and c.get("bearing") is not None:
            cheap = 1
            test = f"Project {c['bearing']}° and {geo.back_bearing(c['bearing']):.0f}° from the previous pin in the bearing workspace; does anything named land within a mile?"
        elif c.get("category") == "structural":
            cheap = 1
            test = "Nothing to test — but if this line is structural, no downstream line may lean on it."
        kills = "A federal name record with no such feature, a private-land or fee boundary, or a distance to the next pin the poem does not allow."
        out.append({"ref": w["ref"], "assumption": f"{w['ref']} means “{c.get('text', '')}”", "load": w["load"], "cost": cheap, "test": test, "would_prove_wrong": kills})
    out.sort(key=lambda a: (a["cost"], -a["load"]))
    return out


def blind_spots():
    cnt = Counter()
    for s in store.list_solves():
        if s["kind"] == "reference":
            continue
        for c in s["state"].get("lines", {}).values():
            cnt[c.get("category", "literal")] += 1
    total = sum(cnt.values()) or 1
    rows_ = [{"category": k, "label": lb, "count": cnt.get(k, 0), "share": round(cnt.get(k, 0) / total * 100)} for k, lb in CATEGORIES]
    under = [r for r in rows_ if r["share"] < 8]
    return {"counts": rows_, "underused": under, "total": total}


# ---------------------------------------------------------------- seed suggestion (clustering)

def seed_suggest(solve):
    if solve["state"].get("seed", {}).get("states") or solve["state"].get("seed", {}).get("region"):
        return None
    com = dict(committed(solve))
    if len(com) < 2:
        return None
    reg = Counter()
    sample = defaultdict(list)
    for l in poem_lines():
        if l["ref"] in com or l["stanza"] in (1, 5):
            continue
        s = suggestions(solve, l["ref"])
        for c in s["suggestions"][:25]:
            if c.get("lat") is None or c["hard_violation"] or c.get("eliminated"):
                continue
            r = region_of(c["lat"], c["lon"])
            key = r["id"] if r else (c.get("state") or "?")
            reg[key] += c["score"]
            if len(sample[key]) < 3:
                sample[key].append(c["text"])
    top = reg.most_common(3)
    if not top:
        return None
    total = sum(reg.values()) or 1
    names = {r["id"]: r["name"] for r in regions()}
    return {"corridors": [{"id": k, "name": names.get(k, k), "share": round(v / total * 100), "examples": sample[k]} for k, v in top], "text": f"Of the readings still standing for the uncommitted lines, most land in {names.get(top[0][0], top[0][0])}" + (f" and {names.get(top[1][0], top[1][0])}" if len(top) > 1 else "") + ". You can seed either, or keep working blind."}


# ---------------------------------------------------------------- automatic solve search

def auto_search(solve, beam=120, top=20, per_line=10):
    lines = [l for l in poem_lines() if 2 <= l["stanza"] <= 4]
    cands = {}
    for l in lines:
        s = suggestions(solve, l["ref"], radius_mi=400)
        lits = [c for c in s["suggestions"] if c.get("lat") is not None and not c["hard_violation"] and not c.get("eliminated")]
        seen, keep = set(), []
        for c in lits:
            if c["text"] in seen:
                continue
            seen.add(c["text"])
            keep.append(c)
            if len(keep) >= per_line:
                break
        cands[l["ref"]] = keep
    beams = [([], 0.0)]
    for l in lines:
        nxt = []
        for path, sc in beams:
            last = next((p for p in reversed(path) if p is not None), None)
            for c in cands[l["ref"]] + [None]:
                if c is None:
                    nxt.append((path + [None], sc - 0.6))
                    continue
                s2 = sc + 0.8 + 0.3 * c.get("conf", 1) + 0.2 * len(c.get("idea_hits") or []) - 0.3 * len(c["rules"])
                if last is not None:
                    d = geo.haversine((last["lat"], last["lon"]), (c["lat"], c["lon"]))
                    if l["stanza"] == 2 and _line(last["_ref"])["stanza"] == 2:
                        s2 -= 0 if d <= 3 else min(3, d / 5)
                    else:
                        s2 -= min(4, d / 25)
                c = dict(c)
                c["_ref"] = l["ref"]
                nxt.append((path + [c], s2))
        nxt.sort(key=lambda x: -x[1])
        beams = nxt[:beam]
    results = []
    for path, sc in beams[:top]:
        pins_ = [p for p in path if p]
        if len(pins_) < 4:
            continue
        regs = Counter((region_of(p["lat"], p["lon"]) or {}).get("name", geo.state_of(p["lat"], p["lon"])) for p in pins_)
        results.append({"score": round(sc, 2), "region": regs.most_common(1)[0][0] if regs else "?", "placed": len(pins_), "lines": {p["_ref"]: {"text": p["text"], "category": p["category"], "lat": p["lat"], "lon": p["lon"], "elev": p.get("elev"), "conf": p.get("conf", 1), "tier": p.get("tier"), "rationale": p.get("rationale", ""), "flags": p.get("flags", []), "ftype": p.get("ftype"), "owner": p.get("owner"), "source": p.get("source")} for p in pins_}})
    return results


# ---------------------------------------------------------------- reverse mode

def reverse(solve, lat, lon, name="endpoint"):
    lines = [l for l in poem_lines() if 2 <= l["stanza"] <= 4]
    tmp = {"id": solve["id"], "name": solve["name"], "kind": solve["kind"], "state": {"lines": {}, "seed": {"endpoint": {"lat": lat, "lon": lon, "name": name}}, "radius": {}, "overrides": {}}}
    out = []
    point = (lat, lon)
    for l in reversed(lines):
        radius = 2 if l["stanza"] == 4 else 15 if l["stanza"] == 3 else 40
        s = suggestions(tmp, l["ref"], radius_mi=400)
        lits = [c for c in s["suggestions"] if c.get("lat") is not None and not c["hard_violation"] and not c.get("eliminated")]
        for c in lits:
            c["_d"] = geo.haversine(point, (c["lat"], c["lon"]))
        lits.sort(key=lambda c: (c["_d"] > radius, -c["score"] + c["_d"] / 50))
        best = lits[0] if lits else None
        others = [c for c in s["suggestions"] if c.get("lat") is None][:3]
        stretch = best is None or best["_d"] > radius or best["score"] < 0.6
        out.append({"ref": l["ref"], "text": l["text"], "would_have_to_mean": best["text"] if best else (others[0]["text"] if others else "nothing in the inventory"), "distance_mi": round(best["_d"], 1) if best else None, "stretch": stretch, "why": (best or {}).get("rationale", "no named feature near the endpoint fits this line — a non-geographic reading would be needed"), "alternatives": [c["text"] for c in lits[1:4]] + [c["text"] for c in others[:2]]})
        if best and not stretch:
            point = (best["lat"], best["lon"])
            tmp["state"]["lines"][l["ref"]] = {"text": best["text"], "lat": best["lat"], "lon": best["lon"], "category": best["category"], "conf": 1}
    out.reverse()
    stretches = sum(1 for o in out if o["stretch"])
    return {"endpoint": {"lat": lat, "lon": lon, "name": name}, "lines": out, "stretches": stretches, "verdict": f"{stretches} of {len(out)} lines need a stretch for this endpoint to hold." + (" That is a lot — the hunch is probably wrong." if stretches >= len(out) / 2 else " Worth pursuing.")}


# ---------------------------------------------------------------- whole-poem feasibility

def feasibility():
    needs = [("surge", "a spring, hot spring, waterfall or pool for 'hope surges'", lambda f: f["ftype"] in ("hotspring", "spring", "waterfall", "pool")),
             ("hole", "a natural Hole (proper noun)", lambda f: f["ftype"] == "hole" or "hole" in f["keys"]),
             ("gate", "gates / a pass / a narrows for 'ancient gates'", lambda f: f["ftype"] in ("gate", "pass")),
             ("granite", "granite for 'double arcs on granite bold'", lambda f: "granite" in f["keys"] or "granite" in (f["notes"] or "").lower()),
             ("bear", "a bear / Ursa name", lambda f: any("bear" in n.lower() or "ursa" in n.lower() for n in [f["name"]] + f["aliases"])),
             ("bride", "a bride / wedding / maiden name or face", lambda f: "bride" in f["keys"] or "wedding" in f["keys"] or f["ftype"] == "face")]
    elim = eliminated_states()
    out = []
    for r in regions():
        fs = [f for f in features() if r["bbox"] and geo.in_bbox(f["lat"], f["lon"], r["bbox"])]
        usable = [f for f in fs if not any(x in f["flags"] for x in ("private", "cave", "graves", "battle", "buildings"))]
        checks = []
        killed_by = None
        for code, label, fn in needs:
            have = [f["name"] for f in usable if fn(f)]
            ok = bool(have)
            checks.append({"need": code, "label": label, "ok": ok, "have": have[:4]})
            if not ok and killed_by is None and code in ("hole", "granite"):
                killed_by = label
        states = set(r["states"].split(","))
        if states & elim:
            killed_by = f"eliminated state ({', '.join(states & elim)})"
        thin = len(fs) < 6
        out.append({"region": r["name"], "id": r["id"], "features": len(fs), "usable": len(usable), "checks": checks, "killed_by": killed_by, "thin": thin, "verdict": "eliminated" if killed_by and "eliminated" in killed_by else ("fails: " + killed_by) if killed_by else ("thin coverage — cannot judge" if thin else "could support a complete solve")})
    return out


# ---------------------------------------------------------------- rescoring on new information

def rescore_all(reason="manual"):
    deltas = []
    for s in store.list_solves():
        sc = score(s)
        cons = contradictions(s)
        prev = s["state"].get("last_score")
        prev_codes = set(s["state"].get("last_conflicts", []))
        codes = {c["code"] for c in cons}
        affected = sorted({r for c in cons if c["code"] not in prev_codes for r in c["refs"]})
        if prev is None or abs(prev - sc["total"]) > 0.01 or codes != prev_codes:
            deltas.append({"solve": s["id"], "name": s["name"], "kind": s["kind"], "before": prev, "after": sc["total"], "affected": affected, "died": sc["total"] < 0 and (prev or 0) >= 0, "new_conflicts": [c["text"] for c in cons if c["code"] not in prev_codes]})
            store.log_history("rescore:" + reason, s["id"], prev, sc["total"], {"affected": affected})
        s["state"]["last_score"] = sc["total"]
        s["state"]["last_conflicts"] = sorted(codes)
        store.save_solve(s)
    return deltas


# ---------------------------------------------------------------- field export ordering

def field_stops(solve):
    pins_ = pinned(solve)
    if not pins_:
        return []
    remaining = list(pins_)
    order = [remaining.pop(0)]
    while remaining:
        last = order[-1][1]
        remaining.sort(key=lambda p: geo.haversine((last["lat"], last["lon"]), (p[1]["lat"], p[1]["lon"])))
        order.append(remaining.pop(0))
    stops = []
    for i, (ref, c) in enumerate(order):
        d = geo.haversine((order[i - 1][1]["lat"], order[i - 1][1]["lon"]), (c["lat"], c["lon"])) if i else 0
        drive_min = round(d * 1.4 / 40 * 60) if d else 0
        season = [s["text"] for s in knowledge.SEASON if any(m.lower() in (c.get("text") or "").lower() for m in s["match"])]
        stops.append({"stop": i + 1, "ref": ref, "name": c.get("text"), "lat": c["lat"], "lon": c["lon"], "elev": c.get("elev"), "expect": c.get("rationale", ""), "why": c.get("note", ""), "drive_mi": round(d, 1), "drive_min": drive_min, "access": c.get("access") or "unknown — check the access layer", "car": c.get("car") or "unknown", "owner": c.get("owner") or "unknown", "hike": "under a mile if the S4 reading holds" if _line(ref)["stanza"] == 4 else "to the feature", "cell": "unknown — assume none", "season": season, "confirm": c.get("confirm", "Photograph the feature; note anything paired, arched, carved or hollow."), "kill": c.get("kill", "The feature is not there, is on private or fee land, or needs gear.")})
    return stops
