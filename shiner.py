import re
import tkinter as tk
from tkinter import filedialog

def convert_sprite_blocks(file_path, output_path):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Regex to capture: name and texturefile inside each SpriteType block
    pattern = re.compile(
        r'SpriteType\s*=\s*\{\s*'
        r'name\s*=\s*"GFX_([^"]+)"\s*'
        r'texturefile\s*=\s*"([^"]+)"\s*'
        r'\}',
        flags=re.DOTALL
    )

    template = (
        'SpriteType = {{\n'
        '\tname = "GFX_{name}_shine"\n'
        '\ttexturefile = "{path}"\n'
        '\teffectFile = "gfx/FX/buttonstate.lua"\n'
        '\tanimation = {{\n'
        '\t\tanimationmaskfile = "{path}"\n'
        '\t\tanimationtexturefile = "gfx/interface/goals/shine_overlay.dds"\n'
        '\t\tanimationrotation = -90.0\n'
        '\t\tanimationlooping = no\n'
        '\t\tanimationtime = 0.75\n'
        '\t\tanimationdelay = 0\n'
        '\t\tanimationblendmode = "add"\n'
        '\t\tanimationtype = "scrolling"\n'
        '\t\tanimationrotationoffset = {{ x = 0.0 y = 0.0 }}\n'
        '\t\tanimationtexturescale = {{ x = 1.0 y = 1.0 }}\n'
        '\t}}\n\n'
        '\tanimation = {{\n'
        '\t\tanimationmaskfile = "{path}"\n'
        '\t\tanimationtexturefile = "gfx/interface/goals/shine_overlay.tga"\n'
        '\t\tanimationrotation = 90.0\n'
        '\t\tanimationlooping = no\n'
        '\t\tanimationtime = 0.75\n'
        '\t\tanimationdelay = 0\n'
        '\t\tanimationblendmode = "add"\n'
        '\t\tanimationtype = "scrolling"\n'
        '\t\tanimationrotationoffset = {{ x = 0.0 y = 0.0 }}\n'
        '\t\tanimationtexturescale = {{ x = 1.0 y = 1.0 }}\n'
        '\t}}\n'
        '\tlegacy_lazy_load = no\n'
        '}}\n'
    )

    new_text = ""
    count = 0

    for match in pattern.finditer(text):
        name, path = match.groups()
        new_text += template.format(name=name, path=path) + "\n"
        count += 1

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(new_text.strip())

    print(f"Converted {count} SpriteType blocks and wrote to: {output_path}")


def main():
    root = tk.Tk()
    root.withdraw()

    input_file = filedialog.askopenfilename(
        title="Select .gfx file to convert",
        filetypes=[("GFX files", "*.gfx"), ("All files", "*.*")]
    )

    if not input_file:
        print("No file selected. Exiting.")
        return

    output_file = input_file.replace(".gfx", "_shine.gfx")
    convert_sprite_blocks(input_file, output_file)


if __name__ == "__main__":
    main()
