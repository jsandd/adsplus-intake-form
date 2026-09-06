# Solve Builder — Beyond the Map's Edge

A local tool for working out solves to Justin Posey's poem. You click a line, see
every candidate reading of it (tagged by the kind of leap it asks for), commit one,
and watch what that does to every other line. Solves can be seeded, forked, compared,
argued against, run backward from an endpoint, and checked in the field.

## Run it

```
python3 run.py
```

That is the whole install. It starts a small server on your own machine and opens
`http://127.0.0.1:8765/` in your browser. Close the terminal to stop it. Your work is
saved in `data/solvebuilder.sqlite` (one file — copy it to back up).

On first run it asks you to paste the poem. Then load your research database:
**Data → choose the Field HQ export → Import through mapping** (or
`python3 run.py import your-export.json`).

## Why these technology choices

- **Python 3** is already on Macs and most Linux machines (Windows: install from python.org, tick "Add to PATH"). Nothing else to install.
- **SQLite** is a database in a single file. No server, no account, works with no signal in the field.
- **One web page** for the interface, served from your machine. It works offline; only the map tiles and the AI need the internet.
- **The AI features** use the official Anthropic package. `run.py` installs it into a private folder the first time it has internet. If it cannot, the tool still runs and the AI buttons are greyed out with the reason. Set `ANTHROPIC_API_KEY` in your environment (or run `ant auth login`) to enable them. Model: `claude-opus-5`, with refusal fallbacks switched on so a declined request is retried on another model rather than failing.

## What is in the box

| Screen | What it does |
|---|---|
| **Line** | Candidate readings across eight categories (literal place, feature class, direction/action, wordplay, naming & culture, numeric/cipher, personal to Posey, structural). Each shows rationale, a confidence you set, reliability tier, distance from the active point and from your seed, rule flags in red, and the Posey statements for or against. Radius slider per line; hard-filter and hide-violations toggles (both off by default). "Generate readings" asks Claude for more with your current solve as context. |
| **Constraint bar** (top) | Seed, states in play, region, active point, bearing, elevation, land owner, cumulative route. **Drop seed & rescore** re-scores unconstrained and tells you your rank among your own solves. |
| **Conflicts** (left) | The contradiction detector: walking-distance breaks, big gaps between consecutive clues, doubling back, field presence before stanza 4, private land, more than one man-made clue, later choices that break locked earlier ones. Override with a note; never silently blocked. |
| **Weakest links** (left) | Every committed line ranked by load-bearing versus your confidence. |
| **Map** | Pins, route in poem order, legs with miles and bearings, one-mile circles, elevation profile, optional land shading (needs point lookups). OpenStreetMap + USGS topo tiles when online; a plain plot offline. Click the map to copy coordinates. |
| **Bearing** | Project a bearing and distance from any pin; back bearing included; snaps to named features (built-in inventory, and GNIS once downloaded); save the landing as a candidate for any line. |
| **Cipher** | Scratchpad for page numbers, letter sums, word positions, coordinate fragments; pull any result into a line's suggestions. |
| **Archive** | Posey statement archive (keyword search, declined/ambiguous flagged, linked to lines), monitor inbox, rumour & field-report layer with visible tiers. |
| **Layers** | Region dossiers, landmark inventory by type / name idea / state / radius, point lookup (USGS elevation, PAD-US land owner, OSM roads, TopoView link, MVUM links). |
| **Rules** | Posey's hard rules (red flags) and soft statements (warnings). Editable; saving re-scores every solve. |
| **Solves** | Your solves and the community theory library (Wisdom/Big Hole, Polaris, Sweetwater/South Pass, Alaska, plus your 12 imported chains). Fork, rename, compare line by line, "explain disagreement". Blind-spot tracker. |
| **Auto search** | Beam search over literal readings of stanzas 2–4, ranked by poem fit, compactness and rules. Optional AI re-rank. Open any result as a solve. |
| **Reverse** | Name an endpoint; the tool works backward and flags each line that would be a stretch. |
| **Feasibility** | Which regions can support a complete valid solve at all, and which constraint kills the others. |
| **Field** | GPS distance and bearing to every pin, what you predicted there, what confirms or kills it; record findings (they feed the score); printable checklist in *driving* order. |
| **Data** | Import through `mapping.json`, edit the mapping, download GNIS, backups, history of how solves have moved. |

Header buttons: **Devil's advocate** (argues against the open solve), **Interview me** (asks what you are avoiding), **Fork**, **Undo/Redo** (branches are kept).

After every commit a **What just changed** panel says which downstream lines went from plausible to nearly impossible, which strengthened, and what conflicts appeared. **Explain (AI)** turns that into prose.

## Reliability tiers — always visible

| Tier | Meaning |
|---|---|
| confirmed | Posey said it directly, with a dated source |
| reported | a named searcher's first-hand account |
| circulating | forum or social consensus with no clear origin |
| fan | from an analysis site, blog or compiled notes |
| unverified | could not be traced to any source |

Nothing is shown at a higher tier than its source supports. **Every built-in place in the
inventory starts as *unverified* and shows "NOT yet verified in GNIS"** until you download
GNIS for that state and the verify step finds a same-named feature within three miles.
A name that GNIS does not have is shown as a gap (✗), not hidden.

## Public data (Data tab or `python3 run.py fetch-data MT WY ID UT`)

| Source | What it gives you | How it is fetched |
|---|---|---|
| USGS GNIS | every officially named feature by type, name, state, county, with coordinates | one zip per state, stored locally (a few MB each) |
| USGS EPQS | elevation of a point in feet | per point, cached |
| PAD-US | who manages the land at a point and whether the public may enter | per point via the USGS ArcGIS service, cached |
| OpenStreetMap | roads and trails within a mile, with surface and track grade where mapped | per point via Overpass, cached |
| USGS TopoView | historical topographic sheets for a point (old names) | a link — you view it in the browser |
| FS / BLM travel maps | road class and seasonal closures | links to the official viewers (too large to download blind) |

All of it is cached in the SQLite file, so a point you looked up at home is still there in the field.

## Monitors (`python3 run.py monitor`, or Archive → Check now)

Watches treasure.quest announcements (enters as *confirmed*), the Mysterious Writings hub and Substack (enter as *fan*), the two subreddits and the MW forum thread (enter as *circulating*). New items land in the Archive inbox labelled "pulled from outside your database" with the date; you accept each into the statement archive at the tier you choose, and every solve is re-scored. Run it on a schedule with your OS scheduler (cron / Task Scheduler) if you want it automatic. Posey's X account cannot be read without logging in; add posts by hand.

## Honest limits

- Built-in dossiers, features and translations were compiled by Claude from general knowledge, with approximate coordinates. They are labelled that way. GNIS download + verify is what makes them real.
- Alaska and the Black Hills have thin coverage; the tool says so instead of filling the gap.
- Public-data downloads and monitors were written against the current public endpoints but could not be exercised from the machine that built this (no outbound internet). If a URL has moved, the error message names the constant to edit in `app/public_data.py`.
- Drive times are estimates (road factor 1.4 × straight line at 40 mph). Cell coverage is always "unknown — assume none".
- The AI's output is analysis, not a source. It is told never to invent Posey quotations and to flag names it cannot place; still check it against the archive.

## Files

```
run.py                 single command
app/server.py          local web server and JSON API
app/engine.py          suggestions, constraints, rules, contradictions, scoring, reactions, auto search, reverse, feasibility
app/knowledge.py       built-in dossiers, landmark inventory, name-pattern index, history, seasons, rules, reference solves
app/ai.py              Claude features
app/importer.py        your database → the tool, through mapping.json
app/public_data.py     GNIS, elevation, land owner, roads
app/monitor.py         statement monitors
app/store.py           SQLite
ui/index.html          the interface
mapping.json           where each table of your database feeds (edit me)
DATABASE-CATALOG.md    what is in your database, in plain language
data/                  your SQLite file (created on first run)
```
