from customtkinter import CTk, CTkTextbox  # type: ignore
from .Widgets import Widgets
from .Helper import Helper
from os import rename as os_rename
from os.path import join as os_join, dirname as os_dirname

class Open_Notepad:
    def __init__(self, root: CTk, notepad_name: str, set_notepads_func):
        self.root = root
        self.name = notepad_name
        self.set_notepads = set_notepads_func

        self.main_top = Helper.setup_top(
            self.root,
            title=notepad_name,
            geometry="750x750",
            withdraw=False,  #! Calculate Geometry?
            quit_parent=False,
            protocol=False,
        )

        self.root.geometry("+0+0")  # Move the root to the top left of the screen

        self.main_top.bind("<Escape>", lambda _e=None: self.main_top.quit())
        self.root.eval("tk::PlaceWindow %s center" % self.main_top.winfo_toplevel())

        self.main_top.protocol("WM_DELETE_WINDOW", lambda: self.on_delete_window())

        self.main_top.bind("<Control-s>", lambda _e: self.save())
        self.main_top.bind("<Control-e>", lambda _e: self.edit())
        self.main_top.bind("<F2>", lambda _e: self.rename())

        self.uptop_frame = Widgets.create_frame(self.main_top)
        self.setup_buttons()

        self.uptop_frame.pack(pady=5, padx=5)

        self.text_box = CTkTextbox(master=self.main_top)
        self.text_box.bind("<<Modified>>", lambda _e: self.on_modify())
        self.text_box.pack(expand=True, fill="both")

        self.notepad_content = Helper.get_notepad_content(self.name)

        self.text_box.insert(
            "1.0",
            (self.notepad_content if len(self.notepad_content) > 0 else ""),
        )

        self.set_readonly()
        self.is_read_only = True

    def on_modify(self):
        self.text_box.edit_modified(False)

        text_box_content = self.text_box.get("1.0", "end-1c")

        if self.notepad_content != text_box_content:
            return self.main_top.title(f"{self.name}* unsaved")

        self.main_top.title(f"{self.name}")

    def setup_buttons(self):
        self.edit_button = self.create_button("Edit", self.edit)
        self.save_button = self.create_button("Save", self.save)
        self.rename_button = self.create_button("Rename", self.rename)

    def edit(self):
        if self.is_read_only:
            self.edit_button.configure(text="Read-only")
            return self.set_editable()

        self.edit_button.configure(text="Edit")
        self.set_readonly()

    def save(self):
        text_box_content = self.text_box.get("1.0", "end-1c")

        if text_box_content != self.notepad_content:
            saved_successfuly = Helper.edit_notepad_content(
                self.name, new_content=text_box_content
            )

            if saved_successfuly:
                self.main_top.title(self.name)

        return

    def rename(self):
        rename_top = Helper.setup_top(
            self.main_top, title="Rename file", withdraw=False, protocol=False
        )
        rename_top.bind("<Return>", lambda _e: rename_file())
        rename_top.resizable(width=False, height=False)

        rename_entry = Widgets.create_entry(rename_top, placeholder_text="New name")
        rename_top.after(300, rename_entry.focus_set)
        rename_entry.pack()

        def rename_file():
            new_name = rename_entry.get()
            if len(new_name) == 0:
                return

            wants_imported_file_renamed = False

            def rename_original_improted_file():
                wants_imported_file_renamed = True

            if Helper.is_imported(self.name):
                Helper.confirmation(
                    "Do you also want to rename the original imported file?",
                    lambda _e: rename_original_improted_file(),
                    root=rename_top,
                )

            try:
                os_rename(
                    Helper.get_notepad_path(self.name),
                    Helper.get_notepad_path(new_name),
                )

                if wants_imported_file_renamed:
                    real_path = Helper.get_notepad_path(self.name, real=True)
                    os_rename(real_path, os_join(os_dirname(real_path), new_name))

                Helper.show_info(
                    f"Renamed '{self.name}' to '{new_name}'", title="Success!"
                )

                self.name = new_name
                self.main_top.title(self.name)
                rename_top.destroy()
                self.set_notepads()

            except Exception as e:
                print(e)
                Helper.show_error("Failed to rename file.", rename_top)

        button = Widgets.create_button(
            rename_top,
            text="Rename",
            command=rename_file,
        )
        button.pack(pady=10, padx=5)

    def on_delete_window(self):
        text_box_content = self.text_box.get("1.0", "end-1c")

        cofirmation_top = None

        def on_yes():
            return self.main_top.destroy()  # Close the open notepad.

        def on_no():
            if cofirmation_top:
                return cofirmation_top.destroy()
            # Close the confirmation top and return to the notepad

        if text_box_content != self.notepad_content:
            cofirmation_top = Helper.confirmation(
                "You have unsaved changes. Are you sure you want to close without saving?",
                confirm_button_text="Yes",
                cancel_button_text="No",
                confirm_callback=on_yes,
                cancel_callback=on_no,
                root=self.main_top,
                button_dark_background_color=True,
                protocol=False,
                quit_parent=False,
            )

        else:
            return self.main_top.destroy()

    def create_button(self, text: str, callback=None):
        button = Widgets.create_button(
            self.uptop_frame, text=text, command=callback, width=40, height=20
        )
        button.pack(pady=10, padx=5, side="left")

        return button

    def set_readonly(self):
        self.text_box.configure(state="disabled")
        self.is_read_only = True

    def set_editable(self):
        self.text_box.configure(state="normal")
        self.is_read_only = False
