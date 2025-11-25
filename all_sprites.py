import os
import re
from tkinter import Tk, filedialog

# Top-level folder substitution (applies to the folder immediately under gfx/)
# Example: anything under gfx/leaders/* becomes folder_name = "portrait"
TOPLEVEL_FOLDER_SUBSTITUTIONS = {
    "leaders": "portrait",
}

# Immediate folder substitutions (as before)
FOLDER_SUBSTITUTIONS = {
    "goals": "focus",
    "ideas": "idea",
    "deluge": "portrait"
}

FOLDER_SUBSTITUTIONS_2 = {
    # "portraits": "characters"
}

OUTPUT_FILENAME = "sprite_autogen.gfx"

Tk().withdraw()

gfx_path = filedialog.askdirectory(title="Select the mod's gfx folder")
if not gfx_path:
    raise SystemExit
gfx_path = os.path.normpath(gfx_path)

mod_root = os.path.dirname(gfx_path)
mod_interface = os.path.join(mod_root, "interface")
if not os.path.isdir(mod_interface):
    raise SystemExit

base_interface = filedialog.askdirectory(title="Select the base game's interface folder (optional)")

def gather_images(gfx_root):
    out = []
    for root, _, files in os.walk(gfx_root):
        for fn in files:
            ext = os.path.splitext(fn)[1].lower()
            if ext in (".png", ".dds"):
                full = os.path.join(root, fn)
                rel_modroot = os.path.relpath(full, mod_root).replace("\\", "/")
                rel_gfx = os.path.relpath(full, gfx_root).replace("\\", "/")
                out.append((full, rel_modroot, rel_gfx))
    return out

images = gather_images(gfx_path)

texture_pattern = re.compile(
    r'texturefile\s*=\s*(?:"([^"]+)"|\'([^\']+)\'|([^\s#\n\r]+))',
    re.IGNORECASE
)

def gather_defined(from_folder):
    res = set()
    if not from_folder or not os.path.isdir(from_folder):
        return res
    for fn in os.listdir(from_folder):
        if fn.lower().endswith(".gfx"):
            p = os.path.join(from_folder, fn)
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
            except:
                continue
            for m in texture_pattern.finditer(text):
                val = m.group(1) or m.group(2) or m.group(3)
                if val:
                    res.add(val.replace("\\", "/"))
    return res

defined = set()
defined |= gather_defined(mod_interface)
if base_interface:
    defined |= gather_defined(base_interface)

new_blocks = []

for full, rel_modroot, rel_gfx in images:
    tex = rel_modroot.replace("\\", "/")
    if not tex.startswith("gfx/"):
        tex = rel_gfx.replace("\\", "/")
        if not tex.startswith("gfx/"):
            tex = rel_modroot.replace("\\", "/")

    if tex in defined:
        continue

    rel_to_gfx = os.path.relpath(full, gfx_path).replace("\\", "/")
    parts = rel_to_gfx.split("/")
    if len(parts) > 1:
        top = parts[0]
    else:
        top = "misc"

    # top-level substitution
    folder_name = TOPLEVEL_FOLDER_SUBSTITUTIONS.get(top, None)
    if folder_name is None:
        # fallback to immediate folder logic
        parent_dir = os.path.dirname(rel_to_gfx).replace("\\", "/")
        if parent_dir in ("", "."):
            folder_name = "misc"
        else:
            folder_name = parent_dir.split("/")[-1]

        if folder_name in FOLDER_SUBSTITUTIONS:
            folder_name = FOLDER_SUBSTITUTIONS[folder_name]
        if folder_name in FOLDER_SUBSTITUTIONS_2:
            folder_name = FOLDER_SUBSTITUTIONS_2[folder_name]

    filename_no_ext = os.path.splitext(os.path.basename(rel_to_gfx))[0]

    # sanitize both parts
    folder_clean = re.sub(r'[^0-9A-Za-z_]', '_', folder_name)
    sprite_clean = re.sub(r'[^0-9A-Za-z_]', '_', filename_no_ext)

    sprite_name = f"GFX_{folder_clean}_{sprite_clean}"

    block = (
        "\tspriteType = {\n"
        f'\t\tname = "{sprite_name}"\n'
        f'\t\ttexturefile = "{tex}"\n'
        "\t}\n"
    )
    new_blocks.append(block)

# ----- DEDUPLICATION AND SEPARATION -----

# Extract name from block:
def extract_name(block):
    m = re.search(r'name\s*=\s*"([^"]+)"', block)
    return m.group(1) if m else None

by_name = {}
for b in new_blocks:
    n = extract_name(b)
    if not n:
        continue
    by_name.setdefault(n, []).append(b)

unique = []
duplicates = []

for name, blocks in by_name.items():
    if len(blocks) == 1:
        unique.append(blocks[0])
    else:
        for i, block in enumerate(blocks, start=1):
            new_name = f"{name}_{i}"
            renamed = re.sub(
                r'(name\s*=\s*")[^"]+(")',
                rf'\1{new_name}\2',
                block
            )
            duplicates.append(renamed)

out_path = os.path.join(mod_interface, OUTPUT_FILENAME)
if unique:
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("spriteTypes = {\n\n")
        for b in unique:
            f.write(b + "\n")
        f.write("}\n")

dup_path = os.path.join(mod_interface, "sprite_autogen_duplicates.gfx")
if duplicates:
    with open(dup_path, "w", encoding="utf-8") as f:
        f.write("# These had duplicate base names and were renamed.\n")
        f.write("spriteTypes = {\n\n")
        for b in duplicates:
            f.write(b + "\n")
        f.write("}\n")

if unique:
    print(len(unique), "unique sprites ->", out_path)
else:
    print("No unique sprites.")

if duplicates:
    print(len(duplicates), "duplicates ->", dup_path)
else:
    print("No duplicates.")
