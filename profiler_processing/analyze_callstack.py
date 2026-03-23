import json
from .dottrace_to_xml import run_reporter
import xml.etree.ElementTree as ET
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "results.xml"
OUTPUT_FILE = BASE_DIR / "ai_input.json"
TOP_N = 30


def parse_functions(xml_path: Path) -> list[dict]:
    root = ET.parse(xml_path).getroot()
    return [
        {
            "Method": func.get("FQN"),
            "TotalTime": float(func.get("TotalTime", 0)),
            "OwnTime": float(func.get("OwnTime", 0)),
            "Calls": int(func.get("Calls", 0)),
        }
        for func in root.findall(".//Function")
        if func.get("FQN") is not None
    ]


def top_functions(functions: list[dict], n: int = TOP_N) -> list[dict]:
    return sorted(functions, key=lambda x: x["TotalTime"], reverse=True)[:n]


def save_json(data: list[dict], path: Path) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

def delete_input_file(path: Path) -> None:
    if path.exists():
        path.unlink()


def process_snapshot(
    snapshot_path: str | Path,
    reporter_path: str | Path,
    output_json_path: str | Path = OUTPUT_FILE,
    top_n: int = TOP_N
) -> Path:
    output_json = Path(output_json_path).expanduser().resolve()
    run_reporter(snapshot_path=snapshot_path, output_file=INPUT_FILE, reporter_path=reporter_path)
    functions = parse_functions(INPUT_FILE)
    top = top_functions(functions, n=top_n)
    save_json(top, output_json)
    delete_input_file(INPUT_FILE)
    return output_json

if __name__ == "__main__":
    process_snapshot("SLOW Starting Tasks tab for the first time SAM.Win.dtp", reporter_path="C:\\DotTraceCommandTools\\Reporter.exe")
