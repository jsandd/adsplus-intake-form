"""Paths, states, and the default rules. Every rule parameter is editable in the UI;
edits are stored in data/store.sqlite and override these defaults."""
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")
UI = os.path.join(HERE, "ui")
STORE = os.path.join(DATA, "store.sqlite")
PADUS_DB = os.path.join(DATA, "padus.sqlite")
VEC_DB = os.path.join(DATA, "vectors.sqlite")
DEM_DIR = os.path.join(DATA, "dem")
SEED = os.path.join(os.path.dirname(HERE), "seed", "beyond-the-maps-edge-seed.json")
PORT = 8790
TNM = "https://prd-tnm.s3.amazonaws.com/StagedProducts/"

# lon_min, lat_min, lon_max, lat_max
STATES = {
    "WA": ("Washington", (-124.85, 45.54, -116.92, 49.00)),
    "ID": ("Idaho", (-117.24, 41.99, -111.04, 49.00)),
    "MT": ("Montana", (-116.05, 44.36, -104.04, 49.00)),
    "WY": ("Wyoming", (-111.06, 40.99, -104.05, 45.00)),
    "UT": ("Utah", (-114.05, 36.99, -109.04, 42.00)),
    "NV": ("Nevada", (-120.01, 35.00, -114.04, 42.00)),
    "CA": ("California", (-124.48, 32.53, -114.13, 42.01)),
    "AZ": ("Arizona", (-114.82, 31.33, -109.04, 37.00)),
    "NM": ("New Mexico", (-109.05, 31.33, -103.00, 37.00)),
    "TX": ("Texas (west, on the map)", (-106.65, 28.90, -102.00, 36.50)),
    "CO": ("Colorado (eliminated)", (-109.06, 36.99, -102.04, 41.00)),
    "OR": ("Oregon (eliminated)", (-124.57, 41.99, -116.46, 46.29)),
}
# Colorado is a near-rectangle; Oregon needs a rough polygon (lon, lat).
OREGON = [(-124.57, 42.00), (-117.03, 42.00), (-117.03, 43.80), (-116.90, 44.20), (-117.20, 44.40), (-116.50, 45.60), (-116.92, 46.00), (-118.98, 45.99), (-119.60, 45.92), (-120.90, 45.65), (-122.30, 45.55), (-122.75, 45.65), (-123.10, 46.19), (-124.05, 46.25), (-124.20, 45.00), (-124.55, 43.30), (-124.40, 42.20), (-124.57, 42.00)]
COLORADO = [(-109.06, 36.99), (-102.04, 36.99), (-102.04, 41.00), (-109.06, 41.00), (-109.06, 36.99)]
MAP_EXTENT = (-125.0, 28.5, -102.0, 49.2)  # the printed map's western sheet, roughly

# Places he has said he searched for Fenn's chest (reported). Editable in the rules panel.
FENN_SITES = [["Madison Junction, Yellowstone", 44.6425, -110.8620], ["Nine Mile Hole, Madison River", 44.6600, -110.8400], ["Hebgen Lake", 44.8700, -111.3000], ["Sinks Canyon (reported via Treasure Among Us)", 42.7400, -108.8200], ["Grand Teton (reported via Treasure Among Us)", 43.7400, -110.8000], ["Iron Springs, Yellowstone (first search with Brandon)", 44.7500, -110.7300]]

DEFAULT_RULES = [
    {"id": "r_state", "name": "Not Colorado, not Oregon", "source": "Seekers Summit (per Mysterious Writings): both eliminated, no clues and no treasure there", "tag": "SAID", "type": "exclude", "severity": "kill", "on": True, "param": None, "unit": ""},
    {"id": "r_map", "name": "Inside the printed map, in the American West", "source": "'Absolutely hidden somewhere on the map that I've published'", "tag": "SAID", "type": "include", "severity": "flag", "on": True, "param": None, "unit": ""},
    {"id": "r_elev", "name": "Below the elevation ceiling", "source": "Dillon Q&A: the treasure is below 11,000 ft", "tag": "SAID", "type": "exclude", "severity": "flag", "on": True, "param": 11000, "unit": "ft"},
    {"id": "r_public", "name": "Publicly accessible land, not private", "source": "Official rules; restated June 2026", "tag": "CONFIRMED", "type": "include", "severity": "kill", "on": True, "param": None, "unit": ""},
    {"id": "r_free", "name": "Free to enter", "source": "FAQ: 'Do you have to pay to get in? No, not as of today'", "tag": "CONFIRMED", "type": "exclude", "severity": "kill", "on": True, "param": None, "unit": ""},
    {"id": "r_dog", "name": "Dogs allowed on the ground crossed", "source": "FAQ: 'If your dog is the outdoors type, absolutely!'", "tag": "CONFIRMED", "type": "include", "severity": "flag", "on": True, "param": None, "unit": ""},
    {"id": "r_road_max", "name": "Within reach of a road a low-clearance car can use", "source": "FAQ: not more than a mile to figure out where it is; Summit: a low rider made it", "tag": "CONFIRMED", "type": "include", "severity": "kill", "on": True, "param": 1.0, "unit": "mi"},
    {"id": "r_road_min", "name": "A hike is required: not at the roadside", "source": "Dillon Q&A: a hike is required, length withheld", "tag": "SAID", "type": "exclude", "severity": "flag", "on": True, "param": 300, "unit": "ft"},
    {"id": "r_trail", "name": "Not near any man-made trail", "source": "Dillon Q&A: 'not in very close proximity to any man-made trail… a little ways off'", "tag": "SAID", "type": "exclude", "severity": "flag", "on": True, "param": 500, "unit": "ft"},
    {"id": "r_bldg", "name": "Not associated with man-made buildings", "source": "Official rules; a gazebo counts", "tag": "CONFIRMED", "type": "exclude", "severity": "kill", "on": True, "param": 500, "unit": "ft"},
    {"id": "r_grave", "name": "Not near graves or grave markers", "source": "Official rules", "tag": "CONFIRMED", "type": "exclude", "severity": "kill", "on": True, "param": 500, "unit": "ft"},
    {"id": "r_rail", "name": "Not at railroad tracks", "source": "Dillon and Summit: tracks are a man-made structure, ruled out", "tag": "CONFIRMED", "type": "exclude", "severity": "kill", "on": True, "param": 500, "unit": "ft"},
    {"id": "r_cave", "name": "Not in a cave, mine or tunnel", "source": "Official rules", "tag": "CONFIRMED", "type": "exclude", "severity": "kill", "on": True, "param": 500, "unit": "ft"},
    {"id": "r_water", "name": "Not underwater", "source": "Official rules", "tag": "CONFIRMED", "type": "exclude", "severity": "kill", "on": True, "param": None, "unit": ""},
    {"id": "r_slope", "name": "No climbing required: slope under the limit", "source": "Official rules: no ropes, ladders or climbing skills", "tag": "CONFIRMED", "type": "exclude", "severity": "kill", "on": True, "param": 30, "unit": "°"},
    {"id": "r_fenn", "name": "Within the Fenn search radius", "source": "Summit: searched for Fenn within 75 miles, then walked back", "tag": "SAID", "type": "include", "severity": "flag", "on": True, "param": 75, "unit": "mi"},
]

CHECKLIST = [
    ("Nothing significant visible from 15 feet", "Summit: 'The most accurate answer is no.'"),
    ("Something must be manipulated to see it; bring a flashlight", "Summit and Q&A"),
    ("Feet stay dry", "Summit: 'You don't have to' get your feet wet"),
    ("Physical objects along the way", "Summit: 'fair to say there are'"),
    ("Dogs allowed on the ground you cross", "FAQ"),
    ("Not near any man-made trail: a little ways off", "Dillon"),
    ("More than a mile from anywhere he, family or friends live, work or own", "Official rules"),
    ("No ropes, ladders, climbing, swimming, or high-clearance vehicle needed", "Official rules"),
    ("A walk, but short: 'if you're needing many bottles of water you're going too far'", "Summit"),
    ("Something along the way is pivotal; the checkpoint is hard to miss", "Summit and Q&A"),
    ("No blaze cut on a tree; markers survive natural forces", "Dillon"),
    ("Below 11,000 feet", "Dillon"),
]
