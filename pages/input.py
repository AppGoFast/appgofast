import customtkinter as ctk
from ctk_markdown import CTkMarkdown
from frames.BottomButtonsFrame import BottomButtonsFrame

class InputPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.profiling_data_json = ""

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.textbox = ctk.CTkTextbox(self, state="disabled")
        self.textbox.grid(row=0, column=0, sticky="wnes")

        self.bottom_buttons = BottomButtonsFrame(self, name1="Return to Profiling", command1=self.on_return_home, name2="Analyze with AI", command2=self.on_analyze)
        self.bottom_buttons.grid(row=99, column=0, pady=10, padx=10, sticky="s")


    def on_return_home(self):
        self.master.set_page("HomePage")

    def on_analyze(self):
        self.master.analyze(self.profiling_data_json)

    def set_text(self, text):
        self.profiling_data_json = text
        self.textbox.configure(state="normal")
        self.textbox.delete("0.0", "end")
        self.textbox.insert("0.0", text)
        self.textbox.configure(state="disabled")
