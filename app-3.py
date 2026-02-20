import streamlit as st
import requests
from datetime import datetime
import time

# ─── Config ───────────────────────────────────────────────
WEBHOOK_URL = "https://jcdcemaco.app.n8n.cloud/webhook/agent-status"
REFRESH_SECONDS = 60

STATUS_CONFIG = {
    "available":  {"label": "Disponible",         "icon": "🟢", "color": "#22c55e"},
    "on_call":    {"label": "En llamada",          "icon": "📞", "color": "#f59e0b"},
    "busy":       {"label": "Atendiendo ticket",   "icon": "🔵", "color": "#3b82f6"},
    "away":       {"label": "Fuera de escritorio", "icon": "🔴", "color": "#ef4444"},
}

STATUS_ORDER = ["on_call", "busy", "available", "away"]

# ─── Page setup ───────────────────────────────────────────
st.set_page_config(
    page_title="Tablero Mayor — CEMACO",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ───────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .main > div { padding-top: 1.5rem; }
    .stApp { background: #080d18; color: #f1f5f9; }
    h1, h2, h3 { color: #f8fafc !important; font-weight: 700 !important; }
    .metric-card { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 16px 20px; text-align: center; }
    .metric-value { font-family: 'DM Mono', monospace; font-size: 32px; font-weight: 600; line-height: 1; margin-bottom: 4px; }
    .metric-label { font-family: 'DM Mono', monospace; font-size: 10px; letter-spacing: 0.1em; color: #475569; }
    .agent-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 14px 16px; margin-bottom: 8px; }
    .agent-name { font-weight: 600; font-size: 14px; color: #f1f5f9; margin-bottom: 4px; }
    .agent-status { font-family: 'DM Mono', monospace; font-size: 11px; letter-spacing: 0.04em; }
    .agent-meta { font-family: 'DM Mono', monospace; font-size: 9px; color: #334155; margin-top: 6px; }
    .ticket-badge { display: inline-block; background: rgba(255,255,255,0.07); border-radius: 5px; padding: 2px 8px; font-family: 'DM Mono', monospace; font-size: 10px; color: #64748b; float: right; }
    .top-bar { font-family: 'DM Mono', monospace; font-size: 9px; color: #3b82f6; letter-spacing: 0.18em; margin-bottom: 6px; }
    .ticket-row { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; padding: 8px 12px; margin-bottom: 6px; font-size: 12px; color: #94a3b8; }
    .ticket-type { font-family: 'DM Mono', monospace; font-size: 9px; border-radius: 4px; padding: 1px 6px; display: inline-block; margin-bottom: 3px; }
    .stButton > button { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.1) !important; color: #64748b !important; font-family: 'DM Mono', monospace !important; font-size: 11px !important; border-radius: 8px !important; }
    .stButton > button:hover { background: rgba(255,255,255,0.09) !important; color: #94a3b8 !important; }
    .stSelectbox > div > div { background: rgba(255,255,255,0.04) !important; border: 1px solid rgba(255,255,255,0.08) !important; color: #f1f5f9 !important; border-radius: 8px !important; font-family: 'DM Mono', monospace !important; font-size: 12px !important; }
    hr { border-color: rgba(255,255,255,0.06) !important; margin: 16px 0 !important; }
    .error-box { background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.2); border-radius: 10px; padding: 12px 16px; font-family: 'DM Mono', monospace; font-size: 11px; color: #ef4444; margin-bottom: 16px; }
    div[data-testid="stTextInput"] input { background: rgba(255,255,255,0.04) !important; border: 1px solid rgba(255,255,255,0.08) !important; color: #f1f5f9 !important; border-radius: 8px !important; font-family: 'DM Mono', monospace !important; font-size: 12px !important; }
</style>
""", unsafe_allow_html=True)


# ─── Helpers ──────────────────────────────────────────────
@st.cache_data(ttl=REFRESH_SECONDS)
def get_agents():
    try:
        r = requests.get(WEBHOOK_URL, timeout=10)
        r.raise_for_status()
        data = r.json()
        agents = data if isinstance(data, list) else [data]
        return sorted(
            agents,
            key=lambda a: STATUS_ORDER.index(a.get("status", "away"))
            if a.get("status") in STATUS_ORDER else 99
        ), None
    except Exception as e:
        return [], str(e)


def time_since(iso_str):
    if not iso_str:
        return "—"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        diff = int((datetime.now().astimezone() - dt).total_seconds())
        if diff < 60: return f"{diff}s"
        if diff < 3600: return f"{diff // 60}m"
        return f"{diff // 3600}h {(diff % 3600) // 60}m"
    except:
        return "—"


# ─── Header ───────────────────────────────────────────────
st.markdown('<div class="top-bar">CEMACO · CONTACT CENTER · TABLERO MAYOR</div>', unsafe_allow_html=True)

col_title, col_btn = st.columns([5, 1])
with col_title:
    st.markdown("## Estado de Agentes")
with col_btn:
    st.write("")
    if st.button("↻ Actualizar"):
        st.cache_data.clear()
        st.rerun()

# ─── Load data ────────────────────────────────────────────
agents, fetch_error = get_agents()

if fetch_error:
    st.markdown(f'<div class="error-box">⚠ Error: {fetch_error}</div>', unsafe_allow_html=True)

# ─── Metrics ──────────────────────────────────────────────
counts = {
    "on_call":   sum(1 for a in agents if a.get("status") == "on_call"),
    "busy":      sum(1 for a in agents if a.get("status") == "busy"),
    "available": sum(1 for a in agents if a.get("status") == "available"),
    "away":      sum(1 for a in agents if a.get("status") == "away"),
}
active_count = counts["on_call"] + counts["busy"] + counts["available"]

m1, m2, m3, m4, m5 = st.columns(5)
for col, (val, label, color) in zip(
    [m1, m2, m3, m4, m5],
    [
        (f"{active_count}/{len(agents)}", "ACTIVOS",      "#22c55e"),
        (counts["on_call"],              "EN LLAMADA",   "#f59e0b"),
        (counts["busy"],                 "EN TICKET",    "#3b82f6"),
        (counts["available"],            "DISPONIBLES",  "#22c55e"),
        (counts["away"],                 "AUSENTES",     "#ef4444"),
    ]
):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:{color}">{val}</div>
            <div class="metric-label">{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown(f'<div style="font-family:\'DM Mono\',monospace;font-size:9px;color:#334155;text-align:right;margin-top:6px;">Actualizado: {datetime.now().strftime("%H:%M:%S")} · Auto-refresh cada {REFRESH_SECONDS}s</div>', unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ─── Filters ──────────────────────────────────────────────
col_f, col_s = st.columns([2, 3])
with col_f:
    filter_option = st.selectbox(
        "Estado", ["Todos", "En llamada", "En ticket", "Disponibles", "Ausentes"],
        label_visibility="collapsed"
    )
with col_s:
    search = st.text_input("Buscar", placeholder="Nombre o email...", label_visibility="collapsed")

filter_map = {"Todos": "all", "En llamada": "on_call", "En ticket": "busy", "Disponibles": "available", "Ausentes": "away"}
selected_filter = filter_map[filter_option]

filtered = [
    a for a in agents
    if (selected_filter == "all" or a.get("status") == selected_filter)
    and (not search or search.lower() in a.get("name", "").lower() or search.lower() in a.get("email", "").lower())
]

st.markdown("<hr>", unsafe_allow_html=True)

# ─── Agent grid + detail panel ────────────────────────────
if "selected_agent" not in st.session_state:
    st.session_state.selected_agent = None

if not filtered:
    st.markdown('<div style="text-align:center;padding:60px;color:#334155;font-family:DM Mono,monospace;font-size:12px;">Sin agentes en este estado</div>', unsafe_allow_html=True)
else:
    has_selection = st.session_state.selected_agent is not None
    grid_col, detail_col = st.columns([3, 1]) if has_selection else (st.columns(1)[0], None)

    with grid_col:
        cols = st.columns(3)
        for i, agent in enumerate(filtered):
            status = agent.get("status", "away")
            cfg = STATUS_CONFIG.get(status, STATUS_CONFIG["away"])
            tickets_count = agent.get("open_tickets_count", 0)
            name = agent.get("name", "")
            email = agent.get("email", "")

            with cols[i % 3]:
                st.markdown(f"""
                <div class="agent-card" style="border-top:2px solid {cfg['color']}55;">
                    {'<span class="ticket-badge">' + str(tickets_count) + ' tkt</span>' if tickets_count > 0 else ''}
                    <div class="agent-name">{name}</div>
                    <div class="agent-status" style="color:{cfg['color']}">{cfg['icon']} {cfg['label']}</div>
                    <div class="agent-meta">ACTIVO {time_since(agent.get('last_active_at'))}{' · DESDE ' + time_since(agent.get('available_since')) if agent.get('available_since') else ''}</div>
                </div>""", unsafe_allow_html=True)

                if st.button("Ver detalle", key=f"btn_{email}", use_container_width=True):
                    st.session_state.selected_agent = None if st.session_state.selected_agent == email else email
                    st.rerun()

    # ─── Detail panel ─────────────────────────────────────
    if has_selection and detail_col:
        agent_data = next((a for a in agents if a.get("email") == st.session_state.selected_agent), None)
        if agent_data:
            with detail_col:
                status = agent_data.get("status", "away")
                cfg = STATUS_CONFIG.get(status, STATUS_CONFIG["away"])
                open_tickets = agent_data.get("open_tickets", [])

                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:14px;padding:18px;">
                    <div style="font-weight:700;font-size:15px;color:#f1f5f9;margin-bottom:2px;">{agent_data.get('name')}</div>
                    <div style="font-family:'DM Mono',monospace;font-size:9px;color:#334155;margin-bottom:14px;">{agent_data.get('email')}</div>
                    <div style="background:{cfg['color']}15;border:1px solid {cfg['color']}30;border-radius:8px;padding:10px 12px;margin-bottom:14px;">
                        <div style="font-family:'DM Mono',monospace;font-size:11px;color:{cfg['color']};">{cfg['icon']} {cfg['label'].upper()}</div>
                        <div style="font-family:'DM Mono',monospace;font-size:9px;color:#334155;margin-top:3px;">Último activo: {time_since(agent_data.get('last_active_at'))}</div>
                    </div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:14px;">
                        <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.05);border-radius:8px;padding:9px 10px;">
                            <div style="font-family:'DM Mono',monospace;font-size:8px;color:#334155;margin-bottom:3px;">TICKETS</div>
                            <div style="font-family:'DM Mono',monospace;font-size:18px;font-weight:600;">{agent_data.get('open_tickets_count', 0)}</div>
                        </div>
                        <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.05);border-radius:8px;padding:9px 10px;">
                            <div style="font-family:'DM Mono',monospace;font-size:8px;color:#334155;margin-bottom:3px;">DISPONIBLE</div>
                            <div style="font-family:'DM Mono',monospace;font-size:14px;font-weight:600;">{time_since(agent_data.get('available_since'))}</div>
                        </div>
                    </div>
                    {'<div style="font-family:DM Mono,monospace;font-size:9px;color:#334155;letter-spacing:0.08em;margin-bottom:8px;">TICKETS ACTIVOS</div>' if open_tickets else ''}
                    {''.join([f"""<div class="ticket-row"><span class="ticket-type" style="background:{'#f59e0b' if t.get('type') == 'Llamadas' else '#3b82f6'}22;color:{'#f59e0b' if t.get('type') == 'Llamadas' else '#3b82f6'};">{(t.get('type') or 'TICKET').upper()}</span> <span style="font-family:DM Mono,monospace;font-size:9px;color:#334155;">#{t.get('id')}</span><div style="margin-top:4px;">{t.get('subject','')}</div></div>""" for t in open_tickets]) if open_tickets else '<div style="text-align:center;padding:16px;color:#1e293b;font-family:DM Mono,monospace;font-size:10px;">Sin tickets activos</div>'}
                </div>""", unsafe_allow_html=True)

                if st.button("✕ Cerrar panel", use_container_width=True):
                    st.session_state.selected_agent = None
                    st.rerun()

# ─── Auto-refresh ─────────────────────────────────────────
time.sleep(REFRESH_SECONDS)
st.rerun()
