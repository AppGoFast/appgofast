import xml.etree.ElementTree as ET


def parse_methods(xml_path: str) -> list[dict]:
    methods = []
    context = ET.iterparse(xml_path, events=("end",))

    for event, elem in context:
        if elem.tag == "Function":
            fqn = elem.get("FQN", "")
            try:
                total_time = float(elem.get("TotalTime", "0"))
                own_time = float(elem.get("OwnTime", "0"))
                calls = int(elem.get("Calls", "0"))
                if calls == 0:
                    elem.clear()
                    continue
                time_per_call = round(total_time / calls, 4)

                methods.append({
                    "method": fqn,
                    "total_time_ms":total_time,
                    "own_time_ms": own_time,
                    "calls": calls,
                    "time_per_call_ms": time_per_call,
                })
            except ValueError:
                pass
            elem.clear()

    return methods

def build_data_markdown(methods: list[dict], top_n: int) -> str:
    by_total = sorted(methods, key=lambda x: x["total_time_ms"], reverse=True)[:top_n]
    by_own   = sorted(methods, key=lambda x: x["own_time_ms"],   reverse=True)[:top_n]

    lines = [f"## Top {top_n} Methods by Total Time"]

    for i, m in enumerate(by_total, 1):
        lines.append(f"\n### #{i} `{m['method']}`")
        lines.append(f"- total_time_ms: {m['total_time_ms']}")
        lines.append(f"- own_time_ms: {m['own_time_ms']}")
        lines.append(f"- calls: {m['calls']}")
        lines.append(f"- time_per_call_ms: {m['time_per_call_ms']}")

    lines.append(f"\n## Top {top_n} Methods by Own Time")
    for i, m in enumerate(by_own, 1):
        lines.append(f"\n### #{i} `{m['method']}`")
        lines.append(f"- own_time_ms: {m['own_time_ms']}")
        lines.append(f"- total_time_ms: {m['total_time_ms']}")
        lines.append(f"- calls: {m['calls']}")
        lines.append(f"- time_per_call_ms: {m['time_per_call_ms']}")

    return "\n".join(lines)
