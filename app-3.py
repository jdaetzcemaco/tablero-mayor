import streamlit as st
import requests
from datetime import datetime, timezone
import time

# ─── Config ───────────────────────────────────────────────
WEBHOOK_URL = "https://jcdcemaco.app.n8n.cloud/webhook/agent-status"
REFRESH_SECONDS = 60

STATUS_CONFIG = {
    "available":  {"label": "Disponible",         "icon": "🟢", "color": "#22c55e"},
    "on_call":    {"label": "En llamada",          "icon": "📞", "color": "#f59e0b"},
    "busy":       {"label": "Atendiendo ticket",   "icon": "🔵", "color": "#3b82f6"},
    "away":       {"label": "Fuera de escritorio", "icon": "🔴", "color": "#6b7280"},
}

STATUS_ORDER = ["on_call", "busy", "available", "away"]

# ─── Page setup ───────────────────────────────────────────
st.set_page_config(
    page_title="Tablero Mayor — CEMACO",
    page_icon="📋",
    layout="wide",
)


# ─── Helpers ──────────────────────────────────────────────
def time_since(iso_str):
    if not iso_str:
        return "—"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        diff = int((datetime.now(timezone.utc) - dt).total_seconds())
        if diff < 60: return f"{diff}s"
        if diff < 3600: return f"{diff // 60}m"
        return f"{diff // 3600}h {(diff % 3600) // 60}m"
    except:
        return "—"


@st.cache_data(ttl=REFRESH_SECONDS)
def get_agents():
    try:
        r = requests.get(WEBHOOK_URL, timeout=10)
        st.write(f"Status: {r.status_code}")
        st.write(f"Response: {r.text[:200]}")  # show first 200 chars
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list):
            agents = data
        elif isinstance(data, dict) and "agents" in data:
            agents = data["agents"]
        else:
            agents = [data]
        agents = [a for a in agents if isinstance(a, dict) and a.get("name")]
        return sorted(
            agents,
            key=lambda a: STATUS_ORDER.index(a.get("status", "away"))
            if a.get("status") in STATUS_ORDER else 99
        ), None
    except Exception as e:
        return [], f"{str(e)} | Response was: {r.text[:100] if 'r' in dir() else 'no response'}"


# ─── Header ───────────────────────────────────────────────
col_title, col_btn = st.columns([6, 1])
with col_title:
    st.caption("CEMACO · CONTACT CENTER · TABLERO MAYOR")
    st.title("Estado de Agentes")
with col_btn:
    st.write("")
    st.write("")
    if st.button("↻ Actualizar", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ─── Load data ────────────────────────────────────────────
agents, fetch_error = get_agents()

if fetch_error:
    st.error(f"⚠ Error conectando al webhook: {fetch_error}")

# ─── Metrics row ──────────────────────────────────────────
counts = {
    "on_call":   sum(1 for a in agents if a.get("status") == "on_call"),
    "busy":      sum(1 for a in agents if a.get("status") == "busy"),
    "available": sum(1 for a in agents if a.get("status") == "available"),
    "away":      sum(1 for a in agents if a.get("status") == "away"),
}
active_count = counts["on_call"] + counts["busy"] + counts["available"]

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Activos", f"{active_count}/{len(agents)}")
m2.metric("📞 En llamada", counts["on_call"])
m3.metric("🔵 En ticket", counts["busy"])
m4.metric("🟢 Disponibles", counts["available"])
m5.metric("🔴 Ausentes", counts["away"])

st.caption(f"Actualizado: {datetime.now().strftime('%H:%M:%S')} · Auto-refresh cada {REFRESH_SECONDS}s")
st.divider()

# ─── Filters ──────────────────────────────────────────────
col_f, col_s = st.columns([2, 3])
with col_f:
    filter_option = st.selectbox(
        "Estado",
        ["Todos", "📞 En llamada", "🔵 En ticket", "🟢 Disponibles", "🔴 Ausentes"],
        label_visibility="collapsed"
    )
with col_s:
    search = st.text_input("Buscar", placeholder="🔍  Nombre o email...", label_visibility="collapsed")

filter_map = {
    "Todos": "all",
    "📞 En llamada": "on_call",
    "🔵 En ticket": "busy",
    "🟢 Disponibles": "available",
    "🔴 Ausentes": "away"
}
selected_filter = filter_map[filter_option]

filtered = [
    a for a in agents
    if (selected_filter == "all" or a.get("status") == selected_filter)
    and (not search or
         search.lower() in a.get("name", "").lower() or
         search.lower() in a.get("email", "").lower())
]

st.divider()

# ─── Agent grid + detail panel ────────────────────────────
if "selected_agent" not in st.session_state:
    st.session_state.selected_agent = None

if not filtered:
    st.info("Sin agentes en este estado.")
else:
    if st.session_state.selected_agent:
        grid_col, detail_col = st.columns([3, 1])
    else:
        grid_col = st.container()
        detail_col = None

    # ── Agent cards ──
    with grid_col:
        cols = st.columns(3)
        for i, agent in enumerate(filtered):
            status = agent.get("status", "away")
            cfg = STATUS_CONFIG.get(status, STATUS_CONFIG["away"])
            name = agent.get("name", "Sin nombre")
            email = agent.get("email", "")
            tickets_count = agent.get("open_tickets_count", 0)
            last_active = time_since(agent.get("last_active_at"))
            avail_since = time_since(agent.get("available_since")) if agent.get("available_since") else None

            with cols[i % 3]:
                with st.container(border=True):
                    n_col, b_col = st.columns([3, 1])
                    with n_col:
                        st.markdown(f"**{name}**")
                    with b_col:
                        if tickets_count > 0:
                            st.caption(f"🎫 {tickets_count}")

                    st.markdown(f"{cfg['icon']} **{cfg['label']}**")

                    meta = f"Activo: {last_active}"
                    if avail_since:
                        meta += f" · Desde: {avail_since}"
                    st.caption(meta)

                    is_selected = st.session_state.selected_agent == email
                    btn_label = "✕ Cerrar" if is_selected else "Ver detalle"
                    if st.button(btn_label, key=f"btn_{email}", use_container_width=True):
                        st.session_state.selected_agent = None if is_selected else email
                        st.rerun()

    # ── Detail panel ──
    if detail_col:
        agent_data = next((a for a in agents if a.get("email") == st.session_state.selected_agent), None)
        if agent_data:
            with detail_col:
                with st.container(border=True):
                    status = agent_data.get("status", "away")
                    cfg = STATUS_CONFIG.get(status, STATUS_CONFIG["away"])
                    open_tickets = agent_data.get("open_tickets", [])

                    st.markdown(f"### {agent_data.get('name')}")
                    st.caption(agent_data.get("email"))
                    st.divider()

                    st.markdown(f"**{cfg['icon']} {cfg['label']}**")
                    st.caption(f"Último activo: {time_since(agent_data.get('last_active_at'))}")
                    st.divider()

                    s1, s2 = st.columns(2)
                    s1.metric("Tickets", agent_data.get("open_tickets_count", 0))
                    s2.metric("Disponible", time_since(agent_data.get("available_since")) if agent_data.get("available_since") else "—")

                    if open_tickets:
                        st.divider()
                        st.caption("TICKETS ACTIVOS")
                        for t in open_tickets:
                            ticket_type = t.get("type", "Ticket")
                            icon = "📞" if ticket_type == "Llamadas" else "🎫"
                            with st.container(border=True):
                                st.caption(f"{icon} {ticket_type} · #{t.get('id')}")
                                st.write(t.get("subject", ""))
                    else:
                        st.info("Sin tickets activos")

                    st.divider()
                    if st.button("✕ Cerrar panel", use_container_width=True):
                        st.session_state.selected_agent = None
                        st.rerun()

# ─── Auto-refresh ─────────────────────────────────────────
time.sleep(REFRESH_SECONDS)
st.rerun()
