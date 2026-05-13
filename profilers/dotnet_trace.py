import os, subprocess, signal, sys


def get_processes():
    result = subprocess.run(
        ["dotnet-trace", "ps"],
        capture_output=True, text=True
    )
    processes = []
    lines = result.stdout.splitlines()
    if len(lines) > 1: # so it doesn't crash when nothing is running
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