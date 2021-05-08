import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
#sudo apt install python3-pil.imagetk
from PIL import Image, ImageTk
import os

class File:
    def __init__(self, TypeTag, FilePath=""):
        self.widget = None
        self.tag = TypeTag
        self.path = FilePath
        self.name = 'NewFile.txt' if not FilePath else os.path.basename(FilePath)

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
    
    def linenumbers_change(self, event):
        """Redraws the line numbering"""
        # if self.is_linenumbers_on:
        self.redraw(14) #self.fsize
        
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

class Tabs(ttk.Notebook):
    def __init__(self, *args, **kwargs):
        ttk.Notebook.__init__(self, *args, **kwargs)
        self.tabs_collection = {} # { index, file }
    
    def add_new(self, file):
        tab_place = tk.Frame(self)
        if file.tag == "doc":
            txt_edit = CustomText(tab_place, font=("Helvetica", 14))  #self.fsize 14
            scrollbar = tk.Scrollbar(tab_place, orient="vertical", command=txt_edit.yview)
            txt_edit.configure(yscrollcommand=scrollbar.set)
            
            linenumbers = TextLineNumbers(tab_place, width=30)
            linenumbers.attach(txt_edit)

            tab_place.pack(fill="both", expand=True, side="left")
            linenumbers.pack(fill="y", side="left")
            txt_edit.pack(fill="both", expand=True, side="left")
            scrollbar.pack(fill="y", side="left")

            txt_edit.bind("<<Change>>", linenumbers.linenumbers_change)
            txt_edit.bind("<Configure>", linenumbers.linenumbers_change)

            file.widget = tab_place

        if file.path != "":
            txt_edit.delete("1.0", tk.END)
            with open(file.path, "r") as input_file:
                text = input_file.read()
                txt_edit.insert(tk.END, text)

        self.add(tab_place, text=file.name)

class Explorer(ttk.Treeview):
    def __init__(self, *args, **kwargs):
        ttk.Treeview.__init__(self, *args, **kwargs)
        self.folder_path = ""

    def runner(self, parent, path):
        tag = "file"
        for d in os.listdir(path):
            full_path=os.path.join(path,d)
            isdir = os.path.isdir(full_path)
            if isdir:
                tag = "folder"
            id = self.insert(parent, "end", text=d, open=False, tags=tag)
            if isdir:
                tag = "file"
                self.runner(id, full_path)

    def start(self, new_folder_path):
        if new_folder_path != "":
            main_folder_id = self.get_children()
            if main_folder_id:
                self.delete(*main_folder_id)
            self.folder_path = new_folder_path

            self.heading("#0", text="Dir：" + self.folder_path, anchor='w')
            path = os.path.abspath(self.folder_path)
            node = self.insert("", "end", text=self.folder_path, open=True)
            self.runner(node, path)
    
    def file_open(self):
        item_id = self.selection()[0]
        file_tag = self.item(item_id, "tags")[0]
        if file_tag == "file":
            item_name = self.item(item_id,"text")
            path = ""
            while True:
                parent_id = self.parent(item_id)
                node = self.item(parent_id)['text']
                if node == self.folder_path:
                    path = node + path + "/" + item_name
                    break
                path = "/" + node + path
                item_id = parent_id
            # # Open file
            # self.txt_edit.delete("1.0", tk.END)
            # with open(self.path_to_file, "r") as input_file:
            #     text = input_file.read()
            #     self.txt_edit.insert(tk.END, text)
            # self.master.title(f"Gavrix - {self.path_to_file}")
            return path

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
        self.path_to_file = 0
        self.path_to_folder = ""
        self.is_folder_explorer_on = False
        
        self.first_screen = ttk.PanedWindow(self, orient="horizontal")
        self.second_screen = ttk.PanedWindow(self.first_screen, orient="horizontal")
        self.first_place = tk.Frame(self.first_screen)
        self.second_place = tk.Frame(self.second_screen)

        self.tabpad = Tabs(self.second_place)

        self.file = File("doc")
        self.tabpad.add_new(self.file)

        self.explorer = Explorer(self.first_place, show="tree")
        self.scrollbar_explorer = tk.Scrollbar(self.first_place, orient="vertical", command=self.explorer.yview)
        self.explorer.configure(yscrollcommand=self.scrollbar_explorer.set)

        self.explorer.start("")

        self.gavrix = tk.Menu(self.mainmenu, tearoff=0)
        self.gavrix.add_command(label='Open File', command=self.file_open)
        self.gavrix.add_command(label='Open Folder', command=self.folder_open) 

        self.gavrix.add_separator()
        self.gavrix.add_command(label='Save', command=self.save)
        self.gavrix.add_command(label='Save as', command=self.save_as)
        self.gavrix.add_separator()
        self.gavrix.add_command(label='Close', command=self.file_close)
        
        self.view = tk.Menu(self.mainmenu, tearoff=0)
        
        self.scale = tk.Menu(self.mainmenu, tearoff=0)
        self.scale_sizes = dict([("25%", 4), ("50%", 8), ("75%", 12), ("100%", 16), ("125%", 20)])
        self.scale_sizes_percent = list(self.scale_sizes.keys())
        for percent in self.scale_sizes_percent:
            self.scale.add_command(label=percent, command=lambda n=self.scale_sizes[percent]: self.change_scale(n))
        
        self.view.add_command(label='Line numbers: On', command=self.switch)
        self.view.add_cascade(label='Scale: 75%', menu=self.scale)

        self.mainmenu.add_cascade(label='Gavrix', menu=self.gavrix)
        self.mainmenu.add_cascade(label='View', menu=self.view)
        
        self.positionWidgets()
        
        self.explorer.bind("<Double-1>", self.explorer_file_open)

    def positionWidgets(self):
        self.first_screen.pack(fill="both", expand=True, side="left")
        self.second_screen.pack(fill="both", expand=True, side="left")
        
        self.explorer.pack(fill="both", expand=True, side="left")
        self.scrollbar_explorer.pack(fill="y", side="left")
        self.tabpad.pack(fill="both", expand=True, side="left")

        self.first_screen.add(self.first_place)
        self.first_screen.add(self.second_screen)
        self.second_screen.add(self.second_place)
    
    def folder_open(self):
        folder_path = askdirectory()
        self.explorer.start(folder_path)

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
        if not self.path_to_file:
            self.save_as()
            return
        with open(self.path_to_file, "w") as output_file:
            text = self.txt_edit.get("1.0", tk.END)
            output_file.write(text)
        self.master.title(f"Gavrix - {self.path_to_file}")

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
        path_to_file = askopenfilename(
                filetypes=[("All files", "*.*"), ("Text files", "*.txt")]
        )
        if not path_to_file:
            return
        file = File("doc", path_to_file)
        self.tabpad.add_new(file)
        self.master.title(f"Gavrix - {path_to_file}")

    def explorer_file_open(self, event):
        path_to_file = self.explorer.file_open()
        if path_to_file:
            file = File("doc", path_to_file)
            self.tabpad.add_new(file)
            self.master.title(f"Gavrix - {path_to_file}")

    def file_close(self):
        """Closes the file that user has opened"""
        self.tabpad.forget(self.tabpad.select())
        self.master.title(f"Gavrix - NewFile.txt")
        self.path_to_file = 0

app = Application(title="Gavrix - NewFile.txt")
app.mainloop()