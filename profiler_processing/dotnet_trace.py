import os
import subprocess
import json
import signal

def list_processes():
    result = subprocess.run(
        ["dotnet-trace", "ps"],
        capture_output=True, text=True
    )
    processes = []
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        processes.append({
            "pid": int(parts[0]),
            "name": parts[1]
        })
    return processes

def start_trace(pid, output="trace.nettrace"):
    tracer = subprocess.Popen([
        "dotnet-trace", "collect",
        "--process-id", str(pid),
        "--output", output,
        "--format", "Speedscope",
    ],  creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return tracer

def stop_trace(tracer):
    if tracer and tracer.poll() is None:
        tracer.send_signal(signal.CTRL_BREAK_EVENT)
        try:
            tracer.wait()
        except KeyboardInterrupt:
            tracer.wait()
    os.remove("trace.nettrace")

def parse_speedscope(json_file, top_n=30):
    with open(json_file) as f:
        data = json.load(f)

    summary = []
    frames = data.get("shared", {}).get("frames", [])

    for profile in data.get("profiles", []):
        frame_counts = {}

        for sample in profile.get("samples", []):
            for frame_idx in sample:
                name = frames[frame_idx].get("name", "?")
                if not any(name.startswith(ns) for ns in ["System.", "Microsoft.", "Interop."]):
                    frame_counts[name] = frame_counts.get(name, 0) + 1

        top_frames = sorted(frame_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
        summary.append({
            "profile": profile.get("name", "unknown"),
            "top_frames": top_frames
        })

    return summary



if __name__ == "__main__":
    processes = list_processes()
    print(f"{'PID':<8} {'Name':<40}")
    print("-" * 50)
    for p in processes:
        pid_str = str(p["pid"])
        name_str = p["name"][:40].ljust(40)
        print(f"{pid_str:<8} {name_str}")
    process = input("Enter the PID of the process to trace: ")
    trace = start_trace(process)
    input("Press Enter to stop trace")
    stop_trace(trace)