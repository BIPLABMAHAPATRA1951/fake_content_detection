import streamlit as st
import time
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import os
from auth import check_credentials, register_user, get_user_role, get_all_users, toggle_user_status, delete_user, change_password

st.set_page_config(
    page_title="DeepGuard — AI Detection System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource(show_spinner="Loading AI models...")
def load_text_model():
    try:
        import warnings
        warnings.filterwarnings("ignore")
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        model_name = "roberta-base-openai-detector"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name, ignore_mismatched_sizes=True)
        model.eval()
        return tokenizer, model
    except:
        return None, None

tokenizer, roberta_model = load_text_model()

# ── Scan History ──────────────────────────────────────────────────────────────
HISTORY_FILE = "scan_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_scan(user, modality, score, verdict, details=""):
    history = load_history()
    history.append({
        "user": user,
        "modality": modality,
        "score": round(score * 100, 1),
        "verdict": verdict,
        "details": details,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    with open(HISTORY_FILE, "w") as f:
        json.dump(history[-100:], f)  # keep last 100

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: #0a0a0f;
    color: #e2e8f0;
}
.stApp { background: linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 50%, #0a0f1a 100%); }

/* Glass cards */
.glass-card {
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
    transition: all 0.3s ease;
}
.glass-card:hover {
    border-color: rgba(99,179,237,0.3);
    background: rgba(255,255,255,0.05);
}

/* Nav cards */
.nav-glass {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 28px 16px;
    text-align: center;
    transition: all 0.3s ease;
    height: 160px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    cursor: pointer;
}
.nav-glass:hover {
    background: rgba(99,179,237,0.08);
    border-color: rgba(99,179,237,0.4);
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(99,179,237,0.15);
}
.nav-icon { font-size: 2rem; margin-bottom: 10px; }
.nav-title { font-family: 'Space Grotesk', sans-serif; font-size: 0.85rem; font-weight: 600; color: #94a3b8; letter-spacing: 0.1em; text-transform: uppercase; }
.nav-desc { font-size: 0.75rem; color: #4a5568; margin-top: 4px; }

/* Header */
.main-header {
    text-align: center;
    padding: 32px 0 16px;
}
.logo-text {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #63b3ed, #9f7aea, #63b3ed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
}
.logo-sub {
    color: #4a5568;
    font-size: 0.85rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-top: 4px;
}

/* Verdict */
.verdict-authentic {
    background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(16,185,129,0.05));
    border: 1px solid rgba(16,185,129,0.3);
    border-radius: 16px;
    padding: 20px 28px;
    text-align: center;
    color: #10b981;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    backdrop-filter: blur(10px);
}
.verdict-manipulated {
    background: linear-gradient(135deg, rgba(239,68,68,0.1), rgba(239,68,68,0.05));
    border: 1px solid rgba(239,68,68,0.3);
    border-radius: 16px;
    padding: 20px 28px;
    text-align: center;
    color: #ef4444;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    backdrop-filter: blur(10px);
}
.verdict-uncertain {
    background: linear-gradient(135deg, rgba(245,158,11,0.1), rgba(245,158,11,0.05));
    border: 1px solid rgba(245,158,11,0.3);
    border-radius: 16px;
    padding: 20px 28px;
    text-align: center;
    color: #f59e0b;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    backdrop-filter: blur(10px);
}

/* Stat cards */
.stat-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    backdrop-filter: blur(10px);
}
.stat-num { font-family:'Space Grotesk',sans-serif; font-size:2rem; font-weight:700; color:#63b3ed; }
.stat-label { font-size:0.8rem; color:#4a5568; margin-top:4px; text-transform:uppercase; letter-spacing:0.1em; }

/* Page header */
.page-header {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 4px;
}
.page-sub { font-size: 0.85rem; color: #4a5568; margin-bottom: 20px; }

/* Divider */
.glass-divider { border: none; height: 1px; background: linear-gradient(90deg, transparent, rgba(99,179,237,0.2), transparent); margin: 20px 0; }

/* Inputs */
.stTextInput input, .stTextArea textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: rgba(99,179,237,0.5) !important;
    box-shadow: 0 0 0 3px rgba(99,179,237,0.1) !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, rgba(99,179,237,0.15), rgba(159,122,234,0.15)) !important;
    color: #63b3ed !important;
    border: 1px solid rgba(99,179,237,0.3) !important;
    border-radius: 10px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.05em !important;
    transition: all 0.3s !important;
    backdrop-filter: blur(10px) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, rgba(99,179,237,0.25), rgba(159,122,234,0.25)) !important;
    border-color: rgba(99,179,237,0.6) !important;
    box-shadow: 0 4px 20px rgba(99,179,237,0.2) !important;
    transform: translateY(-1px) !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px dashed rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(10,10,20,0.95) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
    color: #4a5568 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
}
.stTabs [aria-selected="true"] {
    color: #63b3ed !important;
    border-bottom: 2px solid #63b3ed !important;
}

/* History table */
.history-row {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 16px;
}
</style>
""", unsafe_allow_html=True)

# ── Login Gate ────────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "login_user" not in st.session_state:
    st.session_state.login_user = ""
if "user_role" not in st.session_state:
    st.session_state.user_role = "user"

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center;padding:48px 0 32px">
            <div style="font-family:'Space Grotesk',sans-serif;font-size:2.5rem;font-weight:700;
                background:linear-gradient(135deg,#63b3ed,#9f7aea);-webkit-background-clip:text;
                -webkit-text-fill-color:transparent;background-clip:text;">🛡️ DeepGuard</div>
            <div style="color:#4a5568;font-size:0.8rem;letter-spacing:0.2em;text-transform:uppercase;margin-top:6px">
                AI Deepfake Detection System</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Sign In", "Create Account"])

        with tab1:
            st.markdown("")
            login_user = st.text_input("Username", placeholder="Enter your username", key="l_user")
            login_pass = st.text_input("Password", type="password", placeholder="Enter your password", key="l_pass")
            st.markdown("")
            if st.button("Sign In →", key="login_btn", use_container_width=True):
                if check_credentials(login_user, login_pass):
                    st.session_state.logged_in = True
                    st.session_state.login_user = login_user.strip().lower()
                    st.session_state.user_role = get_user_role(login_user.strip().lower())
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            st.markdown('<div style="text-align:center;color:#2d3748;font-size:0.75rem;margin-top:12px">Default: admin / admin@123</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown("")
            reg_user = st.text_input("Choose Username", placeholder="Min 3 characters", key="r_user")
            reg_pass = st.text_input("Password", type="password", placeholder="Min 6 characters", key="r_pass")
            reg_pass2 = st.text_input("Confirm Password", type="password", placeholder="Repeat password", key="r_pass2")
            st.markdown("")
            if st.button("Create Account →", key="reg_btn", use_container_width=True):
                if not reg_user or not reg_pass:
                    st.error("Please fill all fields")
                elif reg_pass != reg_pass2:
                    st.error("Passwords do not match")
                else:
                    success, msg = register_user(reg_user, reg_pass)
                    if success:
                        st.success("Account created! Please sign in.")
                    else:
                        st.error(msg)
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ── Session state ─────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "home"

# ── Helper functions ──────────────────────────────────────────────────────────
def analyze_text(text):
    import re
    if not text.strip(): return 0.0, "No text provided"
    if roberta_model is not None:
        try:
            import torch
            inputs = tokenizer(text[:512], return_tensors="pt", truncation=True, max_length=512, padding=True)
            with torch.no_grad():
                outputs = roberta_model(**inputs)
                probs = torch.softmax(outputs.logits, dim=-1)[0]
            fake_prob = float(probs[1])
            if fake_prob > 0.75: label = "Very likely AI-generated"
            elif fake_prob > 0.55: label = "Possibly AI-generated"
            elif fake_prob > 0.4: label = "Uncertain"
            else: label = "Likely human-written"
            return fake_prob, f"RoBERTa: {label} ({fake_prob:.0%})"
        except: pass
    score = 0.0; signals = []
    ai_phrases = ["furthermore","moreover","it is worth noting","in conclusion",
                  "it is important to note","delve into","in today's world","in the realm of"]
    found = [p for p in ai_phrases if p.lower() in text.lower()]
    score += min(len(found)*0.12, 0.4)
    if found: signals.append(f"AI phrases: {', '.join(found[:3])}")
    import re
    first_person = len(re.findall(r"\b(I|me|my|mine)\b", text, re.I))
    if first_person == 0 and len(text.split()) > 40:
        score += 0.2; signals.append("no first-person pronouns")
    return min(score,1.0), "Heuristic: " + " | ".join(signals) if signals else "No strong AI signals"

def show_result(score, explanation, label):
    verdict = "MANIPULATED" if score >= 0.75 else "AUTHENTIC" if score <= 0.30 else "UNCERTAIN"
    vc = {"AUTHENTIC":"verdict-authentic","MANIPULATED":"verdict-manipulated","UNCERTAIN":"verdict-uncertain"}[verdict]
    ve = {"AUTHENTIC":"✅","MANIPULATED":"🚨","UNCERTAIN":"⚠️"}[verdict]
    vm = {"AUTHENTIC":"Content Verified","MANIPULATED":"Manipulation Detected","UNCERTAIN":"Inconclusive"}[verdict]

    st.markdown(f'<div class="{vc}">{ve} {vm} &nbsp;·&nbsp; Score: {score:.0%}</div>', unsafe_allow_html=True)
    st.markdown("")
    save_scan(st.session_state.login_user, label, score, verdict, explanation)

    # Increment threat counter if not green
    if verdict in ("MANIPULATED", "UNCERTAIN"):
        if "threat_count" not in st.session_state:
            st.session_state.threat_count = 0
        st.session_state.threat_count += 1

    c1, c2 = st.columns([2,1])
    with c1:
        color = "#ef4444" if score>0.65 else "#10b981" if score<0.35 else "#f59e0b"
        fig = go.Figure(go.Bar(
            x=[label], y=[score*100], marker_color=color,
            text=[f"{score:.0%}"], textposition="outside",
            textfont=dict(color=color, size=16, family="Space Grotesk"),
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.02)",
            font=dict(color="#4a5568", family="Inter"),
            yaxis=dict(range=[0,120], gridcolor="rgba(255,255,255,0.05)", color="#4a5568"),
            xaxis=dict(color="#4a5568"),
            margin=dict(t=20,b=20,l=20,r=20), height=220, showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        gc = "#ef4444" if score>0.65 else "#10b981" if score<0.35 else "#f59e0b"
        fig2 = go.Figure(go.Indicator(
            mode="gauge+number", value=score*100,
            title={"text":"Threat Level","font":{"family":"Space Grotesk","color":"#4a5568","size":12}},
            number={"suffix":"%","font":{"family":"Space Grotesk","color":gc,"size":26}},
            gauge={
                "axis":{"range":[0,100],"tickcolor":"rgba(255,255,255,0.1)","tickfont":{"color":"#4a5568"}},
                "bar":{"color":gc,"thickness":0.6},
                "bgcolor":"rgba(255,255,255,0.02)",
                "bordercolor":"rgba(255,255,255,0.08)",
                "steps":[
                    {"range":[0,35],"color":"rgba(16,185,129,0.08)"},
                    {"range":[35,65],"color":"rgba(245,158,11,0.08)"},
                    {"range":[65,100],"color":"rgba(239,68,68,0.08)"},
                ],
            },
        ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#4a5568"),
            margin=dict(t=30,b=10,l=10,r=10), height=220,
        )
        st.plotly_chart(fig2, use_container_width=True)

    with st.expander("📊 Raw Analysis Signals"):
        st.code(explanation, language=None)

def back_button():
    if st.button("← Back to Home"):
        st.session_state.page = "home"; st.rerun()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:16px 0 8px">
        <div style="font-family:'Space Grotesk',sans-serif;font-size:1.1rem;font-weight:700;
            background:linear-gradient(135deg,#63b3ed,#9f7aea);-webkit-background-clip:text;
            -webkit-text-fill-color:transparent;background-clip:text;">🛡️ DeepGuard</div>
    </div>
    """, unsafe_allow_html=True)

    role = st.session_state.get("user_role", "user")
    st.markdown(f'<div style="font-size:0.8rem;color:#4a5568;margin-bottom:16px">{"👑" if role=="admin" else "👤"} {st.session_state.login_user}</div>', unsafe_allow_html=True)

    st.markdown("**Navigation**")
    pages = [("🏠", "Home", "home"), ("📊", "Dashboard", "dashboard"),
             ("📋", "Scan History", "history"), ("⚙️", "Settings", "settings"), ("ℹ️", "About", "about")]
    for icon, label, key in pages:
        active = "background:rgba(99,179,237,0.1);border-color:rgba(99,179,237,0.3);" if st.session_state.page == key else ""
        if st.button(f"{icon} {label}", key=f"nav_{key}", use_container_width=True):
            st.session_state.page = key; st.rerun()

    st.markdown("---")
    model_status = "🟢 Online" if roberta_model is not None else "🔴 Heuristic"
    st.markdown(f'<div style="font-size:0.75rem;color:#4a5568">Text Model: {model_status}</div>', unsafe_allow_html=True)
    st.markdown("")

    with st.expander("🔑 Change Password"):
        old_p = st.text_input("Current", type="password", key="cp_old")
        new_p = st.text_input("New", type="password", key="cp_new")
        if st.button("Update Password", key="cp_btn"):
            ok, msg = change_password(st.session_state.login_user, old_p, new_p)
            st.success(msg) if ok else st.error(msg)

    if role == "admin":
        with st.expander("👑 Admin Panel"):
            users = get_all_users()
            for u in users:
                c1, c2 = st.columns([2,1])
                with c1:
                    status = "🟢" if u["is_active"] else "🔴"
                    st.markdown(f'<div style="font-size:0.75rem;color:#94a3b8">{status} {u["username"]} ({u["role"]})</div>', unsafe_allow_html=True)
                with c2:
                    if u["username"] != "admin":
                        if st.button("⊘", key=f"del_{u['username']}", help="Delete"):
                            delete_user(u["username"]); st.rerun()

    st.markdown("---")
    if st.button("Sign Out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.login_user = ""
        st.session_state.page = "home"
        st.rerun()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="main-header">
    <div class="logo-text">🛡️ DeepGuard</div>
    <div class="logo-sub">Multimodal AI Detection System</div>
</div>
<hr class="glass-divider">
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HOME PAGE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "home":
    history = load_history()
    user_scans = [h for h in history if h["user"] == st.session_state.login_user]
    total_scans = len(user_scans)
    threats = len([h for h in user_scans if h["verdict"] in ("MANIPULATED", "UNCERTAIN")])
    authentic = len([h for h in user_scans if h["verdict"] == "AUTHENTIC"])

    # Persist threat count in session
    if "threat_count" not in st.session_state:
        st.session_state.threat_count = threats
    else:
        st.session_state.threat_count = threats

    c1, c2, c3, c4 = st.columns(4)
    for col, num, label, color in [
        (c1, total_scans, "Total Scans", "#63b3ed"),
        (c2, st.session_state.threat_count, "Threats Detected", "#ef4444"),
        (c3, authentic, "Verified Clean", "#10b981"),
        (c4, len(history), "Global Scans", "#9f7aea"),
    ]:
        with col:
            st.markdown(f'<div class="stat-card"><div class="stat-num" style="color:{color}">{num}</div><div class="stat-label">{label}</div></div>', unsafe_allow_html=True)

    st.markdown("")
    st.markdown("### Detection Modules")

    c1, c2, c3, c4, c5 = st.columns(5)
    modules = [
        (c1, "📝", "Text", "AI-generated text", "text"),
        (c2, "🖼️", "Image", "Deepfake images", "image"),
        (c3, "🎙️", "Audio", "Synthetic voice", "audio"),
        (c4, "🎬", "Video", "Deepfake video", "video"),
        (c5, "⚡", "Full Scan", "All modalities", "full"),
    ]
    for col, icon, title, desc, key in modules:
        with col:
            st.markdown(f'<div class="nav-glass"><div class="nav-icon">{icon}</div><div class="nav-title">{title}</div><div class="nav-desc">{desc}</div></div>', unsafe_allow_html=True)
            if st.button(f"Scan", key=f"btn_{key}", use_container_width=True):
                st.session_state.page = key; st.rerun()

    if user_scans:
        st.markdown("")
        st.markdown("### Recent Scans")
        for scan in reversed(user_scans[-5:]):
            color = "#ef4444" if scan["verdict"]=="MANIPULATED" else "#10b981" if scan["verdict"]=="AUTHENTIC" else "#f59e0b"
            emoji = "🚨" if scan["verdict"]=="MANIPULATED" else "✅" if scan["verdict"]=="AUTHENTIC" else "⚠️"
            st.markdown(f"""
            <div class="glass-card" style="padding:14px 20px">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <div>
                        <span style="font-size:0.85rem;font-weight:600;color:#e2e8f0">{emoji} {scan['modality']}</span>
                        <span style="font-size:0.75rem;color:#4a5568;margin-left:12px">{scan['timestamp']}</span>
                    </div>
                    <div style="font-family:'Space Grotesk',sans-serif;font-weight:700;color:{color}">{scan['score']}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD PAGE
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "dashboard":
    st.markdown('<div class="page-header">📊 Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Analytics and detection insights</div>', unsafe_allow_html=True)

    history = load_history()
    if not history:
        st.markdown('<div class="glass-card" style="text-align:center;padding:48px"><div style="color:#4a5568">No scan data yet. Start scanning to see analytics!</div></div>', unsafe_allow_html=True)
    else:
        c1, c2 = st.columns(2)
        with c1:
            # Verdict distribution
            verdicts = [h["verdict"] for h in history]
            v_counts = {"AUTHENTIC": verdicts.count("AUTHENTIC"), "MANIPULATED": verdicts.count("MANIPULATED"), "UNCERTAIN": verdicts.count("UNCERTAIN")}
            # 3D Pie Chart
            fig = go.Figure(go.Pie(
                labels=list(v_counts.keys()),
                values=list(v_counts.values()),
                marker=dict(
                    colors=["#10b981", "#ef4444", "#f59e0b"],
                    line=dict(color="#0a0a0f", width=3),
                ),
                hole=0.55,
                textfont=dict(size=13, color="#e2e8f0"),
                pull=[0.08, 0.08, 0.04],
                rotation=45,
                direction="clockwise",
                textinfo="label+percent",
                insidetextorientation="radial",
            ))
            fig.update_layout(
                title=dict(text="Verdict Distribution", font=dict(color="#e2e8f0", family="Space Grotesk", size=15)),
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8"),
                height=340,
                margin=dict(t=50,b=20,l=20,r=20),
                showlegend=True,
                legend=dict(font=dict(color="#94a3b8"), bgcolor="rgba(0,0,0,0)"),
                annotations=[dict(
                    text=f"<b>{len(history)}</b><br><span style='font-size:11px'>Total</span>",
                    x=0.5, y=0.5,
                    font=dict(size=18, color="#e2e8f0", family="Space Grotesk"),
                    showarrow=False
                )],
            )
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            modalities = [h["modality"] for h in history]
            mod_counts = {}
            for m in modalities:
                mod_counts[m] = mod_counts.get(m, 0) + 1

            colors_main = ["#63b3ed","#9f7aea","#f59e0b","#10b981","#ef4444"][:len(mod_counts)]
            colors_dark = ["#1a3a5c","#2d2250","#5c3d10","#023c2a","#4a1010"][:len(mod_counts)]
            colors_mid  = ["#2b6cb0","#553c9a","#975a16","#047857","#9b2c2c"][:len(mod_counts)]

            import numpy as np

            fig2 = go.Figure()
            labels = list(mod_counts.keys())
            values = list(mod_counts.values())
            max_val = max(values) if values else 1

            for i, (label, val) in enumerate(zip(labels, values)):
                # Cylinder = filled scatter3d surface
                theta = np.linspace(0, 2*np.pi, 30)
                r = 0.3
                cx = i

                # Top circle
                x_top = cx + r * np.cos(theta)
                y_top = [val] * len(theta)
                z_top = r * np.sin(theta)

                # Bottom circle
                x_bot = cx + r * np.cos(theta)
                y_bot = [0] * len(theta)
                z_bot = r * np.sin(theta)

                # Side surface
                x_side = np.concatenate([x_top, x_bot])
                y_side = np.concatenate([y_top, y_bot])
                z_side = np.concatenate([z_top, z_bot])

                fig2.add_trace(go.Scatter3d(
                    x=x_side, y=y_side, z=z_side,
                    mode="lines",
                    line=dict(color=colors_dark[i], width=4),
                    showlegend=False, hoverinfo="skip",
                ))
                fig2.add_trace(go.Mesh3d(
                    x=np.concatenate([x_top, x_bot]),
                    y=np.array(y_top + y_bot),
                    z=np.concatenate([z_top, z_bot]),
                    alphahull=0,
                    color=colors_main[i],
                    opacity=0.9,
                    showlegend=False,
                    hovertemplate=f"<b>{label}</b><br>Count: {val}<extra></extra>",
                ))
                # Top cap
                fig2.add_trace(go.Scatter3d(
                    x=x_top, y=y_top, z=z_top,
                    mode="lines",
                    line=dict(color=colors_mid[i], width=3),
                    showlegend=False, hoverinfo="skip",
                ))
                # Label
                fig2.add_trace(go.Scatter3d(
                    x=[cx], y=[val + max_val*0.08], z=[0],
                    mode="text",
                    text=[f"<b>{val}</b>"],
                    textfont=dict(color="#e2e8f0", size=14, family="Space Grotesk"),
                    showlegend=False, hoverinfo="skip",
                ))

            fig2.update_layout(
                title=dict(text="Scans by Modality", font=dict(color="#e2e8f0", family="Space Grotesk", size=15), x=0.5),
                paper_bgcolor="rgba(0,0,0,0)",
                scene=dict(
                    bgcolor="rgba(10,10,20,0.8)",
                    xaxis=dict(
                        tickvals=list(range(len(labels))),
                        ticktext=labels,
                        tickfont=dict(color="#94a3b8", size=12),
                        gridcolor="rgba(255,255,255,0.04)",
                        showbackground=False,
                        zeroline=False,
                    ),
                    yaxis=dict(
                        gridcolor="rgba(255,255,255,0.04)",
                        tickfont=dict(color="#94a3b8"),
                        showbackground=False,
                        zeroline=False,
                        title=dict(text="Count", font=dict(color="#4a5568")),
                    ),
                    zaxis=dict(showticklabels=False, showgrid=False, zeroline=False, showbackground=False),
                    camera=dict(eye=dict(x=1.5, y=1.2, z=0.8)),
                    aspectmode="manual",
                    aspectratio=dict(x=2, y=1, z=0.4),
                ),
                font=dict(color="#94a3b8"),
                height=400,
                margin=dict(t=50,b=0,l=0,r=0),
            )
            st.plotly_chart(fig2, use_container_width=True)

        # 3D Score Distribution
        scores_list = [h["score"] for h in history]
        fig3 = go.Figure()
        # Shadow histogram
        fig3.add_trace(go.Histogram(
            x=scores_list, nbinsx=20,
            marker=dict(color="#1a365d", line=dict(width=0), cornerradius=6),
            opacity=1.0, showlegend=False, hoverinfo="skip",
            xbins=dict(start=0, end=100, size=5),
        ))
        # Main histogram
        fig3.add_trace(go.Histogram(
            x=scores_list, nbinsx=20,
            marker=dict(
                color="#63b3ed",
                line=dict(color="#0a0a0f", width=1),
                cornerradius=6,
                pattern=dict(shape="", solidity=0.85),
            ),
            opacity=0.9,
            name="Score",
            xbins=dict(start=0, end=100, size=5),
        ))
        # Gradient overlay lines for 3D feel
        for i, threshold in enumerate([35, 65]):
            fig3.add_vline(
                x=threshold,
                line=dict(color=["#10b981","#ef4444"][i], width=1.5, dash="dot"),
                annotation=dict(
                    text=["Safe","Danger"][i],
                    font=dict(color=["#10b981","#ef4444"][i], size=11),
                    bgcolor="rgba(0,0,0,0)",
                )
            )
        fig3.update_layout(
            title=dict(text="Score Distribution", font=dict(color="#e2e8f0", family="Space Grotesk", size=15)),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(255,255,255,0.02)",
            font=dict(color="#94a3b8"),
            height=300,
            barmode="overlay",
            xaxis=dict(
                title="Manipulation Score %",
                gridcolor="rgba(255,255,255,0.04)",
                color="#4a5568", zeroline=False, showline=False,
                range=[0, 100],
            ),
            yaxis=dict(
                title="Count",
                gridcolor="rgba(255,255,255,0.04)",
                color="#4a5568", zeroline=False, showline=False,
            ),
            margin=dict(t=50,b=40,l=40,r=20),
            shapes=[
                dict(type="rect", xref="paper", yref="paper",
                    x0=0, y0=0, x1=1, y1=1,
                    line=dict(color="rgba(99,179,237,0.1)", width=1),
                    fillcolor="rgba(0,0,0,0)", layer="below"),
                dict(type="rect", xref="x", yref="paper",
                    x0=0, y0=0, x1=35, y1=1,
                    fillcolor="rgba(16,185,129,0.04)", layer="below",
                    line=dict(width=0)),
                dict(type="rect", xref="x", yref="paper",
                    x0=65, y0=0, x1=100, y1=1,
                    fillcolor="rgba(239,68,68,0.04)", layer="below",
                    line=dict(width=0)),
            ],
        )
        st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# HISTORY PAGE
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "history":
    st.markdown('<div class="page-header">📋 Scan History</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">All previous detection results</div>', unsafe_allow_html=True)

    history = load_history()
    role = st.session_state.get("user_role", "user")

    # Filter
    col1, col2 = st.columns([2,1])
    with col1:
        filter_verdict = st.selectbox("Filter by verdict", ["All", "MANIPULATED", "AUTHENTIC", "UNCERTAIN"])
    with col2:
        show_all = st.checkbox("Show all users", value=False) if role == "admin" else False

    filtered = history
    if not show_all:
        filtered = [h for h in history if h["user"] == st.session_state.login_user]
    if filter_verdict != "All":
        filtered = [h for h in filtered if h["verdict"] == filter_verdict]

    if not filtered:
        st.markdown('<div class="glass-card" style="text-align:center;padding:48px"><div style="color:#4a5568">No scan history found.</div></div>', unsafe_allow_html=True)
    else:
        for scan in reversed(filtered):
            color = "#ef4444" if scan["verdict"]=="MANIPULATED" else "#10b981" if scan["verdict"]=="AUTHENTIC" else "#f59e0b"
            emoji = "🚨" if scan["verdict"]=="MANIPULATED" else "✅" if scan["verdict"]=="AUTHENTIC" else "⚠️"
            st.markdown(f"""
            <div class="glass-card" style="padding:16px 20px">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <div>
                        <span style="font-weight:600;color:#e2e8f0">{emoji} {scan['modality']}</span>
                        <span style="font-size:0.75rem;color:#4a5568;margin-left:12px">by {scan['user']} · {scan['timestamp']}</span>
                    </div>
                    <div style="font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:1.1rem;color:{color}">{scan['score']}%</div>
                </div>
                <div style="font-size:0.75rem;color:#4a5568;margin-top:6px">{scan.get('details','')[:100]}</div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SETTINGS PAGE
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "settings":
    st.markdown('<div class="page-header">⚙️ Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Configure your DeepGuard experience</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("**Account Settings**")
    st.markdown(f"Username: `{st.session_state.login_user}`")
    st.markdown(f"Role: `{st.session_state.get('user_role','user')}`")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("**Change Password**")
    old_p = st.text_input("Current Password", type="password", key="s_old")
    new_p = st.text_input("New Password", type="password", key="s_new")
    new_p2 = st.text_input("Confirm New Password", type="password", key="s_new2")
    if st.button("Update Password", key="s_update"):
        if new_p != new_p2:
            st.error("Passwords don't match")
        else:
            ok, msg = change_password(st.session_state.login_user, old_p, new_p)
            st.success(msg) if ok else st.error(msg)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("**Detection Settings**")
    st.markdown(f"Text Model: {'✅ RoBERTa Loaded' if roberta_model is not None else '⚠️ Heuristic Mode'}")
    st.markdown("Image Analysis: ✅ EXIF + Metadata")
    st.markdown("Audio Analysis: ✅ Spectral Features")
    st.markdown("Video Analysis: ⚠️ Beta (Frame Sampling)")
    gemini_key = st.text_input("Gemini API Key (for enhanced image analysis)", type="password", key="settings_gemini")
    if gemini_key:
        st.session_state.gemini_key = gemini_key
        st.success("✅ Gemini API key saved!")
    st.markdown('<div style="font-size:0.75rem;color:#4a5568">Get free key: <a href="https://aistudio.google.com" target="_blank" style="color:#63b3ed">aistudio.google.com</a></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.get("user_role") == "admin":
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("**Admin: Clear Scan History**")
        if st.button("🗑️ Clear All History", key="clear_history"):
            with open(HISTORY_FILE, "w") as f:
                json.dump([], f)
            st.success("History cleared!")
        st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ABOUT PAGE
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "about":
    st.markdown('<div class="page-header">ℹ️ About DeepGuard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Multimodal AI-powered deepfake detection system</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card">
        <h3 style="color:#e2e8f0;font-family:'Space Grotesk',sans-serif">What is DeepGuard?</h3>
        <p style="color:#94a3b8;line-height:1.8">DeepGuard is a multimodal AI detection system capable of analyzing text, images, audio, and video to identify manipulated or synthetic content. It uses state-of-the-art machine learning models to detect inconsistencies across multiple media formats.</p>
    </div>

    <div class="glass-card">
        <h3 style="color:#e2e8f0;font-family:'Space Grotesk',sans-serif">Detection Methods</h3>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:12px">
            <div style="background:rgba(99,179,237,0.05);border:1px solid rgba(99,179,237,0.15);border-radius:12px;padding:16px">
                <div style="font-size:1.5rem;margin-bottom:8px">📝</div>
                <div style="font-weight:600;color:#e2e8f0;margin-bottom:4px">Text Detection</div>
                <div style="font-size:0.8rem;color:#4a5568">RoBERTa transformer model trained on GPT-2/ChatGPT outputs. Detects statistical patterns unique to AI-generated text.</div>
            </div>
            <div style="background:rgba(159,122,234,0.05);border:1px solid rgba(159,122,234,0.15);border-radius:12px;padding:16px">
                <div style="font-size:1.5rem;margin-bottom:8px">🖼️</div>
                <div style="font-weight:600;color:#e2e8f0;margin-bottom:4px">Image Detection</div>
                <div style="font-size:0.8rem;color:#4a5568">EXIF metadata analysis combined with GPT-4o vision. AI-generated images lack real camera signatures.</div>
            </div>
            <div style="background:rgba(245,158,11,0.05);border:1px solid rgba(245,158,11,0.15);border-radius:12px;padding:16px">
                <div style="font-size:1.5rem;margin-bottom:8px">🎙️</div>
                <div style="font-weight:600;color:#e2e8f0;margin-bottom:4px">Audio Detection</div>
                <div style="font-size:0.8rem;color:#4a5568">Spectral analysis using librosa. Detects unnatural flatness, MFCC uniformity, and pitch consistency in TTS audio.</div>
            </div>
            <div style="background:rgba(16,185,129,0.05);border:1px solid rgba(16,185,129,0.15);border-radius:12px;padding:16px">
                <div style="font-size:1.5rem;margin-bottom:8px">🎬</div>
                <div style="font-weight:600;color:#e2e8f0;margin-bottom:4px">Video Detection</div>
                <div style="font-size:0.8rem;color:#4a5568">Frame-level analysis with EfficientNet + MTCNN face detection. Checks inter-frame consistency for deepfake artifacts.</div>
            </div>
        </div>
    </div>

    <div class="glass-card">
        <h3 style="color:#e2e8f0;font-family:'Space Grotesk',sans-serif">Technology Stack</h3>
        <div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:12px">
            <span style="background:rgba(99,179,237,0.1);border:1px solid rgba(99,179,237,0.2);border-radius:20px;padding:4px 12px;font-size:0.8rem;color:#63b3ed">Python</span>
            <span style="background:rgba(99,179,237,0.1);border:1px solid rgba(99,179,237,0.2);border-radius:20px;padding:4px 12px;font-size:0.8rem;color:#63b3ed">Streamlit</span>
            <span style="background:rgba(99,179,237,0.1);border:1px solid rgba(99,179,237,0.2);border-radius:20px;padding:4px 12px;font-size:0.8rem;color:#63b3ed">PyTorch</span>
            <span style="background:rgba(99,179,237,0.1);border:1px solid rgba(99,179,237,0.2);border-radius:20px;padding:4px 12px;font-size:0.8rem;color:#63b3ed">HuggingFace Transformers</span>
            <span style="background:rgba(99,179,237,0.1);border:1px solid rgba(99,179,237,0.2);border-radius:20px;padding:4px 12px;font-size:0.8rem;color:#63b3ed">librosa</span>
            <span style="background:rgba(99,179,237,0.1);border:1px solid rgba(99,179,237,0.2);border-radius:20px;padding:4px 12px;font-size:0.8rem;color:#63b3ed">OpenCV</span>
            <span style="background:rgba(99,179,237,0.1);border:1px solid rgba(99,179,237,0.2);border-radius:20px;padding:4px 12px;font-size:0.8rem;color:#63b3ed">MySQL</span>
            <span style="background:rgba(99,179,237,0.1);border:1px solid rgba(99,179,237,0.2);border-radius:20px;padding:4px 12px;font-size:0.8rem;color:#63b3ed">Plotly</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SCAN PAGES
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "text":
    back_button()
    st.markdown('<div class="page-header">📝 Text Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Detect AI-generated or manipulated text</div>', unsafe_allow_html=True)

    text_input = st.text_area("Paste text to analyze", height=200, placeholder="Paste any article, post, essay, or message here...")
    if st.button("⚡ Analyze Text", use_container_width=True):
        if not text_input.strip():
            st.warning("Please paste some text first!")
        else:
            with st.spinner("Analyzing text patterns..."):
                score, explanation = analyze_text(text_input)
            show_result(score, explanation, "TEXT")

elif st.session_state.page == "image":
    back_button()
    st.markdown('<div class="page-header">🖼️ Image Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Detect AI-generated or manipulated images</div>', unsafe_allow_html=True)

    image_file = st.file_uploader("Upload image", type=["jpg","jpeg","png","webp"])
    gemini_key = st.session_state.get("gemini_key", "")
    if gemini_key:
        st.markdown('<div style="font-size:0.75rem;color:#10b981;margin-bottom:8px">✅ Gemini Vision active</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size:0.75rem;color:#4a5568;margin-bottom:8px">⚠️ Add Gemini API key in Settings for better accuracy</div>', unsafe_allow_html=True)
    if st.button("⚡ Analyze Image", use_container_width=True):
        if not image_file:
            st.warning("Please upload an image!")
        else:
            with st.spinner("Scanning image artifacts..."):
                from detectors.image_detector import analyze_image
                score, explanation = analyze_image(image_file, gemini_key=gemini_key)
            show_result(score, explanation, "IMAGE")

elif st.session_state.page == "audio":
    back_button()
    st.markdown('<div class="page-header">🎙️ Audio Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Detect synthetic or TTS-generated audio</div>', unsafe_allow_html=True)

    audio_file = st.file_uploader("Upload audio", type=["wav","mp3","ogg"])
    if audio_file:
        st.audio(audio_file)
    if st.button("⚡ Analyze Audio", use_container_width=True):
        if not audio_file:
            st.warning("Please upload an audio file!")
        else:
            with st.spinner("Processing audio spectrum..."):
                from detectors.audio_detector import analyze_audio
                score, explanation = analyze_audio(audio_file)
            show_result(score, explanation, "AUDIO")

elif st.session_state.page == "video":
    back_button()
    st.markdown('<div class="page-header">🎬 Video Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Detect deepfake videos using frame analysis <span style="background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.3);border-radius:20px;padding:2px 8px;font-size:0.7rem;color:#f59e0b">Beta</span></div>', unsafe_allow_html=True)

    video_file = st.file_uploader("Upload video", type=["mp4","mov","avi"])
    if st.button("⚡ Analyze Video", use_container_width=True):
        if not video_file:
            st.warning("Please upload a video file!")
        else:
            with st.spinner("Scanning video frames..."):
                from detectors.video_detector import analyze_video
                score, explanation = analyze_video(video_file)
            show_result(score, explanation, "VIDEO")

elif st.session_state.page == "full":
    back_button()
    st.markdown('<div class="page-header">⚡ Full Multimodal Scan</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Analyze all modalities simultaneously</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        text_input = st.text_area("📝 Text", height=120, placeholder="Optional...")
        image_file = st.file_uploader("🖼️ Image", type=["jpg","jpeg","png","webp"])
    with col2:
        audio_file = st.file_uploader("🎙️ Audio", type=["wav","mp3","ogg"])
        video_file = st.file_uploader("🎬 Video", type=["mp4","mov","avi"])

    if st.button("⚡ Run Full Scan", use_container_width=True):
        if not any([text_input.strip(), image_file, audio_file, video_file]):
            st.warning("Upload at least one file!")
        else:
            from detectors.image_detector import analyze_image
            from detectors.audio_detector import analyze_audio
            from detectors.video_detector import analyze_video
            from fusion import compute_verdict

            scores = {}; explanations = {}
            total = sum([bool(text_input.strip()), bool(image_file), bool(audio_file), bool(video_file)])
            prog = st.progress(0); status = st.empty(); step = 0

            def upd(s, t, msg):
                prog.progress(int(s/t*100))
                status.markdown(f'<div style="color:#63b3ed;font-size:0.8rem">{msg}</div>', unsafe_allow_html=True)
                time.sleep(0.2)

            if text_input.strip():
                upd(step+0.5,total,"Analyzing text..."); sc,ex=analyze_text(text_input)
                scores["TEXT"]=sc; explanations["TEXT"]=ex; step+=1; upd(step,total,"✓ Text done")
            if image_file:
                upd(step+0.5,total,"Scanning image..."); sc,ex=analyze_image(image_file, gemini_key=st.session_state.get("gemini_key",""))
                scores["IMAGE"]=sc; explanations["IMAGE"]=ex; step+=1; upd(step,total,"✓ Image done")
            if audio_file:
                upd(step+0.5,total,"Processing audio..."); sc,ex=analyze_audio(audio_file)
                scores["AUDIO"]=sc; explanations["AUDIO"]=ex; step+=1; upd(step,total,"✓ Audio done")
            if video_file:
                upd(step+0.5,total,"Scanning video..."); sc,ex=analyze_video(video_file)
                scores["VIDEO"]=sc; explanations["VIDEO"]=ex; step+=1; upd(step,total,"✓ Video done")

            prog.empty(); status.empty()
            from fusion import compute_verdict
            verdict, final_score = compute_verdict({k.lower():v for k,v in scores.items()})
            vc = {"AUTHENTIC":"verdict-authentic","MANIPULATED":"verdict-manipulated","UNCERTAIN":"verdict-uncertain"}[verdict]
            ve = {"AUTHENTIC":"✅","MANIPULATED":"🚨","UNCERTAIN":"⚠️"}[verdict]
            vm = {"AUTHENTIC":"Content Verified","MANIPULATED":"Manipulation Detected","UNCERTAIN":"Inconclusive"}[verdict]

            st.markdown(f'<div class="{vc}">{ve} {vm} &nbsp;·&nbsp; Fusion Score: {final_score:.0%}</div>', unsafe_allow_html=True)
            save_scan(st.session_state.login_user, "FULL SCAN", final_score, verdict)
            st.markdown("")

            if scores:
                labels = list(scores.keys())
                values = [v*100 for v in scores.values()]
                colors = ["#ef4444" if v>65 else "#10b981" if v<35 else "#f59e0b" for v in values]
                fig = go.Figure(go.Bar(x=labels, y=values, marker_color=colors,
                    text=[f"{v:.0f}%" for v in values], textposition="outside",
                    textfont=dict(color=colors, size=14, family="Space Grotesk")))
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.02)",
                    font=dict(color="#4a5568"), yaxis=dict(range=[0,120],gridcolor="rgba(255,255,255,0.05)"),
                    margin=dict(t=20,b=20,l=20,r=20), height=260, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

                cols = st.columns(len(scores))
                emoji = {"TEXT":"📝","IMAGE":"🖼️","AUDIO":"🎙️","VIDEO":"🎬"}
                for i,(mod,sc) in enumerate(scores.items()):
                    with cols[i]:
                        color = "#ef4444" if sc>0.65 else "#10b981" if sc<0.35 else "#f59e0b"
                        risk = "High Risk" if sc>0.65 else "Clean" if sc<0.35 else "Suspicious"
                        st.markdown(f'<div class="glass-card" style="text-align:center"><div style="font-size:1.5rem">{emoji[mod]}</div><div style="font-family:Space Grotesk,sans-serif;font-size:1.3rem;font-weight:700;color:{color}">{sc:.0%}</div><div style="font-size:0.75rem;color:#4a5568">{risk}</div></div>', unsafe_allow_html=True)