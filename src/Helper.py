from os.path import dirname, join, abspath, exists, isfile, isdir
from os import mkdir, walk, remove as os_remove_file
from __main__ import __file__ as __main_file__
from tkinter import PhotoImage
from src.Tops import Tops


class Helper(Tops):
    @staticmethod
    def get_notepads_directory(imported: bool = False):
        """
        Get the directory where notepad files are stored.
        Args:
            imported (bool): If True, returns the directory for imported notepads.
                             If False, returns the main notepads directory.
        Returns:
            str: The path to the notepads directory.
        """
        _path = dirname(abspath(__main_file__))
        path = (
            join(_path, "notepads")
            if not imported
            else join(_path, "notepads", "imported")
        )

        if not Helper.dir_exists(path):
            mkdir(path)

        return path

    @staticmethod
    def dir_exists(path):
        """
        Check if a directory exists at the given path.
        """
        try:
            return exists(path) and isdir(path)
        except PermissionError:
            Helper.show_error("Permission Error: No permission to access: " + path)
            return False
        except Exception:
            Helper.show_error(
                "The directory does not exist or is not a directory: " + path
            )
            return False

    @staticmethod
    def file_exists(path) -> bool:

        if not path:
            return False

        try:
            does_exist = exists(path) and isfile(path)
            return does_exist
        except PermissionError:
            Helper.show_error("Permission Error: No permission to access: " + path)
            return False
        except Exception:
            Helper.show_error("The file does not exist or is not a file: " + path)
            return False

    @staticmethod
    def set_icon(window):
        ico_path = join(dirname(__main_file__), "assets\\notepad+.ico")  # For Windows.

        try:
            window.iconbitmap(ico_path)
            window.wm_iconbitmap(True, ico_path)
        except Exception:
            # Fallback to PNG if .ico fails
            icon = PhotoImage(file=join(dirname(__main_file__), "assets\\notepad+.png"))
            window.iconphoto(True, icon)

    @staticmethod
    def get_notepad_path(
        notepad_name: str, imported: bool = False, real: bool = False
    ):  # * NEW
        """
        Get the full app path to a notepad file. (If you want real use real=True)
        """
        notepads_dir = Helper.get_notepads_directory(imported)
        notepad_path = join(notepads_dir, notepad_name + ".txt")

        if imported and real:
            notepad_path = Helper._get_imported_notepad_path(notepad_name)

        return notepad_path

    def _get_imported_notepad_path(
        notepad_name: str,
    ):  # * This is needed for the import functionality. The imported file will contain only the absolute path to the real notepad.
        # * NEW
        """
        Get the full (REAL) path to an imported notepad file. (NOT FOR USAGE) use get_notepad_path instead.
        Args:
            notepad_name (str): The name of the notepad file without extension.
        Returns:
            str: The full path to the imported notepad file.
            None: If the file does not exist or the path is invalid.
        """
        application_file_path = join(
            Helper.get_notepads_directory(imported=True), notepad_name + ".txt"
        )

        if not Helper.file_exists(application_file_path):
            return None

        with open(application_file_path, "r") as file:
            real_notepad_path = file.read().strip()
            if Helper.file_exists(real_notepad_path):
                return real_notepad_path
            else:
                return None

    @staticmethod
    def get_notepad_content(notepad_name: str, imported: bool = False):  # * NEW
        """
        Get the content of a notepad file.
        """
        notepad_path = Helper.get_notepad_path(notepad_name, imported)

        if not Helper.file_exists(notepad_path):
            Helper.show_error(f"The notepad file '{notepad_name}.txt' does not exist.")
            return ""

        try:
            with open(notepad_path, "r") as file:
                return file.read()
        except Exception as e:
            Helper.show_error(f"Error reading notepad file: {e}")
            return ""

    @staticmethod
    def edit_notepad_content(notepad_name: str, new_content: str):
        """
        Edit the content of a notepad file.
        If imported it will edit the ORIGINAL notepad.
        """

        notepad_path = Helper.get_notepad_path(
            notepad_name, imported=Helper.is_imported(notepad_name)
        )

        if not Helper.file_exists(notepad_path):
            Helper.show_error(f"The notepad file '{notepad_name}.txt' does not exist.")

            return False

        try:
            with open(notepad_path, "w") as file:
                file.write(new_content)
        except Exception as e:
            Helper.show_error(f"Error saving notepad file: {e}")
            return False

        return True

    @staticmethod
    def get_notepad_names() -> list[str]:
        """
        Get a list of all notepad names (with extensions) in the notepads directory.
        """
        notepads_dir = Helper.get_notepads_directory()
        paths = walk(notepads_dir)

        def check_file(file: str):
            notepad_dir = isfile(join(notepads_dir, file))
            imported = isfile(join(notepads_dir, "imported", file))

            return notepad_dir or imported

        def check_extension(file: str):
            return file.endswith(".txt")

        notepad_names = []

        for root, _, files in paths:
            for file in files:
                if (
                    check_file(file)
                    and check_extension(file)
                    and file != "__password__.txt"
                ):
                    notepad_names.append(
                        file
                    )  #! file[:-4] to remove the .txt extension

        return notepad_names

    @staticmethod
    def save_imported_notepad(notepad_name: str, real_path: str):
        """
        Save the imported notepad file path to the notepads directory.
        Args:
            notepad_name (str): The name of the notepad file without extension.
            real_path (str): The full path to the real notepad file.
        """
        stored_app_path = Helper.get_notepad_path(notepad_name, imported=True)

        try:
            with open(stored_app_path, "w") as file:
                file.write(real_path)
        except Exception as e:
            Helper.show_error(f"Error saving imported notepad: {e}")

    @staticmethod
    def create_notepad(notepad_name: str) -> bool:
        if notepad_name == "":
            return Helper.show_error(
                "Invalid notepad name! Try actually entering in a name."
            )
        if Helper.file_exists(Helper.get_notepad_path(notepad_name)):
            return Helper.show_error(
                "A notepad by that name already exists! Try another."
            )

        path_to_app_directory = Helper.get_notepad_path(notepad_name)

        try:
            with open(path_to_app_directory, "w") as file:
                file.write("")
                return True
        except Exception as e:
            Helper.show_error(f"Error saving imported notepad: {e}")
            return False

    @staticmethod
    def delete_notepad(notepad_name: str):
        """
        Delete a notepad file from the notepads directory. (DOES NOT DELETE THE REAL FILE IF IMPORTED)
        Args:
            notepad_name (str): The name of the notepad file without extension.
            imported (bool): If True, delete from the imported notepads directory.
        Returns:
            True: If deleted correctly
            False: If an error occured
        """

        imported = Helper.is_imported(notepad_name)

        notepad_path = Helper.get_notepad_path(notepad_name, imported)

        if Helper.file_exists(notepad_path):
            try:
                os_remove_file(notepad_path)
                return True
            except Exception as e:
                Helper.show_error(f"Error deleting notepad file: {e}")
                return False

    @staticmethod
    def is_imported(notepad_name: str) -> bool:
        """
        Check if a notepad is imported or not.
        Args:
            notepad_name (str): The name of the notepad file without extension.
        Returns:
            bool: True if the notepad is imported, False otherwise.
        """
        imported_notepads_dir = Helper.get_notepads_directory(imported=True)
        file_paths = walk(imported_notepads_dir)

        for root, _, files in file_paths:
            for file in files:
                if file == notepad_name + ".txt":
                    return True
        return False
