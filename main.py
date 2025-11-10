import tkinter as tk
from gui.app import NoteApp

if __name__ == "__main__":
    root = tk.Tk()
    app = NoteApp(root)
    root.mainloop()