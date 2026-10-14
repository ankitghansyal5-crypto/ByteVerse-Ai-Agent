# One reactor, drawn with layered CSS. Used by both the header and the intro.
ARC_CSS = """
.arc{position:relative;width:100%;aspect-ratio:1;border-radius:50%;}
.arc>div{position:absolute;border-radius:50%;pointer-events:none;}
.arc .a-bloom{inset:-35%;background:radial-gradient(circle closest-side,rgba(140,235,255,.38),rgba(90,200,255,.14) 45%,transparent 100%);animation:arc-pulse 2.8s ease-in-out infinite;}
.arc .a-housing{inset:0;
  background:radial-gradient(circle closest-side,transparent 80%,rgba(0,0,0,.6) 100%),
  conic-gradient(from 25deg,#d5dce2,#79838d 18%,#d5dce2 36%,#5a636c 55%,#cdd4da 72%,#7b858f 88%,#d5dce2);
  box-shadow:0 0 0 2px #090b0d,0 8px 24px rgba(0,0,0,.85),inset 0 2px 3px rgba(255,255,255,.6);}
.arc .a-bolts{inset:2.5%;background:repeating-conic-gradient(rgba(0,0,0,.8) 0 3deg,transparent 3deg 15deg);
  -webkit-mask:radial-gradient(circle closest-side,transparent 84%,#000 85%,#000 96%,transparent 97%);
  mask:radial-gradient(circle closest-side,transparent 84%,#000 85%,#000 96%,transparent 97%);}
.arc .a-recess{inset:11%;background:radial-gradient(circle closest-side,#04070a 55%,#161b20 100%);
  box-shadow:inset 0 0 18px #000,0 0 0 2px #444d56;}
.arc .a-coils{inset:18%;background:repeating-conic-gradient(from 6deg,#f6cf6a 0 22deg,#2a1c09 22deg 36deg);
  -webkit-mask:radial-gradient(circle closest-side,transparent 60%,#000 61%,#000 100%);
  mask:radial-gradient(circle closest-side,transparent 60%,#000 61%,#000 100%);
  filter:drop-shadow(0 0 4px rgba(255,190,80,.7));}
.arc .a-scan{inset:18%;mix-blend-mode:screen;animation:arc-spin 5s linear infinite;
  background:conic-gradient(from 0deg,transparent 0 290deg,rgba(255,255,255,.55) 340deg,transparent 360deg);
  -webkit-mask:radial-gradient(circle closest-side,transparent 60%,#000 61%,#000 100%);
  mask:radial-gradient(circle closest-side,transparent 60%,#000 61%,#000 100%);}
.arc .a-ring{inset:34%;filter:drop-shadow(0 0 5px #7be8ff);
  background:radial-gradient(circle closest-side,transparent 74%,#f2fdff 78%,#8eeaff 90%,transparent 100%);}
.arc .a-core{inset:40%;animation:arc-pulse 2.6s ease-in-out infinite;
  background:radial-gradient(circle closest-side,#fff 0%,#e4fcff 30%,#85ebff 62%,rgba(60,190,240,.5) 82%,transparent 100%);}
.arc .a-flare{inset:14%;mix-blend-mode:screen;animation:arc-pulse 2.6s ease-in-out infinite;
  background:radial-gradient(circle closest-side,rgba(190,246,255,.6),rgba(120,230,255,.16) 60%,transparent 100%);}
@keyframes arc-pulse{0%,100%{opacity:.82;transform:scale(.96);}50%{opacity:1;transform:scale(1.04);}}
@keyframes arc-spin{to{transform:rotate(360deg);}}
@media (prefers-reduced-motion:reduce){.arc>div{animation:none!important;}}
"""

ARC_HTML = ('<div class="arc"><div class="a-bloom"></div><div class="a-housing"></div>'
            '<div class="a-bolts"></div><div class="a-recess"></div><div class="a-coils"></div>'
            '<div class="a-scan"></div><div class="a-ring"></div><div class="a-core"></div>'
            '<div class="a-flare"></div></div>')