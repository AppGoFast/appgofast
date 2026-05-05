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

        for Page in (HomePage, SettingsPage, LoadingPage, InputPage, OutputPage):
            frame = Page(self)
            self.frames[Page.__name__] = frame
            frame.grid(row=0, column=0, sticky="nesw")

        result_path = os.path.join(APP_PATH, "profiler_processing/ai_input.json")
        with open(result_path) as f:
            profiling_data = json.load(f)
        self.frames["InputPage"].set_text(json.dumps(profiling_data, indent=4))

        self.set_page("HomePage")


    def set_page(self, page):
        frame = self.frames[page]
        frame.tkraise()

    def analyze(self, profiling_data_json):
        self.frames["LoadingPage"].set_info_text("Loading...")
        self.set_page("LoadingPage")
        threading.Thread( target=self.analysis_task, args=(profiling_data_json,), daemon=True).start()

    def re_analyze(self, input): # need fix
        print("Provided additional input: " + input)
        self.frames["LoadingPage"].set_info_text("Loading...")
        self.set_page("LoadingPage")
        threading.Thread( target=self.analysis_task, args=(self.input_file_path, input,), daemon=True).start()

    def get_dottrace_json(self, input_file_path):
        if input_file_path:
            self.input_file_path = input_file_path
            self.frames["LoadingPage"].set_info_text("Loading...")
            self.set_page("LoadingPage")
            threading.Thread( target=self.dottrace_to_json_task, args=(input_file_path,), daemon=True).start()

    def dottrace_to_json_task(self, input_file_path):
        if sys.platform != "linux":
            if input_file_path:
                print(f"Processing:\n{path}")
                try:
                    self.frames["LoadingPage"].set_info_text("Reading profiling snapshot...")
                    output_json = Path(path).with_name("ai_input.json")
                    reporter_path = self.get_config()["reporter_path"]
                    result_path = ""
                    if self.last_profiler_result_path:
                        result_path = self.last_profiler_result_path
                    else:
                        result_path = process_snapshot(path, output_json_path=output_json, reporter_path=reporter_path)
                        self.last_profiler_result_path = result_path
                    if os.path.exists(result_path):
                        with open(result_path) as f:
                            profiling_data = json.load(f)
                    profiling_data_string = json.dumps(profiling_data, indent=4)
                    self.after(0, self.on_dottrace_to_json_result, profiling_data_string)
                except Exception as e:
                    messagebox.showerror("AppGoFast", f".dtp conversion failed:\n{e}")
                    self.set_page("HomePage")
        else:
            try:
                self.frames["LoadingPage"].set_info_text("Reading profiling snapshot...")
                time.sleep(1)
                result_path = ""
                if self.last_profiler_result_path:
                        result_path = self.last_profiler_result_path
                else:
                    result_path = os.path.join(APP_PATH, "profiler_processing/ai_input.json")
                    self.last_profiler_result_path = result_path
                if os.path.exists(result_path):
                    with open(result_path) as f:
                        profiling_data = json.load(f)
                profiling_data_string = json.dumps(profiling_data, indent=4)
                self.after(0, self.on_dottrace_to_json_result, profiling_data_string)
            except Exception as e:
                messagebox.showerror("AppGoFast", f".dtp conversion failed:\n{e}")
                self.set_page("HomePage")

    def on_dottrace_to_json_result(self, json_string):
        self.frames["LoadingPage"].set_info_text("Loading...")
        self.frames["InputPage"].set_text(json_string)
        self.set_page("InputPage")

    def analysis_task(self, profiling_data_json, additional_input = ""):
        config = self.get_config()
        ai_model = config["selected_ai_model"]
        api_key = config["api_key"]
        ai_prompt = config["ai_prompt"]

        dual_ai_model = config["dual_ai_model"]
        ai_model2 = config["selected_ai_model2"]
        ai_prompt2 = config["ai_prompt2"]

        # use demo profiler output for linux
        if sys.platform != "linux":
            if path:
                print(f"Processing:\n{path}")
                try:
                    # self.frames["LoadingPage"].set_info_text("Reading profiling snapshot...")
                    # output_json = Path(path).with_name("ai_input.json")
                    # reporter_path = self.get_config()["reporter_path"]
                    # result_path = ""
                    # if additional_input and self.last_profiler_result_path:
                    #     result_path = self.last_profiler_result_path
                    # else:
                    #     result_path = process_snapshot(path, output_json_path=output_json, reporter_path=reporter_path)
                    #     self.last_profiler_result_path = result_path
                    ai_output = "Analysis failed..."
                    # if os.path.exists(result_path):
                    #     with open(result_path) as f:
                    #         profiling_data = json.load(f)
                    profiling_data = f"<data>\n{str(profiling_data_json)}\n</data>"
                    ai_input = f"{ai_prompt}\n\n{profiling_data}"
                    if dual_ai_model == '0' and additional_input:
                        ai_input = f"{ai_input}\n\n<additional_user_input>\n{additional_input}\n</additional_user_input>"
                    self.frames["LoadingPage"].set_info_text("Identifying bottlenecks...")
                    ai_output = analyze_with_gemini(ai_input, api_key, ai_model)
                    if dual_ai_model == '1':
                        self.frames["LoadingPage"].set_info_text("Writing suggestions...")
                        ai_input2 = f"{ai_prompt2}\n\n<data>\n{ai_output}\n</data>"
                        if additional_input:
                            ai_input2 = f"{ai_input2}\n\n<additional_user_input>\n{additional_input}\n</additional_user_input>"
                        ai_output = analyze_with_gemini(ai_input2, api_key, ai_model2)
                    self.after(0, self.on_analysis_result, ai_output)
                except Exception as e:
                    messagebox.showerror("AppGoFast", f"Analysis failed:\n{e}")
                    self.set_page("HomePage")
        else:
            try:
                # self.frames["LoadingPage"].set_info_text("Reading profiling snapshot...")
                # time.sleep(1)
                # result_path = ""
                # if additional_input and self.last_profiler_result_path:
                #         result_path = self.last_profiler_result_path
                # else:
                #     result_path = os.path.join(APP_PATH, "profiler_processing/ai_input.json")
                #     self.last_profiler_result_path = result_path
                ai_output = "Analysis failed..."
                # if os.path.exists(result_path):
                #     with open(result_path) as f:
                #         profiling_data = json.load(f)
                profiling_data = f"<data>\n{str(profiling_data_json)}\n</data>"
                ai_input = f"{ai_prompt}\n\n{profiling_data}"
                if dual_ai_model == '0' and additional_input:
                    ai_input = f"{ai_input}\n\n<additional_user_input>\n{additional_input}\n</additional_user_input>"
                self.frames["LoadingPage"].set_info_text("Identifying bottlenecks...")
                ai_output = analyze_with_gemini(ai_input, api_key, ai_model)
                if dual_ai_model == '1':
                    self.frames["LoadingPage"].set_info_text("Writing suggestions...")
                    ai_input2 = f"{ai_prompt2}\n\n<data>\n{ai_output}\n</data>"
                    if additional_input:
                        ai_input2 = f"{ai_input2}\n\n<additional_user_input>\n{additional_input}\n</additional_user_input>"
                    ai_output = analyze_with_gemini(ai_input2, api_key, ai_model2)
                self.after(0, self.on_analysis_result, ai_output)
            except Exception as e:
                print(e)
                messagebox.showerror("AppGoFast", f"Analysis failed:\n{e}")
                self.set_page("HomePage")



    def on_analysis_result(self, result):
        self.frames["LoadingPage"].set_info_text("Something went wrong.")
        self.frames["OutputPage"].set_result(result)
        self.set_page("OutputPage")

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
        print(f"\033[1;31mConfig incomplete: Missing required keys: {example_config.keys() - config.keys()}. Delete config.json to generate a new default or add missing key values.\033[0m")
    except Exception as e:
        print(f"Your paths are probably fucked ¯\\_(ツ)_/¯: {e}")
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
