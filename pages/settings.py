import customtkinter as ctk
from tkinter import StringVar, filedialog
from frames.BottomButtonsFrame import BottomButtonsFrame
from frames.LongTextVarFrame import LongTextVarFrame


class SettingsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.app_config = self.master.config

        self.reporter_path_var = StringVar(self, value=self.app_config["reporter_path"])
        self.dottrace_path_var = StringVar(self, value=self.app_config["dottrace_path"])
        self.snapshot_folder_var = StringVar(self, value=self.app_config["snapshot_folder"])
        self.api_key_var = StringVar(self, value=self.app_config["api_key"])
        self.ai_models = self.app_config["ai_models"]
        self.selected_ai_model_var = StringVar(self, value=self.app_config["selected_ai_model"])
        self.selected_ai_model2_var = StringVar(self, value=self.app_config["selected_ai_model2"])

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.settings_frame = SettingsFrame(self, self.reporter_path_var, self.dottrace_path_var, self.snapshot_folder_var, self.api_key_var, self.ai_models, self.selected_ai_model_var, self.selected_ai_model2_var)
        self.settings_frame.configure(corner_radius=0)
        self.settings_frame.grid(row=0, column=0, sticky="nesw")

        self.bottom_buttons = BottomButtonsFrame(self, name1="Discard & Return", command1=self.on_cancel_button, name2="Save & Return", command2=self.on_save_button)
        self.bottom_buttons.grid(row=99, column=0, pady=10, padx=10, sticky="s")


    def on_save_button(self):
        self.app_config["reporter_path"] = self.reporter_path_var.get()
        self.app_config["dottrace_path"] = self.dottrace_path_var.get()
        self.app_config["snapshot_folder"] = self.snapshot_folder_var.get()
        self.app_config["api_key"] = self.api_key_var.get()
        self.app_config["selected_ai_model"] = self.selected_ai_model_var.get()
        self.app_config["selected_ai_model2"] = self.selected_ai_model2_var.get()

        self.master.write_config(self.app_config)
        self.master.set_page("HomePage")

    def on_cancel_button(self):
        self.reporter_path_var.set(self.app_config["reporter_path"])
        self.dottrace_path_var.set(self.app_config["dottrace_path"])
        self.snapshot_folder_var.set(self.app_config["snapshot_folder"])
        self.api_key_var.set(self.app_config["api_key"])
        self.selected_ai_model_var.set(self.app_config["selected_ai_model"])
        self.selected_ai_model2_var.set(self.app_config["selected_ai_model2"])

        self.master.set_page("HomePage")


class SettingsFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, reporter_path_var, dottrace_path_var, snapshot_folder_var, api_key_var, ai_models, selected_ai_model_var, selected_ai_model2_var):
        super().__init__(master)

        self.reporter_path_var = reporter_path_var
        self.dottrace_path_var = dottrace_path_var
        self.snapshot_folder_var = snapshot_folder_var
        self.api_key_var = api_key_var
        self.ai_models = ai_models
        self.selected_ai_model_var = selected_ai_model_var
        self.selected_ai_model2_var = selected_ai_model2_var

        self.toggle_advanced_settings_var = StringVar(self, value="0")

        self.grid_columnconfigure(0, weight=1)

        self.reporter_path = PathSelectionFrame(self, name="Reporter path:", path_var=self.reporter_path_var)
        self.reporter_path.grid(row=1, column=0, sticky="we", padx=10, pady=(10,5))

        self.dottrace_path = PathSelectionFrame(self, name="dotTrace path:", path_var=self.dottrace_path_var)
        self.dottrace_path.grid(row=2, column=0, sticky="we", padx=10, pady=(10,5))

        self.snapshot_folder = PathSelectionFrame(self, name="Snapshots folder:", path_var=self.snapshot_folder_var, is_folder=1)
        self.snapshot_folder.grid(row=3, column=0, sticky="we", padx=10, pady=(10,5))

        self.api_key = TextVarFrame(self, name="Gemini API key:", text_var=self.api_key_var)
        self.api_key.grid(row=4, column=0, sticky="we", padx=10, pady=5)

        self.toggle_advanced_settings = ctk.CTkSwitch(self, text="Advanced settings",command=self.on_toggle_advanced_settings, variable=self.toggle_advanced_settings_var, offvalue="0", onvalue="1")
        self.toggle_advanced_settings.grid(row=5, column=0, sticky="we", padx=11, pady=5)

        self.ai_model_selector = DropDownSelectorFrame(self, name="AI model:", values=self.ai_models, selected_var=self.selected_ai_model_var)

        self.ai2_model_selector = DropDownSelectorFrame(self, name="AI model 2:", values=self.ai_models, selected_var=self.selected_ai_model2_var)


    def on_toggle_advanced_settings(self):
        if self.toggle_advanced_settings_var.get() == "1":
            self.ai_model_selector.grid(row=6, column=0, sticky="we", padx=10, pady=5)
            self.ai2_model_selector.grid(row=7, column=0, sticky="we", padx=10, pady=5)

        else:
            self.ai_model_selector.grid_forget()

            self.ai2_model_selector.grid_forget()


class PathSelectionFrame(ctk.CTkFrame):
    def __init__(self, master, name, path_var, file_extension=".exe", is_folder=0):
        super().__init__(master)
        self.path_var = path_var
        self.file_extension = file_extension
        self.is_folder = is_folder

        self.grid_columnconfigure((1, 2), weight=1)

        self.label = ctk.CTkLabel(self, text=name, width=100, anchor="w")
        self.label.grid(row=0, column=0, sticky="w", padx=(10,5))

        self.path_label = ctk.CTkLabel(self, textvariable=self.path_var, anchor="w", wraplength=400)
        self.path_label.grid(row=0, column=1, sticky="we")

        self.button = ctk.CTkButton(self, text="Select", command=self.open_select_file_dialog, width=60)
        self.button.grid(row=0, column=2, sticky="e")

    def open_select_file_dialog(self):
        if self.is_folder:
            path = filedialog.askdirectory()
        else:
            path = filedialog.askopenfilename(filetypes=[("Files", f"*{self.file_extension}")])
        if path:
            self.path_var.set(path)


class TextVarFrame(ctk.CTkFrame):
    def __init__(self, master, name, text_var):
        super().__init__(master)
        self.text_var = text_var

        self.grid_columnconfigure(1, weight=1)

        self.label = ctk.CTkLabel(self, text=name, width=100, anchor="w")
        self.label.grid(row=0, column=0, sticky="w", padx=(10, 5))

        self.var_entry = ctk.CTkEntry(self, textvariable=self.text_var)
        self.var_entry.grid(row=0, column=1, sticky="we")

class DropDownSelectorFrame(ctk.CTkFrame):
    def __init__(self, master, name, values, selected_var):
        super().__init__(master)
        self.selected_var = selected_var

        self.grid_columnconfigure(1, weight=1)

        self.label = ctk.CTkLabel(self, text=name, width=100, anchor="w")
        self.label.grid(row=0, column=0, sticky="w", padx=(10, 5))

        self.selector = ctk.CTkOptionMenu(self, values=values, variable=self.selected_var)
        self.selector.grid(row=0, column=1, sticky="we")
