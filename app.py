import streamlit as st
import pdfplumber
import math
import time
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
# LIVE PARTICLE BACKGROUND
# -----------------------------------

def render_particle_background():
    st.html("""
    <style>
        iframe {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            z-index: -1 !important;
            pointer-events: none !important; 
        }
        
        .stApp, [data-testid="stApp"], [data-testid="stAppViewContainer"], .main, .block-container, header {
            background: transparent !important;
        }
        
        [data-testid="stSidebar"] {
            background: rgba(13, 16, 24, 0.85) !important;
            backdrop-filter: blur(10px) !important;
        }
        
        .metric-card, .ats-card, [class*="metric-card"], [class*="job-card"] {
            background: rgba(18, 21, 30, 0.85) !important;
            backdrop-filter: blur(8px) !important;
        }
    </style>
    """)

    particle_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            body { margin: 0; padding: 0; background-color: #08090C; overflow: hidden; }
            #tsparticles { position: absolute; width: 100%; height: 100%; }
        </style>
        <script src="https://cdn.jsdelivr.net/npm/tsparticles@2/tsparticles.bundle.min.js"></script>
    </head>
    <body>
        <div id="tsparticles"></div>
        <script>
            tsParticles.load("tsparticles", {
                fpsLimit: 60,
                particles: {
                    color: { value: "#4DFFC3" },
                    links: { color: "#4DFFC3", distance: 150, enable: true, opacity: 0.15, width: 1 },
                    move: { enable: true, speed: 0.8, direction: "none", random: false, straight: false, outModes: { default: "bounce" } },
                    number: { density: { enable: true, area: 800 }, value: 50 },
                    opacity: { value: 0.4, animation: { enable: true, speed: 1, minimumValue: 0.1, sync: false } },
                    shape: { type: "circle" },
                    size: { value: { min: 1.5, max: 3.5 }, animation: { enable: true, speed: 2, minimumValue: 0.5, sync: false } }
                },
                interactivity: { events: { onHover: { enable: true, mode: "repulse" }, resize: true }, modes: { repulse: { distance: 100, duration: 0.4 } } },
                detectRetina: true
            });
        </script>
    </body>
    </html>
    """
    components.html(particle_html, height=0)

render_particle_background()

# -----------------------------------
# GLOBAL CSS
# -----------------------------------

st.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Manrope:wght@300;400;500;600;700&display=swap');

:root {
    --bg:         #08090C;
    --surface:    #0D1018;
    --card:       #12151E;
    --border:     rgba(255,255,255,0.07);
    --border-hi:  rgba(255,255,255,0.12);
    --accent:     #4DFFC3;
    --warn:       #FFBE57;
    --err:        #FF6B6B;
    --text:       #ECE9E2;
    --sub:        #818DA0;
    --muted:      #3A3F4E;
}

#MainMenu, footer, .stDeployButton { display: none !important; }
[data-testid="stToolbar"] { visibility: hidden !important; }

.block-container {
    padding-top: 2rem !important;
    max-width: 1040px !important;
    font-family: 'Manrope', sans-serif !important;
}

[data-testid="stSidebar"] {
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * {
    font-family: 'Manrope', sans-serif !important;
    color: var(--sub) !important;
}

p, div, li, label { font-family: 'Manrope', sans-serif !important; color: var(--text) !important; }
h1, h2, h3 { font-family: 'Syne', sans-serif !important; letter-spacing: -0.025em !important; color: var(--text) !important; }

.stButton > button {
    background: var(--accent) !important;
    color: #08090C !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    height: 44px !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover { opacity: 0.85 !important; transform: translateY(-2px) scale(1.02) !important; box-shadow: 0 8px 20px rgba(77,255,195,0.2) !important; }
.stButton > button:active { transform: translateY(1px) scale(0.98) !important; }

[data-testid="stFileUploader"] > div:first-child {
    background: rgba(18, 21, 30, 0.85) !important;
    backdrop-filter: blur(8px) !important;
    border: 1px dashed var(--border-hi) !important;
    border-radius: 14px !important;
    padding: 2rem !important;
    transition: all 0.3s ease !important;
}
[data-testid="stFileUploader"] > div:first-child:hover { border-color: var(--accent) !important; animation: borderGlow 1.5s infinite !important; }
[data-testid="stFileUploader"] label, [data-testid="stFileUploader"] [data-testid="stWidgetLabel"], [data-testid="stFileUploaderDropzoneInstructions"] { display: none !important; }
[data-testid="stFileUploaderDropzone"] * { font-size: 0 !important; color: transparent !important; }
[data-testid="stFileUploaderDropzone"] button { display: inline-flex !important; align-items: center !important; justify-content: center !important; min-width: 120px !important; min-height: 38px !important; font-size: 0 !important; color: transparent !important; background: rgba(77,255,195,0.1) !important; border: 1px solid rgba(77,255,195,0.3) !important; border-radius: 8px !important; padding: 8px 22px !important; cursor: pointer !important; transition: all 0.2s ease !important; }
[data-testid="stFileUploaderDropzone"] button:hover { background: rgba(77,255,195,0.18) !important; transform: translateY(-2px) !important; box-shadow: 0 4px 12px rgba(77,255,195,0.15) !important; }
[data-testid="stFileUploaderDropzone"] button::after { content: "Browse Files"; font-size: 13px !important; font-family: 'Syne', sans-serif !important; font-weight: 700 !important; letter-spacing: 0.06em !important; color: #4DFFC3 !important; text-transform: uppercase !important; }
[data-testid="stFileUploader"] small { color: var(--sub) !important; }

.stSpinner > div > div { border-top-color: var(--accent) !important; }

textarea { background: rgba(13, 16, 24, 0.85) !important; backdrop-filter: blur(8px) !important; color: var(--sub) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; font-size: 12px !important; transition: all 0.2s ease !important; }
textarea:focus { border-color: var(--accent) !important; box-shadow: 0 0 8px rgba(77,255,195,0.2) !important; }

details { background: rgba(18, 21, 30, 0.85) !important; backdrop-filter: blur(8px) !important; border: 1px solid var(--border) !important; border-radius: 12px !important; padding: 4px 16px !important; transition: all 0.2s ease !important; }
details:hover { border-color: var(--accent) !important; }
details summary { color: var(--sub) !important; font-size: 13px !important; cursor: pointer !important; }
details summary:hover { color: var(--accent) !important; }

hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 1.5rem 0 !important; }

::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-thumb { background: var(--muted); border-radius: 2px; }
::-webkit-scrollbar-track { background: transparent; }

@keyframes fadeUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
@keyframes borderGlow { 0% { border-color: rgba(77,255,195,0.2); box-shadow: 0 0 0 0 rgba(77,255,195,0); } 50% { border-color: rgba(77,255,195,0.6); box-shadow: 0 0 12px 2px rgba(77,255,195,0.2); } 100% { border-color: rgba(77,255,195,0.2); box-shadow: 0 0 0 0 rgba(77,255,195,0); } }
@keyframes pulseDot { 0% { opacity: 0.4; transform: scale(0.8); } 100% { opacity: 1; transform: scale(1.2); box-shadow: 0 0 8px #4DFFC3; } }

.fade-in   { animation: fadeUp 0.4s ease 0.0s both; }
.fade-in-2 { animation: fadeUp 0.4s ease 0.1s both; }
.fade-in-3 { animation: fadeUp 0.4s ease 0.2s both; }
.fade-in-4 { animation: fadeUp 0.4s ease 0.3s both; }

.metric-card { transition: all 0.3s cubic-bezier(0.2, 0.95, 0.4, 1.1) !important; cursor: pointer !important; }
.metric-card:hover { transform: scale(1.04) translateY(-4px) !important; border-color: #4DFFC3 !important; box-shadow: 0 18px 32px -12px rgba(77,255,195,0.25) !important; background: rgba(21, 28, 40, 0.95) !important; }

.ats-card { transition: all 0.3s ease !important; cursor: pointer !important; }
.ats-card:hover { transform: scale(1.01) translateY(-2px) !important; background: rgba(21, 28, 40, 0.95) !important; border-color: #4DFFC3 !important; box-shadow: 0 18px 28px -12px rgba(0,0,0,0.6), 0 0 0 1px rgba(77,255,195,0.3) !important; }

.skill-chip { display: inline-block; padding: 7px 16px; background: rgba(77,255,195,0.08); border: 1px solid rgba(77,255,195,0.2); border-radius: 100px; font-family: 'Manrope', sans-serif; font-size: 12px; font-weight: 500; color: #4DFFC3; margin: 3px 4px 3px 0; transition: all 0.2s ease !important; cursor: pointer; }
.skill-chip:hover { transform: translateY(-2px) scale(1.05) !important; background: rgba(77,255,195,0.2) !important; box-shadow: 0 4px 12px rgba(77,255,195,0.15) !important; border-color: #4DFFC3 !important; }

.job-card { display: flex; align-items: center; justify-content: space-between; padding: 15px 18px; background: rgba(13, 16, 24, 0.85); border: 1px solid rgba(255,255,255,0.07); border-radius: 10px; margin-bottom: 8px; transition: all 0.25s ease !important; cursor: pointer; }
.job-card:hover { transform: translateX(8px) scale(1.01) !important; border-left: 3px solid #4DFFC3 !important; background: rgba(17, 22, 31, 0.95) !important; box-shadow: 0 5px 14px rgba(0,0,0,0.4) !important; }

.suggestion-item { display: flex; gap: 16px; padding: 14px 18px; background: rgba(13, 16, 24, 0.85); border-left: 2px solid #FFBE57; border-radius: 0 10px 10px 0; margin-bottom: 8px; transition: all 0.2s ease !important; }
.suggestion-item:hover { background: rgba(20, 26, 36, 0.95) !important; transform: translateX(5px) !important; border-left-width: 4px !important; }
</style>
""")

# -----------------------------------
# DATABASES & FUNCTIONS
# -----------------------------------

skills_db = ["python", "java", "c++", "html", "css", "javascript", "react", "node", "mongodb", "sql", "mysql", "machine learning", "git", "github", "flutter", "dart", "tensorflow", "django", "aws", "docker", "ci/cd", "rest apis"]

job_roles = {
    "Python Developer":           ["python", "sql", "git"],
    "Frontend Developer":         ["html", "css", "javascript", "react"],
    "Backend Developer":          ["python", "mongodb", "sql"],
    "Machine Learning Engineer":  ["python", "machine learning", "tensorflow"],
    "Flutter Developer":          ["flutter", "dart"]
}

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted: text += extracted.lower() + "\n"
    return text

def extract_skills(text): return [skill for skill in skills_db if skill.lower() in text]
def calculate_ats_score(skills): return round((len(skills) / len(skills_db)) * 100)
def calculate_match_percentage(skills):
    target_skills = ["python", "sql", "git", "machine learning", "react"]
    return round((sum(1 for skill in target_skills if skill in skills) / len(target_skills)) * 100)
def give_suggestions(skills):
    suggestions = []
    if "react" not in skills: suggestions.append("Learn React — it's essential for frontend roles.")
    if "mongodb" not in skills: suggestions.append("Add MongoDB to your stack to strengthen backend profiles.")
    if "machine learning" not in skills: suggestions.append("Machine Learning projects can increase profile relevance.")
    return suggestions
def recommend_jobs(skills): return [role for role, required in job_roles.items() if sum(1 for s in required if s in skills) >= 2]

# -----------------------------------
# SIDEBAR & HEADER
# -----------------------------------

with st.sidebar:
    st.html("""
    <div style="padding:1.4rem 0.4rem;">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:22px;">
            <div style="width:6px;height:6px;border-radius:50%;background:#4DFFC3;box-shadow:0 0 10px #4DFFC3;flex-shrink:0;animation: pulseDot 1.4s infinite;"></div>
            <span style="font-family:'Manrope',sans-serif;font-size:10px;letter-spacing:0.14em;text-transform:uppercase;color:#818DA0;font-weight:600;">System Active</span>
        </div>
        <div style="font-family:'Syne',sans-serif;font-size:17px;font-weight:700;color:#ECE9E2;margin-bottom:10px;">About</div>
        <p style="font-family:'Manrope',sans-serif;font-size:13px;color:#818DA0;line-height:1.8;margin-bottom:0;">Parses your resume PDF, detects technical skills, scores against ATS criteria, and matches you to relevant job roles.</p>
        <div style="border-top:1px solid rgba(255,255,255,0.07);padding-top:18px;margin-top:20px;margin-bottom:18px;">
            <div style="font-size:10px;letter-spacing:0.13em;text-transform:uppercase;color:#3A3F4E;margin-bottom:7px;font-family:'Manrope',sans-serif;">Developed by</div>
            <div style="font-family:'Syne',sans-serif;font-size:14px;font-weight:600;color:#ECE9E2;">Mohit Singh</div>
        </div>
    </div>
    """)

st.html("""
<div class="fade-in" style="margin-bottom:2rem;">
    <span style="font-family:'Manrope',sans-serif;font-size:11px;letter-spacing:0.16em;text-transform:uppercase;color:#4DFFC3;font-weight:600;">◈ Career Intelligence</span>
    <h1 style="font-family:'Syne',sans-serif;font-size:2.9rem;font-weight:800;letter-spacing:-0.04em;line-height:1.05;margin:10px 0 14px;color:#ECE9E2;">Resume <span style="color:#4DFFC3;">Analyzer</span></h1>
    <p style="font-family:'Manrope',sans-serif;font-size:14px;color:#818DA0;margin:0;max-width:500px;line-height:1.8;">Upload your PDF for instant ATS scoring, skill detection, job role matching, and improvement suggestions.</p>
</div>
""")
uploaded_file = st.file_uploader("", type=["pdf"], label_visibility="collapsed")

# -----------------------------------
# MAIN LOGIC (LOADER & RESULTS)
# -----------------------------------

if uploaded_file:
    loader_placeholder = st.empty()
    loading_stages = ["Initializing ATS parsing engine...", "Extracting raw text and document structure...", "Identifying technical skills and frameworks...", "Cross-referencing with job role databases...", "Calculating final industry alignment score..."]
    
    for stage in loading_stages:
        loader_placeholder.html(f"""
        <div class="fade-in" style="background:rgba(18,21,30,0.85);backdrop-filter:blur(8px);border:1px solid rgba(77,255,195,0.3);border-radius:12px;padding:20px 24px;margin-bottom:20px;display:flex;align-items:center;gap:16px;box-shadow: 0 8px 32px rgba(0,0,0,0.2);">
            <div style="width:20px;height:20px;border:2px solid rgba(77,255,195,0.15);border-top-color:#4DFFC3;border-radius:50%;animation:spin 0.7s linear infinite;"></div>
            <div style="font-family:'Syne',sans-serif;font-size:14px;font-weight:600;color:#ECE9E2;letter-spacing:0.02em;">{stage}</div>
        </div>
        <style>@keyframes spin {{ 100% {{ transform:rotate(360deg); }} }}</style>
        """)
        time.sleep(0.45) 
        
    loader_placeholder.empty()

    resume_text      = extract_text_from_pdf(uploaded_file)
    skills           = extract_skills(resume_text)
    ats_score        = calculate_ats_score(skills)
    match_percentage = calculate_match_percentage(skills)
    suggestions      = give_suggestions(skills)
    recommended_jobs = recommend_jobs(skills)

    st.html('<div style="height:6px;"></div>')

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
    </div>
    """)

    r = 58
    circumference = 2 * math.pi * r
    dash = (ats_score / 100) * circumference
    gap = circumference - dash

    if ats_score >= 70: arc_color, rating, tip = "#4DFFC3", "Excellent", "Strong profile. Tailor your resume per role for best results."
    elif ats_score >= 40: arc_color, rating, tip = "#FFBE57", "Good", "Solid foundation. Adding a few more relevant skills will push you to Excellent."
    else: arc_color, rating, tip = "#FF6B6B", "Needs Work", "Expand your skill set and use more job-specific keywords throughout your resume."

    st.html(f"""
    <div class="ats-card fade-in-3" style="background:rgba(18,21,30,0.85);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:28px 32px;margin-bottom:20px;display:flex;align-items:center;gap:36px;flex-wrap:wrap;">
        <div style="position:relative;width:148px;height:148px;flex-shrink:0;">
            <svg width="148" height="148" viewBox="0 0 148 148" style="transform:rotate(-90deg);display:block;">
                <circle cx="74" cy="74" r="{r}" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="10"/>
                <circle cx="74" cy="74" r="{r}" fill="none" stroke="{arc_color}" stroke-width="10" stroke-dasharray="{dash:.2f} {gap:.2f}" stroke-linecap="round"/>
            </svg>
            <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;">
                <div style="font-family:'Syne',sans-serif;font-size:2.1rem;font-weight:800;color:#ECE9E2;line-height:1;">{ats_score}</div>
                <div style="font-family:'Manrope',sans-serif;font-size:10px;color:#3A3F4E;letter-spacing:0.05em;">/100</div>
            </div>
        </div>
        <div>
            <div style="font-family:'Manrope',sans-serif;font-size:10px;letter-spacing:0.14em;text-transform:uppercase;color:#818DA0;margin-bottom:7px;">ATS Score Rating</div>
            <div style="font-family:'Syne',sans-serif;font-size:1.7rem;font-weight:700;color:{arc_color};margin-bottom:10px;">{rating}</div>
            <div style="font-family:'Manrope',sans-serif;font-size:13px;color:#818DA0;line-height:1.75;max-width:380px;">{tip}</div>
        </div>
    </div>
    """)

    if skills:
        chips = "".join([f'<span class="skill-chip">{s}</span>' for s in skills])
        st.html(f"""
        <div class="fade-in-3" style="background:rgba(18,21,30,0.85);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:24px 28px;margin-bottom:20px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
                <div style="font-family:'Syne',sans-serif;font-size:15px;font-weight:700;color:#ECE9E2;">Detected Skills</div>
                <div style="background:rgba(77,255,195,0.09);border:1px solid rgba(77,255,195,0.2);border-radius:100px;padding:3px 13px;font-family:'Manrope',sans-serif;font-size:11px;color:#4DFFC3;font-weight:600;">{len(skills)} found</div>
            </div>
            <div>{chips}</div>
        </div>
        """)
    else:
        st.html("""<div style="background:rgba(18,21,30,0.85);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:24px 28px;margin-bottom:20px;"><div style="font-family:'Syne',sans-serif;font-size:15px;font-weight:700;color:#ECE9E2;margin-bottom:10px;">Detected Skills</div><div style="font-family:'Manrope',sans-serif;font-size:13px;color:#3A3F4E;">No skills detected. Ensure your resume text is readable (not a scanned image).</div></div>""")

    role_icons = {"Python Developer": "⬡", "Frontend Developer": "◻", "Backend Developer": "▨", "Machine Learning Engineer": "◈", "Flutter Developer": "◇"}
    if recommended_jobs:
        job_cards = "".join([f"""
            <div class="job-card">
                <div style="display:flex;align-items:center;gap:14px;">
                    <div style="width:36px;height:36px;border-radius:8px;background:rgba(77,255,195,0.07);border:1px solid rgba(77,255,195,0.15);display:flex;align-items:center;justify-content:center;font-size:16px;color:#4DFFC3;flex-shrink:0;">{role_icons.get(job, "◉")}</div>
                    <div><div style="font-family:'Syne',sans-serif;font-weight:600;font-size:14px;color:#ECE9E2;">{job}</div><div style="font-family:'Manrope',sans-serif;font-size:11px;color:#3A3F4E;margin-top:3px;">Skills matched</div></div>
                </div>
                <div style="background:rgba(77,255,195,0.09);border:1px solid rgba(77,255,195,0.2);border-radius:6px;padding:5px 14px;font-family:'Manrope',sans-serif;font-size:10px;font-weight:700;color:#4DFFC3;letter-spacing:0.06em;text-transform:uppercase;">Match</div>
            </div>
            """ for job in recommended_jobs])
        st.html(f"""<div class="fade-in-4" style="background:rgba(18,21,30,0.85);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:24px 28px;margin-bottom:20px;"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;"><div style="font-family:'Syne',sans-serif;font-size:15px;font-weight:700;color:#ECE9E2;">Recommended Roles</div><div style="background:rgba(77,255,195,0.09);border:1px solid rgba(77,255,195,0.2);border-radius:100px;padding:3px 13px;font-family:'Manrope',sans-serif;font-size:11px;color:#4DFFC3;font-weight:600;">{len(recommended_jobs)} matches</div></div>{job_cards}</div>""")
    else:
        st.html("""<div style="background:rgba(18,21,30,0.85);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:24px 28px;margin-bottom:20px;"><div style="font-family:'Syne',sans-serif;font-size:15px;font-weight:700;color:#ECE9E2;margin-bottom:10px;">Recommended Roles</div><div style="font-family:'Manrope',sans-serif;font-size:13px;color:#3A3F4E;">No roles matched. Add more relevant skills to your resume.</div></div>""")

    if suggestions:
        suggestion_items = "".join([f"""<div class="suggestion-item"><div style="flex-shrink:0;font-family:'Syne',sans-serif;font-size:12px;font-weight:700;color:#FFBE57;letter-spacing:0.05em;margin-top:1px;">0{i + 1}</div><div style="font-family:'Manrope',sans-serif;font-size:13px;color:#818DA0;line-height:1.7;">{s}</div></div>""" for i, s in enumerate(suggestions)])
        st.html(f"""<div class="fade-in-4" style="background:rgba(18,21,30,0.85);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:24px 28px;margin-bottom:20px;"><div style="font-family:'Syne',sans-serif;font-size:15px;font-weight:700;color:#ECE9E2;margin-bottom:14px;">Improvement Suggestions</div>{suggestion_items}</div>""")

    # -----------------------------------
    # PHASE 2: JOB DESCRIPTION MATCHING
    # -----------------------------------
    st.html("""
    <div class="fade-in-4" style="margin-top: 3rem; margin-bottom: 1rem;">
        <span style="font-family:'Manrope',sans-serif;font-size:11px;letter-spacing:0.16em;text-transform:uppercase;color:#FFBE57;font-weight:600;">◈ AI Copilot Feature</span>
        <h2 style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:700;color:#ECE9E2;margin:5px 0 0 0;">Target Role <span style="color:#FFBE57;">Matcher</span></h2>
        <p style="font-family:'Manrope',sans-serif;font-size:13px;color:#818DA0;margin-top:8px;">Paste the description of the job you are applying for to uncover missing keywords.</p>
    </div>
    """)

    jd_text = st.text_area("Job Description", height=200, placeholder="Paste the full job description here...", label_visibility="collapsed")

    if jd_text:
        with st.spinner("Cross-referencing resume with job description..."):
            time.sleep(0.8) 
            
            jd_skills_list = extract_skills(jd_text.lower())
            
            jd_skills_set = set(jd_skills_list)
            resume_skills_set = set(skills)
            
            if not jd_skills_set:
                st.warning("No trackable technical skills found in this job description. Try a more technical JD.")
            else:
                matched_skills = jd_skills_set.intersection(resume_skills_set)
                missing_skills = jd_skills_set - resume_skills_set
                
                jd_match_score = round((len(matched_skills) / len(jd_skills_set)) * 100)
                
                if jd_match_score >= 75: match_color = "#4DFFC3" 
                elif jd_match_score >= 40: match_color = "#FFBE57" 
                else: match_color = "#FF6B6B" 

                missing_chips = "".join([f'<span style="display:inline-block;padding:6px 14px;background:rgba(255,107,107,0.08);border:1px solid rgba(255,107,107,0.3);border-radius:100px;font-family:\'Manrope\',sans-serif;font-size:11px;font-weight:600;color:#FF6B6B;margin:3px 4px 3px 0;">{s}</span>' for s in missing_skills])
                matched_chips = "".join([f'<span class="skill-chip" style="font-size:11px;padding:6px 14px;">{s}</span>' for s in matched_skills])
                
                if not missing_chips: missing_chips = "<span style='color:#818DA0;font-size:12px;font-family:Manrope;'>None! You hit all the keywords.</span>"
                if not matched_chips: matched_chips = "<span style='color:#818DA0;font-size:12px;font-family:Manrope;'>No matching keywords found.</span>"

                st.html(f"""
                <div class="fade-in" style="background:rgba(18,21,30,0.85);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:28px 32px;margin-top:15px;box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
                    <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(255,255,255,0.05);padding-bottom:20px;margin-bottom:20px;">
                        <div style="font-family:'Syne',sans-serif;font-size:18px;font-weight:700;color:#ECE9E2;">Alignment Results</div>
                        <div style="text-align:right;">
                            <div style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;color:{match_color};line-height:1;">{jd_match_score}%</div>
                            <div style="font-family:'Manrope',sans-serif;font-size:10px;text-transform:uppercase;letter-spacing:0.1em;color:#818DA0;margin-top:4px;">JD Match</div>
                        </div>
                    </div>
                    <div style="margin-bottom:24px;">
                        <div style="font-family:'Manrope',sans-serif;font-size:11px;text-transform:uppercase;color:#FF6B6B;letter-spacing:0.1em;font-weight:700;margin-bottom:10px;display:flex;align-items:center;gap:6px;">
                            <div style="width:6px;height:6px;border-radius:50%;background:#FF6B6B;"></div> Missing Keywords (Add These)
                        </div>
                        <div>{missing_chips}</div>
                    </div>
                    <div>
                        <div style="font-family:'Manrope',sans-serif;font-size:11px;text-transform:uppercase;color:#4DFFC3;letter-spacing:0.1em;font-weight:700;margin-bottom:10px;display:flex;align-items:center;gap:6px;">
                            <div style="width:6px;height:6px;border-radius:50%;background:#4DFFC3;"></div> Matched Keywords
                        </div>
                        <div>{matched_chips}</div>
                    </div>
                </div>
                """)
                # -----------------------------------
    # PHASE 3: AI RESUME REWRITER (OPENAI)
    # -----------------------------------
    st.html("""
    <div class="fade-in-4" style="margin-top: 3rem; margin-bottom: 1rem;">
        <span style="font-family:'Manrope',sans-serif;font-size:11px;letter-spacing:0.16em;text-transform:uppercase;color:#4DFFC3;font-weight:600;">◈ Generative AI</span>
        <h2 style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:700;color:#ECE9E2;margin:5px 0 0 0;">AI Resume <span style="color:#4DFFC3;">Enhancer</span></h2>
        <p style="font-family:'Manrope',sans-serif;font-size:13px;color:#818DA0;margin-top:8px;">Powered by Llama 3 via Groq for lightning-fast, free AI feedback.</p>
    </div>
    """)

    api_key = st.text_input("Enter Groq API Key to unlock:", type="password", placeholder="gsk_...")

    if st.button("✨ Generate Expert AI Review"):
        if not api_key:
            st.error("Please enter your Groq API key in the box above first.")
        else:
            with st.spinner("Connecting to Groq... analyzing resume at lightning speed..."):
                try:
                    # Initialize the Groq Client
                    client = Groq(api_key=api_key)
                    
                    # The Prompt
                    prompt = f"""
                    You are an expert FAANG technical recruiter. I will provide you with parsed text from a candidate's resume.
                    
                    RESUME TEXT:
                    {resume_text}
                    
                    Please provide exactly two things in your response:
                    1. CRITIQUE: One short paragraph (max 3 sentences) of brutal, honest feedback on what the resume lacks (e.g., missing metrics, weak action verbs).
                    2. REWRITES: Identify the 2 weakest bullet points in the resume, and rewrite them to be highly professional, quantifiable, and impactful.
                    
                    Format your response clearly. Do not use markdown headers, just plain text with clear spacing.
                    """

                    # Make the API call using Meta's Llama 3 70B model
                    response = client.chat.completions.create(
                       model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": "You are an expert technical recruiter and resume writer."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7
                    )
                    
                    ai_feedback = response.choices[0].message.content

                    # Display the AI's response in a premium card
                    st.html(f"""
                    <div class="fade-in" style="background:rgba(18,21,30,0.85);backdrop-filter:blur(8px);border:1px solid rgba(77,255,195,0.4);border-radius:16px;padding:28px 32px;margin-top:15px;box-shadow: 0 10px 40px rgba(77,255,195,0.1);">
                        <div style="font-family:'Syne',sans-serif;font-size:16px;font-weight:700;color:#4DFFC3;margin-bottom:12px;display:flex;align-items:center;gap:8px;">
                            <span>✦</span> Copilot Analysis Complete
                        </div>
                        <div style="font-family:'Manrope',sans-serif;font-size:14px;color:#ECE9E2;line-height:1.8;white-space:pre-wrap;">{ai_feedback}</div>
                    </div>
                    """)
                    
                except Exception as e:
                    st.error(f"API Error: {e}")
                    # -----------------------------------
    # PHASE 4: INTERVIEW PREP ENGINE
    # -----------------------------------
    st.html("""
    <div class="fade-in-4" style="margin-top: 3rem; margin-bottom: 1rem;">
        <span style="font-family:'Manrope',sans-serif;font-size:11px;letter-spacing:0.16em;text-transform:uppercase;color:#FFBE57;font-weight:600;">◈ Interview Prep</span>
        <h2 style="font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:700;color:#ECE9E2;margin:5px 0 0 0;">Mock <span style="color:#FFBE57;">Interviewer</span></h2>
        <p style="font-family:'Manrope',sans-serif;font-size:13px;color:#818DA0;margin-top:8px;">Generate tailored interview questions based on your resume and target role.</p>
    </div>
    """)

    if st.button("🎯 Generate Mock Interview Questions"):
        if not api_key:
            st.error("Please enter your Groq API key in the box above first.")
        else:
            with st.spinner("Analyzing profile... generating targeted questions..."):
                try:
                    client = Groq(api_key=api_key)
                    
                    # We dynamically add the Job Description to the prompt if the user pasted one earlier!
                    context_addition = f"\n\nTARGET JOB DESCRIPTION:\n{jd_text}" if jd_text else "\n\n(No specific job description provided, ask general technical questions based on the resume)."

                    prompt = f"""
                    You are a Senior Technical Hiring Manager. I am a candidate applying for a role.
                    
                    MY RESUME:
                    {resume_text}
                    {context_addition}
                    
                    Based on my resume and the job description, generate exactly 5 interview questions:
                    - 2 Technical questions (probing specific programming skills or frameworks I listed).
                    - 2 Behavioral/Project questions (asking me to explain specific projects on my resume).
                    - 1 "Curveball" system design or critical thinking question.
                    
                    Format neatly with line breaks. Do not use markdown headers, just plain text with numbers.
                    """

                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": "You are a tough but fair technical interviewer."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7
                    )
                    
                    questions_feedback = response.choices[0].message.content

                    # Display the questions in a premium amber-tinted card
                    st.html(f"""
                    <div class="fade-in" style="background:rgba(18,21,30,0.85);backdrop-filter:blur(8px);border:1px solid rgba(255,190,87,0.4);border-radius:16px;padding:28px 32px;margin-top:15px;box-shadow: 0 10px 40px rgba(255,190,87,0.05);">
                        <div style="font-family:'Syne',sans-serif;font-size:16px;font-weight:700;color:#FFBE57;margin-bottom:12px;display:flex;align-items:center;gap:8px;">
                            <span>🎯</span> Your Custom Interview
                        </div>
                        <div style="font-family:'Manrope',sans-serif;font-size:14px;color:#ECE9E2;line-height:1.8;white-space:pre-wrap;">{questions_feedback}</div>
                    </div>
                    """)
                except Exception as e:
                    st.error(f"API Error: {e}")
    with st.expander("View extracted resume text"):
        st.text_area("", resume_text, height=280, label_visibility="collapsed")

else:
    # -----------------------------------
    # EMPTY STATE (SHOWN BEFORE UPLOAD)
    # -----------------------------------
    st.html("""
    <div class="fade-in-2" style="display: flex; flex-direction: column; align-items: center; 
                justify-content: center; padding: 4rem 2rem; text-align: center;
                background: rgba(18,21,30,0.4); border: 1px dashed rgba(255,255,255,0.05); 
                border-radius: 16px; margin-bottom: 2rem; backdrop-filter: blur(4px);">
        
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#4DFFC3" 
             stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" 
             style="margin-bottom: 1.5rem; opacity: 0.9; filter: drop-shadow(0 0 12px rgba(77,255,195,0.3));">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10 9 9 9 8 9"></polyline>
        </svg>
        
        <h3 style="font-family: 'Syne', sans-serif; font-size: 1.5rem; color: #ECE9E2; margin: 0 0 10px 0;">
            Awaiting Document
        </h3>
        <p style="font-family: 'Manrope', sans-serif; font-size: 14px; color: #818DA0; max-width: 420px; margin: 0 0 0 0; line-height: 1.7;">
            Securely upload your resume PDF above to initialize the ATS parsing engine and uncover your industry alignment.
        </p>
    </div>
    """)

# -----------------------------------
# FOOTER
# -----------------------------------
st.html("""<div style="border-top:1px solid rgba(255,255,255,0.07);margin-top:2rem;text-align:center;padding:20px;color:#3A3F4E;font-size:12px;font-family:'Manrope',sans-serif;">Built with ❤️ using Python, Streamlit &amp; NLP<br>AI Resume Analyzer © 2026</div>""")
