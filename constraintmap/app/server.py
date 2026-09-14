"""Local HTTP server: static UI plus a small JSON API. Standard library only."""
import json
import os
import threading
import traceback
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from . import config, dem, padus, render, rules, scorer, store, vectors

_jobs = {"log": [], "running": None, "last_error": None}


def log(msg):
    _jobs["log"].append(msg)
    _jobs["log"] = _jobs["log"][-200:]
    print(msg)


def run_job(name, fn):
    if _jobs["running"]:
        return False
    def go():
        _jobs["running"] = name
        try:
            _jobs["last_error"] = None
            fn()
            log(f"done: {name}")
        except Exception as e:
            traceback.print_exc()
            _jobs["last_error"] = f"{name}: {e}"
            log(f"FAILED {name}: {e}")
        finally:
            _jobs["running"] = None
    threading.Thread(target=go, daemon=True).start()
    return True


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        b = json.dumps(obj, default=str).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}")

    def do_GET(self):
        u = urlparse(self.path); q = {k: v[0] for k, v in parse_qs(u.query).items()}
        try:
            if u.path == "/" or u.path == "/index.html":
                p = os.path.join(config.UI, "index.html"); b = open(p, "rb").read()
                self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b); return
            if u.path == "/api/status":
                self._json({"dem": dem.coverage(), "padus": padus.loaded(), "vectors": vectors.coverage(), "job": _jobs["running"], "last_error": _jobs["last_error"], "log": _jobs["log"][-30:], "states": {k: v[0] for k, v in config.STATES.items()}}); return
            if u.path == "/api/rules":
                self._json({"rules": rules.merged(store.get_rules_overrides()), "checklist": config.CHECKLIST, "fenn": config.FENN_SITES}); return
            if u.path == "/api/score":
                lat = float(q["lat"]); lon = float(q["lon"])
                rs = rules.merged(store.get_rules_overrides())
                m = scorer.measure(lat, lon, allow_download=q.get("download", "1") == "1")
                v, s = rules.evaluate(rs, m)
                self._json({"measurements": m, "verdicts": v, "summary": s}); return
            if u.path == "/api/candidates":
                self._json({"candidates": store.candidates(), "research": store.research_candidates()}); return
            if u.path == "/api/export":
                cs = store.candidates()
                self._json({"format": "btme-constraintmap-candidates-1", "candidates": [{"letter": c["letter"], "name": c["name"], "coords": f"{c['lat']:.5f}, {c['lon']:.5f}", "notes": c["notes"], "verdict": c["summary"].get("verdict"), "grid": {k: v["status"] for k, v in c["verdicts"].items()}, "values": {k: v["value"] for k, v in c["verdicts"].items()}} for c in cs]}); return
            self._json({"error": "not found"}, 404)
        except Exception as e:
            traceback.print_exc(); self._json({"error": str(e)}, 500)

    def do_POST(self):
        u = urlparse(self.path)
        try:
            b = self._body()
            if u.path == "/api/rules":
                store.set_rules_overrides(b.get("overrides") or {}); self._json({"ok": True, "rules": rules.merged(store.get_rules_overrides())}); return
            if u.path == "/api/candidates":
                cid = store.save_candidate(b); self._json({"ok": True, "id": cid, "candidates": store.candidates()}); return
            if u.path == "/api/candidates/delete":
                store.delete_candidate(b["id"]); self._json({"ok": True, "candidates": store.candidates()}); return
            if u.path == "/api/candidates/rescore":
                rs = rules.merged(store.get_rules_overrides())
                for c in store.candidates():
                    m = scorer.measure(c["lat"], c["lon"]); v, s = rules.evaluate(rs, m)
                    c.update({"measurements": m, "verdicts": v, "summary": s}); store.save_candidate(c)
                self._json({"ok": True, "candidates": store.candidates()}); return
            if u.path == "/api/render":
                rs = rules.merged(store.get_rules_overrides())
                self._json(render.render(b["bbox"], rs, int(b.get("max_cells") or 250000))); return
            if u.path == "/api/fetch":
                kind, st = b["kind"], (b.get("state") or "").upper()
                fn = {"dem": lambda: dem.fetch_state(st, log), "tran": lambda: vectors.ingest_tran(st, log), "gnis": lambda: vectors.ingest_gnis(st, log), "struct": lambda: vectors.ingest_struct(st, log), "padus": lambda: padus.ingest(os.path.join(config.DATA, b.get("path") or "padus.gpkg") if not os.path.isabs(b.get("path") or "") else b["path"], log)}[kind]
                ok = run_job(f"{kind} {st}", fn); self._json({"ok": ok, "running": _jobs["running"]}); return
            self._json({"error": "not found"}, 404)
        except Exception as e:
            traceback.print_exc(); self._json({"error": str(e)}, 500)


def serve(port, open_browser=True):
    os.makedirs(config.DATA, exist_ok=True)
    srv = ThreadingHTTPServer(("127.0.0.1", port), H)
    url = f"http://localhost:{port}"
    print(f"Constraint map: {url}   (Ctrl-C to stop)")
    if open_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
