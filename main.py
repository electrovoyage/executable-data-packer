import os
import argparse
import sys
import gzip

parser = argparse.ArgumentParser('executable data packer or something idk')
parser.add_argument('-d', '-dir', '--directory', type = str, help='Directory to pack.')
parser.add_argument('-b', '-base', '--basedirectory', type = str, help='Base directory of project.')

args = parser.parse_args()

if args.directory is None or args.basedirectory is None and (os.path.basename(args.directory) != 'resources'):
    print('an argument is none')
    sys.exit()
if os.path.basename(args.directory) == 'resources':
    args.basedirectory = os.path.dirname(args.directory)
    
class PathInfo:
    def __init__(self, dirs, files):
        self.dirs = dirs
        self.files = files
    def __repr__(self):
        return f'PathInfo({self.dirs}, {self.files})'

print('Generating directory tree...')
filetree = {}
dirinfo = {}
for _cdir, dirs, files in os.walk(args.directory):
    cdir = os.path.relpath(_cdir, args.basedirectory)
    #current_dict = dirinfo
    for file in files:
        filepath = os.path.join(cdir, file).replace('\\', '/') # done for ease of access further on, i know what the os.path module is
        filedata: bytes

        with open(os.path.join(_cdir, file), 'rb') as rfile:
            filedata = rfile.read()

        filetree[filepath] = filedata
        dirinfo[cdir.replace('\\', '/')] = {'files': files, 'dirs': dirs}
    
print(dirinfo)

packdata = {'tree': filetree, 'dirinfo': dirinfo}
    
'''
for dirpath, dirnames, filenames in os.walk(root_dir):
    current_dir = directory_dict
    for dir_name in dirpath.split(os.sep):
        current_dir = current_dir.setdefault(dir_name, {})
    current_dir.update({dir_name: filenames})
'''

with open(os.path.join(args.basedirectory, 'assets.packed'), 'wb') as assets:
    
    assets.write(b'!PACKED\n' + gzip.compress(str(packdata).encode()))

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