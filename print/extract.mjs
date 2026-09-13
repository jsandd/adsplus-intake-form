import { chromium } from 'playwright';
import fs from 'fs';
const S='/tmp/claude-0/-home-user-adsplus-intake-form/46f457d2-c02d-55f7-ba6b-5343a1b8ce9a/scratchpad/';
const html = fs.readFileSync('/home/user/adsplus-intake-form/maps-edge-workbench.html','utf8');
const rd = d => fs.readdirSync(S+'livedb/'+d).map(f => JSON.parse(fs.readFileSync(S+'livedb/'+d+'/'+f,'utf8')));
const data = { poem: JSON.parse(fs.readFileSync(S+'livedb/poem/doc.json','utf8')), intel: rd('intel'), candidates: rd('candidates'), map: JSON.parse(fs.readFileSync(S+'livedb/map/states.json','utf8')) };
const b = await chromium.launch({ executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const pg = await b.newPage({ viewport:{ width:1400, height:900 } });
await pg.setContent(html, { waitUntil:'load' }); await pg.waitForTimeout(500);
const out = await pg.evaluate(data => {
  state.usingDemo=false; state.poemTitle=data.poem.title; state.poemRaw=data.poem.raw; state.lines=data.poem.lines; state.intel=data.intel.sort((a,b)=>a.id.localeCompare(b.id)); state.solves=data.candidates.map(normSolve); state.mapStates=data.map.states||{};
  const rk = ranked().map(({c,s}) => ({ c, s, plan: fieldPlan(c), mentions: mentions(c).slice(0,10).map(x=>({id:x.it.id, hits:x.hits})) }));
  const lines = state.lines.map((l,i) => ({ ...l, no:L(i), links: linksFor(l.id).map(x=>({id:x.it.id, stance:x.link.stance, weight:x.link.weight, why:x.link.why})), heat: lineHeat(l) }));
  return { title: state.poemTitle, raw: state.poemRaw, lines, intel: state.intel, ranked: rk, reads: bestReads().map(r=>({ line:r.line.id, best: r.best ? { c:r.best.c.id, place:r.best.s.place, reading:r.best.s.reading, conf:r.best.s.conf } : null, agree:r.agree, distinct:r.distinct })),
    moves: nextMoves(), objections: objections().map(o=>o.id), gateRank: gateRank(), sources: sourceRank(), GATES, STAGES, KIND_LABEL, CONF_LABEL, TOP3, mapStates: state.mapStates };
}, data);
fs.writeFileSync(S+'pdf/extract.json', JSON.stringify(out));
console.log('solves', out.ranked.length, 'intel', out.intel.length, 'lines', out.lines.length, 'top', out.ranked[0].c.name, out.ranked[0].s.score);
await b.close();
