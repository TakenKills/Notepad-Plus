from src.Helper import Helper
from src.Widgets import Widgets
from .Open_Notepad import Open_Notepad
from customtkinter import CTkScrollableFrame  # type: ignore
from tkinter import filedialog
from os.path import basename, isfile


HIGHLIGHT_BUTTON_COLOR = "#444950"
DEFAULT_BUTTON_COLOR = "#25292e"

BUTTON_HEIGHT = 30


class Master:
    """
    The Master class initializes the main application window and sets up the UI components.
    It is responsible for displaying the main content of the application.
    """

    def __init__(self, root):
        self.root = root
        self.width = self.root.winfo_width()
        self.setup_ui()

    def setup_ui(self):

        # Text
        self.text = Widgets.create_label(self.root, text="Notepad+!")
        self.text.pack(pady=20)

        # Input Entry (for creating a new notepad)
        self.input_entry = Widgets.create_entry(
            self.root, placeholder_text="New Notepad Name:", width=300
        )
        self.input_entry.pack(pady=10, padx=20, fill="x")
        self.input_entry.focus_set()
        self.input_entry.bind("<Return>", self.create_notepad)

        # Create and Import Buttons in a Frame

        self.create_import_buttons_frame = Widgets.create_frame(self.root)
        self.create_import_buttons_frame.pack(pady=10)

        self.create_button = Widgets.create_button(
            self.create_import_buttons_frame,
            text="Create",
            command=self.create_notepad,
            width=100,
            height=BUTTON_HEIGHT,
        )
        # pack the button right next to the entry
        self.create_button.pack(pady=10, padx=5, side="left")

        self.import_button = Widgets.create_button(
            self.create_import_buttons_frame,
            text="Import 🔗",
            command=self.import_file,
            width=100,
            height=BUTTON_HEIGHT,
        )
        self.import_button.pack(pady=10, padx=5, side="left")

        # Scrollable Frame for viewing notepads

        self.scrollable_frame = CTkScrollableFrame(
            self.root,
            width=self.width,
            height=200,
        )
        self.scrollable_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.root.update()
        self.scrollable_frame.focus_set()

        self.buttons = []
        self.selected_button_index = 0

        # Set up all existing notepads (if any)
        self.set_notepads()

        self.highlight_selected()

        self.scrollable_frame.bind_all("<Up>", self.navigate_up)
        self.scrollable_frame.bind_all("<Down>", self.navigate_down)
        self.scrollable_frame.bind("<Return>", self.on_enter)

        self.delete_button = Widgets.create_button(
            self.root,
            text="Delete",
            command=self.confirm_and_delete_selected_notepad,
            width=100,
            height=BUTTON_HEIGHT,
        )
        self.delete_button.pack(pady=10, padx=5)

    def highlight_selected(self):
        for index, button in enumerate(self.buttons):
            if index == self.selected_button_index:
                button.configure(fg_color=HIGHLIGHT_BUTTON_COLOR)
            else:
                button.configure(fg_color=DEFAULT_BUTTON_COLOR)

    def navigate_up(self, _event):
        if self.root.focus_get() != self.scrollable_frame:
            self.scrollable_frame.focus_set()
        if self.selected_button_index > 0:
            self.selected_button_index -= 1
            self.highlight_selected()
            self.scroll_to_button()

    def navigate_down(self, _event):
        if self.root.focus_get() != self.scrollable_frame:
            self.scrollable_frame.focus_set()

        if self.selected_button_index < len(self.buttons) - 1:
            self.selected_button_index += 1
            self.highlight_selected()
            self.scroll_to_button()

    def on_enter(self, _event):
        if len(self.buttons) > 0:
            self.buttons[self.selected_button_index].invoke()
        else:
            return

    def scroll_to_button(self):
        self.scrollable_frame._parent_canvas.yview(
            "moveto", 0.1 * self.selected_button_index
        )  # * Little cheese... but it works :D

    def set_notepads(self):
        """
        Set up the notepads from the directory.
        This method should be called to refresh the list of notepads.
        """
        notepads = Helper.get_notepad_names()

        if len(self.buttons) > 0:
            for button in self.buttons[:]:
                button.destroy()
                self.buttons.remove(button)

        if len(notepads) == 0:
            return  # No notepads to display

        for notepad in notepads:
            self.create_notepad_button(notepad[:-4])

        self.validate_notepads()

    def validate_notepads(self):
        """
        Validate the notepads in the scrollable frame.
        This method should be called to ensure all notepads are valid.
        """
        for button in self.buttons[:]:  # Creating a shallow copy...
            notepad_name = button.cget("text")

            # Check if only the imported REAL files still exist.
            if not Helper.file_exists(
                Helper.get_notepad_path(notepad_name, imported=True, real=True)
            ) and Helper.is_imported(notepad_name):
                # If the notepad file does
                Helper.show_error(
                    f"Notepad '{notepad_name}' does not exist. Removing from list. And deleting file.",
                    self.root,
                )  #! This shows on the password dialog, how to fix this?
                button.destroy()
                self.buttons.remove(button)
                Helper.delete_notepad(notepad_name)

    def create_notepad_button(self, notepad_name: str):
        """
        Create a button for a notepad and add it to the scrollable frame.
        """
        button = Widgets.create_button(
            self.scrollable_frame,
            text=notepad_name,
            command=lambda: self.open_notepad(notepad_name),
            width=100,
            height=BUTTON_HEIGHT,
        )

        button.pack(pady=5, padx=5, fill="x")
        self.buttons.append(button)

    def import_file(self):
        """
        Import a file and add it as a notepad.
        This method should open a file dialog to select a file.
        """

        file_paths = filedialog.askopenfilenames(
            title="Select a file to import",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )

        if not file_paths or len(file_paths) == 0:
            return

        for file_path in file_paths:
            if not isfile(file_path):
                Helper.show_error(f"File {basename(file_path)} does not exist.")
                continue

            notepad_name = basename(file_path).replace(".txt", "")
            imported_app_notepad_path = Helper.get_notepad_path(
                notepad_name, imported=True, real=False
            )

            if Helper.file_exists(imported_app_notepad_path):
                Helper.show_error(
                    f"Notepad '{notepad_name}' already exists. Please choose a different file.",
                    self.root,
                )
                continue

            # Save the imported notepad
            Helper.save_imported_notepad(notepad_name, file_path)
            self.create_notepad_button(notepad_name)

    def confirm_and_delete_selected_notepad(self):
        if len(self.buttons) == 0:
            return

        selected_notepad_name = self.buttons[self.selected_button_index].cget("text")

        Helper.confirmation(
            f"Are you sure you want to delete '{selected_notepad_name}'?",
            confirm_callback=confirm_deletion,
            height=120,
            root=self.root,
        )

        def confirm_deletion():
            successfully_deleted = Helper.delete_notepad(selected_notepad_name)

            if successfully_deleted:
                Helper.show_info(
                    f"Notepad: {selected_notepad_name} has been successfully deleted.",
                    title="Success!",
                    root=self.root,
                )

                self.set_notepads()
                self.highlight_selected()

    def create_notepad(self, _event=None):
        self.scrollable_frame.focus_set()

        new_notepad_name = self.input_entry.get()

        if new_notepad_name == "":
            return

        successfully_created_notepad = Helper.create_notepad(new_notepad_name)

        if not successfully_created_notepad:
            Helper.show_error("Error creating file.")

        self.set_notepads()
        self.input_entry.delete(0, "end")

    def open_notepad(self, notepad_name: str):  # TODO
        Open_Notepad(self.root, notepad_name, self.set_notepads)


# * Features:
"""
! View File --> Shortcut support (Within an OPEN FILE)
! Edit File --> (Within on OPEN FILE) 
* Save Button + shortcut, Enable/Disable Edit button,
? Rename File --> Within an OPEN FILE or what??

"""
