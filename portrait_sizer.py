import os
from tkinter import Tk, filedialog
from PIL import Image

Tk().withdraw()
path = filedialog.askdirectory(title="Select folder")
if not path:
    exit()

for root, _, files in os.walk(path):
    for f in files:
        if f.lower().endswith(".png"):
            p = os.path.join(root, f)
            try:
                im = Image.open(p)
                im = im.resize((156, 210), Image.LANCZOS)
                im.save(p)
            except Exception:
                pass
