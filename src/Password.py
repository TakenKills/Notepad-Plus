from .Helper import Helper
from .Widgets import Widgets
from os.path import join, getsize
from tkinter import StringVar
from sys import exit as exit_system

def encrypt(password: str) -> str:
    import hashlib
    import base64
    sha256_hash = hashlib.sha256(password.encode()).digest()
    base64_encoded = base64.b64encode(sha256_hash).decode()
    return base64_encoded


class Password:
    """
    Handles password setup and retrieval for Notepad+.
    Shows dialogs for entering or setting a password, and stores the password securely.
    """
    def __init__(self, window):
        """
        Initialize the Password dialog and retrieve or set the password.
        """
        self.root = window
        self.top = Helper.setup_top(self.root, "Enter Password", geometry="400x100")
        self.top.bind("<Escape>", lambda _e=None: self.root.quit())
        self.root.eval("tk::PlaceWindow %s center" % self.top.winfo_toplevel())
        
        self.get_pass() # Invoking it to make sure there is a password set before showing the dialog.

        self.text = Widgets.create_label(
            self.top, text="Please enter your password to access Notepad+"
        )
        self.text.pack(pady=10)

        self.entry = Widgets.create_entry(self.top, placeholder_text="Password", show="*")
        self.entry.pack(pady=10, padx=10, fill="x")
        self.entry.bind("<Return>", self.password_check)

        self.top.update()
        self.entry.focus_set()

        self.confirm_button = Widgets.create_button(self.top, text="Confirm", command=self.password_check)
        self.confirm_button.pack(pady=10)


        self.tries = 0  # Track the number of attempts

    def password_check(self, _event = None):
        """
        Validate the entered password against the stored password.
        If the password is correct, close the dialog; otherwise, show an error.
        """
        entered_password = self.entry.get()
        
        if entered_password is None or entered_password == "":
            return #? Should I show an error if the password is empty??
        
        stored_password = self.get_pass()

        if encrypt(entered_password) == stored_password:
            self.top.destroy() # destroy the password dialog
            self.root.deiconify()  # Show the main window again

        else:
            self.entry.delete(0, 'end')  # Clear the entry
            self.entry.focus()  # Focus back on the entry #? Is this necessary??

            error = Helper.show_error("Incorrect password. Please try again.", self.top) #? Should the parent be the top or the root window?
            error.after(750, error.destroy)

            self.entry.focus() #? Is this redundunt?

            self.tries += 1

            if self.tries >= 3:
                error = Helper.show_error("Too many incorrect attempts. Exiting application.", self.top, min_width=600, height=100)
                self.top.after(1000, lambda: self.destroy_windows())


    def destroy_windows(self):
        self.root.quit()
        exit_system(0)

    def get_pass(self):
        """
        Retrieve the stored password, or prompt the user to set one if not found.
        Returns:
            str: The password string.
        """
        directory = Helper.get_notepads_directory()
        password_file = join(directory, "__password__.txt")

        try:
            if Helper.file_exists(password_file):
                with open(password_file, "r") as pass_file:
                    if getsize(password_file) == 0:
                        # File exists but is empty, prompt to set password
                        return self.enter_pass()
                    else:
                        # Return the stored password (stripped of whitespace)
                        return pass_file.read().strip()
            else:
                # File does not exist, prompt to set password
                return self.enter_pass()
        except Exception as e:
            Helper.show_error(f"Error reading password file: {e}")
            return ""

    def enter_pass(self):
        """
        Show a dialog for the user to set a new password.
        Returns:
            str: The password entered by the user.
        """
        self.top.withdraw()  # Hide the main password window while setting a new password

        top = Helper.setup_top(self.root, "Set Password", geometry="540x140")
        self.root.eval("tk::PlaceWindow %s center" % top.winfo_toplevel())

        # Prompt label
        prompt = "You seem new! Type here the password you want to use for your notepads:"
        top_label = Widgets.create_label(top, text=prompt)
        top_label.pack(pady=10)
 
        # Entry for password
        password_var = StringVar()
        top_entry = Widgets.create_entry(top, placeholder_text="Password", show="*", textvariable=password_var)
        top_entry.pack(pady=5, padx=10, fill="x")
        top.after(100, top_entry.focus) # Delaying to ensure it's ready.

        def button_callback():
            # Validate input
            pw = password_var.get()
            if not pw:
                Helper.show_error("Password cannot be empty.")
                return
            try:
                self.set_pass(pw)

                Helper.show_error("Password set successfully!", top)

                self.top.deiconify()  # Show the main password window again
                top.after(1000, lambda: top.destroy())
            except Exception as e:
                Helper.show_error(f"Error saving password: {e}")

        #TODO UI/UX:

        #TODO You might want to clear the entry after setting the password, or provide feedback to the user (e.g., a messagebox saying “Password set!”).
        #TODO Consider disabling the main window while the password dialog is open to prevent user interaction with the main app before setting a password.

        Widgets.create_button(
                        top,
                        text="Confirm",
                        command=button_callback).pack(pady=10)
        
        top_entry.bind("<Return>", lambda _: button_callback())
        top_entry.focus_set()

        return password_var.get()

    @staticmethod
    def set_pass(password: str):
        """
        Save the given password to the password file (hashed and encoded).
        Args:
            password (str): The password to store.
        """
        directory = Helper.get_notepads_directory()
        password_file = join(directory, "__password__.txt")
        try:
            with open(password_file, "w") as pass_file:
                pass_file.write(encrypt(password))
        except Exception as e:
            Helper.show_error(f"Error writing password file: {e}")
       