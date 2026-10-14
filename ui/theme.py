import streamlit as st
from ui.reactor import ARC_CSS, ARC_HTML

THEME_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@400;500;600&display=swap');

:root{
  --black:#0b0c0e; --gun:#14171b; --ti1:#d5dce2; --ti2:#8a949e; --ti3:#3a4149;
  --red:#c1121f; --red2:#8f0f14; --gold:#d4a537; --gold2:#f0c75e; --text:#e8ecef;
}

.stApp{
  background:
    radial-gradient(ellipse at 50% -10%, rgba(193,18,31,.24), transparent 55%),
    repeating-linear-gradient(45deg, rgba(255,255,255,.014) 0 2px, transparent 2px 6px),
    linear-gradient(180deg,#101216,#08090b);
  color:var(--text);
  font-family:'Rajdhani',sans-serif; font-size:1.06rem;
}

[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#1c2025 0%,#0c0e11 100%);
  border-right:2px solid var(--gold);
  box-shadow:4px 0 24px rgba(0,0,0,.65), inset -3px 0 0 rgba(193,18,31,.5);
}

h1,h2,h3,h4{font-family:'Orbitron',sans-serif!important;letter-spacing:.08em;color:var(--gold)!important;}

/* titanium glass panels */
[data-testid="stChatMessage"]{
  background:linear-gradient(145deg,rgba(62,69,77,.5),rgba(14,16,19,.85));
  border:1px solid rgba(184,192,200,.2);
  border-left:4px solid var(--red);
  border-radius:8px;
  backdrop-filter:blur(6px);
  box-shadow:0 4px 18px rgba(0,0,0,.5), inset 0 1px 0 rgba(255,255,255,.08);
  transition:border-color .3s ease, box-shadow .3s ease;
}
[data-testid="stChatMessage"]:hover{
  border-color:var(--gold); border-left-color:var(--red);
  box-shadow:0 0 18px rgba(212,165,55,.25);
}

.stButton>button{
  background:linear-gradient(180deg,#a3121a,#5e0a0f);
  color:#fff; border:1px solid var(--gold); border-radius:4px;
  font-family:'Orbitron',sans-serif; letter-spacing:.06em;
  transition:transform .15s ease, box-shadow .2s ease;
}
.stButton>button:hover{
  transform:translateY(-1px); box-shadow:0 0 16px rgba(212,165,55,.6);
  border-color:var(--gold2); color:#fff;
}

[data-testid="stExpander"]{
  background:rgba(10,12,15,.75); border:1px solid var(--ti3); border-radius:6px;
}
[data-testid="stFileUploader"] section{
  background:rgba(212,165,55,.05); border:1px dashed var(--gold);
}
[data-testid="stChatInput"]{
  border:1px solid rgba(212,165,55,.5); border-radius:8px; background:rgba(14,16,19,.9);
}

/* header */
.bv-header{display:flex;align-items:center;gap:26px;padding:8px 0 10px 0;}
.bv-arc{width:96px;flex:none;}
.bv-title{
  font-family:'Orbitron',sans-serif;font-weight:900;font-size:2.4rem;letter-spacing:.2em;
  background:linear-gradient(180deg,#ffe9a8,#d4a537 48%,#8a6a1c);
  -webkit-background-clip:text;background-clip:text;color:transparent;
  filter:drop-shadow(0 0 10px rgba(212,165,55,.3));
}
.bv-sub{color:var(--ti1);letter-spacing:.38em;font-size:.82rem;
  border-left:3px solid var(--red);padding-left:10px;margin-top:4px;}
.bv-rule{height:3px;margin:2px 0 14px 0;border-radius:2px;
  background:linear-gradient(90deg,var(--red),var(--gold) 45%,transparent);
  background-size:200% 100%;animation:bv-sheen 5s linear infinite;}
@keyframes bv-sheen{from{background-position:200% 0;}to{background-position:-200% 0;}}
@media (prefers-reduced-motion:reduce){.bv-rule{animation:none;}}
"""

HEADER = ('<div class="bv-header"><div class="bv-arc">' + ARC_HTML + '</div>'
          '<div><div class="bv-title">BYTE-VERSE</div>'
          '<div class="bv-sub">DATA INTELLIGENCE SYSTEM</div></div></div>'
          '<div class="bv-rule"></div>')


def apply_theme():
    st.markdown("<style>" + ARC_CSS + THEME_CSS + "</style>", unsafe_allow_html=True)


def header():
    st.markdown(HEADER, unsafe_allow_html=True)