"""The parts that need a language model: fresh interpretations, devil's advocate,
'what would have to be true', interviews, reverse-mode narrative, ranking the
automatic search, explaining disagreements.

Uses the official Anthropic Python SDK. If it is not installed or no credential
is available, every function returns {"unavailable": reason} and the rest of the
tool keeps working. Model: claude-opus-5 with adaptive thinking (its default) and
server-side refusal fallbacks switched on.
"""
import json
import os

from . import engine, knowledge, store

MODEL = os.environ.get("SOLVEBUILDER_MODEL", "claude-opus-5")
_client = None
_reason = None


def client():
    global _client, _reason
    if _client is not None:
        return _client
    try:
        import anthropic  # noqa
    except Exception as e:  # pragma: no cover
        _reason = "The 'anthropic' package is not installed. run.py installs it automatically when it has internet; you can also run: pip install anthropic"
        return None
    try:
        import anthropic
        _client = anthropic.Anthropic()
        return _client
    except Exception as e:
        _reason = f"Could not create a Claude client: {e}. Set ANTHROPIC_API_KEY or run `ant auth login`."
        return None


def available():
    c = client()
    return {"ok": c is not None, "reason": _reason, "model": MODEL}


def _ask(prompt, schema=None, max_tokens=6000, effort="high"):
    c = client()
    if c is None:
        return {"unavailable": _reason}
    kwargs = dict(model=MODEL, max_tokens=max_tokens, messages=[{"role": "user", "content": prompt}], output_config={"effort": effort})
    if schema:
        kwargs["output_config"]["format"] = {"type": "json_schema", "schema": schema}
    try:
        try:
            resp = c.beta.messages.create(betas=["server-side-fallback-2026-07-01"], fallbacks="default", **kwargs)
        except TypeError:
            resp = c.messages.create(**kwargs)
    except Exception as e:
        # second attempt without structured output in case the account/model rejects it
        try:
            kwargs["output_config"].pop("format", None)
            resp = c.messages.create(**kwargs)
        except Exception as e2:
            return {"error": f"{type(e2).__name__}: {e2}"}
    if getattr(resp, "stop_reason", None) == "refusal":
        return {"error": "The model declined this request (safety classifier)."}
    text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
    if schema:
        try:
            return json.loads(text)
        except Exception:
            m = text[text.find("{"): text.rfind("}") + 1]
            try:
                return json.loads(m)
            except Exception:
                return {"error": "The model did not return valid JSON", "text": text}
    return {"text": text}


# ---------------------------------------------------------------- context builders

def poem_block():
    return "\n".join(f"{l['ref']}: {l['text']}" for l in engine.poem_lines())


def statements_block(limit=40):
    ss = sorted(engine.statements_for(), key=lambda s: ({"confirmed": 0, "reported": 1, "circulating": 2, "fan": 3, "unverified": 4}.get(s["tier"], 5), s.get("date") or ""))
    return "\n".join(f"- [{s['tier']}{', ' + s['date'] if s.get('date') else ''}] {s['text'][:260]}" for s in ss[:limit])


def rules_block():
    return "\n".join(f"- ({r['kind']}) {r['text']}" for r in engine.rules() if r["enabled"])


def solve_block(solve):
    st = engine.constraint_state(solve)
    lines = []
    for l in engine.poem_lines():
        c = solve["state"].get("lines", {}).get(l["ref"])
        if c:
            lines.append(f"{l['ref']} \"{l['text']}\" → [{c.get('category')}, conf {c.get('conf')}, tier {c.get('tier')}] {c.get('text')}" + (f" @ {c['lat']:.4f},{c['lon']:.4f}" if c.get("lat") is not None else "") + (f" — note: {c['note']}" if c.get("note") else ""))
        else:
            lines.append(f"{l['ref']} \"{l['text']}\" → (uncommitted)")
    seed = engine.seed_info(solve)
    cons = engine.contradictions(solve)
    return (f"SOLVE: {solve['name']}\nSeed: {seed['label'] or 'none'}\nStates in play: {', '.join(st['states']) or 'any'}; eliminated: {', '.join(st['eliminated'])}\nRoute so far: {st['distance']} mi over {len(st['legs'])} legs\n" + "\n".join(lines) + "\nDetected conflicts:\n" + ("\n".join("- " + c["text"] for c in cons) or "- none"))


def frame():
    return ("You are the reasoning partner inside a solve-building tool for Justin Posey's poem-led treasure hunt 'Beyond the Map's Edge' (American West, book published 2025). "
            "Be concrete, sceptical and geographic. Prefer named features, bearings, distances and testable claims. Never invent a Posey quotation; when you are unsure whether he said something, say so. "
            "Distinguish what is confirmed from what is circulating. If a place name might not exist in federal records, flag it.\n\nTHE POEM:\n" + poem_block() + "\n\nRULES AND STATEMENTS IN FORCE:\n" + rules_block() + "\n\nPOSEY STATEMENTS ON THE BOARD (highest reliability first):\n" + statements_block())


# ---------------------------------------------------------------- features

CAT_LIST = ", ".join(k for k, _ in engine.CATEGORIES)


def generate(solve, ref, n=15, instruction=""):
    line = engine._line(ref)
    st = engine.constraint_state(solve, ref)
    schema = {"type": "object", "properties": {"readings": {"type": "array", "items": {"type": "object", "properties": {"text": {"type": "string"}, "category": {"type": "string"}, "rationale": {"type": "string"}, "place": {"type": "string"}, "lat": {"type": ["number", "null"]}, "lon": {"type": ["number", "null"]}, "conf": {"type": "integer"}, "exists_in_gnis": {"type": "string"}}, "required": ["text", "category", "rationale", "place", "lat", "lon", "conf", "exists_in_gnis"], "additionalProperties": False}}}, "required": ["readings"], "additionalProperties": False}
    prompt = (frame() + "\n\n" + solve_block(solve) + f"\n\nACTIVE CONSTRAINTS FOR {ref}: states {st['states'] or 'any'}; active point {st['point']} ({st['point_ref']}); next pinned point {st['next_point']} ({st['next_ref']}); bearing {st['bearing']}; elevation {st['elev']}.\n\n"
              f"TASK: Give {n} materially different readings of {ref} \"{line['text']}\" that respect the constraints above. Spread them across these categories: {CAT_LIST}. "
              "For each: the reading, its category, a one-sentence rationale, the specific place it names if any (with approximate lat/lon or null), a sureness 1–3 (3 = the line literally names it), and exists_in_gnis as one of 'yes', 'probably', 'unsure', 'no' — be honest; a name you cannot place should say 'unsure'. "
              + (f"Extra instruction from the user: {instruction}" if instruction else "") + "\nReturn JSON only.")
    res = _ask(prompt, schema, max_tokens=8000)
    if "readings" in res:
        for r in res["readings"]:
            r["tier"] = "unverified"
            r["origin"] = "ai"
            r["source"] = f"generated by {MODEL} — not a source; verify"
            if r.get("category") not in dict(engine.CATEGORIES):
                r["category"] = "literal" if r.get("lat") is not None else "structural"
    return res


def devils_advocate(solve):
    prompt = frame() + "\n\n" + solve_block(solve) + ("\n\nTASK: Argue against this solve as hard as you can. Do not soften it. Cover: (1) the strongest counter-evidence, (2) the Posey statements it conflicts with (quote the statement text from the list above only), (3) the places where the solver reasoned backward from a conclusion instead of forward from the poem, (4) lines where something plausible sits next to the text without producing a location, (5) the single observation in the field that would kill it fastest. Under 400 words, plain prose with short headings.")
    return _ask(prompt, max_tokens=4000)


def what_would_have_to_be_true(solve):
    local = engine.assumptions(solve)
    schema = {"type": "object", "properties": {"assumptions": {"type": "array", "items": {"type": "object", "properties": {"assumption": {"type": "string"}, "load": {"type": "string"}, "cheapest_test": {"type": "string"}, "would_prove_wrong": {"type": "string"}, "cost": {"type": "integer"}}, "required": ["assumption", "load", "cheapest_test", "would_prove_wrong", "cost"], "additionalProperties": False}}}, "required": ["assumptions"], "additionalProperties": False}
    prompt = frame() + "\n\n" + solve_block(solve) + "\n\nThe tool's own list of assumptions (mechanical):\n" + "\n".join(f"- {a['assumption']} (load {a['load']}, cost {a['cost']})" for a in local) + "\n\nTASK: List every assumption this solve depends on, including ones the mechanical list misses (readings of ambiguous words, land status, that a feature is natural, that a name is spelled as the solver thinks). Rank by how load-bearing each is and how cheaply it can be tested (cost 1 = a map or phone call, 2 = an hour of research, 3 = a field visit). For each, name the single observation that would prove it wrong. Return JSON only."
    return _ask(prompt, schema, max_tokens=6000)


def interview(solve):
    bs = engine.blind_spots()
    weak = engine.weakest_links(solve)
    schema = {"type": "object", "properties": {"questions": {"type": "array", "items": {"type": "object", "properties": {"question": {"type": "string"}, "why": {"type": "string"}, "ref": {"type": "string"}}, "required": ["question", "why", "ref"], "additionalProperties": False}}}, "required": ["questions"], "additionalProperties": False}
    prompt = frame() + "\n\n" + solve_block(solve) + "\n\nInterpretation types the solver uses across all their solves: " + json.dumps(bs["counts"]) + "\nWeakest links (load vs confidence): " + json.dumps(weak[:5]) + "\n\nTASK: Interview the solver. Ask five pointed questions that expose what they are avoiding: unassigned lines sitting between pinned ones, low-confidence lines with several lines built on top, interpretation types they never use, a seed doing the work. Each question names the line it is about (ref, or 'all'). Return JSON only."
    return _ask(prompt, schema, max_tokens=3000)


def reverse_narrative(solve, rev):
    prompt = frame() + "\n\n" + solve_block(solve) + "\n\nThe tool worked the poem backward from the endpoint " + json.dumps(rev["endpoint"]) + ":\n" + "\n".join(f"- {o['ref']} would have to mean: {o['would_have_to_mean']} ({'STRETCH' if o['stretch'] else 'fits'}; {o['distance_mi']} mi)" for o in rev["lines"]) + "\n\nTASK: In under 300 words, say what each stanza would have to mean for this endpoint to be right, which readings are a stretch and why, and whether the hunch survives. Be blunt."
    return _ask(prompt, max_tokens=3000)


def rank_auto(solve, results):
    schema = {"type": "object", "properties": {"ranked": {"type": "array", "items": {"type": "object", "properties": {"index": {"type": "integer"}, "verdict": {"type": "string"}, "strongest_line": {"type": "string"}, "weakest_line": {"type": "string"}}, "required": ["index", "verdict", "strongest_line", "weakest_line"], "additionalProperties": False}}}, "required": ["ranked"], "additionalProperties": False}
    body = "\n\n".join(f"[{i}] score {r['score']} · {r['region']}\n" + "\n".join(f"  {ref}: {c['text']}" for ref, c in r["lines"].items()) for i, r in enumerate(results))
    prompt = frame() + "\n\nThe tool's automatic search produced these candidate solves:\n" + body + "\n\nTASK: Re-rank them by how well they satisfy the poem, the rules and Posey's statements — not by the tool's score. For each give a one-line verdict, the strongest and the weakest line. Return JSON only, best first."
    return _ask(prompt, schema, max_tokens=6000)


def explain_disagreement(mine, theirs):
    lines = engine.poem_lines()
    forks = []
    for l in lines:
        a = mine["state"].get("lines", {}).get(l["ref"])
        b = theirs["state"].get("lines", {}).get(l["ref"])
        if a or b:
            forks.append(f"{l['ref']} \"{l['text']}\": MINE = {a.get('text') if a else '—'} | THEIRS = {b.get('text') if b else '—'}")
    prompt = frame() + f"\n\nMY SOLVE: {mine['name']}\nTHEIR SOLVE: {theirs['name']} ({theirs.get('source')})\n" + "\n".join(forks) + "\n\nTASK: Find the exact line where the two solves first fork and explain what each side is betting on there — the assumption, not who is right. Then list any later lines where they converge again. Under 300 words."
    return _ask(prompt, max_tokens=3000)


def react_narrative(solve, reaction):
    prompt = frame() + "\n\n" + solve_block(solve) + "\n\nThe solver just committed " + reaction["ref"] + ". Mechanical analysis:\n" + reaction["summary"] + "\n" + "\n".join(f"- {c['text']}" for c in reaction["changes"]) + "\n\nTASK: In three or four sentences, tell the solver what this choice just did to the rest of the poem — which lines it strengthened, which it made nearly impossible, and any gap or ordering problem it created. Speak plainly."
    return _ask(prompt, max_tokens=1500, effort="medium")


def feasibility_narrative(rows):
    prompt = frame() + "\n\nThe tool's whole-poem feasibility check by region (built-in inventory only, so thin regions cannot be judged):\n" + json.dumps(rows, indent=1)[:12000] + "\n\nTASK: For each region say in one line whether a complete valid solve is possible and, if not, which constraint kills it. Then name the two regions most worth the solver's next hour and why. Under 300 words."
    return _ask(prompt, max_tokens=3000)
