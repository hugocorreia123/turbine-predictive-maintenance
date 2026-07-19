"""Turbine — Predictive Maintenance — visual theme.

Palette, type and signature backdrop for this project's live demo.
Streamlit only. Pair with .streamlit/config.toml (base widget theme).
"""

import streamlit as st

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@600;700&family=IBM+Plex+Sans:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
h1, h2, h3 { font-family: 'Chakra Petch', sans-serif; letter-spacing: .01em; }

.stApp {
  background:
    url('data:image/svg+xml;utf8,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20width%3D%22320%22%20height%3D%22320%22%3E%3Cg%20stroke%3D%22%23F1A33C%22%20stroke-opacity%3D%220.06%22%20fill%3D%22none%22%3E%3Ccircle%20cx%3D%22160%22%20cy%3D%22160%22%20r%3D%22130%22%20stroke-dasharray%3D%222%2014%22/%3E%3Ccircle%20cx%3D%22160%22%20cy%3D%22160%22%20r%3D%2295%22%20stroke-dasharray%3D%222%2018%22/%3E%3C/g%3E%3Cg%20stroke%3D%22%23AEB6C2%22%20stroke-opacity%3D%220.05%22%20fill%3D%22none%22%3E%3Ccircle%20cx%3D%22160%22%20cy%3D%22160%22%20r%3D%2260%22%20stroke-dasharray%3D%221%2010%22/%3E%3C/g%3E%3C/svg%3E') repeat,
    radial-gradient(1000px 460px at 90% -10%, rgba(241,163,60,0.10), transparent 60%),radial-gradient(800px 460px at -10% 110%, rgba(45,212,191,0.05), transparent 55%),linear-gradient(180deg, #16181D 0%, #131519 100%);
  background-attachment: fixed;
}
[data-testid="stHeader"] { background: transparent; }

/* hero */
.tr-hero {
  border-radius: 18px;
  padding: 26px 30px 24px 30px;
  margin: 4px 0 14px 0;
  background: linear-gradient(135deg, rgba(31,35,43,0.94) 0%, rgba(22,24,29,0.94) 70%);
  border: 1px solid #F1A33C40;
  box-shadow: 0 12px 40px -18px #F1A33C59;
}
.tr-hero .eyebrow {
  font-family: 'IBM Plex Sans', sans-serif;
  font-size: .72rem; font-weight: 700; letter-spacing: .22em;
  text-transform: uppercase; color: #F1A33C; margin-bottom: 6px;
}
.tr-hero h1 {
  font-family: 'Chakra Petch', sans-serif;
  font-size: clamp(1.7rem, 3.2vw, 2.5rem); font-weight: 800;
  margin: 0 0 8px 0; padding: 0; color: #ECEDEE; line-height: 1.08;
}
.tr-hero .tag { color: #A6ACB8; font-size: 1.0rem; max-width: 72ch; margin: 0; }
.tr-hero .meta { color: #A6ACB8; opacity: .8; font-size: .8rem; margin-top: 10px; letter-spacing: .04em; }

/* metric cards */
[data-testid="stMetric"] {
  background: rgba(31, 35, 43, 0.60);
  border: 1px solid #ffffff1a;
  border-left: 3px solid #F1A33C;
  border-radius: 14px;
  padding: 14px 16px 12px 16px;
}
[data-testid="stMetricLabel"] p {
  text-transform: uppercase; letter-spacing: .07em;
  font-size: .74rem; font-weight: 700; color: #A6ACB8;
}
[data-testid="stMetricValue"] { font-family: 'Chakra Petch', sans-serif; color: #ECEDEE; }

/* tabs */
.stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid #ffffff1a; }
.stTabs [data-baseweb="tab"] {
  padding: 10px 16px; font-weight: 600; border-radius: 10px 10px 0 0;
}
.stTabs [aria-selected="true"] {
  color: #F1A33C !important;
  box-shadow: inset 0 -2px 0 #F1A33C;
  background: #F1A33C14;
}

/* buttons */
.stButton > button { border-radius: 12px; font-weight: 600; }
button[kind="primary"], [data-testid="stBaseButton-primary"] {
  background: linear-gradient(135deg, #F1A33C 0%, #D97E1A 100%);
  color: #1A1206; border: 0;
}
button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover {
  filter: brightness(1.08);
}

/* containers */
[data-testid="stExpander"] {
  border: 1px solid #ffffff1a; border-radius: 12px; background: rgba(31, 35, 43, 0.60);
}
[data-testid="stImage"] img { border-radius: 12px; border: 1px solid #ffffff1a; }
[data-testid="stCaptionContainer"], .stCaption { color: #A6ACB8; }
[data-testid="stSidebar"] { background: #14161B; border-right: 1px solid #ffffff1a; }
hr { border-color: #ffffff1a; }
[data-testid="stDataFrame"] { border: 1px solid #ffffff1a; border-radius: 12px; }

/* ---------- motion layer: Apple-quiet, minimal ---------- */
html { scroll-behavior: smooth; }

.tr-hero, [data-testid="stMetric"], [data-testid="stExpander"] {
  backdrop-filter: blur(12px) saturate(1.15);
  -webkit-backdrop-filter: blur(12px) saturate(1.15);
}

[data-testid="stMetric"], .stButton > button, [data-testid="stExpander"] {
  transition: transform .28s cubic-bezier(.22,.61,.36,1),
              box-shadow .28s cubic-bezier(.22,.61,.36,1),
              border-color .28s ease, filter .2s ease;
}
[data-testid="stMetric"]:hover {
  transform: translateY(-3px);
  border-color: #F1A33C66;
  box-shadow: 0 16px 38px -18px #F1A33C59;
}
.stButton > button:hover { transform: translateY(-1px); }
.stButton > button:active { transform: translateY(0) scale(.99); }

@media (prefers-reduced-motion: no-preference) {
  @keyframes tr-rise {
    from { opacity: 0; transform: translateY(14px); }
    to   { opacity: 1; transform: none; }
  }
  @keyframes tr-fade { from { opacity: 0; } to { opacity: 1; } }

  .tr-hero { animation: tr-rise .7s cubic-bezier(.22,.61,.36,1) both; }
  [data-testid="stMetric"] { animation: tr-rise .6s cubic-bezier(.22,.61,.36,1) both; }
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) [data-testid="stMetric"] { animation-delay: .06s; }
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"] { animation-delay: .14s; }
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(3) [data-testid="stMetric"] { animation-delay: .22s; }
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"] { animation-delay: .30s; }
  .stTabs { animation: tr-fade .5s ease-out both; animation-delay: .15s; }

  @supports (animation-timeline: view()) {
    [data-testid="stPlotlyChart"], [data-testid="stImage"],
    [data-testid="stExpander"], [data-testid="stDataFrame"] {
      animation: tr-rise .7s cubic-bezier(.22,.61,.36,1) both;
      animation-timeline: view();
      animation-range: entry 0% entry 38%;
    }
  }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; }
}
"""


def inject() -> None:
    """Apply the theme. Call once, right after st.set_page_config."""
    st.markdown(f"<style>{_CSS}</style>", unsafe_allow_html=True)


def hero(eyebrow: str, title: str, tag: str, meta: str = "") -> None:
    """The styled header banner. Replaces st.title + st.caption."""
    meta_html = f'<div class="meta">{meta}</div>' if meta else ""
    st.markdown(
        f'''<div class="tr-hero">
  <div class="eyebrow">{eyebrow}</div>
  <h1>{title}</h1>
  <p class="tag">{tag}</p>
  {meta_html}
</div>''',
        unsafe_allow_html=True,
    )
