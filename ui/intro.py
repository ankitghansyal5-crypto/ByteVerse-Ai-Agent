import json
import streamlit.components.v1 as components
from ui.reactor import ARC_CSS, ARC_HTML

INTRO_CSS = ARC_CSS + """
#bv-intro{--gold:#e0b04a;--red:#c1121f;position:fixed;inset:0;z-index:2147483000;background:#050505;
  overflow:hidden;font-family:'Orbitron','Rajdhani',sans-serif;color:#e6eaee;
  transition:background .9s ease,opacity .9s ease .3s;}
#bv-intro.open{background:transparent;}
#bv-intro.done{opacity:0;pointer-events:none;}
#bv-intro.fast{transition:opacity .35s ease;}
#bv-intro.reduced,#bv-intro.reduced *{transition:none!important;animation:none!important;}
#bv-intro.reduced .led{background:var(--gold);}
#bv-intro.reduced .sys em{opacity:1;}

/* ---------- armour doors (top and bottom) ---------- */
#bv-intro .door{position:absolute;left:0;width:100%;height:50.3%;z-index:2;
  transition:transform 1.3s cubic-bezier(.7,0,.2,1);will-change:transform;background-color:#2b3239;
  background-image:
    radial-gradient(circle,#e3e8ec 0 2px,#161a1e 3px 4px,transparent 5px),
    linear-gradient(180deg,rgba(255,255,255,.08),transparent 16%,rgba(0,0,0,.35)),
    repeating-linear-gradient(90deg,transparent 0 220px,rgba(0,0,0,.6) 220px 224px,rgba(255,255,255,.07) 224px 226px),
    linear-gradient(180deg,#646d76,#2d343b 52%,#171b20);
  background-size:80px 26px,auto,auto,auto;
  background-repeat:repeat-x,no-repeat,repeat,no-repeat;}
#bv-intro .door::after{content:'';position:absolute;left:0;right:0;height:13%;
  background:linear-gradient(90deg,#6e0a10,var(--red) 30%,#ff4a3d 50%,var(--red) 70%,#6e0a10);
  box-shadow:0 0 18px rgba(193,18,31,.55);}
#bv-intro .door.top{top:0;transform:translateY(-101%);border-bottom:4px solid var(--gold);
  background-position:0 calc(100% - 7px),0 0,0 0,0 0;box-shadow:0 10px 34px rgba(0,0,0,.85);}
#bv-intro .door.top::after{bottom:14%;}
#bv-intro .door.bottom{bottom:0;transform:translateY(101%);border-top:4px solid var(--gold);
  background-position:0 7px,0 0,0 0,0 0;box-shadow:0 -10px 34px rgba(0,0,0,.85);}
#bv-intro .door.bottom::after{top:14%;}
#bv-intro.s-plates .door.top,#bv-intro.s-plates .door.bottom{transform:translateY(0);}

/* ---------- side plates with hydraulic pistons ---------- */
#bv-intro .side{position:absolute;top:0;height:100%;width:9vw;min-width:70px;z-index:3;
  transition:transform 1.1s cubic-bezier(.6,0,.2,1) .2s;
  background:linear-gradient(90deg,#3b434b,#14181c);}
#bv-intro .side.left{left:0;transform:translateX(-101%);border-right:4px solid var(--red);}
#bv-intro .side.right{right:0;transform:translateX(101%);border-left:4px solid var(--red);
  background:linear-gradient(270deg,#3b434b,#14181c);}
#bv-intro.s-plates .side.left,#bv-intro.s-plates .side.right{transform:translateX(0);}

#bv-intro .piston{position:absolute;left:100%;height:16px;width:0;margin-top:-8px;
  border-radius:0 8px 8px 0;box-shadow:0 0 0 2px rgba(0,0,0,.5);
  background:linear-gradient(180deg,#f2f6f9,#8a949e 45%,#3a4149);
  transition:width 1.2s steps(10,end) .7s;}
#bv-intro .piston::before{content:'';position:absolute;left:0;top:-5px;width:56px;height:26px;
  background:#252c33;border:2px solid #56616c;}
#bv-intro .piston::after{content:'';position:absolute;right:-10px;top:-6px;width:12px;height:28px;
  background:linear-gradient(180deg,#f6dc8e,#b8892a);}
#bv-intro .side.right .piston{left:auto;right:100%;border-radius:8px 0 0 8px;}
#bv-intro .side.right .piston::before{left:auto;right:0;}
#bv-intro .side.right .piston::after{right:auto;left:-10px;}
#bv-intro.s-plates .piston{width:15vw;}

/* ---------- gold latches that snap onto the seam ---------- */
#bv-intro .latch{position:absolute;top:50%;width:70px;height:34px;margin-top:-17px;z-index:4;
  background:linear-gradient(180deg,#f6dc8e,#a8801f);border:2px solid #5b4510;border-radius:3px;
  opacity:0;transform:translateX(var(--from));
  transition:transform .35s cubic-bezier(.3,1.7,.5,1),opacity .1s;}
#bv-intro.s-locked .latch{opacity:1;transform:translateX(0);}
#bv-intro .seam{position:absolute;left:0;right:0;top:50%;height:2px;margin-top:-1px;z-index:4;
  background:var(--gold);box-shadow:0 0 14px var(--gold);opacity:0;transition:opacity .6s ease;}
#bv-intro.s-reactor .seam{opacity:.9;}

/* open: everything moves away (these rules come last on purpose) */
#bv-intro.open .door.top{transform:translateY(-101%);transition-duration:1.5s;}
#bv-intro.open .door.bottom{transform:translateY(101%);transition-duration:1.5s;}
#bv-intro.open .side.left{transform:translateX(-101%);}
#bv-intro.open .side.right{transform:translateX(101%);}
#bv-intro.open .piston{width:0;transition:width .5s ease;}
#bv-intro.open .latch,#bv-intro.open .seam{opacity:0;transition:opacity .3s;}

/* ---------- reactor (charges up from dark) ---------- */
#bv-intro .reactor-wrap{position:absolute;left:50%;top:44%;width:min(40vmin,360px);z-index:5;
  transform:translate(-50%,-50%) scale(.6);opacity:0;
  transition:transform 1.2s cubic-bezier(.2,.9,.2,1),opacity .8s ease;}
#bv-intro.s-reactor .reactor-wrap{transform:translate(-50%,-50%) scale(1);opacity:1;}
#bv-intro .reactor-wrap .arc{filter:brightness(.18) saturate(.3);transition:filter 2.6s ease-in;}
#bv-intro.s-reactor .reactor-wrap .arc{filter:none;}
#bv-intro.open .reactor-wrap{transform:translate(-50%,-50%) scale(1.8);opacity:0;
  transition:transform 1.2s ease,opacity .9s ease;}
#bv-intro .shock{position:absolute;inset:0;border-radius:50%;border:3px solid #fff;opacity:0;}
#bv-intro.s-flash .shock{animation:bvflash .9s ease-out;}
@keyframes bvflash{0%{opacity:.9;transform:scale(1);}100%{opacity:0;transform:scale(2.4);}}
@keyframes bvled{to{background:var(--gold);box-shadow:0 0 10px var(--gold);}}
@keyframes bvtext{to{opacity:1;}}

/* ---------- status readout ---------- */
#bv-intro .hud{position:absolute;left:50%;top:72%;width:min(440px,84vw);transform:translateX(-50%);
  z-index:6;opacity:0;transition:opacity .8s ease .3s;}
#bv-intro.s-reactor .hud{opacity:1;}
#bv-intro.open .hud{opacity:0;transition:opacity .4s;}
#bv-intro .pct{font-size:clamp(1.6rem,4vw,2.4rem);font-weight:700;color:var(--gold);text-align:center;
  text-shadow:0 0 14px rgba(224,176,74,.7);letter-spacing:.12em;}
#bv-intro .bar{height:6px;background:#12151a;border:1px solid #3a4149;margin:8px 0 14px;}
#bv-intro .bar i{display:block;height:100%;width:0;
  background:linear-gradient(90deg,var(--red),var(--gold),#fff);box-shadow:0 0 10px var(--gold);}
#bv-intro .sys{list-style:none;margin:0;padding:0;font-size:.72rem;letter-spacing:.18em;}
#bv-intro .sys li{display:flex;align-items:center;gap:10px;padding:3px 0;color:#98a3ad;}
#bv-intro .led{width:9px;height:9px;border-radius:50%;background:#3a4149;flex:none;}
#bv-intro .sys em{margin-left:auto;font-style:normal;color:var(--gold);opacity:0;}
#bv-intro.s-reactor .sys li:nth-child(1) .led,#bv-intro.s-reactor .sys li:nth-child(1) em{animation-delay:.6s;}
#bv-intro.s-reactor .sys li:nth-child(2) .led,#bv-intro.s-reactor .sys li:nth-child(2) em{animation-delay:1.2s;}
#bv-intro.s-reactor .sys li:nth-child(3) .led,#bv-intro.s-reactor .sys li:nth-child(3) em{animation-delay:1.8s;}
#bv-intro.s-reactor .sys li:nth-child(4) .led,#bv-intro.s-reactor .sys li:nth-child(4) em{animation-delay:2.4s;}
#bv-intro.s-reactor .sys .led{animation:bvled .3s both;}
#bv-intro.s-reactor .sys em{animation:bvtext .3s both;}

/* ---------- start screen and skip button ---------- */
#bv-gate{position:absolute;inset:0;z-index:20;display:flex;flex-direction:column;align-items:center;
  justify-content:center;gap:12px;background:radial-gradient(circle at 50% 40%,#1a0c0d,#040404 70%);
  transition:opacity .6s ease;}
#bv-gate.hide{opacity:0;pointer-events:none;}
#bv-gate .gate-arc{width:min(30vmin,220px);}
#bv-gate .arc{filter:brightness(.3) saturate(.4);}
#bv-gate h1{margin:10px 0 0;font-size:clamp(1.6rem,5vw,2.8rem);letter-spacing:.3em;font-weight:900;
  background:linear-gradient(180deg,#ffe9a8,#d4a537 48%,#8a6a1c);-webkit-background-clip:text;
  background-clip:text;color:transparent;}
#bv-gate p{margin:0;font-size:.75rem;letter-spacing:.45em;color:#c9d1d8;}
#bv-go{margin-top:18px;padding:12px 34px;background:linear-gradient(180deg,#a3121a,#5e0a0f);color:#fff;
  border:1px solid var(--gold);border-radius:3px;font:700 .9rem 'Orbitron',sans-serif;letter-spacing:.25em;
  cursor:pointer;transition:box-shadow .2s,transform .15s;}
#bv-go:hover{box-shadow:0 0 20px rgba(224,176,74,.8);transform:translateY(-1px);}
#bv-skip{position:absolute;right:22px;bottom:22px;z-index:30;background:rgba(10,12,15,.75);color:#aab4be;
  border:1px solid #3a4149;padding:8px 14px;font:500 .7rem 'Orbitron',sans-serif;letter-spacing:.2em;cursor:pointer;}
#bv-skip:hover{color:#fff;border-color:var(--gold);}

/* subtitle for the spoken greeting (lives outside the intro so it can outlast the doors) */
#bv-sub-float{position:fixed;left:50%;bottom:7%;transform:translateX(-50%);z-index:999991;
  width:min(720px,88vw);text-align:center;font:500 1.15rem 'Rajdhani',sans-serif;letter-spacing:.04em;
  color:#f5e7bd;text-shadow:0 2px 12px #000,0 0 14px rgba(224,176,74,.4);
  background:rgba(8,9,11,.6);border-bottom:2px solid #c1121f;padding:10px 16px;}
"""

INTRO_HTML = """
<div class="door top"></div>
<div class="door bottom"></div>
<div class="seam"></div>
<div class="side left"><div class="piston" style="top:28%"></div><div class="piston" style="top:70%"></div></div>
<div class="side right"><div class="piston" style="top:28%"></div><div class="piston" style="top:70%"></div></div>
<div class="latch" style="left:12%;--from:-90px"></div>
<div class="latch" style="left:27%;--from:90px;transition-delay:.18s"></div>
<div class="latch" style="left:66%;--from:-90px;transition-delay:.4s"></div>
<div class="latch" style="left:81%;--from:90px;transition-delay:.6s"></div>
<div class="reactor-wrap">__ARC__<div class="shock"></div></div>
<div class="hud">
<div class="pct"><span id="bv-pct">0</span>%</div>
<div class="bar"><i id="bv-bar"></i></div>
<ul class="sys">
<li><b class="led"></b>STRUCTURAL LOCKS<em>ENGAGED</em></li>
<li><b class="led"></b>HYDRAULICS<em>PRESSURISED</em></li>
<li><b class="led"></b>ARC CORE<em>STABLE</em></li>
<li><b class="led"></b>ANALYSIS ENGINE<em>ONLINE</em></li>
</ul>
</div>
<div id="bv-gate">
<div class="gate-arc">__ARC__</div>
<h1>BYTE-VERSE</h1>
<p>DATA INTELLIGENCE SYSTEM</p>
<button id="bv-go">INITIALIZE</button>
</div>
<button id="bv-skip">SKIP INTRO &#9656;</button>
""".replace("__ARC__", ARC_HTML)

INTRO_JS = """
if (document.getElementById('bv-intro')) { return; }

const root = document.createElement('div');
root.id = 'bv-intro';
root.innerHTML = HTML;
const reduced = CFG.reduced ||
  (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
if (reduced) { root.classList.add('reduced'); }
document.body.appendChild(root);

const $ = (sel) => root.querySelector(sel);
const timers = [];
let counter = null;
let started = false;
let finished = false;

const later = (fn, ms) => timers.push(setTimeout(fn, ms));
const hook = (name) => { try { if (window.bvAudio) { window.bvAudio.play(name); } } catch (e) {} };

function setProgress(v) {
  $('#bv-pct').textContent = v;
  $('#bv-bar').style.width = v + '%';
}

function runCounter() {
  const t0 = performance.now();
  const dur = 2600;
  counter = setInterval(() => {
    const p = Math.min(1, (performance.now() - t0) / dur);
    setProgress(Math.round(p * 100));
    if (p >= 1) { clearInterval(counter); }
  }, 40);
}

function removeSubtitle() {
  const f = document.getElementById('bv-sub-float');
  if (f) { f.remove(); }
}

function greet() {
  const h = new Date().getHours();
  const hello = (h >= 5 && h < 12) ? 'Good morning' : (h >= 12 && h < 17) ? 'Good afternoon' : 'Good evening';
  const full = hello + ", sir. All systems are online and operational. I'm ready when you are. Shall we take off?";
  removeSubtitle();
  const f = document.createElement('div');
  f.id = 'bv-sub-float';
  f.textContent = full;
  document.body.appendChild(f);
  setTimeout(removeSubtitle, 11500);
  try {
    if (window.bvAudio) {
      window.bvAudio.say([hello + ', sir.', 650, 'All systems are online and operational.', 250,
                          "I'm ready when you are.", 250, 'Shall we take off?']);
    }
  } catch (e) {}
}

function finish(fast) {
  if (finished) { return; }
  finished = true;
  timers.forEach(clearTimeout);
  if (counter) { clearInterval(counter); }
  document.removeEventListener('keydown', onKey);
  if (fast) {
    removeSubtitle();
    try { if (window.bvAudio) { window.bvAudio.silence(); } } catch (e) {}
  }
  try { sessionStorage.setItem('bv_intro_nonce', CFG.nonce); } catch (e) {}
  if (fast) { root.classList.add('fast'); }
  root.classList.add('open', 'done');
  setTimeout(() => root.remove(), reduced ? 100 : (fast ? 500 : 1600));
}

function onKey(e) { if (e.key === 'Escape') { finish(true); } }
document.addEventListener('keydown', onKey);

function start() {
  if (started || finished) { return; }
  started = true;
  try { if (window.bvAudio) { window.bvAudio.unlock(); } } catch (e) {}
  $('#bv-gate').classList.add('hide');
  hook('start');
  if (reduced) {
    root.classList.add('s-plates', 's-locked', 's-reactor', 's-flash');
    setProgress(100);
    later(() => greet(), 400);
    later(() => root.classList.add('open'), 900);
    later(() => finish(false), 1300);
    return;
  }
  later(() => { root.classList.add('s-plates'); hook('panels'); }, 300);
  later(() => hook('hydraulics'), 900);
  later(() => { root.classList.add('s-locked'); hook('lock'); }, 1900);
  later(() => { root.classList.add('s-reactor'); hook('charge'); runCounter(); }, 2300);
  later(() => { root.classList.add('s-flash'); hook('online'); greet(); }, 5000);
  later(() => { root.classList.add('open'); hook('open'); }, 5500);
  later(() => finish(false), 7200);
}

$('#bv-go').addEventListener('click', start);
$('#bv-skip').addEventListener('click', () => finish(true));
"""

# This small page runs inside Streamlit and hands the intro over to the main page.
BOOTSTRAP = """
<script>
(function () {
  const P = __PAYLOAD__;
  try {
    const win = window.parent;
    const pd = win.document;
    if (!P.enabled) { return; }
    if (win.sessionStorage.getItem('bv_intro_nonce') === P.nonce) { return; }
    if (pd.getElementById('bv-intro')) { return; }
    if (!pd.getElementById('bv-intro-style')) {
      const st = pd.createElement('style');
      st.id = 'bv-intro-style';
      st.textContent = P.css;
      pd.head.appendChild(st);
    }
    const s = pd.createElement('script');
    s.textContent = P.js;
    pd.body.appendChild(s);
    s.remove();
  } catch (e) { console.log('Byte-Verse intro could not start:', e); }
})();
</script>
"""


def play_intro(enabled=True, reduced_motion=False, nonce=0):
    """Show the startup animation once per browser tab (or again when nonce changes)."""
    cfg = {"enabled": enabled, "reduced": reduced_motion, "nonce": str(nonce)}
    js = ("(function(){\n"
          "const CFG = " + json.dumps(cfg) + ";\n"
          "const HTML = " + json.dumps(INTRO_HTML) + ";\n"
          + INTRO_JS + "\n})();")
    payload = {"enabled": enabled, "nonce": str(nonce), "css": INTRO_CSS, "js": js}
    components.html(BOOTSTRAP.replace("__PAYLOAD__", json.dumps(payload)), height=0)