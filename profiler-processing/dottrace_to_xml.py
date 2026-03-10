import subprocess
from pathlib import Path

REPORTER_PATH = Path(r"C:\Users\dovyd\Documents\JetBrains.dotTrace.CommandLineTools.windows-x64.2025.3.2\Reporter.exe")
SNAPSHOT_DIR = Path("profiling-snapshots")
PATTERN_FILE = Path("pattern.xml")
OUTPUT_FILE = Path("results.xml")

def run_reporter(snapshot_name: str) -> subprocess.CompletedProcess:
    snapshot = SNAPSHOT_DIR / snapshot_name

    if not REPORTER_PATH.exists():
        raise FileNotFoundError(f"Reporter not found: {REPORTER_PATH}")
    if not snapshot.exists():
        raise FileNotFoundError(f"Snapshot not found: {snapshot}")
    if not PATTERN_FILE.exists():
        raise FileNotFoundError(f"Pattern file not found: {PATTERN_FILE}")

    command = [
        str(REPORTER_PATH),
        "report",
        str(snapshot),
        f"--pattern={PATTERN_FILE}",
        f"--save-to={OUTPUT_FILE}",
    ]

    result = subprocess.run(
        command,
        shell=False,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Reporter failed (exit {result.returncode}):\n{result.stderr.strip()}"
        )

    return result