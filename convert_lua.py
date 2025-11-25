import re
import tkinter as tk
from tkinter import filedialog
from collections import OrderedDict

def parse_lua_defines(file_path):
    """Parse a defines LUA file into an OrderedDict of { full_key: (value, comment) }."""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    stack = []
    defines = OrderedDict()

    open_block = re.compile(r'^\s*([A-Za-z0-9_]+)\s*=\s*\{\s*(--.*)?$')
    kv_pattern = re.compile(r'^\s*([A-Za-z0-9_]+)\s*=\s*(.+?)(--.*)?$')
    close_block = re.compile(r'^\s*\},?\s*(--.*)?$')

    for line in lines:
        # Open new block
        m_open = open_block.match(line)
        if m_open:
            stack.append(m_open.group(1))
            continue

        # Close a block
        if close_block.match(line):
            if stack:
                stack.pop()
            continue

        # Key-value
        m_kv = kv_pattern.match(line)
        if m_kv and stack:
            key, value, comment = m_kv.groups()
            full_key = ".".join(stack + [key])
            defines[full_key] = (value.strip(), (comment or "").strip())
            continue

    return defines


def compare_and_clean(mod_defines, base_defines):
    """Keep mod defines that differ from base but maintain original order."""
    cleaned = OrderedDict()
    for key, (value, comment) in mod_defines.items():
        base_entry = base_defines.get(key)
        if base_entry:
            base_value, _ = base_entry
            if value != base_value:
                cleaned[key] = (value, comment)
        # skip keys not present in base
    return cleaned


def write_flat_lua(defines, output_path):
    """Write cleaned defines grouped by top-level category, keeping original order."""
    last_category = None
    with open(output_path, "w", encoding="utf-8") as f:
        for full_key, (value, comment) in defines.items():
            parts = full_key.split(".")
            if len(parts) >= 2:
                category = parts[1]  # e.g., NDefines.NGame.START_DATE → "NGame"
            else:
                category = "Misc"

            # Add header if category changes
            if category != last_category:
                f.write(f"\n-- {category}\n")
                last_category = category

            line = f"{full_key} = {value}"
            if comment:
                line += f" {comment}"
            f.write(line + "\n")

    print(f"Wrote cleaned defines to {output_path}")


def main():
    root = tk.Tk()
    root.withdraw()

    print("Select your MOD defines LUA file...")
    mod_file = filedialog.askopenfilename(
        title="Select MOD defines.lua",
        filetypes=[("Lua files", "*.lua"), ("All files", "*.*")]
    )
    if not mod_file:
        print("No mod file selected. Exiting.")
        return

    print("Select BASE GAME defines LUA file...")
    base_file = filedialog.askopenfilename(
        title="Select BASE defines.lua",
        filetypes=[("Lua files", "*.lua"), ("All files", "*.*")]
    )
    if not base_file:
        print("No base file selected. Exiting.")
        return

    mod_defines = parse_lua_defines(mod_file)
    base_defines = parse_lua_defines(base_file)
    cleaned_defines = compare_and_clean(mod_defines, base_defines)

    output_file = mod_file.replace(".lua", "_diff.lua")
    write_flat_lua(cleaned_defines, output_file)

    print(f"\nDone! {len(cleaned_defines)} changed defines written to:")
    print(output_file)


if __name__ == "__main__":
    main()
