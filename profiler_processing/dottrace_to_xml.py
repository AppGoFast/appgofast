import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PATTERN_FILE = BASE_DIR / "pattern.xml"
OUTPUT_FILE = BASE_DIR / "results.xml"

def run_reporter(
    snapshot_path: str | Path,
    reporter_path: str | Path,
    pattern_file: str | Path = PATTERN_FILE,
    output_file: str | Path = OUTPUT_FILE,
) -> subprocess.CompletedProcess:
    snapshot = Path(snapshot_path).expanduser().resolve()
    pattern = Path(pattern_file).expanduser().resolve()
    output = Path(output_file).expanduser().resolve()

    if not reporter_path.exists():
        raise FileNotFoundError(f"Reporter not found: {REPORTER_PATH}")
    if not snapshot.exists():
        raise FileNotFoundError(f"Snapshot not found: {snapshot}")
    if not pattern.exists():
        raise FileNotFoundError(f"Pattern file not found: {pattern}")

    command = [
        str(reporter_path),
        "report",
        str(snapshot),
        f"--pattern={pattern}",
        f"--save-to={output}",
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
