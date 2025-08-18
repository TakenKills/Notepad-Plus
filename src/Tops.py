from customtkinter import CTk, CTkToplevel  # type: ignore
from os.path import dirname, join
from PIL import ImageTk  # type: ignore
from src.Widgets import Widgets
from typing import Callable

from __main__ import __file__ as __main_file__


class Tops:
    @staticmethod
    def setup_top(
        parent: CTk | None,
        title: str,
        withdraw: bool = True,
        quit_parent: bool = True,
        **kwargs,
    ):
        """
        Set up a top-level window with the given title and options.
        If you want to set a geometry use, gemotry="WIDTHxHEIGHT+X+Y"
        Args:
            parent (CTk | None): The parent window. If None, the top-level window will not be modal.
            title (str): The title of the top-level window.
            **kwargs: Additional options for the top-level window.
        Returns:
            CTkToplevel: The created top-level window.
        """
        top = CTkToplevel(parent if parent else None)
        top.title(title)

        if parent:
            if quit_parent:
                top.bind("<Escape>", lambda _e=None: parent.quit())

            if withdraw:
                parent.withdraw()

        if "geometry" in kwargs:
            top.geometry(kwargs["geometry"])
        else:
            top.geometry("300x100")  #! Default geometry

        if "resizable" in kwargs:
            top.resizable(width=False, height=False)

        top.configure(
            fg_color=kwargs.get("fg_color", "#1b1a1b"),  # "#25292e"
        )

        # Set icon
        if parent:
            icon_path = join(dirname(__main_file__), "assets\\notepad+.png")
            icon = ImageTk.PhotoImage(file=icon_path)
            top.wm_iconbitmap()
            top.after(
                300,
                lambda: top.iconphoto(False, icon) if top.winfo_exists() else None,
            )  # * This is done to bypass defaulting bug in customtkinter.

        def destroy():
            top.destroy()

            if parent:
                parent.destroy()

        if "protocol" not in kwargs:
            top.protocol("WM_DELETE_WINDOW", destroy)

        return top

    @staticmethod
    def _base_modal_dialog(
        message: str,
        title: str,
        parent: CTk | None = None,
        min_width: int = 300,
        height: int = 100,
        **kwargs
    ) -> CTkToplevel:
        width = max(min_width, Tops._calculate_width(message))

        screen_width = get_window_width(parent)
        X_COORD = (screen_width // 2) - (width // 2)
        Y_COORD = 150

        dialog_top = Tops.setup_top(
            parent=parent,
            title=title,
            geometry=f"{width}x{height}+{X_COORD}+{Y_COORD}",
            withdraw=False,
            **kwargs
        )
        # Modal and always-on-top
        dialog_top.grab_set()  #! Forces user to interact with this dialog.
        dialog_top.attributes(
            "-topmost", True
        )  #! Makes window stay always on top of all other windows.

        dialog_top.bind("<Escape>", lambda _e=None: dialog_top.destroy())

        dialog_label = Widgets.create_label(dialog_top, text=message)
        dialog_label.pack(pady=15)

        return dialog_top

    @staticmethod
    def show_info(
        message: str,
        title: str,
        root: CTk | None = None,
        min_width: int = 300,
        height: int = 100,
        okay_callback: Callable | None = None,
    ):
        info_top = Tops._base_modal_dialog(message, title, root, min_width, height)

        info_top.bind("<Return>", lambda _e=None: info_top.destroy())

        def okay_command(*_):
            if okay_callback:
                okay_callback()
            info_top.destroy()

        okay_button = Widgets.create_button(
            info_top, text="Okay", width=100, command=okay_command
        )

        okay_button.pack(pady=5)
        okay_button.focus_force()

        return info_top

    @staticmethod
    def show_error(
        error_message: str,
        root: CTk | None = None,
        min_width: int = 300,
        height: int = 100,
    ):
        """
        Show a modal, always-on-top error dialog. If root is provided, parent the dialog to it.
        """
        title = "Oh No! Problem!!"

        error_top = Tops.show_info(error_message, title, root, min_width, height)

        return error_top

    @staticmethod
    def confirmation(
        confirmation_message: str,
        confirm_callback: callable,
        cancel_callback: Callable | None = None,
        root: CTk | None = None,
        min_width: int = 300,
        height: int = 110,
        confirm_button_text: str = "Confirm",
        cancel_button_text: str = "Cancel",
        button_dark_background_color: bool = True,
        **kwargs
    ):
        """
        Show a confirmation top dialog, If root is provided parent the dialog to it.
        """
        title = "Are you sure??"
        confirmation_top = Tops._base_modal_dialog(
            confirmation_message, title, root, min_width, height, **kwargs
        )
        BACKGROUND = "#25292e" if not button_dark_background_color else "#1b1a1b"

        confirm_cancel_frame = Widgets.create_frame(
            confirmation_top, fg_color=BACKGROUND, width=200, height=150
        )
        confirm_cancel_frame.pack(pady=5)

        def confirm(*_):
            confirm_callback()
            confirmation_top.destroy()

        confirm_button = Widgets.create_button(
            confirm_cancel_frame,
            text=confirm_button_text,
            width=80,
            height=30,
            command=confirm,
        )
        confirm_button.pack(pady=10, padx=5, side="left", ipadx=20, ipady=20)

        confirmation_top.bind("<Return>", confirm)

        def cancel(*_):
            if cancel_callback:
                cancel_callback()

            confirmation_top.destroy()

        cancel_button = Widgets.create_button(
            confirm_cancel_frame,
            text=cancel_button_text,
            width=80,
            height=30,
            command=cancel,
        )
        cancel_button.pack(pady=10, padx=5, side="left", ipadx=20, ipady=10)

        return confirmation_top

    @staticmethod
    def _calculate_width(text: str) -> int:
        """
        Calculate the width of the text in pixels.
        This is a placeholder function and should be replaced with actual logic.
        """

        padding = 40 * 2  # 40 pixels padding on each side

        return len(text) * 7 + padding


def get_window_width(root: CTk | None = None):
    """Get the width of the main window if root is None."""
    if root is not None:
        return root.winfo_screenwidth()
    else:
        temp = CTk()
        temp.withdraw()
        width = temp.winfo_screenwidth()
        temp.destroy()
        return width
