import customtkinter as ctk  # type: ignore

DARK_MODE = "#25292e"
WHITE = "#ffffff"
LIGHT_GREY = "#d3d3d3"
BACKGROUND = "#1b1a1b"


class Widgets:
    @staticmethod
    def create_label(parent, **kwargs) -> ctk.CTkLabel:
        label = ctk.CTkLabel(parent, **kwargs)
        label.configure(
            text_color=WHITE, fg_color="transparent", font=("American typewriter", 16)
        )
        return label

    @staticmethod
    def create_button(
        parent,
        text=None,
        command=None,
        width=120,
        height=32,
        fg_color=DARK_MODE,
        hover_color="#444950",
        text_color=WHITE,
        font=("Segoe UI", 14, "bold"),
        border_width=2,
        border_color=LIGHT_GREY,
        corner_radius=8,
        **kwargs
    ) -> ctk.CTkButton:
        button = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width,
            height=height,
            fg_color=fg_color,
            hover_color=hover_color,
            text_color=text_color,
            font=font,
            border_width=border_width,
            border_color=border_color,
            corner_radius=corner_radius,
            **kwargs
        )
        return button

    """width=120,
                        height=32,
                        fg_color="#25292e",
                        hover_color="#444950",
                        text_color="#ffffff",
                        border_width=1,
                        border_color="#d3d3d3",
                        corner_radius=8
                        """

    @staticmethod
    def create_entry(parent, **kwargs) -> ctk.CTkEntry:
        entry = ctk.CTkEntry(parent, **kwargs)
        entry.configure(fg_color=DARK_MODE, text_color=WHITE)
        return entry

    @staticmethod
    def create_frame(parent, **kwargs) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(parent, **kwargs)
        if not "fg_color" in kwargs:
            frame.configure(fg_color=BACKGROUND)
        return frame

    @staticmethod
    def create_listbox(parent, **kwargs):  #! LOOK AT DOCUMENTATION
        # customtkinter does not have a Listbox, fallback to tkinter
        import tkinter as tk

        listbox = tk.Listbox(parent, **kwargs)
        listbox.configure(
            bg=DARK_MODE,
            fg=WHITE,
            selectbackground=WHITE,
            selectforeground=DARK_MODE,
            bd=0,
        )
        return listbox

    @staticmethod
    def create_canvas(parent, **kwargs):  #! LOOK AT DOCUMENTATION
        # customtkinter does not have a Canvas, fallback to tkinter
        import tkinter as tk

        canvas = tk.Canvas(parent, **kwargs)
        canvas.configure(bg=DARK_MODE)
        return canvas

    @staticmethod
    def create_text(parent, **kwargs):  #! LOOK AT DOCUMENTATION
        # customtkinter does not have a Text widget, fallback to tkinter
        import tkinter as tk

        text = tk.Text(parent, **kwargs)
        text.configure(bg=DARK_MODE, fg=WHITE, font=("American typewriter", 9))
        return text
