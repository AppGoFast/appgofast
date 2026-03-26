import subprocess, sys, threading, time, json, os, shutil
from pathlib import Path
from tkinter import filedialog, messagebox
from tkinterdnd2 import TkinterDnD
import customtkinter as ctk
from pages.home import HomePage
from pages.settings import SettingsPage
from pages.loading import LoadingPage
from pages.output import OutputPage
from profiler_processing.analyze_callstack import process_snapshot
from util.genai_analysis import analyze_with_gemini


# Custom class to enable TkinterDnD on ctk
class CTkDnD(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)


class App(CTkDnD):
    def __init__(self):
        super().__init__()

        self.title("AppGoFast")
        ctk.set_appearance_mode("dark") # force darkmode
        self.minsize(600, 400)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frames = {}
        self.input_file_path = ""
        self.last_profiler_result_path = ""

        for Page in (HomePage, SettingsPage, LoadingPage, OutputPage):
            frame = Page(self)
            self.frames[Page.__name__] = frame
            frame.grid(row=0, column=0, sticky="nesw")

        self.set_page("HomePage")


    def set_page(self, page):
        frame = self.frames[page]
        frame.tkraise()

    def analyze(self, input_file_path):
        if input_file_path:
            self.input_file_path = input_file_path
            self.set_page("LoadingPage")
            threading.Thread( target=self.analysis_task, args=(input_file_path,), daemon=True).start()

    def re_analyze(self, input):
        print("Provided additional input: " + input)
        self.set_page("LoadingPage")
        threading.Thread( target=self.analysis_task, args=(self.input_file_path, input,), daemon=True).start()

    def analysis_task(self, path, additional_input = ""):
        config = self.get_config()
        ai_model = config["selected_ai_model"]
        api_key = config["api_key"]
        # use demo profiler output for linux
        if sys.platform != "linux":
            if path:
                print(f"Processing:\n{path}")
                try:
                    output_json = Path(path).with_name("ai_input.json")
                    reporter_path = self.get_config()["reporter_path"]
                    result_path = ""
                    if additional_input and self.last_profiler_result_path:
                        result_path = self.last_profiler_result_path
                    else:
                        result_path = process_snapshot(path, output_json_path=output_json, reporter_path=reporter_path)
                        self.last_profiler_result_path = result_path
                    ai_output = "Analysis failed..."
                    if os.path.exists(result_path):
                        with open(result_path) as f:
                            output = json.load(f)
                        if additional_input:
                            output = f"{str(output)}\n{additional_input}"
                        ai_output = analyze_with_gemini( str(output), api_key, ai_model)
                    self.after(0, self.on_analysis_result, ai_output)
                except Exception as e:
                    messagebox.showerror("AppGoFast", f"Analysis failed:\n{e}")
                    self.set_page("HomePage")
        else:
            try:
                time.sleep(1)
                result_path = ""
                if additional_input and self.last_profiler_result_path:
                        result_path = self.last_profiler_result_path
                        print("using last profiler result path")
                else:
                    result_path = "profiler_processing/ai_input.json"
                    self.last_profiler_result_path = result_path
                ai_output = "Analysis failed..."
                if os.path.exists(result_path):
                    with open(result_path) as f:
                        output = json.load(f)
                    if additional_input:
                        output = f"{str(output)}\n{additional_input}"
                    ai_output = analyze_with_gemini( str(output), api_key, ai_model)
                self.after(0, self.on_analysis_result, ai_output)
            except Exception as e:
                print(e)
                messagebox.showerror("AppGoFast", f"Analysis failed:\n{e}")
                self.set_page("HomePage")



    def on_analysis_result(self, result):
        self.frames["OutputPage"].set_result(result)
        self.set_page("OutputPage")

    def get_config(self):
        if not os.path.exists("config.json"):
            shutil.copyfile("config.json.example", "config.json")
        try:
            with open("config.json") as f:
                return json.load(f)
        except Exception as e:
            print(f"! Failed to read confing: {e}")

    def get_config_val(name: str):
        return self.get_config()[value]

    def write_config(self, config):
        try:
            with open("config.json", mode="w", encoding="utf-8") as f:
                json.dump(config, f)
        except Exception as e:
            print(f"! Failed to write config: {e}")


# try catch to handle ctrl+c in console cleanly
try:
    app = App()
    app.mainloop()
except KeyboardInterrupt:
    sys.exit()
