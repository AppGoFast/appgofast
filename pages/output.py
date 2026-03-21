import customtkinter as ctk

class OutputPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)


        self.textbox = ctk.CTkTextbox(self)
        self.textbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.textbox.insert("0.0", "your app sucks!\n" * 50)
        self.textbox.configure(state="disabled")

        self.input_frame = InputFrame(self, on_reanalyze=self.master.re_analyze)
        self.input_frame.grid(row=1, column=0, sticky="we", padx=5)

        self.reset_button = ctk.CTkButton(self, text="Reset", fg_color="firebrick3", hover_color="firebrick4",  command=self.reset_button_event)
        self.reset_button.grid(row=99, column=0, pady=10, padx=10, sticky="ws")


    def reset_button_event(self):
        self.master.set_page("HomePage")

    def set_result(self, result):
        self.input_frame.clear_input()
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", result)
        self.textbox.configure(state="disabled")


class InputFrame(ctk.CTkFrame):
    def __init__(self, master, on_reanalyze):
        super().__init__(master)
        self.on_reanalyze_callback = on_reanalyze

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.configure(fg_color="transparent")


        self.label = ctk.CTkLabel(self, text="Your input:")
        self.label.grid(row=0, column=0, padx=(1, 6), sticky="wn")

        self.entry = ctk.CTkTextbox(self, height=55)
        self.entry.grid(row=0, column=1, sticky="we")
        self.entry.bind("<KeyRelease>", self.on_entry_change)

        self.button = ctk.CTkButton(self, text="Re-analyze", width=20, command=self.on_reanalyze, state="disabled")
        self.button.grid(row=0, column=2, padx=(5, 0), pady=1, sticky="wn")


    def on_reanalyze(self):
        entry_input = self.entry.get(1.0, "end-1c").strip()
        if entry_input:
            self.on_reanalyze_callback(entry_input)

    def on_entry_change(self, event):
        self.button.configure(state="normal" if self.entry.get("1.0", "end-1c").strip() else "disabled")

    def clear_input(self):
        self.entry.delete("1.0", "end")
        self.button.configure(state="disabled")
