import html
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from cpp_backend import run_cpp_simulation

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION & SYSTEM META
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="OS Kernel & VM Hypervisor | C++ Engine",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------------
# HIGH-FIDELITY OS KERNEL & TERMINAL CSS
# -----------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;600;700&display=swap');

:root {
    --bg-void: #070b12;
    --bg-surface: #0c121e;
    --bg-card: #111927;
    --bg-card-hover: #162235;
    --border-dim: #1e293b;
    --border-accent: #00f0ff33;
    --accent-cyan: #00f0ff;
    --accent-green: #10b981;
    --accent-amber: #f59e0b;
    --accent-rose: #f43f5e;
    --accent-indigo: #818cf8;
    --text-primary: #f1f5f9;
    --text-muted: #94a3b8;
    --font-mono: 'JetBrains Mono', monospace;
    --font-sans: 'Space Grotesk', -apple-system, sans-serif;
}

/* Hide Streamlit dev branding & chrome */
#MainMenu, footer, header { visibility: hidden !important; }
div[data-testid="stToolbar"] { display: none !important; }
div[data-testid="stDecoration"] { display: none !important; }
div[data-testid="stStatusWidget"] { display: none !important; }
.stAppDeployButton { display: none !important; }

/* Global resets & typography */
html, body, [class*="st-"] {
    font-family: var(--font-sans);
    color: var(--text-primary);
}

.stApp {
    background-color: var(--bg-void) !important;
    background-image: 
        radial-gradient(circle at 15% 15%, rgba(0, 240, 255, 0.04) 0%, transparent 40%),
        radial-gradient(circle at 85% 80%, rgba(16, 185, 129, 0.03) 0%, transparent 40%),
        linear-gradient(rgba(30, 41, 59, 0.15) 1px, transparent 1px),
        linear-gradient(90deg, rgba(30, 41, 59, 0.15) 1px, transparent 1px);
    background-size: 100% 100%, 100% 100%, 32px 32px, 32px 32px;
}

/* Header & Telemetry Banner */
.os-header-container {
    background: linear-gradient(180deg, #0f172a 0%, #090d16 100%);
    border: 1px solid #1e293b;
    border-top: 3px solid #00f0ff;
    border-radius: 8px;
    padding: 18px 24px;
    margin-bottom: 24px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
}

.os-title-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
}

.os-title-group h1 {
    font-family: var(--font-mono) !important;
    font-size: 1.65rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px;
    margin: 0;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 12px;
}

.os-title-group p {
    font-family: var(--font-mono);
    font-size: 0.82rem;
    color: var(--text-muted);
    margin: 4px 0 0 0;
}

.os-status-badges {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
}

.os-badge {
    font-family: var(--font-mono);
    font-size: 0.72rem;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 4px;
    border: 1px solid var(--border-dim);
    background: #080d17;
    letter-spacing: 0.5px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.os-badge-green {
    border-color: rgba(16, 185, 129, 0.4);
    color: #10b981;
    background: rgba(16, 185, 129, 0.08);
}

.os-badge-cyan {
    border-color: rgba(0, 240, 255, 0.4);
    color: #00f0ff;
    background: rgba(0, 240, 255, 0.08);
}

.os-badge-amber {
    border-color: rgba(245, 158, 11, 0.4);
    color: #f59e0b;
    background: rgba(245, 158, 11, 0.08);
}

.pulse-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background-color: #10b981;
    box-shadow: 0 0 8px #10b981;
    animation: pulseAnimation 2s infinite;
}

@keyframes pulseAnimation {
    0% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.8); }
    100% { opacity: 1; transform: scale(1); }
}

/* Card panels */
.os-card {
    background: var(--bg-card);
    border: 1px solid var(--border-dim);
    border-radius: 6px;
    padding: 18px;
    margin-bottom: 20px;
}

.os-card-header {
    font-family: var(--font-mono);
    font-size: 0.85rem;
    font-weight: 700;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    padding-bottom: 8px;
}

/* Hardware Telemetry Metric Cards */
.os-kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
    gap: 12px;
    margin-bottom: 24px;
}

.os-kpi-box {
    background: linear-gradient(145deg, #0e1624, #0a101a);
    border: 1px solid #1e293b;
    border-radius: 6px;
    padding: 14px 16px;
    position: relative;
    overflow: hidden;
}

.os-kpi-box::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 3px;
    height: 100%;
    background: var(--accent-cyan);
}

.os-kpi-box.green::before { background: var(--accent-green); }
.os-kpi-box.amber::before { background: var(--accent-amber); }
.os-kpi-box.rose::before { background: var(--accent-rose); }
.os-kpi-box.indigo::before { background: var(--accent-indigo); }

.os-kpi-label {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 6px;
}

.os-kpi-value {
    font-family: var(--font-mono);
    font-size: 1.5rem;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.1;
}

.os-kpi-sub {
    font-family: var(--font-mono);
    font-size: 0.72rem;
    color: #64748b;
    margin-top: 4px;
}

/* CPU Core & Register HUD */
.cpu-hud-container {
    background: #090e18;
    border: 1px solid #1e293b;
    border-radius: 6px;
    padding: 16px;
    margin-bottom: 20px;
}

.cpu-registers-strip {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    gap: 10px;
    margin-top: 10px;
}

.cpu-reg-box {
    background: #060a12;
    border: 1px solid #1e293b;
    border-radius: 4px;
    padding: 8px 12px;
    font-family: var(--font-mono);
}

.cpu-reg-name {
    font-size: 0.68rem;
    color: #00f0ff;
    font-weight: 700;
    margin-bottom: 2px;
}

.cpu-reg-val {
    font-size: 1.1rem;
    font-weight: 700;
    color: #f1f5f9;
}

/* Terminal & Log Stream */
.os-terminal {
    background: #050810;
    border: 1px solid #1e293b;
    border-radius: 6px;
    padding: 14px;
    font-family: var(--font-mono);
    font-size: 0.78rem;
    color: #cbd5e1;
    line-height: 1.6;
    max-height: 380px;
    overflow-y: auto;
    position: relative;
}

.os-log-line {
    display: flex;
    gap: 12px;
    padding: 2px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.03);
}

.os-log-time {
    color: #00f0ff;
    font-weight: 600;
    min-width: 65px;
}

.os-log-subsys {
    color: #10b981;
    font-weight: 600;
    min-width: 75px;
}

.os-log-msg {
    color: #e2e8f0;
}

/* Custom memory visual segment bar */
.mem-map-container {
    background: #060a12;
    border: 1px solid #1e293b;
    border-radius: 6px;
    padding: 16px;
    margin: 16px 0;
}

.mem-blocks-strip {
    display: flex;
    height: 48px;
    width: 100%;
    border-radius: 4px;
    overflow: hidden;
    border: 1px solid #334155;
    background: #0f172a;
    margin-top: 10px;
}

.mem-block-seg {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    font-family: var(--font-mono);
    font-size: 0.7rem;
    font-weight: 700;
    color: #ffffff;
    transition: all 0.2s ease;
    border-right: 1px solid rgba(0,0,0,0.4);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    padding: 0 4px;
}

/* Streamlit Widget Customization */
div[data-testid="stDataEditor"] {
    border: 1px solid #1e293b !important;
    border-radius: 6px !important;
    background: #090d16 !important;
}

div[data-baseweb="select"] {
    background-color: #090d16 !important;
    border-color: #1e293b !important;
}

/* Custom button accents */
button[kind="primary"] {
    background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
    border: 1px solid #38bdf8 !important;
    font-family: var(--font-mono) !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
    box-shadow: 0 0 15px rgba(56, 189, 248, 0.25) !important;
    transition: all 0.2s ease !important;
}

button[kind="primary"]:hover {
    box-shadow: 0 0 25px rgba(56, 189, 248, 0.5) !important;
    transform: translateY(-1px) !important;
}

button[kind="secondary"] {
    background: #0f172a !important;
    border: 1px solid #334155 !important;
    color: #e2e8f0 !important;
    font-family: var(--font-mono) !important;
    font-size: 0.8rem !important;
}

button[kind="secondary"]:hover {
    border-color: #00f0ff !important;
    color: #00f0ff !important;
}

/* Streamlit Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background-color: #090d16;
    padding: 6px;
    border-radius: 6px;
    border: 1px solid #1e293b;
}

.stTabs [data-baseweb="tab"] {
    font-family: var(--font-mono);
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    padding: 8px 16px;
    border-radius: 4px;
    color: #94a3b8;
    background: transparent;
    border: none;
}

.stTabs [aria-selected="true"] {
    background-color: #162032 !important;
    color: #00f0ff !important;
    border-bottom: 2px solid #00f0ff !important;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# WORKLOAD PRESETS & DATA DEFINITIONS
# -----------------------------------------------------------------------------
PRESETS = {
    "Standard Heterogeneous": [
        {"PID": 1, "Arrival": 0, "Burst": 5, "Priority": 2, "Memory": 100},
        {"PID": 2, "Arrival": 1, "Burst": 3, "Priority": 1, "Memory": 150},
        {"PID": 3, "Arrival": 2, "Burst": 4, "Priority": 3, "Memory": 200},
        {"PID": 4, "Arrival": 4, "Burst": 2, "Priority": 2, "Memory": 100},
    ],
    "Convoy Effect (CPU Starvation)": [
        {"PID": 1, "Arrival": 0, "Burst": 12, "Priority": 2, "Memory": 80},
        {"PID": 2, "Arrival": 1, "Burst": 2, "Priority": 1, "Memory": 50},
        {"PID": 3, "Arrival": 2, "Burst": 1, "Priority": 1, "Memory": 60},
        {"PID": 4, "Arrival": 3, "Burst": 2, "Priority": 3, "Memory": 40},
    ],
    "Memory Contention (Delayed Admission)": [
        {"PID": 1, "Arrival": 0, "Burst": 6, "Priority": 2, "Memory": 180},
        {"PID": 2, "Arrival": 1, "Burst": 4, "Priority": 1, "Memory": 140},
        {"PID": 3, "Arrival": 2, "Burst": 5, "Priority": 3, "Memory": 100},
        {"PID": 4, "Arrival": 3, "Burst": 3, "Priority": 2, "Memory": 90},
    ],
    "Priority Hierarchy": [
        {"PID": 1, "Arrival": 0, "Burst": 4, "Priority": 4, "Memory": 70},
        {"PID": 2, "Arrival": 1, "Burst": 5, "Priority": 1, "Memory": 90},
        {"PID": 3, "Arrival": 2, "Burst": 3, "Priority": 2, "Memory": 80},
        {"PID": 4, "Arrival": 3, "Burst": 2, "Priority": 3, "Memory": 60},
    ],
    "Quantum Thrashing (Heavy Preemption)": [
        {"PID": 1, "Arrival": 0, "Burst": 8, "Priority": 2, "Memory": 60},
        {"PID": 2, "Arrival": 0, "Burst": 7, "Priority": 2, "Memory": 80},
        {"PID": 3, "Arrival": 1, "Burst": 6, "Priority": 1, "Memory": 70},
        {"PID": 4, "Arrival": 2, "Burst": 5, "Priority": 3, "Memory": 90},
    ],
}

PID_COLORS = {
    1: "#00f0ff",
    2: "#10b981",
    3: "#f59e0b",
    4: "#818cf8",
    5: "#ec4899",
    6: "#06b6d4",
    7: "#eab308",
    8: "#a855f7",
}

RESULT_KEYS = [
    "results",
    "timeline",
    "memory_events",
    "state_events",
    "cpu_events",
    "summary",
    "summary_text",
    "output_dir",
    "algorithm",
    "total_memory",
    "quantum",
    "benchmark_results",
]


if "processes" not in st.session_state:
    st.session_state.processes = [p.copy() for p in PRESETS["Standard Heterogeneous"]]


# -----------------------------------------------------------------------------
# HELPER FUNCTIONS & VALIDATION
# -----------------------------------------------------------------------------
def validate_processes(dataframe, total_memory, quantum):
    required = ["PID", "Arrival", "Burst", "Priority", "Memory"]
    if dataframe.empty:
        raise ValueError("Process table is empty. Insert at least one process descriptor.")

    df = dataframe[required].copy()
    if df.isnull().any().any():
        raise ValueError("All PCB parameters (PID, Arrival, Burst, Priority, Memory) must be defined.")

    for col in required:
        vals = pd.to_numeric(df[col], errors="raise")
        if not vals.map(lambda v: pd.notna(v) and float(v).is_integer()).all():
            raise ValueError(f"PCB field '{col}' requires integral values.")
        df[col] = vals.astype(int)

    if (df["PID"] <= 0).any():
        raise ValueError("Process IDs (PID) must be strictly positive (> 0).")
    if df["PID"].duplicated().any():
        raise ValueError("Duplicate PID detected in process descriptor table.")
    if (df["Arrival"] < 0).any():
        raise ValueError("Arrival time cannot be negative.")
    if (df[["Burst", "Priority", "Memory"]] <= 0).any().any():
        raise ValueError("Burst time, Priority rank, and Memory size must be positive (> 0).")
    if (df["Memory"] > int(total_memory)).any():
        raise ValueError(
            f"Process requested memory exceeds total physical RAM capacity ({total_memory} MB). "
            "MMU admission would deadlock."
        )
    if int(quantum) <= 0:
        raise ValueError("Scheduler time quantum must be >= 1 tick.")

    return df.sort_values(["Arrival", "PID"]).reset_index(drop=True)


def read_metric(summary_dict, key, default=0.0):
    val = summary_dict.get(key)
    if val is None:
        return default
    try:
        return float(str(val).replace("%", "").strip())
    except (ValueError, AttributeError):
        return default


# -----------------------------------------------------------------------------
# SYSTEM HEADER & TELEMETRY STRIP
# -----------------------------------------------------------------------------
st.markdown(
    """
<div class="os-header-container">
    <div class="os-title-row">
        <div class="os-title-group">
            <h1>
                <span style="color:#00f0ff;">⚡</span>
                OS-VM / HYPERVISOR MONITOR
            </h1>
            <p>Multiprogramming Kernel Subsystem • Preemptive Scheduler • MMU Contiguous Allocator • C++ Native Engine</p>
        </div>
        <div class="os-status-badges">
            <div class="os-badge os-badge-green">
                <span class="pulse-dot"></span>
                KERNEL: ONLINE (x86_64 SIM)
            </div>
            <div class="os-badge os-badge-cyan">
                BACKEND: C++ NATIVE (vm_engine.exe)
            </div>
            <div class="os-badge os-badge-amber">
                RING: 0 [KERNEL PRIVILEGE]
            </div>
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# SECTION 1: WORKLOAD GENERATOR & PROCESS CONTROL BLOCK (PCB) SETUP
# -----------------------------------------------------------------------------
st.markdown(
    """
<div class="os-card-header">
    <span>[ 01 ] SYSTEM WORKLOAD & HARDWARE SCHEDULER CONFIGURATION</span>
    <span style="color:#00f0ff; font-size:0.75rem;">INPUT PCB DESCRIPTOR TABLE</span>
</div>
""",
    unsafe_allow_html=True,
)

# Preset buttons
preset_cols = st.columns([1.2, 1.2, 1.4, 1.2, 1.4])
for idx, (p_name, p_data) in enumerate(PRESETS.items()):
    with preset_cols[idx]:
        if st.button(f"Load: {p_name.split()[0]}", key=f"btn_preset_{idx}", use_container_width=True):
            st.session_state.processes = [p.copy() for p in p_data]
            st.rerun()

edited_df = st.data_editor(
    pd.DataFrame(st.session_state.processes),
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    key="process_editor",
    column_config={
        "PID": st.column_config.NumberColumn("Process ID (PID)", min_value=1, step=1, help="Unique hardware PID"),
        "Arrival": st.column_config.NumberColumn("Arrival Tick", min_value=0, step=1, help="Simulation clock tick of arrival"),
        "Burst": st.column_config.NumberColumn("CPU Burst (Ticks)", min_value=1, step=1, help="Total CPU cycles requested"),
        "Priority": st.column_config.NumberColumn("Priority Rank", min_value=1, step=1, help="Lower value indicates higher priority"),
        "Memory": st.column_config.NumberColumn("Allocated RAM (MB)", min_value=1, step=1, help="Contiguous RAM required for admission"),
    },
)
st.session_state.processes = edited_df.to_dict("records")

# Hardware knobs
col_algo, col_quantum, col_ram = st.columns([2, 1.2, 1.5])
with col_algo:
    algorithm = st.selectbox(
        "CPU Scheduling Policy",
        ["FCFS", "SJF", "Priority", "Round Robin"],
        index=3,
        help="Core scheduling discipline executed inside the native C++ engine.",
    )

with col_quantum:
    quantum = st.number_input(
        "Time Quantum (τ)",
        min_value=1,
        value=2,
        step=1,
        disabled=(algorithm != "Round Robin"),
        help="Preemption interval for Round Robin scheduler.",
    )

with col_ram:
    total_memory = st.number_input(
        "Physical RAM Capacity (MB)",
        min_value=50,
        value=250,
        step=50,
        help="Simulated MMU physical memory bounds. Processes queue in 'Waiting for Memory' if RAM is exhausted.",
    )

# Execution Trigger Buttons
btn_col1, btn_col2 = st.columns([2.5, 1.5])
with btn_col1:
    run_sim = st.button("▶ DISPATCH C++ KERNEL SIMULATION", type="primary", use_container_width=True)
with btn_col2:
    run_benchmark = st.button("⚡ BENCHMARK ALL 4 ALGORITHMS", type="secondary", use_container_width=True)

# -----------------------------------------------------------------------------
# SIMULATION DISPATCH EXECUTION
# -----------------------------------------------------------------------------
if run_sim:
    for k in RESULT_KEYS:
        st.session_state.pop(k, None)

    try:
        validated_df = validate_processes(edited_df, total_memory, quantum)
        output = run_cpp_simulation(
            validated_df.to_dict("records"),
            algorithm,
            int(quantum),
            int(total_memory),
        )
        for key, value in output.items():
            st.session_state[key] = value

        st.session_state.algorithm = algorithm
        st.session_state.total_memory = int(total_memory)
        st.session_state.quantum = int(quantum)
        st.toast(f"Kernel simulation complete: Policy [{algorithm}]", icon="⚡")

    except Exception as err:
        st.error(f"Kernel Panic / Hardware Exception: {err}")

if run_benchmark:
    try:
        validated_df = validate_processes(edited_df, total_memory, quantum)
        benchmark_data = []
        algo_list = ["FCFS", "SJF", "Priority", "Round Robin"]

        with st.spinner("Executing C++ benchmark matrix across all 4 scheduling algorithms..."):
            for alg in algo_list:
                res = run_cpp_simulation(
                    validated_df.to_dict("records"),
                    alg,
                    int(quantum),
                    int(total_memory),
                )
                res_df = res["results"]
                summ = res["summary"]
                benchmark_data.append({
                    "Algorithm": alg,
                    "Avg Waiting": round(float(res_df["Waiting"].mean()), 2),
                    "Avg Turnaround": round(float(res_df["Turnaround"].mean()), 2),
                    "Avg Memory Wait": round(float(res_df["Memory Wait"].mean()), 2),
                    "Context Switches": int(read_metric(summ, "Context switches")),
                    "CPU Utilization (%)": read_metric(summ, "CPU utilization"),
                    "Elapsed Time": int(read_metric(summ, "Elapsed time")),
                    "Busy Time": int(read_metric(summ, "Busy time")),
                })

            # Also load primary algorithm into session state
            primary_out = run_cpp_simulation(
                validated_df.to_dict("records"),
                algorithm,
                int(quantum),
                int(total_memory),
            )
            for key, value in primary_out.items():
                st.session_state[key] = value
            st.session_state.algorithm = algorithm
            st.session_state.total_memory = int(total_memory)
            st.session_state.quantum = int(quantum)
            st.session_state.benchmark_results = pd.DataFrame(benchmark_data)
            st.toast("Algorithmic benchmark matrix synthesized successfully!", icon="📊")

    except Exception as err:
        st.error(f"Benchmark Execution Failure: {err}")


# -----------------------------------------------------------------------------
# POST-EXECUTION DASHBOARD & TELEMETRY
# -----------------------------------------------------------------------------
if "results" in st.session_state:
    result_df = st.session_state.results
    timeline_df = st.session_state.timeline
    memory_df = st.session_state.memory_events
    state_df = st.session_state.state_events
    cpu_df = st.session_state.cpu_events
    summary = st.session_state.summary
    algo_used = st.session_state.algorithm
    ram_cap = st.session_state.total_memory

    elapsed_time = int(read_metric(summary, "Elapsed time"))
    busy_time = int(read_metric(summary, "Busy time"))
    ctx_switches = int(read_metric(summary, "Context switches"))
    cpu_util = read_metric(summary, "CPU utilization")
    avg_wait = result_df["Waiting"].mean()
    avg_turnaround = result_df["Turnaround"].mean()
    peak_ram = int(memory_df["UsedMB"].max())

    st.markdown("<hr style='border-color:#1e293b; margin:28px 0 20px 0;'>", unsafe_allow_html=True)

    # Telemetry KPI Grid
    st.markdown(
        f"""
<div class="os-kpi-grid">
    <div class="os-kpi-box">
        <div class="os-kpi-label">SCHEDULING POLICY</div>
        <div class="os-kpi-value" style="color:#00f0ff; font-size:1.3rem;">{algo_used}</div>
        <div class="os-kpi-sub">Quantum τ = {st.session_state.quantum if algo_used == 'Round Robin' else 'N/A'}</div>
    </div>
    <div class="os-kpi-box green">
        <div class="os-kpi-label">CPU UTILIZATION</div>
        <div class="os-kpi-value" style="color:#10b981;">{cpu_util:.1f}%</div>
        <div class="os-kpi-sub">{busy_time} busy / {elapsed_time} total ticks</div>
    </div>
    <div class="os-kpi-box amber">
        <div class="os-kpi-label">CONTEXT SWITCHES</div>
        <div class="os-kpi-value" style="color:#f59e0b;">{ctx_switches}</div>
        <div class="os-kpi-sub">{int(result_df["Execution Slices"].sum())} total slices</div>
    </div>
    <div class="os-kpi-box indigo">
        <div class="os-kpi-label">AVG CPU WAITING</div>
        <div class="os-kpi-value" style="color:#818cf8;">{avg_wait:.2f}</div>
        <div class="os-kpi-sub">Ticks in Ready Queue</div>
    </div>
    <div class="os-kpi-box">
        <div class="os-kpi-label">AVG TURNAROUND</div>
        <div class="os-kpi-value" style="color:#38bdf8;">{avg_turnaround:.2f}</div>
        <div class="os-kpi-sub">Submission to exit latency</div>
    </div>
    <div class="os-kpi-box rose">
        <div class="os-kpi-label">PEAK RAM USAGE</div>
        <div class="os-kpi-value" style="color:#f43f5e;">{peak_ram} <span style="font-size:0.9rem;">MB</span></div>
        <div class="os-kpi-sub">{peak_ram / ram_cap * 100:.1f}% of {ram_cap} MB physical</div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # -------------------------------------------------------------------------
    # INTERACTIVE STEP-THROUGH DEBUGGER & CYCLE SCRUBBER
    # -------------------------------------------------------------------------
    st.markdown(
        """
<div class="os-card-header">
    <span>[ 02 ] INTERACTIVE CLOCK CYCLE REPLAY / HARDWARE STEPPER</span>
    <span style="color:#10b981; font-size:0.75rem;">LIVE CYCLE-BY-CYCLE TELEMETRY</span>
</div>
""",
        unsafe_allow_html=True,
    )

    scrubber_col, info_col = st.columns([3, 1])
    with scrubber_col:
        scrub_t = st.slider(
            "Hardware System Clock Tick (T)",
            min_value=0,
            max_value=max(1, elapsed_time),
            value=0,
            step=1,
            help="Scrub through simulation time to inspect CPU registers, ready queue, and RAM layout at tick T.",
        )
    with info_col:
        st.markdown(
            f"""
<div style="font-family:var(--font-mono); font-size:0.8rem; background:#060a12; border:1px solid #1e293b; padding:10px 14px; border-radius:4px; margin-top:14px;">
    <div>SYS_CLK: <span style="color:#00f0ff; font-weight:700;">T = {scrub_t:02d}</span></div>
    <div>SIM STATUS: <span style="color:{'#10b981' if scrub_t < elapsed_time else '#f59e0b'};">{'EXECUTING' if scrub_t < elapsed_time else 'HALTED'}</span></div>
</div>
""",
            unsafe_allow_html=True,
        )

    # Determine CPU & Memory state at scrub_t
    # 1. Active process on CPU
    active_block = timeline_df[(timeline_df["Start"] <= scrub_t) & (timeline_df["End"] > scrub_t)]
    if not active_block.empty:
        curr_proc_str = str(active_block.iloc[0]["Process"])
        cpu_status = "RUNNING"
        proc_num = int(curr_proc_str.replace("P", "").strip()) if "P" in curr_proc_str else -1
    else:
        curr_proc_str = "IDLE (WAITING)"
        cpu_status = "IDLE"
        proc_num = -1

    # 2. CPU register state at scrub_t
    latest_cpu_ev = cpu_df[cpu_df["Time"] <= scrub_t]
    if not latest_cpu_ev.empty:
        last_ev = latest_cpu_ev.iloc[-1]
        pc_val = f"0x{int(last_ev['PC']):04X}"
        reg_raw = str(last_ev["Registers"])
        if ";" in reg_raw:
            regs = reg_raw.split(";")
            r0 = regs[0] if len(regs) > 0 else "0"
            r1 = regs[1] if len(regs) > 1 else "0"
            r2 = regs[2] if len(regs) > 2 else "0"
            r3 = regs[3] if len(regs) > 3 else "0"
        else:
            r0, r1, r2, r3 = "0", "0", "0", "0"
    else:
        pc_val = "0x0000"
        r0, r1, r2, r3 = "0", "0", "0", "0"

    # 3. Memory & queue state at scrub_t
    # Admitted processes at scrub_t: Admission Time <= scrub_t and Completion > scrub_t
    in_ram_pids = []
    ready_pids = []
    mem_wait_pids = []
    used_ram_at_t = 0

    for _, p_row in result_df.iterrows():
        p_pid = int(p_row["PID"])
        p_arr = int(p_row["Arrival"])
        p_adm = int(p_row["Admission Time"])
        p_comp = int(p_row["Completion"])
        p_mem = int(p_row["Memory (MB)"])

        if p_adm <= scrub_t < p_comp:
            in_ram_pids.append(p_pid)
            used_ram_at_t += p_mem
            if p_pid != proc_num:
                ready_pids.append(p_pid)
        elif p_arr <= scrub_t and scrub_t < p_adm:
            mem_wait_pids.append(p_pid)

    # Render Virtual CPU HUD & Queues
    hud_c1, hud_c2 = st.columns([1.5, 1.5])
    with hud_c1:
        st.markdown(
            f"""
<div class="cpu-hud-container">
    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #1e293b; padding-bottom:8px;">
        <span style="font-family:var(--font-mono); font-size:0.75rem; color:#94a3b8; font-weight:700;">VIRTUAL CPU CORE 0</span>
        <span style="font-family:var(--font-mono); font-size:0.75rem; color:{'#10b981' if cpu_status == 'RUNNING' else '#f59e0b'}; font-weight:700;">● {cpu_status}: {curr_proc_str}</span>
    </div>
    <div class="cpu-registers-strip">
        <div class="cpu-reg-box">
            <div class="cpu-reg-name">PROGRAM COUNTER</div>
            <div class="cpu-reg-val" style="color:#00f0ff;">{pc_val}</div>
        </div>
        <div class="cpu-reg-box">
            <div class="cpu-reg-name">REG $R0 (ACC)</div>
            <div class="cpu-reg-val">{r0}</div>
        </div>
        <div class="cpu-reg-box">
            <div class="cpu-reg-name">REG $R1 (DAT)</div>
            <div class="cpu-reg-val">{r1}</div>
        </div>
        <div class="cpu-reg-box">
            <div class="cpu-reg-name">REG $R2 (IDX)</div>
            <div class="cpu-reg-val">{r2}</div>
        </div>
        <div class="cpu-reg-box">
            <div class="cpu-reg-name">REG $R3 (STS)</div>
            <div class="cpu-reg-val">{r3}</div>
        </div>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

    with hud_c2:
        ready_pids_html = (
            " ".join([f"<span class='os-badge os-badge-cyan' style='font-size:0.75rem;'>PID {p}</span>" for p in ready_pids])
            if ready_pids
            else "<span style='color:#64748b;'>Queue empty</span>"
        )
        mem_wait_html = (
            " ".join([f"<span class='os-badge os-badge-amber' style='font-size:0.75rem;'>PID {p}</span>" for p in mem_wait_pids])
            if mem_wait_pids
            else "<span style='color:#64748b;'>None (MMU clear)</span>"
        )

        st.markdown(
            f"""
<div class="cpu-hud-container">
    <div style="font-family:var(--font-mono); font-size:0.75rem; color:#94a3b8; font-weight:700; border-bottom:1px solid #1e293b; padding-bottom:8px;">
        KERNEL PROCESS SCHEDULER QUEUES (T = {scrub_t})
    </div>
    <div style="margin-top:10px; font-family:var(--font-mono); font-size:0.78rem;">
        <div style="margin-bottom:8px;">
            <span style="color:#94a3b8;">READY QUEUE (IN RAM):</span>
            <div style="margin-top:4px; display:flex; gap:6px; flex-wrap:wrap;">{ready_pids_html}</div>
        </div>
        <div>
            <span style="color:#f59e0b;">MEMORY BLOCKED QUEUE (WAITING RAM):</span>
            <div style="margin-top:4px; display:flex; gap:6px; flex-wrap:wrap;">{mem_wait_html}</div>
        </div>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

    # -------------------------------------------------------------------------
    # TABBED WORKSPACE: HARDWARE DEEP-DIVE
    # -------------------------------------------------------------------------
    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
    tabs = st.tabs([
        "CPU LOGIC ANALYZER / GANTT",
        "PHYSICAL MMU & RAM MAP",
        "PROCESS CONTROL BLOCK (PCB)",
        "CPU EVENT & INSTRUCTION LOG",
        "KERNEL SYSLOG (DMESG)",
        "ALGORITHM BENCHMARK MATRIX",
        "C++ RAW DIAGNOSTICS & EXPORT",
    ])

    # -------------------------------------------------------------------------
    # TAB 1: GANTT CHART & TIMELINE
    # -------------------------------------------------------------------------
    with tabs[0]:
        st.markdown(
            """
        <div style="font-family:var(--font-mono); font-size:0.8rem; color:#94a3b8; margin-bottom:10px;">
            CPU DISPATCH LOGIC ANALYZER • CYCLE EXECUTION BLOCKS
        </div>
        """,
            unsafe_allow_html=True,
        )

        gantt_fig = go.Figure()
        for _, b in timeline_df.iterrows():
            p_name = str(b["Process"])
            b_start = int(b["Start"])
            b_end = int(b["End"])
            b_dur = int(b["Duration"])

            p_id = int(p_name.replace("P", "").strip()) if "P" in p_name else 0
            block_color = PID_COLORS.get(p_id, "#38bdf8")

            gantt_fig.add_trace(
                go.Bar(
                    x=[b_dur],
                    y=["CPU Core 0"],
                    base=[b_start],
                    orientation="h",
                    name=p_name,
                    text=[f"{p_name} ({b_dur}t)"],
                    textposition="inside",
                    marker=dict(
                        color=block_color,
                        line=dict(color="#ffffff", width=1),
                    ),
                    hovertemplate=(
                        f"<b>Process:</b> {p_name}<br>"
                        f"<b>Start Tick:</b> {b_start}<br>"
                        f"<b>End Tick:</b> {b_end}<br>"
                        f"<b>Duration:</b> {b_dur} ticks<extra></extra>"
                    ),
                )
            )

        # Highlight current scrubbed tick
        gantt_fig.add_vline(
            x=scrub_t,
            line_dash="dot",
            line_color="#00f0ff",
            line_width=2,
            annotation_text=f"T={scrub_t}",
            annotation_position="top",
            annotation_font=dict(color="#00f0ff", size=11, family="JetBrains Mono"),
        )

        gantt_fig.update_layout(
            barmode="overlay",
            paper_bgcolor="#090d16",
            plot_bgcolor="#060a12",
            height=260,
            margin=dict(l=20, r=20, t=35, b=40),
            xaxis=dict(
                title=dict(text="System Clock Ticks", font=dict(family="JetBrains Mono", color="#94a3b8")),
                range=[0, max(1, elapsed_time)],
                dtick=1,
                showgrid=True,
                gridcolor="#1e293b",
                tickfont=dict(family="JetBrains Mono", color="#94a3b8"),
            ),
            yaxis=dict(
                title="",
                showticklabels=True,
                tickfont=dict(family="JetBrains Mono", color="#00f0ff", size=12),
            ),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(family="JetBrains Mono", color="#e2e8f0", size=10),
            ),
        )
        st.plotly_chart(gantt_fig, use_container_width=True)

        st.dataframe(
            timeline_df[["Process", "Start", "End", "Duration"]],
            use_container_width=True,
            hide_index=True,
        )

    # -------------------------------------------------------------------------
    # TAB 2: PHYSICAL MEMORY MANAGEMENT (MMU)
    # -------------------------------------------------------------------------
    with tabs[1]:
        st.markdown(
            """
        <div style="font-family:var(--font-mono); font-size:0.8rem; color:#94a3b8; margin-bottom:10px;">
            PHYSICAL RAM SEGMENTATION MAP • BASE/LIMIT REGISTERS
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Dynamic Memory Bar at scrub_t
        free_ram_at_t = ram_cap - used_ram_at_t
        mem_blocks_html = []
        cur_offset = 0

        for pid_in in in_ram_pids:
            p_row = result_df[result_df["PID"] == pid_in].iloc[0]
            p_mem = int(p_row["Memory (MB)"])
            pct = (p_mem / ram_cap) * 100
            color = PID_COLORS.get(pid_in, "#38bdf8")
            base_hex = f"0x{cur_offset:04X}"
            cur_offset += p_mem
            limit_hex = f"0x{cur_offset:04X}"

            mem_blocks_html.append(
                f'<div class="mem-block-seg" style="width:{pct:.1f}%; background:{color}; color:#000000;" '
                f'title="PID {pid_in}: {p_mem}MB [{base_hex} - {limit_hex}]">'
                f'PID {pid_in} ({p_mem}MB)'
                f'</div>'
            )

        if free_ram_at_t > 0:
            free_pct = (free_ram_at_t / ram_cap) * 100
            free_base = f"0x{cur_offset:04X}"
            free_limit = f"0x{ram_cap:04X}"
            mem_blocks_html.append(
                f'<div class="mem-block-seg" style="width:{free_pct:.1f}%; background:#1e293b; color:#94a3b8;" '
                f'title="FREE RAM: {free_ram_at_t}MB [{free_base} - {free_limit}]">'
                f'FREE ({free_ram_at_t}MB)'
                f'</div>'
            )

        st.markdown(
            f"""
<div class="mem-map-container">
    <div style="display:flex; justify-content:space-between; font-family:var(--font-mono); font-size:0.75rem;">
        <span style="color:#00f0ff;">PHYSICAL RAM ALLOCATION SNAPSHOT (T = {scrub_t})</span>
        <span style="color:#94a3b8;">ALLOCATED: {used_ram_at_t} MB / {ram_cap} MB ({used_ram_at_t / ram_cap * 100:.1f}%)</span>
    </div>
    <div class="mem-blocks-strip">
        {''.join(mem_blocks_html)}
    </div>
    <div style="display:flex; justify-content:space-between; font-family:var(--font-mono); font-size:0.68rem; color:#64748b; margin-top:6px;">
        <span>BASE: 0x0000</span>
        <span>LIMIT: 0x{ram_cap:04X} ({ram_cap} MB)</span>
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

        # Plotly Memory Over Time
        st.markdown(
            "<div style='font-family:var(--font-mono); font-size:0.75rem; color:#94a3b8; margin:14px 0 6px 0;'>RAM USAGE OVER TIME (MB)</div>",
            unsafe_allow_html=True,
        )
        fig_mem = go.Figure()
        fig_mem.add_trace(
            go.Scatter(
                x=memory_df["Time"],
                y=memory_df["UsedMB"],
                mode="lines+markers",
                line=dict(shape="hv", color="#00f0ff", width=2.5),
                marker=dict(size=6, color="#10b981"),
                name="Used RAM",
                hovertemplate="Time: %{x} ticks<br>Used RAM: %{y} MB<extra></extra>",
            )
        )
        fig_mem.add_hline(
            y=ram_cap,
            line_dash="dash",
            line_color="#f43f5e",
            annotation_text=f"RAM BOUND ({ram_cap} MB)",
            annotation_position="top left",
            annotation_font=dict(color="#f43f5e", family="JetBrains Mono"),
        )
        fig_mem.update_layout(
            paper_bgcolor="#090d16",
            plot_bgcolor="#060a12",
            height=320,
            margin=dict(l=20, r=20, t=30, b=30),
            xaxis=dict(
                title=dict(text="Simulation Clock Ticks", font=dict(family="JetBrains Mono", color="#94a3b8")),
                showgrid=True,
                gridcolor="#1e293b",
                tickfont=dict(family="JetBrains Mono", color="#94a3b8"),
            ),
            yaxis=dict(
                title=dict(text="Memory (MB)", font=dict(family="JetBrains Mono", color="#94a3b8")),
                range=[0, ram_cap * 1.15],
                showgrid=True,
                gridcolor="#1e293b",
                tickfont=dict(family="JetBrains Mono", color="#94a3b8"),
            ),
        )
        st.plotly_chart(fig_mem, use_container_width=True)

        st.markdown(
            "<div style='font-family:var(--font-mono); font-size:0.75rem; color:#94a3b8; margin-top:14px;'>MMU ALLOCATION & RELEASE EVENT LEDGER</div>",
            unsafe_allow_html=True,
        )
        st.dataframe(memory_df, use_container_width=True, hide_index=True)

    # -------------------------------------------------------------------------
    # TAB 3: PROCESS CONTROL BLOCK (PCB) MASTER MATRIX
    # -------------------------------------------------------------------------
    with tabs[2]:
        st.markdown(
            """
        <div style="font-family:var(--font-mono); font-size:0.8rem; color:#94a3b8; margin-bottom:10px;">
            KERNEL PROCESS CONTROL BLOCK (task_struct) MASTER DIRECTORY
        </div>
        """,
            unsafe_allow_html=True,
        )

        display_pcb_df = result_df.copy()
        # Format register preview
        display_pcb_df["Registers"] = display_pcb_df.apply(
            lambda r: f"[{r['R0']}, {r['R1']}, {r['R2']}, {r['R3']}]", axis=1
        )
        display_pcb_df["PC"] = display_pcb_df["Program Counter"].apply(lambda pc: f"0x{int(pc):04X}")

        st.dataframe(
            display_pcb_df[[
                "PID",
                "State",
                "Priority",
                "Arrival",
                "Admission Time",
                "Memory Wait",
                "Burst",
                "First Start",
                "Completion",
                "Turnaround",
                "Waiting",
                "PC",
                "Registers",
                "Execution Slices",
                "Context Switches",
                "Memory (MB)",
            ]],
            use_container_width=True,
            hide_index=True,
        )

    # -------------------------------------------------------------------------
    # TAB 4: CPU EXECUTION & INSTRUCTION EVENT LOG
    # -------------------------------------------------------------------------
    with tabs[3]:
        st.markdown(
            """
        <div style="font-family:var(--font-mono); font-size:0.8rem; color:#94a3b8; margin-bottom:10px;">
            VIRTUAL HARDWARE EXECUTION TRACE & INTERRUPT LOG
        </div>
        """,
            unsafe_allow_html=True,
        )
        st.dataframe(cpu_df, use_container_width=True, hide_index=True)

        st.markdown(
            "<div style='font-family:var(--font-mono); font-size:0.75rem; color:#94a3b8; margin-top:14px;'>PROCESS STATE TRANSITION TRAIL</div>",
            unsafe_allow_html=True,
        )
        st.dataframe(state_df, use_container_width=True, hide_index=True)

    # -------------------------------------------------------------------------
    # TAB 5: KERNEL RING BUFFER (DMESG)
    # -------------------------------------------------------------------------
    with tabs[4]:
        st.markdown(
            """
        <div style="font-family:var(--font-mono); font-size:0.8rem; color:#94a3b8; margin-bottom:10px;">
            KERNEL RING BUFFER • DIAGNOSTIC SYS_LOG OUTPUT
        </div>
        """,
            unsafe_allow_html=True,
        )

        log_lines = []
        log_lines.append((0, "KERN_BOOT", f"Hypervisor Kernel initialized. RAM capacity: {ram_cap} MB, Policy: {algo_used}"))

        # Merge memory events, state events, and cpu events into a chronological syslog
        for _, m in memory_df.iterrows():
            t = int(m["Time"])
            p = m["PID"]
            ev = m["Event"]
            used = m["UsedMB"]
            log_lines.append((t, "MMU_ALLOC", f"Process {p} {ev}. Physical RAM used: {used}/{ram_cap} MB"))

        for _, s in state_df.iterrows():
            t = int(s["Time"])
            p = s["PID"]
            f_st = s.get("Previous State", s.get("From", "Unknown"))
            t_st = s.get("New State", s.get("To", "Unknown"))
            log_lines.append((t, "SCHED_STATE", f"PID {p} state shift: [{f_st}] -> [{t_st}]"))

        for _, c in cpu_df.iterrows():
            t = int(c["Time"])
            ev = str(c.get("Event", ""))
            fr = str(c.get("From PID", "-"))
            to = str(c.get("To PID", "-"))
            try:
                pc = int(c.get("PC", 0))
            except (ValueError, TypeError):
                pc = 0
            dur = c.get("Duration", 0)
            if ev == "CONTEXT SWITCH":
                log_lines.append((t, "SCHED_CTX", f"Context switch: PID {fr} preempted -> PID {to} dispatched (Saved PC: 0x{pc:04X})"))
            else:
                log_lines.append((t, "CPU_EXEC", f"CPU executed PID {to} for {dur} ticks. PC: 0x{pc:04X}"))

        log_lines.sort(key=lambda x: x[0])

        dmesg_html = []
        for t, subsys, msg in log_lines:
            dmesg_html.append(
                f'<div class="os-log-line">'
                f'<span class="os-log-time">[{t:04d}.00]</span>'
                f'<span class="os-log-subsys">[{html.escape(str(subsys))}]</span>'
                f'<span class="os-log-msg">{html.escape(str(msg))}</span>'
                f'</div>'
            )

        st.markdown(
            f'<div class="os-terminal">{"".join(dmesg_html)}</div>',
            unsafe_allow_html=True,
        )

    # -------------------------------------------------------------------------
    # TAB 6: MULTI-ALGORITHM BENCHMARK MATRIX
    # -------------------------------------------------------------------------
    with tabs[5]:
        st.markdown(
            """
        <div style="font-family:var(--font-mono); font-size:0.8rem; color:#94a3b8; margin-bottom:10px;">
            SCHEDULER PERFORMANCE MATRIX • ALGORITHM COMPARISON
        </div>
        """,
            unsafe_allow_html=True,
        )

        if "benchmark_results" in st.session_state:
            bench_df = st.session_state.benchmark_results
            st.dataframe(bench_df, use_container_width=True, hide_index=True)

            # Comparative Plotly grouped chart
            b_fig = go.Figure()
            b_fig.add_trace(go.Bar(
                x=bench_df["Algorithm"],
                y=bench_df["Avg Waiting"],
                name="Avg Waiting Time",
                marker_color="#00f0ff",
            ))
            b_fig.add_trace(go.Bar(
                x=bench_df["Algorithm"],
                y=bench_df["Avg Turnaround"],
                name="Avg Turnaround Time",
                marker_color="#818cf8",
            ))
            b_fig.add_trace(go.Bar(
                x=bench_df["Algorithm"],
                y=bench_df["Context Switches"],
                name="Context Switches",
                marker_color="#f59e0b",
            ))

            b_fig.update_layout(
                barmode="group",
                paper_bgcolor="#090d16",
                plot_bgcolor="#060a12",
                height=350,
                margin=dict(l=20, r=20, t=35, b=40),
                xaxis=dict(
                    title=dict(text="Scheduling Discipline", font=dict(family="JetBrains Mono", color="#94a3b8")),
                    tickfont=dict(family="JetBrains Mono", color="#e2e8f0"),
                    gridcolor="#1e293b",
                ),
                yaxis=dict(
                    title=dict(text="Clock Ticks / Count", font=dict(family="JetBrains Mono", color="#94a3b8")),
                    tickfont=dict(family="JetBrains Mono", color="#94a3b8"),
                    gridcolor="#1e293b",
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(family="JetBrains Mono", color="#e2e8f0"),
                ),
            )
            st.plotly_chart(b_fig, use_container_width=True)

            # Algorithmic verdict
            best_wait = bench_df.loc[bench_df["Avg Waiting"].idxmin()]
            best_switch = bench_df.loc[bench_df["Context Switches"].idxmin()]
            st.markdown(
                f"""
<div style="font-family:var(--font-mono); font-size:0.8rem; background:#060a12; border:1px solid #1e293b; border-left:3px solid #10b981; padding:12px 16px; border-radius:4px; margin-top:14px;">
    <div>🏆 <b>MINIMUM LATENCY:</b> <span style="color:#00f0ff;">{best_wait['Algorithm']}</span> achieved lowest average waiting time (<span style="color:#10b981;">{best_wait['Avg Waiting']} ticks</span>).</div>
    <div>⚡ <b>MINIMUM OVERHEAD:</b> <span style="color:#00f0ff;">{best_switch['Algorithm']}</span> incurred minimal context switches (<span style="color:#f59e0b;">{best_switch['Context Switches']} switches</span>).</div>
</div>
""",
                unsafe_allow_html=True,
            )

        else:
            st.info("Click the '⚡ BENCHMARK ALL 4 ALGORITHMS' button in the control panel to generate comparative metrics.")

    # -------------------------------------------------------------------------
    # TAB 7: C++ RAW DIAGNOSTICS & DATA EXPORT HUB
    # -------------------------------------------------------------------------
    with tabs[6]:
        st.markdown(
            """
        <div style="font-family:var(--font-mono); font-size:0.8rem; color:#94a3b8; margin-bottom:10px;">
            NATIVE C++ ENGINE (vm_engine.exe) DIAGNOSTICS & CSV EXPORT
        </div>
        """,
            unsafe_allow_html=True,
        )

        with st.expander("Show Native C++ Summary Diagnostic Output", expanded=True):
            st.code(st.session_state.summary_text, language="text")
            st.caption(f"C++ Output Directory: {st.session_state.output_dir}")

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
        export_col1, export_col2, export_col3 = st.columns(3)

        with export_col1:
            st.download_button(
                "📥 Export Process Results (CSV)",
                data=result_df.to_csv(index=False),
                file_name="process_results.csv",
                mime="text/csv",
                use_container_width=True,
            )
            st.download_button(
                "📥 Export MMU Memory Events (CSV)",
                data=memory_df.to_csv(index=False),
                file_name="memory_events.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with export_col2:
            st.download_button(
                "📥 Export CPU Gantt Timeline (CSV)",
                data=timeline_df.to_csv(index=False),
                file_name="execution_timeline.csv",
                mime="text/csv",
                use_container_width=True,
            )
            st.download_button(
                "📥 Export State Transitions (CSV)",
                data=state_df.to_csv(index=False),
                file_name="state_transitions.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with export_col3:
            st.download_button(
                "📥 Export Virtual CPU Events (CSV)",
                data=cpu_df.to_csv(index=False),
                file_name="cpu_events.csv",
                mime="text/csv",
                use_container_width=True,
            )
            st.download_button(
                "📥 Export C++ Summary Log (TXT)",
                data=st.session_state.summary_text,
                file_name="kernel_summary.txt",
                mime="text/plain",
                use_container_width=True,
            )
