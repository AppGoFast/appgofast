import customtkinter as ctk

class BottomButtonsFrame(ctk.CTkFrame):
    def __init__(self, master, name1, command1, name2, command2, left_is_red = 1):
        super().__init__(master)
        self.configure(fg_color="transparent")
        self.grid_columnconfigure((0, 1), weight=1)

        if left_is_red:
            self.button1 = ctk.CTkButton(self, text=name1, fg_color="firebrick3", hover_color="firebrick4", command=command1)
        else:
            self.button1 = ctk.CTkButton(self, text=name1, command=command1)
        self.button1.grid(row=0, column=0, padx=(0, 10))

        self.button1 = ctk.CTkButton(self, text=name2, command=command2)
        self.button1.grid(row=0, column=1)
