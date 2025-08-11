import customtkinter as ctk  # type: ignore
from src import Helper, Master, Password

def main():  
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    window = ctk.CTk()

    Helper.set_icon(window)

    window.title("Notepad+ - by: @Takenkills")
    window.resizable(width=False, height=False)
    window.geometry("400x500")
    window.eval("tk::PlaceWindow %s center" % window.winfo_toplevel())
    window.bind("<Escape>", lambda _: window.quit())

    Password(window)
    window.withdraw()  # Hide the main window until password is verified
    window.after(300, lambda: Master(window))
    window.deiconify()  # Show the main window after password verification

    window.mainloop()


if __name__ == "__main__":
    main()

#! pyinstaller main.py --icon=(___.ico)