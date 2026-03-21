import sys, subprocess
from tkinter import filedialog

def select_file_dialog():
    path = ''
    try:
        if sys.platform == "win32":
            # Use PowerShell's native file dialog on Windows
            ps_script = (
                "Add-Type -AssemblyName System.Windows.Forms;"
                "$f = New-Object System.Windows.Forms.OpenFileDialog;"
                "$f.ShowDialog() | Out-Null;"
                "Write-Output $f.FileName"
            )
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_script],
                capture_output=True, text=True
            )
            p = result.stdout.strip()
            if p:
                path = p
        elif subprocess.call(["which", "kdialog"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
            result = subprocess.run(["kdialog", "--getopenfilename", "."], capture_output=True, text=True)
            p = result.stdout.strip()
            if p:
                path = p
        elif subprocess.call(["which", "zenity"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
            result = subprocess.run(["zenity", "--file-selection"], capture_output=True, text=True)
            p = result.stdout.strip()
            if p:
                path = p
    except Exception as e:
        print(f"! Failed to open select file dialog: {e}")
    if not path:
        path = filedialog.askopenfilename()
    return path
