from os.path import splitext
from tkinter import Tk, filedialog
from tkinter.ttk import Frame
from classes.helper import Helper
from classes.view_file import ViewFile
from classes.Widgets import Widgets
from classes.editmenu import EditMenu

class Master:
    def __init__(self, root: Tk):
        self.root = root
        self.x = self.root.winfo_width()

        self.frame_y = self.root.winfo_screenheight() / 6
        self.views = []

        self.root.focus_set()

        self.text = Widgets.create_label(self.root, text="Notepad Plus!")
        self.text.place(anchor="n", y=25, x=self.x / 2)

        self.input_entry = Widgets.create_entry(self.root)
        self.input_entry.place(anchor="n", y=50, x=self.x / 2)
        self.input_entry.bind("<Return>", self.create)
        self.input_entry.focus_set()

        self.create_button = Widgets.create_button(self.root, text="Create", command=self.create)
        self.create_button.place(anchor="n", x=(self.x / 2) + 105, y=48)

        self.importfile_button = Widgets.create_button(self.root, text="Import 🔗", command=self.import_file)
        self.importfile_button.place(anchor="n", x=(self.x / 2) + 105, y=20)

        self.list_frame = Frame(self.root)

        self.list_scrollbar = Widgets.create_scrollbar(self.list_frame, orient="vertical")

        self.list_box = Widgets.create_listbox(self.list_frame, width=40, yscrollcommand=self.list_scrollbar.set, selectmode="extended", activestyle="none")

        self.list_box.bind("<Double-Button>", self.view)

        self.list_scrollbar.config(command=self.list_box.yview)
        self.list_scrollbar.pack(side="right", fill="y")

        self.list_frame.place(x=85, y=self.frame_y, anchor="w")

        self.list_box.pack()

        self.view_button = Widgets.create_button(self.root, text="View", command=self.view)
        self.view_button.place(y=self.frame_y + 90, x=90)

        self.edit_button = Widgets.create_button(self.root, text="Edit", command=self.open_editmenu)
        self.edit_button.place(y=self.frame_y + 90, x=165)
        self.delete_button = Widgets.create_button(self.root, text="Delete", command=self.delete)
        self.delete_button.place(y=self.frame_y + 90, x=240)

        self.delete_button = Widgets.create_button(self.root, text="Delete All", command=self.delete_all)
        self.delete_button.place(y=self.frame_y + 118, x=165)

        self.set_notepads()



    def import_file(self):
        file = self.ask_import_file()

        if not file or not Helper.file_exists(file):
            return

        (file_name, ext) = splitext(file)

        if ext != ".txt":
            Helper.show_error("Currently only \".txt\" file extensions are supported.", self.root)
            return

        if not Helper.add_notepad(None, file, imported=True):
            Helper.show_error("A notepad by that name already exists.", self.root)
            return

        name: str = file.split("/")[-1].split(".")[0]

        self.list_box.insert("end", name)

    @staticmethod
    def ask_import_file():
        return filedialog.askopenfilename(initialdir="/", title="Select file", filetypes=(("Files", "*"), ("All files", "*.*")))

    def open_editmenu(self):
        selected = self.list_box.curselection()

        if len(selected) > 1:
            Helper.show_error("Please select only one notepad.", self.root)
            return

        if len(selected) == 0:
            Helper.show_error("Please select a notepad.", self.root)
            return

        selected = selected[0]

        name = self.list_box.get(selected)

        path = Helper.get_notepad_path(name)

        try:
            if not Helper.file_exists(path):
                path = Helper.get_notepad_path_raw(name, imported=True)
                if not Helper.file_exists(path):
                    Helper.show_error("The notepad you selected does not exist.", self.root)
                    return
        except:
            Helper.show_error("The notepad you selected does not exist anymore.", self.root)
            return

        EditMenu(name, path, self.root, self.list_box)

    def view(self, *_):
        selected = self.list_box.curselection()
        if len(selected) > 1:
            Helper.show_error("Please select only one notepad.", self.root)
            return

        if len(selected) == 0:
            Helper.show_error("Please select a notepad.", self.root)
            return

        name = self.list_box.get(selected[0])

        try:
            if not Helper.file_exists(Helper.get_notepad_path(name)):
                if not Helper.file_exists(Helper.get_notepad_path(name, imported=True)):
                    Helper.show_error("The notepad does not exist.", self.root)
                    return
                else:
                    ViewFile(self.root, name, True)
                    return
        except:
            Helper.show_error("The notepad does not exist.", self.root)
            return

        ViewFile(self.root, name)

    def create(self, *_):
        name = self.input_entry.get()
        if name == "":
            Helper.show_error("Please enter a name.", self.root)
            return
        self.input_entry.delete(0, "end")

        if not Helper.add_notepad(name):
            Helper.show_error("That notepad already exists.", self.root)
            return

        self.add_view(name)

    def delete(self, *_):
        selected = self.list_box.curselection()

        if len(selected) == 0:
            Helper.show_error("Please select a notepad.", self.root)
            return

        self.delete_notepads(selected)

    def add_view(self, name):
        self.views.append(name)
        self.set_views()

    def remove_view(self, name):
        if name in self.views:
            self.views.remove(name)
            self.set_views()

    def set_views(self):
        items: list = self.list_box.get(0, "end")

        for view in self.views:
            print(view);
            if view in items:
                continue
            else:
                print(Helper.file_exists(Helper.get_notepad_path(view)));
                if Helper.file_exists(Helper.get_notepad_path(view)):
                    print(f"added file {view}")
                    self.list_box.insert("end", view)

    def delete_all(self):
        all_names = self.list_box.get(0, "end")
        all_indexes = tuple(range(len(all_names)))

        if len(all_indexes) == 0:
            Helper.show_error("Please select a notepad.", self.root)
            return

        self.delete_notepads(all_indexes)

    def delete_notepads(self, notes: tuple[int], remove: bool = True, cb: callable = None):
        _names = [self.list_box.get(n) for n in notes]
        names = ", ".join(_names)

        wording = f"these notepads:\n{names}" if len(notes) > 1 else f"\"{names}\""

        Helper.confirmation("Deletion", f"Are you sure you want to delete {wording}?",
                            lambda: execute(reversed(_names), remove), self.root)

        def execute(selected, remove_list):
            for name in selected:
                delete = Helper.delete_notepad(name)

                if not delete:
                    Helper.show_error("That notepad does not exist.", self.root)
                    return
                elif delete == "perm":
                    Helper.show_error("I do not have permissions to delete files. Please run me as an administrator.", self.root)
                    return

                if remove_list:
                    self.list_box.delete(list(self.list_box.get(0, "end")).index(name))
                self.remove_view(name)
            if type(cb) == callable:
                cb()

    def set_notepads(self):
        notepads: list[str] = Helper.get_notepads()
        
        if len(notepads) == 0:
            return

        for notepad in notepads:
            self.list_box.insert("end", notepad.removesuffix(".txt"))
            self.views.append(notepad)
