import tkinter as tk
from tkinter import Scrollbar, Widget, ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
import tkinter.font as tkfont
#sudo apt install python3-pil.imagetk
from PIL import Image, ImageTk
#pip install python-magic
import pickle5 as pickle
#pip install pickle5
import magic
import os
import json
import sys

class JsonTheme():
    def __init__(self):
        self.file_path = "themes/theme.json"
        self.data = {}
        self.data["themes"] = {}
        self.data["themes"]["Light"] = {
                    "text_color": "Black",
                    "line_num_color": "Dark Grey",
                    "line_num_text_color": "#bbb5eb",
                    "background_color": "White"
                }
        self.data["themes"]["Dark"] = {
                    "text_color": "Light Grey",
                    "line_num_color": "Light Grey",
                    "line_num_text_color": "#bbb5eb",
                    "background_color": "Dark Grey"
                    }
        self.data["current"] = "Light"
        
    def check(self):
        """Checks whether the theme.json file exists and if it doesn't creates it"""   
        try:
            open(self.file_path, "r")
        except IOError:
            json.dump(self.data, open(self.file_path, "w+"), indent=4)

    def read(self):
        """Reads the json file to specify the text, background and line numbers colors"""   
        self.file = open(self.file_path, "r")
        self.file_data = json.loads(self.file.read())
    
        self.theme_id = self.file_data["current"]
        self.text_color = self.file_data["themes"][self.theme_id]["text_color"]
        self.bg_color = self.file_data["themes"][self.theme_id]["background_color"]
        self.line_num_color = self.file_data["themes"][self.theme_id]["line_num_color"]
        self.line_num_text_color = self.file_data["themes"][self.theme_id]["line_num_text_color"]

json_file = JsonTheme()
json_file.check()
json_file.read()

class File:
    def __init__(self, TypeTag, FilePath=""):
        self.widget = None
        self.tag = TypeTag
        self.path = FilePath
        self.edit = False
        self.name = 'NewFile.txt' if not FilePath else os.path.basename(FilePath)

    def change_values(self, FileWidget, TypeTag, FilePath, FileName, EditStatus):
        # self.tab_widget = None
        self.widget = FileWidget
        self.tag = TypeTag
        self.path = FilePath
        self.name = FileName
        self.edit = EditStatus

class Interface:
    def __init__(self):
        self.folder_path = ""
        self.tabulation = 4
        self.font_size = 12
        self.files_list = []
    
interface = Interface()

class CustomText(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)

        font = tkfont.Font(font=self['font'])
        tab = font.measure(" " * interface.tabulation)
        self.config(tabs=tab)
           
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
        tk.Canvas.__init__(
            self, 
            *args, 
            **kwargs, 
            bg = json_file.line_num_color, 
            highlightbackground = json_file.line_num_color)
        self.textwidget = None
        # self.is_on = True

    def resize(self, event):
        self.config(width=(interface.font_size * 5))

    def attach(self, text_widget):
        self.textwidget = text_widget
    
    def linenumbers_change(self, event):
        """Redraws the line numbering"""
        self.redraw() #self.fsize
        
    def redraw(self, *args):
        """Redraw line numbers"""
        self.delete("all")

        i = self.textwidget.index("@0,0")
        while True :
            dline= self.textwidget.dlineinfo(i)
            if dline is None: break
            linenum = str(i).split(".")[0]

            x = 4*interface.font_size-interface.font_size*len(linenum)
            y = dline[1]

            self.create_text(
                x, 
                y, 
                anchor="nw", 
                text=linenum, 
                font=("TkDefaultFont", interface.font_size-2), fill = json_file.line_num_text_color)
            i = self.textwidget.index("%s+1line" % i)

class Tabs(ttk.Notebook):
    def __init__(self, *args, **kwargs):
        ttk.Notebook.__init__(self, *args, **kwargs)
        ttk.Style().configure(
            "TNotebook", 
            background = json_file.bg_color, 
            foreground = json_file.text_color,
            darkcolor = json_file.bg_color,
            lightcolor = json_file.text_color, 
            fieldbackground = json_file.bg_color,
            highlightbackground = json_file.bg_color,
            bordercolor = json_file.bg_color,
            fill=json_file.bg_color)
        tab_style = ttk.Style()
        tab_style.configure(
            "TNotebook.Tab",
            background = json_file.bg_color, 
            foreground = json_file.text_color,
            darkcolor = json_file.bg_color,
            lightcolor = json_file.text_color, 
            fieldbackground = json_file.bg_color,
            highlightbackground = json_file.bg_color,
            bordercolor = json_file.bg_color,
            fill=json_file.bg_color)

        self.tabs_collection = {} # { index, file }
        self.path_list = []
    
    def add_new(self, file):
        """Adds new tab with frame"""
        if (not file.path in self.path_list) or file.path == "":
            if file.path != "":
                self.path_list.append(file.path)
            frame_style = ttk.Style()
            frame_style.configure("TFrame", bg = json_file.bg_color, fg = json_file.text_color,)
            tab_place = ttk.Frame(self, style="TFrame")
            tab_place.pack(fill="both", expand=True, side="left")
            if file.tag[0] == "t":
                if (file.widget):
                    text = file.widget
                else:
                    text = ""
                file.widget = self.txt_edit = CustomText(
                    tab_place, 
                    undo=True,
                    font=("Helvetica", interface.font_size),
                    fg = json_file.text_color, 
                    highlightthickness=0, 
                    borderwidth=0, 
                    background=json_file.bg_color)  #self.fsize 14
                
                # self.scrollview = CustomText(
                #     tab_place, 
                #     width=60, 
                #     font=("Helvetica", 2), 
                #     fg = json_file.text_color,
                #     borderwidth=0,
                #     highlightbackground=json_file.line_num_color,
                #     background=json_file.bg_color)

                scrollbar_style = ttk.Style()
                scrollbar_style.configure("Vertical.TScrollbar", background = json_file.bg_color)
                
                self.scrollbar = ttk.Scrollbar(tab_place, orient="vertical", command=self.txt_edit.yview)
                self.txt_edit['yscrollcommand'] = self.scrollbar.set
                # txt_edit.configure(yscrollcommand=scrollbar.set)
                
                # self.scrollbar['command'] = self.on_scrollbar
                # self.txt_edit['yscrollcommand'] = self.on_textscroll_txt_edit
                # self.scrollview['yscrollcommand'] = self.on_textscroll_scrollview

                self.linenumbers = TextLineNumbers(tab_place, width=(interface.font_size * 5))
                self.linenumbers.attach(self.txt_edit)

                # scrollview.attach(txt_edit)

                self.linenumbers.pack(fill="y", side="left")
                self.scrollbar.pack(fill="y", side="right", padx=self.txt_edit.winfo_width())
                self.txt_edit.pack(fill="both", expand=True, side="left")
                # self.scrollview.pack(fill="y", side="left")

                self.txt_edit.bind("<KeyPress>", self.file_edit)
                self.txt_edit.bind("<<Change>>", self.linenumbers.linenumbers_change)
                self.txt_edit.bind("<Configure>", self.linenumbers.linenumbers_change)
                self.txt_edit.bind("<FocusIn>", self.linenumbers.resize)
                # self.txt_edit.bind("<<Modified>>", self.update)

                if file.path != "":
                    self.txt_edit.delete("1.0", tk.END)
                    with open(file.path, "r") as input_file:
                        if (text == ""):
                            text = input_file.read()
                        self.txt_edit.insert(tk.END, text)
                    # self.scrollview.delete("1.0", tk.END)
                    # self.scrollview.config(state='disabled')
                if file.path == "" and text != "":
                    self.txt_edit.insert(tk.END, text)
                    # self.scrollview.insert(tk.END, text)
                    # self.scrollview.config(state='disabled')

            if file.tag[0] == "i":
                file.widget = None
                load = Image.open(file.path)
                render = ImageTk.PhotoImage(load)
                img_label = tk.Label(tab_place, image=render)
                img_label.image = render
                img_label.place(x=0, y=0)
                img_label.pack(fill="both", expand=True, side="left")

            # file.tab_widget = tab_place #+-
            file_name = file.name
            if (file.edit):
                file_name = file_name + "*"
            self.add(tab_place, text=file_name)
            self.tabs_collection[tab_place] = file

    # def on_scrollbar(self, *args):
    #     """Scrolls both text widgets when the scrollbar is moved"""
    #     self.txt_edit.yview(*args)
    #     self.scrollview.yview(*args)

    # def on_textscroll_scrollview(self, *args):
    #     """Moves the scrollbar and scrolls text widgets when the mousewheel
    #     is moved on a text widget"""
    #     # self.on_scrollbar('moveto', args[0])
    
    # def on_textscroll_txt_edit(self, *args):
    #     """Moves the scrollbar and scrolls text widgets when the mousewheel
    #     is moved on a text widget"""
    #     self.scrollbar.set(*args)
    #     self.on_scrollbar('moveto', args[0])
    
    # def update(self, event):
    #     #print(self.scrollbar.get())
    #     # self.txt_edit.edit_modified(False)
    #     input = self.txt_edit.get("1.0",'end-1c')
    #     self.scrollview.config(state='normal')
    #     self.scrollview.delete("1.0", tk.END)
    #     self.scrollview.insert(tk.END, input)
    #     self.scrollview.config(state='disabled')
    
    def file_edit(self, event):
        key = self._nametowidget(self.select())
        file = self.tabs_collection[key]
        if file.edit != True:
            file.edit = True
            self.tab(key, text = (file.name + "*"))
        

class Explorer(ttk.Treeview):
    def __init__(self, *args, **kwargs):
        ttk.Treeview.__init__(self, *args, **kwargs)
        ttk.Style().configure(
            "Treeview", 
            background = json_file.bg_color, 
            foreground = json_file.text_color, 
            fieldbackground = json_file.bg_color,
            highlightbackground = json_file.bg_color,
            bordercolor = json_file.bg_color,
            fill=json_file.bg_color)
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

    def start(self):
        new_folder_path = interface.folder_path
        if new_folder_path != "":
            main_folder_id = self.get_children()
            if main_folder_id:
                self.delete(*main_folder_id)
            self.folder_path = new_folder_path

            self.heading("#0", text="Dir：" + self.folder_path, anchor='w')
            path = os.path.abspath(self.folder_path)
            node = self.insert("", "end", text=self.folder_path, open=True, tags="folder")
            self.runner(node, path)
        else:
            for i in self.get_children():
                self.delete(i)
    
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

class Application(ttk.Frame):
    def __init__(self, master=None, title="<application>", **kwargs):
        super().__init__(master, **kwargs)
        self.master.title(title)
        
        self.master.call('wm', 'iconphoto', self.master._w, tk.PhotoImage(file='img/icon.png'))

        style = ttk.Style(self.master)
        self.master.tk.call('source', 'styles/gavrix/gavrix.tcl')
        style.theme_use('gavrix')

        self.mainmenu = tk.Menu(
            self.master, 
            bg = json_file.bg_color, 
            fg = json_file.text_color,
            activebackground = json_file.bg_color,
            activeforeground = json_file.text_color,
            borderwidth="0")
        self.master.config(menu=self.mainmenu)

        self.pack(fill="both", expand=True)
        self.createWidgets()
    
    def createWidgets(self):
        self.path_to_file = 0

        self.first_screen = tk.PanedWindow(self, orient="horizontal", bg=json_file.bg_color)
        self.second_screen = tk.PanedWindow(self.first_screen, orient="horizontal", bg=json_file.bg_color)
        self.first_place = tk.Frame(self.first_screen, bg=json_file.bg_color)
        frame_style = ttk.Style()
        frame_style.configure("TFrame", 
            bg = json_file.bg_color, 
            fg = json_file.text_color,
            activebackground = json_file.bg_color,
            activeforeground = json_file.text_color)
        self.second_place = ttk.Frame(self.second_screen, style="TFrame")

        self.tabpad = Tabs(self.second_place)

        if (os.path.exists("settings.bin")):
            with open("settings.bin", "rb") as bin_file:
                intrfc = pickle.load(bin_file)
                interface.folder_path = intrfc.folder_path
                interface.font_size = intrfc.font_size
                interface.tabulation = intrfc.tabulation
      
            if intrfc.files_list:
                for file in intrfc.files_list:
                    self.file = File("t")
                    self.file.change_values(file.widget, file.tag, file.path, file.name, file.edit)
                    self.tabpad.add_new(self.file)
        else:
            self.new_file()

        self.explorer = Explorer(self.first_place, show="tree")
        self.scrollbar_explorer = ttk.Scrollbar(self.first_place, orient="vertical", command=self.explorer.yview)
        self.explorer.configure(yscrollcommand=self.scrollbar_explorer.set)

        self.explorer.start()

        self.gavrix = tk.Menu(
            self.mainmenu, 
            tearoff=0,
            bg = json_file.bg_color, 
            fg = json_file.text_color,
            activebackground = json_file.bg_color,
            activeforeground = json_file.text_color)
        self.gavrix.add_command(label="New File", command=self.new_file)
        self.gavrix.add_separator()
        self.gavrix.add_command(label="Open File", command=self.file_open)
        self.gavrix.add_command(label="Save", command=self.save)
        self.gavrix.add_command(label="Save as", command=self.save_as)
        self.gavrix.add_command(label="Close File", command=self.file_close)
        self.gavrix.add_separator()
        self.gavrix.add_command(label="Open Folder", command=self.folder_open) 
        # self.gavrix.add_separator()
        self.gavrix.add_command(label="Refresh", command=self.explorer.start)
        self.gavrix.add_command(label="Close Folder", command=self.folder_close)

        self.editmenu = tk.Menu(
            self.mainmenu, 
            tearoff=0,
            bg = json_file.bg_color, 
            fg = json_file.text_color,
            activebackground = json_file.bg_color,
            activeforeground = json_file.text_color)
        self.editmenu.add_command(label="Undo", command=self.undo)
        self.editmenu.add_command(label="Redo", command=self.redo)
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Cut", command=self.cut)
        self.editmenu.add_command(label="Copy", command=self.copy)
        self.editmenu.add_command(label="Paste", command=self.paste)
        self.editmenu.add_command(label="Delete", command=self.delete)
        self.editmenu.add_command(label="Select All", command=self.select_all)
        
        self.view = tk.Menu(
            self.mainmenu, 
            tearoff=0,
            bg = json_file.bg_color, 
            fg = json_file.text_color,
            activebackground = json_file.bg_color,
            activeforeground = json_file.text_color)
        
        self.scale = tk.Menu(
            self.mainmenu, 
            tearoff=0,
            bg = json_file.bg_color, 
            fg = json_file.text_color,
            activebackground = json_file.bg_color,
            activeforeground = json_file.text_color)
        self.scale_sizes = dict([("25%", 4), ("50%", 8), ("75%", 12), ("100%", 16), ("125%", 20)])
        self.scale_sizes_percent = list(self.scale_sizes.keys())
        for percent in self.scale_sizes_percent:
            self.scale.add_command(label=percent, command=lambda n=self.scale_sizes[percent]: self.change_scale(n))
        
        self.themes = tk.Menu(
            self.mainmenu, 
            tearoff=0,
            bg = json_file.bg_color, 
            fg = json_file.text_color,
            activebackground = json_file.bg_color,
            activeforeground = json_file.text_color)
        self.themes.add_command(label="Light", command=self.light_theme)
        self.themes.add_command(label="Dark", command=self.dark_theme)
        
        # self.view.add_command(label="Line numbers: On", command=self.switch)
        self.view.add_cascade(label="Scale: 75%", menu=self.scale)
        #Баг, два одинаковых пункта
        self.view.add_cascade(label="Theme", menu=self.themes)

        self.mainmenu.add_cascade(label="Gavrix", menu=self.gavrix)
        self.mainmenu.add_cascade(label="Edit", menu=self.editmenu)
        self.mainmenu.add_command(label="Find", command=self.find)
        self.mainmenu.add_cascade(label="View", menu=self.view)
        self.mainmenu.add_command(label="About", command=self.about)
        
        self.positionWidgets()
        
        self.explorer.bind("<Double-1>", self.explorer_file_open)
        self.master.protocol("WM_DELETE_WINDOW", self.gavrix_exit)

    def copy(self):
        # Clears the clipboard, copies selected contents.
        try: 
            key = self.tabpad._nametowidget(self.tabpad.select())
            file = self.tabpad.tabs_collection[key]
            sel = file.widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.master.clipboard_clear()
            self.master.clipboard_append(sel)
        # If no text is selected.
        except tk.TclError:
            pass
            
    def delete(self):
        # Delete the selected text.
        try:
            key = self.tabpad._nametowidget(self.tabpad.select())
            file = self.tabpad.tabs_collection[key]
            file.widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
        # If no text is selected.
        except tk.TclError:
            pass
            
    def cut(self):
        # Copies selection to the clipboard, then deletes selection.
        try: 
            key = self.tabpad._nametowidget(self.tabpad.select())
            file = self.tabpad.tabs_collection[key]
            sel = file.widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.master.clipboard_clear()
            self.master.clipboard_append(sel)
            file.widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
        # If no text is selected.
        except tk.TclError:
            pass
            
    def paste(self):
        try: 
            key = self.tabpad._nametowidget(self.tabpad.select())
            file = self.tabpad.tabs_collection[key]
            file.widget.insert(tk.INSERT, self.master.clipboard_get())
        except tk.TclError:
            pass
            
    def select_all(self, *args):
        key = self.tabpad._nametowidget(self.tabpad.select())
        file = self.tabpad.tabs_collection[key]
        
        # Selects / highlights all the text.
        file.widget.tag_add(tk.SEL, "1.0", tk.END)
        
        # Set mark position to the end and scroll to the end of selection.
        file.widget.mark_set(tk.INSERT, tk.END)
        file.widget.see(tk.INSERT)

    def undo(self):
        key = self.tabpad._nametowidget(self.tabpad.select())
        file = self.tabpad.tabs_collection[key]
        file.widget.edit_undo()

    def redo(self):
        key = self.tabpad._nametowidget(self.tabpad.select())
        file = self.tabpad.tabs_collection[key]
        file.widget.edit_redo()

    def new_file(self):
        self.file = File("t")
        self.tabpad.add_new(self.file)
    
    def folder_close(self):
        interface.folder_path = ""
        self.explorer.start()
    
    def about(self):
        dialogue = tk.Toplevel(bg = json_file.bg_color, 
            highlightbackground = json_file.text_color)
        dialogue.geometry("350x350")
        dialogue.title("About")

        frame = tk.Frame(
            dialogue, 
            highlightbackground = json_file.bg_color, 
            bg = json_file.bg_color)
        frame.pack(fill="both", expand=True)
        label1 = ttk.Label(
            frame, 
            text ="Gavrix 2.0", 
            background = json_file.bg_color, 
            foreground = json_file.text_color)
        label1.place(x=350/2, y=350/2, anchor="center")
        label2 = ttk.Label(
            frame, 
            text ="Developed by", 
            background = json_file.bg_color, 
            foreground = json_file.text_color)
        label2.place(x=350/2, y=350/2, anchor="center")
        label3 = ttk.Label(
            frame, 
            text ="Ilya Doroshenko [github: fickmann]", 
            background = json_file.bg_color, 
            foreground = json_file.text_color)
        label3.place(x=350/2, y=350/2, anchor="center")
        label4 = ttk.Label(
            frame, 
            text ="&", 
            background = json_file.bg_color, 
            foreground = json_file.text_color)
        label4.place(x=350/2, y=350/2, anchor="center")
        label5 = ttk.Label(
            frame, 
            text ="Roman Karpenkov [github: warnachinka]", 
            background = json_file.bg_color, 
            foreground = json_file.text_color)
        label5.place(x=350/2, y=350/2, anchor="center")
        label5.pack(side="bottom")
        label4.pack(side="bottom")
        label3.pack(side="bottom")
        label2.pack(side="bottom")
        label1.pack(side="bottom")

        load = Image.open("img/gavrixlogoX350.png")
        render = ImageTk.PhotoImage(load)
        img_label = tk.Label(frame, image=render)
        img_label.image = render
        img_label.place(x=0, y=0)
        img_label.pack(fill="both", expand=True, side="left")

        dialogue.resizable(1,1)
        dialogue.mainloop()

    def find(self, event = None):
        """Find dialogue window handler, includes the window itself and all of its widgets"""
        self.find_dialogue = tk.Toplevel(bg = json_file.bg_color, 
            highlightbackground = json_file.text_color)
        self.find_dialogue.geometry("375x150")
        self.find_dialogue.title("Find")
        self.find_dialogue.resizable(1,0)

        self.find_frame = tk.Frame(
            self.find_dialogue, 
            highlightbackground = json_file.bg_color, 
            bg = json_file.bg_color)
        self.find_frame.pack(pady=5, fill="both", expand=True)

        self.replace_frame = tk.Frame(
            self.find_dialogue, 
            bg = json_file.bg_color, 
            highlightbackground = json_file.bg_color)
        self.replace_frame.pack(pady=5, fill="both", expand=True)

        self.button_frame = tk.Frame(
            self.find_dialogue, 
            highlightbackground = json_file.bg_color, 
            bg = json_file.bg_color)
        self.button_frame.pack(pady=5, padx=15, fill="both")

        self.text_find_label = ttk.Label(
            self.find_frame, 
            text ="Find: ", 
            width=8, 
            background = json_file.bg_color, 
            foreground = json_file.text_color)
        self.text_replace_label = ttk.Label(
            self.replace_frame, 
            text= "Replace: ", 
            width=8, 
            background = json_file.bg_color, 
            foreground = json_file.text_color)

        self.find_input = tk.Entry(
            self.find_frame, 
            width = 30, 
            foreground=json_file.text_color,
            background=json_file.bg_color)
        self.replace_input = tk.Entry(
            self.replace_frame, 
            width = 30, 
            foreground=json_file.text_color,
            background=json_file.bg_color)

        self.find_button = tk.Button(
            self.button_frame, 
            text ="Find", 
            command= self.find_text, 
            background = json_file.bg_color, 
            foreground = json_file.text_color)
        self.replace_button= tk.Button(
            self.button_frame, 
            text= "Replace", 
            command= self.replace, 
            background = json_file.bg_color, 
            foreground = json_file.text_color)

        self.text_find_label.pack(side="left")
        self.text_replace_label.pack(side="left")

        self.find_input.pack(side="left", fill="x", expand=True)
        self.replace_input.pack(side="left", fill="x", expand=True)

        self.find_button.pack(side="left")
        self.replace_button.pack(side="left", padx=5)
        self.find_dialogue.protocol("WM_DELETE_WINDOW", self.updateText)
        self.find_dialogue.mainloop()

    def updateText(self):
        """Restores the text color upon closing the dialogue window"""
        self.tabpad.txt_edit.tag_config("match", background=json_file.bg_color, foreground=json_file.text_color)
        self.find_dialogue.destroy()

    def find_text(self):
        """Finds the specified text in the text field and marks it"""
        word = self.find_input.get()
        self.tabpad.txt_edit.tag_remove("match", "1.0", tk.END)
        matches = 0
        if word:
            start_pos = "1.0"
            while True:
                start_pos = self.tabpad.txt_edit.search(word, start_pos, stopindex=tk.END)
                if not start_pos:
                    break
                end_pos =f"{start_pos}+ {len(word)}c"
                self.tabpad.txt_edit.tag_add("match", start_pos, end_pos)
                matches +=1
                start_pos = end_pos
                self.tabpad.txt_edit.tag_config("match", foreground ="yellow", background= "green")
    
    def replace(self):
        """Replaces all found entities with the same specified text"""
        word = self.find_input.get()
        replace_text = self.replace_input.get()
        content= self.tabpad.txt_edit.get(1.0, tk.END)

        new_content = content.replace(word, replace_text)
        self.tabpad.txt_edit.delete(1.0, tk.END)
        self.tabpad.txt_edit.insert(1.0, new_content)
        
    def light_theme(self):
        """Changes the current theme to light in the json file and restarts the program to apply changes"""
        json_file.file_data["current"] = "Light"
        json.dump(json_file.file_data, open(json_file.file_path, "w+"), indent=4)
        if messagebox.askokcancel("Restart required", "Do you want to restart now?"):
            tabs_collection = self.tabpad.tabs_collection
            for key, file in tabs_collection.items():
                if (file.widget):
                    file.widget = file.widget.get("1.0", 'end-1c')
            interface.files_list = list(tabs_collection.values())
            bin_file = open("settings.bin", "wb")
            pickle.dump(interface, bin_file)
            bin_file.close()
            python = sys.executable
            os.execl(python, python, * sys.argv)

    def dark_theme(self):
        """Changes the current theme to dark in the json file and restarts the program to apply changes"""
        json_file.file_data["current"] = "Dark"
        json.dump(json_file.file_data, open(json_file.file_path, "w+"), indent=4)
        if messagebox.askokcancel("Restart required", "Do you want to restart now?"):
            self.make_settings_bin()
            python = sys.executable
            os.execl(python, python, * sys.argv)

    def positionWidgets(self):
        self.first_screen.pack(fill="both", expand=True, side="left")
        self.second_screen.pack(fill="both", expand=True, side="left")
        
        self.scrollbar_explorer.pack(fill="y", side="right")
        self.explorer.pack(fill="both", expand=True, side="left")
        self.tabpad.pack(fill="both", expand=True, side="left")

        self.first_screen.add(self.first_place)
        self.first_screen.add(self.second_screen)
        self.second_screen.add(self.second_place)

    def explorer_file_open(self, event):
        if interface.folder_path:
            path_to_file = self.explorer.file_open()
            if path_to_file:
                tag = magic.from_file(path_to_file, mime=True)
                file = File(tag, path_to_file)
                self.tabpad.add_new(file)
        else:
            self.folder_open()
    
    def folder_open(self, event=None):
        folder_path = askdirectory()
        if not folder_path:
            return
        interface.folder_path = folder_path
        self.explorer.start()

    def change_scale(self,s):
        """Changes the font size of the whole document, supports 5 different sizes"""
        # file = interface.tabs_collection[self.tabpad._nametowidget(self.tabpad.select())]
        for key, file in self.tabpad.tabs_collection.items():
            if file.widget:
                file.widget.config(font=("Helvetica", s))
                file.widget.focus_set()
            
        # self.tabpad.linenumbers.redraw()
        interface.font_size = s
        self.view.entryconfigure(1, label = "Scale: "+str(int(6.25*s))+"%")

    # def switch(self):
    #     """Toggles the button state"""
    #     if self.tabpad.linenumbers.is_on:
    #         self.view.entryconfigure(0, label ="Line numbers: Off")
    #         self.tabpad.linenumbers.is_on = False
    #         self.tabpad.linenumbers.pack_forget()
    #     else:
    #         self.view.entryconfigure(0, label ="Line numbers: On")
    #         self.tabpad.linenumbers.is_on = True

    #         self.tabpad.linenumbers.pack_forget()
    #         self.tabpad.txt_edit.pack_forget()
    #         self.tabpad.scrollview.pack_forget()

    #         self.tabpad.linenumbers.pack(fill="y", side="left")
    #         self.tabpad.txt_edit.pack(fill="both", expand=True, side="left")
    #         self.tabpad.scrollview.pack(fill="y", side="left")

    def gavrix_exit(self):
        self.make_settings_bin()
        self.master.destroy()

    def make_settings_bin(self):
        tabs_collection = self.tabpad.tabs_collection
        for key, file in tabs_collection.items():
            if (file.widget):
                file.widget = file.widget.get("1.0", 'end-1c')
        interface.files_list = list(tabs_collection.values())
        bin_file = open("settings.bin", "wb")
        pickle.dump(interface, bin_file)
        bin_file.close()

    def save(self):
        """Saves the opened file, if no file is opened - acts like save_as()"""
        file = self.tabpad.tabs_collection[self.tabpad._nametowidget(self.tabpad.select())]
        if not file.path:
            self.save_as()
            return
        key = self.tabpad._nametowidget(self.tabpad.select())
        file = self.tabpad.tabs_collection[key]
        with open(file.path, "w") as output_file:
            text = file.widget.get("1.0", tk.END)
            output_file.write(text)
        self.tabpad.tab(key, text = file.name)
        file.edit = False

    def save_as(self):
        """Saves the current file as new"""
        path_to_an_file = asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files","*.txt"),("All files", "*.*")]
        )
        if not path_to_an_file:
            return
        key = self.tabpad._nametowidget(self.tabpad.select())
        file = self.tabpad.tabs_collection[key]
        file.path = path_to_an_file
        with open(path_to_an_file, "w") as output_an_file:
            text = file.widget.get("1.0", tk.END)
            output_an_file.write(text)
        self.tabpad.tab(key, text = file.name)
        file.edit = False

    def file_open(self):
        """Opens the file that user wants to edit"""
        path_to_file = askopenfilename(
                filetypes=[("All files", "*.*"), ("Text files", "*.txt")]
        )
        if not path_to_file:
            return
        tag = magic.from_file(path_to_file, mime=True)
        file = File(tag, path_to_file)
        self.tabpad.add_new(file)

    def file_close(self):
        """Closes the file that user has opened"""
        if self.tabpad.tabs_collection:
            tab_place = self.tabpad._nametowidget(self.tabpad.select())
            del self.tabpad.tabs_collection[tab_place]
            self.tabpad.forget(self.tabpad.select())

app = Application(title="Gavrix")
app.mainloop()