from PIL import Image, ImageTk
from ttkbootstrap import *
from ttkbootstrap.scrolled import ScrolledFrame as _ScrolledFrame
import sys
import os
import electrovoyage_asset_unpacker as pack
from tkinter.filedialog import askopenfilename, askdirectory, asksaveasfilename
from math import ceil
import tktooltip as tip

win = Window('Asset browser', size = (500, 248))

'''global bundle
bundle = pack.AssetPack(_file)'''

def getFormatIconType(format: str) -> str:
    if format in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'ico']:
        return 'image'
    elif format in ['txt', 'json']:
        return 'text'
    else: return 'unknown'

current_directory = StringVar(win, 'resources')

def setdir(s: str):
    current_directory.set(s)
    prerendered_dirs[current_directory.get()].pack(expand=True, fill=BOTH)
    pathsel.set(s)

def changedir(s: str):
    prerendered_dirs[current_directory.get()].pack_forget()
    setdir(s)

PYINSTALLER = getattr(sys, 'frozen', False)
APP_DIRECTORY = os.path.dirname(sys.executable) if PYINSTALLER else os.getcwd()
_ICONS = {
    'folder_empty': Image.open(os.path.join(APP_DIRECTORY, 'resources', 'folder.png')),
    'folder': Image.open(os.path.join(APP_DIRECTORY, 'resources', 'folder_files.png')),
    'text': Image.open(os.path.join(APP_DIRECTORY, 'resources', 'text.png')),
    'up': Image.open(os.path.join(APP_DIRECTORY, 'resources', 'up.png')),
    'unknown': Image.open(os.path.join(APP_DIRECTORY, 'resources', 'unknown.png')),
    'export': Image.open(os.path.join(APP_DIRECTORY, 'resources', 'export.png')),
    'run': Image.open(os.path.join(APP_DIRECTORY, 'resources', 'run.png')),
    'tofolder': Image.open(os.path.join(APP_DIRECTORY, 'resources', 'export_tofolder.png')),
    'zip': Image.open(os.path.join(APP_DIRECTORY, 'resources', 'export_zip.png'))
}

ICONS: dict[str, ImageTk.PhotoImage] = {}
for key, value in _ICONS.items():
    ICONS[key] = ImageTk.PhotoImage(value)

fileicons = {}

def getFileIcon(f: str) -> ImageTk.PhotoImage:
    mode = getFormatIconType(os.path.splitext(os.path.basename(f))[1][1:])
    match mode:
        case 'image':
            imgdata = bundle.getfile(f)
            
            #with open('h.png', 'wb') as h:
            #    h.write(imgdata.read())
            print(f)
            
            img = Image.open(imgdata)
            del imgdata
            
            largeside = max(*img.size)
            largeside_ratio = 1
            if largeside is img.size[0]: largeside_obj = 'width'
            else: largeside_obj = 'height'
            
            smallside = min(*img.size)
            smallside_ratio = smallside / largeside
            smallside_newsize = ceil(smallside_ratio * 64)
            
            if largeside_obj == 'width':
                size = (largeside_ratio * 64, smallside_newsize)
            else:
                size = (smallside_newsize, largeside_ratio * 64)
            
            img = img.resize(size, Image.BICUBIC)
            
            del largeside, largeside_ratio, largeside_obj, smallside, smallside_ratio, size, smallside_newsize
            
            img = img.convert('RGBA')
            
            global itk
            itk = ImageTk.PhotoImage(img)
            
            fileicons[f] = itk
            
            return fileicons[f]
        case _:
            return ICONS[mode]
        
def getPILFileIcon(f: str) -> Image.Image:
    mode = getFormatIconType(os.path.splitext(os.path.basename(f))[1][1:])
    match mode:
        case 'image':
            imgdata = bundle.getfile(f)
            img = Image.open(imgdata)
            del imgdata
            
            largeside = max(*img.size)
            largeside_ratio = 1
            if largeside is img.size[0]: largeside_obj = 'width'
            else: largeside_obj = 'height'
            
            smallside = min(*img.size)
            smallside_ratio = smallside / largeside
            smallside_newsize = ceil(smallside_ratio * 64)
            
            if largeside_obj == 'width':
                size = (largeside_ratio * 64, smallside_newsize)
            else:
                size = (smallside_newsize, largeside_ratio * 64)
            
            img = img.resize(size, Image.BICUBIC)
            
            del largeside, largeside_ratio, largeside_obj, smallside, smallside_ratio, size, smallside_newsize
            
            img = img.convert('RGBA')         
            return img
        case _:
            return _ICONS[mode]
        
selfile = StringVar(win, '')

ITEMS_PER_ROW = 4

class Directory:
    def __init__(self, files: list[str], dirs: list[str], location: str):
        self.files = files
        self.dirs = dirs
        self.location = location
    def __str__(self) -> str:
        return f'Directory({self.files}, {self.dirs}, {self.location})'
    __repr__ = __str__
    def createFrame(self) -> Frame:
        fram = Frame(dirview)
        
        lastdir = 0
        for i, obj in enumerate(self.dirs):
            row, column = divmod(i, ITEMS_PER_ROW)
            def opencmd(dir_: str):
                changedir(dir_)
            btn = Button(fram, text=obj, image=ICONS['folder' + ('' if self.location + '/' + obj in list(bundle.getDir().keys()) else '_empty')], style=(LIGHT), compound=TOP, command=lambda dir_=self.location + '/' + obj, opencmd=opencmd: opencmd(dir_))
            del opencmd
            btn.grid(row=row, column=column, padx=5, pady=5)
            
            lastdir = i + 1
        
        for i, file in enumerate(self.files):
            row, column = divmod(i + lastdir, ITEMS_PER_ROW)
            def opencmd(path: str):
                selfile.set(path)
                updateselfile()
                file_options.focus()
            btn = Button(fram, text=file, compound=TOP, style=(LIGHT), image=getFileIcon(self.location + '/' + file), command=lambda path=self.location + '/' + file, opencmd=opencmd: opencmd(path))
            del opencmd
            btn.grid(row=row, column=column, padx=5, pady=5)
            
        return fram
    
    def createFrame_alt(self) -> Frame:
        fram = Frame(dirview)
        
        lastdir = 0
        for i, obj in enumerate(self.dirs):
            row, column = divmod(i, ITEMS_PER_ROW)
            def opencmd(dir_: str):
                changedir(dir_)
            btn = Button(fram, text=obj, image=ICONS['folder' + ('' if self.location + '/' + obj in list(bundle.getDir().keys()) else '_empty')], style=(LIGHT), compound=TOP, command=lambda dir_=self.location + '/' + obj, opencmd=opencmd: opencmd(dir_))
            del opencmd
            btn.grid(row=row, column=column, padx=5, pady=5)
            
            lastdir = i + 1
        
        for i, file in enumerate(self.files):
            row, column = divmod(i + lastdir, ITEMS_PER_ROW)
            def opencmd(path: str):
                selfile.set(path)
                updateselfile()
                
            global _itk
            _itk = ImageTk.PhotoImage(getPILFileIcon(self.location + '/' + file))    
            
            searchicons[self.location + '/' + file] = _itk
            
            btn = Button(fram, text=file, compound=TOP, style=(LIGHT), image=searchicons[self.location + '/' + file], command=lambda path=self.location + '/' + file, opencmd=opencmd: opencmd(path))
            del opencmd
            btn.grid(row=row, column=column, padx=5, pady=5)
            
        return fram
    
global _itk
searchicons: dict[str, ImageTk.PhotoImage] = {}

#for dir in bundle.getDirList():
#print(bundle.listobjects(), bundle.getDir(), sep='\n'*2)

def get_size_format(b: bytes) -> tuple[float, str]:
    # Define the size units and their corresponding labels
    size_units = ('bytes', 'KB', 'MB', 'GB', 'TB')

    # Calculate the size of the bytes object in different units
    size = sys.getsizeof(b)
    size_label = size_units[0]

    for i in range(1, len(size_units)):
        if size < 1024.0:
            break
        size /= 1024.0
        size_label = size_units[i]

    return size, size_label

def format_size(b: bytes) -> str:
    return '{:.2f} {}'.format(*get_size_format(b))

lowerhalf = Frame(win)
lowerhalf.pack(side=BOTTOM, expand=True, fill=BOTH)

dirview = _ScrolledFrame(lowerhalf, autohide=True)
dirview.pack(expand=True, fill=BOTH, ipadx=50)

def go_up():
    if current_directory.get() != 'resources':
        changedir('/'.join(current_directory.get().split('/')[:-1]))
    
Button(win, image=ICONS['up'], command=go_up, style=DARK).pack(side=LEFT, expand=True, anchor=W)

#dirs = {}
global dirinfo
dirinfo: dict[str, Directory] = {}
    
pathsel = Combobox(win, values=list(dirinfo.keys()))
pathsel.pack(side=RIGHT, expand=True, fill=X, ipadx=500000000)

def selectdir():
    if pathsel.get() in list(bundle.getDir().keys()):
        changedir(pathsel.get())
    else:
        search_kwd = pathsel.get()
        pathsel.set(f'Search for "{pathsel.get()}" in "{current_directory.get()}"')
        search(search_kwd)

global prerendered_dirs
prerendered_dirs: dict[str, Frame] = {}

menu = Menu(win)
win.configure(menu=menu)

file_menu = Menu(menu)
menu.add_cascade(menu=file_menu, label='File')
    
def loadBundle(f: str):
    if f:
        file_menu.entryconfigure(1, state=NORMAL)
        file_menu.entryconfigure(2, state=NORMAL)
        
        global bundle
        bundle = pack.identifyAndReadAssetPack(f)
        
        global prerendered_dirs
        if prerendered_dirs:
            for key, value in prerendered_dirs.items():
                value.destroy()

        prerendered_dirs = {}

        menu.entryconfigure(0, state=DISABLED)
        for num, (dirpath, objects) in enumerate(bundle.getDir().items(), 1):
            dirinfo[dirpath] = Directory(**objects, location=dirpath)
            prerendered_dirs[dirpath] = dirinfo[dirpath].createFrame()
            win.title(f'Asset browser - Loading assets: {num}/{len(bundle.getDir().items())}')
            
        menu.entryconfigure(0, state=NORMAL)

        pathsel.configure(values=list(dirinfo.keys()))
        
        setdir('resources')
        
file_menu.add_command(label='Open', command=lambda: loadBundle(askopenfilename(title='Pick a file to browse', defaultextension='.packed', filetypes=[('Packed executable assets', '.packed')])))
file_menu.add_command(label='Extract to folder...', command=lambda: bundle.extract(askdirectory(mustexist=True, title='Select folder to extract to')), image=ICONS['tofolder'], compound=LEFT, state=DISABLED)
file_menu.add_command(label='Convert to ZIP archive...', command=lambda: bundle.extract_tozip(asksaveasfilename(title='Select folder to extract to', defaultextension='.zip', filetypes=[('ZIP archive', '.zip')])), image=ICONS['zip'], compound=LEFT, state=DISABLED)

file_options = Toplevel('Export & properties', size=(250, 390))

global nofileicon
nofileicon = ImageTk.PhotoImage(file=os.path.join(APP_DIRECTORY, 'resources', 'nofile.png'))

selfile_maininfo = Label(file_options, text='No file selected', image=nofileicon, compound=TOP, font=24, justify=CENTER)
selfile_maininfo.pack(padx=5, pady=50)

selfile_info = Label(file_options, text='No file selected', justify=CENTER)
selfile_info.pack(side=TOP, padx=5, pady=10)

selfile_options = Labelframe(file_options, text='Operations')
selfile_options.pack(side=BOTTOM, expand=True, fill=BOTH, padx=5, pady=25)

exportbtn = Button(selfile_options, image=ICONS['export'], state=DISABLED)
exportbtn.pack(side=LEFT, padx=5, pady=5, ipady=4, expand=True)

exportandrun = Button(selfile_options, image=ICONS['run'], state=DISABLED)
exportandrun.pack(side=LEFT, padx=5, pady=5, ipady=4, expand=True)

tip.ToolTip(exportbtn, 'Export this file.')
tip.ToolTip(exportandrun, 'Export this file and open it with the associated program.')

FILEINFO_FORMAT = '''
Type: {}
Size: {}
'''

if len(sys.argv) == 2:
    loadBundle(sys.argv[-1])
    
def export_file(f: str):
    f_ext = os.path.splitext(f)[1]
    expath = asksaveasfilename(confirmoverwrite=True, defaultextension=f_ext, filetypes=[(f'{f_ext[1:].upper()} file', f_ext)])
    if expath:
        bundle.exportfile(f, expath)
        
    return expath

def exportandrun_func(f: str):
    npath = export_file(f)
    if npath:
       os.startfile(npath)

def updateselfile():
    global previewfileicon
    previewfileicon = ImageTk.PhotoImage(getPILFileIcon(selfile.get()))
    
    selfile_maininfo.configure(text=selfile.get(), image=previewfileicon)
    file = bundle.getfile(selfile.get())
    selfile_info.configure(text=FILEINFO_FORMAT.format(os.path.splitext(selfile.get())[1][1:].upper() + ' file', format_size(file.read())))
    expfunc = eval(f'lambda: export_file({repr(selfile.get())})', {'export_file': export_file})
    
    #print(selfile.get(), f'lambda: export_file({repr(selfile.get())})')
    exportbtn.configure(state=NORMAL, command=expfunc)
    exportandrun.configure(state=NORMAL, command=lambda f=selfile.get(), exportandrun_func=exportandrun_func: exportandrun_func(f))
    
def search(keyword: str):
    try:
        _cdir = bundle.getDir()[current_directory.get()]
        cdir = {'files': [], 'dirs': []}
        for file in _cdir['files']:
            if keyword in file:
                cdir['files'].append(file)
        for dir in _cdir['dirs']:
            if keyword in dir:
                cdir['dirs'].append(dir)
        prerendered_dirs[pathsel.get()] = Directory(**cdir, location=current_directory.get()).createFrame_alt()
        changedir(pathsel.get())
    except KeyError:
        pass

pathsel.bind('<<ComboboxSelected>>', lambda x: selectdir())
pathsel.bind('<Return>', lambda x: selectdir())

file_menu.add_separator()
file_menu.add_command(label='Quit', command=win.quit)

tip.ToolTip(pathsel, 'Select path to browse or enter text to search')

win.mainloop()