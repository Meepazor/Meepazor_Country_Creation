#!/usr/bin/env python3
import os
import re
import random
import tkinter as tk
from tkinter import filedialog

# --------------------------
# CONFIG
# --------------------------
VP_PERCENTAGE = {
    "fascism": 0.25,
    "democratic": 0.1,
    "communism": 0.2,
    "neutrality": 0.15
}
DEFAULT_PERCENTAGE = 0.15

TEMPLATES = """division_template = {
    name = "Militia Division"
    regiments = {
        infantry = { x = 0 y = 0 }
        infantry = { x = 0 y = 1 }
        infantry = { x = 1 y = 0 }
        infantry = { x = 1 y = 1 }
    }
    support = { }
}
division_template = {
    name = "Infantry Division"
    regiments = {
        infantry = { x = 0 y = 0 }
        infantry = { x = 0 y = 1 }
        infantry = { x = 0 y = 2 }
        infantry = { x = 1 y = 0 }
        infantry = { x = 1 y = 1 }
        infantry = { x = 1 y = 2 }
        infantry = { x = 2 y = 0 }
        infantry = { x = 2 y = 1 }
        infantry = { x = 2 y = 2 }
    }
    support = { }
}
division_template = {
    name = "Artillery Division"
    regiments = {
        infantry = { x = 0 y = 0 }
        infantry = { x = 0 y = 1 }
        infantry = { x = 0 y = 2 }
        infantry = { x = 1 y = 0 }
        infantry = { x = 1 y = 1 }
        infantry = { x = 1 y = 2 }
        artillery_brigade = { x = 2 y = 0 }
        artillery_brigade = { x = 2 y = 1 }
    }
    support = {
        artillery = { x = 0 y = 0 }
    }
}
division_template = {
    name = "Cavalry Division"
    regiments = {
        cavalry = { x = 0 y = 0 }
        cavalry = { x = 0 y = 1 }
        cavalry = { x = 1 y = 0 }
        cavalry = { x = 1 y = 1 }
        cavalry = { x = 2 y = 0 }
        cavalry = { x = 2 y = 1 }
    }
    support = { }
}
"""

DIVISION_TYPES = ["Militia Division", "Infantry Division", "Artillery Division", "Cavalry Division"]
WEIGHTS = [1, 3, 1, 1]

OWNER_PATTERN = re.compile(r'owner\s*=\s*"?([A-Z]{2,3})"?', flags=re.IGNORECASE)
VP_BLOCK_RE = re.compile(r'victory_points\s*=\s*(\{[^}]*\}|[^\n\r]*)', flags=re.IGNORECASE)
IDEOLOGY_PATTERN = re.compile(r'ruling_party\s*=\s*([a-zA-Z_]+)', flags=re.IGNORECASE)

def extract_vp_pairs_from_block(block_text):
    nums = re.findall(r'\d+', block_text)
    pairs = []
    for i in range(0, len(nums), 2):
        prov = int(nums[i])
        val = int(nums[i+1]) if (i + 1) < len(nums) else 0
        pairs.append((prov, val))
    return pairs

def parse_states(states_folder):
    tag_states = {}
    state_vps = {}
    for fname in os.listdir(states_folder):
        if not fname.endswith(".txt"):
            continue
        path = os.path.join(states_folder, fname)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        owner_m = OWNER_PATTERN.search(text)
        if not owner_m:
            continue
        tag = owner_m.group(1).upper()
        tag_states.setdefault(tag, []).append(fname)

        vps = []
        for vp_match in VP_BLOCK_RE.finditer(text):
            block = vp_match.group(1)
            vps.extend(extract_vp_pairs_from_block(block))

        seen = set()
        unique_pairs = []
        for prov, val in vps:
            if prov not in seen:
                seen.add(prov)
                unique_pairs.append((prov, val))
        state_vps[fname] = unique_pairs
    return tag_states, state_vps

def get_tag_ideology(countries_folder, tag):
    for fname in os.listdir(countries_folder):
        if fname.startswith(f"{tag} - "):
            path = os.path.join(countries_folder, fname)
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            m = IDEOLOGY_PATTERN.search(text)
            if m:
                return m.group(1).lower()
    return None

def state_filename_to_id(fname):
    m = re.match(r'\s*(\d+)', fname)
    return int(m.group(1)) if m else None

def write_units_file(units_folder, tag, vp_provinces):
    os.makedirs(units_folder, exist_ok=True)
    out_path = os.path.join(units_folder, f"{tag}_1936.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(TEMPLATES)
        f.write("\nunits = {\n")
        div_id = 1
        for prov in vp_provinces:
            div_type = random.choices(DIVISION_TYPES, weights=WEIGHTS, k=1)[0]
            f.write("    division = {\n")
            f.write(f'        name = "{div_type} {div_id}"\n')
            f.write(f'        location = {prov}\n')
            f.write(f'        division_template = "{div_type}"\n')
            f.write(f'        start_experience_factor = 0.4\n')
            f.write(f'        start_equipment_factor = 0.9\n')
            f.write("    }\n")
            div_id += 1
        f.write("}\n")
    print(f"Created OOB for {tag}: {out_path} ({len(vp_provinces)} divisions).")

def update_country_history(countries_folder, tag, owned_state_files, state_vps):
    for fname in os.listdir(countries_folder):
        if not fname.startswith(f"{tag} - "):
            continue
        path = os.path.join(countries_folder, fname)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        capital_match = re.search(r'^\s*capital\s*=\s*(\d+)\s*$', text, flags=re.MULTILINE)
        current_capital = int(capital_match.group(1)) if capital_match else None

        owned_state_ids = [state_filename_to_id(s) for s in owned_state_files if state_filename_to_id(s)]
        new_text = text

        # Choose new capital if missing or invalid
        if owned_state_ids:
            best_state_file = max(
                owned_state_files,
                key=lambda s: sum(val for _, val in state_vps.get(s, []))
            )
            best_state_id = state_filename_to_id(best_state_file)
            if best_state_id:
                if capital_match:
                    # Replace *all* existing capital lines, not just the first one
                    new_text = re.sub(r'^\s*capital\s*=\s*\d+\s*$',
                                      f"capital = {best_state_id}",
                                      new_text,
                                      flags=re.MULTILINE)
                else:
                    # Only add if no capital line exists at all
                    new_text = f"capital = {best_state_id}\n" + new_text
                print(f"{tag}: capital set to state {best_state_id}")

        oob_line = f'oob = "{tag}_1936"'
        if oob_line not in new_text:
            new_text = new_text.rstrip() + "\n" + oob_line + "\n"
            print(f"{tag}: added oob line")

        if new_text != text:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_text)
            print(f"Updated {fname}")

def main():
    random.seed()
    root = tk.Tk()
    root.withdraw()
    mod_folder = filedialog.askdirectory(title="Select Mod Root Folder")
    if not mod_folder:
        print("No folder chosen.")
        return

    states_folder = os.path.join(mod_folder, "history", "states")
    units_folder = os.path.join(mod_folder, "history", "units")
    countries_folder = os.path.join(mod_folder, "history", "countries")

    tag_states, state_vps = parse_states(states_folder)
    for tag, state_files in tag_states.items():
        provs = []
        for sfile in state_files:
            provs.extend(p for p, _ in state_vps.get(sfile, []))
        if not provs:
            continue

        ideology = get_tag_ideology(countries_folder, tag) if os.path.exists(countries_folder) else None
        pct = VP_PERCENTAGE.get(ideology, DEFAULT_PERCENTAGE)
        sample_size = max(1, int(len(provs) * pct))
        selected = random.sample(provs, sample_size)

        write_units_file(units_folder, tag, selected)
        if os.path.exists(countries_folder):
            update_country_history(countries_folder, tag, state_files, state_vps)

    print("Done: OOBs and country files updated.")

if __name__ == "__main__":
    main()
