
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from cpp_backend import run_cpp_simulation


st.set_page_config(
    page_title="OS Virtual Machine Simulator",
    page_icon="⚙️",
    layout="wide",
)

st.title("⚙️ Virtual Machine Simulator")
st.caption(
    "Design and Implementation of a Virtual Machine Simulator "
    "for Operating System Process Execution"
)
st.info("Simulation backend: C++ engine | Dashboard: Streamlit")


DEFAULT_PROCESSES = [
    {"PID": 1, "Arrival": 0, "Burst": 5, "Priority": 2, "Memory": 100},
    {"PID": 2, "Arrival": 1, "Burst": 3, "Priority": 1, "Memory": 150},
    {"PID": 3, "Arrival": 2, "Burst": 4, "Priority": 3, "Memory": 200},
    {"PID": 4, "Arrival": 4, "Burst": 2, "Priority": 2, "Memory": 100},
]

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
]


if "processes" not in st.session_state:
    st.session_state.processes = [
        p.copy() for p in DEFAULT_PROCESSES
    ]


def validate_processes(dataframe, total_memory, quantum):
    required = ["PID", "Arrival", "Burst", "Priority", "Memory"]

    if dataframe.empty:
        raise ValueError("Add at least one process.")

    df = dataframe[required].copy()

    if df.isnull().any().any():
        raise ValueError("Fill in every process field.")

    for column in required:
        values = pd.to_numeric(df[column], errors="raise")

        if not values.map(
            lambda value: pd.notna(value)
            and float(value).is_integer()
        ).all():
            raise ValueError(f"{column} must contain whole numbers.")

        df[column] = values.astype(int)

    if (df["PID"] <= 0).any():
        raise ValueError("PIDs must be positive.")

    if df["PID"].duplicated().any():
        raise ValueError("Each process must have a unique PID.")

    if (df["Arrival"] < 0).any():
        raise ValueError("Arrival times cannot be negative.")

    if (df[["Burst", "Priority", "Memory"]] <= 0).any().any():
        raise ValueError(
            "Burst, Priority and Memory must be positive."
        )

    if (df["Memory"] > int(total_memory)).any():
        raise ValueError(
            "A process requests more RAM than the total RAM. "
            "That process can never be admitted."
        )

    if int(quantum) <= 0:
        raise ValueError("The time quantum must be positive.")

    return df.sort_values(
        ["Arrival", "PID"]
    ).reset_index(drop=True)


def read_number(summary, key, default=0.0):
    value = summary.get(key)

    if value is None:
        return default

    try:
        return float(value.replace("%", "").strip())
    except (ValueError, AttributeError):
        return default


# ---------------------------------------------------------
# 1. Process configuration
# ---------------------------------------------------------

st.subheader("1. Process Configuration")

edited_df = st.data_editor(
    pd.DataFrame(st.session_state.processes),
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    key="process_editor",
    column_config={
        "PID": st.column_config.NumberColumn(
            "PID", min_value=1, step=1
        ),
        "Arrival": st.column_config.NumberColumn(
            "Arrival Time", min_value=0, step=1
        ),
        "Burst": st.column_config.NumberColumn(
            "CPU Burst Time", min_value=1, step=1
        ),
        "Priority": st.column_config.NumberColumn(
            "Priority", min_value=1, step=1
        ),
        "Memory": st.column_config.NumberColumn(
            "Memory (MB)", min_value=1, step=1
        ),
    },
)

st.session_state.processes = edited_df.to_dict("records")


# ---------------------------------------------------------
# 2. Simulation settings
# ---------------------------------------------------------

st.subheader("2. Simulation Settings")

col1, col2, col3 = st.columns(3)

with col1:
    algorithm = st.selectbox(
        "Scheduling Algorithm",
        ["FCFS", "SJF", "Priority", "Round Robin"],
    )

with col2:
    quantum = st.number_input(
        "Round Robin Time Quantum",
        min_value=1,
        value=2,
        step=1,
        disabled=(algorithm != "Round Robin"),
    )

with col3:
    total_memory = st.number_input(
        "Available RAM (MB)",
        min_value=1,
        value=250,
        step=50,
    )

st.caption(
    "Priority scheduling is non-preemptive; a smaller number "
    "means higher priority. RAM is released when a process terminates."
)

run_clicked = st.button(
    "▶ Run C++ Simulation",
    type="primary",
    use_container_width=True,
)

if run_clicked:
    # Remove previous results before attempting a new run.
    for key in RESULT_KEYS:
        st.session_state.pop(key, None)

    try:
        validated_df = validate_processes(
            edited_df,
            total_memory,
            quantum,
        )

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

        st.success("C++ simulation completed successfully.")

    except Exception as error:
        st.error(f"Simulation failed: {error}")


# ---------------------------------------------------------
# 3. Results and metrics
# ---------------------------------------------------------

if "results" in st.session_state:
    result_df = st.session_state.results
    timeline_df = st.session_state.timeline
    memory_df = st.session_state.memory_events
    state_df = st.session_state.state_events
    cpu_df = st.session_state.cpu_events
    summary = st.session_state.summary

    algorithm_used = st.session_state.algorithm
    ram = st.session_state.total_memory

    elapsed = read_number(summary, "Elapsed time")
    busy = read_number(summary, "Busy time")
    context_switches = int(
        read_number(summary, "Context switches")
    )
    utilization = read_number(summary, "CPU utilization")

    st.divider()
    st.subheader(f"3. Simulation Results — {algorithm_used}")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Processes", len(result_df))
    c2.metric(
        "Average CPU Waiting",
        f'{result_df["Waiting"].mean():.2f}',
    )
    c3.metric(
        "Average Turnaround",
        f'{result_df["Turnaround"].mean():.2f}',
    )
    c4.metric("CPU Utilization", f"{utilization:.2f}%")

    cpu1, cpu2, cpu3 = st.columns(3)

    cpu1.metric("Context Switches", context_switches)
    cpu2.metric(
        "Execution Slices",
        int(result_df["Execution Slices"].sum()),
    )
    cpu3.metric("Total CPU Busy Time", f"{busy:g} units")

    st.caption(
        "Metrics are read from C++-generated output. CPU waiting "
        "excludes memory waiting. The initial dispatch from idle "
        "is not counted as a context switch."
    )

    # -----------------------------------------------------
    # 4. Process results
    # -----------------------------------------------------

    st.subheader("4. Process Execution Results")

    st.dataframe(
        result_df,
        use_container_width=True,
        hide_index=True,
    )

    # -----------------------------------------------------
    # 5. Gantt chart
    # -----------------------------------------------------

    st.subheader("5. CPU Gantt Chart")

    fig = go.Figure()

    for _, block in timeline_df.iterrows():
        name = str(block["Process"])
        start = int(block["Start"])
        end = int(block["End"])
        duration = int(block["Duration"])

        fig.add_trace(
            go.Bar(
                x=[duration],
                y=["CPU"],
                base=[start],
                orientation="h",
                name=name,
                text=[name],
                textposition="inside",
                hovertemplate=(
                    f"Process: {name}<br>"
                    f"Start: {start}<br>"
                    f"End: {end}<br>"
                    f"Duration: {duration}"
                    "<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        barmode="overlay",
        xaxis_title="Simulation Time",
        yaxis_title="",
        xaxis={
            "range": [0, max(1, elapsed)],
            "dtick": 1,
            "showgrid": True,
        },
        yaxis={"showticklabels": False},
        height=260,
        margin={"l": 20, "r": 20, "t": 35, "b": 40},
        legend_title="Execution Blocks",
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        timeline_df[
            ["Process", "Start", "End", "Duration"]
        ],
        use_container_width=True,
        hide_index=True,
    )

    # -----------------------------------------------------
    # 6. Process state transitions
    # -----------------------------------------------------

    st.subheader("6. Process State Transitions")

    if state_df.empty:
        st.info("No state transitions were recorded.")
    else:
        st.dataframe(
            state_df,
            use_container_width=True,
            hide_index=True,
        )

    # -----------------------------------------------------
    # 7. Virtual CPU log
    # -----------------------------------------------------

    st.subheader("7. Virtual CPU Execution Log")

    if cpu_df.empty:
        st.info("No CPU events were recorded.")
    else:
        st.dataframe(
            cpu_df,
            use_container_width=True,
            hide_index=True,
        )

    st.caption(
        "The program counter and registers are simulated values, "
        "not physical CPU registers."
    )

    # -----------------------------------------------------
    # 8. Memory management
    # -----------------------------------------------------

    st.subheader("8. Memory Management")

    peak_used = int(memory_df["UsedMB"].max())
    available_now = int(memory_df.iloc[-1]["AvailableMB"])

    m1, m2, m3 = st.columns(3)

    m1.metric("Total RAM", f"{ram} MB")
    m2.metric("Peak Memory Used", f"{peak_used} MB")
    m3.metric("Available at End", f"{available_now} MB")

    st.progress(min(peak_used / ram, 1.0))

    st.subheader("Memory Usage Over Time")

    fig_memory = go.Figure()

    fig_memory.add_trace(
        go.Scatter(
            x=memory_df["Time"],
            y=memory_df["UsedMB"],
            mode="lines+markers",
            line_shape="hv",
            name="Used RAM",
            customdata=memory_df[
                ["PID", "Event", "AvailableMB"]
            ].to_numpy(),
            hovertemplate=(
                "Time: %{x}<br>"
                "Used RAM: %{y} MB<br>"
                "PID: %{customdata[0]}<br>"
                "Event: %{customdata[1]}<br>"
                "Available RAM: %{customdata[2]} MB"
                "<extra></extra>"
            ),
        )
    )

    fig_memory.add_hline(
        y=ram,
        line_dash="dash",
        annotation_text="RAM Capacity",
    )

    fig_memory.update_layout(
        xaxis_title="Simulation Time",
        yaxis_title="Memory Used (MB)",
        yaxis={"range": [0, ram * 1.1]},
        height=350,
    )

    st.plotly_chart(fig_memory, use_container_width=True)

    st.subheader("Memory Allocation Event Log")

    st.dataframe(
        memory_df,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Process Memory Waiting")

    st.dataframe(
        result_df[
            [
                "PID",
                "Memory (MB)",
                "Admission Time",
                "Memory Wait",
                "Waiting",
                "State",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    if available_now == ram:
        st.success("All simulated process memory has been released.")
    else:
        st.warning("Some simulated memory remains allocated.")

    # -----------------------------------------------------
    # 9. C++ summary and exports
    # -----------------------------------------------------

    with st.expander("View C++ Engine Summary"):
        st.code(st.session_state.summary_text, language="text")
        st.caption(
            f'Output directory: {st.session_state.output_dir}'
        )

    st.subheader("9. Export Simulation Results")

    download_items = [
        (
            "Process Results CSV",
            result_df,
            "simulation_results.csv",
        ),
        (
            "Memory Events CSV",
            memory_df,
            "memory_events.csv",
        ),
        (
            "CPU Timeline CSV",
            timeline_df,
            "execution_timeline.csv",
        ),
        (
            "State Transitions CSV",
            state_df,
            "process_state_transitions.csv",
        ),
        (
            "Virtual CPU Events CSV",
            cpu_df,
            "virtual_cpu_events.csv",
        ),
    ]

    for start in range(0, len(download_items), 3):
        cols = st.columns(3)

        for col, item in zip(
            cols,
            download_items[start:start + 3],
        ):
            label, dataframe, filename = item

            with col:
                st.download_button(
                    label,
                    data=dataframe.to_csv(index=False),
                    file_name=filename,
                    mime="text/csv",
                    use_container_width=True,
                )

    st.download_button(
        "C++ Engine Summary TXT",
        data=st.session_state.summary_text,
        file_name="simulation_summary.txt",
        mime="text/plain",
        use_container_width=True,
    )
