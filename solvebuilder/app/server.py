"""Local web server: serves the interface and a JSON API on localhost only."""
import json
import os
import re
import threading
import time
import traceback
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from . import ai, engine, geo, importer, knowledge, monitor, public_data, store

HERE = os.path.dirname(os.path.abspath(__file__))
UI = os.path.join(os.path.dirname(HERE), "ui", "index.html")
JOBS = {}


def _snapshot(solve):
    h = solve["state"].setdefault("history", [])
    h.append({"ts": time.time(), "lines": json.loads(json.dumps(solve["state"].get("lines", {}))), "seed": json.loads(json.dumps(solve["state"].get("seed", {})))})
    del h[:-60]
    solve["state"]["redo"] = []


def solve_view(solve):
    sc = engine.score(solve)
    return {"solve": solve, "score": sc, "constraints": engine.constraint_state(solve), "contradictions": engine.contradictions(solve), "weakest": engine.weakest_links(solve), "seed": engine.seed_dependence(solve), "seed_suggest": engine.seed_suggest(solve) if len(solve["state"].get("lines", {})) >= 2 else None, "stops": engine.field_stops(solve)}


def overview():
    poem = store.get_poem()
    solves = []
    for s in store.list_solves():
        sc = engine.score(s)
        solves.append({"id": s["id"], "name": s["name"], "kind": s["kind"], "source": s.get("source"), "parent_id": s.get("parent_id"), "fork_ref": s.get("fork_ref"), "score": sc["total"], "seed_share": sc["seed_share"], "lines": sc["lines"], "updated": s["updated"], "seed": engine.seed_info(s)["label"]})
    return {"poem": poem, "solves": solves, "rules": engine.rules(), "regions": [{"id": r["id"], "name": r["name"], "states": r["states"], "status": r["status"], "bbox": r["bbox"]} for r in engine.regions()], "ai": ai.available(), "gnis": public_data.gnis_status(), "last_import": store.setting("last_import"), "blind_spots": engine.blind_spots(), "categories": engine.CATEGORIES, "tiers": engine.TIER_LABEL, "states": geo.STATE_NAMES, "eliminated": sorted(engine.eliminated_states()), "monitor_new": store.rows("SELECT COUNT(*) n FROM monitor_items WHERE seen=0")[0]["n"], "feature_count": store.rows("SELECT COUNT(*) n FROM features")[0]["n"], "statement_count": store.rows("SELECT COUNT(*) n FROM statements")[0]["n"], "mapstates": {k[len("mapstate_"):]: store.unj(v) for k, v in [(r["key"], r["value"]) for r in store.rows("SELECT key, value FROM settings WHERE key LIKE 'mapstate_%'")]}}


def api(method, path, q, body):
    parts = [p for p in path.split("/") if p][1:]  # drop 'api'
    def sv(sid):
        s = store.get_solve(sid)
        if not s:
            raise KeyError("no such solve")
        return s
    if parts == ["state"]:
        return overview()
    if parts == ["poem"] and method == "POST":
        p = store.save_poem(body.get("title", "Poem"), body.get("raw", ""))
        engine.ensure_knowledge()
        return p
    if parts[:1] == ["solve"]:
        if len(parts) == 2 and parts[1] == "new" and method == "POST":
            s = store.new_solve(body.get("name") or "Untitled solve", seed=body.get("seed") or {})
            if body.get("adopt"):
                s["state"]["lines"] = body["adopt"]
                store.save_solve(s)
            store.log_history("new solve", s["id"])
            return solve_view(s)
        sid = parts[1]
        s = sv(sid)
        action = parts[2] if len(parts) > 2 else ""
        if method == "GET" and not action:
            return solve_view(s)
        if action == "suggest":
            ref = q.get("ref")
            radius = float(q["radius"]) if q.get("radius") else None
            extra = None
            if q.get("ai"):
                g = ai.generate(s, ref, n=int(q.get("n", 15)), instruction=q.get("instruction", ""))
                extra = g.get("readings") if isinstance(g, dict) else None
                if isinstance(g, dict) and (g.get("error") or g.get("unavailable")):
                    return {"error": g.get("error") or g.get("unavailable")}
                for e in extra or []:
                    e["id"] = "ai_" + store.uid("")[2:]
            return engine.suggestions(s, ref, radius_mi=radius, extra=extra)
        if action == "commit" and method == "POST":
            before = json.loads(json.dumps(s))
            _snapshot(s)
            ref = body["ref"]
            c = dict(body["candidate"])
            c["conf"] = int(body.get("conf") or c.get("conf") or 1)
            c["ts"] = time.time()
            if body.get("note"):
                c["note"] = body["note"]
            if c.get("lat") is not None and not c.get("owner"):
                c["owner"] = None
            if c.get("category") == "direction" and c.get("bearing") is None:
                m = re.search(r"(\d{1,3})°", c.get("text", ""))
                if m:
                    c["bearing"] = int(m.group(1))
            s["state"].setdefault("lines", {})[ref] = c
            store.save_solve(s)
            r = engine.react(before, s, ref)
            store.log_history("commit " + ref, sid, r["score_before"], r["score_after"], c.get("text", ""))
            return {"view": solve_view(s), "reaction": r}
        if action == "uncommit" and method == "POST":
            _snapshot(s)
            s["state"].get("lines", {}).pop(body["ref"], None)
            store.save_solve(s)
            return solve_view(s)
        if action == "update" and method == "POST":
            ref = body["ref"]
            c = s["state"].get("lines", {}).get(ref)
            if c:
                for k in ("conf", "note", "locked", "field", "manmade", "confirm", "kill"):
                    if k in body:
                        c[k] = body[k]
                store.save_solve(s)
            return solve_view(s)
        if action == "radius" and method == "POST":
            s["state"].setdefault("radius", {})[body["ref"]] = float(body["radius"])
            store.save_solve(s)
            return {"ok": True}
        if action == "options" and method == "POST":
            for k in ("hard_filter", "hide_violations"):
                if k in body:
                    s["state"][k] = bool(body[k])
            store.save_solve(s)
            return solve_view(s)
        if action == "seed" and method == "POST":
            _snapshot(s)
            s["state"]["seed"] = body.get("seed") or {}
            store.save_solve(s)
            return solve_view(s)
        if action == "override" and method == "POST":
            ov = s["state"].setdefault("overrides", {})
            if body.get("clear"):
                ov.pop(body["code"], None)
            else:
                ov[body["code"]] = {"note": body.get("note", ""), "ts": time.time()}
            store.save_solve(s)
            return solve_view(s)
        if action == "undo" and method == "POST":
            h = s["state"].get("history", [])
            if h:
                snap = h.pop()
                s["state"].setdefault("redo", []).append({"lines": s["state"].get("lines", {}), "seed": s["state"].get("seed", {})})
                s["state"]["lines"], s["state"]["seed"] = snap["lines"], snap["seed"]
                store.save_solve(s)
            return solve_view(s)
        if action == "redo" and method == "POST":
            r = s["state"].get("redo", [])
            if r:
                snap = r.pop()
                s["state"].setdefault("history", []).append({"ts": time.time(), "lines": s["state"].get("lines", {}), "seed": s["state"].get("seed", {})})
                s["state"]["lines"], s["state"]["seed"] = snap["lines"], snap["seed"]
                store.save_solve(s)
            return solve_view(s)
        if action == "fork" and method == "POST":
            ref = body.get("ref")
            lines = {}
            for l in engine.poem_lines():
                if ref and engine.line_index(l["ref"]) >= engine.line_index(ref):
                    break
                if l["ref"] in s["state"].get("lines", {}):
                    lines[l["ref"]] = json.loads(json.dumps(s["state"]["lines"][l["ref"]]))
            if not ref:
                lines = json.loads(json.dumps(s["state"].get("lines", {})))
            st = {"lines": lines, "history": [], "overrides": {}, "notes": {}, "radius": dict(s["state"].get("radius", {})), "hard_filter": s["state"].get("hard_filter", False), "hide_violations": s["state"].get("hide_violations", False)}
            ns = store.new_solve(body.get("name") or f"{s['name']} — fork at {ref or 'end'}", seed=s["state"].get("seed"), state=st, parent_id=sid, fork_ref=ref)
            store.log_history("fork", ns["id"], detail=f"from {sid} at {ref}")
            return solve_view(ns)
        if action == "rename" and method == "POST":
            s["name"] = body.get("name") or s["name"]
            store.save_solve(s)
            return solve_view(s)
        if action == "delete" and method == "POST":
            store.delete_solve(sid)
            return {"ok": True}
        if action == "compare":
            other = sv(parts[3])
            lines = []
            for l in engine.poem_lines():
                a = s["state"].get("lines", {}).get(l["ref"])
                b = other["state"].get("lines", {}).get(l["ref"])
                lines.append({"ref": l["ref"], "text": l["text"], "a": a, "b": b, "differs": bool(a or b) and ((a or {}).get("text") != (b or {}).get("text"))})
            return {"a": {"id": s["id"], "name": s["name"], "score": engine.score(s)}, "b": {"id": other["id"], "name": other["name"], "score": engine.score(other), "kind": other["kind"]}, "lines": lines, "fork_at": next((x["ref"] for x in lines if x["differs"]), None)}
        if action == "assumptions":
            return {"assumptions": engine.assumptions(s), "weakest": engine.weakest_links(s)}
        if action == "auto" and method == "POST":
            res = engine.auto_search(s, top=int(body.get("top", 20)))
            out = {"results": res}
            if body.get("ai") and res:
                out["ai"] = ai.rank_auto(s, res)
            return out
        if action == "reverse" and method == "POST":
            rev = engine.reverse(s, float(body["lat"]), float(body["lon"]), body.get("name", "endpoint"))
            if body.get("ai"):
                rev["ai"] = ai.reverse_narrative(s, rev)
            return rev
        if action == "field" and method == "GET":
            return field_html(s)
        if action == "finding" and method == "POST":
            store.upsert("findings", {"id": store.uid("fd"), "solve_id": sid, "ref": body.get("ref"), "lat": body.get("lat"), "lon": body.get("lon"), "text": body.get("text", ""), "verdict": body.get("verdict", ""), "created": time.time()})
            c = s["state"].get("lines", {}).get(body.get("ref"))
            if c and body.get("verdict") in ("confirmed", "killed"):
                c["field_verdict"] = body["verdict"]
                c["conf"] = 3 if body["verdict"] == "confirmed" else 0
                store.save_solve(s)
            return {"ok": True, "findings": store.rows("SELECT * FROM findings WHERE solve_id=? ORDER BY created DESC", (sid,))}
        if action == "findings":
            return store.rows("SELECT * FROM findings WHERE solve_id=? ORDER BY created DESC", (sid,))
    if parts[:1] == ["ai"] and method == "POST":
        fn = parts[1]
        s = sv(body["solve_id"]) if body.get("solve_id") else None
        if fn == "devil":
            return ai.devils_advocate(s)
        if fn == "assumptions":
            return ai.what_would_have_to_be_true(s)
        if fn == "interview":
            return ai.interview(s)
        if fn == "react":
            return ai.react_narrative(s, body["reaction"])
        if fn == "disagree":
            return ai.explain_disagreement(s, sv(body["other_id"]))
        if fn == "feasibility":
            return ai.feasibility_narrative(engine.feasibility())
        return {"error": "unknown ai function"}
    if parts == ["feasibility"]:
        return engine.feasibility()
    if parts == ["dossier"]:
        if q.get("id"):
            r = next((r for r in engine.regions() if r["id"] == q["id"]), None)
        else:
            r = engine.region_of(float(q["lat"]), float(q["lon"]))
        if not r:
            return {"gap": True, "text": "No dossier covers this point. That is a coverage gap, not a verdict."}
        r["features"] = [f for f in engine.features() if r["bbox"] and geo.in_bbox(f["lat"], f["lon"], r["bbox"])]
        r["history"] = [h for h in knowledge.HISTORY if r["id"] in h["regions"]]
        r["season"] = [s_["text"] for s_ in knowledge.SEASON if any(m.lower() in (r["name"] + " " + " ".join(f["name"] for f in r["features"])).lower() for m in s_["match"])]
        r["rumors"] = [x for x in store.rows("SELECT * FROM rumors") if any(k.lower() in (x["text"] or "").lower() for k in r["name"].replace("&", " ").split() if len(k) > 4)][:12]
        r["searchers_note"] = r["dossier"].get("searchers")
        return r
    if parts == ["rules"]:
        if method == "POST":
            for r in body.get("rules", []):
                store.upsert("rules", {"id": r.get("id") or store.uid("r"), "text": r["text"], "kind": r.get("kind", "soft"), "enabled": 1 if r.get("enabled", True) else 0, "code": r.get("code", "check:none"), "note": r.get("note", ""), "source": r.get("source", "")})
            for rid in body.get("delete", []):
                store.run("DELETE FROM rules WHERE id=?", (rid,))
            engine.rescore_all("rules changed")
        return engine.rules()
    if parts == ["statements"]:
        if method == "POST":
            store.upsert("statements", {"id": body.get("id") or store.uid("st"), "text": body["text"], "date": body.get("date", ""), "venue": body.get("venue", ""), "context": body.get("context", ""), "tier": body.get("tier", "unverified"), "kind": body.get("kind", "answer"), "lines_json": store.j(body.get("lines", [])), "source": body.get("source", ""), "url": body.get("url", ""), "tags_json": store.j(body.get("tags", [])), "origin": body.get("origin", "manual"), "created": time.time()})
            return {"ok": True, "rescored": engine.rescore_all("new statement")}
        ss = engine.statements_for(q.get("ref") or None)
        if q.get("q"):
            qq = q["q"].lower()
            ss = [s_ for s_ in ss if qq in (s_["text"] or "").lower() or qq in (s_.get("venue") or "").lower()]
        if q.get("kind"):
            ss = [s_ for s_ in ss if s_.get("kind") == q["kind"]]
        return sorted(ss, key=lambda s_: (s_.get("date") or ""), reverse=True)
    if parts == ["rumors"]:
        out = store.rows("SELECT * FROM rumors ORDER BY created DESC")
        for r in out:
            r["lines"] = store.unj(r.pop("lines_json"), [])
            r["tags"] = store.unj(r.pop("tags_json"), [])
        if q.get("q"):
            out = [r for r in out if q["q"].lower() in (r["text"] or "").lower()]
        return out
    if parts == ["book"]:
        out = store.rows("SELECT * FROM book")
        for r in out:
            r["tags"] = store.unj(r.pop("tags_json"), [])
        return out
    if parts == ["features"]:
        fs = engine.features()
        if q.get("ftype"):
            fs = [f for f in fs if f["ftype"] == q["ftype"]]
        if q.get("state"):
            fs = [f for f in fs if f["state"] == q["state"]]
        if q.get("idea"):
            fs = [f for f in fs if engine._feature_idea_hits(f, [q["idea"]])]
        if q.get("lat") and q.get("lon"):
            c = (float(q["lat"]), float(q["lon"]))
            r = float(q.get("radius", 30))
            for f in fs:
                f["dist_mi"] = round(geo.haversine(c, (f["lat"], f["lon"])), 1)
            fs = sorted([f for f in fs if f["dist_mi"] <= r], key=lambda f: f["dist_mi"])
        return {"features": fs, "gnis": public_data.gnis_query(state=q.get("state"), fclass=q.get("ftype"), name_like=q.get("q"), center=(float(q["lat"]), float(q["lon"])) if q.get("lat") else None, radius_mi=float(q.get("radius", 30)) if q.get("lat") else None, limit=100) if (q.get("ftype") or q.get("q")) else [], "patterns": knowledge.NAME_PATTERNS}
    if parts == ["project"] and method == "POST":
        a = (float(body["lat"]), float(body["lon"]))
        brg, mi = float(body["bearing"]), float(body["mi"])
        d = geo.destination(a, brg, mi)
        back = geo.destination(a, geo.back_bearing(brg), mi)
        def near(pt):
            fs = sorted([{**f, "dist_mi": round(geo.haversine(pt, (f["lat"], f["lon"])), 2)} for f in engine.features()], key=lambda f: f["dist_mi"])[:6]
            g = public_data.gnis_query(center=pt, radius_mi=2, limit=12)
            return {"inventory": fs, "gnis": g}
        return {"from": a, "bearing": brg, "back_bearing": geo.back_bearing(brg), "mi": mi, "dest": d, "back_dest": back, "near": near(tuple(d)), "near_back": near(tuple(back))}
    if parts == ["point"]:
        return public_data.point_report(float(q["lat"]), float(q["lon"]))
    if parts == ["scratch"]:
        if method == "POST":
            store.upsert("scratch", {"id": body.get("id") or store.uid("sc"), "text": body.get("text", ""), "result": body.get("result", ""), "tags_json": store.j(body.get("tags", [])), "created": time.time()})
        if method == "DELETE" or body.get("delete"):
            store.run("DELETE FROM scratch WHERE id=?", (body["delete"],))
        out = store.rows("SELECT * FROM scratch ORDER BY created DESC")
        for r in out:
            r["tags"] = store.unj(r.pop("tags_json"), [])
        return out
    if parts == ["history"]:
        return store.rows("SELECT * FROM history ORDER BY ts DESC LIMIT 300")
    if parts == ["rescore"] and method == "POST":
        return engine.rescore_all(body.get("reason", "manual"))
    if parts == ["import"] and method == "POST":
        data = body.get("export")
        if body.get("path"):
            with open(body["path"]) as f:
                data = json.load(f)
        return importer.run_import(data)
    if parts == ["mapping"]:
        if method == "POST":
            with open(importer.DEFAULT_MAPPING_PATH, "w") as f:
                json.dump(body, f, indent=2)
        return importer.load_mapping()
    if parts == ["catalog"]:
        p = os.path.join(os.path.dirname(HERE), "DATABASE-CATALOG.md")
        return {"text": open(p).read() if os.path.exists(p) else ""}
    if parts == ["fetch"] and method == "POST":
        states = body.get("states") or ["MT", "WY", "ID", "UT"]
        jid = store.uid("job")
        JOBS[jid] = {"log": [], "done": False}
        def run():
            try:
                res = public_data.fetch_all(states, lambda m: JOBS[jid]["log"].append(m))
                JOBS[jid]["result"] = res
            except Exception as e:
                JOBS[jid]["log"].append("failed: " + str(e))
            JOBS[jid]["done"] = True
        threading.Thread(target=run, daemon=True).start()
        return {"job": jid}
    if parts[:1] == ["job"]:
        return JOBS.get(parts[1], {"log": ["unknown job"], "done": True})
    if parts == ["monitor", "run"] and method == "POST":
        return monitor.run_monitors(lambda m: None)
    if parts == ["monitor", "items"]:
        monitor.ensure_monitors()
        return {"items": store.rows("SELECT * FROM monitor_items WHERE seen=0 ORDER BY created DESC LIMIT 200"), "monitors": store.rows("SELECT * FROM monitors")}
    if parts == ["monitor", "accept"] and method == "POST":
        return {"rescored": monitor.accept_item(body["id"], body.get("tier", "circulating"), body.get("ref"), body.get("stance", "supports"))}
    if parts == ["monitor", "dismiss"] and method == "POST":
        store.run("UPDATE monitor_items SET seen=1 WHERE id=?", (body["id"],))
        return {"ok": True}
    if parts == ["monitor", "set"] and method == "POST":
        store.upsert("monitors", {"url": body["url"], "label": body.get("label", body["url"]), "last_hash": "", "last_check": 0, "enabled": 1 if body.get("enabled", True) else 0})
        t = store.setting("monitor_tiers", {})
        t[body["url"]] = body.get("tier", "circulating")
        store.set_setting("monitor_tiers", t)
        return store.rows("SELECT * FROM monitors")
    if parts == ["export"]:
        return {"poem": store.get_poem(), "solves": store.list_solves(), "statements": engine.statements_for(), "rules": engine.rules(), "scratch": store.rows("SELECT * FROM scratch"), "findings": store.rows("SELECT * FROM findings")}
    raise KeyError("no route " + path)


def field_html(s):
    stops = engine.field_stops(s)
    sc = engine.score(s)
    rows_ = "".join(f"""<section class=stop><h2>Stop {x['stop']} · {x['ref']} — {x['name']}</h2>
<div class=grid><div><b>Coordinates</b><br><code>{x['lat']:.5f}, {x['lon']:.5f}</code>{f"<br>{x['elev']:,} ft" if x.get('elev') else ''}</div>
<div><b>From previous stop</b><br>{x['drive_mi']} mi · ~{x['drive_min']} min drive</div>
<div><b>Access</b><br>{x['access']}<br>Car: {x['car']}<br>Land: {x['owner']}</div>
<div><b>Hike</b><br>{x['hike']}<br>Cell: {x['cell']}</div></div>
<p><b>Expect to find:</b> {x['expect'] or '—'}</p><p><b>Why here:</b> {x['why'] or '—'}</p>
<p><b>Confirms the line:</b> {x['confirm']}</p><p><b>Kills the line:</b> {x['kill']}</p>
{''.join(f'<p class=season>⚠ {t}</p>' for t in x['season'])}
<p class=chk>☐ found &nbsp; ☐ not there &nbsp; ☐ inconclusive &nbsp; notes: ____________________________</p></section>""" for x in stops)
    return {"html": f"""<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>Field checklist — {s['name']}</title>
<style>body{{font:15px/1.45 -apple-system,Helvetica,Arial,sans-serif;margin:16px;color:#111;background:#fff}}h1{{font-size:22px;margin:0 0 4px}}.sub{{color:#555;margin-bottom:16px}}.stop{{border:1px solid #bbb;border-radius:8px;padding:12px 14px;margin:0 0 14px;page-break-inside:avoid}}h2{{font-size:17px;margin:0 0 8px}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:8px 16px;font-size:14px}}code{{font-size:15px}}.season{{background:#fff3cd;padding:6px 8px;border-radius:4px;font-size:13px}}.chk{{border-top:1px dashed #bbb;padding-top:8px;margin-top:8px}}@media print{{.stop{{border-color:#000}}}}</style>
<h1>{s['name']}</h1><div class=sub>Field checklist in driving order · {len(stops)} stops · board score {sc['total']} · printed {time.strftime('%Y-%m-%d')} · offline copy: save this page</div>
<p><b>Before leaving:</b> download offline maps for the area; the tool's coordinates are as typed in the solve — verify each against a topo before relying on it. Rules to re-check on site: public land, no buildings, no graves, no cave, no fee, dogs allowed, a normal car gets you within a mile.</p>{rows_}"""}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype + ("; charset=utf-8" if "text" in ctype else ""))
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _handle(self, method):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        body = {}
        if method in ("POST", "DELETE"):
            n = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(n) if n else b""
            try:
                body = json.loads(raw or b"{}")
            except Exception:
                body = {}
        if not u.path.startswith("/api/"):
            with open(UI, "rb") as f:
                return self._send(200, f.read(), "text/html")
        try:
            res = api(method, u.path, q, body)
            if u.path.endswith("/field") and isinstance(res, dict) and "html" in res and q.get("raw"):
                return self._send(200, res["html"].encode(), "text/html")
            self._send(200, res)
        except KeyError as e:
            self._send(404, {"error": str(e)})
        except Exception as e:
            traceback.print_exc()
            self._send(500, {"error": f"{type(e).__name__}: {e}"})

    def do_GET(self):
        self._handle("GET")

    def do_POST(self):
        self._handle("POST")

    def do_DELETE(self):
        self._handle("DELETE")


def boot():
    store.db()
    engine.ensure_knowledge()
    monitor.ensure_monitors()


def serve(port=8765, open_browser=True):
    boot()
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    url = f"http://127.0.0.1:{port}/"
    print(f"Solve builder running at {url}  (Ctrl+C to stop)")
    if open_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


def cli_import(path):
    boot()
    with open(path) as f:
        data = json.load(f)
    rep = importer.run_import(data)
    print(json.dumps(rep, indent=2))
    print(json.dumps(engine.rescore_all("import"), indent=1)[:2000])


def cli_fetch(states):
    boot()
    print(json.dumps(public_data.fetch_all([s.upper() for s in states]), indent=2, default=str))


def cli_verify():
    boot()
    print(public_data.verify_features())


def cli_monitor():
    boot()
    print(json.dumps(monitor.run_monitors(), indent=1, default=str)[:4000])


def cli_rescore():
    boot()
    print(json.dumps(engine.rescore_all("cli"), indent=1)[:4000])
