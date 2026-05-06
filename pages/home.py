import customtkinter as ctk
from tkinterdnd2 import DND_ALL
from urllib.parse import urlparse, unquote
from util.select_file_dialog import select_file_dialog


class HomePage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.profiler_var = ctk.StringVar(value="dotnet-trace")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.spacer35 = ctk.CTkFrame(self, width=36, height=36, fg_color="transparent")
        self.spacer35.grid(row=0, column=0)

        self.settings_button = ctk.CTkButton(self, text="⚙", width=36, height=36, corner_radius=0, border_spacing=0, font=("", -24), fg_color="transparent", command=self.settings_button_event)
        self.settings_button.grid(row=0, column=2)

        self.segemented_button = ctk.CTkSegmentedButton(self, values=["dotnet-trace", "  dotTrace  "], width=210, dynamic_resizing=False, command=self.on_profiler_select, variable=self.profiler_var)
        self.segemented_button.grid(row=0, column=1)

        self.dottrace_frame = DotTraceFrame(self)

        self.dotnettrace_frame = DotNetTraceFrame(self)

        self.dotnettrace_frame.grid(row=1, column=1, sticky="wnes")


    def settings_button_event(self):
        self.master.set_page("SettingsPage")

    def on_profiler_select(self, val):
        if val == "  dotTrace  ":
            self.dotnettrace_frame.grid_forget()
            self.dottrace_frame.grid(row=1, column=1, sticky="wnes")
        else:
            self.dottrace_frame.grid_forget()
            self.dotnettrace_frame.grid(row=1, column=1, sticky="wnes")


class DotNetTraceFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.selected_pid_var = ctk.IntVar(value=0)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.configure(fg_color="transparent")

        self.label = ctk.CTkLabel(self, text="Processes, available to profile:")
        self.label.grid(row=0, column=1, pady=(10, 0), sticky="wnes")

        self.processes = ProcessesFrame(self, self.selected_pid_var, self.on_process_selected)
        self.processes.grid(row=1, column=1, padx=30, sticky="wnes")

        self.refresh_button = ctk.CTkButton(self, text="⟳ Refresh", width=0, fg_color="gray28", hover_color="gray20", command=self.refresh_processes)
        self.refresh_button.grid(row=2, column=1, pady=10, sticky="n")

        self.start_button = ctk.CTkButton(self, text="Start Tracing", command=self.start_profling, state="disabled")
        self.start_button.grid(row=99, column=1, pady=10, sticky="s")


    def start_profling(self):
        self.master.master.start_dotnet_trace(self.selected_pid_var.get()) # fix later

    def refresh_processes(self):
        for child in self.processes.winfo_children():
            child.destroy()
        self.processes.list_processes()

    def on_process_selected(self):
        self.start_button.configure(state="normal")


class DotTraceFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.input_file_path = ""

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((1, 2), weight=1)
        self.configure(fg_color="transparent")

        self.label = ctk.CTkLabel(self, text="Drag & drop your .dtp file\n\n or:", wraplength=550)
        self.label.grid(row=1, column=0, sticky="s")
        self.drop_target_register(DND_ALL)
        self.dnd_bind("<<Drop>>", self.file_drop_event)

        self.select_file_button = ctk.CTkButton(self, text="Select File", fg_color="gray28", hover_color="gray20", command=self.open_select_file_dialog)
        self.select_file_button.grid(row=2, column=0, sticky="n", pady=20)

        self.analyze_button = ctk.CTkButton(self, text="Analyze", command=self.analyze_button_event, state="disabled")
        self.analyze_button.grid(row=99, column=0, pady=10, sticky="s")


    def open_select_file_dialog(self):
        path = select_file_dialog()
        if path:
            self.input_file_path = path
            self.label.configure(text = self.input_file_path)
            self.analyze_button.configure(state="normal")

    def _convert_file_url_to_path(self, file_url: str) -> str:
        """Convert file URL to filesystem path, handling both file:/// and file:/ formats."""
        if file_url.startswith("file:"):
            # Parse the URL and extract the path
            parsed = urlparse(file_url)
            # unquote handles URL encoding like %20 for spaces
            path = unquote(parsed.path)
            # On Windows, urlparse returns /C:/ for file:///C:/, so we need to remove the leading /
            if path.startswith("/") and len(path) > 2 and path[2] == ":":
                path = path[1:]
            return path
        return file_url

    def file_drop_event(self, event):
        self.input_file_path = self._convert_file_url_to_path(event.data)
        self.label.configure(text = self.input_file_path)
        self.analyze_button.configure(state="normal")

    def analyze_button_event(self):
        if self.input_file_path:
            self.master.master.get_dottrace_json(self.input_file_path) # fix later


class ProcessesFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, selected_pid_var, on_process_selected):
        super().__init__(master)

        self.configure(fg_color="gray15")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.selected_pid_var = selected_pid_var
        self.on_process_selected = on_process_selected

        self.list_processes()


    def list_processes(self):
        i = 1
        processes = self.master.master.master.master.master.get_dotnet_processes() # fix later
        if processes:
            if len(processes) >= 1:
                for p in processes:
                    name = p["name"][:38]
                    if name == "dotnet":
                        continue
                    if i % 2 == 0:
                        bg_color = "gray19"
                    else:
                        bg_color = "gray15"
                    self.process_button = ctk.CTkRadioButton(self, text=f"{name:<42} PID: {p["pid"]}", font=("Consolas", 12), bg_color=bg_color, width=9999, height=32, variable=self.selected_pid_var, value=p["pid"], command=self.on_process_selected)
                    self.process_button.grid(row=i, column=0, sticky="we")
                    i = i+1
        else:
            self.label = ctk.CTkLabel(self, text="    No running processes found!", height=215)
            self.label.grid(row=0, column=0, sticky="wnes")


