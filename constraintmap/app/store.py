"""Candidates, rule overrides and settings in data/store.sqlite."""
import json
import os
import sqlite3
import threading
import time

from . import config

_lock = threading.Lock()
_conn = None


def _db():
    global _conn
    with _lock:
        if _conn is None:
            os.makedirs(config.DATA, exist_ok=True)
            _conn = sqlite3.connect(config.STORE, check_same_thread=False)
            _conn.execute("CREATE TABLE IF NOT EXISTS kv(k TEXT PRIMARY KEY, v TEXT)")
            _conn.execute("CREATE TABLE IF NOT EXISTS candidates(id TEXT PRIMARY KEY, letter TEXT, name TEXT, lat REAL, lon REAL, notes TEXT, measurements TEXT, verdicts TEXT, summary TEXT, created REAL, updated REAL)")
        return _conn


def get_rules_overrides():
    r = _db().execute("SELECT v FROM kv WHERE k='rules'").fetchone()
    return json.loads(r[0]) if r else {}


def set_rules_overrides(o):
    c = _db(); c.execute("INSERT OR REPLACE INTO kv VALUES ('rules', ?)", (json.dumps(o),)); c.commit()


def candidates():
    rows = _db().execute("SELECT id, letter, name, lat, lon, notes, measurements, verdicts, summary, created, updated FROM candidates ORDER BY letter").fetchall()
    return [{"id": r[0], "letter": r[1], "name": r[2], "lat": r[3], "lon": r[4], "notes": r[5], "measurements": json.loads(r[6] or "{}"), "verdicts": json.loads(r[7] or "{}"), "summary": json.loads(r[8] or "{}"), "created": r[9], "updated": r[10]} for r in rows]


def next_letter():
    used = {r[0] for r in _db().execute("SELECT letter FROM candidates").fetchall()}
    for i in range(26 * 3):
        l = chr(65 + i % 26) + ("" if i < 26 else str(i // 26))
        if l not in used:
            return l
    return "Z9"


def save_candidate(c):
    db = _db(); now = time.time()
    cid = c.get("id") or ("cm_" + str(int(now * 1000)))
    old = db.execute("SELECT letter, created FROM candidates WHERE id=?", (cid,)).fetchone()
    letter = c.get("letter") or (old[0] if old else next_letter())
    db.execute("INSERT OR REPLACE INTO candidates VALUES (?,?,?,?,?,?,?,?,?,?,?)", (cid, letter, c.get("name") or f"Candidate {letter}", c["lat"], c["lon"], c.get("notes") or "", json.dumps(c.get("measurements") or {}), json.dumps(c.get("verdicts") or {}), json.dumps(c.get("summary") or {}), old[1] if old else now, now))
    db.commit(); return cid


def delete_candidate(cid):
    db = _db(); db.execute("DELETE FROM candidates WHERE id=?", (cid,)); db.commit()


def research_candidates():
    """Candidates from the research database export (seed JSON) with parseable coordinates."""
    import re
    try:
        d = json.load(open(config.SEED, encoding="utf-8"))
    except Exception:
        return []
    out = []
    for c in d.get("candidates", []):
        m = re.search(r"(-?\d{1,2}\.\d+)[,\s]+(-?\d{2,3}\.\d+)", c.get("coords") or "")
        if m:
            out.append({"id": c["id"], "name": c["name"], "lat": float(m.group(1)), "lon": float(m.group(2)), "region": c.get("region", ""), "top3": c.get("top3")})
    return out
