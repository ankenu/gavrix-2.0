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
        
    def redraw(self, font_size, *args):
        """Redraw line numbers"""
        self.delete("all")

        i = self.textwidget.index("@0,0")
        while True :
            dline= self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2, y, anchor="nw", text=linenum, font=("TkDefaultFont", font_size-2))
            i = self.textwidget.index("%s+1line" % i)

class Application(tk.Frame):
    def __init__(self, master=None, title="<application>", **kwargs):
        super().__init__(master, **kwargs)
        self.fsize = 12
        self.master.title(title)
        self.mainmenu = tk.Menu(self.master)
        self.master.config(menu=self.mainmenu)

        self.pack(fill="both", expand=True)
        self.createWidgets()
    
    def createWidgets(self):
        self.txt_edit = CustomText(self, font=('Helvetica', self.fsize))
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.txt_edit.yview)
        self.txt_edit.configure(yscrollcommand=self.scrollbar.set)
        
        self.is_linenumbers_on = True
        
        self.linenumbers = TextLineNumbers(self, width=30)
        self.linenumbers.attach(self.txt_edit)

        self.gavrix = tk.Menu(self.mainmenu, tearoff=0)
        self.gavrix.add_command(label='Open', command=self.file_open)
        self.gavrix.add_command(label='Save', command=self.save)
        self.gavrix.add_command(label='Save as', command=self.save_as)
        self.gavrix.add_separator()
        self.gavrix.add_command(label='Close', command=self.file_close)
        
        self.view = tk.Menu(self.mainmenu, tearoff=0)
        
        self.scale = tk.Menu(self.mainmenu, tearoff=0)
        for num in range(4, 21, 4):
            self.scale.add_command(label=str(int(6.25*num))+"%", command=lambda n=num: self.change_scale(n))
        
        self.view.add_command(label='Line numbers: On', command=self.switch)
        self.view.add_cascade(label='Scale: 75%', menu=self.scale)

        self.mainmenu.add_cascade(label='Gavrix', menu=self.gavrix)
        self.mainmenu.add_cascade(label='View', menu=self.view)
        
        self.positionWidgets()

        self.txt_edit.bind("<<Change>>", self.linenumbers_change)
        self.txt_edit.bind("<Configure>", self.linenumbers_change)

    def positionWidgets(self):
        self.linenumbers.pack(fill="y", side="left")
        self.txt_edit.pack(fill="both", expand=True, side="left")
        self.scrollbar.pack(fill="y", side="left")
        
    def linenumbers_change(self, event):
        """Redraws the line numbering"""
        if self.is_linenumbers_on:
            self.linenumbers.redraw(self.fsize)

    def change_scale(self,s):
        """Changes the font size of the whole document, supports 5 different sizes"""
        self.fsize = s
        self.txt_edit.config(font=('Helvetica', s))
        self.txt_edit.insert(tk.END, "")
        self.view.entryconfigure(1, label = "Scale: "+str(int(6.25*s))+"%")

    def switch(self):
        """Toggles the button state"""
        if self.is_linenumbers_on:
            self.view.entryconfigure(0, label ="Line numbers: Off")
            self.is_linenumbers_on = False
            self.linenumbers.pack_forget()
        else:
            self.view.entryconfigure(0, label ="Line numbers: On")
            self.is_linenumbers_on = True
            
            self.txt_edit.pack_forget()
            self.scrollbar.pack_forget()

            self.positionWidgets()

    def save(self):
        """Saves the opened file, if no file is opened - acts like save_as()"""
        try:
            if not path_to_file:
                return
        except NameError:
            self.save_as()
            return
        with open(path_to_file, "w") as output_file:
            text = self.txt_edit.get("1.0", tk.END)
            output_file.write(text)
        self.master.title(f"Gavrix - {path_to_file}")

    def save_as(self):
        """Saves the current file as new"""
        path_to_an_file = asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files","*.txt"),("All files", "*.*")]
        )
        if not path_to_an_file:
            return
        with open(path_to_an_file, "w") as output_an_file:
            text = self.txt_edit.get("1.0", tk.END)
            output_file.write(text)
        self.master.title(f"Gavrix - {path_to_an_file}")

    def file_open(self):
        """Opens the file that user wants to edit"""
        global path_to_file
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