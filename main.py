from tkinterdnd2 import TkinterDnD
import customtkinter as ctk
from pages.home import HomePage
from pages.settings import SettingsPage
from pages.loading import LoadingPage
from pages.output import OutputPage
import sys
import time
import threading

def fake_task(input_file_path):
    print("started task...")
    time.sleep(1)
    print("task finished.")
    return input_file_path + ":\n" + "\nyour app sucks!" * 50

# Custom class to enable TkinterDnD on ctk
class CTkDnD(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)


class App(CTkDnD):
    def __init__(self):
        super().__init__()

        self.title("dpops")
        self.minsize(600, 400)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frames = {}
        self.input_file_path = ""

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
        self.analyze(self.input_file_path)

    def analysis_task(self, input_file_path):
        result = fake_task(input_file_path)
        self.after(0, self.on_analysis_result, result)

    def on_analysis_result(self, result):
        self.frames["OutputPage"].set_result(result)
        self.set_page("OutputPage")


# try catch to handle ctrl+c in console cleanly
try:
    app = App()
    app.mainloop()
except KeyboardInterrupt:
    sys.exit()
