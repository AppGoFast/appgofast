import json
from dottrace_to_xml import run_reporter
import xml.etree.ElementTree as ET
from pathlib import Path

INPUT_FILE = Path("results.xml")
OUTPUT_FILE = Path("ai_input.json")
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

if __name__ == "__main__":
    run_reporter("SLOW Starting Tasks tab for the first time SAM.Win.dtp")
    functions = parse_functions(INPUT_FILE)
    top = top_functions(functions)
    save_json(top, OUTPUT_FILE)
    delete_input_file(INPUT_FILE)