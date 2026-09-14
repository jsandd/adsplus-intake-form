import html
e=html.escape
def T(head, rows, cls=""):
    return f'<table class="m {cls}"><thead><tr>'+''.join(f'<th>{e(h)}</th>' for h in head)+'</tr></thead><tbody>'+''.join('<tr>'+''.join(f'<td>{c}</td>' for c in r)+'</tr>' for r in rows)+'</tbody></table>'
def c(*ids): return ' '.join(f'<span class="cite">{i}</span>' for i in ids)
def blank(): return '<span class="fill"></span>'
def tag(t): return f'<span class="tag {t.lower()[0]}">{t}</span>'
P=[]
P.append('''<div class="cover"><div class="eyebrow">Posey-only working tool</div><h1>Solve Matrix</h1><p class="sub">Built from Justin Posey's own statements and nothing else: 216 items, cited by section.item number from "What Justin Posey Has Said." No fan theories, no community solves. Seven matrices, each with blank columns for your own work.</p>
<ol class="toc"><li><b>A</b> Journey matrix: the poem stage by stage, with the mode, constraints, distances and open questions Posey attached to each</li><li><b>B</b> Location filter: every rule that applies to the final spot, with pass/fail boxes for three candidates</li><li><b>C</b> Distance and geometry ledger: every statement that carries a length, a direction or a shape</li><li><b>D</b> Element matrix: what each part of the hunt (poem, book, map, series, songs, cipher, logo, time) contains and what it is for</li><li><b>E</b> Deductions that follow from his words alone, with the chain of citations</li><li><b>F</b> Progress timeline: what he says has been solved, and when</li><li><b>G</b> Open-question ledger: what he declined, and a specific, not-on-the-nose way to ask it again</li></ol>
<p class="note">Citation key: [3.4] = section 3, item 4 of the statements list. Tags: C confirmed · S said · L leaned · D declined.</p></div>''')

# A journey matrix
head=["Stage","Mode per Posey","What he confirmed or said","Hard constraints in force","Distance he attached","Still open (declined)","Test you can run","Your reading"]
rows=[
["<b>Stanza 1</b> (1:1–1:4)","Armchair. Not actionable, but 'helpful context' "+c("2.5"),"Every line is helpful; first stanza 'at least a large portion' solved by Sep 2025 "+c("2.5","14.4")+". Numbers hide in words and wordplay "+c("2.9")+". The element of time is important "+c("2.11"),"No red herrings "+c("2.3")+". Consecutive order "+c("2.2"),"None","Whether it must be rearranged: 'not going to rule that out' "+c("2.7"),"Read it as instructions for reading, not as a place. Count what can be counted "+c("2.9"),blank()],
["<b>2:1</b> As hope surges, clear and bright","Armchair. First actionable clue "+c("2.6"),"The book does not name the specific area but has descriptions that 'pertain to the area' "+c("9.10"),"Free, 24/7, public "+c("1.7","1.10"),"None stated here","Whether the surge is water: never asked in his words","Find the book passages that describe terrain, then match "+c("9.10","9.18"),blank()],
["<b>2:2</b> Walk near waters' silent flight","Walking distance begins "+c("3.4"),"Walking distance from here through 2:3 "+c("3.4"),"No swimming, no dangerous water crossing "+c("1.3","1.16")+". Feet wet not required "+c("4.13"),"Walking distance to 2:3 "+c("3.4"),"River crossing: not specified "+c("1.15"),"Measure 2:2 to 2:3 on foot; if it needs a car it fails "+c("3.4"),blank()],
["<b>2:3</b> Round the bend, past the Hole","Walking "+c("3.4"),"The Hole has no man-made implication "+c("5.1")+". Not the man-made clue "+c("5.1"),"Not a cave, mine or tunnel "+c("1.1"),"Walking distance from 2:2 "+c("3.4"),"Whether the Hole is a hole-named place: 'on the nose' "+c("5.2"),"Your Hole must be natural and on the walk; a culvert, tunnel or mine fails "+c("1.1","5.1"),blank()],
["<b>2:4</b> I wait for you to cast your pole","Walking (continues)","Nothing confirmed","—","—","Fishing pole: not specified "+c("2.26"),"Test both readings against 3:1 "+c("2.26"),blank()],
["<b>3:1</b> In ursa east his realm awaits","Armchair (stanza 3 is before BOTG) "+c("3.2"),"Only Ursa East matters; no west Ursa "+c("6.1")+". Lowercase intentional "+c("6.2")+". 'He' alive 'depends on your perspective' "+c("6.3"),"Consecutive after 2:4 "+c("2.2"),"Not a great distance from the previous clue "+c("2.17"),"'Use a star': no further clarity "+c("6.2"),"Ursa East must be a thing with an east, not a heading "+c("6.1"),blank()],
["<b>3:2</b> His bride stands guard at ancient gates","Armchair","Bride identified by someone "+c("6.6")+". Not alive now; something visible "+c("6.4")+". 'Bride' is the right word "+c("2.25")+". Strange to find the bride without understanding the gates "+c("6.7"),"Gates first, then bride "+c("6.7"),"Bride to treasure: 'a matter of perspective' "+c("6.11"),"Ever alive: 'depends how you define alive' "+c("6.5"),"Name the gates before the bride; if your bride comes first, re-order "+c("6.7"),blank()],
["<b>3:3</b> Her foot of three at twenty degree","Armchair","You do not need to be at the bride to identify her foot of three "+c("6.12")+". Numbers indirect "+c("2.9")+". A distance element exists "+c("2.10"),"Solvable from a map or a distance "+c("6.12"),"'Twenty' and 'three' are the poem's only stated numbers; he keeps wordplay for numbers in play "+c("2.9"),"Nothing declined here","Identify the foot of three from a map. If it needs standing at the bride, it is wrong "+c("6.12"),blank()],
["<b>3:4</b> Return her face to find the place","Armchair","Her face belongs to the bride "+c("6.8")+". Physical rotation 'technically' yes "+c("6.9")+". Face to place 'not as far as many think' "+c("6.10")+". The place is not necessarily the sacred space "+c("6.13"),"—","Face to place: short "+c("6.10"),"Face or gaze: no clarity "+c("6.14"),"Rotate something physical and see where it points; the place should be near "+c("6.9","6.10"),blank()],
["<b>4:1</b> Double arcs on granite bold","Boots on the ground required from here "+c("3.2"),"One clue, depending on path, has a man-made implication; the Hole is not it "+c("4.8","5.1"),"Not associated with buildings "+c("1.1")+"; exterior of a structure 'always a possibility' "+c("1.13"),"—","Is this the man-made clue: punted "+c("5.3")+". Natural or created: not answered "+c("5.4")+". A bearing: punted "+c("5.5"),"Ask whether the arcs can be seen without being on site; if yes, that contradicts BOTG at stanza 4 "+c("3.2"),blank()],
["<b>4:2–4:4</b> Secrets of the past, beyond time's reach, wonder guards this sacred space","Boots on the ground","Sacred space not necessarily the place "+c("6.13")+". Something must be manipulated to see the treasure; a flashlight may help "+c("4.9")+". No clue visible from 15 feet "+c("4.6")+". No blaze on a tree "+c("4.19"),"Not near a trail "+c("4.7")+". Not near graves "+c("1.1"),"Within a mile of the car to figure out where it is "+c("3.5"),"Buried: will not say "+c("4.10")+". Rocks: punted "+c("4.12"),"Your spot must be invisible from 15 feet and off-trail "+c("4.6","4.7"),blank()],
["<b>Stanza 5</b>","Possibly the last actionable clue "+c("2.6"),"Last actionable clue is stanza four or five 'depending on interpretation' "+c("2.6"),"—","—","—","Decide whether stanza 5 moves you or only warns you "+c("2.6"),blank()],
["<b>Checkpoint</b>","Not specified whether before or after boots on the ground "+c("7.5"),"Placed AND already there "+c("7.2")+". Topographic 'implication' "+c("7.2")+". At least halfway through the clues "+c("7.1")+". Hard to get all the way without seeing it "+c("7.3")+". Not in the series "+c("7.4"),"Same rules as the treasure: not underwater, cave, private, graves "+c("1.1"),"Searchers have been within 200 feet of it "+c("14.3"),"Before or after BOTG "+c("7.5"),"Your route must pass something you could photograph and send him "+c("14.3"),blank()],
["<b>The final spot</b>","Retrieving, not searching "+c("3.10"),"Only he knows "+c("4.1")+". Important to him, known 'for quite some time' "+c("4.2")+". Kitchen-sized area, unreached "+c("7.8","14.5")+". Below 11,000 ft "+c("4.17"),"All of section 1","A hike is required, length unspecified "+c("3.8")+"; a low-rider car reaches the road "+c("3.9"),"Prius within a mile: punted "+c("4.22"),"Run matrix B","—"],
]
P.append('<div class="page"><h2><span>A</span>Journey matrix</h2><p class="hint">The poem stage by stage. Mode and constraints come only from his statements; the Test column is what his words let you check.</p>'+T(head,rows,"journey")+'</div>')

# B location filter
head=["Rule","Tag","Cite","Applies to","What it eliminates","Candidate A","Candidate B","Candidate C"]
R=lambda rule,t,ids,app,elim:[rule,tag(t),c(*ids),app,elim,blank(),blank(),blank()]
rows=[
R("Not underwater","Confirmed",["1.1"],"Treasure, checkpoint, placed clues","Lakebeds, river bottoms, springs you must enter"),
R("Not on private property","Confirmed",["1.1","1.5","1.9"],"All hunt items","Any spot needing permission; check property lines"),
R("Not in a cave, mine or tunnel","Confirmed",["1.1"],"All hunt items","Caverns, adits, culverts, road tunnels"),
R("Nothing that needs rappelling, ropes, ladders, climbing or swimming","Confirmed",["1.1","1.3","1.12"],"All hunt items","Cliff faces, canyon drops, islands"),
R("Not associated with man-made buildings; gazebo counts","Confirmed",["1.1","1.13"],"All hunt items","Cabins, ruins with roofs, shelters. Exterior of a structure not ruled out"),
R("Not near graves or grave markers","Confirmed",["1.1"],"All hunt items","Cemeteries, battlefield markers, memorial plots"),
R("Not in dangerous places","Confirmed",["1.1","1.12"],"All hunt items","Anything a rescue would be needed for"),
R("Railroad tracks ruled out","Confirmed",["1.4"],"Site","Trackside, trestles, rail tunnels"),
R("More than one mile from anywhere he, family or friends live, work or own","Confirmed",["1.2"],"All hunt items","The family cabin's immediate mile, his own properties"),
R("Publicly accessible land; free; 24/7","Confirmed",["1.2","1.7","1.10"],"Final location","Fee areas, gated parks, hours-limited sites"),
R("Dogs welcome","Confirmed",["1.8"],"Final location","Places that bar dogs from the ground you must cross"),
R("No high-clearance vehicle; a low rider reaches the road","Confirmed",["1.3","3.9"],"Approach","Four-wheel-drive-only roads"),
R("Not near any man-made trail, 'a little ways off'","Said",["4.7"],"Site","Trailside caches, trailhead features"),
R("Not more than a mile from the car to figure out where it is","Confirmed",["3.5"],"Site","Backcountry more than a mile in"),
R("A hike is required","Said",["3.8"],"Site","Drive-up spots, roadside pullouts"),
R("Below 11,000 feet","Said",["4.17"],"Site","High summits and cirques above 11,000"),
R("Built on natural landscape; at most one clue with a man-made implication","Said",["4.8"],"Route","Routes that need two or more man-made features"),
R("No blaze cut on a tree; markers must survive natural forces","Said",["4.19"],"Site and route","Any solve that relies on a carved or painted mark"),
R("Something must be manipulated to see it; flashlight may help","Confirmed",["4.9"],"Site","Open-ground placements visible on approach"),
R("No significant clue visible from 15 feet","Confirmed",["4.6"],"Site","Spots marked by an obvious feature at the cache"),
R("You do not have to get your feet wet","Confirmed",["4.13"],"Route and site","Mid-stream rocks, wading approaches"),
R("Inside the printed map; the American West","Said",["8.6","3.6"],"Site","Anything off the map's edge"),
R("Not Colorado; not Oregon (complete elimination: no clues, no treasure)","Said",["8.2","8.3"],"Clues and site","Both states entirely. Note the transcript caveat in 8.2"),
R("Not in a pay park or fee area (hub-relayed, secondary)","Said",["4.18"],"Site","Fee-entry parks, unless the hub is wrong"),
R("Physical objects along the way","Confirmed",["4.4"],"Route","Routes with nothing tangible between clues"),
R("Something along the way is 'pivotal to your journey'","Confirmed",["4.14"],"Route","Routes with no confidence marker before the end"),
R("Only he knows; never returned since hiding","Confirmed",["4.1","13.3"],"Site","Anything requiring maintenance or a helper"),
]
P.append('<div class="page"><h2><span>B</span>Location filter</h2><p class="hint">Every rule he has stated about the final spot, the checkpoint or the route. Mark each candidate ✓ pass, ✕ fail, or ? unknown. One ✕ on a Confirmed row ends the candidate.</p>'+T(head,rows,"filter")+'</div>')

# C distance ledger
head=["Statement","Cite","Kind","What it fixes","Number"]
rows=[
["Walking distance from 'waters' silent flight' through 'past the Hole'",c("3.4"),"Length","2:2 to 2:3 is on foot","walking"],
["Not more than a mile to figure out where the treasure is",c("3.5"),"Length","Car to the point of knowing","≤ 1 mile"],
["A hike is required; length withheld",c("3.8"),"Length","There is a walk; not a pullout","> 0"],
["If you need many bottles of water you are going too far",c("3.7"),"Length","Short walk, not a day",""],
["Each clue is not meant to convey great distance",c("2.17"),"Spacing","Clue-to-clue gaps are small","small"],
["First clue to last in miles: impossible to answer given the structure",c("2.23"),"Structure","The clues are not a simple line",""],
["Distance from the first actionable clue to the treasure: forming the question may give the answer",c("2.22"),"Structure","The question contains a premise he rejects",""],
["Beginning to end, the poem creates 'some sort of shape'",c("2.16"),"Shape","The route draws a figure","shape"],
["Indiana Jones and National Treasure, offered instead of linear / points / hybrid",c("2.18"),"Shape","Leaned toward a device or construction, not a march",""],
["Backtracking: no if you knew the whole solution; yes in the natural progression",c("2.19"),"Shape","The path re-crosses itself for a first-timer",""],
["You do not need to be at the bride to identify her foot of three",c("6.12"),"Geometry","The foot is readable from a distance or a map",""],
["Her face to the place: not as far as many think",c("6.10"),"Length","Short",""],
["Bride to treasure: a matter of perspective",c("6.11"),"Length","Depends how you measure it",""],
["Return her face implies a physical rotation, technically",c("6.9"),"Geometry","Something turns","rotation"],
["Twenty degree; foot of three",c("2.9","6.12"),"Numbers","The only numbers in the poem; wordplay for numbers is in play","20, 3"],
["42 is relevant",c("9.22"),"Number","A number outside the poem matters","42"],
["Clock: the lower the number the better; 4:02 and 5:26 out; clocks are part of the cipher",c("11.7","10.6"),"Number","A clock reading feeds the cipher, not the map",""],
["Below 11,000 feet",c("4.17"),"Elevation","Ceiling","< 11,000 ft"],
["Within 75 miles of a Fenn search location, then walked back",c("8.9"),"Radius","Soft","75 mi"],
["Element of time is important",c("2.11"),"Time","Time matters somewhere in the solve",""],
["Vantage point involved, but no clue is necessarily about it",c("4.16"),"Geometry","A viewpoint exists in the solve",""],
["Checkpoint at least halfway through the clues; at least ten clues",c("7.1","2.1"),"Order","Checkpoint at clue 5 or later","≥ 5th clue"],
["Searchers within 200 feet of the checkpoint; within two miles of the treasure",c("14.3","14.2"),"Length","How close the crowd got","200 ft; 2 mi"],
]
P.append('<div class="page"><h2><span>C</span>Distance and geometry ledger</h2><p class="hint">Every statement of his that carries a length, an order, a direction or a shape. Use it to size a candidate route before you drive.</p>'+T(head,rows,"ledger")+'</div>')

# D element matrix
head=["Element","What he says it holds","Required to find it?","What it points to","Status","Cite"]
rows=[
["<b>The poem</b>","All essential clues; at least ten; consecutive; every line helpful; numbers hidden in words","Yes, the whole thing","An exact location when solved in full","Stanza 1, part of 2, part of 3 solved by others",c("2.1","2.2","2.5","2.9","3.3","14.5")],
["<b>The book</b>","Several hints sprinkled through the stories, not every story; descriptions that pertain to the area; photographs useful; the Tucker poem helpful; dedication layered and intentional; four points of the compass, 'the book is the best reference'","Written so everyone is on equal footing","The area, the person, the container","Read as a memoir first",c("9.10","9.11","9.12","9.18","9.19","9.4","9.17","9.8")],
["<b>The map</b>","The treasure is on it; he chose which landmarks are labeled; names, positions and elevations are the designer's and errors are unintentional","'A good primer'","The region","Useful early; still a primer later",c("8.6","8.7","9.20")],
["<b>Layer five</b>","'Has some bearing on the treasure hunt'","Not stated","Not stated","Undefined",c("9.2")],
["<b>The Netflix series</b>","At least five singular clues plus compound ones; two super obvious hints in an episode 2 or 3 scene without him; hints 'guide you in the book'; checkpoint not shown; Carl scene and Red Mountain clip hold nothing","Hints, not the solution","Back into the book","The two obvious hints were found by Sep 2025",c("11.2","11.3","9.1","7.4","11.4","11.5")],
["<b>The clock</b>","Part of the cipher; lower number is better; Roman numerals irrelevant; 4:02 and 5:26 out; 'a little uncanny'","Feeds the cipher","The cipher","Open",c("10.6","11.7","11.8")],
["<b>The songs</b>","Clues in the songs; one 'extremely definitive' clue; a hidden audio message is the technical clue","Technical clue not required","'The key to one direction lies in another'; not the azimuth","Technical clue solved by one person",c("10.7","10.5","10.9")],
["<b>The cipher</b>","MAGYAR; basic math; a nod to what the container is; gives no coordinates, state or region; 'who says it's in the book'","No","The container","Solved April 2026",c("10.4","10.3","10.8")],
["<b>The logo</b>","Angzarr, chosen and modified intentionally; 'has some meaning'","Not stated","Not stated","Open",c("9.6")],
["<b>42</b>","'The short answer is yes'; Hitchhiker's Guide","Not stated","Not stated","Open",c("9.22")],
["<b>Time</b>","'The element of time is important'; no time travel","Not stated","Not stated","Open",c("2.11","2.12")],
["<b>The checkpoint</b>","Placed and already there; topographic implication; halfway or later; pivotal","Practically yes: hard to get all the way without it","Confidence that you are on the path","Reached within 200 ft by some; no correct photo",c("7.2","7.1","7.3","14.3")],
["<b>The container</b>","An existing object with deliberate modifications; recognizable to anyone who read the book or saw the series; not a box; Saddleback briefcase is what carried it, not what holds it","Recognize it on sight","Itself","Guessed correctly by some",c("12.1","12.2","10.4")],
]
P.append('<div class="page"><h2><span>D</span>Element matrix</h2><p class="hint">What each part of the hunt is for, in his words. The Required column separates what you must solve from what only helps.</p>'+T(head,rows,"elements")+'</div>')

# E deductions
head=["#","Deduction","Chain of his statements","Confidence"]
rows=[
["1","Stanzas 1 to 3 are solvable from home even though stanza 2 describes walking. The walk is described before it is taken.","Boots on the ground required only at stanza four "+c("3.2")+" + a fair amount solvable from home "+c("3.1")+" + walking distance 2:2 to 2:3 "+c("3.4"),"High"],
["2","The checkpoint is at or after the fifth clue, so it is in stanza 3 or later.","At least ten clues "+c("2.1")+" + at least halfway when you reach it "+c("7.1")+" + consecutive order "+c("2.2"),"High"],
["3","The checkpoint is a natural feature that he added something to, or a placed thing set at a natural feature.","Both placed and already there "+c("7.2")+" + topographic implication "+c("7.2")+" + not something you need to worry about moving "+c("7.2")+" + hunt items obey the rules "+c("1.1"),"High"],
["4","The bride is a visible landform or object, identified by its gates first. Anything alive, or anything found before its gates, is wrong.","Not alive now, something visible "+c("6.4")+" + strange to find her without the gates "+c("6.7")+" + 'bride' is the right word "+c("2.25"),"High"],
["5","'Ursa east' names a thing that has an east, not a direction to walk.","Only Ursa East matters, no west Ursa "+c("6.1")+" + lowercase intentional "+c("6.2"),"High"],
["6","Stanza 3 is a construction on a map: a foot found at a distance, a rotation, and a short hop to the place.","Foot of three without being at the bride "+c("6.12")+" + rotation technically yes "+c("6.9")+" + face to place short "+c("6.10")+" + Indiana Jones / National Treasure "+c("2.18")+" + shape "+c("2.16"),"Medium"],
["7","'The place' (3:4) and 'the sacred space' (4:4) can be two spots, so the stanza 3 construction may deliver you somewhere that stanza 4 then moves you from.","Not necessarily the same "+c("6.13")+" + boots on the ground from stanza four "+c("3.2"),"Medium"],
["8","The one man-made implication, if it exists on your path, sits in stanza 4, because the Hole is cleared and stanza 3 is map work.","Hole not man-made "+c("5.1")+" + one clue may have a man-made implication depending on path "+c("4.8")+" + arcs question punted "+c("5.3")+" + exterior of a structure possible "+c("1.13"),"Medium"],
["9","The final spot is within a mile of a car, reached by a real but short walk, off any trail, and not obvious from 15 feet.","Not more than a mile "+c("3.5")+" + hike required "+c("3.8")+" + not near a trail "+c("4.7")+" + nothing visible from 15 feet "+c("4.6")+" + manipulate something to see it "+c("4.9"),"High"],
["10","Whether the treasure is buried does not change the solve; the poem delivers an exact location regardless.","'Wouldn't matter either way' "+c("4.10")+" + exact location on full solve "+c("3.3"),"High"],
["11","The cipher does not locate anything. Solving MAGYAR tells you what to look for, not where.","MAGYAR gives no coordinates, state or region "+c("10.4")+" + a nod to the container "+c("10.4")+" + not critical "+c("10.1"),"High"],
["12","The book describes the area without naming it, so terrain descriptions in the stories are the best filter for the first actionable clue.","Specific area not mentioned but descriptions pertain to it "+c("9.10")+" + hints sprinkled, not in every story "+c("9.12")+" + first actionable clue is 2:1 "+c("2.6"),"High"],
["13","The crowd's best position is 200 feet from the checkpoint and outside the kitchen-sized area, so the checkpoint is not at the treasure.","200 feet from the checkpoint "+c("14.3")+" + kitchen-sized area unreached "+c("7.8")+" + no correct checkpoint photo "+c("14.3"),"Medium"],
["14","Some part of the solve depends on time (a date, an hour, a season, an age), and it is not a rule about when to visit.","Element of time important "+c("2.11")+" + 24/7 access "+c("1.10")+" + clues stand the test of time "+c("1.18"),"Medium"],
["15","Spoken answers are less reliable than written ones, by his own account. Weight the rules, the FAQ and his posts above any podcast reply.","Prefers written responses to avoid errors "+c("15.3")+" + off-the-cuff forum replies can muddy the waters "+c("15.5"),"High"],
]
P.append('<div class="page"><h2><span>E</span>Deductions that follow from his words alone</h2><p class="hint">These are inferences, not statements. Each one shows the chain of his own statements it rests on, so you can break the chain if you disagree with a link.</p>'+T(head,rows,"deduce")+'</div>')

# F timeline
head=["Date","What he said","Solved so far (his count)","Cite"]
rows=[
["Mar 28 2025","Not found","—",c("14.1")],
["Apr 9 2025","Only he knows; 'who says it's a box'; cipher toward poem or book not specified","—",c("4.1","12.1","10.2")],
["Jun 21 2025","Within two miles; nobody at the checkpoint; nobody has said the cipher answer; no state ruled out; below 11,000 ft","Under two clues implied",c("14.2","8.1","4.17")],
["Aug 1 2025","Several have solved at least the first two clues; some within 200 ft of the checkpoint; zero correct photos","2 clues",c("14.3")],
["Sep 2025","Stanza 1 and at least part of stanza 2 solved; searchers 'quite close'; the two obvious Netflix hints found","Stanza 1 + part of 2",c("14.4","11.3")],
["Mar 28 2026","Bride identified; part of stanza 3 solved; at least six clues by the most advanced searcher; kitchen-sized area unreached; nobody way off, nobody uber close","6 clues",c("6.6","14.5","7.8")],
["Apr 2026","Cipher solved: MAGYAR; technical clue confirmed","Cipher done",c("10.4","10.5")],
["Jul 2026","Marked-book prize found, not the treasure; monthly Featured Question begins","—",c("14.7","14.9")],
]
P.append('<div class="page"><h2><span>F</span>Progress timeline</h2><p class="hint">What he says has been solved, in order. The gap between six clues and the kitchen-sized area is where the hunt stands.</p>'+T(head,rows,"timeline")+'''<div class="two"><div><h3>What "six clues" can cover</h3><p>With at least ten clues in consecutive order [2.1, 2.2], six solved clues starting at 2:1 [2.6] reach into stanza 3, which matches "part of stanza 3 solved" [14.5] and "bride identified" [6.6]. So the frontier is between the bride and the foot of three, or between the foot and the rotation. Nobody has reported the arcs.</p></div><div><h3>Use of the timeline</h3><p>If your solve places the checkpoint before the bride, it must explain how searchers were within 200 feet of the checkpoint in Aug 2025 [14.3] while stanza 3 was unsolved until 2026 [14.5]. If it places the checkpoint after the bride, the 200-foot group had solved more than he credited them with at the time. Either way, write down which.</p></div></div></div>''')

# G open questions
head=["What he declined","Cite","Why it was refused (his words)","A specific, not-on-the-nose way to ask","Your note"]
rows=[
["Does the Hole correspond to a hole-named place?",c("5.2"),"'An on the nose question'","Is the Hole something a fisherman would call a hole?",blank()],
["Is 'double arcs' the man-made clue? Natural or created?",c("5.3","5.4"),"Punted; 'he knows what he knows'","Were the double arcs there before you first visited the site?",blank()],
["Is 'double arcs' a bearing?",c("5.5"),"Punted","Do the double arcs stay in one place through the year?",blank()],
["Is the place in her face or her gaze?",c("6.14"),"No clarity","When her face is returned, does the place lie in front of her or behind her?",blank()],
["Is the checkpoint before or after boots on the ground?",c("7.5"),"Not specified; may reconsider","Can a searcher describe the checkpoint to you accurately without having stood at it?",blank()],
["Do you need to move rocks?",c("4.12"),"Punted","Is what must be manipulated lighter than the treasure?",blank()],
["Is it buried?",c("4.10"),"AI could use it","Skip; he has stated it does not change the solve",blank()],
["Are national parks ruled out?",c("4.20"),"Will not say yes or no","Is the final location on land where a dog may go off-trail on a leash?",blank()],
["Is 'cast your pole' a fishing pole?",c("2.26"),"Not specified","Would the person in 'I wait for you' be standing in water or beside it?",blank()],
["Can a Prius get within a mile?",c("4.22"),"Punted","Is the last road before the walk paved?",blank()],
["Does the hunt require a river crossing?",c("1.15"),"Not specified","Is every hunt item on the same side of every river it is near?",blank()],
["Does the site predate your Fenn searches?",c("4.21"),"Not specified","Did you know the site before 2010?",blank()],
["Which animal did you see?",c("8.12"),"Would affect the search area","Is the animal's range on the printed map limited to one state?",blank()],
["The one question nobody has asked",c("2.14"),"He cannot verbalize it","Work backward from 'the key to one direction lies in another' [10.5] and the element of time [2.11]",blank()],
]
P.append('<div class="page"><h2><span>G</span>Open-question ledger</h2><p class="hint">Everything he refused, with his stated reason. He answers questions that are specific but not on the nose [14.9]. The suggested rewordings are drafts for the monthly Featured Question, not facts.</p>'+T(head,rows,"ledger")+'</div>')

CSS='''
@page{size:Letter landscape; margin:.55in .6in .65in .6in}
body{font-family:"Bitstream Charter","Liberation Serif",Georgia,serif; font-size:8.6pt; line-height:1.35; color:#161a20; margin:0}
h1,h2,h3{font-family:"Liberation Sans",Arial,sans-serif}
.cover{padding-top:1.2in; max-width:7.5in; border-left:5pt solid #9a6e12; padding-left:.35in}
.eyebrow{font-family:"DejaVu Sans Mono"; font-size:8pt; letter-spacing:.2em; text-transform:uppercase; color:#9a6e12}
.cover h1{font-size:40pt; margin:6pt 0 8pt} .sub{font-size:11pt; color:#4a5361; margin:0 0 14pt}
.toc{font-size:10.5pt; padding-left:0; list-style:none} .toc li{padding:5pt 0; border-bottom:1pt dotted #c3cad5} .toc b{display:inline-block; width:22pt; color:#9a6e12; font-family:"Liberation Sans"}
.note{font-family:"DejaVu Sans Mono"; font-size:8pt; color:#7a8493; margin-top:14pt}
.page{page-break-before:always}
h2{font-size:17pt; text-transform:uppercase; margin:0 0 3pt; padding-bottom:4pt; border-bottom:2pt solid #9a6e12} h2 span{display:inline-block; background:#9a6e12; color:#fff; font-size:11pt; padding:1pt 7pt; border-radius:3pt; margin-right:8pt; vertical-align:middle}
h3{font-size:10.5pt; margin:8pt 0 3pt; color:#9a6e12; text-transform:uppercase; letter-spacing:.04em}
.hint{color:#5c6675; font-size:8.6pt; margin:2pt 0 6pt}
table.m{width:100%; border-collapse:collapse; font-size:8pt} .m th{font-family:"Liberation Sans"; font-size:6.8pt; letter-spacing:.06em; text-transform:uppercase; text-align:left; color:#9a6e12; border-bottom:1.2pt solid #9a6e12; padding:3pt 4pt; vertical-align:bottom} .m td{padding:4pt 4pt; border-bottom:.6pt solid #dfe3ea; vertical-align:top} .m tr{page-break-inside:avoid} .m thead{display:table-header-group}
.cite{font-family:"DejaVu Sans Mono"; font-size:6.4pt; color:#9a6e12; border:.6pt solid #d9c9a3; border-radius:2pt; padding:0 2pt; white-space:nowrap}
.fill{display:block; min-height:22pt; border:.7pt dashed #b9c0cb; border-radius:2pt}
.tag{font-family:"DejaVu Sans Mono"; font-size:6.4pt; letter-spacing:.06em; text-transform:uppercase; padding:1pt 3pt; border:.7pt solid; border-radius:2pt; white-space:nowrap} .tag.c{color:#1f8f5f; border-color:#1f8f5f} .tag.s{color:#9a6e12; border-color:#9a6e12} .tag.l{color:#2e86b5; border-color:#2e86b5} .tag.d{color:#7a8493; border-color:#a9b1bd}
.journey td:nth-child(1){width:9%} .journey td:nth-child(2){width:9%} .journey td:nth-child(3){width:22%} .journey td:nth-child(4){width:12%} .journey td:nth-child(5){width:9%} .journey td:nth-child(6){width:12%} .journey td:nth-child(7){width:14%} .journey td:nth-child(8){width:13%}
.filter td:nth-child(1){width:26%} .filter td:nth-child(4){width:13%} .filter td:nth-child(5){width:22%} .filter td:nth-child(n+6){width:8%}
.ledger td:nth-child(1){width:34%} .elements td:nth-child(1){width:10%} .elements td:nth-child(2){width:36%}
.deduce td:nth-child(1){width:3%} .deduce td:nth-child(2){width:36%} .deduce td:nth-child(4){width:8%}
.timeline td:nth-child(1){width:10%} .timeline td:nth-child(2){width:54%}
.two{display:grid; grid-template-columns:1fr 1fr; gap:18pt; margin-top:10pt} .two p{font-size:9pt}
'''
doc=f'<!doctype html><html><head><meta charset="utf-8"><title>Posey Solve Matrix</title><style>{CSS}</style></head><body>{"".join(P)}</body></html>'
open('matrix.html','w').write(doc); print('ok')
