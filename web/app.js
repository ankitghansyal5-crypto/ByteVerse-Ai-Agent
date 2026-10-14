// BYTEVERSE — Holographic AI Laboratory Controller
// AI Assistant: J.A.R.V.I.S.
// Project: BYTEVERSE | INTELLIGENCE BEYOND DATA
// Coordinates: Golden Neural Universe + Focal Telemetry Core + Real Data Analysis Agent

import { playIntro, stopSpeech } from './intro.js';

(() => {
  "use strict";

  // Global settings & preferences
  const settings = {
    voice: true,
    rate: 1.1,
    volume: 0.8,
    reduceMotion: false,
    muted: false
  };

  try {
    const saved = localStorage.getItem("bv_settings");
    if (saved) Object.assign(settings, JSON.parse(saved));
  } catch (e) {}

  function saveSettings() {
    try {
      localStorage.setItem("bv_settings", JSON.stringify(settings));
    } catch (e) {}
  }

  // Application State Machine
  const AppState = {
    IDLE: "idle",
    LISTENING: "listening",
    THINKING: "thinking",
    SPEAKING: "speaking",
    ANALYZING: "analyzing",
    SUCCESS: "success",
    ERROR: "error"
  };

  let currentState = AppState.IDLE;
  let activeDataset = null;
  let recognition = null;
  let isListening = false;
  let isSpeaking = false;

  /* -------------------------------------------------------------
     Three.js: Focal Neural Core Telemetry Monitor (#globe-canvas)
     Complements the background neural universe with focal telemetry
     ------------------------------------------------------------- */
  async function initFocalCore() {
    const canvas = document.getElementById("globe-canvas");
    const stage = document.getElementById("ai-stage");
    if (!canvas) return null;

    let THREE;
    try {
      THREE = await import('three');
    } catch (e) {
      console.warn("Three.js not available for focal core.", e);
      return null;
    }

    const renderer = new THREE.WebGLRenderer({
      canvas,
      alpha: true,
      antialias: true,
      powerPreference: "high-performance"
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(36, 1, 0.1, 50);
    camera.position.set(0, 0, 6.2);

    const group = new THREE.Group();
    scene.add(group);

    // 1. Concentric Holographic Telemetry Rings
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0xdfbb70,
      transparent: true,
      opacity: 0.55,
      wireframe: true
    });

    const r1 = new THREE.Mesh(new THREE.TorusGeometry(2.1, 0.015, 6, 100), ringMat);
    r1.rotation.set(0.4, 0.2, 0.1);
    group.add(r1);

    const r2 = new THREE.Mesh(new THREE.TorusGeometry(2.35, 0.01, 6, 100), ringMat.clone());
    r2.rotation.set(1.1, 0.8, -0.4);
    group.add(r2);

    const r3 = new THREE.Mesh(new THREE.TorusGeometry(2.55, 0.008, 6, 100), ringMat.clone());
    r3.rotation.set(-0.7, 0.5, 1.2);
    group.add(r3);

    // 2. Central Neural Core Sphere
    const coreMesh = new THREE.Mesh(
      new THREE.SphereGeometry(0.55, 32, 32),
      new THREE.MeshBasicMaterial({ color: 0xdfbb70, transparent: true, opacity: 0.8 })
    );
    group.add(coreMesh);

    const innerRuby = new THREE.Mesh(
      new THREE.SphereGeometry(0.28, 24, 24),
      new THREE.MeshBasicMaterial({ color: 0xb72e3c, transparent: true, opacity: 0.85 })
    );
    group.add(innerRuby);

    const coreLight = new THREE.PointLight(0xdfbb70, 2.5, 8);
    group.add(coreLight);

    // 3. Focal Synaptic Web Nodes
    const focalNodeCount = 90;
    const focalPositions = [];
    const phi = Math.PI * (Math.sqrt(5) - 1);
    for (let i = 0; i < focalNodeCount; i++) {
      const y = 1 - (i / (focalNodeCount - 1)) * 2;
      const rad = Math.sqrt(1 - y * y);
      const theta = phi * i;
      focalPositions.push(new THREE.Vector3(
        Math.cos(theta) * rad * 1.8,
        y * 1.8,
        Math.sin(theta) * rad * 1.8
      ));
    }

    const focalPoints = [];
    for (let i = 0; i < focalPositions.length; i++) {
      for (let j = i + 1; j < focalPositions.length; j++) {
        if (focalPositions[i].distanceTo(focalPositions[j]) < 0.95) {
          focalPoints.push(
            focalPositions[i].x, focalPositions[i].y, focalPositions[i].z,
            focalPositions[j].x, focalPositions[j].y, focalPositions[j].z
          );
        }
      }
    }

    const focalLineGeo = new THREE.BufferGeometry();
    focalLineGeo.setAttribute('position', new THREE.Float32BufferAttribute(focalPoints, 3));
    const focalLineMat = new THREE.LineBasicMaterial({
      color: 0xdfbb70,
      transparent: true,
      opacity: 0.45,
      blending: THREE.AdditiveBlending
    });
    const focalLines = new THREE.LineSegments(focalLineGeo, focalLineMat);
    group.add(focalLines);

    const focalNodeGeo = new THREE.BufferGeometry();
    focalNodeGeo.setFromPoints(focalPositions);
    const focalNodeMat = new THREE.PointsMaterial({
      color: 0xffe5a4,
      size: 0.08,
      transparent: true,
      opacity: 0.9,
      blending: THREE.AdditiveBlending
    });
    const focalNodesMesh = new THREE.Points(focalNodeGeo, focalNodeMat);
    group.add(focalNodesMesh);

    scene.add(new THREE.AmbientLight(0xffeedd, 0.4));

    function resize() {
      if (canvas.clientWidth && canvas.clientHeight) {
        const w = canvas.clientWidth;
        const h = canvas.clientHeight;
        renderer.setSize(w, h, false);
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
      }
    }

    const ro = new ResizeObserver(resize);
    ro.observe(canvas);
    window.addEventListener("resize", resize);
    resize();

    if (stage) stage.classList.add("stage-loaded");

    // Animation Loop for Focal Core
    let rotSpeed = 0.006;
    let targetRotSpeed = 0.006;

    function renderFocal(now) {
      requestAnimationFrame(renderFocal);
      const t = now / 1000;
      const motion = settings.reduceMotion ? 0.3 : 1.0;

      // Adapt core appearance to state
      let targetColor = 0xdfbb70;
      let breathAmp = 0.04;

      switch (currentState) {
        case AppState.IDLE:
          targetRotSpeed = 0.006;
          targetColor = 0xdfbb70;
          break;
        case AppState.LISTENING:
          targetRotSpeed = 0.016;
          targetColor = 0xf05b62; // soft amber-crimson
          breathAmp = 0.08;
          break;
        case AppState.THINKING:
        case AppState.ANALYZING:
          targetRotSpeed = 0.035;
          targetColor = 0xffe5a4;
          breathAmp = 0.09;
          break;
        case AppState.SPEAKING:
          targetRotSpeed = 0.012;
          targetColor = 0xffe5a4;
          breathAmp = 0.07;
          break;
        case AppState.SUCCESS:
          targetRotSpeed = 0.008;
          targetColor = 0x82c7a0;
          break;
        case AppState.ERROR:
          targetRotSpeed = 0.003;
          targetColor = 0xf05b62;
          break;
      }

      rotSpeed += (targetRotSpeed * motion - rotSpeed) * 0.05;

      group.rotation.y += rotSpeed;
      group.rotation.x = Math.sin(t * 0.35) * 0.06 * motion;

      const breath = 1 + breathAmp * Math.sin(t * 2.4) * motion;
      group.scale.setScalar(breath);
      coreMesh.scale.setScalar(1 + 0.1 * Math.sin(t * 3.5));

      r1.rotation.z += 0.01 * motion;
      r2.rotation.y -= 0.014 * motion;
      r3.rotation.x += 0.008 * motion;

      coreMesh.material.color.setHex(targetColor);
      coreLight.color.setHex(targetColor);

      renderer.render(scene, camera);
    }
    requestAnimationFrame(renderFocal);
  }

  /* -------------------------------------------------------------
     HUD & State Coordinator
     ------------------------------------------------------------- */
  function setState(state, message = null) {
    currentState = state;
    const aiStage = document.getElementById("ai-stage");
    const aiMode = document.getElementById("ai-mode");
    const aiMsg = document.getElementById("ai-message");
    const led = document.getElementById("led");
    const stateLabel = document.getElementById("state");
    const sysState = document.getElementById("sys-state");
    const neuralStatus = document.getElementById("neural-status");
    const procStatus = document.getElementById("processing-status");
    const voiceStatus = document.getElementById("voice-status");

    aiStage?.classList.remove("is-listening", "is-thinking", "is-speaking", "is-analyzing");

    if (led) led.className = "led";

    switch (state) {
      case AppState.IDLE:
        led?.classList.add(activeDataset ? "online" : "idle");
        if (aiMode) aiMode.textContent = activeDataset ? "ONLINE" : "STANDBY";
        if (stateLabel) stateLabel.textContent = activeDataset ? "DATASET ACTIVE" : "SYSTEM STANDBY";
        if (sysState) sysState.textContent = activeDataset ? "ACTIVE" : "STANDBY";
        if (neuralStatus) neuralStatus.textContent = activeDataset ? "SYNAPSE READY" : "DORMANT";
        if (procStatus) procStatus.textContent = "IDLE";
        if (voiceStatus) voiceStatus.textContent = settings.voice ? "READY" : "MUTED";
        if (aiMsg && message) aiMsg.textContent = message;
        break;

      case AppState.LISTENING:
        aiStage?.classList.add("is-listening");
        led?.classList.add("busy");
        if (aiMode) aiMode.textContent = "LISTENING";
        if (stateLabel) stateLabel.textContent = "CAPTURING AUDIO";
        if (sysState) sysState.textContent = "LISTENING";
        if (neuralStatus) neuralStatus.textContent = "AUDIO ACTIVE";
        if (procStatus) procStatus.textContent = "PROCESSING AUDIO";
        if (voiceStatus) voiceStatus.textContent = "CAPTURING";
        if (aiMsg) aiMsg.textContent = message || "Listening to your instructions, sir...";
        break;

      case AppState.THINKING:
        aiStage?.classList.add("is-thinking");
        led?.classList.add("busy");
        if (aiMode) aiMode.textContent = "THINKING";
        if (stateLabel) stateLabel.textContent = "QUERY PROCESSING";
        if (sysState) sysState.textContent = "COMPUTING";
        if (neuralStatus) neuralStatus.textContent = "SYNAPSE FIRING";
        if (procStatus) procStatus.textContent = "COMPUTING";
        if (aiMsg) aiMsg.textContent = message || "Evaluating statistical query and data tools...";
        break;

      case AppState.ANALYZING:
        aiStage?.classList.add("is-analyzing", "is-thinking");
        led?.classList.add("busy");
        if (aiMode) aiMode.textContent = "ANALYZING";
        if (stateLabel) stateLabel.textContent = "EXECUTING ANALYSIS";
        if (sysState) sysState.textContent = "EXECUTING TOOLS";
        if (neuralStatus) neuralStatus.textContent = "HIGH-SPEED NEURAL FLUX";
        if (procStatus) procStatus.textContent = "EXECUTING TOOLS";
        if (aiMsg) aiMsg.textContent = message || "Performing dataset calculation and profiling...";
        break;

      case AppState.SPEAKING:
        aiStage?.classList.add("is-speaking");
        led?.classList.add("online");
        if (aiMode) aiMode.textContent = "SPEAKING";
        if (stateLabel) stateLabel.textContent = "TRANSMITTING VOICE";
        if (voiceStatus) voiceStatus.textContent = "TRANSMITTING";
        if (neuralStatus) neuralStatus.textContent = "RESONANT SPEECH";
        if (aiMsg && message) aiMsg.textContent = message;
        break;

      case AppState.SUCCESS:
        led?.classList.add("online");
        if (aiMode) aiMode.textContent = "SUCCESS";
        if (stateLabel) stateLabel.textContent = "ANALYSIS COMPLETE";
        if (sysState) sysState.textContent = "TASK COMPLETE";
        if (neuralStatus) neuralStatus.textContent = "STABILIZED";
        if (procStatus) procStatus.textContent = "FINISHED";
        if (aiMsg && message) aiMsg.textContent = message;
        break;

      case AppState.ERROR:
        led?.classList.add("error");
        if (aiMode) aiMode.textContent = "ERROR";
        if (stateLabel) stateLabel.textContent = "EXCEPTION DETECTED";
        if (sysState) sysState.textContent = "ERROR";
        if (neuralStatus) neuralStatus.textContent = "ANOMALY DETECTED";
        if (procStatus) procStatus.textContent = "HALTED";
        if (aiMsg && message) aiMsg.textContent = message;
        break;
    }
  }

  /* -------------------------------------------------------------
     Logging & Voice Output
     ------------------------------------------------------------- */
  function addLog(text) {
    const log = document.getElementById("log");
    if (!log) return;
    const time = new Date().toLocaleTimeString();
    const item = document.createElement("div");
    item.className = "log-item";
    item.innerHTML = `<span class="log-time">[${time}]</span><span>${escapeHtml(text)}</span>`;
    log.appendChild(item);
    log.scrollTop = log.scrollHeight;
  }

  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function playSound(name) {
    try {
      if (window.BVAudio) window.BVAudio.play(name);
    } catch (e) {}
  }

  function speakText(text) {
    if (!settings.voice || settings.muted) return;
    if (!('speechSynthesis' in window)) return;

    speechSynthesis.cancel();
    const cleanText = text.replace(/[*_#`[\]()]/g, " ").replace(/\s+/g, " ").trim();
    if (!cleanText) return;

    const utterance = new SpeechSynthesisUtterance(cleanText);
    const voices = speechSynthesis.getVoices();
    const ukVoice = voices.find(v => /en[-_]GB/i.test(v.lang) && /(ryan|george|daniel|arthur|male)/i.test(v.name)) ||
                    voices.find(v => /en[-_]GB/i.test(v.lang)) ||
                    voices.find(v => /^en/i.test(v.lang));

    if (ukVoice) {
      utterance.voice = ukVoice;
      utterance.lang = ukVoice.lang;
    } else {
      utterance.lang = "en-GB";
    }

    utterance.rate = settings.rate;
    utterance.volume = settings.volume;
    utterance.pitch = 0.95;

    utterance.onstart = () => {
      isSpeaking = true;
      setState(AppState.SPEAKING, text);
    };

    utterance.onend = () => {
      isSpeaking = false;
      if (currentState === AppState.SPEAKING) {
        setState(AppState.IDLE);
      }
    };

    utterance.onerror = () => {
      isSpeaking = false;
      if (currentState === AppState.SPEAKING) {
        setState(AppState.IDLE);
      }
    };

    speechSynthesis.speak(utterance);
  }

  /* -------------------------------------------------------------
     Backend Data API Integration
     ------------------------------------------------------------- */
  async function loadTools() {
    try {
      const res = await fetch("/api/tools");
      if (!res.ok) throw new Error("Could not fetch tools");
      const tools = await res.json();
      const list = document.getElementById("tools");
      const sysEngine = document.getElementById("sys-engine");

      if (sysEngine) sysEngine.textContent = "FASTAPI ONLINE";
      if (!list) return;

      list.innerHTML = "";
      tools.forEach(t => {
        const li = document.createElement("li");
        li.innerHTML = `<b>${escapeHtml(t.name)}</b>: <span class="dim">${escapeHtml(t.about)}</span>`;
        list.appendChild(li);
      });
      addLog(`Connected to backend: ${tools.length} analysis tools active.`);
    } catch (e) {
      console.warn("Could not load tools:", e);
      const sysEngine = document.getElementById("sys-engine");
      if (sysEngine) sysEngine.textContent = "OFFLINE";
      addLog("Warning: Could not connect to analysis backend.");
    }
  }

  async function loadMemories() {
    try {
      const res = await fetch("/api/memory");
      if (!res.ok) return;
      const mems = await res.json();
      const list = document.getElementById("memory");
      if (!list) return;

      list.innerHTML = "";
      if (mems.length === 0) {
        list.innerHTML = '<li class="dim">No definitions saved yet.</li>';
        return;
      }

      mems.forEach(m => {
        const li = document.createElement("li");
        li.className = "mem-item";
        li.innerHTML = `
          <div>
            <b>${escapeHtml(m.key)}</b>: ${escapeHtml(m.value)}
            <div class="dim">${escapeHtml(m.kind)} (${escapeHtml(m.scope)})</div>
          </div>
          <button type="button" class="mem-btn-forget" data-key="${escapeHtml(m.key)}">Forget</button>
        `;
        list.appendChild(li);
      });

      // Wire up forget buttons
      list.querySelectorAll(".mem-btn-forget").forEach(btn => {
        btn.addEventListener("click", async (e) => {
          e.stopPropagation();
          const key = btn.dataset.key;
          try {
            await fetch(`/api/memory?key=${encodeURIComponent(key)}`, { method: "DELETE" });
            playSound("click");
            addLog(`Memory removed: ${key}`);
            loadMemories();
          } catch (err) {
            console.error("Failed to forget memory:", err);
          }
        });
      });
    } catch (e) {
      console.warn("Could not load memories:", e);
    }
  }

  /* -------------------------------------------------------------
     Dataset Handling & Upload
     ------------------------------------------------------------- */
  async function handleDatasetFile(file) {
    if (!file) return;

    const name = file.name;
    const msg = document.getElementById("upload-msg");
    if (msg) msg.textContent = "Uploading and analyzing dataset...";

    setState(AppState.ANALYZING, `Reading dataset: ${name}...`);
    playSound("charge");
    addLog(`Uploading file: ${name} (${(file.size / 1024).toFixed(1)} KB)...`);

    // Signal the 3D Neural Universe
    if (window.neuralUniverse) {
      window.neuralUniverse.onUploadStart();
    }

    try {
      const res = await fetch(`/api/upload?filename=${encodeURIComponent(name)}`, {
        method: "POST",
        body: file
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(errData.detail || "Upload failed");
      }

      const data = await res.json();
      activeDataset = data;
      renderDatasetDashboard(data);

      setState(AppState.SUCCESS, `Dataset ${data.filename} loaded successfully.`);
      playSound("chime");
      addLog(`Dataset verified: ${data.rows} rows, ${data.columns.length} columns.`);

      // Neural Universe success reaction
      if (window.neuralUniverse) {
        window.neuralUniverse.onUploadSuccess();
      }

      speakText(`Dataset loaded successfully, sir. I have profiled ${data.rows} rows and ${data.columns.length} columns. Ready for your analysis.`);

      // Enable askbar
      const qInput = document.getElementById("q");
      const sendBtn = document.getElementById("send");
      if (qInput) {
        qInput.disabled = false;
        qInput.placeholder = `Ask J.A.R.V.I.S. about ${data.filename}...`;
        qInput.focus();
      }
      if (sendBtn) sendBtn.disabled = false;

      // Update sidebar
      const sideDs = document.getElementById("side-dataset");
      const sysDs = document.getElementById("sys-dataset");
      if (sideDs) sideDs.innerHTML = `<b>${escapeHtml(data.filename)}</b><br><span class="dim">${data.rows} rows, ${data.columns.length} columns</span>`;
      if (sysDs) sysDs.textContent = data.filename;

      setTimeout(() => {
        if (currentState === AppState.SUCCESS) setState(AppState.IDLE);
      }, 3500);

    } catch (err) {
      console.error("Upload error:", err);
      setState(AppState.ERROR, `Error loading dataset: ${err.message}`);
      playSound("error");
      if (msg) msg.textContent = `Error: ${err.message}`;
      addLog(`Upload error: ${err.message}`);

      if (window.neuralUniverse) {
        window.neuralUniverse.onError();
      }

      speakText(`I encountered an issue loading the file: ${err.message}`);
      setTimeout(() => {
        if (currentState === AppState.ERROR) setState(AppState.IDLE);
      }, 4000);
    }
  }

  function renderDatasetDashboard(data) {
    const uploadSection = document.getElementById("upload");
    const dsPanel = document.getElementById("dataset-panel");
    const dsName = document.getElementById("ds-name");
    const dsSize = document.getElementById("ds-size");
    const mRows = document.getElementById("m-rows");
    const mCols = document.getElementById("m-cols");
    const mMissing = document.getElementById("m-missing");
    const mDups = document.getElementById("m-dups");
    const colsDiv = document.getElementById("cols");
    const previewDiv = document.getElementById("preview");
    const suggestDiv = document.getElementById("suggest");

    if (uploadSection) uploadSection.hidden = true;
    if (dsPanel) dsPanel.hidden = false;

    if (dsName) dsName.textContent = data.filename;
    if (dsSize) dsSize.textContent = `${(data.bytes / 1024).toFixed(1)} KB`;
    if (mRows) mRows.textContent = data.rows.toLocaleString();
    if (mCols) mCols.textContent = data.columns.length;
    if (mMissing) mMissing.textContent = data.missing_cells.toLocaleString();
    if (mDups) mDups.textContent = data.duplicates.toLocaleString();

    // Detected Columns
    if (colsDiv) {
      colsDiv.innerHTML = '<div class="col-tags">' + data.columns.map(c => `
        <span class="col-tag">
          <b>${escapeHtml(c.name)}</b>
          <span class="col-kind">${escapeHtml(c.kind)}</span>
        </span>
      `).join("") + '</div>';
    }

    // Data Preview Table
    if (previewDiv && data.preview && data.preview.columns) {
      let html = '<table><thead><tr>';
      data.preview.columns.forEach(c => {
        html += `<th>${escapeHtml(c)}</th>`;
      });
      html += '</tr></thead><tbody>';
      data.preview.data.forEach(row => {
        html += '<tr>';
        row.forEach(cell => {
          html += `<td>${escapeHtml(cell !== null ? cell : "—")}</td>`;
        });
        html += '</tr>';
      });
      html += '</tbody></table>';
      previewDiv.innerHTML = html;
    }

    // Suggested Queries
    if (suggestDiv && data.suggestions) {
      suggestDiv.innerHTML = '<div class="suggest-chips">' + data.suggestions.map(q => `
        <button type="button" class="suggest-btn" data-q="${escapeHtml(q)}">${escapeHtml(q)}</button>
      `).join("") + '</div>';

      suggestDiv.querySelectorAll(".suggest-btn").forEach(btn => {
        btn.addEventListener("click", () => {
          const qText = btn.dataset.q;
          const qInput = document.getElementById("q");
          if (qInput) qInput.value = qText;
          submitQuestion(qText);
        });
      });
    }
  }

  /* -------------------------------------------------------------
     Ask Question & Statistical Analysis Execution
     ------------------------------------------------------------- */
  async function submitQuestion(question) {
    question = (question || "").trim();
    if (!question || !activeDataset) return;

    const qInput = document.getElementById("q");
    const sendBtn = document.getElementById("send");
    if (qInput) {
      qInput.value = "";
      qInput.disabled = true;
    }
    if (sendBtn) sendBtn.disabled = true;

    // Render User Query Card
    renderFeedCard({
      role: "user",
      text: question
    });

    setState(AppState.ANALYZING, `Executing analysis: "${question}"`);
    playSound("charge");
    addLog(`Running statistical agent for query: "${question}"`);

    // Signal Neural Universe: activation wave
    if (window.neuralUniverse) {
      window.neuralUniverse.onQueryStart();
    }

    addHistoryItem(question);

    try {
      const res = await fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question })
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || "Query failed");
      }

      const result = await res.json();

      // Render Assistant Finding
      renderFeedCard({
        role: "assistant",
        text: result.answer,
        applied: result.applied,
        trace: result.trace,
        chart: result.chart
      });

      setState(AppState.SUCCESS, "Analysis complete.");
      playSound("chime");
      addLog("Analysis generated with verified data tools.");

      // Neural reactions
      if (window.neuralUniverse) {
        window.neuralUniverse.onQuerySuccess();
        if (result.chart) {
          window.neuralUniverse.onChartGenerated();
        }
        if (result.trace && result.trace.length > 0) {
          window.neuralUniverse.onToolExecuted();
        }
      }

      // Refresh memory list in case definitions were updated
      loadMemories();

      // Voice synthesis
      speakText(result.answer);

    } catch (err) {
      console.error("Ask query error:", err);
      setState(AppState.ERROR, `Analysis failed: ${err.message}`);
      playSound("error");

      if (window.neuralUniverse) {
        window.neuralUniverse.onError();
      }

      renderFeedCard({
        role: "error",
        text: `Analysis Error: ${err.message}`
      });
      addLog(`Analysis error: ${err.message}`);
      speakText(`I encountered an issue executing the analysis, sir.`);
    } finally {
      if (qInput) {
        qInput.disabled = false;
        qInput.focus();
      }
      if (sendBtn) sendBtn.disabled = false;
      setTimeout(() => {
        if (currentState === AppState.SUCCESS || currentState === AppState.ERROR) {
          setState(AppState.IDLE);
        }
      }, 4000);
    }
  }

  function renderFeedCard(data) {
    const feed = document.getElementById("feed");
    if (!feed) return;

    const card = document.createElement("div");
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    if (data.role === "user") {
      card.className = "feed-card msg-user";
      card.innerHTML = `
        <div class="feed-card-header">
          <span>YOU</span>
          <span class="feed-card-time">${time}</span>
        </div>
        <div class="feed-body">${escapeHtml(data.text)}</div>
      `;
    } else if (data.role === "error") {
      card.className = "feed-card msg-error";
      card.innerHTML = `
        <div class="feed-card-header">
          <span>J.A.R.V.I.S. / ERROR</span>
          <span class="feed-card-time">${time}</span>
        </div>
        <div class="feed-body">${escapeHtml(data.text)}</div>
      `;
    } else {
      card.className = "feed-card msg-assistant";

      let appliedHtml = "";
      if (data.applied && data.applied.length > 0) {
        appliedHtml = `
          <div class="applied-pill">
            <span>🧠 Memory applied:</span>
            <span>${data.applied.map(m => `${escapeHtml(m.key)} = ${escapeHtml(m.value)}`).join("; ")}</span>
          </div>
        `;
      }

      let traceHtml = "";
      if (data.trace && data.trace.length > 0) {
        traceHtml = `
          <details class="trace-block">
            <summary class="trace-summary">🔧 Analysis Tools Executed (${data.trace.length})</summary>
            <div class="trace-content">
              ${data.trace.map(step => `
                <div class="trace-step">
                  <div class="trace-step-name">${escapeHtml(step.tool)}</div>
                  <pre>${escapeHtml(JSON.stringify(step.inputs, null, 2))}</pre>
                </div>
              `).join("")}
            </div>
          </details>
        `;
      }

      const chartId = data.chart ? `chart-${Date.now()}` : null;
      let chartHtml = "";
      if (chartId) {
        chartHtml = `<div id="${chartId}" class="chart-box"></div>`;
      }

      card.innerHTML = `
        <div class="feed-card-header">
          <span>J.A.R.V.I.S.</span>
          <span class="feed-card-time">${time}</span>
        </div>
        <div class="feed-body">
          <p>${escapeHtml(data.text)}</p>
          ${appliedHtml}
          ${traceHtml}
          ${chartHtml}
        </div>
      `;

      // Plotly graph rendering
      if (data.chart && window.Plotly) {
        setTimeout(() => {
          const el = document.getElementById(chartId);
          if (el) {
            window.Plotly.newPlot(el, data.chart.data, data.chart.layout, {
              responsive: true,
              displayModeBar: false
            });
          }
        }, 50);
      }
    }

    feed.appendChild(card);
    card.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function addHistoryItem(question) {
    const historyList = document.getElementById("history");
    if (!historyList) return;

    if (historyList.querySelector(".dim")) {
      historyList.innerHTML = "";
    }

    const li = document.createElement("li");
    li.style.cursor = "pointer";
    li.textContent = question;
    li.title = "Click to run this question again";
    li.addEventListener("click", () => {
      const qInput = document.getElementById("q");
      if (qInput) qInput.value = question;
      submitQuestion(question);
    });

    historyList.prepend(li);
  }

  /* -------------------------------------------------------------
     Microphone Speech Recognition
     ------------------------------------------------------------- */
  function initSpeechRecognition() {
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    const btnMic = document.getElementById("btn-mic");

    if (!SpeechRec || !btnMic) {
      if (btnMic) btnMic.title = "Voice recognition not supported in this browser";
      return;
    }

    recognition = new SpeechRec();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onstart = () => {
      isListening = true;
      btnMic.classList.add("is-listening");
      setState(AppState.LISTENING, "Listening to your voice command...");
      playSound("pulse");
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      const qInput = document.getElementById("q");
      if (qInput) qInput.value = transcript;
      playSound("click");
      submitQuestion(transcript);
    };

    recognition.onerror = (event) => {
      console.warn("Speech recognition error:", event.error);
      isListening = false;
      btnMic.classList.remove("is-listening");
      setState(AppState.IDLE);
    };

    recognition.onend = () => {
      isListening = false;
      btnMic.classList.remove("is-listening");
      if (currentState === AppState.LISTENING) {
        setState(AppState.IDLE);
      }
    };

    btnMic.addEventListener("click", () => {
      if (isListening) {
        recognition.stop();
      } else {
        stopSpeech();
        try {
          recognition.start();
        } catch (e) {
          console.warn("Recognition start failed:", e);
        }
      }
    });
  }

  /* -------------------------------------------------------------
     DOM Initializer & Event Wiring
     ------------------------------------------------------------- */
  document.addEventListener("DOMContentLoaded", async () => {
    console.log("BYTEVERSE AI Laboratory initializing...");

    // 1. Launch the 3D Golden Neural Sphere & Cinematic Intro
    try {
      await playIntro();
    } catch (err) {
      console.warn("Intro bypassed:", err);
      document.body.classList.remove("pre");
      document.body.classList.add("ready");
    }

    // 2. Start Focal Telemetry Core in Stage
    initFocalCore();

    // 3. Connect Backend Data APIs
    loadTools();
    loadMemories();

    // 4. Hook up Speech Recognition
    initSpeechRecognition();

    // 5. Hook up File Upload Elements
    const fileInput = document.getElementById("file");
    const uploadArea = document.getElementById("upload");

    if (uploadArea && fileInput) {
      uploadArea.addEventListener("click", (e) => {
        if (e.target.closest(".btn-sample")) return;
        fileInput.click();
      });

      uploadArea.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          fileInput.click();
        }
      });

      uploadArea.addEventListener("dragover", (e) => {
        e.preventDefault();
        uploadArea.classList.add("dragover");
      });

      uploadArea.addEventListener("dragleave", () => {
        uploadArea.classList.remove("dragover");
      });

      uploadArea.addEventListener("drop", (e) => {
        e.preventDefault();
        uploadArea.classList.remove("dragover");
        const files = e.dataTransfer?.files;
        if (files && files.length > 0) {
          handleDatasetFile(files[0]);
        }
      });

      fileInput.addEventListener("change", (e) => {
        if (fileInput.files && fileInput.files.length > 0) {
          handleDatasetFile(fileInput.files[0]);
        }
      });
    }

    // Quick Sample Buttons
    document.querySelectorAll(".btn-sample").forEach(btn => {
      btn.addEventListener("click", async (e) => {
        e.stopPropagation();
        const sampleName = btn.dataset.sample;
        addLog(`Loading sample dataset: ${sampleName}...`);
        try {
          const res = await fetch(`/api/sample?name=${encodeURIComponent(sampleName)}`);
          if (!res.ok) throw new Error("Could not fetch sample file");
          const blob = await res.blob();
          const file = new File([blob], sampleName, { type: "text/csv" });
          handleDatasetFile(file);
        } catch (err) {
          console.error("Failed to load sample:", err);
          addLog(`Error loading sample: ${err.message}`);
        }
      });
    });

    // Replace Dataset Button
    const btnReplace = document.getElementById("btn-replace");
    if (btnReplace) {
      btnReplace.addEventListener("click", () => {
        const uploadSection = document.getElementById("upload");
        const dsPanel = document.getElementById("dataset-panel");
        if (uploadSection) uploadSection.hidden = false;
        if (dsPanel) dsPanel.hidden = true;
        playSound("click");
      });
    }

    // Askbar Form
    const askbar = document.getElementById("askbar");
    const qInput = document.getElementById("q");
    if (askbar) {
      askbar.addEventListener("submit", (e) => {
        e.preventDefault();
        if (qInput) submitQuestion(qInput.value);
      });
    }

    // Replay Intro Button
    const btnReplay = document.getElementById("btn-replay");
    if (btnReplay) {
      btnReplay.addEventListener("click", () => {
        stopSpeech();
        playSound("click");
        playIntro({ force: true });
      });
    }

    // Silence Voice Button
    const btnSilence = document.getElementById("btn-silence");
    if (btnSilence) {
      btnSilence.addEventListener("click", () => {
        settings.muted = !settings.muted;
        if (settings.muted) {
          stopSpeech();
          btnSilence.textContent = "UNMUTE VOICE";
          btnSilence.style.color = "var(--red-bright)";
          if (window.BVAudio) window.BVAudio.setMuted(true);
        } else {
          btnSilence.textContent = "SILENCE VOICE";
          btnSilence.style.color = "";
          if (window.BVAudio) window.BVAudio.setMuted(false);
          playSound("click");
        }
        saveSettings();
      });
    }

    // Settings Controls
    const setVoice = document.getElementById("set-voice");
    if (setVoice) {
      setVoice.checked = settings.voice;
      setVoice.addEventListener("change", (e) => {
        settings.voice = e.target.checked;
        saveSettings();
        if (!settings.voice) stopSpeech();
      });
    }

    const setRate = document.getElementById("set-rate");
    const outRate = document.getElementById("out-rate");
    if (setRate) {
      setRate.value = settings.rate;
      if (outRate) outRate.textContent = `${Number(settings.rate).toFixed(2)}x`;
      setRate.addEventListener("input", (e) => {
        settings.rate = parseFloat(e.target.value);
        if (outRate) outRate.textContent = `${settings.rate.toFixed(2)}x`;
        saveSettings();
      });
    }

    const setVolume = document.getElementById("set-volume");
    if (setVolume) {
      setVolume.value = settings.volume;
      setVolume.addEventListener("input", (e) => {
        settings.volume = parseFloat(e.target.value);
        if (window.BVAudio) window.BVAudio.setVolume(settings.volume);
        saveSettings();
      });
    }

    const setCalm = document.getElementById("set-calm");
    if (setCalm) {
      setCalm.checked = settings.reduceMotion;
      setCalm.addEventListener("change", (e) => {
        settings.reduceMotion = e.target.checked;
        document.body.classList.toggle("reduce-motion", settings.reduceMotion);
        if (window.neuralUniverse) {
          window.neuralUniverse.setReducedMotion(settings.reduceMotion);
        }
        saveSettings();
      });
    }

    addLog("BYTEVERSE laboratory ready. Awaiting dataset input.");
  });
})();
