import re
from tkinter import filedialog, Tk
import os

def load_tags(path):
    """Load tags in order from a localisation file."""
    tags = []
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            m = re.match(r'^([A-Z0-9_]+):\d*\s+"[^"]*"', line)
            if m:
                tags.append(m.group(1))
    return tags

def load_localisation(path):
    """Load all localisation key-value pairs."""
    localisation = {}
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            m = re.match(r'^([A-Z0-9_]+):\d*\s+"([^"]*)"', line)
            if m:
                localisation[m.group(1)] = m.group(2)
    return localisation

def update_localisation(mod_path, mapping, base_loc):
    """Update mod localisation using base localisation via mapping."""
    updated_lines = []
    with open(mod_path, encoding="utf-8-sig") as f:
        for line in f:
            m = re.match(r'^([A-Z0-9_]+):\d*\s+"([^"]*)"', line)
            if m:
                mod_key = m.group(1)
                # Map to base tag if available
                base_tag = mapping.get(mod_key.split("_")[0])
                if base_tag:
                    suffix = mod_key[len(mod_key.split("_")[0]):]  # e.g. "_ADJ", "_DEF", "_ideology_DEF"
                    base_key = base_tag + suffix
                    if base_key in base_loc:
                        new_val = base_loc[base_key]
                        new_line = re.sub(r'"[^"]*"', f'"{new_val}"', line)
                        updated_lines.append(new_line)
                        print(f"{mod_key} → {base_key} ({new_val})")
                        continue
            updated_lines.append(line)
    return updated_lines

def update_colors(mod_path, base_path, mapping):
    """Update colors.txt blocks using mapping."""
    with open(base_path, encoding="utf-8-sig") as f:
        base_content = f.read()
    with open(mod_path, encoding="utf-8-sig") as f:
        mod_content = f.read()

    for mod_tag, base_tag in mapping.items():
        base_match = re.search(rf'{base_tag}\s*=\s*\{{.*?\n\}}', base_content, re.DOTALL)
        mod_match = re.search(rf'{mod_tag}\s*=\s*\{{.*?\n\}}', mod_content, re.DOTALL)
        if base_match and mod_match:
            new_block = re.sub(base_tag, mod_tag, base_match.group(0), count=1)
            mod_content = mod_content.replace(mod_match.group(0), new_block)
            print(f"Updated colors: {mod_tag} → {base_tag}")
        else:
            print(f"Skipped colors for {mod_tag} (no match found)")
    return mod_content

def main():
    Tk().withdraw()

    print("Select base game countries_l_english.yml")
    base_yml = filedialog.askopenfilename(title="Base countries_l_english.yml")
    print("Select mod countries_l_english.yml")
    mod_yml = filedialog.askopenfilename(title="Mod countries_l_english.yml")

    base_tags = load_tags(base_yml)
    mod_tags = load_tags(mod_yml)
    base_loc = load_localisation(base_yml)

    # Build mapping: each mod tag maps to the base tag in the same order
    mapping = {mod: base for mod, base in zip(mod_tags, base_tags)}
    print("Mapping built:")
    for m, b in mapping.items():
        print(f"  {m} → {b}")

    updated_lines = update_localisation(mod_yml, mapping, base_loc)
    mod_dir = os.path.dirname(mod_yml)
    updated_yml_path = os.path.join(mod_dir, "countries_l_english_updated.yml")
    with open(updated_yml_path, "w", encoding="utf-8-sig") as f:
        f.writelines(updated_lines)
    print(f"Updated localisation saved to {updated_yml_path}")

    print("Select base game colors.txt")
    base_colors = filedialog.askopenfilename(title="Base colors.txt")
    print("Select mod colors.txt")
    mod_colors = filedialog.askopenfilename(title="Mod colors.txt")

    updated_colors = update_colors(mod_colors, base_colors, mapping)
    updated_colors_path = os.path.join(os.path.dirname(mod_colors), "colors_updated.txt")
    with open(updated_colors_path, "w", encoding="utf-8-sig") as f:
        f.write(updated_colors)
    print(f"Updated colors saved to {updated_colors_path}")

if __name__ == "__main__":
    main()
