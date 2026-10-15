import streamlit as st

st.set_page_config(
    page_title="CloudForge Worker Scaling",
    page_icon="⚙️",
    layout="wide"
)

st.title("☁️ CloudForge 2026")
st.subheader("Queue-Depth Worker Scaling Dashboard")

st.write("Change the queue depth to simulate automatic worker scaling.")

if "queue_depth" not in st.session_state:
    st.session_state.queue_depth = 12

if st.button("Reset Demo"):
    st.session_state.queue_depth = 12
    st.rerun()
queue_depth = st.slider(
    "Pending tasks in queue",
    min_value=0,
    max_value=50,
    key="queue_depth"
)

MAX_WORKERS = 5
TASKS_PER_WORKER = 3

workers = max(1, min(MAX_WORKERS, (queue_depth + TASKS_PER_WORKER - 1) // TASKS_PER_WORKER))

if queue_depth > 10:
    status = "SCALING UP"
elif queue_depth < 10:
    status = "SCALING DOWN"
else:
    status = "STEADY"

col1, col2, col3 = st.columns(3)

col1.metric("Queue Depth", queue_depth)
col2.metric("Active Workers", workers)
col3.metric("Scaling Status", status)

st.divider()
st.subheader("📊 Queue Depth Monitor")

st.line_chart({
    "Queue Depth": [5, 8, 12, 20, queue_depth],
    "Worker Count": [2, 3, 4, 5, workers]
})

st.subheader("Scaling Rules")
st.write("⬆️ Queue depth above 10: scale up.")
st.write("⬇️ Queue depth below 10: scale down.")
st.write(f"👷 Worker count is limited to {MAX_WORKERS}.")

st.info("This is a local simulation; it does not create real AWS workers.")
st.divider()

st.subheader("📋 Demo Summary")

st.write(f"• Pending tasks: {queue_depth}")
st.write(f"• Active workers: {workers}")
st.write(f"• Scaling status: {status}")

if queue_depth > 10:
    st.success("High queue detected — scaling up!")
elif queue_depth < 10:
    st.info("Low queue detected — scaling down!")
else:
    st.warning("Queue is at the threshold.")