import math
from datetime import datetime
import pandas as pd
import streamlit as st

# CloudForge 2026 — local queue/worker scaling simulation.
# This demo does not connect to AWS or create real workers.

st.set_page_config(
    page_title="CloudForge 2026",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Theme ----------
st.markdown("""
<style>
:root { color-scheme: dark; }
.stApp {
    background:
      radial-gradient(ellipse at 15% 0%, rgba(24, 73, 155, .22), transparent 34%),
      radial-gradient(ellipse at 95% 100%, rgba(99, 45, 180, .16), transparent 32%),
      #06142c;
    color: #edf4ff;
}
[data-testid="stHeader"] { background: rgba(4, 15, 34, .8); }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #071a36 0%, #08152d 100%);
    border-right: 1px solid rgba(95, 140, 220, .22);
}
.block-container { padding-top: 1.4rem; padding-bottom: 2rem; max-width: 1600px; }
h1, h2, h3 { color: #f2f6ff !important; }
p, label, .stMarkdown { color: #d5e2fb; }
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(21, 48, 94, .94), rgba(13, 34, 72, .94));
    border: 1px solid rgba(80, 134, 230, .35);
    border-radius: 15px;
    padding: 16px 18px;
    min-height: 120px;
}
div[data-testid="stMetricLabel"] { color: #d9e6ff !important; }
div[data-testid="stMetricValue"] { color: #ffffff !important; }
div[data-testid="stMetricDelta"] { color: #69e4bd !important; }
.stButton > button {
    border: 1px solid rgba(108, 153, 255, .5);
    border-radius: 10px;
    min-height: 2.7rem;
    color: #fff;
    background: linear-gradient(100deg, #2369f5, #7550e9);
    font-weight: 650;
    transition: .15s ease;
}
.stButton > button:hover { border-color: #a9c6ff; filter: brightness(1.12); }
button[kind="secondary"] { background: rgba(28, 51, 88, .9); }
div[data-testid="stDataFrame"] {
    border: 1px solid rgba(90, 136, 218, .28);
    border-radius: 12px;
    overflow: hidden;
}
.cf-brand {
    display:flex; align-items:center; gap:14px; padding: 4px 0 18px 0;
}
.cf-logo {
    width:56px; height:56px; display:flex; align-items:center; justify-content:center;
    border-radius:17px; font-size:32px;
    background:linear-gradient(145deg, #123b70, #102448);
    border:1px solid rgba(70, 222, 222, .5);
}
.cf-title { font-size:32px; line-height:1.05; font-weight:850; letter-spacing:-.7px; color:#f2f6ff; }
.cf-title span { color:#7b8dff; }
.cf-tag { font-size:11px; letter-spacing:2px; color:#b5c9ec; margin-top:7px; }
.cf-pill {
    display:inline-block; padding:8px 14px; border-radius:999px;
    background:rgba(14, 122, 108, .22); border:1px solid rgba(47, 220, 178, .25);
    color:#a4ffe5; font-size:12px;
}
.cf-panel {
    background:linear-gradient(145deg, rgba(13, 35, 72, .92), rgba(8, 26, 56, .94));
    border:1px solid rgba(93, 137, 214, .3); border-radius:17px;
    padding:18px 20px; margin-bottom:14px;
}
.cf-panel h3 { margin-top:0; font-size:18px; }
.cf-note { color:#9bbce9; font-size:12px; }
.cf-status {
    padding:18px 20px; border-radius:14px; font-size:24px; font-weight:800;
    border:1px solid rgba(61, 231, 178, .5); background:rgba(0, 151, 115, .2);
}
hr { border-color: rgba(99, 143, 218, .22) !important; }
[data-testid="stProgress"] > div > div { background:linear-gradient(90deg,#27d8bc,#2876ff); }
</style>
""", unsafe_allow_html=True)

# ---------- State ----------
def init_state():
    defaults = {
        "queue_depth": 12,
        "history": [],
        "logs": [],
        "max_workers": 10,
        "tasks_per_worker": 5,
        "auto_record": True,
        "simulation_speed": "Normal",
        "page": "Dashboard",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    if "history" not in st.session_state or not isinstance(st.session_state.history, list):
        st.session_state.history = []
    if "logs" not in st.session_state or not isinstance(st.session_state.logs, list):
        st.session_state.logs = []
    if not st.session_state.history:
        snapshot("Initial state", record_log=False)

def now_text():
    return datetime.now().strftime("%I:%M:%S %p")

def estimated_workers(queue_depth=None):
    q = st.session_state.queue_depth if queue_depth is None else max(0, int(queue_depth))
    per_worker = max(1, int(st.session_state.tasks_per_worker))
    max_w = max(1, int(st.session_state.max_workers))
    return min(max_w, max(1, math.ceil(q / per_worker)))

def scaling_status(queue_depth=None):
    q = st.session_state.queue_depth if queue_depth is None else max(0, int(queue_depth))
    if q <= 5:
        return "SCALE DOWN", "⬇️", "Queue is light. Fewer workers may be enough."
    if q >= 20:
        return "SCALE UP", "⬆️", "High task load detected. Add worker capacity."
    return "STEADY", "➖", "Queue is within the steady operating range."

def add_log(message, level="INFO"):
    st.session_state.logs.insert(0, {
        "Time": now_text(),
        "Level": level,
        "Event": message,
        "Queue Depth": int(st.session_state.queue_depth),
        "Estimated Workers": estimated_workers(),
    })
    st.session_state.logs = st.session_state.logs[:200]

def snapshot(reason="Manual snapshot", record_log=True):
    q = int(st.session_state.queue_depth)
    st.session_state.history.append({
        "Time": now_text(),
        "Total Tasks": q,
        "Estimated Workers": estimated_workers(q),
        "Scaling Status": scaling_status(q)[0],
        "Event": reason,
    })
    st.session_state.history = st.session_state.history[-100:]
    if record_log:
        add_log(f"History recorded: {reason}")

def change_queue(amount, reason):
    old_q = int(st.session_state.queue_depth)
    st.session_state.queue_depth = max(0, old_q + int(amount))
    new_q = int(st.session_state.queue_depth)
    add_log(f"{reason} ({old_q} → {new_q})")
    if st.session_state.auto_record:
        snapshot(reason, record_log=False)
    if scaling_status(old_q)[0] != scaling_status(new_q)[0]:
        add_log(f"Scaling state changed to {scaling_status(new_q)[0]}", "WARN")

init_state()

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("""
    <div class="cf-brand">
      <div class="cf-logo">☁️</div>
      <div><div style="font-size:23px;font-weight:850;color:#f2f6ff;">CloudForge <span style="color:#8494ff">2026</span></div>
      <div class="cf-tag">SMART SCALING · HAPPY WORKERS</div></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="cf-pill">🟢 System Online · Local Demo</div>', unsafe_allow_html=True)
    st.markdown("---")
    pages = ["Dashboard", "Workers", "Queue", "Scaling", "Logs", "Settings"]
    icons = {"Dashboard":"⌂", "Workers":"▤", "Queue":"▦", "Scaling":"↗", "Logs":"▧", "Settings":"⚙"}
    for p in pages:
        if st.button(f"{icons[p]}  {p}", key=f"nav_{p}", use_container_width=True,
                     type="primary" if st.session_state.page == p else "secondary"):
            st.session_state.page = p
            st.rerun()
    st.markdown("---")
    st.markdown("<div style='color:#94afd9;font-size:13px;line-height:1.7'>Build<br>Scale<br>Innovate<br><br><span style='font-size:11px'>CloudForge 2026<br>Hackathon Prototype</span></div>", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown("""
<div class="cf-brand" style="justify-content:space-between;border-bottom:1px solid rgba(100,145,220,.2);margin-bottom:22px;">
  <div><div class="cf-title">CloudForge <span>2026</span></div>
  <div class="cf-tag">SMART SCALING • HAPPY WORKERS • SMOOTHER CLOUD</div></div>
  <div class="cf-pill">● &nbsp; System Online &nbsp; | &nbsp; Hackathon Demo</div>
</div>
""", unsafe_allow_html=True)

page = st.session_state.page
q = int(st.session_state.queue_depth)
workers = estimated_workers(q)
status, status_icon, status_message = scaling_status(q)
avg_processing = 2.3 if q < 20 else 3.1 if q < 35 else 4.2

# ---------- Dashboard ----------
if page == "Dashboard":
    st.title("Hello, Builder! 👋")
    st.caption("Welcome to CloudForge — Your Smart Worker Scaling Dashboard")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("▦  Queue Depth", q, "Pending tasks")
    m2.metric("♟  Active Workers", workers, "Estimated capacity")
    m3.metric("↗  Scaling Status", status, status_message)
    m4.metric("◷  Avg. Processing Time", f"{avg_processing:.1f} min", "Simulated per task")

    left, right = st.columns([1.04, 0.96], gap="large")
    with left:
        st.markdown('<div class="cf-panel"><h3>⚡ Live Task Generator</h3><div class="cf-note">Add demo tasks and see how your system scales.</div></div>', unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        with b1:
            if st.button("＋  Add 5 Demo Tasks", use_container_width=True, key="add5"):
                change_queue(5, "Added 5 demo tasks")
                st.rerun()
        with b2:
            if st.button("⚡  Auto Generate 10 Tasks", use_container_width=True, key="add10"):
                change_queue(10, "Auto-generated 10 demo tasks")
                st.rerun()
        b3, b4 = st.columns([1, 1])
        with b3:
            if st.button("✓  Process 5 Tasks", use_container_width=True, key="process5", type="secondary"):
                change_queue(-5, "Processed up to 5 tasks")
                st.rerun()
        with b4:
            if st.button("↻  Reset Task Counter", use_container_width=True, key="reset", type="secondary"):
                st.session_state.queue_depth = 0
                add_log("Task counter reset", "WARN")
                snapshot("Reset task counter", record_log=False)
                st.rerun()
        a, b = st.columns(2)
        with a:
            st.metric("Total Demo Tasks Added", q)
        with b:
            st.metric("Estimated Workers Needed", workers)
        st.caption("ℹ️ Local simulation only — these are demo tasks, not real AWS SQS messages.")
    with right:
        st.markdown('<div class="cf-panel"><h3>🧠 Scaling Decision Panel</h3></div>', unsafe_allow_html=True)
        if status == "SCALE UP":
            st.markdown(f'<div class="cf-status" style="background:rgba(0,155,119,.22);border-color:#0ecda4">⬆️ &nbsp; SCALE UP<br><span style="font-size:14px;font-weight:450">{status_message}</span></div>', unsafe_allow_html=True)
        elif status == "SCALE DOWN":
            st.markdown(f'<div class="cf-status" style="background:rgba(31,105,204,.2);border-color:#4597ff">⬇️ &nbsp; SCALE DOWN<br><span style="font-size:14px;font-weight:450">{status_message}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="cf-status" style="background:rgba(173,128,35,.15);border-color:#b99b42">➖ &nbsp; STEADY<br><span style="font-size:14px;font-weight:450">{status_message}</span></div>', unsafe_allow_html=True)
        st.write("")
        c1, c2, c3 = st.columns(3)
        c1.metric("≤ 5 tasks", "SCALE DOWN")
        c2.metric("6–19 tasks", "STEADY")
        c3.metric("≥ 20 tasks", "SCALE UP")
        st.caption("ℹ️ Demo simulation: this panel does not create or remove real cloud workers.")

    st.markdown("---")
    left_chart, right_table = st.columns([1.04, 0.96], gap="large")
    with left_chart:
        st.markdown("### 📈 Task & Worker Trends")
        mode = st.segmented_control("Show trend", ["Tasks", "Workers"], default="Tasks", key="trend_mode")
        hist = st.session_state.history
        if hist:
            df = pd.DataFrame(hist)
            df["Snapshot"] = range(1, len(df) + 1)
            if mode == "Tasks":
                chart_df = df.set_index("Snapshot")[["Total Tasks"]].rename(columns={"Total Tasks":"Total Tasks"})
            else:
                chart_df = df.set_index("Snapshot")[["Estimated Workers"]].rename(columns={"Estimated Workers":"Estimated Workers"})
            st.line_chart(chart_df, height=260, use_container_width=True)
        else:
            st.info("Add tasks to start the trend chart.")
        st.caption("Trend points are saved during this app session.")
    with right_table:
        st.markdown("### 📋 Task History")
        if st.button("📝 Record Current Task Count", use_container_width=True, key="record_history"):
            snapshot("Manual snapshot")
            st.rerun()
        if st.session_state.history:
            hdf = pd.DataFrame(st.session_state.history[::-1])
            hdf.insert(0, "#", range(len(hdf), 0, -1))
            st.dataframe(hdf[["#", "Total Tasks", "Estimated Workers", "Scaling Status", "Time", "Event"]].head(8),
                         use_container_width=True, hide_index=True)
        else:
            st.info("No history yet.")
        st.caption("Session-based history may reset when the app restarts.")

# ---------- Workers ----------
elif page == "Workers":
    st.title("👷 Worker Overview")
    st.caption("Worker count is calculated from queue depth and your configured tasks-per-worker target.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Estimated Active Workers", workers)
    c2.metric("Maximum Workers", st.session_state.max_workers)
    c3.metric("Tasks per Worker", st.session_state.tasks_per_worker)
    st.progress(min(1.0, workers / max(1, st.session_state.max_workers)), text=f"Estimated capacity used: {workers}/{st.session_state.max_workers}")
    worker_rows = []
    for i in range(1, workers + 1):
        assigned = min(st.session_state.tasks_per_worker, max(0, q - (i - 1) * st.session_state.tasks_per_worker))
        worker_rows.append({"Worker": f"worker-{i:02d}", "Status": "Processing" if assigned else "Idle", "Assigned Tasks": assigned, "Mode": "Simulated"})
    st.subheader("Worker Pool")
    st.dataframe(pd.DataFrame(worker_rows), use_container_width=True, hide_index=True)
    st.info("These are simulated worker records. No cloud instances or background workers are created.")

# ---------- Queue ----------
elif page == "Queue":
    st.title("📥 Queue Monitor")
    st.caption("Manage the simulated pending task count.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Pending Tasks", q)
    c2.metric("Queue State", "Busy" if q >= 20 else "Light" if q <= 5 else "Normal")
    c3.metric("Suggested Workers", workers)
    st.progress(min(1.0, q / 50), text=f"Queue load indicator: {min(q, 50)}/50")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Add 1 Task", use_container_width=True, key="q_add1"):
            change_queue(1, "Added 1 task"); st.rerun()
    with col2:
        if st.button("Process 1 Task", use_container_width=True, key="q_process1"):
            change_queue(-1, "Processed 1 task"); st.rerun()
    with col3:
        if st.button("Clear Queue", use_container_width=True, key="q_clear"):
            st.session_state.queue_depth = 0
            add_log("Queue cleared", "WARN")
            snapshot("Queue cleared", record_log=False); st.rerun()
    st.subheader("Recent queue snapshots")
    if st.session_state.history:
        st.dataframe(pd.DataFrame(st.session_state.history[::-1]).head(15), use_container_width=True, hide_index=True)
    else:
        st.info("No snapshots recorded yet.")

# ---------- Scaling ----------
elif page == "Scaling":
    st.title("⚙️ Scaling Policy")
    st.caption("Thresholds are configurable for this local simulation.")
    st.markdown('<div class="cf-panel"><h3>Current Decision</h3></div>', unsafe_allow_html=True)
    st.markdown(f"### {status_icon} {status}")
    st.write(status_message)
    st.write(f"Current queue depth: **{q}** · Estimated workers: **{workers}**")
    st.markdown("---")
    st.subheader("Policy reference")
    st.dataframe(pd.DataFrame([
        {"Queue Depth": "0–5", "Decision": "SCALE DOWN", "Reason": "Low workload"},
        {"Queue Depth": "6–19", "Decision": "STEADY", "Reason": "Normal workload"},
        {"Queue Depth": "20+", "Decision": "SCALE UP", "Reason": "High workload"},
    ]), use_container_width=True, hide_index=True)
    st.info("This rule-based policy is a prototype, not a production autoscaler. Real autoscaling needs monitoring, safety limits, and cloud integration.")

# ---------- Logs ----------
elif page == "Logs":
    st.title("🗒️ Activity Logs")
    st.caption("Recent events from the local simulation.")
    c1, c2 = st.columns([1, 5])
    with c1:
        if st.button("Clear Logs", use_container_width=True):
            st.session_state.logs = []
            st.rerun()
    if st.session_state.logs:
        log_df = pd.DataFrame(st.session_state.logs)
        st.dataframe(log_df, use_container_width=True, hide_index=True)
        csv = log_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download logs as CSV", data=csv, file_name="cloudforge_logs.csv", mime="text/csv")
    else:
        st.info("No log entries yet. Use the task generator to create activity.")

# ---------- Settings ----------
elif page == "Settings":
    st.title("🛠️ Settings")
    st.caption("Change the local demo's worker estimation rules.")
    with st.form("settings_form"):
        max_workers = st.slider("Maximum estimated workers", min_value=1, max_value=50, value=int(st.session_state.max_workers))
        tasks_per_worker = st.slider("Tasks per worker", min_value=1, max_value=20, value=int(st.session_state.tasks_per_worker))
        auto_record = st.checkbox("Automatically record history when queue changes", value=bool(st.session_state.auto_record))
        submitted = st.form_submit_button("Save Settings", use_container_width=True)
        if submitted:
            st.session_state.max_workers = max_workers
            st.session_state.tasks_per_worker = tasks_per_worker
            st.session_state.auto_record = auto_record
            add_log("Settings updated")
            snapshot("Settings updated", record_log=False)
            st.success("Settings saved for this session.")
            st.rerun()
    st.markdown("---")
    st.subheader("Reset demo data")
    st.warning("This clears the current queue, history, and logs for this browser session.")
    if st.button("Reset Entire Demo", type="secondary"):
        st.session_state.queue_depth = 0
        st.session_state.history = []
        st.session_state.logs = []
        snapshot("Fresh demo state", record_log=False)
        add_log("Demo reset", "WARN")
        st.success("Demo reset complete.")
        st.rerun()

st.markdown("---")
st.markdown("<div style='display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;color:#8da9d4;font-size:12px'><span>☁️ CloudForge 2026 · Hackathon Prototype</span><span>Smarter scaling. A stronger cloud. · Simulation only</span></div>", unsafe_allow_html=True)