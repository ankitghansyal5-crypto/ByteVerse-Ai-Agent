// BYTEVERSE — The Golden Neural Sphere & Cinematic Transition
// Hero Visual: Thousands of interconnected golden filaments, fine geometric lines,
// glowing nodes, flowing particles, and deep graphite space with subtle crimson undertones.
// On Initialize: Accelerates, camera flies forward through the outer filaments,
// enters the immersive neural universe, and reveals the ByteVerse workspace.
// Preserves exact J.A.R.V.I.S. identity, headings, intro text, and voice greeting.
const SEEN_KEY = 'bv_intro_seen';

/* ---------------- Voice Engine ---------------- */
let speechToken = 0;
function readSettings() {
  try {
    return { voice: true, rate: 1.1, volume: 0.8, ...JSON.parse(localStorage.getItem('bv_settings') || '{}') };
  } catch (e) {
    return { voice: true, rate: 1.1, volume: 0.8 };
  }
}

export function stopSpeech() {
  speechToken++;
  try {
    if ('speechSynthesis' in window) speechSynthesis.cancel();
  } catch (e) {}
}

export function speak(parts, onComplete) {
  const S = readSettings();
  if (!S.voice || !('speechSynthesis' in window)) {
    if (onComplete) onComplete();
    return;
  }
  const mine = ++speechToken;
  speechSynthesis.cancel();
  const voices = speechSynthesis.getVoices();
  const uk = voices.filter((v) => /en[-_]GB/i.test(v.lang));
  const v = uk.find((x) => /(ryan|george|daniel|arthur|oliver|thomas|male)/i.test(x.name)) ||
            uk[0] ||
            voices.find((x) => /^en/i.test(x.lang)) ||
            null;

  let i = 0;
  (function next() {
    if (mine !== speechToken || i >= parts.length) {
      if (mine === speechToken && onComplete) onComplete();
      return;
    }
    const p = parts[i++];
    if (typeof p === 'number') {
      setTimeout(next, p);
      return;
    }
    const u = new SpeechSynthesisUtterance(p);
    if (v) {
      u.voice = v;
      u.lang = v.lang;
    } else {
      u.lang = 'en-GB';
    }
    u.rate = S.rate;
    u.pitch = 0.95;
    u.volume = S.volume;
    u.onend = next;
    u.onerror = next;
    speechSynthesis.speak(u);
  })();
}

/* ---------------- 3D Libraries Loader ---------------- */
let libsPromise = null;
function loadLibs() {
  if (!libsPromise) {
    libsPromise = Promise.all([
      import('three'),
      import('three/addons/postprocessing/EffectComposer.js'),
      import('three/addons/postprocessing/RenderPass.js'),
      import('three/addons/postprocessing/UnrealBloomPass.js'),
      import('three/addons/postprocessing/OutputPass.js'),
    ]).then(([THREE, ec, rp, ub, op]) => ({
      THREE,
      EffectComposer: ec.EffectComposer,
      RenderPass: rp.RenderPass,
      UnrealBloomPass: ub.UnrealBloomPass,
      OutputPass: op.OutputPass,
    })).catch((e) => {
      console.warn('ByteVerse: WebGL Three.js libraries could not load.', e);
      return null;
    });
  }
  return libsPromise;
}
loadLibs();

/* ---------------- Intro Overlay HTML & CSS ---------------- */
const MARKUP = `
<div class="vig"></div>
<div class="bvi-status">
  <div><span>SYSTEM STATUS</span><b data-k="sys" class="off">STANDBY</b></div>
  <div><span>NEURAL CORE</span><b data-k="core" class="off">DORMANT</b></div>
  <div><span>POWER GRID</span><b data-k="power" class="off">STANDBY</b></div>
  <div><span>CONTAINMENT SEAL</span><b data-k="seal" class="off">OPEN</b></div>
  <div><span>J.A.R.V.I.S.</span><b data-k="ai" class="off">NOT INITIALIZED</b></div>
</div>
<button class="bvi-init" type="button"><i></i><span>INITIALIZE [SPACE]</span></button>
<div class="bvi-title">
  <div class="l1">INITIALIZATION COMPLETE</div>
  <h1 class="bv-brand-title"></h1>
  <div class="l3">ALL SYSTEMS OPERATIONAL</div>
</div>
<button class="bvi-skip" type="button">SKIP INTRO &#9656;</button>`;

const CSS = `
#bvi{position:fixed;inset:0;z-index:2147483000;background:transparent;overflow:hidden;color:#f1efe9;
  font-family:'Inter','Segoe UI',sans-serif;pointer-events:auto;transition:opacity .9s cubic-bezier(0.22, 1, 0.36, 1)}
#bvi.out{opacity:0;pointer-events:none}
#bvi.fast{transition-duration:.35s}
#bvi .vig{position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse at 50% 50%,transparent 40%,rgba(5,6,7,.85) 100%)}
#bvi .bvi-status{position:absolute;left:28px;top:26px;font:500 .72rem 'Oxanium',monospace;letter-spacing:.14em;line-height:2.1;color:#8da2b0;text-shadow:0 1px 8px #000}
#bvi .bvi-status div{display:flex;gap:16px}
#bvi .bvi-status span{min-width:142px}
#bvi .bvi-status b{font-weight:600;color:#f1efe9;transition:color .4s,text-shadow .4s}
#bvi .bvi-status b.on{color:#38d996;text-shadow:0 0 10px rgba(56,217,150,.65)}
#bvi .bvi-status b.warn{color:#e0b04a;text-shadow:0 0 10px rgba(224,176,74,.6)}
#bvi .bvi-status b.off{color:#f05b62;text-shadow:0 0 10px rgba(240,91,98,.6)}
#bvi button.bvi-init{position:absolute;left:50%;bottom:9%;transform:translateX(-50%);padding:16px 56px;cursor:pointer;
  background:rgba(17,17,15,.85);border:1px solid rgba(223,187,112,.6);border-radius:4px;color:#ffe5a4;
  font:700 .95rem 'Oxanium',sans-serif;letter-spacing:.38em;text-indent:.38em;backdrop-filter:blur(12px);
  box-shadow:0 0 28px rgba(223,187,112,.22);
  transition:opacity .5s,transform .5s,border-color .25s,letter-spacing .35s,box-shadow .25s}
#bvi button.bvi-init i{position:absolute;inset:-6px;pointer-events:none;transition:inset .3s ease;
  background:
   linear-gradient(#dfbb70,#dfbb70) top left/14px 2px no-repeat,linear-gradient(#dfbb70,#dfbb70) top left/2px 14px no-repeat,
   linear-gradient(#dfbb70,#dfbb70) top right/14px 2px no-repeat,linear-gradient(#dfbb70,#dfbb70) top right/2px 14px no-repeat,
   linear-gradient(#dfbb70,#dfbb70) bottom left/14px 2px no-repeat,linear-gradient(#dfbb70,#dfbb70) bottom left/2px 14px no-repeat,
   linear-gradient(#dfbb70,#dfbb70) bottom right/14px 2px no-repeat,linear-gradient(#dfbb70,#dfbb70) bottom right/2px 14px no-repeat}
#bvi button.bvi-init:hover,#bvi button.bvi-init:focus-visible{border-color:#ffe5a4;letter-spacing:.48em;box-shadow:0 0 38px rgba(223,187,112,.45);transform:translateX(-50%) translateY(-2px)}
#bvi button.bvi-init:hover i,#bvi button.bvi-init:focus-visible i{inset:-11px}
#bvi button.bvi-init.go{opacity:0;pointer-events:none;transform:translateX(-50%) translateY(18px)}
#bvi button.bvi-skip{position:absolute;right:24px;bottom:22px;padding:9px 16px;cursor:pointer;background:rgba(17,17,15,.75);
  color:#aaa79e;border:1px solid rgba(223,187,112,.25);border-radius:4px;font:600 .7rem 'Oxanium',sans-serif;letter-spacing:.2em;
  transition:color .2s,border-color .2s,box-shadow .2s}
#bvi button.bvi-skip:hover{color:#ffe5a4;border-color:#dfbb70;box-shadow:0 0 16px rgba(223,187,112,.2)}
#bvi .bvi-title{position:absolute;left:0;right:0;bottom:8%;text-align:center;pointer-events:none;padding:26px 0;
  background:radial-gradient(ellipse at 50% 55%,rgba(5,6,7,.82),transparent 75%)}
#bvi .l1{font:700 .85rem 'Oxanium',sans-serif;letter-spacing:.5em;color:#dfbb70;opacity:0;filter:blur(6px);
  transition:opacity .8s ease,letter-spacing 1.4s cubic-bezier(.2,.8,.2,1),filter .8s ease}
#bvi .l3{font:600 .8rem 'Oxanium',sans-serif;letter-spacing:.6em;color:#e4e6e4;opacity:0;filter:blur(6px);
  transition:opacity .8s ease,letter-spacing 1.4s cubic-bezier(.2,.8,.2,1),filter .8s ease}
#bvi .l1.show{opacity:1;letter-spacing:.32em;filter:none}
#bvi .l3.show{opacity:1;letter-spacing:.36em;filter:none}
#bvi h1.bv-brand-title{position:relative;display:inline-block;overflow:hidden;margin:10px 0;padding:0 .25em;
  font:800 clamp(2.4rem,6.5vw,4.5rem) 'Oxanium',sans-serif;letter-spacing:.28em;color:#ffe5a4;
  text-shadow:0 0 32px rgba(223,187,112,.5)}
#bvi h1 .c{display:inline-block;opacity:0;transform:translateY(.45em) scale(1.1);filter:blur(8px);
  transition:opacity .6s ease var(--d),transform .8s cubic-bezier(.2,.8,.2,1) var(--d),filter .6s ease var(--d)}
#bvi h1.show .c{opacity:1;transform:none;filter:none}
#bvi h1::after{content:'';position:absolute;top:0;bottom:0;width:35%;left:-50%;transform:skewX(-20deg);
  background:linear-gradient(100deg,transparent,rgba(255,245,215,.6),transparent)}
#bvi h1.show::after{animation:bvisweep 1.5s ease .8s 1 forwards}
@keyframes bvisweep{to{left:130%}}`;

function injectStyle() {
  if (document.getElementById('bvi-style')) return;
  const s = document.createElement('style');
  s.id = 'bvi-style';
  s.textContent = CSS;
  document.head.appendChild(s);
}

/* ---------------- 3D Golden Neural Universe Engine ---------------- */
let globalUniverse = null;

function buildNeuralUniverse(L, canvas) {
  const { THREE } = L;

  const W = () => Math.max(2, window.innerWidth);
  const H = () => Math.max(2, window.innerHeight);

  const renderer = new THREE.WebGLRenderer({
    canvas,
    antialias: true,
    alpha: false,
    powerPreference: 'high-performance'
  });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(W(), H(), false);
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.1;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x060708);
  scene.fog = new THREE.FogExp2(0x060708, 0.04);

  const camera = new THREE.PerspectiveCamera(40, W() / H(), 0.1, 100);
  camera.position.set(0, 0, 8.5); // Starts in hero view of golden sphere

  // Postprocessing Bloom
  const composer = new L.EffectComposer(renderer);
  composer.addPass(new L.RenderPass(scene, camera));
  const bloomPass = new L.UnrealBloomPass(new THREE.Vector2(W(), H()), 0.95, 0.45, 0.82);
  composer.addPass(bloomPass);
  if (L.OutputPass) composer.addPass(new L.OutputPass());

  /* ========================================================
     THE HERO VISUAL: GOLDEN NEURAL SPHERE
     Thousands of interconnected filaments, nodes & particles
     ======================================================== */
  const neuralGroup = new THREE.Group();
  scene.add(neuralGroup);

  const R = 3.6; // Sphere radius
  const NODE_COUNT = 1500;
  const nodePositions = [];
  const nodeBaseColors = [];
  const phi = Math.PI * (Math.sqrt(5) - 1); // Golden ratio angle

  // Generate surface & layered depth nodes on the sphere
  for (let i = 0; i < NODE_COUNT; i++) {
    const y = 1 - (i / (NODE_COUNT - 1)) * 2;
    const ringRad = Math.sqrt(1 - y * y);
    const theta = phi * i;

    // Layer depth: 75% on surface, 25% in interior volumetric layers
    let rad = R;
    if (i % 4 === 0) {
      rad = R * (0.45 + 0.5 * Math.random());
    } else if (i % 7 === 0) {
      rad = R * (0.8 + 0.3 * Math.random());
    }

    const x = Math.cos(theta) * ringRad * rad;
    const z = Math.sin(theta) * ringRad * rad;
    const pos = new THREE.Vector3(x, y * rad, z);
    nodePositions.push(pos);

    // Warm champagne-gold with occasional warm-white and amber accents
    const isBright = Math.random() < 0.2;
    const isCrimsonAccent = Math.random() < 0.05;
    if (isCrimsonAccent) {
      nodeBaseColors.push(0.72, 0.12, 0.18); // Subtle crimson undertone
    } else if (isBright) {
      nodeBaseColors.push(1.0, 0.96, 0.88); // Warm-white highlight
    } else {
      nodeBaseColors.push(0.88, 0.74, 0.44); // Champagne gold
    }
  }

  // 1. INTERCONNECTED GOLDEN FILAMENTS (LineSegments)
  const linePoints = [];
  const lineColors = [];
  const MAX_CONNECT_DIST = 1.18;

  for (let i = 0; i < nodePositions.length; i++) {
    const p1 = nodePositions[i];
    let count = 0;
    for (let j = i + 1; j < nodePositions.length; j++) {
      const p2 = nodePositions[j];
      const d = p1.distanceTo(p2);
      if (d < MAX_CONNECT_DIST && count < 4) {
        linePoints.push(p1.x, p1.y, p1.z, p2.x, p2.y, p2.z);
        // Base champagne-gold line color
        lineColors.push(0.88, 0.74, 0.44, 0.88, 0.74, 0.44);
        count++;
      }
    }
  }

  const lineGeo = new THREE.BufferGeometry();
  lineGeo.setAttribute('position', new THREE.Float32BufferAttribute(linePoints, 3));
  lineGeo.setAttribute('color', new THREE.Float32BufferAttribute(lineColors, 3));

  const lineMat = new THREE.LineBasicMaterial({
    vertexColors: true,
    transparent: true,
    opacity: 0.55,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  });
  const filaments = new THREE.LineSegments(lineGeo, lineMat);
  neuralGroup.add(filaments);

  // 2. GLOWING NEURAL NODES (Points)
  const nodeGeo = new THREE.BufferGeometry();
  nodeGeo.setFromPoints(nodePositions);
  nodeGeo.setAttribute('color', new THREE.Float32BufferAttribute(nodeBaseColors, 3));

  // Circular soft-glow texture
  const makeNodeTexture = () => {
    const c = document.createElement('canvas');
    c.width = c.height = 64;
    const g = c.getContext('2d');
    const gr = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    gr.addColorStop(0, 'rgba(255,255,255,1)');
    gr.addColorStop(0.3, 'rgba(255,232,168,0.9)');
    gr.addColorStop(0.7, 'rgba(223,187,112,0.25)');
    gr.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = gr;
    g.fillRect(0, 0, 64, 64);
    const t = new THREE.CanvasTexture(c);
    t.colorSpace = THREE.SRGBColorSpace;
    return t;
  };

  const nodeTexture = makeNodeTexture();
  const nodeMat = new THREE.PointsMaterial({
    map: nodeTexture,
    size: 0.12,
    vertexColors: true,
    transparent: true,
    opacity: 0.95,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    sizeAttenuation: true
  });
  const nodesMesh = new THREE.Points(nodeGeo, nodeMat);
  neuralGroup.add(nodesMesh);

  // 3. FINE GEOMETRIC GEODESIC LATTICE (Sophisticated structural AI lines)
  const icoGeo = new THREE.IcosahedronGeometry(R * 0.98, 2);
  const icoMat = new THREE.MeshBasicMaterial({
    color: 0xdfbb70,
    wireframe: true,
    transparent: true,
    opacity: 0.14,
    blending: THREE.AdditiveBlending
  });
  const icoMesh = new THREE.Mesh(icoGeo, icoMat);
  neuralGroup.add(icoMesh);

  const innerIcoGeo = new THREE.IcosahedronGeometry(R * 0.62, 1);
  const innerIcoMat = new THREE.MeshBasicMaterial({
    color: 0xe0b04a,
    wireframe: true,
    transparent: true,
    opacity: 0.18,
    blending: THREE.AdditiveBlending
  });
  const innerIcoMesh = new THREE.Mesh(innerIcoGeo, innerIcoMat);
  neuralGroup.add(innerIcoMesh);

  // 4. FLOWING SWARM OF PARTICLES
  const PARTICLE_COUNT = 900;
  const particlePositions = new Float32Array(PARTICLE_COUNT * 3);
  const particleVelocities = [];

  for (let i = 0; i < PARTICLE_COUNT; i++) {
    const r = R * (0.3 + 0.9 * Math.random());
    const theta = Math.random() * Math.PI * 2;
    const phiAngle = Math.acos(Math.random() * 2 - 1);
    particlePositions[i * 3] = r * Math.sin(phiAngle) * Math.cos(theta);
    particlePositions[i * 3 + 1] = r * Math.sin(phiAngle) * Math.sin(theta);
    particlePositions[i * 3 + 2] = r * Math.cos(phiAngle);

    particleVelocities.push({
      thetaSpeed: (0.15 + 0.3 * Math.random()) * (Math.random() < 0.5 ? 1 : -1),
      rad: r,
      theta,
      phiAngle
    });
  }

  const particleGeo = new THREE.BufferGeometry();
  particleGeo.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));
  const particleMat = new THREE.PointsMaterial({
    map: nodeTexture,
    size: 0.14,
    color: 0xffdf9b,
    transparent: true,
    opacity: 0.85,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  });
  const particleSystem = new THREE.Points(particleGeo, particleMat);
  neuralGroup.add(particleSystem);

  // 5. INNER ILLUMINATION (Soft ambient glow for neural filaments)
  const coreLight = new THREE.PointLight(0xffe5a4, 1.2, 14);
  neuralGroup.add(coreLight);

  const rimLight = new THREE.DirectionalLight(0xb72e3c, 1.2);
  rimLight.position.set(-8, -4, -6);
  scene.add(rimLight);

  const goldKeyLight = new THREE.DirectionalLight(0xfff4db, 1.8);
  goldKeyLight.position.set(6, 8, 8);
  scene.add(goldKeyLight);

  // 6. FINE ORBITAL RINGS WITH TICK MARKS
  const ringMat = new THREE.MeshBasicMaterial({
    color: 0xdfbb70,
    transparent: true,
    opacity: 0.4,
    wireframe: true
  });
  const orbit1 = new THREE.Mesh(new THREE.TorusGeometry(R * 1.15, 0.012, 6, 140), ringMat);
  orbit1.rotation.set(0.4, 0.2, 0.1);
  neuralGroup.add(orbit1);

  const orbit2 = new THREE.Mesh(new THREE.TorusGeometry(R * 1.28, 0.009, 6, 140), ringMat.clone());
  orbit2.rotation.set(1.1, 0.8, -0.4);
  neuralGroup.add(orbit2);

  const orbit3 = new THREE.Mesh(new THREE.TorusGeometry(R * 1.42, 0.007, 6, 140), ringMat.clone());
  orbit3.rotation.set(-0.7, 0.5, 1.2);
  neuralGroup.add(orbit3);

  // Ambient dust constellation extending into the infinite background
  const dustCount = 450;
  const dustPos = new Float32Array(dustCount * 3);
  for (let i = 0; i < dustCount; i++) {
    dustPos[i * 3] = (Math.random() - 0.5) * 36;
    dustPos[i * 3 + 1] = (Math.random() - 0.5) * 28;
    dustPos[i * 3 + 2] = (Math.random() - 0.5) * 32;
  }
  const dustGeo = new THREE.BufferGeometry();
  dustGeo.setAttribute('position', new THREE.BufferAttribute(dustPos, 3));
  const dustMat = new THREE.PointsMaterial({
    map: nodeTexture,
    size: 0.1,
    color: 0xdfbb70,
    transparent: true,
    opacity: 0.35,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  });
  const dustMesh = new THREE.Points(dustGeo, dustMat);
  scene.add(dustMesh);

  /* ========================================================
     ANIMATION DYNAMICS & TRANSITION STATE MACHINE
     ======================================================== */
  const STATE = {
    phase: 'initial', // 'initial', 'accelerating', 'passing', 'inside'
    targetCamZ: 8.5,
    camZ: 8.5,
    rotSpeed: 0.003,
    targetRotSpeed: 0.003,
    particleSpeedMul: 1.0,
    waveActive: 0,
    waveProgress: 0,
    crimsonAlert: 0,
    chartHighlight: 0,
  };

  let mouseX = 0, mouseY = 0;
  window.addEventListener('pointermove', (e) => {
    mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
    mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
  }, { passive: true });

  function onResize() {
    const w = W(), h = H();
    renderer.setSize(w, h, false);
    composer.setSize(w, h);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
  window.addEventListener('resize', onResize);

  let lastTime = performance.now();

  function tick(now) {
    const dt = Math.min(0.05, (now - lastTime) / 1000);
    lastTime = now;
    const t = now / 1000;

    // Smoothly interpolate rotation speed & camera Z
    STATE.rotSpeed += (STATE.targetRotSpeed - STATE.rotSpeed) * 0.06;
    STATE.camZ += (STATE.targetCamZ - STATE.camZ) * 0.045;

    // Camera position: approaches and enters the sphere smoothly
    if (STATE.phase === 'initial') {
      camera.position.set(mouseX * 0.4, -mouseY * 0.3, STATE.camZ);
      camera.lookAt(0, 0, 0);
    } else {
      camera.position.set(mouseX * 0.2, -mouseY * 0.15, STATE.camZ);
      camera.lookAt(0, 0, -STATE.camZ * 0.2);
    }

    // Sphere rotation
    neuralGroup.rotation.y += STATE.rotSpeed;
    neuralGroup.rotation.x = Math.sin(t * 0.3) * 0.08;

    // Organic breathing pulse
    const breath = 1 + 0.028 * Math.sin(t * 2.2);
    neuralGroup.scale.setScalar(breath);

    // Orbital rings drift
    orbit1.rotation.z += 0.01;
    orbit2.rotation.y -= 0.014;
    orbit3.rotation.x += 0.008;

    // Update flowing particle swarm
    const pArr = particleGeo.attributes.position.array;
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const v = particleVelocities[i];
      v.theta += v.thetaSpeed * dt * STATE.particleSpeedMul;
      v.phiAngle += Math.sin(t * 0.5 + i) * 0.01;

      pArr[i * 3] = v.rad * Math.sin(v.phiAngle) * Math.cos(v.theta);
      pArr[i * 3 + 1] = v.rad * Math.sin(v.phiAngle) * Math.sin(v.theta);
      pArr[i * 3 + 2] = v.rad * Math.cos(v.phiAngle);
    }
    particleGeo.attributes.position.needsUpdate = true;

    // Wave propagation (activation shockwaves during analysis)
    if (STATE.waveActive > 0) {
      STATE.waveProgress += dt * 2.8;
      const colors = lineGeo.attributes.color.array;
      for (let i = 0; i < linePoints.length / 3; i++) {
        const x = linePoints[i * 3];
        const y = linePoints[i * 3 + 1];
        const z = linePoints[i * 3 + 2];
        const dist = Math.sqrt(x * x + y * y + z * z);
        const waveDist = Math.abs(dist - STATE.waveProgress * 1.5);
        if (waveDist < 0.6) {
          const intensity = 1.0 - waveDist / 0.6;
          colors[i * 3] = 0.88 + intensity * 0.12;
          colors[i * 3 + 1] = 0.74 + intensity * 0.24;
          colors[i * 3 + 2] = 0.44 + intensity * 0.5;
        } else {
          colors[i * 3] = 0.88;
          colors[i * 3 + 1] = 0.74;
          colors[i * 3 + 2] = 0.44;
        }
      }
      lineGeo.attributes.color.needsUpdate = true;

      if (STATE.waveProgress > 3.0) {
        STATE.waveActive = 0;
        STATE.waveProgress = 0;
      }
    }

    // Crimson alert pulse (upon error)
    if (STATE.crimsonAlert > 0) {
      STATE.crimsonAlert = Math.max(0, STATE.crimsonAlert - dt * 0.8);
      coreLight.color.setHex(STATE.crimsonAlert > 0.1 ? 0xf05b62 : 0xffe5a4);
      nodeMat.color.setHex(STATE.crimsonAlert > 0.1 ? 0xf05b62 : 0xffffff);
    }

    // Chart highlight (when graph generated)
    if (STATE.chartHighlight > 0) {
      STATE.chartHighlight = Math.max(0, STATE.chartHighlight - dt * 0.6);
      orbit1.material.color.setHex(STATE.chartHighlight > 0.1 ? 0xffffff : 0xdfbb70);
      orbit2.material.color.setHex(STATE.chartHighlight > 0.1 ? 0xffeaad : 0xdfbb70);
    }

    composer.render();
  }

  /* ---------------- Universe Public Control API ---------------- */
  const api = {
    // Camera transition: accelerate -> zoom -> pass through filaments -> inside
    startTransition(onFilamentPass, onArrivedInside) {
      STATE.phase = 'accelerating';
      STATE.targetRotSpeed = 0.042; // Accelerate rotation
      STATE.particleSpeedMul = 4.2; // Rapid particle swirl

      // Phase 2: Move camera forward toward the sphere
      setTimeout(() => {
        STATE.targetCamZ = 3.6; // Approaches outer shell, expanding through perspective
      }, 1100);

      // Phase 3: Pass through the outer filaments
      setTimeout(() => {
        STATE.phase = 'passing';
        STATE.targetCamZ = -1.2; // Passes through filaments and enters inside!
        if (onFilamentPass) onFilamentPass();
      }, 3000);

      // Phase 4: Settle inside the neural universe
      setTimeout(() => {
        STATE.phase = 'inside';
        STATE.targetRotSpeed = 0.005; // Settles to majestic ambient drift
        STATE.particleSpeedMul = 1.2;
        if (onArrivedInside) onArrivedInside();
      }, 5200);
    },

    // Reset camera back to hero exterior view (for Replay Intro)
    resetToHero() {
      STATE.phase = 'initial';
      STATE.targetCamZ = 8.5;
      STATE.camZ = 8.5;
      camera.position.set(0, 0, 8.5);
      camera.lookAt(0, 0, 0);
      STATE.rotSpeed = 0.003;
      STATE.targetRotSpeed = 0.003;
      STATE.particleSpeedMul = 1.0;
    },

    // Instantly position camera inside the calm neural universe (for repeat visits / refresh)
    setInside() {
      STATE.phase = 'inside';
      STATE.camZ = -1.2;
      STATE.targetCamZ = -1.2;
      camera.position.set(0, 0, -1.2);
      camera.lookAt(0, 0, 0.24);
      STATE.rotSpeed = 0.005;
      STATE.targetRotSpeed = 0.005;
      STATE.particleSpeedMul = 1.2;
    },

    // Real Application Event Responses
    onUploadStart() {
      STATE.targetRotSpeed = 0.022;
      STATE.particleSpeedMul = 3.0;
    },
    onUploadSuccess() {
      STATE.targetRotSpeed = 0.006;
      STATE.particleSpeedMul = 1.2;
      STATE.waveActive = 1;
      STATE.waveProgress = 0;
    },
    onQueryStart() {
      STATE.targetRotSpeed = 0.028;
      STATE.particleSpeedMul = 3.5;
      STATE.waveActive = 1;
      STATE.waveProgress = 0;
    },
    onQuerySuccess() {
      STATE.targetRotSpeed = 0.006;
      STATE.particleSpeedMul = 1.2;
    },
    onChartGenerated() {
      STATE.chartHighlight = 1.0;
      STATE.waveActive = 1;
    },
    onToolExecuted() {
      STATE.waveActive = 1;
    },
    onError() {
      STATE.crimsonAlert = 1.0;
      STATE.targetRotSpeed = 0.004;
    },
    setReducedMotion(reduced) {
      STATE.targetRotSpeed = reduced ? 0.001 : 0.005;
      STATE.particleSpeedMul = reduced ? 0.4 : 1.2;
    }
  };

  // Start unified animation loop
  let rafId;
  function loop(now) {
    rafId = requestAnimationFrame(loop);
    tick(now);
  }
  rafId = requestAnimationFrame(loop);

  return api;
}

/* ---------------- Intro Controller ---------------- */
let introPromise = null;
let introCalls = 0;

export function playIntro(options = {}) {
  if (introPromise) return introPromise;
  const forced = options.force || introCalls++ > 0;
  introPromise = runIntro(forced).finally(() => {
    introPromise = null;
  });
  return introPromise;
}

async function runIntro(forced) {
  const calm = document.body.classList.contains('reduce-motion');
  let seen = false;
  try {
    seen = sessionStorage.getItem(SEEN_KEY) === '1';
  } catch (e) {}

  const bgCanvas = document.getElementById('bg-canvas');
  const L = await loadLibs();

  // Initialize unified 3D neural universe once if not yet active
  if (!globalUniverse && L && bgCanvas) {
    try {
      globalUniverse = buildNeuralUniverse(L, bgCanvas);
      window.neuralUniverse = globalUniverse;
    } catch (e) {
      console.warn('Could not build 3D neural universe:', e);
    }
  }

  // If already seen and not forced, reveal workspace immediately
  if (calm || (!forced && seen)) {
    if (globalUniverse) {
      globalUniverse.setInside(); // Immediately place camera inside calm universe
    }
    document.body.classList.remove('pre');
    document.body.classList.add('ready');
    return Promise.resolve();
  }

  injectStyle();
  const root = document.createElement('div');
  root.id = 'bvi';
  root.innerHTML = MARKUP;
  document.body.appendChild(root);
  document.documentElement.style.overflow = 'hidden';

  // If forced (Replay), reset camera back to hero exterior
  if (globalUniverse) {
    globalUniverse.resetToHero();
  }

  const q = (s) => root.querySelector(s);
  const setStatus = (k, text, tone) => {
    const b = q(`[data-k="${k}"]`);
    if (b) {
      b.textContent = text;
      b.className = tone || '';
    }
  };

  const h1 = q('h1.bv-brand-title');
  [...'BYTEVERSE'].forEach((ch, i) => {
    const s = document.createElement('span');
    s.className = 'c';
    s.style.setProperty('--d', i * 75 + 'ms');
    s.textContent = ch;
    h1.appendChild(s);
  });

  return new Promise((resolve) => {
    let phase = 'dormant';
    let finished = false;

    function finish(fast) {
      if (finished) return;
      finished = true;
      try {
        sessionStorage.setItem(SEEN_KEY, '1');
      } catch (e) {}

      document.removeEventListener('keydown', onKey);
      if (fast) {
        stopSpeech();
        root.classList.add('fast');
      }
      root.classList.add('out');

      // Reveal ByteVerse workspace smoothly inside the neural universe!
      document.body.classList.remove('pre');
      document.body.classList.add('ready');

      resolve();

      setTimeout(() => {
        root.remove();
        document.documentElement.style.overflow = '';
      }, fast ? 350 : 950);
    }

    const onKey = (e) => {
      if (e.key === 'Escape') {
        finish(true);
      } else if (e.key === ' ' || e.code === 'Space') {
        if (phase === 'dormant') {
          e.preventDefault();
          start();
        }
      }
    };
    document.addEventListener('keydown', onKey);
    q('.bvi-skip').addEventListener('click', () => finish(true));

    function start() {
      if (phase !== 'dormant') return;
      phase = 'running';
      q('.bvi-init').classList.add('go');

      if (window.BVAudio) window.BVAudio.play('start');

      const hello = (() => {
        const h = new Date().getHours();
        return h >= 5 && h < 12 ? 'Good morning' : h < 17 && h >= 12 ? 'Good afternoon' : 'Good evening';
      })();

      // 1. Initial status & sound
      setStatus('sys', 'INITIALIZING', 'warn');
      setStatus('core', 'CHARGING', 'warn');
      if (window.BVAudio) window.BVAudio.play('charge');

      // 2. Begin cinematic transition: Accelerate & fly camera through sphere
      if (globalUniverse) {
        globalUniverse.startTransition(
          // On passing outer filaments:
          () => {
            if (window.BVAudio) window.BVAudio.play('unlock');
            setStatus('power', 'ONLINE', 'on');
            setStatus('seal', 'ENGAGED', 'on');
          },
          // On arriving inside the neural universe:
          () => {
            if (window.BVAudio) window.BVAudio.play('lock');
            setStatus('sys', 'ONLINE', 'on');
            setStatus('core', 'STABLE', 'on');
            setStatus('ai', 'ONLINE', 'on');
          }
        );
      }

      // 3. Title reveal
      setTimeout(() => {
        q('.l1').classList.add('show');
      }, 5400);

      setTimeout(() => {
        h1.classList.add('show');
      }, 5800);

      setTimeout(() => {
        q('.l3').classList.add('show');
        if (window.BVAudio) window.BVAudio.play('chime');
      }, 6600);

      // 4. Exact JARVIS Voice Dialogue
      setTimeout(() => {
        speak([
          hello + ', sir.',
          350,
          'All systems are online and operational.',
          150,
          "I'm ready when you are.",
          150,
          'Shall we take off?'
        ]);
      }, 7400);

      // 5. Seamlessly fade out overlay and deploy the working workspace
      setTimeout(() => {
        finish(false);
      }, 9800);
    }

    q('.bvi-init').addEventListener('click', start);
    q('.bvi-init').focus({ preventScroll: true });
  });
}