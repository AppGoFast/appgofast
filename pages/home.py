import customtkinter as ctk
from tkinterdnd2 import DND_ALL
from urllib.parse import urlparse, unquote
from util.select_file_dialog import select_file_dialog


class HomePage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.exe_path_var = ctk.StringVar(self, value="")
        self.dtp_path_var = ctk.StringVar(self, value="")
        self.selected_pid_var = ctk.IntVar(value=0)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.spacer35 = ctk.CTkFrame(self, width=36, height=36, fg_color="transparent")
        self.spacer35.grid(row=0, column=0)

        self.settings_button = ctk.CTkButton(self, text="⚙", width=36, height=36, corner_radius=0, border_spacing=0, font=("", -24), fg_color="transparent", command=self.settings_button_event)
        self.settings_button.grid(row=0, column=2)

        self.segemented_button = ctk.CTkSegmentedButton(self, values=["dotnet-trace", "   dotTrace   "], width=240, dynamic_resizing=False, command=self.on_profiler_select, variable=master.profiler_var)
        self.segemented_button.grid(row=0, column=1)

        self.dotnettrace_frame = DotNetTraceFrame(self, self.selected_pid_var, master.get_dotnet_processes, self.on_pid_changed)

        self.dottrace_frame = DotTraceFrame(self, self.selected_pid_var, self.exe_path_var, self.dtp_path_var, self.on_exe_path_changed, self.on_dtp_path_changed, master.get_dotnet_processes, self.on_pid_changed)

        self.dottrace_frame.grid(row=1, column=1, sticky="wnes")

        self.start_button = ctk.CTkButton(self, text="▶︎ Start", command=self.start_profling, state="disabled")
        self.start_button.grid(row=99, column=1, pady=10, sticky="s")


    def settings_button_event(self):
        self.master.set_page("SettingsPage")

    def on_profiler_select(self, val):
        if val == "   dotTrace   ":
            self.dotnettrace_frame.grid_forget()
            self.dottrace_frame.grid(row=1, column=1, sticky="wnes")
        elif val == "dotnet-trace":
            self.dottrace_frame.grid_forget()
            self.dotnettrace_frame.grid(row=1, column=1, sticky="wnes")

    def enable_start_button(self):
        self.start_button.configure(state="normal")

    def on_exe_path_changed(self):
        self.selected_pid_var.set(0)
        self.dtp_path_var.set("")
        self.dottrace_frame.right_area.dtp_frame.reset_label()
        self.enable_start_button()

    def on_dtp_path_changed(self):
        self.selected_pid_var.set(0)
        self.exe_path_var.set("")
        self.dottrace_frame.right_area.tracing_frame.reset_label()
        self.enable_start_button()

    def on_pid_changed(self):
        self.dtp_path_var.set("")
        self.dottrace_frame.right_area.dtp_frame.reset_label()
        self.exe_path_var.set("")
        self.dottrace_frame.right_area.tracing_frame.reset_label()
        self.enable_start_button()

    def start_profling(self):
        if self.master.profiler_var.get() == "dotnet-trace":
            self.master.start_dotnet_trace(self.selected_pid_var.get())
        elif self.selected_pid_var.get() > 0:
            self.master.start_dottrace_sampling(self.selected_pid_var.get())
        elif self.exe_path_var.get() != "":
            self.master.start_dottrace_tracing(self.exe_path_var.get())
        else:
            self.master.parse_dottrace(self.dtp_path_var.get())


class DotTraceFrame(ctk.CTkFrame):
    def __init__(self, master, selected_pid_var, exe_path_var, dtp_path_var, on_exe_path_changed, on_dtp_path_changed, get_dotnet_processes, on_process_selected):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.configure(fg_color="transparent")

        self.label = ctk.CTkLabel(self, text="Sampling:")
        self.label.grid(row=0, column=0, padx=(0, 10), sticky="wnes")

        self.processes = ProcessesFrame(self, selected_pid_var, get_dotnet_processes, on_process_selected, 22)
        self.processes.grid(row=1, column=0, padx=(0, 10), sticky="wnes")

        self.label = ctk.CTkLabel(self, text="Tracing:")
        self.label.grid(row=0, column=1, sticky="wnes")

        self.right_area = DotTraceRightAreaFrame(self, exe_path_var, dtp_path_var, on_exe_path_changed, on_dtp_path_changed)
        self.right_area.grid(row=1, column=1, sticky="wnes")


class DotNetTraceFrame(ctk.CTkFrame):
    def __init__(self, master, selected_pid_var, get_dotnet_processes, on_process_selected):
        super().__init__(master)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.configure(fg_color="transparent")

        self.label = ctk.CTkLabel(self, text="Processes, available to trace:")
        self.label.grid(row=0, column=1, sticky="wnes")

        self.processes = ProcessesFrame(self, selected_pid_var, get_dotnet_processes, on_process_selected)
        self.processes.grid(row=1, column=1, padx=40, sticky="wnes")


class DotTraceRightAreaFrame(ctk.CTkFrame):
    def __init__(self, master, exe_path_var, dtp_path_var, on_exe_path_changed, on_dtp_path_changed):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((1, 3), weight=1)

        self.tracing_frame = SelectOrDropFrame(self, exe_path_var, on_exe_path_changed, ".exe", "to trace")
        self.tracing_frame.grid(row=1, column=0, sticky="wnes")

        self.label = ctk.CTkLabel(self, text="Use snapshot:")
        self.label.grid(row=2, column=0, pady=(5, 0), sticky="wnes")

        self.dtp_frame = SelectOrDropFrame(self, dtp_path_var, on_dtp_path_changed)
        self.dtp_frame.grid(row=3, column=0, sticky="wnes")


class SelectOrDropFrame(ctk.CTkFrame):
    def __init__(self, master, file_path_var, path_change_callback, file_extension = ".dtp", what_is_it = "snapshot"):
        super().__init__(master)

        self.file_path_var = file_path_var
        self.path_change_callback = path_change_callback
        self.file_extension = file_extension
        self.what_is_it = what_is_it

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((1, 2), weight=1)
        self.configure(fg_color="gray15")#self.configure(fg_color="transparent", border_color="gray30", border_width=2)

        self.label = ctk.CTkLabel(self, text=f"Drag & drop {file_extension} {what_is_it}\n or:", wraplength=160)
        self.label.grid(row=1, column=0, sticky="s")
        self.drop_target_register(DND_ALL)
        self.dnd_bind("<<Drop>>", self.on_file_drop)

        self.select_file_button = ctk.CTkButton(self, text=f"Select {file_extension} {what_is_it}", fg_color="gray28", hover_color="gray20", command=self.open_select_file_dialog)
        self.select_file_button.grid(row=2, column=0, pady=(5, 0), sticky="n")


    def open_select_file_dialog(self):
        path = select_file_dialog()
        if path:
            self.file_path_var.set(path)
            self.path_change_callback()
            self.label.configure(text = self.file_path_var.get())

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

    def on_file_drop(self, event):
        self.file_path_var.set(self._convert_file_url_to_path(event.data))
        self.path_change_callback()
        self.label.configure(text = self.file_path_var.get())

    def reset_label(self):
        self.label.configure(text = f"Drag & drop {self.file_extension} {self.what_is_it}\n or:")


class ProcessesFrame(ctk.CTkFrame):
    def __init__(self, master, selected_pid_var, get_dotnet_processes, on_process_selected, pid_offset=42):
        super().__init__(master)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.configure(fg_color="gray15")

        self.processes = ProcessListFrame(self, selected_pid_var, get_dotnet_processes, on_process_selected, pid_offset)
        self.processes.grid(row=1, column=1, pady=(5, 0), sticky="wnes")

        self.refresh_button = ctk.CTkButton(self, text="⟳ Refresh", width=0, fg_color="gray28", hover_color="gray20", command=self.refresh_processes)
        self.refresh_button.grid(row=2, column=1, pady=(0, 10), sticky="n")


    def refresh_processes(self):
        for child in self.processes.winfo_children():
            child.destroy()
        self.processes.list_processes()


class ProcessListFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, selected_pid_var, get_dotnet_processes, on_process_selected, pid_offset):
        super().__init__(master)

        self.selected_pid_var = selected_pid_var
        self.get_dotnet_processes = get_dotnet_processes
        self.on_process_selected = on_process_selected
        self.pid_offset = pid_offset

        self.configure(fg_color="gray15")

        self.list_processes()


    def list_processes(self):
        i = 1
        processes = self.get_dotnet_processes()
        if processes and len(processes) >= 1:
            for p in processes:
                name = p["name"][:(self.pid_offset - 4)]
                if name == "dotnet":
                    continue
                if i % 2 == 0:
                    bg_color = "gray19"
                else:
                    bg_color = "gray15"
                self.process_button = ctk.CTkRadioButton(self, text=f"{name:<{self.pid_offset}} PID: {p["pid"]}", font=("Consolas", 12), bg_color=bg_color, width=9999, height=32, variable=self.selected_pid_var, value=p["pid"], command=self.on_process_selected)
                self.process_button.grid(row=i, column=0, sticky="we")
                i = i+1
        else:
            self.label = ctk.CTkLabel(self, text="    No running processes found!", height=215)
            self.label.grid(row=0, column=0, sticky="wnes")


