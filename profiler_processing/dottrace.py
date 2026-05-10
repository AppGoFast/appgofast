import signal
import subprocess
from pathlib import Path

PATTERN_FILE = str(Path(__file__).parent / "pattern.xml")


def start_dottrace_sampling(dottrace_path: str, pid: int, snapshot_path: str):
    process = subprocess.Popen([
        dottrace_path,
        "attach", str(pid),
        "--profiling-type=Sampling",
        f"--save-to={snapshot_path}",
    ], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return process

def start_dottrace_tracing(dottrace_path: str, snapshot_path: str, target_path: str):
    process = subprocess.Popen([
        dottrace_path, "start",
        f"--save-to={snapshot_path}",
        "--profiling-type=Tracing",
        target_path
    ], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return process

def stop_dottrace(process):
    if process and process.poll() is None:
        process.send_signal(signal.CTRL_BREAK_EVENT)
        process.wait()

def run_reporter(reporter_path: str, snapshot_path: str, output_file: str, pattern_file: str = PATTERN_FILE):
    process = subprocess.run([
        reporter_path, "report",
        snapshot_path,
        f"--pattern={pattern_file}",
        f"--save-to={output_file}"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return process
