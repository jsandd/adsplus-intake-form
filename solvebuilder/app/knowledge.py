"""Built-in knowledge layers.

Everything in this file was compiled by Claude from general knowledge, NOT from
federal name records. Every feature is stored with tier 'unverified' and
gnis_verified = 0 until `run.py fetch-data` downloads USGS GNIS for the state and
`run.py verify` confirms the name exists there. Coordinates are approximate
(usually within a mile) and are labelled that way in the interface.

Your own database (imported through mapping.json) is layered on top and, where
it carries a higher reliability tier, wins.
"""

# ---------------------------------------------------------------- regions
# bbox = [south, west, north, east]
REGIONS = [
    {"id": "bighole", "name": "Big Hole & Beaverhead valleys", "states": "MT", "bbox": [44.95, -113.95, 45.95, -112.3], "status": "hot",
     "dossier": {
         "terrain": "A broad, high (6,000 ft) hay-meadow valley ringed by the Pioneer, Anaconda-Pintler, Beaverhead and Bitterroot ranges. The Big Hole River runs north then east through willow bottoms; the Beaverhead is a slower ranch-country river with Beaverhead Rock rising alone from the flats near Dillon.",
         "indigenous": ["Big Hole valley — used by the Shoshone (Lemhi) and Nez Perce as a summer camas and hunting ground; the Nez Perce called the valley area near the 1877 battle 'Iskumtselalik Pah' (place of the ground squirrels) — translation commonly cited, verify.", "Beaverhead Rock — Sacagawea recognised it from its resemblance to a swimming beaver's head; the Shoshone name is not consistently recorded — verify."],
         "trails": ["Lewis and Clark 1805: up the Beaverhead (Jefferson's 'Philosophy' and 'Wisdom' rivers named here), Camp Fortunate (now under Clark Canyon Reservoir), over Lemhi Pass.", "Nez Perce 1877 flight: Big Hole battlefield, Chief Joseph Pass, on to Bannack country.", "Bannack–Virginia City stage road; Corinne (UT) to Bannack freight road."],
         "history": "Bannack (1862 gold, first territorial capital) is a state park; placer diggings on Grasshopper Creek; Wisdom and Jackson are ranch towns; Jackson Hot Springs lodge is private.",
         "ownership": "Beaverhead-Deerlodge NF on the ranges; BLM on the foothills; large private ranches on the valley floor; Big Hole National Battlefield (NPS, fee-free, but a battle site — excluded by the rules); Clark Canyon Reservoir (BOR, free).",
         "community": "The dominant Montana theory: Wisdom (S1L3), the Big Hole as the Hole (S2L3), Polaris for Ursa, Beaverhead Rock as the bride. Dillon is Posey's grandfather country per the book. Objections: heavily searched, the 'bride' is 40 miles from Polaris, and Posey has not confirmed Montana.",
         "elimination": "in play — not eliminated",
         "searchers": "Dozens of reports on Reddit and the MW forum; at least two full published solves (Big Hole cluster; Hidden Lake BOTG trips).",
     }},
    {"id": "pioneers", "name": "Pioneer Mountains", "states": "MT", "bbox": [45.25, -113.35, 45.85, -112.75], "status": "hot",
     "dossier": {
         "terrain": "Two parallel granitic ranges (East and West Pioneers) split by the Wise River–Grasshopper valley, crossed by the Pioneer Mountains Scenic Byway. Cirque lakes, talus, lodgepole; Elkhorn Hot Springs and Crystal Park (free public quartz-crystal digging on the Pioneer batholith) on the byway.",
         "indigenous": ["No widely cited native names for the byway features — a gap to investigate at the Beaverhead County museum."],
         "trails": ["Pioneer Mountains Scenic Byway (FS 484), Wise River to Polaris; upper section closed in winter (opens ~mid May).", "Bannack–Elkhorn mining wagon roads."],
         "history": "Elkhorn and Polaris silver/lead mines; Coolidge ghost town (Elkhorn mine) on the byway; Polaris post office named for the Polaris mine.",
         "ownership": "Almost entirely Beaverhead-Deerlodge NF; Crystal Park is FS with a day-use fee in season (fee is a rules question); private inholdings at Elkhorn Hot Springs and Maverick Mountain.",
         "community": "The 'Polaris' reading of 'ursa east': Polaris MT is the north-star name; Crystal Park's granite fits 'granite bold'. Objection: the byway is a well-travelled road and the park is a developed site (buildings, toilets).",
         "elimination": "in play",
         "searchers": "Heavily searched summer 2025–2026; Posey's Sep 2026 meet-and-greet is in Polaris (an event, not a clue).",
     }},
    {"id": "grasshopper", "name": "Grasshopper & Polaris corridor", "states": "MT", "bbox": [45.05, -113.35, 45.5, -112.9], "status": "hot",
     "dossier": {
         "terrain": "Grasshopper Creek valley from Bannack up to Polaris: sage benches, cottonwood bottoms, placer tailings, the road climbing toward the Pioneers.",
         "indigenous": ["Grasshopper Creek was 'Willard's Creek' to Lewis and Clark; native name not recorded — gap."],
         "trails": ["Bannack freight road; Lewis and Clark passed the mouth of Grasshopper (Willard's) Creek on the Beaverhead."],
         "history": "1862 Grasshopper Creek gold discovery founded Bannack; Polaris mine (1885) and smelter; Bannack Days each July.",
         "ownership": "Bannack State Park (fee, buildings — excluded); BLM and private ranch along the creek; NF above.",
         "community": "Bridges the Wisdom/Big Hole and Polaris readings; the book's 'Grasshopper Valley' chapter name is why it matters.",
         "elimination": "in play",
         "searchers": "Moderate; mostly as a drive-through on the way to Polaris.",
     }},
    {"id": "sweetwater", "name": "Sweetwater & South Pass country", "states": "WY", "bbox": [42.2, -109.1, 42.75, -106.9], "status": "hot",
     "dossier": {
         "terrain": "High sage desert along the Sweetwater River with granite domes (Independence Rock, Devil's Gate, Split Rock, the Sweetwater Rocks) rising from the plain, climbing west to the broad saddle of South Pass on the Continental Divide.",
         "indigenous": ["Sweetwater — translation of the trappers' 'Eau Sucrée'; the Shoshone name is not consistently recorded — verify.", "Split Rock was a Shoshone and Arapaho landmark; oral names not recorded in GNIS."],
         "trails": ["Oregon, California, Mormon and Pony Express trails all follow the Sweetwater: Independence Rock, Devil's Gate, Martin's Cove, Split Rock, Ice Slough, Rocky Ridge, South Pass.", "Lander Cutoff and Seminoe Cutoff.", "Cherokee Trail to the south."],
         "history": "Emigrant names carved on Independence Rock (1840s–60s); Martin's Cove handcart tragedy 1856; South Pass City and Atlantic City gold (1867); Carissa mine.",
         "ownership": "Independence Rock is a state historic site (free, rest area); Devil's Gate and Martin's Cove are on LDS-managed land with a visitor centre (buildings — rules question); Split Rock is BLM with a highway interpretive pullout; South Pass City is a state park (fee, buildings); the Sweetwater Rocks are BLM.",
         "community": "The TreasureNet full walkthrough: Devil's Gate = ancient gates, Split Rock = double arcs on granite, ending at South Pass. Objection: no proper-noun Hole; everything is beside a highway.",
         "elimination": "in play",
         "searchers": "Many; the walkthrough was widely read.",
     }},
    {"id": "windriver", "name": "Wind River Range & Lander front", "states": "WY", "bbox": [42.5, -109.9, 43.7, -108.0], "status": "hot",
     "dossier": {
         "terrain": "Wyoming's highest range: a granite core with glacial cirques and hundreds of tarns, flanked on the east by the Wind River Reservation and the limestone canyons of the Popo Agie (Sinks Canyon) and on the north by the Wind River Canyon through the Owl Creek Mountains to Thermopolis.",
         "indigenous": ["Popo Agie — Crow, usually glossed 'beginning of the waters' or 'gurgling river' — verify.", "Washakie — Shoshone chief; Fort Washakie is the reservation seat; Sacagawea's reputed grave is there (a grave — excluded as a site).", "Wind River — the Shoshone called it the 'Warm Valley' (translation commonly cited)."],
         "trails": ["Lander Cutoff of the Oregon Trail; Union Pass (Astorians 1811); Sheridan's 1877 Sinks Canyon route."],
         "history": "Atlantic City–South Pass gold to the south; Sinks Canyon CCC road; Thermopolis hot springs deeded by Chief Washakie (1896, the 'gift of the waters').",
         "ownership": "Shoshone NF (free) above Sinks Canyon State Park (free, dogs on leash); Wind River Reservation (tribal permit required — a rules question); Hot Springs State Park (free but hours 6–10 — a rules question); BLM in the Wind River Canyon; Bridger-Teton on the west slope.",
         "community": "Sinks Canyon (a natural Hole where the river vanishes and a Rise where it surges up) is on the list of places Posey searched for Fenn; Thermopolis offers 'Wedding of the Waters' for the bride at the gates. Objection: stanza 3 is unpinned in both.",
         "elimination": "in play",
         "searchers": "Growing since the Fenn-footprint statement; Sinks Canyon is a known Posey Fenn location.",
     }},
    {"id": "lasals", "name": "La Sal Mountains & Moab", "states": "UT", "bbox": [38.3, -109.9, 38.9, -109.0], "status": "active",
     "dossier": {
         "terrain": "Red sandstone canyon country around Moab (arches, fins, the Colorado River) rising to the laccolithic La Sal peaks above 12,000 ft with aspen basins, Medicine Lakes, Warner and Oowah lakes on the north and east slopes.",
         "indigenous": ["Tukuhnikivatz — Ute, commonly glossed 'where the sun sets last' or 'where the sun lingers' — verify.", "La Sal — Spanish 'the salt' (Dominguez–Escalante 1776).", "Moab — biblical name given by Mormon settlers; the Ute name for the valley is not consistently recorded."],
         "trails": ["Old Spanish Trail crossed the Colorado at Moab.", "Dominguez–Escalante expedition 1776 skirted the range.", "La Sal Loop Road; Geyser Pass and La Sal Pass roads (high-clearance in places)."],
         "history": "Uranium boom 1950s (Charlie Steen); Potash Road; Matrimony Spring roadside legend; Castle Valley.",
         "ownership": "Manti-La Sal NF on the range (free); BLM around Moab (some fee sites); Arches NP (fee, excluded by 24/7 access); private in Castle Valley and along the river road.",
         "community": "The user's own working solve (Matrimony Spring, Corona/Bowtie arches, Medicine Lakes). Objections: outside Fenn's 2013 map, no granite (sandstone and intrusive porphyry), no bear name among the peaks, Medicine Lakes trailhead is a developed 4WD site.",
         "elimination": "in play — but outside the Fenn map, which Posey used as his hunt area",
         "searchers": "Some; the region is favoured mostly by Utah locals.",
     }},
    {"id": "cityofrocks", "name": "City of Rocks & the Idaho–Utah border", "states": "ID,UT", "bbox": [41.6, -114.3, 42.6, -111.0], "status": "inplay",
     "dossier": {
         "terrain": "Granite spires and domes (City of Rocks, Castle Rocks) on the California Trail, the Raft River valley, and east across the Curlew and Malad valleys to Bear Lake and the Bear River Range (limestone canyons, caves).",
         "indigenous": ["Bear River — Shoshone name commonly glossed as relating to the bear; verify.", "City of Rocks: Shoshone-Bannock seasonal camps; no widely cited native name for the spires."],
         "trails": ["California Trail (Register Rock, Twin Sisters as the trail's 'gateway'), Salt Lake Alternate, Kelton Road; Oregon Trail on the Snake to the north."],
         "history": "Emigrant axle-grease signatures on Register Rock (1840s–50s); Almo massacre legend (disputed); Bear Lake Monster legend; Minnetonka Cave.",
         "ownership": "City of Rocks National Reserve (NPS/Idaho parks, free day use, dogs on leash, some fees to camp); Castle Rocks State Park (fee); Caribou-Targhee and Sawtooth NF; BLM; Bear Lake shoreline largely private/state park (fee).",
         "community": "Strong on stanza 4 (granite, twins, arches) and weak on stanzas 2–3; the 42nd parallel is the state line, feeding the '42' number theories.",
         "elimination": "in play",
         "searchers": "Light.",
     }},
    {"id": "bearlake", "name": "Bear Lake", "states": "ID,UT", "bbox": [41.75, -111.6, 42.25, -111.1], "status": "inplay",
     "dossier": {
         "terrain": "A turquoise 20-mile lake on the Idaho–Utah line, the Bear River Range (limestone) to the west with Logan Canyon, Minnetonka Cave and Bloomington Lake; the Bear River loops around the north end.",
         "indigenous": ["Bear Lake — 'Black Bear Lake' in the trappers' record (Donald Mackenzie, 1819); Shoshone name not consistently recorded."],
         "trails": ["Oregon Trail passed north of the lake through Montpelier; 1827 fur rendezvous on the south shore."],
         "history": "1827 and 1828 rendezvous; Bear Lake Monster newspaper legend (1868); Paris, ID tabernacle.",
         "ownership": "State parks on the shore (fee); Caribou-Targhee NF and Uinta-Wasatch-Cache NF in the range (free); much private shoreline.",
         "community": "Bear name for ursa; a lake rather than a hole; little else pinned.",
         "elimination": "in play",
         "searchers": "Light.",
     }},
    {"id": "blackhills", "name": "Black Hills & Bear Lodge", "states": "SD,WY", "bbox": [43.5, -104.9, 44.9, -103.2], "status": "fringe",
     "dossier": {
         "terrain": "A granite core (Needles, Cathedral Spires, Black Elk Peak) ringed by limestone and red beds; Devils Tower (phonolite) and the Bear Lodge Mountains on the Wyoming side; Spearfish Canyon waterfalls.",
         "indigenous": ["Paha Sapa (Lakota, 'hills that are black'); Mato Tipila (Lakota, 'bear lodge') for Devils Tower; Bear Butte is Mato Paha, a sacred site — access restrictions and sacred-site status are rules questions."],
         "trails": ["Custer's 1874 expedition; Cheyenne–Deadwood stage; Sidney–Deadwood trail."],
         "history": "1876 gold rush; Deadwood; Homestake mine; Mount Rushmore and Crazy Horse (man-made — excluded).",
         "ownership": "Black Hills NF (free); Custer State Park (fee); Wind Cave and Jewel Cave (caves, excluded); Devils Tower NM (fee); Bear Butte State Park (fee).",
         "community": "'Ursa' as Bear Lodge; the Needles for 'needle' names; outside Fenn's map, which most searchers treat as a soft exclusion.",
         "elimination": "in play but outside the Fenn map",
         "searchers": "Very light.",
     }},
    {"id": "alaska", "name": "Alaska", "states": "AK", "bbox": [54.0, -170.0, 71.5, -130.0], "status": "fringe",
     "dossier": {
         "terrain": "Not covered by any built-in feature. The 'Alaska' reading (Mike Unfiltered) rests on the north star and the state flag's Big Dipper; nothing in the poem has been pinned to a named Alaskan feature by anyone.",
         "indigenous": ["Coverage gap — no entries."],
         "trails": ["Coverage gap."],
         "history": "Coverage gap.",
         "ownership": "Mostly federal and state land; public access broad. Coverage gap for specifics.",
         "community": "Fringe theory; kept as a reference solve so it can be compared, not because it is supported.",
         "elimination": "not eliminated; outside the Fenn map; Posey has said the American West / the map he printed",
         "searchers": "Unknown.",
     }},
    {"id": "jacksonhole", "name": "Jackson Hole & Gros Ventre", "states": "WY", "bbox": [43.2, -111.0, 44.0, -110.2], "status": "inplay",
     "dossier": {
         "terrain": "The valley (a proper-noun 'Hole') between the Tetons and the Gros Ventre; Granite Creek and Granite Hot Springs in the Gros Ventre; the Sleeping Indian (Sheep Mountain) on the east rim; Snake and Hoback rivers.",
         "indigenous": ["Teton — French trappers' 'Trois Tétons'; Shoshone names for the peaks are recorded inconsistently.", "Gros Ventre — French for the Atsina people."],
         "trails": ["Astorians 1811 over Teton Pass; Jackson's Hole named for trapper David Jackson (1829)."],
         "history": "Fur trade rendezvous; dude ranching; Grand Teton NP (fee — excluded inside the park boundary); Bridger-Teton NF outside it is free.",
         "ownership": "Grand Teton NP (fee); Bridger-Teton NF (free, dogs); National Elk Refuge (restricted); Granite Hot Springs pool is a fee concession but the creek and canyon are NF.",
         "community": "Posey named Jackson Hole as an example of a proper-noun Hole; searchers read the Tetons as 'her' and 'three'. Objection: he named it as an example, not a clue.",
         "elimination": "in play",
         "searchers": "Moderate.",
     }},
    {"id": "gates", "name": "Helena, Gates of the Mountains & the Missouri", "states": "MT", "bbox": [46.5, -112.3, 47.1, -111.6], "status": "inplay",
     "dossier": {
         "terrain": "Limestone cliffs where the Missouri cuts the Big Belt front (the 'Gates'), Holter Lake behind the dam, the Sleeping Giant (Beartooth Mountain) profile to the west.",
         "indigenous": ["The Gates were a Blackfeet and Salish travel corridor; native names for the canyon are not consistently recorded."],
         "trails": ["Lewis and Clark named the Gates on 19 July 1805.", "Mullan Road passed to the west."],
         "history": "Last Chance Gulch (1864) founded Helena; Holter Dam 1918.",
         "ownership": "Helena NF and BLM around Holter Lake (free except developed campgrounds); the Gates boat tour is a private concession; Sleeping Giant WSA is BLM (free).",
         "community": "The most literal 'ancient gates' in the West beside a sleeping 'he'; objection: limestone, not granite.",
         "elimination": "in play",
         "searchers": "Light to moderate.",
     }},
]

# ---------------------------------------------------------------- feature inventory
# (name, ftype, lat, lon, elev_ft, state, region, owner, access, car, rules_flags, aliases/native names, notes)
# ftype vocabulary: arch, waterfall, hotspring, spring, rock, cirque, pair, pass, gate, bend, confluence, face, pool, hole, peak, lake, river, town, historic, cave, monument
F = []


def _f(name, ftype, lat, lon, elev, state, region, owner, access, car, flags, aliases=(), notes="", keys=()):
    F.append({"name": name, "ftype": ftype, "lat": lat, "lon": lon, "elev": elev, "state": state, "region": region, "owner": owner, "access": access, "car": car, "flags": list(flags), "aliases": list(aliases), "notes": notes, "keys": list(keys)})


# Montana — Big Hole / Beaverhead / Pioneers
_f("Wisdom", "town", 45.6166, -113.4536, 6060, "MT", "bighole", "town", "US-43", "yes", [], ["Wisdom River (Lewis & Clark's name for the Big Hole River)"], "Town on the Big Hole River named after the river Lewis named for Jefferson's 'wisdom'.", ["wisdom"])
_f("Big Hole River", "river", 45.62, -113.45, 6050, "MT", "bighole", "mixed", "public fishing access sites along US-43 and MT-43", "yes", [], ["Wisdom River (1805)"], "Blue-ribbon trout river; the 'Hole' of the Montana theory. Proper-noun natural Hole.", ["hole", "wisdom", "waters"])
_f("Big Hole River at Wise River", "confluence", 45.79, -112.95, 5680, "MT", "pioneers", "FAS/public", "MT-43 at Wise River", "yes", [], [], "Wise River joins the Big Hole at the foot of the Pioneer byway.", ["hole", "wise", "bend"])
_f("Beaverhead Rock", "rock", 45.4267, -112.4563, 5000, "MT", "bighole", "state park (day use, free)", "MT-41 pullout", "yes", [], ["Point of Rocks"], "Sacagawea's landmark, Aug 1805. Visible-only (no trail to the top); a 'bride' candidate that is not alive but visible.", ["bride", "face", "sacagawea"])
_f("Clark Canyon Reservoir (Camp Fortunate)", "lake", 45.00, -112.87, 5560, "MT", "bighole", "BOR (free)", "I-15 exit 44", "yes", [], ["Camp Fortunate"], "Lewis & Clark's Camp Fortunate lies under the reservoir; Sacagawea reunited with her brother nearby.", ["sacagawea", "waters"])
_f("Bannack", "historic", 45.16, -112.998, 5800, "MT", "grasshopper", "state park (fee)", "Bannack Rd", "yes", ["buildings", "fee"], [], "Ghost town; buildings and a fee — excluded as a site, useful as a waypoint.", ["gold", "past"])
_f("Grasshopper Creek", "river", 45.15, -113.0, 5800, "MT", "grasshopper", "BLM/private", "Bannack Rd", "yes", [], ["Willard's Creek (Lewis & Clark)"], "1862 gold creek; book chapter 'Grasshopper Valley'.", ["gold", "waters"])
_f("Polaris", "town", 45.366, -113.122, 6400, "MT", "pioneers", "town/NF", "Pioneer Mountains Scenic Byway", "yes", [], ["Polaris mine"], "Named for the Polaris silver mine; the north-star name behind the 'ursa' reading.", ["polaris", "north star", "ursa"])
_f("Elkhorn Hot Springs", "hotspring", 45.4483, -113.1236, 7400, "MT", "pioneers", "private resort on NF", "Byway", "yes", ["buildings", "private"], [], "Commercial hot springs — surge candidate but private with buildings.", ["surge", "hot"])
_f("Crystal Park", "rock", 45.487, -113.113, 7800, "MT", "pioneers", "FS (day fee in season)", "Byway", "yes", ["fee"], [], "Public quartz-crystal digging on Pioneer batholith granite; developed site with toilets.", ["granite", "crystal", "secrets"])
_f("Coolidge ghost town (Elkhorn mine)", "historic", 45.48, -113.09, 7100, "MT", "pioneers", "NF", "gravel spur off byway, 1.5 mi walk", "mostly", ["buildings"], [], "Mining ruins; buildings.", ["past", "silence"])
_f("Maverick Mountain", "peak", 45.44, -113.13, 8400, "MT", "pioneers", "NF/ski lease", "Byway", "yes", ["buildings"], [], "Small ski area.", [])
_f("Torrey Mountain", "peak", 45.42, -113.03, 11147, "MT", "pioneers", "NF", "trail from Dinner Station CG", "approach only", ["high"], [], "Highest East Pioneer summit; well above a mile high.", ["three"])
_f("Jackson Hot Springs", "hotspring", 45.367, -113.404, 6470, "MT", "bighole", "private lodge", "MT-278 at Jackson", "yes", ["buildings", "private"], [], "Lewis & Clark's 'boiling spring' 1806; private lodge.", ["surge", "hot"])
_f("Big Hole National Battlefield", "historic", 45.646, -113.643, 6300, "MT", "bighole", "NPS (free)", "MT-43", "yes", ["battle", "graves"], [], "1877 battle site — excluded by the rules (graves/battle).", ["past"])
_f("Chief Joseph Pass", "pass", 45.69, -113.95, 7241, "MT", "bighole", "NF", "MT-43 / US-93", "yes", [], [], "Continental Divide pass on the Nez Perce route.", ["pass", "gate"])
_f("Big Hole Pass", "pass", 45.34, -113.57, 7360, "MT", "bighole", "NF", "MT-278", "yes", [], [], "Divide pass between Jackson and the Bloody Dick country.", ["pass", "hole"])
_f("Lemhi Pass", "pass", 44.974, -113.445, 7373, "MT", "bighole", "FS (Sacajawea Memorial Area, free)", "gravel, passenger car dry season, closed winter", "yes (dry)", [], ["Sacajawea Memorial Area"], "Continental Divide crossing of Lewis & Clark; Sacagawea's return to the Shoshone.", ["sacagawea", "return", "pass", "gate"])
_f("Twin Bridges", "confluence", 45.546, -112.332, 4630, "MT", "bighole", "FAS (free)", "MT-41", "yes", [], ["Three Forks of the Jefferson"], "Big Hole, Beaverhead and Ruby (Wisdom, Philosophy, Philanthropy) make the Jefferson.", ["three", "twin", "confluence", "wisdom"])
_f("Hidden Lake (Anaconda-Pintler)", "lake", 46.05, -113.30, 8500, "MT", "bighole", "NF wilderness (free)", "trail from Storm Lake, 3+ mi", "no (trail)", ["far"], [], "Cirque lake; the Hub-featured Hidden Lake solve. Coordinates approximate — verify.", ["hidden", "secret", "lake", "arcs"])
_f("Storm Lake", "lake", 46.06, -113.29, 8000, "MT", "bighole", "NF", "rough road, high clearance", "no", ["high-clearance"], [], "Trailhead lake below Storm Lake Pass; the road is not passenger-car.", ["lake"])
_f("Rainbow Arch bridge, Warm Springs", "monument", 46.18, -112.78, 4800, "MT", "gates", "state WMA", "Warm Springs road", "yes", ["man-made", "buildings"], [], "Double-arched stone bridge — man-made; a 'double arcs' candidate only as a mark.", ["arcs", "double", "warm"])
_f("Lewis and Clark Caverns", "cave", 45.83, -111.87, 5200, "MT", "bighole", "state park (fee)", "MT-2", "yes", ["cave", "fee"], [], "Cave — excluded.", ["cave"])
# Montana — Helena / Missouri / Bozeman
_f("Gates of the Mountains", "gate", 46.8446, -111.913, 3600, "MT", "gates", "Helena NF / private tour dock", "I-15 exit 209; boat tour", "yes (dock)", [], [], "Lewis 1805 named the limestone cliffs 'the gates of the rocky mountains'.", ["gates", "ancient", "gate"])
_f("Sleeping Giant (Beartooth Mountain)", "face", 46.83, -112.02, 6792, "MT", "gates", "BLM WSA (free)", "Sleeping Giant Rd off I-15", "gravel", [], ["Beartooth Mountain"], "The giant's profile lies with head to the east; 'bear' name for ursa; a 'he' alive or not by perspective.", ["ursa", "bear", "face", "sleeping", "he"])
_f("Holter Lake", "lake", 46.99, -112.01, 3560, "MT", "gates", "BLM (fee campgrounds)", "Beartooth Rd", "yes", [], [], "Reservoir above Holter Dam; blue-ribbon Missouri below.", ["waters", "lake"])
_f("Missouri Headwaters (Three Forks)", "confluence", 45.926, -111.507, 4045, "MT", "bighole", "state park (fee)", "I-90 exit 278", "yes", ["fee"], [], "Jefferson, Madison and Gallatin make the Missouri; Sacagawea was taken here.", ["three", "confluence", "sacagawea"])
_f("Sacajawea Peak", "peak", 45.90, -110.96, 9665, "MT", "gates", "Custer-Gallatin NF", "Fairy Lake trailhead, rough road", "no", ["high", "high-clearance"], ["Sacagawea Peak"], "Highest Bridger summit; a bride's name on a peak.", ["sacagawea", "bride", "peak"])
_f("Bear Trap Canyon", "gate", 45.61, -111.60, 4900, "MT", "gates", "BLM wilderness (free)", "trailhead at Ennis Lake dam", "yes", [], [], "Madison River canyon; a literal Bear for ursa; gneiss and granite walls.", ["bear", "ursa", "canyon", "gate"])
_f("Sphinx Mountain", "face", 45.13, -111.48, 10876, "MT", "gates", "Custer-Gallatin NF", "trail", "no", ["high"], ["The Helmet (adjacent)"], "A named face in the Madison Range.", ["face", "sphinx"])
_f("Quake Lake", "lake", 44.83, -111.42, 6400, "MT", "gates", "NF (free)", "US-287", "yes", [], ["Earthquake Lake"], "Formed by the 1959 landslide; Posey searched the Madison corridor for Fenn.", ["lake", "past"])
_f("Hebgen Lake", "lake", 44.87, -111.33, 6530, "MT", "gates", "NF", "US-287", "yes", [], [], "Posey's Fenn search area.", ["lake", "fenn"])
_f("Baker's Hole", "hole", 44.70, -111.10, 6640, "MT", "gates", "NF campground (fee)", "US-191", "yes", ["fee"], [], "Named Hole on the Madison north of West Yellowstone; the Greer solve's start.", ["hole", "waters"])
_f("Devil's Slide (Gardiner)", "rock", 45.08, -110.79, 5200, "MT", "gates", "private/roadside", "US-89 pullout", "yes", ["private"], [], "Posey searched here for Fenn; visible from the road.", ["rock", "bold"])
_f("Boiling River (Gardiner)", "hotspring", 44.99, -110.69, 5600, "MT", "gates", "NPS (fee, closed since 2022)", "US-89", "yes", ["fee", "closed"], [], "Posey searched here for Fenn; inside Yellowstone.", ["surge", "hot", "fenn"])
# Wyoming — Sweetwater / South Pass
_f("Independence Rock", "rock", 42.4936, -107.1319, 6028, "WY", "sweetwater", "state historic site (free rest area)", "WY-220", "yes", ["buildings"], [], "Granite dome with 5,000 carved emigrant names; rest area with toilets.", ["granite", "names", "past", "secrets"])
_f("Devil's Gate", "gate", 42.4467, -107.2131, 6000, "WY", "sweetwater", "LDS-managed (Martin's Cove) / BLM", "WY-220, visitor centre", "yes", ["buildings"], [], "370-ft granite cleft cut by the Sweetwater; the emigrants' gate.", ["gate", "gates", "ancient", "granite"])
_f("Martin's Cove", "historic", 42.47, -107.24, 6000, "WY", "sweetwater", "LDS-managed", "visitor centre", "yes", ["buildings", "graves"], [], "1856 handcart tragedy site; memorial.", ["past", "graves"])
_f("Split Rock", "rock", 42.4762, -107.5661, 6300, "WY", "sweetwater", "BLM (highway interpretive site)", "US-287 pullout", "yes", [], [], "Granite notch on the Sweetwater Rocks; the TreasureNet 'double arcs'.", ["granite", "double", "split", "gate"])
_f("Ice Slough", "spring", 42.42, -107.83, 6500, "WY", "sweetwater", "BLM", "US-287", "yes", [], [], "Emigrant ice-in-summer marsh.", ["waters", "silent"])
_f("South Pass", "pass", 42.35, -108.88, 7412, "WY", "sweetwater", "BLM", "WY-28", "yes", [], [], "The Oregon Trail's Continental Divide crossing; broad and gentle.", ["pass", "gate", "return", "divide"])
_f("South Pass City", "historic", 42.468, -108.802, 7800, "WY", "sweetwater", "state park (fee)", "gravel", "yes", ["buildings", "fee"], [], "Gold-camp ghost town, 1867.", ["gold", "past"])
_f("Atlantic City", "historic", 42.49, -108.73, 7700, "WY", "sweetwater", "town/BLM", "gravel", "yes", ["buildings"], [], "Gold camp; Carissa mine nearby.", ["gold"])
_f("Sweetwater Rocks", "rock", 42.55, -107.5, 6500, "WY", "sweetwater", "BLM", "US-287; two-track", "partly", [], [], "A 20-mile granite range of domes north of the river.", ["granite", "bold"])
# Wyoming — Wind River / Lander / Thermopolis
_f("The Sinks (Sinks Canyon)", "hole", 42.7315, -108.8357, 6300, "WY", "windriver", "Sinks Canyon State Park (free)", "WY-131", "yes", ["cave-adjacent"], [], "The Popo Agie vanishes into a limestone cavern — a natural Hole; the cavern itself is off-limits (cave).", ["hole", "sinks", "waters", "silent"])
_f("The Rise (Sinks Canyon)", "pool", 42.7397, -108.8187, 6200, "WY", "windriver", "Sinks Canyon State Park (free)", "WY-131", "yes", [], [], "Spring pool where the river surges back up, full of huge trout; fishing prohibited here.", ["surge", "clear", "bright", "pool", "waters"])
_f("Popo Agie Falls", "waterfall", 42.70, -108.87, 7000, "WY", "windriver", "Shoshone NF (free)", "Bruce's Bridge trailhead, 1.5 mi trail", "trail", ["trail"], [], "Falls above Sinks Canyon; reached only by trail (a rules question).", ["waterfall", "waters"])
_f("Sacagawea's grave, Fort Washakie", "monument", 43.0057, -108.9022, 5600, "WY", "windriver", "Wind River Reservation cemetery", "Fort Washakie", "yes", ["graves", "reservation"], [], "A grave — excluded as a site; a 'bride not alive but visible' as a statue.", ["sacagawea", "bride", "graves"])
_f("Bears Ears (Wind River Range)", "peak", 43.15, -109.35, 11800, "WY", "windriver", "Shoshone NF", "trail", "no", ["high"], [], "Twin-summit peak in the northern Winds; coordinates approximate — verify in GNIS.", ["bear", "ursa", "pair", "twin"])
_f("Torrey Lake petroglyphs", "rock", 43.45, -109.55, 7800, "WY", "windriver", "Whiskey Basin WHMA (state)", "gravel road from Dubois", "yes", [], [], "Dinwoody-style petroglyphs incl. bighorn horns (double arcs) on sandstone boulders.", ["arcs", "double", "past", "secrets"])
_f("Union Pass", "pass", 43.49, -109.83, 9210, "WY", "windriver", "Shoshone/Bridger-Teton NF", "gravel, closed winter", "yes (dry)", ["high"], [], "Triple divide (Missouri, Colorado, Columbia).", ["three", "pass", "divide"])
_f("Wedding of the Waters", "confluence", 43.5963, -108.2085, 4400, "WY", "windriver", "public fishing access (free)", "US-20", "yes", [], [], "Where the Wind River becomes the Bighorn at the canyon mouth — a 'bride' by name at the gates.", ["bride", "wedding", "gates", "waters", "confluence"])
_f("Wind River Canyon", "gate", 43.55, -108.20, 4500, "WY", "windriver", "BLM / reservation (tunnels)", "US-20", "yes", ["tunnel-adjacent"], [], "Canyon through the Owl Creek Mountains with 2.9-billion-year rock; three highway tunnels (tunnels excluded).", ["gates", "ancient", "time", "granite"])
_f("Big Spring (Thermopolis)", "hotspring", 43.6533, -108.199, 4350, "WY", "windriver", "Hot Springs State Park (free, hours 6–10)", "US-20", "yes", ["hours", "buildings"], [], "3.6 million gallons a day; the state bathhouse is free.", ["surge", "hot", "clear", "bright"])
_f("Boysen Reservoir", "lake", 43.42, -108.17, 4725, "WY", "windriver", "state park (fee)", "US-20", "yes", ["fee"], [], "Reservoir above the canyon.", ["lake"])
_f("Cirque of the Towers", "cirque", 42.77, -109.21, 10500, "WY", "windriver", "Bridger Wilderness", "Big Sandy trailhead, 8+ mi", "no", ["far", "high"], [], "Famous granite cirque; far beyond a mile from any car.", ["cirque", "granite", "arcs"])
_f("Photographers Point", "face", 42.85, -109.63, 10000, "WY", "windriver", "Bridger-Teton NF", "Elkhart Park, 4.5 mi trail", "no", ["far", "high"], [], "Overlook of the Winds' granite peaks.", [])
# Wyoming — Jackson Hole / Gros Ventre / Tetons
_f("Jackson Hole", "hole", 43.48, -110.76, 6200, "WY", "jacksonhole", "mixed", "US-89/191", "yes", [], ["Jackson's Hole"], "Posey's example of a proper-noun Hole.", ["hole"])
_f("Granite Hot Springs", "hotspring", 43.3598, -110.4416, 6900, "WY", "jacksonhole", "Bridger-Teton NF (pool concession fee; creek free)", "Granite Creek Rd, 10 mi gravel, closed winter", "yes (summer)", ["fee-pool"], [], "Hot water surges up Granite Creek; falls below the pool.", ["surge", "hot", "granite"])
_f("Granite Creek Falls", "waterfall", 43.35, -110.44, 6800, "WY", "jacksonhole", "Bridger-Teton NF (free)", "Granite Creek Rd", "yes", [], [], "Falls on Granite Creek below the springs.", ["waterfall", "granite", "waters"])
_f("Sleeping Indian (Sheep Mountain)", "face", 43.55, -110.55, 11239, "WY", "jacksonhole", "Bridger-Teton NF", "visible from US-89; summit by trail", "no (summit)", ["high"], ["Sheep Mountain"], "A named profile on the Gros Ventre rim; 'he' alive or not by perspective.", ["face", "he", "sleeping"])
_f("Grand Teton", "peak", 43.7412, -110.8024, 13775, "WY", "jacksonhole", "Grand Teton NP (fee)", "climbing", "no", ["fee", "climbing", "high"], ["Trois Tétons"], "'Her' and 'three' in the Tetons reading; inside a fee park.", ["three", "her", "peak"])
_f("Shadow Mountain", "peak", 43.72, -110.60, 8250, "WY", "jacksonhole", "Bridger-Teton NF (free)", "gravel road to the top", "yes (dry)", [], [], "Named for its shadow at sunset; free NF viewpoint of the Tetons.", ["shadow", "sight"])
_f("Teton Pass", "pass", 43.499, -110.956, 8431, "WY", "jacksonhole", "NF", "WY-22", "yes", [], [], "Astorians' 1811 crossing.", ["pass", "gate"])
_f("Hoback Junction", "confluence", 43.28, -110.74, 5900, "WY", "jacksonhole", "public", "US-89", "yes", [], [], "Hoback joins the Snake; canyon downstream.", ["confluence", "waters"])
# Wyoming — other
_f("Hole-in-the-Wall", "hole", 43.47, -106.98, 5600, "WY", "windriver", "BLM (free)", "gravel from Kaycee; Outlaw Cave CG", "yes (dry)", [], [], "The outlaw pass through the Red Wall; a Hole that is itself a gate; sandstone.", ["hole", "gate", "past"])
_f("Medicine Wheel", "monument", 44.826, -107.922, 9640, "WY", "windriver", "Bighorn NF (restricted, 1.5 mi walk)", "US-14A, closed till June", "yes (summer)", ["high", "sacred", "restricted"], [], "Ancient stone circle — sacred site; access restrictions.", ["sacred", "ancient", "arcs", "wonder"])
_f("Devils Tower", "monument", 44.590, -104.715, 5112, "WY", "blackhills", "NPS (fee)", "WY-24", "yes", ["fee"], ["Bear Lodge (Mato Tipila)", "Bear's Tipi"], "Lakota 'Bear Lodge'; a national monument with a fee.", ["bear", "ursa", "lodge", "realm"])
_f("Bear Lodge Mountains", "peak", 44.55, -104.5, 6600, "WY", "blackhills", "Black Hills NF (free)", "gravel FS roads", "yes", [], [], "The range east of Devils Tower; 'ursa' as a proper-noun Bear Lodge.", ["bear", "ursa", "lodge", "realm"])
_f("Vedauwoo", "rock", 41.16, -105.37, 8000, "WY", "sweetwater", "Medicine Bow NF (day fee at main area)", "I-80 exit 329", "yes", ["fee"], [], "Sherman granite blobs on Pole Mountain.", ["granite", "pole", "bold"])
_f("Ayres Natural Bridge", "arch", 42.73, -105.61, 5000, "WY", "sweetwater", "Converse County park (free, hours)", "I-25 exit 151", "yes", ["hours"], [], "Natural arch over LaPrele Creek; park hours apply.", ["arch", "arcs", "bridge"])
# Utah — La Sals / Moab
_f("Corona Arch", "arch", 38.579, -109.621, 4600, "UT", "lasals", "BLM (free)", "Potash Rd, 1.5 mi trail with cable/ladder", "yes", ["ladder", "trail"], [], "Large sandstone arch; the trail uses a bolted cable and a short ladder (rules question).", ["arch", "arcs", "crown", "corona"])
_f("Bowtie Arch", "arch", 38.580, -109.620, 4600, "UT", "lasals", "BLM", "same trail as Corona", "yes", ["trail"], [], "Pothole arch beside Corona — a natural pair of arcs.", ["arch", "arcs", "double", "pair"])
_f("Jeep Arch", "arch", 38.60, -109.62, 4800, "UT", "lasals", "BLM", "Potash Rd, 2 mi trail", "yes", ["trail"], ["Gold Bar Arch"], "Arch shaped like a jeep; the user's cover-shape candidate. Coordinates approximate.", ["arch", "arcs", "gold"])
_f("Matrimony Spring", "spring", 38.575, -109.53, 4000, "UT", "lasals", "roadside (UDOT)", "US-191 / SR-128 junction", "yes", ["man-made pipe"], [], "Roadside spring with a wedding legend; piped outlet.", ["bride", "wedding", "spring", "surge", "waters"])
_f("Medicine Lakes", "pair", 38.42, -109.24, 10000, "UT", "lasals", "Manti-La Sal NF", "La Sal Pass Rd, 4WD spur; trailhead toilets", "no", ["high-clearance", "buildings", "high"], [], "Paired lakes at Tukuhnikivatz's south foot; developed trailhead.", ["pair", "double", "lake", "medicine"])
_f("Mount Tukuhnikivatz", "peak", 38.44, -109.26, 12482, "UT", "lasals", "Manti-La Sal NF", "trail from La Sal Pass", "no", ["high"], ["Tuk", "'where the sun sets last' (Ute, commonly cited)"], "Ute-named peak; translation commonly cited, verify.", ["light", "sun", "peak"])
_f("Mount Peale", "peak", 38.438, -109.229, 12721, "UT", "lasals", "Manti-La Sal NF", "trail", "no", ["high"], [], "Highest La Sal.", ["peak"])
_f("Mount Waas", "peak", 38.54, -109.23, 12331, "UT", "lasals", "NF", "trail", "no", ["high"], [], "Named for a Ute leader (commonly cited).", ["peak"])
_f("Gold Basin", "cirque", 38.47, -109.26, 10500, "UT", "lasals", "NF", "Gold Basin Rd, gravel", "partly", ["high"], [], "Cirque below Tukuhnikivatz's north face.", ["gold", "cirque", "arcs"])
_f("La Sal Pass", "pass", 38.41, -109.24, 10100, "UT", "lasals", "NF", "gravel, snow till June", "yes (dry)", ["high"], [], "Pass between Tuk and South Mountain.", ["pass"])
_f("Warner Lake", "lake", 38.52, -109.28, 9400, "UT", "lasals", "NF campground (fee)", "La Sal Loop, gravel", "yes", ["fee"], [], "Small lake with campground.", ["lake"])
_f("Oowah Lake", "lake", 38.50, -109.29, 8800, "UT", "lasals", "NF (free)", "gravel", "yes", [], [], "Small lake; free.", ["lake"])
_f("Fisher Towers", "rock", 38.72, -109.31, 4700, "UT", "lasals", "BLM (free)", "SR-128", "yes", [], [], "Sandstone towers.", ["rock", "bold"])
_f("Castleton Tower", "rock", 38.65, -109.37, 6600, "UT", "lasals", "BLM/private base", "Castle Valley", "yes", [], [], "Sandstone tower.", ["rock", "castle"])
_f("Delicate Arch", "arch", 38.7436, -109.4993, 4800, "UT", "lasals", "Arches NP (fee, timed entry)", "trail 1.5 mi", "yes", ["fee", "trail"], [], "Inside a fee park — excluded.", ["arch"])
_f("Bridal Veil Falls (Provo)", "waterfall", 40.34, -111.60, 4600, "UT", "lasals", "Utah County park (free)", "US-189", "yes", [], [], "Named 'bridal' falls; the maiden's-tears legend; Timpanogos's profile above.", ["bride", "waterfall", "veil", "face"])
_f("Mount Timpanogos", "face", 40.39, -111.65, 11752, "UT", "lasals", "Uinta-Wasatch-Cache NF", "trail", "no", ["high"], [], "Sleeping-woman profile of legend.", ["face", "her", "sleeping"])
# Idaho / Utah border
_f("Twin Sisters (City of Rocks)", "pair", 42.0525, -113.7278, 6800, "ID", "cityofrocks", "City of Rocks NR (free day use)", "Reserve road", "yes", [], [], "Paired granite spires; the California Trail's gateway.", ["twin", "pair", "double", "granite", "gate"])
_f("Register Rock (City of Rocks)", "rock", 42.07, -113.72, 6300, "ID", "cityofrocks", "City of Rocks NR", "Reserve road", "yes", [], [], "Emigrant axle-grease signatures.", ["names", "past", "secrets"])
_f("Castle Rocks", "rock", 42.13, -113.68, 6000, "ID", "cityofrocks", "state park (fee)", "Almo", "yes", ["fee"], [], "Granite domes; fee park.", ["granite", "castle"])
_f("Bear Lake", "lake", 41.99, -111.33, 5924, "ID", "bearlake", "state parks (fee) / private shore", "US-89", "yes", ["fee-shore"], ["Black Bear Lake (1819)"], "Bear name for ursa.", ["bear", "ursa", "lake"])
_f("Minnetonka Cave", "cave", 42.09, -111.53, 7700, "ID", "bearlake", "NF (fee tours)", "St Charles Canyon", "yes", ["cave", "fee"], [], "Cave — excluded.", ["cave"])
_f("Bloomington Lake", "lake", 42.17, -111.43, 8200, "ID", "bearlake", "Caribou-Targhee NF (free)", "gravel, 0.5 mi trail", "yes (dry)", [], [], "Cirque lake with a rope swing.", ["lake", "cirque"])
_f("Big Springs (Island Park)", "spring", 44.50, -111.26, 6400, "ID", "cityofrocks", "Caribou-Targhee NF (free)", "Big Springs Rd", "yes", [], [], "120 million gal/day, crystal clear; no fishing at the spring.", ["surge", "clear", "bright", "spring", "waters"])
_f("Upper Mesa Falls", "waterfall", 44.187, -111.33, 5600, "ID", "cityofrocks", "NF (fee day use)", "Mesa Falls Scenic Byway", "yes", ["fee", "buildings"], ["Lower Mesa Falls (a pair)"], "Two falls in a row — a double.", ["waterfall", "double", "pair"])
_f("Thousand Springs", "spring", 42.75, -114.85, 3000, "ID", "cityofrocks", "state park (fee)", "US-30", "yes", ["fee"], [], "Springs bursting from the canyon wall, fed by the sinking Lost Rivers.", ["surge", "spring", "waters"])
_f("Shoshone Falls", "waterfall", 42.594, -114.401, 3300, "ID", "cityofrocks", "city park (fee in season)", "Twin Falls", "yes", ["fee"], [], "'Niagara of the West'.", ["waterfall"])
_f("Craters of the Moon", "rock", 43.42, -113.52, 5900, "ID", "cityofrocks", "NPS (fee)", "US-20", "yes", ["fee", "cave"], [], "Lava field; fee; caves.", ["rock"])
# Black Hills
_f("Needles Eye", "arch", 43.84, -103.49, 6000, "SD", "blackhills", "Custer State Park (fee)", "Needles Hwy", "yes", ["fee"], [], "Granite needle with an eye; fee park.", ["needle", "eye", "granite", "hole"])
_f("Cathedral Spires", "rock", 43.85, -103.50, 6600, "SD", "blackhills", "Custer SP / Black Elk Wilderness", "trail", "trail", ["fee", "trail"], [], "Granite spires.", ["granite", "spire"])
_f("Black Elk Peak", "peak", 43.866, -103.531, 7242, "SD", "blackhills", "Black Hills NF", "trail from Sylvan Lake", "no", ["trail"], ["Harney Peak (renamed 2016)"], "Renamed 2016 — a changed historical name.", ["peak", "renamed"])
_f("Bear Butte", "peak", 44.48, -103.43, 4426, "SD", "blackhills", "state park (fee); sacred", "SD-79", "yes", ["fee", "sacred"], ["Mato Paha (Lakota, 'bear mountain')"], "Sacred Lakota/Cheyenne mountain; fee park.", ["bear", "ursa", "sacred"])
_f("Spearfish Falls", "waterfall", 44.32, -103.86, 5000, "SD", "blackhills", "Black Hills NF (free)", "US-14A, short trail", "yes", [], [], "Falls in Spearfish Canyon.", ["waterfall"])
_f("Bridal Veil Falls (Spearfish)", "waterfall", 44.42, -103.85, 4400, "SD", "blackhills", "Black Hills NF (free)", "US-14A pullout", "yes", [], [], "Named 'bridal' falls beside the highway. Coordinates approximate.", ["bride", "veil", "waterfall"])
# New Mexico
_f("Heron Lake", "lake", 36.70, -106.70, 7200, "NM", "gates", "state park (fee)", "US-64", "yes", ["fee", "reservoir"], [], "The book's 'north star' lake; a reservoir (dam not on an old map).", ["north star", "lake", "pole"])
_f("Ojo Caliente", "hotspring", 36.30, -106.05, 6300, "NM", "gates", "private resort", "US-285", "yes", ["private", "buildings"], [], "Posey searched here for Fenn.", ["hot", "surge", "fenn"])
_f("Tres Piedras", "rock", 36.65, -105.97, 8000, "NM", "gates", "Carson NF (free)", "US-64/285", "yes", [], ["'three stones' (Spanish)"], "Granitic gneiss crags; 'three' by name.", ["three", "granite", "rock"])
_f("Blue Hole (Santa Rosa)", "hole", 34.94, -104.67, 4600, "NM", "gates", "city park (fee dive permits)", "I-40", "yes", ["fee", "south-of-cutoff"], [], "Artesian sinkhole; south of the Santa Fe cutoff.", ["hole", "clear", "bright", "surge"])
_f("Rio Grande Gorge", "gate", 36.48, -105.73, 6500, "NM", "gates", "BLM (free)", "US-64 bridge", "yes", [], [], "Basalt gorge; silent water far below.", ["silent", "waters", "gorge"])
# Beartooth / Absaroka
_f("Beartooth Butte", "peak", 44.95, -109.60, 10514, "WY", "windriver", "Shoshone NF", "Beartooth Hwy (late May–mid Oct)", "yes (summer)", ["high"], [], "A literal Beartooth for ursa; well above a mile high.", ["bear", "ursa", "tooth"])
_f("Beartooth Pass", "pass", 44.97, -109.47, 10947, "WY", "windriver", "NF", "US-212, seasonal", "yes (summer)", ["high"], [], "Highest pass on the Beartooth Highway.", ["bear", "pass"])
_f("Pompeys Pillar", "rock", 46.00, -108.00, 2900, "MT", "gates", "BLM NM (fee)", "I-94", "yes", ["fee", "man-made"], [], "Clark's 1806 carved signature; sandstone; fee.", ["names", "past", "secrets"])


# La Sals / Castle Valley additions (session notes Sep 6 2026)
_f("Castleton Tower (Castle Rock)", "rock", 38.652, -109.372, 6656, "UT", "lasals", "BLM (free)", "Castle Valley Rd, 1.4 mi trail", "yes", ["climbing"], ["Castle Rock (official)"], "Wingate sandstone tower at the mouth of Castle Valley; the 'castle' of the realm reading.", ["castle", "realm", "rock"])
_f("Sister Superior (Rectory ridge)", "rock", 38.657, -109.376, 6800, "UT", "lasals", "BLM (free)", "Castle Valley Rd; technical climb", "yes (base)", ["climbing"], ["The Rectory", "Priest and Nuns", "The Convent (same ridge)"], "A nun is a 'bride of Christ' — the Sep 6 2026 bride reading. Posey: you need not be at the bride. Coordinates approximate.", ["bride", "sister", "three", "face"])
_f("Parriott Mesa", "rock", 38.66, -109.40, 6600, "UT", "lasals", "BLM", "SR-128", "yes", [], [], "West flank of the Castle Valley mouth — the other 'gate post' in the valley-mouth reading.", ["gate", "gates"])
_f("Castle Mountain (La Sal)", "peak", 38.61, -109.26, 12044, "UT", "lasals", "Manti-La Sal NF", "trail", "no", ["high"], [], "A realm is what a castle governs — better 'realm' candidate than Waas. Coordinates approximate.", ["castle", "realm"])
_f("Manns Peak", "peak", 38.55, -109.24, 12272, "UT", "lasals", "Manti-La Sal NF", "trail from Geyser Pass", "no", ["high"], [], "Beside Mount Waas; if Waas means 'man', two adjacent peaks say the same thing in two languages.", ["man", "he"])
_f("Mount Tomasaki", "peak", 38.56, -109.25, 12239, "UT", "lasals", "Manti-La Sal NF", "trail", "no", ["high"], ["Ute name — meaning not established"], "Adjacent to Manns and Waas. Open lookup: meaning and gender of the name.", ["ute"])
_f("Mount Laurel (La Sal)", "peak", 38.49, -109.25, 12271, "UT", "lasals", "Manti-La Sal NF", "trail", "no", ["high"], [], "Woman's name; laurel = wedding garland; one foot lower than Manns Peak — an elevation coincidence, not a clue.", ["bride", "laurel", "her"])
_f("Haystack Mountain (La Sal)", "peak", 38.60, -109.27, 11642, "UT", "lasals", "Manti-La Sal NF", "trail", "no", ["high"], [], "Shape name that multiplies across the West; the Moab Times casts it as a hen with chicks. Rival to the Montana 'land of 10,000 haystacks'.", ["haystack", "her"])
_f("Mount Mellenthin", "peak", 38.47, -109.23, 12645, "UT", "lasals", "Manti-La Sal NF", "trail", "no", ["high", "memorial"], [], "Named for a ranger killed there in 1918 — a non-living man, but a memorial angle.", ["he", "memorial"])
# Beartooths / Great Bannock Trail (session notes Sep 6 2026)
_f("Granite Peak", "peak", 45.163, -109.807, 12807, "MT", "windriver", "Custer-Gallatin NF", "multi-day climb", "no", ["high", "climbing", "far"], [], "Montana's high point; Beartooth rock dated ~3.96 billion years — the oldest in the West.", ["granite", "bear", "time", "past"])
_f("Great Bannock Trail (Cooke City)", "historic", 45.02, -109.93, 7600, "MT", "windriver", "NF / YNP boundary", "US-212", "yes", [], [], "Shoshone-Bannock buffalo route across Yellowstone's NE corner — an 'ancient gate' as a passage.", ["gates", "ancient", "pass", "trail"])

# ---------------------------------------------------------------- name-pattern index
# idea -> words that count as a match in a name or alias (lowercase substrings)
NAME_PATTERNS = {
    "bear": ["bear", "ursa", "mato", "bruin", "grizzly"],
    "north star / polaris": ["polaris", "north star", "northstar", "lodestar"],
    "wisdom": ["wisdom", "wise", "sage", "sophia"],
    "hole": ["hole", "sink", "eye", "window", "pothole"],
    "bride / wedding": ["bride", "bridal", "wedding", "matrimony", "marriage", "veil", "honeymoon", "sweetheart"],
    "gold": ["gold", "oro", "golden"],
    "needle": ["needle", "aguja", "spire"],
    "crown": ["crown", "corona", "king", "queen", "royal"],
    "three": ["three", "tres", "trois", "triple", "trinity", "tri-", "trident"],
    "twenty": ["twenty", "20 mile", "twentymile", "veinte"],
    "silence": ["silent", "silence", "quiet", "still", "hush"],
    "shadow": ["shadow", "sombra", "shade", "dark"],
    "light": ["light", "lumin", "luz", "bright", "sun", "lightning"],
    "two / pair": ["twin", "double", "sisters", "brothers", "pair", "two ", "dos ", "gemini"],
    "time": ["time", "clock", "hour", "century", "eternal", "ancient", "old"],
    "face": ["face", "sleeping", "profile", "head", "sphinx", "indian", "giant", "chief", "maiden"],
}

# ---------------------------------------------------------------- historical & cultural layer
HISTORY = [
    {"name": "Lewis and Clark 1805–06", "kind": "trail", "regions": ["bighole", "grasshopper", "gates"], "text": "Up the Jefferson and Beaverhead (Wisdom, Philosophy and Philanthropy rivers named 6 Aug 1805), Beaverhead Rock (8 Aug), Camp Fortunate (17 Aug), Lemhi Pass (12 Aug); Gates of the Mountains (19 Jul 1805); Three Forks (27 Jul 1805). Return 1806 via the Big Hole and Jackson Hot Springs.", "source": "Journals of the Lewis and Clark Expedition (Moulton ed.)"},
    {"name": "Nez Perce flight 1877", "kind": "trail", "regions": ["bighole"], "text": "Lolo Pass → Bitterroot → Big Hole battle (9 Aug) → Bannack country → Yellowstone. Battle sites are excluded by the rules.", "source": "NPS Nez Perce NHT"},
    {"name": "Oregon / California / Mormon / Pony Express trails", "kind": "trail", "regions": ["sweetwater", "windriver"], "text": "Independence Rock, Devil's Gate, Martin's Cove, Split Rock, Ice Slough, Rocky Ridge, South Pass; Lander Cutoff north through the Wind River foothills.", "source": "NPS National Historic Trails"},
    {"name": "California Trail — Raft River / City of Rocks", "kind": "trail", "regions": ["cityofrocks"], "text": "Twin Sisters and Register Rock; Salt Lake Alternate rejoins near Almo.", "source": "NPS California NHT"},
    {"name": "Old Spanish Trail", "kind": "trail", "regions": ["lasals"], "text": "Crossed the Colorado at Moab; north fork through Castle Valley.", "source": "NPS Old Spanish NHT"},
    {"name": "Astorians 1811 / Union Pass / Teton Pass", "kind": "trail", "regions": ["windriver", "jacksonhole"], "text": "Wilson Price Hunt's party crossed Union Pass and Teton Pass westbound.", "source": "Irving, Astoria"},
    {"name": "Bannack–Virginia City road; Corinne freight road", "kind": "trail", "regions": ["grasshopper", "bighole"], "text": "Stage and freight routes of the 1860s gold camps; stage stops along the Beaverhead.", "source": "Montana Historical Society"},
    {"name": "Mining camps", "kind": "settlement", "regions": ["grasshopper", "pioneers", "sweetwater", "blackhills"], "text": "Bannack (1862), Polaris and Elkhorn/Coolidge (1880s–1920s), South Pass City and Atlantic City (1867), Deadwood (1876).", "source": "state historical societies"},
    {"name": "Sacagawea", "kind": "person", "regions": ["bighole", "windriver"], "text": "Taken at Three Forks; recognised Beaverhead Rock; reunited with Cameahwait near Camp Fortunate/Lemhi; reputed grave at Fort Washakie (disputed — another tradition places her death at Fort Manuel, SD, 1812).", "source": "Moulton; Wind River Reservation tradition"},
    {"name": "Great Bannock Trail", "kind": "trail", "regions": ["windriver", "gates"], "text": "Shoshone-Bannock route to the buffalo grounds across the NE corner of Yellowstone by Cooke City and the Beartooth front.", "source": "NPS / Haines"},
    {"name": "Local legends", "kind": "legend", "regions": ["lasals", "bearlake", "cityofrocks"], "text": "Matrimony Spring (drink and you'll marry / return); Bear Lake Monster (1868 Deseret News); Almo massacre (disputed 1861 story, marker erected 1938).", "source": "local newspapers; verify each"},
]

# ---------------------------------------------------------------- access & season
SEASON = [
    {"match": ["Beartooth"], "text": "Beartooth Highway opens late May and closes mid-October; snow can close it any month."},
    {"match": ["Pioneer", "Polaris", "Elkhorn", "Crystal Park", "Coolidge"], "text": "Pioneer Mountains Scenic Byway: the upper (Elkhorn–Wise River) section is closed in winter, opening around mid May; passenger car fine when open."},
    {"match": ["La Sal", "Medicine Lakes", "Gold Basin", "Warner", "Oowah", "Tukuhnikivatz"], "text": "La Sal Loop is paved; Geyser Pass and La Sal Pass roads are gravel with snow until June; the last spurs to Medicine Lakes and Gold Basin are high-clearance."},
    {"match": ["Sinks", "Rise", "Popo Agie"], "text": "Sinks Canyon Road (WY-131) is open to the park year-round; the Loop Road above (Louis Lake) opens ~June. Runoff peaks late May–June and the Rise runs high and murky then."},
    {"match": ["Lemhi"], "text": "Lemhi Pass road: gravel, closed by snow roughly November–June; passenger car OK when dry, muddy after rain."},
    {"match": ["Union Pass"], "text": "Union Pass road: gravel, closed in winter, open ~June–October."},
    {"match": ["Granite Hot Springs", "Granite Creek"], "text": "Granite Creek Road: 10 miles of gravel, closed to cars in winter (snowmobile/dogsled), open ~late May."},
    {"match": ["Medicine Wheel"], "text": "US-14A over the Bighorns closes in winter; the Medicine Wheel road opens around June with a 1.5-mile walk."},
    {"match": ["South Pass", "Sweetwater", "Split Rock", "Devil's Gate", "Independence Rock"], "text": "Highways open all year; two-tracks to the Sweetwater Rocks are dry-weather only."},
    {"match": ["Thermopolis", "Wind River Canyon", "Wedding"], "text": "US-20 through the canyon is open all year; Hot Springs State Park hours 6 am–10 pm."},
    {"match": ["Hidden Lake", "Storm Lake"], "text": "Storm Lake road is rough (high clearance); trails snowbound until July."},
    {"match": ["Gates of the Mountains", "Sleeping Giant", "Holter"], "text": "Boat tours run Memorial Day to mid-September; Sleeping Giant road is gravel, open most of the year."},
    {"match": ["Big Hole", "Wisdom", "Jackson"], "text": "US-43 and MT-278 are open all year; Big Hole Pass and Chief Joseph Pass are plowed. The valley floods in June runoff."},
]

# ---------------------------------------------------------------- rules (hard) and statements (soft)
HARD_RULES = [
    ("r_underwater", "Not underwater", "flag:underwater"),
    ("r_private", "Not on private property", "flag:private"),
    ("r_cave", "Not in a cave, mine or tunnel", "flag:cave,tunnel,mine"),
    ("r_rappel", "Not reachable only by rappelling; no ropes, ladders, climbing or swimming", "flag:climbing,ladder,rappel,swim"),
    ("r_buildings", "Not associated with man-made buildings", "flag:buildings"),
    ("r_graves", "Not near graves or grave markers", "flag:graves,battle"),
    ("r_danger", "Not in a dangerous place", "flag:danger"),
    ("r_home", "More than a mile from where Posey, family or friends live, work or own property", "flag:posey-property"),
    ("r_public", "On publicly accessible land", "flag:private,restricted,closed"),
    ("r_safe", "Safe to reach; no high-clearance vehicle needed", "flag:high-clearance"),
]
SOFT_RULES = [
    ("s_order", "Clues are in consecutive order", "check:order"),
    ("s_noredherring", "No red herrings", "check:none"),
    ("s_tenclues", "At least 10 clues", "check:count"),
    ("s_botg", "Boots on the ground becomes required at stanza four; stanzas 1–3 solvable from home", "check:field"),
    ("s_walk", "Walking distance between the S2L2 clue and the S2L3 clue", "check:walk:S2L2:S2L3:3"),
    ("s_mile", "No more than a mile of hiking to determine the treasure location", "check:hike"),
    ("s_states", "Colorado and Oregon are eliminated", "check:states:CO,OR"),
    ("s_cipher", "One cipher and one technical hint exist, neither critical", "check:none"),
    ("s_distance", "A distance element exists", "check:distance"),
    ("s_manmade", "One clue has a man-made implication, and only one", "check:manmade"),
    ("s_free", "Access is free and available 24/7", "check:flag:fee,hours"),
    ("s_dog", "You can bring your dog", "check:flag:no-dogs"),
    ("s_trail", "The site is a little ways off any man-made trail", "check:flag:trail"),
    ("s_fenn", "Within about 75 miles of somewhere Posey searched for Fenn (soft, walked back)", "check:fenn:75"),
    ("s_map", "Inside the printed map; the American West", "check:map"),
]
FENN_SITES = [("Madison Jct / Nine Mile Hole", 44.64, -110.86), ("Hebgen Lake", 44.87, -111.33), ("Gardiner / Boiling River", 45.03, -110.70), ("Grand Teton", 43.74, -110.80), ("Sinks Canyon", 42.74, -108.83), ("Glacier NP", 48.70, -113.80), ("Ojo Caliente", 36.30, -106.05)]
FENN_MAP_BBOX = [31.33, -116.05, 49.0, -102.05]

# ---------------------------------------------------------------- personal-to-Posey hooks (prompts, not facts)
PERSONAL = [
    "Tucker the dog — any 'Tucker', dog, or hound-named feature; dog-friendly access is a stated rule.",
    "Grandfather in Montana (fish-and-game warden per community accounts) — Dillon / Beaverhead country in the book.",
    "Arizona childhood — 'Wonder' and desert imagery; Arizona is a fringe state on the map.",
    "The Fenn search — Madison, Hebgen, Gardiner, Grand Teton, Sinks Canyon, Glacier, Ojo Caliente are documented Posey search areas.",
    "Four dedicatees (late loved ones) — a memorial reading of 'his bride' or 'sacred space'.",
    "Horses and ranch life — corrals, stage stops, horse-named features.",
    "Disney Imagineering background — 'wonder', staged reveals, a checkpoint.",
]

# ---------------------------------------------------------------- community reference solves (read-only)
REFERENCE_SOLVES = [
    {"name": "Wisdom / Big Hole (Montana)", "source": "community consensus, 2025–26", "lines": {
        "S1L3": {"text": "Wisdom, MT / the Wisdom River", "category": "literal", "lat": 45.6166, "lon": -113.4536, "conf": 3},
        "S2L2": {"text": "Walk the Big Hole River", "category": "literal", "lat": 45.62, "lon": -113.45, "conf": 2},
        "S2L3": {"text": "The Big Hole is the Hole", "category": "literal", "lat": 45.62, "lon": -113.45, "conf": 3},
        "S2L4": {"text": "Fish the Big Hole", "category": "direction", "conf": 2},
        "S3L1": {"text": "Polaris, MT", "category": "naming", "lat": 45.366, "lon": -113.122, "conf": 2},
        "S3L2": {"text": "Beaverhead Rock", "category": "literal", "lat": 45.4267, "lon": -112.4563, "conf": 2},
        "S4L1": {"text": "Pioneer batholith granite", "category": "feature_class", "conf": 1}}},
    {"name": "Polaris (Montana)", "source": "community, Pioneer byway variant", "lines": {
        "S2L1": {"text": "Elkhorn Hot Springs", "category": "literal", "lat": 45.4483, "lon": -113.1236, "conf": 2},
        "S2L3": {"text": "Big Hole River", "category": "literal", "lat": 45.79, "lon": -112.95, "conf": 2},
        "S3L1": {"text": "Polaris — north star, Ursa Minor", "category": "wordplay", "lat": 45.366, "lon": -113.122, "conf": 3},
        "S4L1": {"text": "Crystal Park granite", "category": "literal", "lat": 45.487, "lon": -113.113, "conf": 2}}},
    {"name": "Sweetwater / South Pass (Wyoming)", "source": "TreasureNet walkthrough, Apr 2026", "lines": {
        "S2L4": {"text": "Sweetwater River", "category": "literal", "lat": 42.47, "lon": -107.5, "conf": 1},
        "S3L2": {"text": "Devil's Gate", "category": "literal", "lat": 42.4467, "lon": -107.2131, "conf": 3},
        "S3L4": {"text": "South Pass — turn west", "category": "direction", "lat": 42.35, "lon": -108.88, "conf": 1},
        "S4L1": {"text": "Split Rock", "category": "literal", "lat": 42.4762, "lon": -107.5661, "conf": 2},
        "S4L2": {"text": "Independence Rock names", "category": "literal", "lat": 42.4936, "lon": -107.1319, "conf": 2}}},
    {"name": "Alaska (north star reading)", "source": "Mike Unfiltered substack", "lines": {
        "S3L1": {"text": "Ursa Major on the Alaska flag; the north star", "category": "wordplay", "conf": 1},
        "S3L3": {"text": "20° as a bearing from the flag stars", "category": "numeric", "conf": 1}}},
]

# ---------------------------------------------------------------- line keyword → feature types and instruction hints
LINE_HINTS = {
    "surge": ["hotspring", "spring", "waterfall", "pool"], "hope": ["spring"], "clear": ["spring", "pool", "lake"], "bright": ["spring", "pool"],
    "water": ["river", "spring", "lake", "waterfall", "confluence"], "waters": ["river", "confluence", "spring", "lake"], "silent": ["hole", "river"], "flight": ["waterfall", "river", "bend"],
    "bend": ["bend", "river", "confluence"], "hole": ["hole", "arch", "cave"], "pole": ["pool", "river", "lake", "peak"], "cast": ["river", "lake", "pool"],
    "ursa": ["peak", "rock", "gate", "face"], "east": [], "realm": ["peak", "pass", "gate"], "bride": ["waterfall", "spring", "rock", "confluence", "monument"], "gates": ["gate", "pass", "rock"], "ancient": ["gate", "rock", "monument"],
    "foot": ["peak", "pass"], "three": ["confluence", "pair", "peak", "pass"], "twenty": [], "degree": [], "face": ["face", "peak", "rock"], "return": ["pass", "bend"],
    "arcs": ["arch", "pair", "cirque", "rock"], "double": ["arch", "pair"], "granite": ["rock", "arch", "cirque", "peak"], "bold": ["rock", "peak"], "secrets": ["historic", "rock", "monument"], "past": ["historic", "monument"],
    "time": ["historic", "rock"], "race": ["river"], "wonder": ["arch", "waterfall", "cirque"], "sacred": ["monument", "peak"], "space": ["cirque", "pass"],
    "river": ["river", "confluence"], "flow": ["river", "spring"], "wisdom": ["town", "river"], "shadow": ["peak", "cirque", "face"], "sight": ["face", "peak"], "rhyme": [],
}
