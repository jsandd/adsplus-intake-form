import json, html, re, datetime
S='/tmp/claude-0/-home-user-adsplus-intake-form/46f457d2-c02d-55f7-ba6b-5343a1b8ce9a/scratchpad/pdf/'
D=json.load(open(S+'extract.json'))
e=lambda s: html.escape(str(s if s is not None else ""))
lines=D['lines']; L={l['id']:l for l in lines}; lineNo={l['id']:l['no'] for l in lines}
intel={i['id']:i for i in D['intel']}
cands={r['c']['id']:r for r in D['ranked']}
GATES=D['GATES']; GL={g[0]:g for g in GATES}
KIND=D['KIND_LABEL']; CONF=D['CONF_LABEL']; STAGES=D['STAGES']; T3=D['TOP3']
TIER={"confirmed":"Confirmed","reported":"Reported","circulating":"Circulating","fan":"Fan analysis","unverified":"Unverified"}
today=datetime.date(2026,9,13).strftime("%B %d, %Y")
stmts=[i for i in D['intel'] if i['kind']=='statement']
standing=[r for r in D['ranked'] if not r['s']['ruledOut']]; out_=[r for r in D['ranked'] if r['s']['ruledOut']]
lead=standing[0]
def short(c): return c['name'].split(' — ')[0].split(' (')[0]
def chip(kind,txt): return f'<span class="chip {kind}">{e(txt)}</span>'
def conf(c): return chip('c-'+c, CONF.get(c,c))
def links_of(it): return ' '.join(f'<span class="lk {"con" if k["stance"]=="contradicts" else ""}">{"✕" if k["stance"]=="contradicts" else "→"}{lineNo.get(k["lineId"],"?")}</span>' for k in it.get('links',[]))
def fact_row(it, why=None):
    meta=f'{e(KIND.get(it["kind"],it["kind"]))} · {e(CONF.get(it["conf"],it["conf"]))}' + (f' · {e(it["source"])}' if it.get('source') else '') + (f' · {e(it["when"])}' if it.get('when') else '')
    return f'<div class="fact"><div class="ft"><span class="fid mono">{e(it["id"])}</span>{e(it["text"])}</div>{f"<div class=why>Why: {e(why)}</div>" if why else ""}<div class="fm">{meta} {links_of(it)}</div></div>'

P=[]  # html parts
P.append(f'''<div class="cover">
<div class="eyebrow">Field HQ · printed edition</div>
<h1>Beyond the Map's Edge</h1>
<div class="sub">The complete working file: poem, solves, evidence, gate, statements, map and next moves</div>
<div class="covergrid">
<div><b>{len(D['ranked'])}</b><span>solves on the board</span></div>
<div><b>{len(standing)}</b><span>still standing</span></div>
<div><b>{len(D['intel'])}</b><span>facts</span></div>
<div><b>{len(stmts)}</b><span>Posey statements</span></div>
<div><b>{sum(1 for i in stmts if i['conf']=='confirmed')}</b><span>confirmed in writing</span></div>
<div><b>{len(GATES)}</b><span>gate rules</span></div>
</div>
<div class="coverfoot">Printed {today} from the live Field HQ database.<br>Leading solve: <b>{e(short(lead['c']))}</b> · score {lead['s']['score']}<br><span class="mono">claude.ai/code/artifact/1487d6f0-4342-4d62-b67b-c46c2a88d5ed</span></div>
</div>''')

TOC=[("1","Hunt status at a glance"),("2","The poem, line by line"),("3","Top 3 solves — analyst verdict"),("4","Solve roster — every candidate, ranked"),("5","The gate — twenty rules"),("6","What Posey said"),("7","Evidence by line"),("8","Facts catalogue"),("9","The map — state by state"),("10","Next moves, objections and sources")]
P.append('<div class="page"><h2 class="sec">Contents</h2><ol class="toc">'+''.join(f'<li><span class="n">{n}</span>{e(t)}</li>' for n,t in TOC)+'</ol><div class="legend"><h4>How to read the tiers</h4><p><b>Confirmed</b>: Posey in writing or the official rules. <b>Likely / Reported</b>: Posey through a named secondary source (a transcript, a Q&amp;A compilation). <b>Circulating</b>: community consensus. <b>Fan analysis</b>: a derived argument. <b>Unverified</b>: a single claim, unchecked. Nothing below Reported carries a poem line on its own.</p><h4>How a solve is scored</h4><p>score = chain×2 + poem verdicts×3 − fails×4 + gates passed×1.5 + evidence − hard-line fails×30 − gate fails×40. A solve is <i>ruled out</i> when it fails a gate or a hard line.</p></div></div>')

# 1 status
reads={r['line']:r for r in D['reads']}
placed=sum(1 for r in D['reads'] if r['best']); contested=sum(1 for r in D['reads'] if r['distinct']>1)
P.append(f'<div class="page"><h2 class="sec"><span class="n">1</span>Hunt status at a glance</h2>')
P.append(f'<div class="tiles"><div class="tile gold"><span class="k">Leading solve</span><b>{e(short(lead["c"]))}</b><span class="s">score {lead["s"]["score"]} · {lead["s"]["filled"]}/{len(lines)} lines placed · {lead["s"]["gPass"]} gates passed</span></div><div class="tile"><span class="k">Standing / total</span><b>{len(standing)} / {len(D["ranked"])}</b><span class="s">{len(out_)} ruled out by the gate or a hard line</span></div><div class="tile"><span class="k">Poem placed</span><b>{placed} / {len(lines)}</b><span class="s">{contested} lines contested between solves</span></div><div class="tile"><span class="k">Posey said</span><b>{len(stmts)}</b><span class="s">{sum(1 for i in stmts if i["conf"]=="confirmed")} confirmed in writing · {len(D["intel"])} facts total</span></div></div>')
P.append('<h3>Top 3 verdict</h3><div class="t3mini">'+''.join(f'<div><b>{s["rank"]}</b><div><div class="nm">{e(s["name"])}</div><div class="vd">{e(s["verdict"])}</div></div></div>' for s in T3['solves'])+'</div>')
P.append('<h3>Leaderboard</h3><table class="tbl board"><thead><tr><th>#</th><th>Solve</th><th>Region</th><th>Score</th><th>Chain</th><th>Poem</th><th>Gate</th><th>Evid.</th><th>Placed</th><th>Gates ✓/✕</th><th>Status</th></tr></thead><tbody>')
for i,r in enumerate(D['ranked']):
    c,s=r['c'],r['s']
    P.append(f'<tr class="{"out" if s["ruledOut"] else ""}"><td>{i+1}</td><td><b>{e(short(c))}</b></td><td class="sm">{e(c.get("region",""))}</td><td><b>{s["score"]}</b></td><td>{s["parts"]["chain"]}</td><td>{s["parts"]["fit"]}</td><td>{s["parts"]["gate"] if not s["gFail"] else -40*s["gFail"]}</td><td>{s["parts"]["evid"]}</td><td>{s["filled"]}/{len(lines)}</td><td>{s["gPass"]}/{s["gFail"]}</td><td>{"ruled out" if s["ruledOut"] else "standing"}</td></tr>')
P.append('</tbody></table>')
P.append('<h3>Best read of the poem</h3><p class="hint">The top-confidence placement per line across standing solves. Contested = more than one distinct reading.</p><table class="tbl"><thead><tr><th>Line</th><th>Poem</th><th>Best read</th><th>By</th><th>Agree</th></tr></thead><tbody>')
for l in lines:
    r=reads[l['id']]
    if r['best']: P.append(f'<tr class="{"contested" if r["distinct"]>1 else ""}"><td class="mono">{l["no"]}</td><td class="poem">{e(l["text"])}</td><td><b>{e(r["best"]["place"] or r["best"]["reading"])}</b>{("<div class=sm>"+e(r["best"]["reading"])+"</div>") if r["best"]["place"] and r["best"]["reading"] else ""}</td><td class="sm">{e(short(cands[r["best"]["c"]]["c"]))}</td><td class="sm">{r["agree"]} place · {r["distinct"]} read{"s" if r["distinct"]!=1 else ""}</td></tr>')
    else: P.append(f'<tr><td class="mono">{l["no"]}</td><td class="poem">{e(l["text"])}</td><td class="sm" colspan="3">no standing solve places this line</td></tr>')
P.append('</tbody></table></div>')

# 2 poem
P.append(f'<div class="page"><h2 class="sec"><span class="n">2</span>The poem, line by line</h2><div class="poemblock"><div class="ptitle">{e(D["title"])}</div>'+''.join(f'<p>{"<br>".join(e(x) for x in st.splitlines())}</p>' for st in D['raw'].split('\n\n'))+'</div>')
stz=0
for l in lines:
    if l['stanza']!=stz:
        stz=l['stanza']; st=STAGES.get(str(stz),["",""]); P.append(f'<h3 class="stz">Stanza {stz} · {e(st[0])} <span class="mode">{e(st[1])}</span></h3>')
    h=l['heat']; r=reads[l['id']]
    P.append(f'<div class="lineblk"><div class="lh"><span class="mono">{l["no"]}</span><span class="poem">{e(l["text"])}</span>{chip("st-"+l.get("status","unsolved"),l.get("status","unsolved"))}{chip("kd",l.get("kind","")) if l.get("kind") else ""}{chip("hard","hard line") if l.get("hard") else ""}<span class="heat">{h["facts"]} facts · {h["against"]} against · {h["placed"]} solves place it</span></div>'+(f'<div class="note">{e(l.get("note",""))}</div>' if l.get('note') else '')+(f'<div class="best">Best read: <b>{e(r["best"]["place"] or r["best"]["reading"])}</b> ({e(short(cands[r["best"]["c"]]["c"]))})</div>' if r['best'] else '')+'</div>')
P.append('</div>')

# 3 top3
P.append(f'<div class="page"><h2 class="sec"><span class="n">3</span>Top 3 solves — analyst verdict</h2><p class="hint">{e(T3["date"])}. Every claim carries its reliability tier.</p><div class="two"><div><h4>How they were ranked</h4><ul>'+''.join(f'<li>{e(x)}</li>' for x in T3['method']['how'])+'</ul></div><div><h4>What all three share</h4><ul>'+''.join(f'<li>{e(x)}</li>' for x in T3['method']['shared'])+'</ul></div></div>')
for s in T3['solves']:
    r=cands.get(s['candidate']); sc=r['s']['score'] if r else '—'
    gp=sum(1 for v in s['gates'].values() if v=='pass'); gf=sum(1 for v in s['gates'].values() if v=='fail')
    P.append(f'<div class="t3card"><div class="t3h"><div class="rank">{s["rank"]}</div><div><h3>{e(s["name"])}</h3><div class="meta mono">{e(s["region"])} · {e(s["coords"])} · {e(s["elev"])}</div><p class="verdict">{e(s["verdict"])}</p></div><div class="score"><b>{sc}</b><span>engine score</span><span>{gp}✓ {gf}✕ {len(GATES)-gp-gf} open</span></div></div>')
    P.append(f'<h4>The case</h4><p class="thesis">{e(s["thesis"])}</p>')
    P.append('<h4>Route through the poem</h4><table class="tbl"><thead><tr><th>Line</th><th>Place</th><th>Reading</th><th>Tier</th></tr></thead><tbody>'+''.join(f'<tr><td class="mono">{lineNo.get(x["line"],x["line"])}<div class="sm poem">{e(L[x["line"]]["text"]) if x["line"] in L else ""}</div></td><td><b class="{"open" if x["place"].startswith(("OPEN","UNPLACED")) else ""}">{e(x["place"])}</b></td><td class="sm">{e(x["reading"])}</td><td>{chip("t-"+x["tier"],TIER[x["tier"]])}</td></tr>' for x in s['route'])+'</tbody></table>')
    P.append('<div class="two"><div><h4>Evidence</h4>'+''.join(f'<div class="ev">{chip("t-"+x["tier"],TIER[x["tier"]])} {e(x["t"])}<div class="sm mono">{e(x["src"])}</div></div>' for x in s['evidence'])+'</div><div><h4>Against it</h4><ul class="bad">'+''.join(f'<li>{e(x)}</li>' for x in s['against'])+f'</ul><h4>What would kill it</h4><p class="kill">{e(s["kill"])}</p></div></div>')
    P.append('<h4>Cheapest tests, in order</h4><ol>'+''.join(f'<li>{e(x)}</li>' for x in s['tests'])+'</ol><h4>Still open</h4><p>'+' · '.join(e(x) for x in s['open'])+'</p>')
    P.append('<h4>The gate</h4><div class="gates">'+''.join(f'<span class="g {s["gates"].get(g[0],"unk")}">{"✓" if s["gates"].get(g[0])=="pass" else "✕" if s["gates"].get(g[0])=="fail" else "·"} {e(g[1])}</span>' for g in GATES)+'</div></div>')
P.append('<h3>Side by side</h3><table class="tbl"><thead><tr><th></th>'+''.join(f'<th>{s["rank"]}. {e(s["name"].split(" — ")[0].split(" (")[0])}</th>' for s in T3['solves'])+'</tr></thead><tbody>'+''.join(('<tr><td>Engine score</td>'+''.join(f'<td><b>{cands[s["candidate"]]["s"]["score"] if s["candidate"] in cands else "—"}</b></td>' for s in T3['solves'])+'</tr>') if row[0]=='Engine score' else f'<tr><td>{e(row[0])}</td>'+''.join(f'<td>{e(v)}</td>' for v in row[1:])+'</tr>' for row in T3['compare'])+'</tbody></table>')
P.append(f'<div class="two"><div><h4>Where the Moab solve stands</h4><p>{e(T3["method"]["moab"])}</p></div><div class="warnbox"><h4>What I do not know</h4><ul>'+''.join(f'<li>{e(x)}</li>' for x in T3['method']['unknown'])+'</ul></div></div></div>')

# 4 roster
P.append(f'<div class="page"><h2 class="sec"><span class="n">4</span>Solve roster — every candidate, ranked</h2><p class="hint">Standing solves first, then those ruled out. Each entry shows its case, what would kill it, the cheapest test, gate results and its route through the poem.</p>')
def solve_block(i,r):
    c,s=r['c'],r['s']; g=c.get('gates',{}); ch=c.get('chain',{}); v=c.get('verdicts',{})
    gp=[GL[k][1] for k,x in g.items() if x=='pass' and k in GL]; gf=[GL[k][1] for k,x in g.items() if x=='fail' and k in GL]
    hardtxt=('<span>hard lines <b>−%d</b></span>' % (30*s['hardFail'])) if s['hardFail'] else ''
    h=f'<div class="solve {"out" if s["ruledOut"] else ""}"><div class="sh"><span class="rk">{i}</span><div><h3>{e(c["name"])}</h3><div class="meta mono">{e(c.get("region",""))}{" · "+e(c["coords"]) if c.get("coords") else ""}{" · "+e(c["elev"]) if c.get("elev") else ""}</div></div><div class="score"><b>{s["score"]}</b><span>{"ruled out" if s["ruledOut"] else "standing"}</span></div></div>'
    h+=f'<div class="parts"><span>chain <b>{s["parts"]["chain"]}</b> ({s["filled"]} slots)</span><span>poem <b>{s["parts"]["fit"]}</b> ({s["fit"]} fit · {s["fail"]} fail)</span><span>gate <b>{("−"+str(40*s["gFail"])) if s["gFail"] else "+"+str(s["parts"]["gate"])}</b> ({s["gPass"]}✓ {s["gFail"]}✕ {s["gUnk"]} open)</span><span>evidence <b>{s["parts"]["evid"]}</b> ({s["mentions"]} facts mention it)</span>{hardtxt}</div>'
    if c.get('notes'): h+=f'<div class="kv"><span class="k">Case</span>{e(c["notes"])}</div>'
    if c.get('kill'): h+=f'<div class="kv kill"><span class="k">What would kill it</span>{e(c["kill"])}</div>'
    if c.get('test'): h+=f'<div class="kv test"><span class="k">Cheapest test</span>{e(c["test"])}</div>'
    if gp or gf: h+='<div class="kv"><span class="k">Gate</span>'+(('<span class="ok">Passes:</span> '+'; '.join(e(x) for x in gp)+'. ') if gp else '')+(('<span class="badt">Fails:</span> '+'; '.join(e(x) for x in gf)+'.') if gf else '')+'</div>'
    rows=[(l,ch[l['id']]) for l in lines if l['id'] in ch and (ch[l['id']].get('place') or ch[l['id']].get('reading'))]
    if rows: h+='<table class="tbl route"><thead><tr><th>Line</th><th>Place</th><th>Reading</th><th>Sure</th><th>Verdict</th></tr></thead><tbody>'+''.join(f'<tr><td class="mono">{l["no"]}<div class="sm poem">{e(l["text"])}</div></td><td><b>{e(sl.get("place",""))}</b>{("<div class=sm mono>"+e(sl["coords"])+"</div>") if sl.get("coords") else ""}</td><td class="sm">{e(sl.get("reading",""))}</td><td>{sl.get("conf") or "—"}</td><td class="{v.get(l["id"],"")}">{ {"fit":"✓ fits","fail":"✕ fails"}.get(v.get(l["id"]),"unjudged")}</td></tr>' for l,sl in rows)+'</tbody></table>'
    else: h+='<p class="hint">No lines placed.</p>'
    return h+'</div>'
for i,r in enumerate(D['ranked']): P.append(solve_block(i+1,r))
P.append('</div>')

# 5 gate
P.append(f'<div class="page"><h2 class="sec"><span class="n">5</span>The gate — twenty rules</h2><p class="hint">Every solve is judged against these. Ranked by how many solves each rule has killed.</p><table class="tbl"><thead><tr><th>#</th><th>Rule</th><th>Source</th><th>Kills</th><th>Pass</th><th>Open</th></tr></thead><tbody>'+''.join(f'<tr><td>{i+1}</td><td><b>{e(x["g"][1])}</b></td><td class="sm">{e(x["g"][2])}</td><td class="badt">{x["kills"]}</td><td class="ok">{x["pass"]}</td><td class="sm">{x["unk"]}</td></tr>' for i,x in enumerate(D['gateRank']))+'</tbody></table>')
P.append('<h3>Gate matrix</h3><p class="hint">✓ pass · ✕ fail · blank open. Columns are the rules in the order above.</p><div class="matrixwrap"><table class="tbl matrix"><thead><tr><th>Solve</th>'+''.join(f'<th title="{e(x["g"][1])}">{i+1}</th>' for i,x in enumerate(D['gateRank']))+'</tr></thead><tbody>'+''.join(f'<tr class="{"out" if r["s"]["ruledOut"] else ""}"><td>{e(short(r["c"]))}</td>'+''.join(f'<td class="{r["c"].get("gates",{}).get(x["g"][0],"")}">{ {"pass":"✓","fail":"✕"}.get(r["c"].get("gates",{}).get(x["g"][0]),"")}</td>' for x in D['gateRank'])+'</tr>' for r in D['ranked'])+'</tbody></table></div></div>')

# 6 statements
P.append(f'<div class="page"><h2 class="sec"><span class="n">6</span>What Posey said</h2><p class="hint">{len(stmts)} statements. Confirmed (in writing or the rules) first, then reported through a named source. Arrows show which poem lines each statement is matched to; ✕ marks a contradiction.</p>')
for cf,label in [('confirmed','Confirmed'),('likely','Likely / reported'),('unverified','Unverified'),('disputed','Disputed')]:
    grp=[i for i in stmts if i['conf']==cf]
    if grp: P.append(f'<h3>{label} · {len(grp)}</h3>'+''.join(fact_row(i) for i in grp))
P.append('</div>')

# 7 evidence by line
P.append(f'<div class="page"><h2 class="sec"><span class="n">7</span>Evidence by line</h2><p class="hint">Every fact matched to each poem line, with the reason for the match. Strongest confidence first. Long facts are shortened here; the fact id (i001…) finds the full text in sections 6 and 8.</p>')
for l in lines:
    P.append(f'<h3 class="lh2"><span class="mono">{l["no"]}</span> {e(l["text"])} <span class="heat">{l["heat"]["facts"]} facts · {l["heat"]["against"]} against</span></h3>')
    if not l['links']: P.append('<p class="hint">Nothing binds to this line yet.</p>'); continue
    for k in l['links']:
        it=intel.get(k['id']); 
        if not it: continue
        txt=it["text"]; txt=(txt[:230].rsplit(' ',1)[0]+' …') if len(txt)>240 else txt
        P.append(f'<div class="lnk {"con" if k["stance"]=="contradicts" else ""}"><span class="stance">{"CONTRADICTS" if k["stance"]=="contradicts" else "SUPPORTS"} · w{k.get("weight","")} · <span class="fid">{e(it["id"])}</span></span><div class="ft">{e(txt)}</div>'+(f'<div class="why">{e(k["why"])}</div>' if k.get('why') else '')+f'<div class="fm">{e(KIND.get(it["kind"],it["kind"]))} · {e(CONF.get(it["conf"],it["conf"]))}{" · "+e(it["source"]) if it.get("source") else ""}</div></div>')
P.append('</div>')

# 8 facts catalogue
P.append(f'<div class="page"><h2 class="sec"><span class="n">8</span>Facts catalogue</h2><p class="hint">Everything in the store except Posey statements (section 6), grouped by kind and ordered by weight (links × confidence).</p>')
def fw(it): return len(it.get('links',[]))*(1+{"confirmed":3,"likely":2,"unverified":1}.get(it['conf'],0))
for kind,label in [(k,v) for k,v in KIND.items() if k!='statement']:
    grp=sorted([i for i in D['intel'] if i['kind']==kind], key=lambda i:(-fw(i), -(i.get('created') or 0)))
    if grp: P.append(f'<h3>{e(label)} · {len(grp)}</h3>'+''.join(fact_row(i) for i in grp))
P.append('</div>')

# 9 map
ms=D['mapStates']; order={'active':0,'hot':1,'inplay':2,'warm':2,'open':3,'cold':4,'fringe':5,'out':6,'eliminated':6}
P.append(f'<div class="page"><h2 class="sec"><span class="n">9</span>The map — state by state</h2><table class="tbl"><thead><tr><th>State</th><th>Status</th><th>Note</th></tr></thead><tbody>'+''.join(f'<tr><td><b>{e(k)}</b></td><td>{chip("ms-"+v.get("status",""),v.get("status",""))}</td><td class="sm">{e(v.get("note",""))}</td></tr>' for k,v in sorted(ms.items(), key=lambda kv:(order.get(kv[1].get('status'),9),kv[0])))+'</tbody></table></div>')

# 10 next moves, objections, sources
P.append(f'<div class="page"><h2 class="sec"><span class="n">10</span>Next moves, objections and sources</h2><h3>Next moves</h3><p class="hint">The cheapest actions that would change the ranking, as the site computes them today.</p><ol class="moves">'+''.join(f'<li><span class="pri p{m["pri"]}">P{m["pri"]}</span> {e(m["t"])}<div class="sm">{e(m["m"])}</div></li>' for m in D['moves'])+'</ol>')
P.append('<h3>Standing objections</h3>'+''.join(fact_row(intel[i]) for i in D['objections'] if i in intel))
P.append('<h3>Sources, ranked by weight</h3><table class="tbl"><thead><tr><th>Source</th><th>Facts</th><th>Weight</th><th>Earliest</th></tr></thead><tbody>'+''.join(f'<tr><td>{e(x["source"])}</td><td>{x["n"]}</td><td>{x["w"]}</td><td class="sm">{e(x["when"])}</td></tr>' for x in D['sources'])+'</tbody></table></div>')

CSS='''
@page{ size:Letter; margin:0.7in 0.65in 0.75in 0.65in; }
*{box-sizing:border-box}
body{font-family:"Bitstream Charter","Liberation Serif",Georgia,serif; font-size:9.6pt; line-height:1.38; color:#161a20; margin:0}
.mono{font-family:"DejaVu Sans Mono",monospace; font-size:8pt}
h1,h2,h3,h4,.tile b,.rank,.score b{font-family:"Liberation Sans","DejaVu Sans",Arial,sans-serif}
.page{page-break-before:always}
h2.sec{font-size:22pt; margin:0 0 6pt; padding-bottom:6pt; border-bottom:2.5pt solid #9a6e12; letter-spacing:-.01em; text-transform:uppercase}
h2.sec .n{display:inline-block; background:#9a6e12; color:#fff; font-size:12pt; padding:2pt 7pt; border-radius:3pt; margin-right:9pt; vertical-align:middle}
h3{font-size:12.5pt; margin:14pt 0 5pt; color:#1c222b; text-transform:uppercase; letter-spacing:.02em; page-break-after:avoid}
h4{font-size:9.5pt; margin:9pt 0 3pt; color:#9a6e12; text-transform:uppercase; letter-spacing:.06em; page-break-after:avoid}
p{margin:0 0 6pt} ul,ol{margin:0 0 6pt; padding-left:16pt} li{margin-bottom:3pt}
.hint{color:#5c6675; font-size:8.8pt}
.sm{font-size:8.2pt; color:#5c6675}
.poem{font-style:italic}
.cover{height:9.3in; display:flex; flex-direction:column; justify-content:center; padding:0 .4in; border-left:6pt solid #9a6e12}
.cover .eyebrow{font-family:"DejaVu Sans Mono"; font-size:9pt; letter-spacing:.2em; text-transform:uppercase; color:#9a6e12}
.cover h1{font-size:44pt; line-height:1; margin:8pt 0 10pt; letter-spacing:-.01em}
.cover .sub{font-size:13pt; color:#4a5361; max-width:5.6in; margin-bottom:28pt}
.covergrid{display:grid; grid-template-columns:repeat(3,1fr); gap:10pt; max-width:5.6in; margin-bottom:28pt}
.covergrid div{border-top:1.5pt solid #d9dee6; padding-top:6pt} .covergrid b{font-family:"Liberation Sans"; font-size:22pt; display:block} .covergrid span{font-size:8.5pt; color:#5c6675; text-transform:uppercase; letter-spacing:.08em}
.coverfoot{font-size:9.5pt; color:#4a5361; line-height:1.6}
.toc{list-style:none; padding:0; font-size:13pt; font-family:"Liberation Sans"} .toc li{border-bottom:1pt dotted #c3cad5; padding:6pt 0} .toc .n{display:inline-block; width:28pt; color:#9a6e12; font-weight:bold}
.legend{margin-top:22pt; padding:10pt 12pt; background:#f4f5f8; border-radius:4pt} .legend p{font-size:9pt}
.chip{display:inline-block; font-family:"DejaVu Sans Mono"; font-size:6.8pt; letter-spacing:.06em; text-transform:uppercase; padding:1.5pt 4pt; border:0.8pt solid #8a93a2; border-radius:2pt; margin-left:4pt; vertical-align:middle; color:#4a5361; white-space:nowrap}
.chip.t-confirmed,.chip.c-confirmed{color:#1f8f5f; border-color:#1f8f5f} .chip.t-reported,.chip.c-likely{color:#9a6e12; border-color:#9a6e12} .chip.t-circulating{color:#2e86b5; border-color:#2e86b5} .chip.t-fan{color:#6a4fd8; border-color:#6a4fd8} .chip.t-unverified,.chip.c-unverified{color:#c2611f; border-color:#c2611f} .chip.c-disputed{color:#c23b3b; border-color:#c23b3b}
.chip.st-pinned{color:#1f8f5f; border-color:#1f8f5f} .chip.st-contested{color:#c23b3b; border-color:#c23b3b} .chip.st-partial{color:#9a6e12; border-color:#9a6e12} .chip.hard{background:#c23b3b; color:#fff; border-color:#c23b3b}
.chip.ms-active{color:#1f8f5f; border-color:#1f8f5f} .chip.ms-hot{color:#c2611f; border-color:#c2611f} .chip.ms-warm{color:#9a6e12; border-color:#9a6e12}
.tiles{display:grid; grid-template-columns:repeat(4,1fr); gap:8pt; margin:8pt 0 12pt}
.tile{border:1pt solid #d9dee6; border-radius:4pt; padding:8pt 10pt} .tile.gold{border-color:#9a6e12; background:#fbf6ea} .tile .k{display:block; font-family:"DejaVu Sans Mono"; font-size:7pt; letter-spacing:.1em; text-transform:uppercase; color:#7a8493} .tile b{display:block; font-size:15pt; margin:3pt 0} .tile .s{font-size:8pt; color:#5c6675}
.t3mini{display:grid; grid-template-columns:repeat(3,1fr); gap:8pt; margin-bottom:8pt} .t3mini>div{display:flex; gap:8pt; border:1pt solid #d9dee6; border-radius:4pt; padding:7pt 9pt} .t3mini b{font-family:"Liberation Sans"; font-size:20pt; color:#9a6e12; line-height:1} .t3mini .nm{font-weight:bold; font-size:9pt} .t3mini .vd{font-size:8pt; color:#5c6675}
.tbl{width:100%; border-collapse:collapse; margin:4pt 0 10pt; font-size:8.6pt; page-break-inside:auto} .tbl th{font-family:"Liberation Sans"; font-size:7.2pt; text-transform:uppercase; letter-spacing:.06em; text-align:left; color:#9a6e12; border-bottom:1.2pt solid #9a6e12; padding:4pt 5pt} .tbl td{padding:4pt 5pt; border-bottom:0.6pt solid #dfe3ea; vertical-align:top} .tbl tr{page-break-inside:avoid}
.tbl tr.out td{color:#8a93a2} .tbl tr.contested td{background:#fdf3f3}
.tbl td.fit{color:#1f8f5f} .tbl td.fail{color:#c23b3b}
.board td:nth-child(n+4){text-align:right} .board th:nth-child(n+4){text-align:right} .board td:nth-child(11),.board th:nth-child(11){text-align:left}
.poemblock{background:#f4f5f8; padding:12pt 16pt; border-left:3pt solid #9a6e12; margin-bottom:12pt; columns:2; column-gap:24pt} .poemblock p{font-style:italic; font-size:10pt; break-inside:avoid; margin:0 0 8pt} .ptitle{font-family:"Liberation Sans"; font-weight:bold; column-span:all; margin-bottom:6pt}
h3.stz .mode{font-family:"DejaVu Sans Mono"; font-size:7.5pt; text-transform:none; letter-spacing:0; color:#7a8493; margin-left:8pt}
.lineblk{border-top:0.6pt solid #dfe3ea; padding:6pt 0; page-break-inside:avoid} .lh{display:flex; gap:6pt; align-items:center; flex-wrap:wrap} .lh .poem{font-size:10.5pt; font-weight:bold} .heat{font-size:7.5pt; color:#7a8493; margin-left:auto; font-family:"DejaVu Sans Mono"} .note{font-size:8.8pt; color:#3a4350; margin-top:3pt} .best{font-size:8.6pt; color:#1f8f5f; margin-top:2pt}
.two{display:grid; grid-template-columns:1fr 1fr; gap:16pt}
.t3card{border:1.2pt solid #9a6e12; border-radius:5pt; padding:10pt 12pt; margin:12pt 0; page-break-before:always}
.t3h{display:flex; gap:10pt; align-items:flex-start} .rank{background:#9a6e12; color:#fff; font-size:22pt; font-weight:bold; width:34pt; height:34pt; display:flex; align-items:center; justify-content:center; border-radius:4pt; flex:0 0 auto} .t3h h3{margin:0 0 2pt; font-size:15pt; text-transform:none} .t3h .meta{font-size:7.5pt; color:#7a8493} .verdict{color:#4a5361; margin:4pt 0 0}
.score{margin-left:auto; text-align:right; flex:0 0 auto} .score b{display:block; font-size:22pt; color:#9a6e12; line-height:1} .score span{display:block; font-size:7pt; text-transform:uppercase; letter-spacing:.08em; color:#7a8493}
.thesis{font-size:9.6pt}
b.open{color:#c2611f}
.ev{font-size:8.6pt; padding:4pt 0; border-bottom:0.6pt dotted #d9dee6} .ev .chip{margin:0 4pt 0 0}
ul.bad li::marker{color:#c23b3b} .kill{border-left:2.5pt solid #c23b3b; padding-left:8pt; color:#3a4350}
.gates{display:flex; flex-wrap:wrap; gap:3pt} .g{font-family:"DejaVu Sans Mono"; font-size:6.8pt; border:0.7pt solid #c3cad5; border-radius:2pt; padding:2pt 4pt; color:#7a8493} .g.pass{color:#1f8f5f; border-color:#1f8f5f} .g.fail{color:#c23b3b; border-color:#c23b3b; background:#fdf0f0}
.warnbox{border:1pt solid #c2611f; border-radius:4pt; padding:6pt 10pt} .warnbox h4{margin-top:2pt}
.solve{border:0.8pt solid #d9dee6; border-radius:4pt; padding:8pt 10pt; margin:0 0 10pt} .sh,.parts,.kv{page-break-inside:avoid} .sh{page-break-after:avoid} .solve.out{background:#f7f7f9} .solve.out h3{color:#7a8493}
.sh{display:flex; gap:8pt; align-items:flex-start} .rk{font-family:"Liberation Sans"; font-weight:bold; font-size:14pt; color:#9a6e12; width:24pt; flex:0 0 auto} .sh h3{margin:0; font-size:12pt; text-transform:none} .sh .meta{font-size:7.5pt; color:#7a8493} .sh .score b{font-size:18pt}
.parts{display:flex; gap:10pt; flex-wrap:wrap; font-size:7.2pt; color:#5c6675; margin:5pt 0; font-family:"DejaVu Sans Mono"}
.kv{font-size:8.8pt; margin:3pt 0} .kv .k{display:inline-block; font-family:"DejaVu Sans Mono"; font-size:6.8pt; letter-spacing:.08em; text-transform:uppercase; color:#9a6e12; margin-right:5pt; min-width:60pt} .kv.kill .k{color:#c23b3b} .kv.test .k{color:#1f8f5f} .ok{color:#1f8f5f; font-weight:bold} .badt{color:#c23b3b; font-weight:bold}
.route{margin-top:6pt} .route td.fit{color:#1f8f5f} .route td.fail{color:#c23b3b}
.matrix{font-size:7.5pt} .matrix td,.matrix th{padding:2pt 3pt; text-align:center} .matrix td:first-child{text-align:left; white-space:nowrap} .matrix td.pass{color:#1f8f5f} .matrix td.fail{color:#c23b3b; background:#fdf0f0}
.fact{padding:5pt 0; border-bottom:0.6pt solid #e6e9ef; page-break-inside:avoid} .fact .ft{font-size:9pt} .fact .fm,.lnk .fm{font-size:7.4pt; color:#7a8493; font-family:"DejaVu Sans Mono"; margin-top:2pt} .why{font-size:8.2pt; color:#4a5361; font-style:italic; margin-top:2pt}
.lk{display:inline-block; font-size:6.8pt; padding:0 3pt; border:0.6pt solid #c3cad5; border-radius:2pt; margin-left:2pt; color:#4a5361} .lk.con{color:#c23b3b; border-color:#c23b3b}
h3.lh2{font-size:11pt; text-transform:none; display:flex; gap:6pt; align-items:baseline; border-top:1pt solid #9a6e12; padding-top:6pt} h3.lh2 .heat{margin-left:auto}
.lnk{padding:4pt 0 4pt 8pt; border-left:2pt solid #1f8f5f; margin:3pt 0; page-break-inside:avoid} .lnk.con{border-left-color:#c23b3b} .lnk .stance{font-family:"DejaVu Sans Mono"; font-size:6.6pt; letter-spacing:.08em; color:#1f8f5f} .lnk.con .stance{color:#c23b3b} .lnk .ft{font-size:8.6pt} .fid{font-family:"DejaVu Sans Mono"; font-size:6.8pt; color:#9a6e12; margin-right:5pt}
.moves li{margin-bottom:5pt} .pri{font-family:"DejaVu Sans Mono"; font-size:7pt; padding:1pt 4pt; border-radius:2pt; background:#e9edf2; margin-right:4pt} .pri.p1{background:#9a6e12; color:#fff}
'''
doc=f'<!doctype html><html><head><meta charset="utf-8"><title>Beyond the Map\'s Edge — Field HQ</title><style>{CSS}</style></head><body>{"".join(P)}</body></html>'
open(S+'fieldhq.html','w').write(doc); print('html', len(doc))
