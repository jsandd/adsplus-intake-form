# Constraint map (local)

One command: `python3 run.py` → http://localhost:8790

Scores any point in the West against Posey's stated rules, with the measured
value beside each rule, and paints pass/flag/kill overlays for a box you draw.
Only local data is used when you click; every layer is downloaded once into `data/`.

## Data
| Layer | Source | How it gets here |
|---|---|---|
| Elevation and slope (30 m) | USGS 3DEP 1 arc-second | Downloads the 1°×1° tile the first time you click inside it (~50 MB), or `python3 run.py fetch-dem MT WY` |
| Land owner, public access | USGS PAD-US 4 | Download the GeoPackage from the USGS yourself, save as `data/padus.gpkg`, press Load in the Data panel. PAD-US has no fee field: NPS units are treated as likely fee, state parks as "check". |
| Roads, trails, railroads | USGS National Transportation Dataset | Data panel → Roads, per state |
| Building footprints, cemeteries | USGS National Structures Dataset (FEMA USA Structures) | Data panel → Bldgs, per state |
| Caves, mines | USGS GNIS dropped these classes in 2021; needs OpenStreetMap (natural=cave_entrance, man_made=adit/mineshaft) or USGS MRDS | not wired yet; the GNIS button loads nothing for them today |
| Water bodies | USGS NHD | not wired yet |
| OSM roads with surface, trails | Geofabrik per-state extracts | not wired yet; USGS NTD roads and trails are used meanwhile (trail coverage is thin) |

Rules live in `app/config.py` (defaults) and are edited in the Rules panel;
edits are stored in `data/store.sqlite`. Candidates are stored there too and
can be exported for the site with the Copy export button.
