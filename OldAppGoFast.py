import subprocess
import sys
from pathlib import Path
import customtkinter
from tkinter import filedialog, messagebox

PROFILER_DIR = Path(__file__).resolve().parent / "profiler-processing"
sys.path.insert(0, str(PROFILER_DIR))

from analyze_callstack import process_snapshot  # type: ignore[import-not-found]


class App(customtkinter.CTk):
    pass


def select_file():
    path = None
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
    except Exception:
        pass

    if not path:
        path = filedialog.askopenfilename()

    if path:
        file_label.configure(text=f"Processing:\n{path}")
        app.update_idletasks()
        try:
            output_json = Path(path).with_name("ai_input.json")
            result_path = process_snapshot(path, output_json_path=output_json)
            file_label.configure(text=f"Done:\n{result_path}")
            messagebox.showinfo("AppGoFast", f"Analysis complete.\nOutput: {result_path}")
        except Exception as exc:
            file_label.configure(text=f"Failed:\n{path}")
            messagebox.showerror("AppGoFast", f"Analysis failed:\n{exc}")


app = App()
app.title("AppGoFast")
app.geometry("500x300")

file_label = customtkinter.CTkLabel(app, text="No file selected", fg_color=("gray80", "gray20"), corner_radius=8)
file_label.pack(fill="both", expand=True, padx=20, pady=(20, 10))

button = customtkinter.CTkButton(app, text="Select File", command=select_file)
button.pack(padx=20, pady=(0, 20))


app.mainloop()