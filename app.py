import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename


path_to_file = "NewFile.txt"
text = ""


def change_scale(*args):
    if scale_option.get() == scale_option_list[0]:
        txt_edit.config(font=('Helvetica', 4))
    elif scale_option.get() == scale_option_list[1]:
        txt_edit.config(font=('Helvetica', 8))
    elif scale_option.get() == scale_option_list[2]:
        txt_edit.config(font=('Helvetica', 12))
    elif scale_option.get() == scale_option_list[3]:
        txt_edit.config(font=('Helvetica', 16))
    elif scale_option.get() == scale_option_list[4]:
        txt_edit.config(font=('Helvetica', 20))

    txt_edit.insert(tk.END, "")

def save_as():
    """Saves the current file as new"""
    path_to_file = asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files","*.txt"),("All files", "*.*")]
    )
    if not path_to_file:
        return
    with open(path_to_file, "w") as output_file:
        text = txt_edit.get("1.0", tk.END)
        output_file.write(text)
    window.title(f"Gavrix - {path_to_file}")

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

def file_close():
    path_to_file = "NewFile.txt"
    text = ""
    txt_edit.delete("1.0", tk.END)
    window.title(f"Gavrix - {path_to_file}")

window = tk.Tk()
window.title(f"Gavrix - {path_to_file}")
 
window.rowconfigure(0, minsize=640, weight=1)
window.columnconfigure(1, minsize=800, weight=1)

txt_edit = tk.Text(window, undo=True, font='fixed', borderwidth=2, relief='groove')
fr_buttons = tk.Frame(window)

scale_option_list = [
"25%",
"50%",
"75%",
"100%",
"125%"
]

scale_option=tk.StringVar(window)
scale_option.set(scale_option_list[2])

btn_open = tk.Button(fr_buttons, text="Open", command = file_open)
btn_save = tk.Button(fr_buttons, text="Save")
btn_save_as = tk.Button(fr_buttons, text="Save As", command = save_as)
close = tk.Button(fr_buttons, text="Close", command = file_close)

scale = tk.OptionMenu(fr_buttons, scale_option, *scale_option_list)
scale.config(width=1)

scale_option.trace("w", change_scale)

btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
btn_save.grid(row=1, column=0, sticky="ew", padx=5)
btn_save_as.grid(row=1, column=1, sticky="ew", padx=5)
close.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
scale.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
 
fr_buttons.grid(row=0, column=0, sticky="ns")
txt_edit.grid(row=0, column=1, sticky="nsew")
 
window.mainloop()
