python3 -m PyInstaller -y --onefile --distpath Explorer --workpath temp --windowed --upx-dir /mnt/f/upx --hidden-import='PIL._tkinter_finder' file_explorer.py
cp -r resources Packer