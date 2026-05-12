import json
from collections import defaultdict
import xml.etree.ElementTree as ET

def parse_speedscope(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)

    noise_filters = [
        "System.",
        "Microsoft.",
        "JetBrains.",
        "Hangfire.",
        "WaitHandle",
        "Monitor.Wait",
        "ManualResetEvent",
        "libcoreclr"
    ]

    frames = data['shared']['frames']
    frame_names = [f.get('name', 'Unknown').split('!')[-1] for f in frames]

    summary = []

    for profile in data['profiles']:
        stats = defaultdict(lambda: [0.0, 0.0, 0])
        stack = []

        for event in profile['events']:
            f_idx = event['frame']
            at = event['at']

            if event['type'] == 'O':
                stack.append([at, 0.0])
                stats[f_idx][2] += 1

            elif event['type'] == 'C':
                if not stack:
                    continue

                start_time, children_duration = stack.pop()
                total_duration = at - start_time
                stats[f_idx][0] += total_duration
                own_duration = total_duration - children_duration
                stats[f_idx][1] += own_duration

                if stack:
                    stack[-1][1] += total_duration

        profile_summary = []
        for idx, (total, own, count) in stats.items():
            method_name = frame_names[idx]

            if any(noise in method_name for noise in noise_filters):
                if "UNMANAGED_CODE_TIME" in method_name and total > 500:
                    pass
                else:
                    continue

            if own < 0.1 and total < 1.0:
                continue

            if count == 0:
                continue

            time_per_call = round(total / count, 4)

            profile_summary.append({
                "method":           method_name,
                "total_time_ms":    round(total, 2),
                "own_time_ms":      round(own, 2),
                "calls":            count,
                "time_per_call_ms": time_per_call,
            })

        profile_summary.sort(key=lambda x: x["total_time_ms"], reverse=True)

        if profile_summary:
            summary.extend(profile_summary)

    return summary

def parse_dottrace(xml_path: str) -> list[dict]:
     methods = []
     xml_path = str(xml_path)

     try:
         context = ET.iterparse(xml_path, events=("end",))
     except Exception as e:
         return methods

     try:
         for event, elem in context:
             if elem.tag == "Function":
                 fqn = elem.get("FQN", "")
                 total_time_str = elem.get("TotalTime", "0")
                 own_time_str = elem.get("OwnTime", "0")

                 # Try to get calls from Samples (dotTrace reporter format) or Calls (dotnet-trace format)
                 calls_str = elem.get("Samples") or elem.get("Calls", "0")

                 try:
                     total_time = float(total_time_str)
                     own_time = float(own_time_str)
                     calls = int(calls_str) if calls_str else 0

                     if calls == 0:
                         elem.clear()
                         continue

                     time_per_call = round(total_time / calls, 4)

                     methods.append({
                         "method": fqn,
                         "total_time_ms": total_time,
                         "own_time_ms": own_time,
                         "calls": calls,
                         "time_per_call_ms": time_per_call,
                     })
                 except ValueError:
                     pass
                 elem.clear()
     except Exception:
         pass

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
