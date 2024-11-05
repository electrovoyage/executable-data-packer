python3 -m PyInstaller -y --onefile --distpath Explorer --workpath temp --windowed --hidden-import='PIL._tkinter_finder' file_explorer.py
cp -r resources Packer