import subprocess, sys, threading, time, json, os, shutil
from pathlib import Path
from tkinter import filedialog, messagebox, StringVar
from tkinterdnd2 import TkinterDnD
import customtkinter as ctk
from pages.home import HomePage
from pages.settings import SettingsPage
from pages.loading import LoadingPage
from pages.output import OutputPage
from pages.input import InputPage
from pages.tracing import TracingPage
from profilers.dottrace import *
from profilers.parser import *
from profilers.dotnet_trace import *
from ai.genai_analysis import *
from datetime import datetime
from pathlib import Path

# Custom class to enable TkinterDnD on ctk
class CTkDnD(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)


class App(CTkDnD):
    def __init__(self):
        super().__init__()

        self.title("AppGoFast")
        ctk.set_appearance_mode("dark") # force dark mode
        ctk.set_default_color_theme("green")
        self.minsize(600, 400)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frames = {}
        self.last_identified_bottlenecks = ""
        self.current_trace_process = None
        self.top_n = 30
        self.config = self.get_config()
        self.snapshot_path = ""

        if sys.platform == "linux":
            self.profiler_var = ctk.StringVar(self, value="dotnet-trace") # ["dotnet-trace", "   dotTrace   "]
        else:
            self.profiler_var = ctk.StringVar(self, value="   dotTrace   ")

        for Page in (HomePage, SettingsPage, LoadingPage, InputPage, OutputPage, TracingPage):
            frame = Page(self)
            self.frames[Page.__name__] = frame
            frame.grid(row=0, column=0, sticky="nesw")

        self.set_page("HomePage")


    def set_page(self, page):
        frame = self.frames[page]
        frame.tkraise()

    def start_profiling(self, selected_pid, exe_path, dtp_path, profiler_choice):
        try:
            if profiler_choice == "dotnet-trace":
                self.start_dotnet_trace(selected_pid)
            elif selected_pid > 0:
                self.start_dottrace_sampling(selected_pid)
            elif exe_path != "":
                self.start_dottrace_tracing(exe_path)
            else:
                self.parse_dottrace(dtp_path)
        except Exception as e:
            messagebox.showerror("AppGoFast", f"Failed to start profiling:\n{e}")
            self.set_page("HomePage")

#region dotTrace

    def dottrace_path_check(self):
        if self.config["dottrace_path"] == "" or self.config["reporter_path"] == "":
            messagebox.showerror("AppGoFast", f"dotTrace or Reporter path missing!")
            self.set_page("SettingsPage")
            return False
        return True

    def start_dottrace_sampling(self, pid):
        if not self.dottrace_path_check():
            return
        self.frames["TracingPage"].set_info_text(f"Sampling (PID: {pid}) ...")
        self.frames["TracingPage"].toggle_dottrace(1)
        self.set_page("TracingPage")
        threading.Thread( target=self.dottrace_sampling_task, args=(pid,), daemon=True).start()

    def start_dottrace_tracing(self, target_path):
        if not self.dottrace_path_check():
            return
        self.frames["TracingPage"].set_info_text(f"Tracing...")
        self.frames["TracingPage"].toggle_dottrace(1)
        self.set_page("TracingPage")
        threading.Thread( target=self.dottrace_tracing_task, args=(target_path,), daemon=True).start()

    def dottrace_tracing_task(self, target_path):
        try:
            snapshot_folder = self.config["snapshot_folder"]
            self.snapshot_path = os.path.join(snapshot_folder, f"{Path(target_path).stem}_at_{datetime.now().strftime("%Y%m%d_%H%M%S")}.dtp")
            self.current_trace_process = start_dottrace_tracing(self.config["dottrace_path"], self.snapshot_path, target_path)
        except Exception as e:
            messagebox.showerror("AppGoFast", f"Tracing failed:\n{e}")
            self.set_page("HomePage")

    def stop_dottrace(self):
        threading.Thread( target=self.finish_dottrace_task, daemon=True).start()

    def dottrace_sampling_task(self, pid):
        try:
            snapshot_folder = self.config["snapshot_folder"]
            self.snapshot_path = os.path.join(snapshot_folder, f"{pid}_at_{datetime.now().strftime("%Y%m%d_%H%M%S")}.dtp")
            self.current_trace_process = start_dottrace_sampling(self.config["dottrace_path"], pid, self.snapshot_path)
        except Exception as e:
            messagebox.showerror("AppGoFast", f"Sampling failed:\n{e}")
            self.set_page("HomePage")

    def finish_dottrace_task(self):
        try:
            self.frames["TracingPage"].set_info_text("Stopping..")
            stop_dottrace(self.current_trace_process)
            self.current_trace_process = None
            self.after(0, self.parse_dottrace, self.snapshot_path)
        except Exception as e:
            messagebox.showerror("AppGoFast", f"Tracing failed:\n{e}")
            self.set_page("HomePage")

#endregion
#region dotnet_trace

    def get_dotnet_processes(self):
        try:
            return get_processes()
        except Exception as e:
            messagebox.showerror("AppGoFast", f"Check if dotnet-trace is installed.\nFailed to get current dotnet processes:\n{e}")

    def start_dotnet_trace(self, pid):
        self.frames["TracingPage"].set_info_text(f"Tracing (PID: {pid}) ...")
        self.frames["TracingPage"].toggle_dottrace(0)
        self.set_page("TracingPage")
        threading.Thread( target=self.dotnet_trace_task, args=(pid,), daemon=True).start()

    def stop_dotnet_trace(self):
        threading.Thread( target=self.finish_dotnet_trace_task, daemon=True).start()

    def dotnet_trace_task(self, pid):
        try:
            self.current_trace_process = start_trace(pid) #, os.path.join(APP_PATH, "profilers/trace.nettrace"))
        except Exception as e:
            messagebox.showerror("AppGoFast", f"Tracing failed:\n{e}")
            self.set_page("HomePage")

    def finish_dotnet_trace_task(self):
        try:
            self.frames["TracingPage"].set_info_text("Stopping..")
            stop_trace(self.current_trace_process)
            self.frames["TracingPage"].set_info_text("Parsing output...")
            methods = parse_speedscope("trace.speedscope.json")
            top_methods_md = build_data_markdown(methods, self.top_n)
            self.current_trace_process = None
            self.after(0, self.on_dotnet_trace_finished, top_methods_md, methods)
        except Exception as e:
            messagebox.showerror("AppGoFast", f"Tracing failed:\n{e}")
            self.set_page("HomePage")

    def on_dotnet_trace_finished(self, top_methods_md, methods):
        self.frames["TracingPage"].set_info_text("Tracing...")
        self.frames["InputPage"].set_data(top_methods_md, methods)
        self.set_page("InputPage")

#endregion
#region dotTrace parsing

    def parse_dottrace(self, snapshot_path):
        if not self.dottrace_path_check():
            return
        self.frames["LoadingPage"].set_info_text("Loading...")
        self.set_page("LoadingPage")
        threading.Thread( target=self.parse_dottrace_task, args=(snapshot_path,), daemon=True).start()

    def parse_dottrace_task(self, snapshot_path):
        if sys.platform == "linux":
            messagebox.showerror("AppGoFast", f"OS not supported")
            self.set_page("HomePage")
        else:
            try:
                self.frames["LoadingPage"].set_info_text("Reading snapshot...")
                reporter_path = self.config["reporter_path"]
                reporter_output = Path(snapshot_path).with_name("reporter_output.xml")
                run_reporter(reporter_path, snapshot_path, reporter_output)
                methods = parse_dottrace(reporter_output)
                top_methods_md = build_data_markdown(methods, self.top_n)
                self.after(0, self.on_parse_dottrace_result, methods, top_methods_md)
            except Exception as e:
                messagebox.showerror("AppGoFast", f".dtp conversion failed:\n{e}")
                self.set_page("HomePage")

    def on_parse_dottrace_result(self, methods, top_methods_md):
        self.frames["LoadingPage"].set_info_text("Loading...")
        self.frames["InputPage"].set_data(top_methods_md, methods)
        self.set_page("InputPage")

#endregion
#region AI analysis

    def analyze(self, methods, data_block, scenario):
        self.frames["LoadingPage"].set_info_text("Loading...")
        self.set_page("LoadingPage")
        threading.Thread( target=self.analysis_task, args=(methods, data_block, scenario,), daemon=True).start()

    def re_analyze(self, user_input):
        self.frames["LoadingPage"].set_info_text("Loading...")
        self.set_page("LoadingPage")
        threading.Thread( target=self.re_analysis_task, args=(user_input,), daemon=True).start()

    def analysis_task(self, methods, data_block, scenario):
        ai_model = self.config["selected_ai_model"]
        api_key = self.config["api_key"]
        base_prompt = ""
        ai_model2 = self.config["selected_ai_model2"]
        base_prompt2 = ""

        try:
            prompt_1_path = os.path.join(APP_PATH, "ai/prompt_1.txt")
            with open(prompt_1_path, encoding="utf-8") as f:
                base_prompt = f.read()
            prompt_2_path = os.path.join(APP_PATH, "ai/prompt_2.txt")
            with open(prompt_2_path, encoding="utf-8") as f:
                base_prompt2 = f.read()
        except Exception as e:
            messagebox.showerror("AppGoFast", f"Failed to read prompts:\n{e}")
            self.set_page("InputPage")

        try:
            ai_output = "Analysis failed..."
            if data_block:
                self.frames["LoadingPage"].set_info_text("Identifying bottlenecks...")
                prompt = build_diagnostic_prompt(base_prompt, methods, self.top_n, data_block, scenario)
                ai_output = analyze_with_gemini(prompt, api_key, ai_model)
                self.last_identified_bottlenecks = ai_output
                self.frames["LoadingPage"].set_info_text("Writing suggestions...")
                prompt = build_investigation_prompt(base_prompt2, ai_output, scenario)
                ai_output = analyze_with_gemini(prompt, api_key, ai_model2)
            self.after(0, self.on_analysis_result, ai_output)
        except Exception as e:
            messagebox.showerror("AppGoFast", f"Analysis failed:\n{e}")
            self.set_page("InputPage")

    def re_analysis_task(self, user_input): # change to chat
        try:
            ai_output = "Not implemented."
            self.after(0, self.on_analysis_result, ai_output)
        except Exception as e:
            messagebox.showerror("AppGoFast", f"Analysis failed:\n{e}")
            self.set_page("OutputPage")

    def on_analysis_result(self, result):
        self.frames["LoadingPage"].set_info_text("Loading...")
        self.frames["OutputPage"].set_result(result)
        self.set_page("OutputPage")

#endregion

    def get_config(self):
        try:
            with open(os.path.join(APP_PATH, "config.json")) as f:
                return json.load(f)
        except Exception as e:
            print(f"! Failed to read confing: {e}")

    def write_config(self, config):
        try:
            with open(os.path.join(APP_PATH, "config.json") , mode="w", encoding="utf-8") as f:
                json.dump(config, f)
            self.config = config
        except Exception as e:
            print(f"! Failed to write config: {e}")

def validate_config():
    try:
        if not os.path.exists(os.path.join(APP_PATH, "config.json")):
            shutil.copyfile(os.path.join(APP_PATH, "config.json.example"), os.path.join(APP_PATH, "config.json"))
        with open(os.path.join(APP_PATH, "config.json.example")) as f:
            example_config = json.load(f)
        with open(os.path.join(APP_PATH, "config.json")) as f:
            config = json.load(f)
        if example_config.keys() == config.keys():
            return True
        print(f"\033[1;31mInvalid config schema!\nDelete config.json to generate a new defaul? [y/N]\033[0m")
        choice = input()
        if choice.lower() == "y":
            shutil.copyfile(os.path.join(APP_PATH, "config.json.example"), os.path.join(APP_PATH, "config.json"))
            print("Default configuration applied.")
            return True
    except Exception as e:
        print(f"{e}")
    return False

if __name__ == "__main__":
    try: # try catch to handle ctrl+c in console cleanly
        if getattr(sys, 'frozen', False):
            APP_PATH = sys._MEIPASS
        else:
            APP_PATH = os.path.dirname(os.path.abspath(__file__))
        if not validate_config():
            print("\033[1;31mConfig validation failed!\033[0m")
            sys.exit()
        app = App()
        app.mainloop()
    except KeyboardInterrupt:
        sys.exit()
