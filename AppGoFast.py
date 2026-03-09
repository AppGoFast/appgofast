import subprocess
import sys
import customtkinter
from tkinter import filedialog


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
        print(path)
        file_label.configure(text=path)


app = App()
app.title("AppGoFast")
app.geometry("500x300")

file_label = customtkinter.CTkLabel(app, text="No file selected", fg_color=("gray80", "gray20"), corner_radius=8)
file_label.pack(fill="both", expand=True, padx=20, pady=(20, 10))

button = customtkinter.CTkButton(app, text="Select File", command=select_file)
button.pack(padx=20, pady=(0, 20))


app.mainloop()