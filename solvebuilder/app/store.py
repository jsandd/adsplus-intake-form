"""SQLite storage for the solve builder. One file, no server, works offline.

Every table is created on first run. JSON columns hold flexible structures so the
schema rarely needs to change; anything the user edits (rules, mapping, solves)
lives here rather than in code.
"""
import json
import os
import sqlite3
import threading
import time
import uuid

DATA_DIR = os.environ.get("SOLVEBUILDER_DATA", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"))
DB_PATH = os.path.join(DATA_DIR, "solvebuilder.sqlite")
_lock = threading.RLock()

SCHEMA = """
CREATE TABLE IF NOT EXISTS poems (id TEXT PRIMARY KEY, title TEXT, raw TEXT, created REAL);
CREATE TABLE IF NOT EXISTS lines (poem_id TEXT, ref TEXT, stanza INTEGER, n INTEGER, text TEXT, PRIMARY KEY (poem_id, ref));
CREATE TABLE IF NOT EXISTS solves (id TEXT PRIMARY KEY, poem_id TEXT, name TEXT, parent_id TEXT, fork_ref TEXT, kind TEXT DEFAULT 'mine', source TEXT, state_json TEXT, created REAL, updated REAL);
CREATE TABLE IF NOT EXISTS statements (id TEXT PRIMARY KEY, text TEXT, date TEXT, venue TEXT, context TEXT, tier TEXT, kind TEXT, lines_json TEXT, source TEXT, url TEXT, tags_json TEXT, origin TEXT, created REAL);
CREATE TABLE IF NOT EXISTS rumors (id TEXT PRIMARY KEY, text TEXT, tier TEXT, source TEXT, date TEXT, region TEXT, lines_json TEXT, tags_json TEXT, origin TEXT, created REAL);
CREATE TABLE IF NOT EXISTS features (id TEXT PRIMARY KEY, name TEXT, ftype TEXT, lat REAL, lon REAL, elev INTEGER, state TEXT, region TEXT, owner TEXT, access TEXT, car TEXT, rules_json TEXT, source TEXT, tier TEXT, aliases_json TEXT, notes TEXT, keys_json TEXT, gnis_verified INTEGER DEFAULT 0, origin TEXT);
CREATE TABLE IF NOT EXISTS regions (id TEXT PRIMARY KEY, name TEXT, states TEXT, bbox_json TEXT, dossier_json TEXT, status TEXT, origin TEXT);
CREATE TABLE IF NOT EXISTS rules (id TEXT PRIMARY KEY, text TEXT, kind TEXT, enabled INTEGER DEFAULT 1, code TEXT, note TEXT, source TEXT);
CREATE TABLE IF NOT EXISTS scratch (id TEXT PRIMARY KEY, text TEXT, result TEXT, tags_json TEXT, created REAL);
CREATE TABLE IF NOT EXISTS history (id TEXT PRIMARY KEY, ts REAL, event TEXT, solve_id TEXT, before REAL, after REAL, detail TEXT);
CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, value TEXT, ts REAL);
CREATE TABLE IF NOT EXISTS monitors (url TEXT PRIMARY KEY, label TEXT, last_hash TEXT, last_check REAL, enabled INTEGER DEFAULT 1);
CREATE TABLE IF NOT EXISTS monitor_items (id TEXT PRIMARY KEY, url TEXT, title TEXT, text TEXT, date TEXT, tier TEXT, seen INTEGER DEFAULT 0, created REAL);
CREATE TABLE IF NOT EXISTS findings (id TEXT PRIMARY KEY, solve_id TEXT, ref TEXT, lat REAL, lon REAL, text TEXT, verdict TEXT, created REAL);
CREATE TABLE IF NOT EXISTS book (id TEXT PRIMARY KEY, kind TEXT, title TEXT, text TEXT, page TEXT, chapter TEXT, tags_json TEXT, source TEXT, tier TEXT, origin TEXT);
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);
"""


def uid(prefix="x"):
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def connect():
    os.makedirs(DATA_DIR, exist_ok=True)
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


_con = None


def db():
    global _con
    if _con is None:
        _con = connect()
        with _lock:
            _con.executescript(SCHEMA)
            _con.commit()
    return _con


def j(v):
    return json.dumps(v, ensure_ascii=False)


def unj(s, default=None):
    if s is None or s == "":
        return default
    try:
        return json.loads(s)
    except Exception:
        return default


def rows(sql, args=()):
    with _lock:
        return [dict(r) for r in db().execute(sql, args).fetchall()]


def row(sql, args=()):
    with _lock:
        r = db().execute(sql, args).fetchone()
        return dict(r) if r else None


def run(sql, args=()):
    with _lock:
        db().execute(sql, args)
        db().commit()


def runmany(sql, seq):
    with _lock:
        db().executemany(sql, seq)
        db().commit()


def upsert(table, rec):
    keys = list(rec.keys())
    sql = f"INSERT OR REPLACE INTO {table} ({','.join(keys)}) VALUES ({','.join('?' for _ in keys)})"
    run(sql, [rec[k] for k in keys])


def setting(key, default=None):
    r = row("SELECT value FROM settings WHERE key=?", (key,))
    return unj(r["value"], default) if r else default


def set_setting(key, value):
    upsert("settings", {"key": key, "value": j(value)})


def log_history(event, solve_id=None, before=None, after=None, detail=""):
    upsert("history", {"id": uid("h"), "ts": time.time(), "event": event, "solve_id": solve_id, "before": before, "after": after, "detail": detail if isinstance(detail, str) else j(detail)})


# ---------- poem ----------

def parse_poem(raw):
    """Split pasted text into stanzas and lines. Blank lines separate stanzas.
    Returns [{ref, stanza, n, text}] with refs like S2L3."""
    out, stanza, n, blank = [], 1, 0, False
    for line in raw.splitlines():
        t = line.strip()
        if not t:
            if out:
                blank = True
            continue
        if blank:
            stanza += 1
            n = 0
            blank = False
        n += 1
        out.append({"ref": f"S{stanza}L{n}", "stanza": stanza, "n": n, "text": t})
    return out


def save_poem(title, raw):
    pid = "poem"
    run("DELETE FROM lines WHERE poem_id=?", (pid,))
    upsert("poems", {"id": pid, "title": title, "raw": raw, "created": time.time()})
    runmany("INSERT INTO lines (poem_id, ref, stanza, n, text) VALUES (?,?,?,?,?)", [(pid, l["ref"], l["stanza"], l["n"], l["text"]) for l in parse_poem(raw)])
    return get_poem()


def get_poem():
    p = row("SELECT * FROM poems WHERE id='poem'")
    if not p:
        return None
    p["lines"] = rows("SELECT ref, stanza, n, text FROM lines WHERE poem_id='poem' ORDER BY stanza, n")
    return p


# ---------- solves ----------

def new_solve(name, seed=None, kind="mine", source="", state=None, parent_id=None, fork_ref=None):
    sid = uid("s")
    st = state or {"lines": {}, "history": [], "overrides": {}, "notes": {}, "radius": {}, "hard_filter": False, "hide_violations": False}
    st["seed"] = seed or {}
    rec = {"id": sid, "poem_id": "poem", "name": name, "parent_id": parent_id, "fork_ref": fork_ref, "kind": kind, "source": source, "state_json": j(st), "created": time.time(), "updated": time.time()}
    upsert("solves", rec)
    return get_solve(sid)


def get_solve(sid):
    r = row("SELECT * FROM solves WHERE id=?", (sid,))
    if not r:
        return None
    r["state"] = unj(r.pop("state_json"), {})
    return r


def save_solve(s):
    upsert("solves", {"id": s["id"], "poem_id": s.get("poem_id", "poem"), "name": s["name"], "parent_id": s.get("parent_id"), "fork_ref": s.get("fork_ref"), "kind": s.get("kind", "mine"), "source": s.get("source", ""), "state_json": j(s["state"]), "created": s.get("created", time.time()), "updated": time.time()})


def list_solves():
    out = []
    for r in rows("SELECT * FROM solves ORDER BY updated DESC"):
        r["state"] = unj(r.pop("state_json"), {})
        out.append(r)
    return out


def delete_solve(sid):
    run("DELETE FROM solves WHERE id=?", (sid,))
