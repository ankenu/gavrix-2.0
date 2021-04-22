import tkinter as tk
from tkinter.filedialog import askopenfilename


def file_open():
    """Opens the file that user wants to edit"""
    path_to_file = askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if not path_to_file:
        return
    txt_edit.delete("1.0", tk.END)
    with open(path_to_file, "r") as input_file:
        text = input_file.read()
        txt_edit.insert(tk.END, text)
    window.title(f"Gavrix - {path_to_file}")
 
window = tk.Tk()
window.title("Gavrix")
 
window.rowconfigure(0, minsize=640, weight=1)
window.columnconfigure(1, minsize=800, weight=1)
 
txt_edit = tk.Text(window, undo=True, font='fixed', borderwidth=2, relief='groove')
fr_buttons = tk.Frame(window)

btn_open = tk.Button(fr_buttons, text="Open", command = file_open)
btn_save = tk.Button(fr_buttons, text="Save")
btn_save_as = tk.Button(fr_buttons, text="Save As")
close = tk.Button(fr_buttons, text="Close")

btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
btn_save.grid(row=1, column=0, sticky="ew", padx=5)
btn_save_as.grid(row=1, column=1, sticky="ew", padx=5)
close.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
 
fr_buttons.grid(row=0, column=0, sticky="ns")
txt_edit.grid(row=0, column=1, sticky="nsew")
 
window.mainloop()
