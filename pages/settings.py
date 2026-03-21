import customtkinter as ctk
from tkinter import StringVar
from util.select_file_dialog import select_file_dialog


class SettingsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.app_config = self.master.get_config()
        self.reporter_path_var= StringVar(self, value=self.app_config["reporter_path"])

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)


        self.reporter_path = PathSelectionFrame(self, name="Reporter path:", path=self.reporter_path_var)
        self.reporter_path.grid(row=0, column=0, sticky="we", padx=10)

        self.save_button = ctk.CTkButton(self, text="Save & Return", command=self.on_save_button)
        self.save_button.grid(row=99, column=0, pady=10, sticky="s")


    def on_save_button(self):
        self.app_config["reporter_path"] = self.reporter_path_var.get()
        self.master.write_config(self.app_config)
        self.master.set_page("HomePage")


class PathSelectionFrame(ctk.CTkFrame):
    def __init__(self, master, name, path):
        super().__init__(master)
        self.path_var = path

        self.grid_columnconfigure((1, 2), weight=1)

        self.label = ctk.CTkLabel(self, text=name)
        self.label.grid(row=0, column=0, sticky="w", padx=(10,5))

        self.path_label = ctk.CTkLabel(self, textvariable=self.path_var, anchor="w", wraplength=400)
        self.path_label.grid(row=0, column=1, sticky="we")

        self.button = ctk.CTkButton(self, text="Select", command=self.open_select_file_dialog, width=60)
        self.button.grid(row=0, column=2, sticky="e")

    def open_select_file_dialog(self):
        path = select_file_dialog()
        if path:
            self.path_var.set(path)
