import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename

class CustomText(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)
           
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def _proxy(self, *args):
        """Lets the actual widget perform the requested action;
        Generates an event if something was added or deleted or the cursor position changed
        Returns what the actual widget returned
        """
        cmd = (self._orig,) + args
        result = self.tk.call(cmd)

        if (args[0] in ("insert", "replace", "delete") or 
            args[0:3] == ("mark", "set", "insert") or
            args[0:2] == ("xview", "moveto") or
            args[0:2] == ("xview", "scroll") or
            args[0:2] == ("yview", "moveto") or
            args[0:2] == ("yview", "scroll")
        ):
            self.event_generate("<<Change>>", when="tail")

        return result

class TextLineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget):
        self.textwidget = text_widget
        
    def redraw(self, *args):
        '''redraw line numbers'''
        self.delete("all")

        i = self.textwidget.index("@0,0")
        while True :
            dline= self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2,y,anchor="nw", text=linenum)
            i = self.textwidget.index("%s+1line" % i)

class Application(tk.Frame):
    def __init__(self, master=None, title="<application>", **kwargs):
        super().__init__(master, **kwargs)
        self.master.title(title)

        self.grid(sticky = "news")
        self.createWidgets()
    
    def createWidgets(self):
        self.txt_edit = CustomText(self)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.txt_edit.yview)
        self.txt_edit.configure(yscrollcommand=self.scrollbar.set)
        
        self.linenumbers = TextLineNumbers(self, width=30)
        self.linenumbers.attach(self.txt_edit)
        
        self.fr_buttons = tk.Frame(self)

        self.is_on = True
        self.scale_option_list = ["25%", "50%", "75%", "100%", "125%"]

        self.scale_option = tk.StringVar(self)
        self.scale_option.set(self.scale_option_list[2])
        self.scale = tk.OptionMenu(self.fr_buttons, self.scale_option, *self.scale_option_list)
        self.scale.config(width=1)
        self.scale_option.trace("w", self.change_scale)

        self.btn_open = tk.Button(self.fr_buttons, text="Open", command=self.file_open)
        self.btn_save = tk.Button(self.fr_buttons, text="Save")
        self.btn_save_as = tk.Button(self.fr_buttons, text="Save As", command=self.save_as)
        self.close = tk.Button(self.fr_buttons, text="Close", command=self.file_close)
        self.line_num = tk.Button(self.fr_buttons, text="Line numbers: On", command=self.switch)
        self.line_num.config(width=14)

        self.btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.btn_save.grid(row=1, column=0, sticky="ew", padx=5)
        self.btn_save_as.grid(row=1, column=1, sticky="ew", padx=5)
        self.close.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.scale.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        self.line_num.grid(row=3, column=0, sticky="ew", padx=5)
        self.fr_buttons.grid(row=0, column=0, sticky="ns")
        self.txt_edit.grid(row=0, column=2, sticky="nsew")
        self.scrollbar.grid(row=0, column=3, sticky='ns')
        self.linenumbers.grid(row=0, column=1, sticky="nsew")

        self.txt_edit.bind("<<Change>>", self.linenumbers_change)
        self.txt_edit.bind("<Configure>", self.linenumbers_change)
        
    def linenumbers_change(self, event):
        """Redraws the line numbering"""
        self.linenumbers.redraw()

    def change_scale(self, *args):
        """Changes the font size of the whole document, supports 5 different sizes"""
        if self.scale_option.get() == self.scale_option_list[0]:
            self.txt_edit.config(font=('Helvetica', 4))
        elif self.scale_option.get() == self.scale_option_list[1]:
            self.txt_edit.config(font=('Helvetica', 8))
        elif self.scale_option.get() == self.scale_option_list[2]:
            self.txt_edit.config(font=('Helvetica', 12))
        elif self.scale_option.get() == self.scale_option_list[3]:
            self.txt_edit.config(font=('Helvetica', 16))
        elif self.scale_option.get() == self.scale_option_list[4]:
            self.txt_edit.config(font=('Helvetica', 20))

        self.txt_edit.insert(tk.END, "")

    def switch(self):
        """Toggles the button state"""
        if self.is_on:
            self.line_num.config(text="Line numbers: Off")
            self.is_on = False
        else:
            self.line_num.config(text="Line numbers: On")
            self.is_on = True

    def save_as(self):
        """Saves the current file as new"""
        path_to_file = asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files","*.txt"),("All files", "*.*")]
        )
        if not path_to_file:
            return
        with open(path_to_file, "w") as output_file:
            text = self.txt_edit.get("1.0", tk.END)
            output_file.write(text)
        self.master.title(f"Gavrix - {path_to_file}")

    def file_open(self):
        """Opens the file that user wants to edit"""
        path_to_file = askopenfilename(
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path_to_file:
            return
        self.txt_edit.delete("1.0", tk.END)
        with open(path_to_file, "r") as input_file:
            text = input_file.read()
            self.txt_edit.insert(tk.END, text)
        self.master.title(f"Gavrix - {path_to_file}")

    def file_close(self):
        """Closes the file that user has opened"""
        self.txt_edit.delete("1.0", tk.END)
        self.master.title(f"Gavrix - NewFile.txt")

app = Application(title="Gavrix - NewFile.txt")
app.mainloop()