// BYTEVERSE — Procedural Audio Engine
// Synthesizes sci-fi sound effects via Web Audio API without external audio files.

(() => {
  "use strict";

  let ctx = null;
  let master = null;
  let noiseBuf = null;

  const SETTINGS_KEY = "bv_audio_settings";
  const state = {
    muted: false,
    volume: 0.8
  };

  try {
    const saved = localStorage.getItem(SETTINGS_KEY);
    if (saved) {
      const parsed = JSON.parse(saved);
      if (typeof parsed.muted === "boolean") state.muted = parsed.muted;
      if (typeof parsed.volume === "number") state.volume = Math.max(0, Math.min(1, parsed.volume));
    }
  } catch (e) {}

  function save() {
    try {
      localStorage.setItem(SETTINGS_KEY, JSON.stringify(state));
    } catch (e) {}
  }

  function initContext() {
    if (!ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return null;
      ctx = new AudioCtx();

      const compressor = ctx.createDynamicsCompressor();
      compressor.threshold.setValueAtTime(-24, ctx.currentTime);
      compressor.knee.setValueAtTime(30, ctx.currentTime);
      compressor.ratio.setValueAtTime(12, ctx.currentTime);
      compressor.attack.setValueAtTime(0.003, ctx.currentTime);
      compressor.release.setValueAtTime(0.25, ctx.currentTime);

      master = ctx.createGain();
      master.gain.setValueAtTime(state.muted ? 0 : state.volume, ctx.currentTime);

      master.connect(compressor);
      compressor.connect(ctx.destination);

      // 2 seconds of white noise
      const len = ctx.sampleRate * 2;
      noiseBuf = ctx.createBuffer(1, len, ctx.sampleRate);
      const data = noiseBuf.getChannelData(0);
      for (let i = 0; i < len; i++) {
        data[i] = Math.random() * 2 - 1;
      }
    }

    if (ctx && ctx.state === "suspended") {
      ctx.resume().catch(() => {});
    }

    return ctx;
  }

  function noise(startTime, duration, opts) {
    if (!initContext()) return;
    const o = Object.assign({
      type: "bandpass",
      f0: 800,
      f1: 800,
      q: 1,
      gain: 0.25,
      attack: 0.01,
      release: 0.1
    }, opts);

    const src = ctx.createBufferSource();
    src.buffer = noiseBuf;
    src.loop = true;

    const filter = ctx.createBiquadFilter();
    filter.type = o.type;
    filter.Q.value = o.q;
    filter.frequency.setValueAtTime(Math.max(20, o.f0), startTime);
    filter.frequency.exponentialRampToValueAtTime(Math.max(20, o.f1), startTime + duration);

    const gain = ctx.createGain();
    const peakTime = startTime + Math.min(o.attack, duration * 0.5);
    gain.gain.setValueAtTime(0.0001, startTime);
    gain.gain.exponentialRampToValueAtTime(o.gain, peakTime);
    gain.gain.setValueAtTime(o.gain, Math.max(peakTime, startTime + duration - o.release));
    gain.gain.exponentialRampToValueAtTime(0.0001, startTime + duration);

    src.connect(filter);
    filter.connect(gain);
    gain.connect(master);

    src.start(startTime, Math.random());
    src.stop(startTime + duration + 0.05);
  }

  function tone(startTime, duration, opts) {
    if (!initContext()) return;
    const o = Object.assign({
      type: "sine",
      f0: 220,
      f1: 220,
      gain: 0.25,
      attack: 0.01,
      lowpass: 0
    }, opts);

    const osc = ctx.createOscillator();
    osc.type = o.type;
    osc.frequency.setValueAtTime(Math.max(20, o.f0), startTime);
    osc.frequency.exponentialRampToValueAtTime(Math.max(20, o.f1), startTime + duration);

    const gain = ctx.createGain();
    const peakTime = startTime + Math.min(o.attack, duration * 0.5);
    gain.gain.setValueAtTime(0.0001, startTime);
    gain.gain.exponentialRampToValueAtTime(o.gain, peakTime);
    gain.gain.exponentialRampToValueAtTime(0.0001, startTime + duration);

    let output = osc;
    if (o.lowpass) {
      const fl = ctx.createBiquadFilter();
      fl.type = "lowpass";
      fl.frequency.setValueAtTime(o.lowpass, startTime);
      osc.connect(fl);
      output = fl;
    }

    output.connect(gain);
    gain.connect(master);

    osc.start(startTime);
    osc.stop(startTime + duration + 0.05);
  }

  function thud(startTime) {
    tone(startTime, 0.35, { f0: 120, f1: 35, gain: 0.45 });
    noise(startTime, 0.14, { type: "lowpass", f0: 800, f1: 150, gain: 0.3, attack: 0.002, release: 0.08 });
  }

  const SOUND_LIBRARY = {
    start(t) {
      tone(t, 0.3, { type: "sine", f0: 440, f1: 880, gain: 0.15 });
      tone(t + 0.08, 0.4, { type: "sine", f0: 660, f1: 1320, gain: 0.12 });
      noise(t, 0.25, { type: "bandpass", f0: 1200, f1: 2800, q: 2, gain: 0.1 });
    },
    unlock(t) {
      tone(t, 0.25, { type: "sawtooth", f0: 180, f1: 340, gain: 0.12, lowpass: 800 });
      noise(t, 0.2, { type: "highpass", f0: 2400, f1: 1600, q: 1, gain: 0.15 });
      thud(t + 0.18);
    },
    armor(t) {
      noise(t, 0.8, { f0: 250, f1: 1200, q: 1.2, gain: 0.18, attack: 0.1, release: 0.2 });
      tone(t, 0.7, { type: "sawtooth", f0: 60, f1: 95, gain: 0.1, lowpass: 300 });
    },
    eyes(t) {
      tone(t, 0.5, { type: "sine", f0: 800, f1: 1800, gain: 0.16, attack: 0.04 });
      tone(t + 0.15, 0.4, { type: "sine", f0: 1600, f1: 2400, gain: 0.1, attack: 0.02 });
    },
    conduits(t) {
      tone(t, 0.15, { type: "triangle", f0: 420, f1: 640, gain: 0.1 });
      tone(t + 0.07, 0.18, { type: "triangle", f0: 640, f1: 980, gain: 0.08 });
    },
    charge(t) {
      tone(t, 1.8, { type: "sine", f0: 65, f1: 320, gain: 0.22, attack: 0.3 });
      tone(t + 0.2, 1.6, { type: "sawtooth", f0: 90, f1: 650, gain: 0.06, lowpass: 1200, attack: 0.4 });
      noise(t + 0.4, 1.2, { type: "bandpass", f0: 400, f1: 2800, q: 1.5, gain: 0.12, attack: 0.4 });
    },
    clamps(t) {
      noise(t, 0.35, { type: "highpass", f0: 3000, f1: 1500, q: 1.5, gain: 0.2 });
      thud(t + 0.2);
    },
    glassdrop(t) {
      noise(t, 0.4, { type: "bandpass", f0: 1600, f1: 900, q: 2, gain: 0.14 });
      tone(t + 0.05, 0.6, { type: "sine", f0: 1400, f1: 950, gain: 0.12 });
    },
    press(t) {
      noise(t, 0.3, { type: "lowpass", f0: 800, f1: 200, q: 1, gain: 0.25 });
      tone(t, 0.25, { type: "sine", f0: 180, f1: 75, gain: 0.2 });
    },
    lock(t) {
      tone(t, 0.2, { type: "sine", f0: 220, f1: 90, gain: 0.35 });
      tone(t + 0.04, 0.28, { type: "triangle", f0: 1100, f1: 880, gain: 0.12 });
      noise(t, 0.08, { f0: 2800, f1: 1200, q: 2, gain: 0.28, attack: 0.001, release: 0.05 });
    },
    chime(t) {
      // Golden completion chime
      tone(t, 0.6, { type: "sine", f0: 880, f1: 880, gain: 0.18, attack: 0.005 });
      tone(t + 0.08, 0.8, { type: "sine", f0: 1320, f1: 1320, gain: 0.14, attack: 0.005 });
      tone(t + 0.16, 1.2, { type: "sine", f0: 1760, f1: 1760, gain: 0.1, attack: 0.005 });
    },
    error(t) {
      // Restrained alert tone
      tone(t, 0.22, { type: "sawtooth", f0: 220, f1: 180, gain: 0.18, lowpass: 700 });
      tone(t + 0.18, 0.3, { type: "sawtooth", f0: 180, f1: 140, gain: 0.16, lowpass: 600 });
    },
    click(t) {
      tone(t, 0.03, { type: "triangle", f0: 1400, f1: 700, gain: 0.08, attack: 0.001 });
    },
    pulse(t) {
      tone(t, 0.12, { type: "sine", f0: 660, f1: 880, gain: 0.06, attack: 0.005 });
    }
  };

  const BVAudio = {
    play(soundName) {
      if (state.muted) return;
      const fn = SOUND_LIBRARY[soundName];
      if (!fn) return;
      try {
        const c = initContext();
        if (!c) return;
        fn(c.currentTime);
      } catch (e) {}
    },
    setVolume(vol) {
      state.volume = Math.max(0, Math.min(1, vol));
      if (master && ctx) {
        master.gain.setTargetAtTime(state.muted ? 0 : state.volume, ctx.currentTime, 0.03);
      }
      save();
    },
    setMuted(m) {
      state.muted = !!m;
      if (master && ctx) {
        master.gain.setTargetAtTime(state.muted ? 0 : state.volume, ctx.currentTime, 0.03);
      }
      save();
    },
    isMuted() {
      return state.muted;
    },
    getVolume() {
      return state.volume;
    }
  };

  window.BVAudio = BVAudio;
})();
