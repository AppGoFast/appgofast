import customtkinter as ctk
from tkinter import StringVar

class TracingPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.info_text_var = StringVar(self, "Tracing...")
        self.is_dottrace = 0;

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)


        self.label = ctk.CTkLabel(self, textvariable=self.info_text_var)
        self.label.grid(row=0, column=0, sticky="s")
        self.progress = ctk.CTkProgressBar(self, mode="indeterminate")
        self.progress.grid(row=1, column=0, sticky="n")
        self.progress.start()

        self.stop_button = ctk.CTkButton(self, text="Stop", command=self.on_stop_button)
        self.stop_button.grid(row=99, column=0, pady=10, sticky="s")


    def on_stop_button(self):
        if self.is_dottrace:
            self.master.stop_dottrace()
        else:
            self.master.stop_dotnet_trace()

    def toggle_dottrace(self, is_dottrace):
        self.is_dottrace = is_dottrace

    def set_info_text(self, text):
        self.info_text_var.set(text)
