import customtkinter as ctk

class LongTextVarFrame(ctk.CTkFrame):
    def __init__(self, master, name, text_var, height=150):
        super().__init__(master)
        self.text_var = text_var

        self.grid_columnconfigure(1, weight=1)

        self.label = ctk.CTkLabel(self, text=name, width=100, anchor="nw")
        self.label.grid(row=0, column=0, sticky="swn", padx=(10, 5), pady=5)

        self.textbox = ctk.CTkTextbox(self, height=height)
        self.textbox.grid(row=0, column=1, sticky="we")

        self.textbox.insert("0.0", self.text_var.get())
        self.textbox.bind("<KeyRelease>", self.on_text_changed)


    def on_text_changed(self, event):
        self.text_var.set(self.textbox.get("0.0", "end").strip())
