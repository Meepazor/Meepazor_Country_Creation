import os
import re
import shutil
import random
from collections import defaultdict
from tkinter import Tk, filedialog

# === CONFIGURATION ===

# Ideology mapping for splitting
IDEOLOGY_MAP = {
    "fascism": ["extreme_nationalism", "national_socialism"],
    "communism": ["national_communism", "alt_communism", "radical_socialist"],
    "democratic": ["socialism_democracy", "liberal_democracy", "conservative_democracy"],
    "neutrality": ["authoritarian_democracy", "despotism_ideology"]
}

# Process only these file extensions
TARGET_EXTENSIONS = (".txt", ".yml", ".gui")

# List of filenames to ignore
IGNORE_FILES = [ "console_history.txt", "00_static_modifiers.txt" ]

SCRIPTED_TRIGGER_MAP = {
    "communism": "is_communist",
    "fascism": "is_fascist",
    "democratic": "is_democratic",
    "neutrality": "is_neutral"
}

def choose_directory(prompt):
    root = Tk()
    root.withdraw()
    selected_dir = filedialog.askdirectory(title=prompt)
    root.destroy()
    return selected_dir


def get_mod_relative_path(file_path, base_game_path):
    rel_path = os.path.relpath(file_path, base_game_path)
    parts = rel_path.split(os.sep)
    if len(parts) > 2 and (parts[0] == "integrated_dlc" or parts[0] == "dlc"):
        rel_path = os.path.join(*parts[2:])
    return rel_path

def transform_has_government(content):
    """Replace has_government = ideology with scripted trigger, robust to spacing, braces, comments, and newlines."""
    for ideology, trigger in SCRIPTED_TRIGGER_MAP.items():
        # Multiline match, ignore trailing spaces, match before end-of-line, comment, or closing brace
        pattern = rf"(?m)^\s*has_government\s*=\s*{ideology}\s*(?=$|[#}}])"
        content = re.sub(pattern, f"{trigger} = yes", content)
    return content

def transform_ruling_party(line):
    match = re.search(r"ruling_party\s*=\s*(\w+)", line)
    if match:
        ideology = match.group(1)
        if ideology in IDEOLOGY_MAP:
            replacement = random.choice(IDEOLOGY_MAP[ideology])
            return re.sub(r"ruling_party\s*=\s*\w+", f"ruling_party = {replacement}", line)
    return line


def transform_set_popularities(block):
    original_block = block
    lines = block.strip().splitlines()
    totals = {ideo: 0 for ideo in IDEOLOGY_MAP.keys()}

    for line in lines:
        m = re.match(r"\s*(\w+)\s*=\s*(\d+)", line)
        if m:
            old_ideo, value = m.group(1), int(m.group(2))
            if old_ideo in totals:
                totals[old_ideo] = value

    total_value = sum(totals.values())
    if total_value == 0:
        return original_block

    factor = 100 / total_value
    for k in totals:
        totals[k] = round(totals[k] * factor)

    new_lines = ["set_popularities = {"]
    for old_ideo, old_value in totals.items():
        new_ideos = IDEOLOGY_MAP[old_ideo]
        base_share = old_value // len(new_ideos)
        remainder = old_value % len(new_ideos)
        for i, new_ideo in enumerate(new_ideos):
            value = base_share + (remainder if i == len(new_ideos) - 1 else 0)
            new_lines.append(f"    {new_ideo} = {value}")
    new_lines.append("}")
    return "\n".join(new_lines)


def transform_add_popularity(content):
    def replacer(match):
        block = match.group("block")
        cleaned_block = "\n".join(line.split("#")[0] for line in block.splitlines())
        ideology = None
        popularity = None

        m_ideo = re.search(r"ideology\s*=\s*(\w+)", cleaned_block)
        if m_ideo:
            ideology = m_ideo.group(1)

        m_pop = re.search(r"popularity\s*=\s*([\-]?\d*\.?\d+|\w+)", cleaned_block)
        if m_pop:
            popularity = m_pop.group(1)

        if not ideology or ideology not in IDEOLOGY_MAP:
            return match.group(0)

        new_ideos = IDEOLOGY_MAP[ideology]

        # Numeric popularity
        if popularity and re.match(r"^-?\d*\.?\d+$", popularity):
            value = float(popularity)
            per_ideo = round((value / len(new_ideos)) / 0.005) * 0.005
            total_assigned = per_ideo * len(new_ideos)
            diff = round(value - total_assigned, 3)
            lines_out = []
            for i, ideo in enumerate(new_ideos):
                val = per_ideo if i < len(new_ideos) - 1 else per_ideo + diff
                lines_out.append(f"add_popularity = {{ ideology = {ideo} popularity = {val:.3f} }}")
            return "\n".join(lines_out)

        # Variable popularity
        if popularity:
            lines_out = [f"set_temp_variable = {{ ideology_pct = {popularity} }}",
                         f"divide_temp_variable = {{ ideology_pct = {len(new_ideos)} }}"]
            for ideo in new_ideos:
                lines_out.append(f"add_popularity = {{ ideology = {ideo} popularity = ideology_pct }}")
            return "\n".join(lines_out)

        return match.group(0)

    return re.sub(r"add_popularity\s*=\s*\{(?P<block>.*?)\}",
                  replacer,
                  content,
                  flags=re.DOTALL)


def transform_drift_and_acceptance(content):
    for ideo, new_ideos in IDEOLOGY_MAP.items():
        pattern = rf"{ideo}_drift\s*=\s*(-?\d*\.?\d+)"
        def drift_replacer(m):
            value = float(m.group(1))
            per = round((value / len(new_ideos)) / 0.1) * 0.1
            total_assigned = per * len(new_ideos)
            diff = round(value - total_assigned, 3)
            lines = []
            for i, n in enumerate(new_ideos):
                val = per if i < len(new_ideos) - 1 else per + diff
                lines.append(f"{n}_drift = {val:.1f}")
            return "\n".join(lines)
        content = re.sub(pattern, drift_replacer, content)

        pattern2 = rf"{ideo}_acceptance\s*=\s*(-?\d+)"
        def accept_replacer(m):
            value = int(m.group(1))
            per = round((value / len(new_ideos)) / 5) * 5
            total_assigned = per * len(new_ideos)
            diff = value - total_assigned
            lines = []
            for i, n in enumerate(new_ideos):
                val = per if i < len(new_ideos) - 1 else per + diff
                lines.append(f"{n}_acceptance = {val}")
            return "\n".join(lines)
        content = re.sub(pattern2, accept_replacer, content)

    return content


def process_content(content):
    new_content = transform_has_government(content)

    new_lines = []
    changed = False
    for line in new_content.splitlines():
        new_line = transform_ruling_party(line)
        if new_line != line:
            changed = True
        new_lines.append(new_line)
    new_content = "\n".join(new_lines)

    def popularity_replacer(match):
        nonlocal changed
        new_block = transform_set_popularities(match.group(0))
        if new_block != match.group(0):
            changed = True
        return new_block
    new_content = re.sub(r"set_popularities\s*=\s*\{([^}]*)\}", popularity_replacer, new_content, flags=re.DOTALL)

    transformed = transform_add_popularity(new_content)
    if transformed != new_content:
        changed = True
        new_content = transformed

    transformed = transform_drift_and_acceptance(new_content)
    if transformed != new_content:
        changed = True
        new_content = transformed

    return new_content if changed else content


def process_file(file_path, base_game_path, mod_path):
    if os.path.basename(file_path) in IGNORE_FILES:
        return None

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    new_content = process_content(content)

    if new_content == content:
        # DEBUG: if file contains ideologies but no change was made, alert user
        if any(ideo in content for ideo in IDEOLOGY_MAP.keys()):
            print(f"[DEBUG] Potential missed file (contains ideologies but no change): {file_path}")
        return None

    rel_path = get_mod_relative_path(file_path, base_game_path)
    mod_file_path = os.path.join(mod_path, rel_path)
    os.makedirs(os.path.dirname(mod_file_path), exist_ok=True)
    shutil.copy2(file_path, mod_file_path)
    with open(mod_file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Modified: {mod_file_path}")
    return mod_file_path


def generate_scripted_triggers(mod_path):
    triggers_dir = os.path.join(mod_path, "common", "scripted_triggers")
    os.makedirs(triggers_dir, exist_ok=True)
    file_path = os.path.join(triggers_dir, "00_generated_ideologies.txt")

    triggers = []
    for old_ideo, new_ideos in IDEOLOGY_MAP.items():
        trigger_name = SCRIPTED_TRIGGER_MAP[old_ideo]
        triggers.append(f"{trigger_name} = {{")
        triggers.append("    OR = {")
        for new_ideo in new_ideos:
            triggers.append(f"        has_government = {new_ideo}")
        triggers.append("    }")
        triggers.append("}")
        triggers.append("")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(triggers))

    print(f"Generated scripted triggers: {file_path}")


def process_directory(path, base_game_path, mod_path):
    modified_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(TARGET_EXTENSIONS):
                file_path = os.path.join(root, file)
                result = process_file(file_path, base_game_path, mod_path)
                if result:
                    modified_files.append(result)
    return modified_files


def print_summary(modified_files, mod_path):
    print("\n=== Summary of Changes ===")
    counts = defaultdict(int)
    for f in modified_files:
        rel = os.path.relpath(f, mod_path)
        top_folder = rel.split(os.sep)[0] if os.sep in rel else "<root>"
        counts[top_folder] += 1

    for folder, count in sorted(counts.items()):
        print(f"{folder}: {count} file(s) modified")


def review_changes(modified_files):
    print("\n=== Review Changes ===")
    if not modified_files:
        print("No files were modified.")
        return
    print(f"{len(modified_files)} file(s) were modified.")
    choice = input("Keep all modified files? [y/n]: ").strip().lower()
    if choice == "n":
        for file_path in modified_files:
            if os.path.basename(file_path) not in IGNORE_FILES and os.path.exists(file_path):
                os.remove(file_path)
        for root, dirs, files in os.walk(mod_path, topdown=False):
            if not dirs and not files:
                try:
                    os.rmdir(root)
                except OSError:
                    pass
        print("All modified files deleted.")
    else:
        print("All modified files kept.")


def main():
    print("Choose your HOI4 base game folder...")
    base_game_path = choose_directory("Select Hearts of Iron IV Base Game Folder")
    print(f"Base Game Path: {base_game_path}")

    print("Choose your mod folder...")
    global mod_path
    mod_path = choose_directory("Select Your Mod Folder")
    print(f"Mod Path: {mod_path}")

    print("\n=== Starting HOI4 Mod Script ===")
    modified_files = process_directory(base_game_path, base_game_path, mod_path)

    generate_scripted_triggers(mod_path)
    print_summary(modified_files, mod_path)

    print("\n=== Done! ===")
    review_changes(modified_files)


if __name__ == "__main__":
    main()
