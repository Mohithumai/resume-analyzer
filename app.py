import streamlit as st
import pdfplumber
import math
import time
import json
import streamlit.components.v1 as components
from groq import Groq

# -----------------------------------
# PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="Resume Analyzer",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------
# SESSION STATE
# -----------------------------------

for _key in ["voice_q", "voice_transcript", "voice_eval"]:
    if _key not in st.session_state:
        st.session_state[_key] = None

# -----------------------------------
# LIVE PARTICLE BACKGROUND
# -----------------------------------

def render_particle_background():
    st.html("""
    <style>
        iframe {
            position: fixed !important;
            top: 0 !important; left: 0 !important;
            width: 100vw !important; height: 100vh !important;
            z-index: -1 !important;
            pointer-events: none !important;
        }
        .stApp, [data-testid="stApp"], [data-testid="stAppViewContainer"], .main, .block-container, header {
            background: transparent !important;
        }
        [data-testid="stSidebar"] {
            background: rgba(13,16,24,0.85) !important;
            backdrop-filter: blur(10px) !important;
        }
    </style>
    """)
    components.html("""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8">
    <style>body{margin:0;padding:0;background:#08090C;overflow:hidden;}#p{position:absolute;width:100%;height:100%;}</style>
    <script src="https://cdn.jsdelivr.net/npm/tsparticles@2/tsparticles.bundle.min.js"></script>
    </head><body><div id="p"></div>
    <script>
    tsParticles.load("p",{fpsLimit:60,particles:{color:{value:"#4DFFC3"},links:{color:"#4DFFC3",distance:150,enable:true,opacity:0.15,width:1},move:{enable:true,speed:0.8,outModes:{default:"bounce"}},number:{density:{enable:true,area:800},value:50},opacity:{value:0.4,animation:{enable:true,speed:1,minimumValue:0.1}},shape:{type:"circle"},size:{value:{min:1.5,max:3.5}}},interactivity:{events:{onHover:{enable:true,mode:"repulse"},resize:true},modes:{repulse:{distance:100,duration:0.4}}},detectRetina:true});
    </script></body></html>
    """, height=0)

render_particle_background()

# -----------------------------------
# GLOBAL CSS
# -----------------------------------

st.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Manrope:wght@300;400;500;600;700&display=swap');

:root {
    --bg: #08090C; --surface: #0D1018; --card: #12151E;
    --border: rgba(255,255,255,0.07); --border-hi: rgba(255,255,255,0.12);
    --accent: #4DFFC3; --warn: #FFBE57; --err: #FF6B6B;
    --text: #ECE9E2; --sub: #818DA0; --muted: #3A3F4E;
}

#MainMenu, footer, .stDeployButton { display: none !important; }
[data-testid="stToolbar"] { visibility: hidden !important; }

.block-container { padding-top: 2rem !important; max-width: 1040px !important; font-family: 'Manrope', sans-serif !important; }
[data-testid="stSidebar"] { border-right: 1px solid var(--border) !important; }
[data-testid="stSidebar"] * { font-family: 'Manrope', sans-serif !important; color: var(--sub) !important; }

p, div, li, label { font-family: 'Manrope', sans-serif !important; color: var(--text) !important; }
h1, h2, h3 { font-family: 'Syne', sans-serif !important; letter-spacing: -0.025em !important; color: var(--text) !important; }

.stButton > button {
    background: #1C2030 !important; color: #C8C4BC !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important; font-family: 'Syne', sans-serif !important; font-weight: 600 !important;
    font-size: 13px !important; letter-spacing: 0.05em !important; text-transform: uppercase !important;
    height: 44px !important; transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: #252B3D !important; color: #ECE9E2 !important;
    border-color: rgba(255,255,255,0.22) !important;
    transform: translateY(-1px) !important; box-shadow: 0 6px 20px rgba(0,0,0,0.35) !important;
}
.stButton > button:active { transform: translateY(1px) scale(0.98) !important; }

[data-testid="stFileUploader"] > div:first-child {
    background: rgba(18,21,30,0.85) !important; backdrop-filter: blur(8px) !important;
    border: 1px dashed var(--border-hi) !important; border-radius: 14px !important;
    padding: 2rem !important; transition: all 0.3s ease !important;
}
[data-testid="stFileUploader"] > div:first-child:hover { border-color: var(--accent) !important; }
[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] [data-testid="stWidgetLabel"],
[data-testid="stFileUploaderDropzoneInstructions"] { display: none !important; }
[data-testid="stFileUploaderDropzone"] * { font-size: 0 !important; color: transparent !important; }
[data-testid="stFileUploaderDropzone"] button {
    display: inline-flex !important; align-items: center !important; justify-content: center !important;
    min-width: 120px !important; min-height: 38px !important; font-size: 0 !important; color: transparent !important;
    background: rgba(77,255,195,0.1) !important; border: 1px solid rgba(77,255,195,0.3) !important;
    border-radius: 8px !important; padding: 8px 22px !important; cursor: pointer !important; transition: all 0.2s ease !important;
}
[data-testid="stFileUploaderDropzone"] button:hover { background: rgba(77,255,195,0.18) !important; transform: translateY(-2px) !important; }
[data-testid="stFileUploaderDropzone"] button::after {
    content: "Browse Files"; font-size: 13px !important; font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important; letter-spacing: 0.06em !important; color: #4DFFC3 !important; text-transform: uppercase !important;
}
[data-testid="stFileUploader"] small { color: var(--sub) !important; }

.stSpinner > div > div { border-top-color: var(--accent) !important; }

textarea {
    background: rgba(13,16,24,0.85) !important; backdrop-filter: blur(8px) !important;
    color: var(--sub) !important; border: 1px solid var(--border) !important;
    border-radius: 8px !important; font-size: 12px !important; transition: all 0.2s ease !important;
}
textarea:focus { border-color: var(--accent) !important; box-shadow: 0 0 8px rgba(77,255,195,0.2) !important; }

details {
    background: rgba(18,21,30,0.85) !important; backdrop-filter: blur(8px) !important;
    border: 1px solid var(--border) !important; border-radius: 12px !important;
    padding: 4px 16px !important; transition: all 0.2s ease !important;
}
details:hover { border-color: var(--accent) !important; }
details summary { color: var(--sub) !important; font-size: 13px !important; cursor: pointer !important; }
details summary:hover { color: var(--accent) !important; }

hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 1.5rem 0 !important; }
::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-thumb { background: var(--muted); border-radius: 2px; }

@keyframes fadeUp { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:translateY(0); } }
@keyframes borderGlow {
    0%   { border-color:rgba(77,255,195,0.2); box-shadow:0 0 0 0 rgba(77,255,195,0); }
    50%  { border-color:rgba(77,255,195,0.6); box-shadow:0 0 12px 2px rgba(77,255,195,0.2); }
    100% { border-color:rgba(77,255,195,0.2); box-shadow:0 0 0 0 rgba(77,255,195,0); }
}
@keyframes pulseDot { 0% { opacity:0.4; transform:scale(0.8); } 100% { opacity:1; transform:scale(1.2); box-shadow:0 0 8px #4DFFC3; } }
@keyframes spin { 100% { transform:rotate(360deg); } }
@keyframes micPulse {
    0%   { box-shadow: 0 0 0 0 rgba(77,255,195,0.5); }
    70%  { box-shadow: 0 0 0 14px rgba(77,255,195,0); }
    100% { box-shadow: 0 0 0 0 rgba(77,255,195,0); }
}

.fade-in   { animation: fadeUp 0.4s ease 0.0s both; }
.fade-in-2 { animation: fadeUp 0.4s ease 0.1s both; }
.fade-in-3 { animation: fadeUp 0.4s ease 0.2s both; }
.fade-in-4 { animation: fadeUp 0.4s ease 0.3s both; }

.metric-card { transition: all 0.3s cubic-bezier(0.2,0.95,0.4,1.1) !important; cursor: pointer !important; }
.metric-card:hover { transform: scale(1.04) translateY(-4px) !important; border-color: #4DFFC3 !important; box-shadow: 0 18px 32px -12px rgba(77,255,195,0.25) !important; }

.ats-card { transition: all 0.3s ease !important; cursor: pointer !important; }
.ats-card:hover { transform: scale(1.01) translateY(-2px) !important; border-color: #4DFFC3 !important; box-shadow: 0 18px 28px -12px rgba(0,0,0,0.6), 0 0 0 1px rgba(77,255,195,0.3) !important; }

.skill-chip { display:inline-block; padding:7px 16px; background:rgba(77,255,195,0.08); border:1px solid rgba(77,255,195,0.2); border-radius:100px; font-family:'Manrope',sans-serif; font-size:12px; font-weight:500; color:#4DFFC3; margin:3px 4px 3px 0; transition:all 0.2s ease !important; cursor:pointer; }
.skill-chip:hover { transform:translateY(-2px) scale(1.05) !important; background:rgba(77,255,195,0.2) !important; box-shadow:0 4px 12px rgba(77,255,195,0.15) !important; border-color:#4DFFC3 !important; }

.job-card { display:flex; align-items:center; justify-content:space-between; padding:15px 18px; background:rgba(13,16,24,0.85); border:1px solid rgba(255,255,255,0.07); border-radius:10px; margin-bottom:8px; transition:all 0.25s ease !important; cursor:pointer; }
.job-card:hover { transform:translateX(8px) scale(1.01) !important; border-left:3px solid #4DFFC3 !important; background:rgba(17,22,31,0.95) !important; box-shadow:0 5px 14px rgba(0,0,0,0.4) !important; }

.suggestion-item { display:flex; gap:16px; padding:14px 18px; background:rgba(13,16,24,0.85); border-left:2px solid #FFBE57; border-radius:0 10px 10px 0; margin-bottom:8px; transition:all 0.2s ease !important; }
.suggestion-item:hover { background:rgba(20,26,36,0.95) !important; transform:translateX(5px) !important; border-left-width:4px !important; }

/* Native audio input widget */
[data-testid="stAudioInput"] {
    background: #1C2030 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    padding: 4px !important;
}
[data-testid="stAudioInput"] button {
    background: #252B3D !important;
    border-color: rgba(255,255,255,0.15) !important;
    color: #C8C4BC !important;
}
[data-testid="stAudioInput"] button:hover {
    background: #2E3550 !important;
    border-color: rgba(255,255,255,0.25) !important;
}
</style>
""")

# -----------------------------------
# DATABASES & FUNCTIONS
# -----------------------------------

skills_db = ["python","java","c++","html","css","javascript","react","node","mongodb",
             "sql","mysql","machine learning","git","github","flutter","dart",
             "tensorflow","django","aws","docker","ci/cd","rest apis"]

job_roles = {
    "Python Developer":          ["python","sql","git"],
    "Frontend Developer":        ["html","css","javascript","react"],
    "Backend Developer":         ["python","mongodb","sql"],
    "Machine Learning Engineer": ["python","machine learning","tensorflow"],
    "Flutter Developer":         ["flutter","dart"]
}

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted: text += extracted.lower() + "\n"
    return text

def extract_skills(text): return [s for s in skills_db if s.lower() in text]
def calculate_ats_score(skills): return round((len(skills) / len(skills_db)) * 100)
def calculate_match_percentage(skills):
    t = ["python","sql","git","machine learning","react"]
    return round((sum(1 for s in t if s in skills) / len(t)) * 100)
def give_suggestions(skills):
    out = []
    if "react" not in skills:           out.append("Learn React — essential for frontend roles.")
    if "mongodb" not in skills:         out.append("Add MongoDB to strengthen backend profiles.")
    if "machine learning" not in skills: out.append("ML projects dramatically increase tech profile relevance.")
    return out
def recommend_jobs(skills): return [r for r, req in job_roles.items() if sum(1 for s in req if s in skills) >= 2]

# -----------------------------------
# SIDEBAR
# -----------------------------------

with st.sidebar:
    st.html("""
    <div style="padding:1.4rem 0.4rem;">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:22px;">
            <div style="width:6px;height:6px;border-radius:50%;background:#4DFFC3;box-shadow:0 0 10px #4DFFC3;flex-shrink:0;animation:pulseDot 1.4s infinite alternate;"></div>
            <span style="font-family:'Manrope',sans-serif;font-size:10px;letter-spacing:0.14em;text-transform:uppercase;color:#818DA0;font-weight:600;">System Active</span>
        </div>
        <div style="font-family:'Syne',sans-serif;font-size:17px;font-weight:700;color:#ECE9E2;margin-bottom:10px;">About</div>
        <p style="font-family:'Manrope',sans-serif;font-size:13px;color:#818DA0;line-height:1.8;margin-bottom:0;">Parses your resume PDF, detects skills, scores ATS criteria, and matches you to relevant roles.</p>
        <div style="border-top:1px solid rgba(255,255,255,0.07);padding-top:18px;margin-top:20px;margin-bottom:18px;">
            <div style="font-size:10px;letter-spacing:0.13em;text-transform:uppercase;color:#3A3F4E;margin-bottom:7px;font-family:'Manrope',sans-serif;">Developed by</div>
            <div style="font-family:'Syne',sans-serif;font-size:14px;font-weight:600;color:#ECE9E2;">Shreeji Tiwari</div>
        </div>
    </div>
    """)

# -----------------------------------
# HEADER + UPLOAD
# -----------------------------------

st.html("""
<div class="fade-in" style="margin-bottom:2rem;">
    <span style="font-family:'Manrope',sans-serif;font-size:11px;letter-spacing:0.16em;text-transform:uppercase;color:#4DFFC3;font-weight:600;">◈ Career Intelligence</span>
    <h1 style="font-family:'Syne',sans-serif;font-size:2.9rem;font-weight:800;letter-spacing:-0.04em;line-height:1.05;margin:10px 0 14px;color:#ECE9E2;">Resume <span style="color:#4DFFC3;">Analyzer</span></h1>
    <p style="font-family:'Manrope',sans-serif;font-size:14px;color:#818DA0;margin:0;max-width:500px;line-height:1.8;">Upload your PDF for instant ATS scoring, skill detection, job role matching, and improvement suggestions.</p>
</div>
""")

uploaded_file = st.file_uploader("", type=["pdf"], label_visibility="collapsed")

# -----------------------------------
# MAIN LOGIC
# -----------------------------------

if uploaded_file:

    # ── LOADER ───────────────────────────────────────────────────────────
    loader_placeholder = st.empty()
    for stage in ["Initializing ATS parsing engine...", "Extracting document structure...",
                  "Identifying technical skills...", "Cross-referencing job databases...",
                  "Calculating industry alignment score..."]:
        loader_placeholder.html(f"""
        <div class="fade-in" style="background:rgba(18,21,30,0.85);backdrop-filter:blur(8px);border:1px solid rgba(77,255,195,0.3);border-radius:12px;padding:20px 24px;margin-bottom:20px;display:flex;align-items:center;gap:16px;">
            <div style="width:20px;height:20px;border:2px solid rgba(77,255,195,0.15);border-top-color:#4DFFC3;border-radius:50%;animation:spin 0.7s linear infinite;flex-shrink:0;"></div>
            <div style="font-family:'Syne',sans-serif;font-size:14px;font-weight:600;color:#ECE9E2;">{stage}</div>
        </div>""")
        time.sleep(0.45)
    loader_placeholder.empty()

    resume_text      = extract_text_from_pdf(uploaded_file)
    skills           = extract_skills(resume_text)
    ats_score        = calculate_ats_score(skills)
    match_percentage = calculate_match_percentage(skills)
    suggestions      = give_suggestions(skills)
    recommended_jobs = recommend_jobs(skills)

    st.html('<div style="height:6px;"></div>')

    # ── METRICS ──────────────────────────────────────────────────────────
    st.html(f"""
    <div class="fade-in-2" style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:18px 0 22px;">
        <div class="metric-card" style="background:rgba(18,21,30,0.85);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:22px 24px;">
            <div style="font-family:'Manrope',sans-serif;font-size:10px;letter-spacing:0.13em;text-transform:uppercase;color:#818DA0;margin-bottom:8px;">ATS Score</div>
            <div style="font-family:'Syne',sans-serif;font-size:2.5rem;font-weight:800;color:#ECE9E2;line-height:1;">{ats_score}</div>
            <div style="font-family:'Manrope',sans-serif;font-size:11px;color:#3A3F4E;margin-top:5px;">/100 points</div>
        </div>
        <div class="metric-card" style="background:rgba(18,21,30,0.85);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:22px 24px;">
            <div style="font-family:'Manrope',sans-serif;font-size:10px;letter-spacing:0.13em;text-transform:uppercase;color:#818DA0;margin-bottom:8px;">Skills Found</div>
            <div style="font-family:'Syne',sans-serif;font-size:2.5rem;font-weight:800;color:#ECE9E2;line-height:1;">{len(skills)}</div>
            <div style="font-family:'Manrope',sans-serif;font-size:11px;color:#3A3F4E;margin-top:5px;">of {len(skills_db)} tracked</div>
        </div>
        <div class="metric-card" style="background:rgba(18,21,30,0.85);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:22px 24px;">
            <div style="font-family:'Manrope',sans-serif;font-size:10px;letter-spacing:0.13em;text-transform:uppercase;color:#818DA0;margin-bottom:8px;">Job Matches</div>
            <div style="font-family:'Syne',sans-serif;font-size:2.5rem;font-weight:800;color:#ECE9E2;line-height:1;">{len(recommended_jobs)}</div>
            <div style="font-family:'Manrope',sans-serif;font-size:11px;color:#3A3F4E;margin-top:5px;">roles matched</div>
        </div>
        <div class="metric-card" style="background:rgba(18,21,30,0.85);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:22px 24px;">
            <div style="font-family:'Manrope',sans-serif;font-size:10px;letter-spacing:0.13em;text-transform:uppercase;color:#818DA0;margin-bottom:8px;">Resume Match</div>
            <div style="font-family:'Syne',sans-serif;font-size:2.5rem;font-weight:800;color:#ECE9E2;line-height:1;">{match_percentage}%</div>
            <div style="font-family:'Manrope',sans-serif;font-size:11px;color:#3A3F4E;margin-top:5px;">Industry alignment</div>
        </div>
    </div>""")

    # ── ATS ARC ──────────────────────────────────────────────────────────
    r = 58
    circ = 2 * math.pi * r
    dash = (ats_score / 100) * circ
    gap  = circ - dash
    if ats_score >= 70:   arc_color, rating, tip = "#4DFFC3", "Excellent", "Strong profile. Tailor per role for best results."
    elif ats_score >= 40: arc_color, rating, tip = "#FFBE57", "Good",      "Solid base. A few more skills will push you to Excellent."
    else:                 arc_color, rating, tip = "#FF6B6B", "Needs Work","Expand skill set and use more job-specific keywords."

    st.html(f"""
    <div class="ats-card fade-in-3" style="background:rgba(18,21,30,0.85);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:28px 32px;margin-bottom:20px;display:flex;align-items:center;gap:36px;flex-wrap:wrap;">
        <div style="position:relative;width:148px;height:148px;flex-shrink:0;">
            <svg width="148" height="148" viewBox="0 0 148 148" style="transform:rotate(-90deg);display:block;">
                <circle cx="74" cy="74" r="{r}" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="10"/>
                <circle cx="74" cy="74" r="{r}" fill="none" stroke="{arc_color}" stroke-width="10" stroke-dasharray="{dash:.2f} {gap:.2f}" stroke-linecap="round"/>
            </svg>
            <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;">
                <div style="font-family:'Syne',sans-serif;font-size:2.1rem;font-weight:800;color:#ECE9E2;line-height:1;">{ats_score}</div>
                <div style="font-family:'Manrope',sans-serif;font-size:10px;color:#3A3F4E;">/100</div>
            </div>
        </div>
        <div>
            <div style="font-family:'Manrope',sans-serif;font-size:10px;letter-spacing:0.14em;text-transform:uppercase;color:#818DA0;margin-bottom:7px;">ATS Score Rating</div>
            <div style="font-family:'Syne',sans-serif;font-size:1.7rem;font-weight:700;color:{arc_color};margin-bottom:10px;">{rating}</div>
            <div style="font-family:'Manrope',sans-serif;font-size:13px;color:#818DA0;line-height:1.75;max-width:380px;">{tip}</div>
        </div>
    </div>""")

    # ── SKILLS ───────────────────────────────────────────────────────────
    if skills:
        chips = "".join([f'<span class="skill-chip">{s}</span>' for s in skills])
        st.html(f"""
        <div class="fade-in-3" style="background:rgba(18,21,30,0.85);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:24px 28px;margin-bottom:20px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
                <div style="font-family:'Syne',sans-serif;font-size:15px;font-weight:700;color:#ECE9E2;">Detected Skills</div>
                <div style="background:rgba(77,255,195,0.09);border:1px solid rgba(77,255,195,0.2);border-radius:100px;padding:3px 13px;font-family:'Manrope',sans-serif;font-size:11px;color:#4DFFC3;font-weight:600;">{len(skills)} found</div>
            </div>
            <div>{chips}</div>
        </div>""")

    # ── JOB MATCHES ──────────────────────────────────────────────────────
    role_icons = {"Python Developer":"⬡","Frontend Developer":"◻","Backend Developer":"▨","Machine Learning Engineer":"◈","Flutter Developer":"◇"}
    if recommended_jobs:
        jcards = "".join([f"""<div class="job-card">
            <div style="display:flex;align-items:center;gap:14px;">
                <div style="width:36px;height:36px;border-radius:8px;background:rgba(77,255,195,0.07);border:1px solid rgba(77,255,195,0.15);display:flex;align-items:center;justify-content:center;font-size:16px;color:#4DFFC3;flex-shrink:0;">{role_icons.get(j,"◉")}</div>
                <div><div style="font-family:'Syne',sans-serif;font-weight:600;font-size:14px;color:#ECE9E2;">{j}</div><div style="font-family:'Manrope',sans-serif;font-size:11px;color:#3A3F4E;margin-top:3px;">Skills matched</div></div>
            </div>
            <div style="background:rgba(77,255,195,0.09);border:1px solid rgba(77,255,195,0.2);border-radius:6px;padding:5px 14px;font-family:'Manrope',sans-serif;font-size:10px;font-weight:700;color:#4DFFC3;letter-spacing:0.06em;text-transform:uppercase;">Match</div>
        </div>""" for j in recommended_jobs])
        st.html(f"""<div class="fade-in-4" style="background:rgba(18,21,30,0.85);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:24px 28px;margin-bottom:20px;"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;"><div style="font-family:'Syne',sans-serif;font-size:15px;font-weight:700;color:#ECE9E2;">Recommended Roles</div><div style="background:rgba(77,255,195,0.09);border:1px solid rgba(77,255,195,0.2);border-radius:100px;padding:3px 13px;font-family:'Manrope',sans-serif;font-size:11px;color:#4DFFC3;font-weight:600;">{len(recommended_jobs)} matches</div></div>{jcards}</div>""")

    # ── SUGGESTIONS ──────────────────────────────────────────────────────
    if suggestions:
        sitems = "".join([f"""<div class="suggestion-item"><div style="flex-shrink:0;font-family:'Syne',sans-serif;font-size:12px;font-weight:700;color:#FFBE57;letter-spacing:0.05em;margin-top:1px;">0{i+1}</div><div style="font-family:'Manrope',sans-serif;font-size:13px;color:#818DA0;line-height:1.7;">{s}</div></div>""" for i, s in enumerate(suggestions)])
        st.html(f"""<div class="fade-in-4" style="background:rgba(18,21,30,0.85);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:24px 28px;margin-bottom:20px;"><div style="font-family:'Syne',sans-serif;font-size:15px;font-weight:700;color:#ECE9E2;margin-bottom:14px;">Improvement Suggestions</div>{sitems}</div>""")

    # ════════════════════════════════════════════════════════════════
    # PHASE 2 — JD MATCHER
    # ════════════════════════════════════════════════════════════════
    st.html("""<div class="fade-in-4" style="margin-top:3rem;margin-bottom:1rem;">
        <span style="font-family:'Manrope',sans-serif;font-size:11px;letter-spacing:0.16em;text-transform:uppercase;color:#FFBE57;font-weight:600;">◈ AI Copilot Feature</span>
        <h2 style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:700;color:#ECE9E2;margin:5px 0 0 0;">Target Role <span style="color:#FFBE57;">Matcher</span></h2>
        <p style="font-family:'Manrope',sans-serif;font-size:13px;color:#818DA0;margin-top:8px;">Paste the job description to uncover missing keywords.</p>
    </div>""")

    jd_text = st.text_area("Job Description", height=200, placeholder="Paste the full job description here...", label_visibility="collapsed")
    if jd_text:
        with st.spinner("Cross-referencing resume with job description..."):
            time.sleep(0.6)
            jd_skills_set     = set(extract_skills(jd_text.lower()))
            resume_skills_set = set(skills)
            if not jd_skills_set:
                st.warning("No trackable skills found in this JD.")
            else:
                matched = jd_skills_set & resume_skills_set
                missing = jd_skills_set - resume_skills_set
                jd_score = round((len(matched) / len(jd_skills_set)) * 100)
                mc = "#4DFFC3" if jd_score >= 75 else ("#FFBE57" if jd_score >= 40 else "#FF6B6B")
                m_chips = "".join([f'<span style="display:inline-block;padding:6px 14px;background:rgba(255,107,107,0.08);border:1px solid rgba(255,107,107,0.3);border-radius:100px;font-family:Manrope,sans-serif;font-size:11px;font-weight:600;color:#FF6B6B;margin:3px 4px 3px 0;">{s}</span>' for s in missing]) or "<span style='color:#818DA0;font-size:12px;font-family:Manrope;'>None — you hit all keywords!</span>"
                g_chips = "".join([f'<span class="skill-chip" style="font-size:11px;padding:6px 14px;">{s}</span>' for s in matched]) or "<span style='color:#818DA0;font-size:12px;font-family:Manrope;'>No matches found.</span>"
                st.html(f"""<div class="fade-in" style="background:rgba(18,21,30,0.85);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:28px 32px;margin-top:15px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(255,255,255,0.05);padding-bottom:20px;margin-bottom:20px;">
                        <div style="font-family:'Syne',sans-serif;font-size:18px;font-weight:700;color:#ECE9E2;">Alignment Results</div>
                        <div style="text-align:right;"><div style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:{mc};line-height:1;">{jd_score}%</div><div style="font-family:'Manrope',sans-serif;font-size:10px;text-transform:uppercase;letter-spacing:0.1em;color:#818DA0;margin-top:4px;">JD Match</div></div>
                    </div>
                    <div style="margin-bottom:24px;"><div style="font-family:'Manrope',sans-serif;font-size:11px;text-transform:uppercase;color:#FF6B6B;letter-spacing:0.1em;font-weight:700;margin-bottom:10px;">Missing Keywords (Add These)</div><div>{m_chips}</div></div>
                    <div><div style="font-family:'Manrope',sans-serif;font-size:11px;text-transform:uppercase;color:#4DFFC3;letter-spacing:0.1em;font-weight:700;margin-bottom:10px;">Matched Keywords</div><div>{g_chips}</div></div>
                </div>""")

    # ════════════════════════════════════════════════════════════════
    # PHASE 3 — AI RESUME ENHANCER
    # ════════════════════════════════════════════════════════════════
    st.html("""<div class="fade-in-4" style="margin-top:3rem;margin-bottom:1rem;">
        <span style="font-family:'Manrope',sans-serif;font-size:11px;letter-spacing:0.16em;text-transform:uppercase;color:#4DFFC3;font-weight:600;">◈ Generative AI</span>
        <h2 style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:700;color:#ECE9E2;margin:5px 0 0 0;">AI Resume <span style="color:#4DFFC3;">Enhancer</span></h2>
        <p style="font-family:'Manrope',sans-serif;font-size:13px;color:#818DA0;margin-top:8px;">Powered by Llama 3 via Groq for lightning-fast AI feedback.</p>
    </div>""")

    api_key = st.text_input("Enter Groq API Key to unlock all AI features:", type="password", placeholder="gsk_...")

    if st.button("✨ Generate Expert AI Review"):
        if not api_key:
            st.error("Please enter your Groq API key above first.")
        else:
            with st.spinner("Connecting to Groq..."):
                try:
                    client = Groq(api_key=api_key)
                    resp = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role":"system","content":"You are an expert FAANG technical recruiter."},
                                  {"role":"user","content":f"Resume:\n{resume_text}\n\nGive: 1) CRITIQUE (3 sentences max). 2) REWRITES of the 2 weakest bullet points. Plain text, no markdown."}],
                        temperature=0.7)
                    st.html(f"""<div class="fade-in" style="background:rgba(18,21,30,0.85);backdrop-filter:blur(8px);border:1px solid rgba(77,255,195,0.4);border-radius:16px;padding:28px 32px;margin-top:15px;box-shadow:0 10px 40px rgba(77,255,195,0.1);">
                        <div style="font-family:'Syne',sans-serif;font-size:16px;font-weight:700;color:#4DFFC3;margin-bottom:12px;">✦ Copilot Analysis Complete</div>
                        <div style="font-family:'Manrope',sans-serif;font-size:14px;color:#ECE9E2;line-height:1.8;white-space:pre-wrap;">{resp.choices[0].message.content}</div>
                    </div>""")
                except Exception as e:
                    st.error(f"API Error: {e}")

    # ════════════════════════════════════════════════════════════════
    # PHASE 4 — MOCK INTERVIEWER
    # ════════════════════════════════════════════════════════════════
    st.html("""<div class="fade-in-4" style="margin-top:3rem;margin-bottom:1rem;">
        <span style="font-family:'Manrope',sans-serif;font-size:11px;letter-spacing:0.16em;text-transform:uppercase;color:#FFBE57;font-weight:600;">◈ Interview Prep</span>
        <h2 style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:700;color:#ECE9E2;margin:5px 0 0 0;">Mock <span style="color:#FFBE57;">Interviewer</span></h2>
        <p style="font-family:'Manrope',sans-serif;font-size:13px;color:#818DA0;margin-top:8px;">Generate tailored interview questions based on your resume and target role.</p>
    </div>""")

    if st.button("🎯 Generate Mock Interview Questions"):
        if not api_key:
            st.error("Enter your Groq API key above first.")
        else:
            with st.spinner("Generating targeted questions..."):
                try:
                    client  = Groq(api_key=api_key)
                    jd_ctx  = f"\nTARGET JD:\n{jd_text}" if jd_text else ""
                    resp = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role":"system","content":"You are a Senior Technical Hiring Manager."},
                                  {"role":"user","content":f"Resume:\n{resume_text}{jd_ctx}\n\nGenerate exactly 5 questions: 2 technical, 2 behavioral/project, 1 curveball. Plain text with numbers."}],
                        temperature=0.7)
                    st.html(f"""<div class="fade-in" style="background:rgba(18,21,30,0.85);backdrop-filter:blur(8px);border:1px solid rgba(255,190,87,0.4);border-radius:16px;padding:28px 32px;margin-top:15px;box-shadow:0 10px 40px rgba(255,190,87,0.05);">
                        <div style="font-family:'Syne',sans-serif;font-size:16px;font-weight:700;color:#FFBE57;margin-bottom:12px;">🎯 Your Custom Interview</div>
                        <div style="font-family:'Manrope',sans-serif;font-size:14px;color:#ECE9E2;line-height:1.8;white-space:pre-wrap;">{resp.choices[0].message.content}</div>
                    </div>""")
                except Exception as e:
                    st.error(f"API Error: {e}")

    # ════════════════════════════════════════════════════════════════
    # PHASE 5 — AI VOICE INTERVIEW
    # ════════════════════════════════════════════════════════════════
    st.html("""<div class="fade-in-4" style="margin-top:3rem;margin-bottom:1rem;">
        <span style="font-family:'Manrope',sans-serif;font-size:11px;letter-spacing:0.16em;text-transform:uppercase;color:#4DFFC3;font-weight:600;">◈ Voice AI — Phase 5</span>
        <h2 style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:700;color:#ECE9E2;margin:5px 0 0 0;">AI Voice <span style="color:#4DFFC3;">Interviewer</span></h2>
        <p style="font-family:'Manrope',sans-serif;font-size:13px;color:#818DA0;margin-top:8px;">
            AI asks a question aloud → you speak your answer → Groq transcribes &amp; scores your response in real-time.
        </p>
    </div>""")

    # Step indicators
    st.html("""
    <div class="fade-in" style="display:flex;align-items:center;gap:0;margin-bottom:24px;flex-wrap:wrap;gap:8px;">
        <div style="display:flex;align-items:center;gap:8px;background:rgba(77,255,195,0.08);border:1px solid rgba(77,255,195,0.2);border-radius:100px;padding:6px 14px;">
            <div style="width:20px;height:20px;border-radius:50%;background:#4DFFC3;display:flex;align-items:center;justify-content:center;font-family:'Syne',sans-serif;font-size:11px;font-weight:700;color:#08090C;">1</div>
            <span style="font-family:'Manrope',sans-serif;font-size:12px;color:#4DFFC3;">Generate Question</span>
        </div>
        <div style="color:#3A3F4E;font-size:18px;padding:0 4px;">→</div>
        <div style="display:flex;align-items:center;gap:8px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);border-radius:100px;padding:6px 14px;">
            <div style="width:20px;height:20px;border-radius:50%;background:#3A3F4E;display:flex;align-items:center;justify-content:center;font-family:'Syne',sans-serif;font-size:11px;font-weight:700;color:#ECE9E2;">2</div>
            <span style="font-family:'Manrope',sans-serif;font-size:12px;color:#818DA0;">AI Reads Aloud</span>
        </div>
        <div style="color:#3A3F4E;font-size:18px;padding:0 4px;">→</div>
        <div style="display:flex;align-items:center;gap:8px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);border-radius:100px;padding:6px 14px;">
            <div style="width:20px;height:20px;border-radius:50%;background:#3A3F4E;display:flex;align-items:center;justify-content:center;font-family:'Syne',sans-serif;font-size:11px;font-weight:700;color:#ECE9E2;">3</div>
            <span style="font-family:'Manrope',sans-serif;font-size:12px;color:#818DA0;">Record Answer</span>
        </div>
        <div style="color:#3A3F4E;font-size:18px;padding:0 4px;">→</div>
        <div style="display:flex;align-items:center;gap:8px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);border-radius:100px;padding:6px 14px;">
            <div style="width:20px;height:20px;border-radius:50%;background:#3A3F4E;display:flex;align-items:center;justify-content:center;font-family:'Syne',sans-serif;font-size:11px;font-weight:700;color:#ECE9E2;">4</div>
            <span style="font-family:'Manrope',sans-serif;font-size:12px;color:#818DA0;">AI Evaluates</span>
        </div>
    </div>
    """)

    col_btn1, col_btn2 = st.columns([1, 3])
    with col_btn1:
        gen_q = st.button("🎤 Generate Question", key="gen_voice_q")

    if gen_q:
        if not api_key:
            st.error("Enter your Groq API key above first.")
        else:
            with st.spinner("Generating interview question..."):
                try:
                    client = Groq(api_key=api_key)
                    q_resp = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": "You are a senior technical interviewer. Output ONLY the question text — no preamble, no numbering, nothing else."},
                            {"role": "user",   "content": f"Skills on this resume: {', '.join(skills)}. Generate one sharp, specific technical interview question."}
                        ],
                        max_tokens=120, temperature=0.85)
                    st.session_state.voice_q          = q_resp.choices[0].message.content.strip()
                    st.session_state.voice_transcript = None
                    st.session_state.voice_eval       = None
                except Exception as e:
                    st.error(f"Error generating question: {e}")

    # ── Show question + TTS button ────────────────────────────────
    if st.session_state.voice_q:
        st.html(f"""
        <div class="ats-card fade-in" style="background:rgba(18,21,30,0.85);backdrop-filter:blur(8px);border:1px solid rgba(77,255,195,0.25);border-radius:16px;padding:24px 28px;margin-bottom:16px;">
            <div style="font-family:'Manrope',sans-serif;font-size:10px;letter-spacing:0.14em;text-transform:uppercase;color:#4DFFC3;margin-bottom:10px;font-weight:600;">◈ Interview Question</div>
            <div style="font-family:'Syne',sans-serif;font-size:1.25rem;font-weight:600;color:#ECE9E2;line-height:1.5;">{st.session_state.voice_q}</div>
        </div>""")

        # TTS — plays question aloud via browser Speech API
        tts_col1, tts_col2 = st.columns([1, 3])
        with tts_col1:
            if st.button("🔊 Read Aloud", key="tts_btn"):
                q_escaped = json.dumps(st.session_state.voice_q)
                components.html(f"""
                <script>
                    window.speechSynthesis.cancel();
                    const u = new SpeechSynthesisUtterance({q_escaped});
                    u.rate = 0.88; u.pitch = 1.0; u.volume = 1.0;
                    const setVoice = () => {{
                        const voices = window.speechSynthesis.getVoices();
                        const pick = voices.find(v => v.lang.startsWith('en') && (v.name.includes('Google') || v.name.includes('Premium') || v.name.includes('Enhanced')));
                        if (pick) u.voice = pick;
                        window.speechSynthesis.speak(u);
                    }};
                    if (window.speechSynthesis.getVoices().length > 0) setVoice();
                    else {{ window.speechSynthesis.onvoiceschanged = setVoice; }}
                </script>
                """, height=0)

        # ── Audio recorder ────────────────────────────────────────
        st.html("""
        <div style="font-family:'Manrope',sans-serif;font-size:12px;letter-spacing:0.1em;text-transform:uppercase;color:#818DA0;margin:20px 0 6px;font-weight:600;">
            🎙️ Record Your Answer
        </div>""")

        audio_input = st.audio_input("", key="phase5_recorder", label_visibility="collapsed")
        audio_bytes = audio_input.read() if audio_input else None

        if audio_bytes and len(audio_bytes) > 2000:
            with st.spinner("Transcribing your answer via Whisper..."):
                try:
                    client = Groq(api_key=api_key)
                    st.session_state.voice_transcript = client.audio.transcriptions.create(
                        file=("answer.wav", audio_bytes),
                        model="whisper-large-v3",
                        response_format="text"
                    )
                    st.session_state.voice_eval = None
                except Exception as e:
                    st.error(f"Transcription error: {e}")

    # ── Show transcript + evaluate ────────────────────────────────
    if st.session_state.voice_transcript:
        st.html(f"""
        <div class="fade-in" style="background:rgba(13,16,24,0.9);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.07);border-left:3px solid #4DFFC3;border-radius:0 14px 14px 0;padding:20px 24px;margin-bottom:16px;">
            <div style="font-family:'Manrope',sans-serif;font-size:10px;letter-spacing:0.12em;text-transform:uppercase;color:#4DFFC3;margin-bottom:8px;font-weight:600;">📝 Your Answer (Transcribed)</div>
            <div style="font-family:'Manrope',sans-serif;font-size:14px;color:#ECE9E2;line-height:1.75;font-style:italic;">"{st.session_state.voice_transcript}"</div>
        </div>""")

        if st.button("⚡ Evaluate My Answer", key="eval_voice"):
            with st.spinner("Analyzing your response..."):
                try:
                    client   = Groq(api_key=api_key)
                    eval_res = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": "You are a strict but fair technical interviewer. Be concise and direct."},
                            {"role": "user",   "content": f"""
QUESTION: {st.session_state.voice_q}
CANDIDATE ANSWER: {st.session_state.voice_transcript}

Evaluate with exactly this structure:
Score: X/10
Strengths: (1 sentence)
Gaps: (1 sentence)
Ideal Answer Hint: (1-2 sentences)

Plain text only. No markdown symbols.
"""}],
                        temperature=0.5, max_tokens=300)
                    st.session_state.voice_eval = eval_res.choices[0].message.content
                except Exception as e:
                    st.error(f"Evaluation error: {e}")

    # ── Show evaluation ───────────────────────────────────────────
    if st.session_state.voice_eval:
        # Parse score for color
        score_color = "#4DFFC3"
        try:
            score_line = [l for l in st.session_state.voice_eval.split('\n') if 'Score' in l][0]
            score_num  = int(''.join(filter(str.isdigit, score_line.split('/')[0])))
            score_color = "#4DFFC3" if score_num >= 7 else ("#FFBE57" if score_num >= 4 else "#FF6B6B")
        except Exception:
            pass

        st.html(f"""
        <div class="fade-in" style="background:rgba(18,21,30,0.85);backdrop-filter:blur(8px);border:1px solid {score_color}40;border-radius:16px;padding:28px 32px;margin-top:4px;box-shadow:0 10px 40px {score_color}10;">
            <div style="font-family:'Syne',sans-serif;font-size:16px;font-weight:700;color:{score_color};margin-bottom:16px;display:flex;align-items:center;gap:8px;">
                <span>⚡</span> AI Evaluation
            </div>
            <div style="font-family:'Manrope',sans-serif;font-size:14px;color:#ECE9E2;line-height:1.9;white-space:pre-wrap;">{st.session_state.voice_eval}</div>
            <div style="border-top:1px solid rgba(255,255,255,0.06);margin-top:20px;padding-top:16px;display:flex;justify-content:flex-end;">
                <div style="font-family:'Manrope',sans-serif;font-size:11px;color:#3A3F4E;">Powered by Llama 3.3 70B · Groq · Whisper</div>
            </div>
        </div>""")

    # ── Expander ──────────────────────────────────────────────────
    with st.expander("View extracted resume text"):
        st.text_area("", resume_text, height=280, label_visibility="collapsed")

else:
    st.html("""
    <div class="fade-in-2" style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:4rem 2rem;text-align:center;background:rgba(18,21,30,0.4);border:1px dashed rgba(255,255,255,0.05);border-radius:16px;margin-bottom:2rem;backdrop-filter:blur(4px);">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#4DFFC3" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom:1.5rem;opacity:0.9;filter:drop-shadow(0 0 12px rgba(77,255,195,0.3));">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>
        </svg>
        <h3 style="font-family:'Syne',sans-serif;font-size:1.5rem;color:#ECE9E2;margin:0 0 10px 0;">Awaiting Document</h3>
        <p style="font-family:'Manrope',sans-serif;font-size:14px;color:#818DA0;max-width:420px;margin:0;line-height:1.7;">Upload your resume PDF above to initialize the ATS engine and unlock all 5 AI phases.</p>
    </div>""")

# -----------------------------------
# FOOTER
# -----------------------------------
st.html("""<div style="border-top:1px solid rgba(255,255,255,0.07);margin-top:2rem;text-align:center;padding:20px;color:#3A3F4E;font-size:12px;font-family:'Manrope',sans-serif;">Built with ❤️ using Python, Streamlit, Groq &amp; Whisper<br>AI Resume Analyzer © 2026</div>""")
