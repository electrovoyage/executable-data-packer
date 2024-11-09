import os
import argparse
import sys
import gzip
import fnmatch

parser = argparse.ArgumentParser('main.exe')
parser.add_argument('-d', '-dir', '--directory', type = str, help='Directory to pack.')
parser.add_argument('-b', '-base', '--basedirectory', type = str, help='Base directory of project.')
parser.add_argument('-i', '-ignore', '--ignorelist', type = str, help='Ignorelist file. If specified, filenames written in this file will not be packed.', required=False)
parser.add_argument('-ne', '-noempty', '--ignore-empty', action='store_true', help='Don\'t write empty folders into the directory information. Folders are considered empty if there are no files in them after skipping files in the ignorelist (if specified).')

group = parser.add_mutually_exclusive_group(required=False)
group.add_argument('-il', '-interl', '--interleave', action='store_true', help='Create an interleaved asset pack.')
#group.add_argument('-s', '--split', action='store_true', help='Create an asset pack where every packed file is a new compressed file.')

args = parser.parse_args()

#print(args.interleave)
INTERLEAVE = 'interleave'
SPLIT_PACK = 'split_pack'
NORMAL = 'normal'

if args.interleave:
    ASSET_PACK_MODE = INTERLEAVE
elif args.split:
    ASSET_PACK_MODE = SPLIT_PACK
else:
    ASSET_PACK_MODE = NORMAL

print(f'Delete empty folders: {args.ignore_empty}')

def load_ignore_patterns(ignore_file: str) -> list[str]:
    """Load ignore patterns from the specified file."""
    patterns = []
    with open(ignore_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):  # Ignore empty lines and comments
                patterns.append('resources/' + line)
    return patterns

def should_ignore(file_path: str, patterns: list[str]) -> bool:
    """Check if the file matches any of the ignore patterns."""
    for pattern in patterns:
        #print(f'Pattern {pattern}, file {file_path}:', end='', flush=True)
        if fnmatch.fnmatch(file_path, pattern):
            #print('skipped')
            return True
        
    #print('packed')
    return False

if getattr(args, 'ignorelist', None) is not None:
    if not os.path.exists(args.ignorelist):
        raise ValueError('ignorelist is a non-existent file')

    patterns = load_ignore_patterns(args.ignorelist)
    
else: patterns = None

def removeAssetPack(files: list[str]) -> list[str]:
    _files = files
    if 'assets.packed' in _files:
        _files.remove('assets.packed')
        
    return _files

if args.directory is None or args.basedirectory is None and (os.path.basename(args.directory) != 'resources'):
    parser.print_help()
    sys.exit()
if os.path.basename(args.directory) == 'resources':
    args.basedirectory = os.path.dirname(args.directory)

excluded_folders: list[str] = []

print('Collecting files...')
filetree = {}
_dirinfo = {}
for _cdir, dirs, files in os.walk(args.directory):
    cdir: str = os.path.relpath(_cdir, args.basedirectory)
    #current_dict = _dirinfo
    
    '''
    def walk_directory(directory, ignore_file):
    """Recursively walk through the directory and skip ignored files."""
    ignore_patterns = load_ignore_patterns(ignore_file)

    for dirpath, dirnames, filenames in os.walk(directory):
        # Modify dirnames in-place to skip ignored directories
        dirnames[:] = [d for d in dirnames if not should_ignore(os.path.join(dirpath, d), ignore_patterns)]
        
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if not should_ignore(file_path, ignore_patterns):
                print(file_path)  # Process the file (e.g., print its path)
    '''
    
    if patterns:
        dirs = list(filter(lambda x: not should_ignore(os.path.join(cdir, x), patterns), dirs))
        files = list(filter(lambda x: not should_ignore(os.path.join(cdir, x), patterns), files))
        
        #print(files)
        
    #print(len(files), len(dirs))
    if len(files) + len(dirs) == 0 and args.ignore_empty == True:
        excluded_folders.append(cdir)
        _dirinfo[cdir.replace('\\', '/')] = {'files': [], 'dirs': []}
        continue
    
    for file in removeAssetPack(files):
        filepath = os.path.join(cdir, file).replace('\\', '/') # done for ease of access further on, i know what the os.path module is
        
        filedata: bytes

        with open(os.path.join(_cdir, file), 'rb') as rfile:
            filedata = rfile.read()

        filetree[filepath] = filedata
        
    #print(cdir, files, dirs)
    _dirinfo[cdir.replace('\\', '/')] = {'files': files, 'dirs': dirs}
    
dirinfo: dict[str, dict[str, list[str]]] = {}

if args.ignore_empty == True:
    print('Excluding empty directories (--ignore-empty)...')
    for path in _dirinfo:
        if len(_dirinfo[path]['files']) + len(_dirinfo[path]['dirs']) > 0:
            dirinfo[path] = _dirinfo[path]
        else:
            if path not in excluded_folders:
                excluded_folders.append(path)
            
    #print(dirinfo)   
            
    for path in dirinfo:
        for folder in excluded_folders:
            parent = '/'.join(path.split('/')[:-1])
            #print(parent)
            if parent.strip() == '': continue
            #print(_dirinfo[parent]['dirs'], folder)

            actualfoldername = folder.replace('\\', '/').split('/')[-1]

            if actualfoldername in _dirinfo[parent]['dirs']:
                dirinfo[parent]['dirs'].remove(actualfoldername)
                print(f'    - Excluded: "{folder}"')

def interleave_files(file_dict: dict[str, bytes]) -> tuple[bytearray, dict[str, dict[str, int]]]:
    '''
    Interleave files and return a `bytearray, dict` tuple where the bytearray is the interleaved file data and the dict is the allocation data.
    '''
    
    max_len = max(*[len(i) for i in file_dict.values()])
    filecount = len(file_dict)
    allocations: dict[str, dict[str, int]] = {}
    
    buffer = bytearray(max_len * filecount)
    
    for path, data in file_dict.items():
        findex = list(file_dict.keys()).index(path)
        
        for bindex, byte in enumerate(data):
            pos = findex + (filecount * bindex)
            
            buffer[pos] = byte
            
        allocations[path] = {'offset': findex, 'size': len(data)}
        
    return (buffer, allocations)
        
    #for findex, path in enumerate(file_dict):
    #    #while (char := readers[path].read(1)):
    #    #    pos = findex + (filecount * )
    #        #buffer[]
    #       # buffer.extend()

with open(os.path.join(args.basedirectory, 'assets.packed'), 'wb') as assets:
    
    match ASSET_PACK_MODE:
        case 'normal':
            packdata = {'tree': filetree, 'dirinfo': dirinfo}
            header = b'!PACKED\n'
        case 'interleave':
            packdata = {'allocations': {}, 'data': b'', 'dirinfo': dirinfo, 'filecount': len(filetree)}
            
            print('Interleaving files...')
            array, allocations = interleave_files(filetree)
            
            packdata['allocations'] = allocations
                
            header = b'!PACKED_INTERLEAVE\n'
            packdata['data'] = array

    print('Compressing...')
    data = gzip.compress(str(packdata).encode())
    
    print('Writing...')
    assets.write(header + data)    

def convert_size(size_bytes):
    # List of units in increasing order
    units = ['bytes', 'KB', 'MB', 'GB', 'TB']

    # Calculate the appropriate unit
    unit_index = 0
    while size_bytes >= 1024 and unit_index < len(units) - 1:
        size_bytes /= 1024
        unit_index += 1

    return f"{size_bytes:.2f} {units[unit_index]}"

print(f'Done, file size is {convert_size(os.path.getsize(os.path.join(args.basedirectory, "assets.packed")))}')