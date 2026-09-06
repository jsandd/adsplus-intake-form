# Your research database — what is actually in it

Inspected 6 September 2026 by reading every record in the Field HQ shared store
(the database behind https://claude.ai/code/artifact/1487d6f0-4342-4d62-b67b-c46c2a88d5ed).
Nothing below is assumed; every count comes from the records themselves.

## Tables

| Table | Records | What it holds |
|---|---|---|
| `poem` | 1 document, 20 lines | The poem text plus your per-line working notes, status and type |
| `intel` | 223 | Every fact, quote, claim, objection and theory, each linked to poem lines |
| `candidates` | 36 | Solves and candidate sites, 12 of them with a line-by-line chain |
| `readings` | 0 | Empty — the readings feature was never used |
| `map` | 1 document | Status and note for each Western state |

All 223 intel records and all 36 candidates were created on **2026-09-05** (the day the board was seeded). Dates *inside* records (the `when` field) run from **2025-03 to 2026-09**; 157 of 223 records carry one.

## `intel` in plain language

223 pieces of research. Fields present on every record: `id, text, kind, conf, source, tags, links, created`. `when` (a date) is on 157.

**By kind** (what sort of thing it is):

| kind | count | meaning |
|---|---|---|
| statement | 85 | things Posey said (rules, Q&A answers, interviews, X posts) |
| speculation | 49 | your own theories and the working La Sals solve |
| community | 39 | claims from searchers, forums, analysis sites |
| objection | 21 | constraints that argue against a reading |
| book | 17 | facts about the book, its pages, editions, audiobook |
| map | 8 | verified geography (all marked VERIFIED by web search, Sep 5 2026) |
| question | 4 | questions to ask Posey |
| field | 0 | no first-hand field reports yet |
| math | 0 | no cipher work recorded here |

**By confidence:** confirmed 41 · likely 85 · unverified 95 · disputed 2.
Of the 85 Posey statements, 28 are confirmed and 57 likely. 10 statements contain decline/punt language ("declined", "wouldn't say", "ambiguous").

**Links to the poem:** 216 of 223 records are matched to at least one line; 547 links in total, 109 of them marked *contradicts*. Seven records are unmatched.

**Sources (top):** My own analysis 27 · Seekers Summit, Tucson 23 · Posey Q&A compiled by Mysterious Writings 22 · Cross-reference 20 · Working solve 13 · Mysterious Writings 11 · Verified by web search 11 · treasurehuntamusementpark.com 15 · Master file §12/§13 10 · Community roundup 6 · Public-statements research report 6 · Reddit 5 · Treasure Among Us 5 · MW Substack 5 · treasure.quest rules/FAQ 5.

**Tags:** 365 distinct. Most used: map, bride, numbers, checkpoint, hole, 42, montana, verified, distance, moab, granite, access, netflix, fenn, la-sals, wyoming.

**Content probes:** 22 records mention Netflix / the documentary; 10 mention page numbers; 5 mention songs or lyrics; 20 mention Tucker, dogs, horses, family or the grandfather; 14 mention indigenous names or peoples; 3 contain coordinates.

Text length: 52 to 1,134 characters, average 350.

## `candidates` in plain language

36 records. Fields on every record: `id, name, region, coords, elev, notes, kill, test, verdicts, gates, created`; `chain` on 12.

- Every candidate has an approximate coordinate and an elevation (all marked "verify").
- **By state:** MT 14 · WY 9 · UT 5 · ID 3 · NM 3 · MT/WY 1 · MT/ID 1.
- **Gate judgments:** 344 cells filled across Posey's 20 hard statements; 23 are fails (these are what rule a site out).
- **Poem verdicts:** 138 fit/fail judgments.
- **Chains:** 12 solves carry a per-line route (68 slots, 63 with coordinates): Sinks Canyon, Thermopolis, Jackson Hole, Big Hole cluster, Pioneers, Twin Bridges, Sweetwater, Gates of the Mountains, Hidden Lake, Hole-in-the-Wall, City of Rocks, Bear Trap.
- 27 have a "cheapest test"; all 36 have a "what would kill it".

## `poem`

Title "Beyond the Map's Edge", 20 lines in 5 stanzas. Each line carries your working note (all 20 have one), a status (thematic 6, partial 5, unsolved 4, pinned 3, contested 2) and a type (mystery 4, geographic 4, instruction 3, navigate 3, checkpoint 2, literary 2, celestial 1, precision 1). No line is marked hard.

## `map`

Per-state status: MT hot · WY hot · UT active (your solve) · ID in play · NM in play · AK fringe · AZ fringe · CO eliminated · OR eliminated · CA, NV, WA open. Nine states carry a note.

## Proposed mapping (edit `mapping.json` to change it)

| Source | → Feeds | Why |
|---|---|---|
| `poem` | The poem the tool works from (only if you have not pasted one) | Same 20 lines; ids l01–l20 become S1L1–S5L4 |
| `intel` kind **statement** (85) | **Posey statement archive** | confirmed → tier *confirmed*; likely → *reported* (most were compiled by MW/THAP, not quoted from a dated primary); unverified → *circulating*; disputed → *unverified*. Records with decline language are flagged *declined/ambiguous* |
| `intel` kind **book** (17) | **Book & media index** | tiers as above |
| `intel` kinds **community, speculation, objection, question, map, field, math** (121) | **Rumour & field report layer** | community → circulating; speculation/objection/question → fan analysis; map (verified) → reported. Each keeps its line links so it surfaces on the right line |
| `candidates` with coordinates (36) | **Landmark inventory** as type *site*, tier fan analysis | Failed gate cells become rule flags (private, fee, buildings, high-clearance, cave) |
| `candidates` with a chain (12) | **Community theory library** as read-only reference solves | So your new solves can be compared line by line against your old ones |
| `map` eliminated states (CO, OR) | **Rules engine** eliminated-states rule | Other statuses and notes kept as settings |
| `readings` (0) | nothing | empty |

## Things that do not fit cleanly — your call

1. **`speculation` (49) is your own analysis, not community rumour.** It lands in the rumour layer at tier *fan analysis* so it never reads as evidence. If you would rather have a separate "my theories" layer, say so.
2. **`objection` (21) are constraints, not claims.** They go to rumours with their *contradicts* links intact so they show as "against" on the line. Some could become soft rules in the rules engine instead — tell me which.
3. **`question` (4)** are things to ask Posey. They have no natural home; they sit in rumours tagged `question`. An "open questions" list would be a better fit if you want one.
4. **`map` (8) VERIFIED records** are the most reliable geography you have, but they are prose, not features. They go to rumours at tier *reported*; the places they describe are already in the built-in inventory.
5. **`created` is the same day for everything**, so it cannot be used for a timeline; the `when` field can, and is.
6. **Two records typed `statement` are not Posey's words** (one "Cross-reference (Claude…)", one "Verified by web search (Claude…)"). They still go to the archive at tier *reported*; change their kind in Field HQ if you want them out.
7. **Per-line notes on the poem** are kept with the poem but the solve builder has its own per-line notes field; the old notes are shown, not merged.
