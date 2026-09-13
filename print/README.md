# Printed edition of Field HQ

Rebuilds `Beyond-the-Maps-Edge-Field-HQ.pdf` from the live Field HQ database.

1. Dump the artifact database (collections `poem`, `intel`, `candidates`, `map`) as JSON files into a `livedb/` folder next to these scripts.
2. `node extract.mjs` loads `maps-edge-workbench.html` in headless Chromium with that data and runs the site's own ranking engine, writing `extract.json`.
3. `python3 build.py` writes the print layout `fieldhq.html`.
4. `node render.mjs` prints it to PDF (Letter, page numbers in the footer).

Paths at the top of each script point at the session scratchpad; change `S` to the folder you use.
