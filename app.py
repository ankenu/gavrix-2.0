import tkinter as tk
 
window = tk.Tk()
window.title("Gavrix")
 
window.rowconfigure(0, minsize=640, weight=1)
window.columnconfigure(1, minsize=800, weight=1)
 
txt_edit = tk.Text(window, undo=True, font='fixed', borderwidth=2, relief='groove')

txt_edit.grid(row=0, column=1, sticky="nsew")
 
window.mainloop()