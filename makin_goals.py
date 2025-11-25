import os
import tkinter as tk
from tkinter import filedialog

def generate_sprite_files(selected_files, output_dir):
    if not selected_files:
        print("No files selected. Exiting.")
        return

    normal_output = []
    shine_output = []

    normal_template = (
        'SpriteType = {{\n'
        '\tname = "{gfx_name}"\n'
        '\ttexturefile = "{path}"\n'
        '}}\n'
    )

    shine_template = (
        'SpriteType = {{\n'
        '\tname = "{gfx_name}_shine"\n'
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

    for file_path in selected_files:
        unix_path = file_path.replace("\\", "/")

        # Ensure path starts from "gfx/"
        gfx_index = unix_path.lower().find("gfx/")
        if gfx_index != -1:
            path_for_gfx = unix_path[gfx_index:]
        else:
            print(f"Warning: file not under gfx folder: {file_path}")
            continue

        filename = os.path.basename(file_path)
        base_name, _ = os.path.splitext(filename)

        # Enforce GFX_focus_ prefix
        if not base_name.lower().startswith("focus_"):
            gfx_name = f"GFX_focus_{base_name}"
        else:
            gfx_name = f"GFX_{base_name}"

        normal_output.append(normal_template.format(gfx_name=gfx_name, path=path_for_gfx))
        shine_output.append(shine_template.format(gfx_name=gfx_name, path=path_for_gfx))

    # Output in the same directory as the script
    normal_path = os.path.join(output_dir, "focus_sprites_normal.gfx")
    shine_path = os.path.join(output_dir, "focus_sprites_shine.gfx")

    with open(normal_path, "w", encoding="utf-8") as f:
        f.write("\n".join(normal_output))

    with open(shine_path, "w", encoding="utf-8") as f:
        f.write("\n".join(shine_output))

    print(f"\nCreated {len(selected_files)} sprite definitions.")
    print(f"Normal file: {normal_path}")
    print(f"Shine file:  {shine_path}")


def main():
    root = tk.Tk()
    root.withdraw()

    print("Select all focus icon files (e.g. .dds, .tga, .png)...")
    selected_files = filedialog.askopenfilenames(
        title="Select focus icons",
        filetypes=[
            ("Image files", "*.dds *.tga *.png"),
            ("All files", "*.*")
        ]
    )

    # Output in the same folder as the Python script
    output_dir = os.path.dirname(os.path.abspath(__file__))
    generate_sprite_files(selected_files, output_dir)


if __name__ == "__main__":
    main()
