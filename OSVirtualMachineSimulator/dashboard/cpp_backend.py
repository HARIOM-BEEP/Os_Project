
from pathlib import Path
import subprocess

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENGINE_PATH = PROJECT_ROOT / "vm_engine.exe"
INPUT_PATH = PROJECT_ROOT / "data" / "processes.csv"
OUTPUT_DIR = PROJECT_ROOT / "results" / "streamlit_cpp"

OUTPUT_FILES = [
    "process_results.csv",
    "timeline.csv",
    "memory_events.csv",
    "state_events.csv",
    "cpu_events.csv",
    "summary.txt",
]


def run_cpp_simulation(processes, algorithm, quantum, total_memory):
    """
    Run the C++ simulator and return its generated output files.

    processes: list of dictionaries containing PID, Arrival, Burst,
               Priority and Memory.
    algorithm: FCFS, SJF, Priority or Round Robin.
    quantum: Round Robin time quantum.
    total_memory: simulated RAM capacity in MB.
    """

    if not ENGINE_PATH.exists():
        raise FileNotFoundError(
            f"C++ executable not found: {ENGINE_PATH}\n"
            "Compile cpp/vm_engine.cpp from the project root first."
        )

    INPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Write the exact five columns expected by the C++ engine.
    input_df = pd.DataFrame(processes).rename(
        columns={
            "PID": "pid",
            "Arrival": "arrival",
            "Burst": "burst",
            "Priority": "priority",
            "Memory": "memory",
        }
    )

    input_df = input_df[
        ["pid", "arrival", "burst", "priority", "memory"]
    ]

    input_df.to_csv(INPUT_PATH, index=False)

    # Remove old outputs so failed runs cannot display stale results.
    for filename in OUTPUT_FILES:
        old_file = OUTPUT_DIR / filename
        if old_file.exists():
            old_file.unlink()

    command = [
        str(ENGINE_PATH),
        str(INPUT_PATH),
        str(OUTPUT_DIR),
        str(algorithm),
        str(int(quantum)),
        str(int(total_memory)),
    ]

    completed = subprocess.run(
        command,
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )

    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(
            message or
            f"C++ engine exited with code {completed.returncode}."
        )

    missing = [
        filename
        for filename in OUTPUT_FILES
        if not (OUTPUT_DIR / filename).exists()
    ]

    if missing:
        raise RuntimeError(
            "The C++ engine did not generate these files: "
            + ", ".join(missing)
        )

    # Load the C++-generated files, not a Python simulation.
    results = pd.read_csv(OUTPUT_DIR / "process_results.csv")
    timeline = pd.read_csv(OUTPUT_DIR / "timeline.csv")
    memory_events = pd.read_csv(OUTPUT_DIR / "memory_events.csv")
    state_events = pd.read_csv(OUTPUT_DIR / "state_events.csv")
    cpu_events = pd.read_csv(OUTPUT_DIR / "cpu_events.csv")

    # The summary contains the authoritative C++ statistics.
    summary_text = (
        OUTPUT_DIR / "summary.txt"
    ).read_text(encoding="utf-8")

    summary = {}

    for line in summary_text.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            summary[key.strip()] = value.strip()

    return {
        "results": results,
        "timeline": timeline,
        "memory_events": memory_events,
        "state_events": state_events,
        "cpu_events": cpu_events,
        "summary": summary,
        "summary_text": summary_text,
        "output_dir": str(OUTPUT_DIR),
    }
