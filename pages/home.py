import customtkinter as ctk
from tkinterdnd2 import DND_ALL

class HomePage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.input_file_path = ""

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)


        self.settings_button = ctk.CTkButton(self, text="⚙️", width=35, corner_radius=0, border_spacing=0, font=("", -25), fg_color="transparent", command=self.settings_button_event)
        self.settings_button.grid(row=0, column=0, sticky="e")

        self.label = ctk.CTkLabel(self, text="Drop profiler output .xml here")
        self.label.grid(row=1, column=0)
        self.drop_target_register(DND_ALL)
        self.dnd_bind("<<Drop>>", self.file_drop_event)

        self.analyze_button = ctk.CTkButton(self, text="Analyze", command=self.analyze_button_event, state="disabled")
        self.analyze_button.grid(row=99, column=0, pady=10, sticky="s")


    def settings_button_event(self):
        self.master.set_page("SettingsPage")

    def file_drop_event(self, event):
        self.input_file_path = event.data
        self.label.configure(text = self.input_file_path)
        self.analyze_button.configure(state="normal")

    def analyze_button_event(self):
        if self.input_file_path:
            self.master.analyze(self.input_file_path)
