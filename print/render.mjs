import { chromium } from 'playwright';
const S='/tmp/claude-0/-home-user-adsplus-intake-form/46f457d2-c02d-55f7-ba6b-5343a1b8ce9a/scratchpad/pdf/';
const b = await chromium.launch({ executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const pg = await b.newPage();
await pg.goto('file://'+S+'fieldhq.html', { waitUntil:'load' });
await pg.pdf({ path:S+'Beyond-the-Maps-Edge-Field-HQ.pdf', format:'Letter', printBackground:true, displayHeaderFooter:true, margin:{ top:'0.7in', bottom:'0.75in', left:'0.65in', right:'0.65in' },
  headerTemplate:'<div style="font-family:DejaVu Sans Mono,monospace; font-size:7px; color:#7a8493; width:100%; padding:0 0.65in; display:flex; justify-content:space-between"><span>BEYOND THE MAP\'S EDGE · FIELD HQ</span><span>Printed from the live database</span></div>',
  footerTemplate:'<div style="font-family:DejaVu Sans Mono,monospace; font-size:7px; color:#7a8493; width:100%; padding:0 0.65in; display:flex; justify-content:space-between"><span>Reliability tiers on every claim · nothing below Reported carries a line alone</span><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>' });
await b.close(); console.log('pdf done');
