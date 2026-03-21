import customtkinter as ctk

class SettingsPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)


        self.label = ctk.CTkLabel(self, text="SettingsPage")
        self.label.grid(row=0, column=0)

        self.save_button = ctk.CTkButton(self, text="Save & Return", command=self.save_button_event)
        self.save_button.grid(row=99, column=0, pady=10, sticky="s")


    def save_button_event(self):
        self.master.set_page("HomePage")

