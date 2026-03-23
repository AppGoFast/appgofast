import customtkinter as ctk
from tkinter import StringVar
from util.select_file_dialog import select_file_dialog


class SettingsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.app_config = self.master.get_config()
        self.reporter_path_var = StringVar(self, value=self.app_config["reporter_path"])
        self.api_key_var = StringVar(self, value=self.app_config["api_key"])

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((1, 2), weight=1)

        self.title = ctk.CTkLabel(self, text="Settings:", font=("TkTextFont",18))
        self.title.grid(row=0, column=0, padx=20, pady=10, sticky="n")

        self.reporter_path = PathSelectionFrame(self, name="Reporter path:", path=self.reporter_path_var)
        self.reporter_path.grid(row=1, column=0, sticky="esw", padx=10, pady=5)

        self.api_key = TextVarFrame(self, name="API key:", text_var=self.api_key_var)
        self.api_key.grid(row=2, column=0, sticky="wne", padx=10, pady=5)

        self.bottom_buttons = BottomButtonsFrame(self, name1="Discard & Return", command1=self.on_cancel_button, name2="Save & Return", command2=self.on_save_button)
        self.bottom_buttons.grid(row=99, column=0, pady=10, padx=10, sticky="s")


    def on_save_button(self):
        self.app_config["reporter_path"] = self.reporter_path_var.get()
        self.app_config["api_key"] = self.api_key_var.get()
        self.master.write_config(self.app_config)
        self.master.set_page("HomePage")

    def on_cancel_button(self):
        self.reporter_path_var.set(self.app_config["reporter_path"])
        self.api_key_var.set(self.app_config["api_key"])
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


class TextVarFrame(ctk.CTkFrame):
    def __init__(self, master, name, text_var):
        super().__init__(master)
        self.text_var = text_var

        self.grid_columnconfigure(1, weight=1)

        self.label = ctk.CTkLabel(self, text=name)
        self.label.grid(row=0, column=0, sticky="w", padx=(10, 5))

        self.var_entry = ctk.CTkEntry(self, textvariable=self.text_var)
        self.var_entry.grid(row=0, column=1, sticky="we")


class BottomButtonsFrame(ctk.CTkFrame):
    def __init__(self, master, name1, command1, name2, command2):
        super().__init__(master)
        self.configure(fg_color="transparent")
        self.grid_columnconfigure((0, 1), weight=1)

        self.button1 = ctk.CTkButton(self, text=name1, fg_color="firebrick3", hover_color="firebrick4", command=command1)
        self.button1.grid(row=0, column=0, padx=(0, 10))

        self.button1 = ctk.CTkButton(self, text=name2, command=command2)
        self.button1.grid(row=0, column=1)
