import customtkinter as ctk
from tkinter import StringVar

class LoadingPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.info_text_var = StringVar(self, "Loading...")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)


        self.label = ctk.CTkLabel(self, textvariable=self.info_text_var)
        self.label.grid(row=0, column=0, sticky="s")
        self.progress = ctk.CTkProgressBar(self, mode="indeterminate")
        self.progress.grid(row=1, column=0, sticky="n")
        self.progress.start()

        #self.cancel_button = ctk.CTkButton(self, text="Cancel", fg_color="firebrick3", hover_color="firebrick4", command=self.cancel_button_event)
        #self.cancel_button.grid(row=99, column=0, pady=10, sticky="s")


    def cancel_button_event(self):
        self.master.set_page("OutputPage")

    def set_info_text(self, text):
        self.info_text_var.set(text)
