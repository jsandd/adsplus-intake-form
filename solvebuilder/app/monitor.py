"""Monitors: watch the places new Posey statements show up, store anything new at
its correct reliability tier, and re-score every solve when something lands.

Nothing here is promoted to 'confirmed' automatically except the official
treasure.quest announcements page. Everything else arrives as 'circulating' or
'fan' and waits for you to accept it into the statement archive.
"""
import hashlib
import html
import re
import time
import urllib.request
import xml.etree.ElementTree as ET

from . import engine, store

UA = {"User-Agent": "solvebuilder/1.0 (personal research tool)"}
DEFAULT_MONITORS = [
    ("https://treasure.quest/en/announcements/", "treasure.quest announcements (official)", "confirmed"),
    ("https://mysteriouswritings.com/beyond-the-maps-edge-treasure-hunt/", "Mysterious Writings hub (Featured Questions land here)", "fan"),
    ("https://mysteriouswritings.substack.com/feed", "Mysterious Writings Substack RSS", "fan"),
    ("https://www.reddit.com/r/beyondthemapsedge/new/.rss", "r/beyondthemapsedge new posts", "circulating"),
    ("https://www.reddit.com/r/JustinPoseysTreasure/new/.rss", "r/JustinPoseysTreasure new posts", "circulating"),
    ("https://mysteriouswritings.proboards.com/thread/7358/maps-edge-treasure-hunt", "MW forum thread", "circulating"),
]


def ensure_monitors():
    if not store.row("SELECT 1 FROM monitors LIMIT 1"):
        for url, label, tier in DEFAULT_MONITORS:
            store.upsert("monitors", {"url": url, "label": label, "last_hash": "", "last_check": 0, "enabled": 1})
        store.set_setting("monitor_tiers", {u: t for u, _, t in DEFAULT_MONITORS})


def _fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode("utf-8", "replace")


def _strip(s):
    s = re.sub(r"<script.*?</script>|<style.*?</style>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    return html.unescape(re.sub(r"\s+", " ", s)).strip()


def _items_from_rss(text):
    out = []
    try:
        root = ET.fromstring(text.encode())
    except Exception:
        return out
    for it in root.iter():
        tag = it.tag.split("}")[-1]
        if tag in ("item", "entry"):
            title = next((c.text for c in it if c.tag.split("}")[-1] == "title"), "") or ""
            body = next((c.text for c in it if c.tag.split("}")[-1] in ("description", "summary", "content")), "") or ""
            date = next((c.text for c in it if c.tag.split("}")[-1] in ("pubDate", "published", "updated")), "") or ""
            link = next((c.attrib.get("href") or c.text for c in it if c.tag.split("}")[-1] == "link"), "") or ""
            out.append({"title": _strip(title)[:200], "text": _strip(body)[:1200], "date": date[:40], "link": link})
    return out


def _items_from_html(text):
    paras = [p for p in re.split(r"</p>|<br\s*/?>|</li>|</h\d>", text, flags=re.I)]
    out = []
    for p in paras:
        t = _strip(p)
        if 80 <= len(t) <= 1500:
            out.append({"title": t[:90], "text": t, "date": "", "link": ""})
    return out


def run_monitors(progress=print):
    ensure_monitors()
    tiers = store.setting("monitor_tiers", {})
    new_items = []
    for m in store.rows("SELECT * FROM monitors WHERE enabled=1"):
        try:
            text = _fetch(m["url"])
        except Exception as e:
            progress(f"monitor {m['label']}: failed — {e}")
            store.run("UPDATE monitors SET last_check=? WHERE url=?", (time.time(), m["url"]))
            continue
        items = _items_from_rss(text) if "<rss" in text[:400] or "<feed" in text[:400] else _items_from_html(text)
        tier = tiers.get(m["url"], "circulating")
        for it in items:
            h = hashlib.sha1((m["url"] + it["title"] + it["text"][:300]).encode()).hexdigest()[:16]
            if store.row("SELECT 1 FROM monitor_items WHERE id=?", (h,)):
                continue
            store.upsert("monitor_items", {"id": h, "url": m["url"], "title": it["title"], "text": it["text"], "date": it["date"], "tier": tier, "seen": 0, "created": time.time()})
            new_items.append({"id": h, "source": m["label"], "title": it["title"], "tier": tier})
        store.run("UPDATE monitors SET last_hash=?, last_check=? WHERE url=?", (hashlib.sha1(text.encode()).hexdigest(), time.time(), m["url"]))
        progress(f"monitor {m['label']}: {len(items)} items, {len([n for n in new_items if n['source'] == m['label']])} new")
    deltas = engine.rescore_all("monitor") if new_items else []
    store.log_history("monitor", detail={"new": len(new_items), "rescored": len(deltas)})
    return {"new": new_items, "rescored": deltas}


def accept_item(item_id, tier, ref=None, stance="supports"):
    it = store.row("SELECT * FROM monitor_items WHERE id=?", (item_id,))
    if not it:
        return None
    lines = [{"ref": ref, "stance": stance, "why": ""}] if ref else []
    store.upsert("statements", {"id": "mon_" + item_id, "text": (it["title"] + ": " if it["title"] and it["title"] not in it["text"] else "") + it["text"], "date": it["date"], "venue": it["url"], "context": "pulled from outside your database by the monitor on " + time.strftime("%Y-%m-%d"), "tier": tier, "kind": "answer", "lines_json": store.j(lines), "source": it["url"], "url": it["url"], "tags_json": store.j(["monitor"]), "origin": "web", "created": time.time()})
    store.run("UPDATE monitor_items SET seen=1 WHERE id=?", (item_id,))
    return engine.rescore_all("new statement")
