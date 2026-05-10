import customtkinter as ctk
from tkinter import StringVar
from frames.BottomButtonsFrame import BottomButtonsFrame
from frames.LongTextVarFrame import LongTextVarFrame

class InputPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.top_methods_md = ""
        self.methods = ""
        self.scenario = StringVar(self, value="unknown")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.textbox = ctk.CTkTextbox(self, state="disabled")
        self.textbox.grid(row=0, column=0, padx=5, pady=5,  sticky="wnes")

        self.scenario_frame = LongTextVarFrame(self, "Scenario:", self.scenario, 50)
        self.scenario_frame.grid(row=1, column=0, padx=5, sticky="wnes")

        self.bottom_buttons = BottomButtonsFrame(self, name1="Return to Profiling", command1=self.on_return_home, name2="Analyze with AI", command2=self.on_analyze)
        self.bottom_buttons.grid(row=99, column=0, pady=10, padx=10, sticky="s")


    def on_return_home(self):
        self.master.set_page("HomePage")

    def on_analyze(self):
        self.master.analyze(self.methods, self.top_methods_md, self.scenario.get())

    def set_data(self, top_methods_md, methods):
        self.top_methods_md = top_methods_md
        self.methods = methods
        self.textbox.configure(state="normal")
        self.textbox.delete("0.0", "end")
        self.textbox.insert("0.0", f"{top_methods_md}\n\n{str(methods)}")
        self.textbox.configure(state="disabled")
