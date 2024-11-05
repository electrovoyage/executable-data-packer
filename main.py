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

args = parser.parse_args()

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
    print('an argument is none')
    sys.exit()
if os.path.basename(args.directory) == 'resources':
    args.basedirectory = os.path.dirname(args.directory)

print('Collecting files...')
filetree = {}
dirinfo = {}
for _cdir, dirs, files in os.walk(args.directory):
    cdir = os.path.relpath(_cdir, args.basedirectory)
    #current_dict = dirinfo
    
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
        
    if len(files) + len(dirs) == 0 and args.ignore_empty:
        continue
    
    for file in removeAssetPack(files):
        filepath = os.path.join(cdir, file).replace('\\', '/') # done for ease of access further on, i know what the os.path module is
        
        #if filepath.strip() in ignorelist:
        #    _files.remove(file)
        #    continue
        
        filedata: bytes

        with open(os.path.join(_cdir, file), 'rb') as rfile:
            filedata = rfile.read()

        filetree[filepath] = filedata
        
    dirinfo[cdir.replace('\\', '/')] = {'files': (files), 'dirs': dirs}

packdata = {'tree': filetree, 'dirinfo': dirinfo}

with open(os.path.join(args.basedirectory, 'assets.packed'), 'wb') as assets:
    
    print('Compressing...')
    data = gzip.compress(str(packdata).encode())
    
    print('Writing...')
    assets.write(b'!PACKED\n' + data)

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