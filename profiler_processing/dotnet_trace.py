import os, subprocess, json, signal, sys
from collections import defaultdict


def get_processes():
    result = subprocess.run(
        ["dotnet-trace", "ps"],
        capture_output=True, text=True
    )
    processes = []
    lines = result.stdout.splitlines()
    if len(lines) > 1: # so it doesnt crash when nothing is running
        for line in lines:
            parts = line.split()
            if len(parts) < 2:
                continue
            processes.append({
                "pid": int(parts[0]),
                "name": parts[1]
            })
    return processes

def start_trace(pid, output="trace.nettrace"):
    if sys.platform == "linux":
            tracer = subprocess.Popen([
                "dotnet-trace", "collect",
                "--process-id", str(pid),
                "--output", output,
                "--format", "Speedscope"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        tracer = subprocess.Popen([
            "dotnet-trace", "collect",
            "--process-id", str(pid),
            "--output", output,
            "--format", "Speedscope"
        ],  creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return tracer

def stop_trace(tracer):
    if tracer and tracer.poll() is None:
        if sys.platform == "linux":
            tracer.send_signal(signal.SIGINT)
        else:
            tracer.send_signal(signal.CTRL_BREAK_EVENT)
        tracer.wait()
    if os.path.exists("trace.nettrace"):
        os.remove("trace.nettrace")


def parse_speedscope(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Namespaces and keywords to exclude to reduce noise
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
    # Clean assembly prefixes (e.g., 'System.Private.CoreLib.il!') for readability
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

            # Skip known noise namespaces
            if any(noise in method_name for noise in noise_filters):
                if "UNMANAGED_CODE_TIME" in method_name and total > 500:
                    pass
                else:
                    continue

            # Skip if OwnTime is little
            if own < 0.1 and total < 1.0:
                continue

            profile_summary.append({
                "Method": method_name,
                "TotalTime": round(total, 2),
                "OwnTime": round(own, 2),
                "Calls": count
            })

        # Sort TotalTime descending
        profile_summary.sort(key=lambda x: x["TotalTime"], reverse=True)

        if profile_summary:
            summary.append(profile_summary)

    return summary
