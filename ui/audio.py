import json
import streamlit.components.v1 as components

AUDIO_CSS = """
#bv-audio-ui{position:fixed;left:14px;bottom:14px;z-index:999990;font-family:'Orbitron',sans-serif;}
#bv-au-btn{background:linear-gradient(180deg,#a3121a,#5e0a0f);color:#fff;border:1px solid #d4a537;
  border-radius:4px;padding:8px 12px;font:600 .68rem 'Orbitron',sans-serif;letter-spacing:.18em;cursor:pointer;}
#bv-au-btn:hover{box-shadow:0 0 14px rgba(212,165,55,.7);}
#bv-au-panel{position:absolute;bottom:44px;left:0;width:262px;background:rgba(10,12,15,.97);
  border:1px solid #d4a537;border-radius:6px;padding:12px 14px;color:#e6eaee;
  box-shadow:0 8px 28px rgba(0,0,0,.8);}
#bv-au-panel[hidden]{display:none;}
#bv-au-panel h4{margin:0 0 8px;font:700 .72rem 'Orbitron',sans-serif;letter-spacing:.2em;color:#d4a537;}
#bv-au-panel label{display:flex;align-items:center;gap:8px;font:500 .95rem 'Rajdhani',sans-serif;padding:3px 0;cursor:pointer;}
#bv-au-panel input[type=range]{width:100%;accent-color:#d4a537;}
#bv-au-panel input[type=checkbox]{accent-color:#d4a537;}
#bv-au-panel hr{border:0;border-top:1px solid #3a4149;margin:8px 0;}
#bv-au-panel button{background:#1a1e23;color:#e6eaee;border:1px solid #56616c;border-radius:3px;
  padding:5px 9px;margin:6px 6px 0 0;font:500 .78rem 'Rajdhani',sans-serif;cursor:pointer;}
#bv-au-panel button:hover{border-color:#d4a537;}
"""

AUDIO_JS = """
(function () {
if (window.bvAudio) { return; }

const KEY = 'bv_audio_v1';
const defaults = {muted: false, volume: 0.7,
  cats: {panels: true, hydraulics: true, reactor: true, startup: true, voice: true}};
let S = {muted: defaults.muted, volume: defaults.volume, cats: Object.assign({}, defaults.cats)};
try {
  const raw = localStorage.getItem(KEY);
  if (raw) {
    const o = JSON.parse(raw);
    S.muted = !!o.muted;
    if (typeof o.volume === 'number' && o.volume >= 0 && o.volume <= 1) { S.volume = o.volume; }
    S.cats = Object.assign({}, defaults.cats, o.cats || {});
  }
} catch (e) {}
function save() { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) {} }

/* ---------------- sound engine (everything is synthesized, no audio files) ---------------- */
let ctx = null, master = null, noiseBuf = null;

function ensure() {
  if (!ctx) {
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) { return false; }
    ctx = new AC();
    const comp = ctx.createDynamicsCompressor();
    master = ctx.createGain();
    master.gain.value = S.muted ? 0 : S.volume;
    master.connect(comp);
    comp.connect(ctx.destination);
    const len = ctx.sampleRate * 2;
    noiseBuf = ctx.createBuffer(1, len, ctx.sampleRate);
    const d = noiseBuf.getChannelData(0);
    for (let i = 0; i < len; i++) { d[i] = Math.random() * 2 - 1; }
  }
  if (ctx.state === 'suspended') { ctx.resume(); }
  return true;
}

function applyVol() {
  if (master) { master.gain.setTargetAtTime(S.muted ? 0 : S.volume, ctx.currentTime, 0.03); }
}

// filtered noise: hiss, whoosh, impact
function noise(t, dur, o) {
  o = Object.assign({type: 'bandpass', f0: 800, f1: 800, q: 1, g: 0.3, attack: 0.01, release: 0.1}, o || {});
  const src = ctx.createBufferSource();
  src.buffer = noiseBuf; src.loop = true;
  const fl = ctx.createBiquadFilter();
  fl.type = o.type; fl.Q.value = o.q;
  fl.frequency.setValueAtTime(o.f0, t);
  fl.frequency.exponentialRampToValueAtTime(Math.max(o.f1, 20), t + dur);
  const gn = ctx.createGain();
  const peakAt = t + Math.min(o.attack, dur * 0.5);
  gn.gain.setValueAtTime(0.0001, t);
  gn.gain.exponentialRampToValueAtTime(o.g, peakAt);
  gn.gain.setValueAtTime(o.g, Math.max(peakAt, t + dur - o.release));
  gn.gain.exponentialRampToValueAtTime(0.0001, t + dur);
  src.connect(fl); fl.connect(gn); gn.connect(master);
  src.start(t, Math.random()); src.stop(t + dur + 0.05);
}

// tone: hum, servo whine, clang, boom
function tone(t, dur, o) {
  o = Object.assign({type: 'sine', f0: 100, f1: 100, g: 0.3, attack: 0.01, lp: 0}, o || {});
  const osc = ctx.createOscillator();
  osc.type = o.type;
  osc.frequency.setValueAtTime(o.f0, t);
  osc.frequency.exponentialRampToValueAtTime(Math.max(o.f1, 20), t + dur);
  const gn = ctx.createGain();
  gn.gain.setValueAtTime(0.0001, t);
  gn.gain.exponentialRampToValueAtTime(o.g, t + Math.min(o.attack, dur * 0.5));
  gn.gain.exponentialRampToValueAtTime(0.0001, t + dur);
  let node = osc;
  if (o.lp) {
    const fl = ctx.createBiquadFilter();
    fl.type = 'lowpass'; fl.frequency.value = o.lp;
    osc.connect(fl); node = fl;
  }
  node.connect(gn); gn.connect(master);
  osc.start(t); osc.stop(t + dur + 0.05);
}

function thud(t) {
  tone(t, 0.35, {f0: 110, f1: 38, g: 0.6});
  noise(t, 0.12, {type: 'lowpass', f0: 900, f1: 200, g: 0.35, attack: 0.002, release: 0.08});
}

const SOUNDS = {
  start: function (t) {
    tone(t, 0.25, {type: 'square', f0: 900, f1: 300, g: 0.08, lp: 2500});
    tone(t, 0.5, {f0: 60, f1: 40, g: 0.3});
  },
  panels: function (t) {   // heavy plates sliding in, ending with a thud
    noise(t, 1.4, {f0: 150, f1: 900, q: 1.2, g: 0.35, attack: 0.2, release: 0.4});
    tone(t, 1.4, {type: 'sawtooth', f0: 48, f1: 70, g: 0.18, lp: 200, attack: 0.3});
    thud(t + 1.3);
  },
  hydraulics: function (t) {   // stepped pistons: hiss bursts plus servo whine
    for (let i = 0; i < 5; i++) {
      const s = t + i * 0.24;
      noise(s, 0.14, {type: 'highpass', f0: 3500, f1: 2500, q: 0.7, g: 0.22, attack: 0.01, release: 0.1});
      tone(s, 0.2, {type: 'sawtooth', f0: 220 + i * 35, f1: 300 + i * 45, g: 0.07, lp: 700, attack: 0.03});
    }
    noise(t + 1.25, 0.5, {type: 'highpass', f0: 4000, f1: 2000, g: 0.25, attack: 0.02, release: 0.4});
  },
  lock: function (t) {   // four metallic latches snapping shut
    [0, 0.18, 0.4, 0.6].forEach(function (d, i) {
      const s = t + d;
      tone(s, 0.3, {f0: 150, f1: 60, g: 0.5});
      noise(s, 0.06, {f0: 2200, f1: 1800, q: 3, g: 0.45, attack: 0.001, release: 0.04});
      tone(s, 0.35, {type: 'triangle', f0: 920 + i * 60, f1: 900 + i * 60, g: 0.12});
      tone(s, 0.3, {type: 'triangle', f0: 1470 + i * 70, f1: 1450 + i * 70, g: 0.08});
    });
  },
  charge: function (t) {   // reactor spooling up
    const d = 2.7;
    tone(t, d, {f0: 55, f1: 110, g: 0.35, attack: 0.4});
    tone(t, d, {type: 'sawtooth', f0: 80, f1: 700, g: 0.07, lp: 1800, attack: 0.6});
    tone(t, d, {f0: 200, f1: 1600, g: 0.08, attack: 1});
    noise(t, d, {f0: 300, f1: 4000, q: 0.8, g: 0.12, attack: 0.8, release: 0.3});
  },
  online: function (t) {   // core fully active: deep boom plus a bright ring
    tone(t, 1.6, {f0: 90, f1: 32, g: 0.8});
    noise(t, 0.9, {type: 'lowpass', f0: 3000, f1: 150, g: 0.5, attack: 0.01, release: 0.7});
    tone(t + 0.05, 1.4, {f0: 1320, f1: 1320, g: 0.07, attack: 0.02});
    tone(t + 0.05, 1.4, {f0: 1980, f1: 1980, g: 0.04, attack: 0.02});
  },
  open: function (t) {   // armour parting
    noise(t, 1.8, {f0: 900, f1: 140, q: 1.1, g: 0.38, attack: 0.25, release: 0.6});
    tone(t, 1.8, {type: 'sawtooth', f0: 70, f1: 42, g: 0.16, lp: 220, attack: 0.3});
    noise(t + 0.2, 0.6, {type: 'highpass', f0: 4000, f1: 2200, g: 0.25, attack: 0.02, release: 0.45});
    thud(t + 1.5);
  }
};
const CAT = {start: 'startup', online: 'startup', panels: 'panels', open: 'panels',
             hydraulics: 'hydraulics', lock: 'hydraulics', charge: 'reactor'};

function play(name) {
  if (S.muted || !SOUNDS[name]) { return; }
  if (CAT[name] && !S.cats[CAT[name]]) { return; }
  if (!ensure()) { return; }
  try { SOUNDS[name](ctx.currentTime + 0.02); } catch (e) { console.log('sound error', e); }
}

/* ---------------- voice (browser text-to-speech, British English) ---------------- */
let voices = [];
function loadVoices() { try { voices = speechSynthesis.getVoices() || []; } catch (e) {} }
if ('speechSynthesis' in window) { loadVoices(); speechSynthesis.onvoiceschanged = loadVoices; }

function pickVoice() {
  const uk = voices.filter(function (v) { return /en[-_]GB/i.test(v.lang); });
  const male = /(ryan|george|daniel|arthur|oliver|thomas|male)/i;
  return uk.find(function (v) { return male.test(v.name); }) || uk[0] ||
         voices.find(function (v) { return /^en/i.test(v.lang); }) || null;
}

let seq = 0;
function say(parts) {   // parts: text, or a list of texts and pauses (numbers, in milliseconds)
  if (S.muted || !S.cats.voice || !('speechSynthesis' in window)) { return; }
  if (!Array.isArray(parts)) { parts = [parts]; }
  const mine = ++seq;
  try { speechSynthesis.cancel(); } catch (e) {}
  const v = pickVoice();
  let i = 0;
  (function next() {
    if (mine !== seq || i >= parts.length) { return; }
    const p = parts[i++];
    if (typeof p === 'number') { setTimeout(next, p); return; }
    const u = new SpeechSynthesisUtterance(p);
    if (v) { u.voice = v; }
    u.lang = v ? v.lang : 'en-GB';
    u.rate = 0.9; u.pitch = 0.75;
    u.volume = Math.min(1, S.volume * 1.2);
    u.onend = next; u.onerror = next;
    speechSynthesis.speak(u);
  })();
}

function silence() {   // used when the intro is skipped
  seq++;
  try { speechSynthesis.cancel(); } catch (e) {}
  if (master) {
    master.gain.cancelScheduledValues(ctx.currentTime);
    master.gain.setValueAtTime(0, ctx.currentTime);
    setTimeout(applyVol, 2300);
  }
}

/* ---------------- floating audio control panel ---------------- */
function buildUI() {
  if (document.getElementById('bv-audio-ui')) { return; }
  const box = document.createElement('div');
  box.id = 'bv-audio-ui';
  box.innerHTML = `
    <button id="bv-au-btn"></button>
    <div id="bv-au-panel" hidden>
      <h4>AUDIO CONTROL</h4>
      <label><input type="checkbox" id="bv-au-mute"> Mute everything</label>
      <label>Volume</label>
      <input type="range" id="bv-au-vol" min="0" max="100">
      <hr>
      <label><input type="checkbox" data-cat="panels"> Panel movement</label>
      <label><input type="checkbox" data-cat="hydraulics"> Hydraulics and locks</label>
      <label><input type="checkbox" data-cat="reactor"> Reactor charging</label>
      <label><input type="checkbox" data-cat="startup"> System startup</label>
      <label><input type="checkbox" data-cat="voice"> AI voice</label>
      <hr>
      <button id="bv-au-tsound">Test sound</button><button id="bv-au-tvoice">Test voice</button>
    </div>`;
  document.body.appendChild(box);
  const btn = box.querySelector('#bv-au-btn');
  const panel = box.querySelector('#bv-au-panel');
  const mute = box.querySelector('#bv-au-mute');
  const vol = box.querySelector('#bv-au-vol');

  function refresh() {
    btn.textContent = S.muted ? '\\uD83D\\uDD07 MUTED' : '\\uD83D\\uDD0A AUDIO';
    mute.checked = S.muted;
    vol.value = Math.round(S.volume * 100);
    box.querySelectorAll('input[data-cat]').forEach(function (c) { c.checked = !!S.cats[c.dataset.cat]; });
  }
  btn.addEventListener('click', function () { panel.hidden = !panel.hidden; });
  mute.addEventListener('change', function () { S.muted = mute.checked; save(); applyVol(); refresh(); });
  vol.addEventListener('input', function () { S.volume = vol.value / 100; save(); applyVol(); });
  box.querySelectorAll('input[data-cat]').forEach(function (c) {
    c.addEventListener('change', function () { S.cats[c.dataset.cat] = c.checked; save(); });
  });
  box.querySelector('#bv-au-tsound').addEventListener('click', function () { play('lock'); });
  box.querySelector('#bv-au-tvoice').addEventListener('click', function () {
    say(['Good evening, sir.', 500, 'All systems are online and operational.']);
  });
  refresh();
}
buildUI();

// browsers keep audio locked until the first click; this unlocks it
document.addEventListener('pointerdown', function () {
  if (ctx && ctx.state === 'suspended') { ctx.resume(); }
});

window.bvAudio = {play: play, say: say, silence: silence, unlock: ensure, settings: S};
})();
"""

BOOT = """
<script>
(function () {
  const P = __PAYLOAD__;
  try {
    const win = window.parent;
    const pd = win.document;
    if (win.bvAudio) { return; }
    if (!pd.getElementById('bv-audio-style')) {
      const st = pd.createElement('style');
      st.id = 'bv-audio-style';
      st.textContent = P.css;
      pd.head.appendChild(st);
    }
    const s = pd.createElement('script');
    s.textContent = P.js;
    pd.body.appendChild(s);
    s.remove();
  } catch (e) { console.log('Byte-Verse audio could not start:', e); }
})();
</script>
"""


def install_audio():
    """Adds the sound engine, voice and the floating AUDIO panel to the page (once)."""
    payload = {"css": AUDIO_CSS, "js": AUDIO_JS}
    components.html(BOOT.replace("__PAYLOAD__", json.dumps(payload)), height=0)


def say(text):
    """Speak a short sentence in the assistant voice (the text is always shown on screen too)."""
    components.html("<script>try{window.parent.bvAudio.say(" + json.dumps(text) + ");}catch(e){}</script>",
                    height=0)