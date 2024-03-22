from PIL import Image, ImageTk
from ttkbootstrap import *
from ttkbootstrap.scrolled import ScrolledFrame as _ScrolledFrame
from tkinter.filedialog import asksaveasfilename
from sys import argv, exit, getsizeof
import os
import electrovoyage_asset_unpacker as pack
from tkinter.filedialog import askopenfilename
from math import ceil

win = Window('Assetbundle Browser', size = (500, 232))

if len(argv) == 2:
    _file = argv[-1]
else:
    _file = askopenfilename(title='Pick a file to browse', defaultextension='.packed', filetypes=[('Packed executable assets', '.packed')])
    if not _file:
        exit()

global bundle
bundle = pack.AssetPack(_file)

def getFormatIconType(format: str) -> str:
    if format in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'ico']:
        return 'image'
    elif format in ['txt', 'json']:
        return 'text'
    else: return 'unknown'

current_directory = StringVar(win, 'resources') 

def changedir(s: str):
    #print(list(prerendered_dirs.keys()), current_directory.get())
    prerendered_dirs[current_directory.get()].pack_forget()
    current_directory.set(s)
    prerendered_dirs[current_directory.get()].pack(expand=True, fill=BOTH)

bundle_dir = bundle.getDir()
prerendered_dirs = {}

ICONS = {
    'folder_empty': ImageTk.PhotoImage(file=os.path.join(os.getcwd(), 'resources', 'folder.png')),
    'folder': ImageTk.PhotoImage(file=os.path.join(os.getcwd(), 'resources', 'folder_files.png')),
    'text': ImageTk.PhotoImage(file=os.path.join(os.getcwd(), 'resources', 'text.png')),
    'up': ImageTk.PhotoImage(file=os.path.join(os.getcwd(), 'resources', 'up.png')),
    'unknown': ImageTk.PhotoImage(file=os.path.join(os.getcwd(), 'resources', 'unknown.png'))
}

fileicons = {}

def getFileIcon(f: str) -> ImageTk.PhotoImage:
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
            
            global itk
            itk = ImageTk.PhotoImage(img)
            
            fileicons[f] = itk
            
            return fileicons[f]
            #return ImageTk.PhotoImage(Image.open(bundle.getfile(f)).resize((64, 64), Image.BICUBIC).convert('RGBA'))
        case _:
            return ICONS[mode]
        
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
        
        #Button(fram, text='Up', style=LIGHT, command=lambda: changedir('/'.join(self.location.split('/')[:-1])), state=DISABLED if self.location == 'resources' else NORMAL).grid(row=0, column=0, padx=5, pady=5)
        
        lastdir = 0
        for i, obj in enumerate(self.dirs):
            row, column = divmod(i, ITEMS_PER_ROW)
            def opencmd(dir_: str):
                changedir(dir_)
            btn = Button(fram, text=obj, image=ICONS['folder' + ('' if self.location + '/' + obj in list(bundle_dir.keys()) else '_empty')], style=(LIGHT), compound=TOP, command=lambda dir_=self.location + '/' + obj, opencmd=opencmd: opencmd(dir_))
            del opencmd
            btn.grid(row=row, column=column, padx=5, pady=5)
            
            lastdir = i + 1
        
        for i, file in enumerate(self.files):
            row, column = divmod(i + lastdir, ITEMS_PER_ROW)
            def opencmd(path: str):
                #bundle.unzip(path, exportpath)
                selfile.set(path)
            btn = Button(fram, text=file, compound=TOP, style=(LIGHT), image=getFileIcon(self.location + '/' + file), command=lambda path=self.location + '/' + file, opencmd=opencmd: opencmd(path))
            del opencmd
            btn.grid(row=row, column=column, padx=5, pady=5)
            
        return fram

#for dir in bundle.getDirList():
#print(bundle.listobjects(), bundle.getDir(), sep='\n'*2)

def get_size_format(b):
    # Define the size units and their corresponding labels
    size_units = ('bytes', 'KB', 'MB', 'GB', 'TB')

    # Calculate the size of the bytes object in different units
    size = getsizeof(b)
    size_label = size_units[0]

    for i in range(1, len(size_units)):
        if size < 1024.0:
            break
        size /= 1024.0
        size_label = size_units[i]

    return size, size_label

lowerhalf = Frame(win)
lowerhalf.pack(side=BOTTOM, expand=True, fill=BOTH)

dirview = _ScrolledFrame(lowerhalf, autohide=True)
dirview.pack(expand=True, fill=BOTH, ipadx=50)

def go_up():
    if current_directory.get() != 'resources':
        changedir('/'.join(current_directory.get().split('/')[:-1]))
    
Button(win, image=ICONS['up'], command=go_up, style=DARK).pack(side=LEFT, expand=True, anchor=W)
pathsel = Combobox(win)
pathsel.pack(side=RIGHT, expand=True, fill=X, ipadx=500)

pathsel.insert()

#dirs = {}
dirinfo: dict[str, Directory] = {}
for dirpath, objects in bundle.getDir().items():
    dirinfo[dirpath] = Directory(**objects, location=dirpath)
    prerendered_dirs[dirpath] = dirinfo[dirpath].createFrame()
    
print(dirinfo)

changedir('resources')

win.mainloop()