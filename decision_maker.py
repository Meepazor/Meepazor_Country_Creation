import os
import re
import csv
import codecs
import sys

def sanitize_key_component(text: str, tag: str) -> str:
    """
    Convert input into a HOI4-safe lower_snake_case key.
    Special replacements:
      ADJ/NAME/DEF -> tag.lower()
      LEAD -> leader
    Then deduplicate redundant tag prefixes and collapse possessive '_s'.
    """
    low_tag = tag.lower()

    # Handle special tokens
    text = text.replace("ADJ", low_tag)
    text = text.replace("NAME", low_tag)
    text = text.replace("DEF", low_tag)
    text = text.replace("LEAD", "leader")

    # Collapse non-alphanumeric to underscores
    s = re.sub(r'[^A-Za-z0-9]+', '_', text.strip())
    s = re.sub(r'_+', '_', s)
    s = s.strip('_').lower()

    # Deduplicate tag mentions: e.g. ger_ger_rearmament -> ger_rearmament
    parts = s.split('_')
    deduped = []
    for i, p in enumerate(parts):
        if i > 0 and p == low_tag and parts[i-1] == low_tag:
            continue
        deduped.append(p)
    s = '_'.join(deduped)

    # Collapse "_s_" into just "_" (handles LEADs_speech -> leader_speech)
    s = re.sub(r'_s_', '_', s)

    # Also clean trailing "_s" if at end (e.g. leader_s -> leader)
    s = re.sub(r'_s$', '', s)

    return s

def non_blank_input(prompt):
    while True:
        s = input(prompt).strip()
        if s:
            return s

def write_category(tag, category_key, categories_dir):
    categories_file = os.path.join(categories_dir, f"{tag}_categories.txt")
    category_block = f"""{category_key} = {{
    #icon = 
    #picture = 

    allowed = {{
        tag = {tag}
    }}
}}
"""
    os.makedirs(categories_dir, exist_ok=True)

    if not os.path.exists(categories_file):
        with open(categories_file, "w", encoding="utf-8") as f:
            f.write(category_block + "\n")
        return

    with open(categories_file, "r", encoding="utf-8") as f:
        content = f.read()

    if re.search(rf"\b{re.escape(category_key)}\s*=\s*{{", content):
        return

    with open(categories_file, "a", encoding="utf-8") as f:
        f.write("\n" + category_block + "\n")

def write_decision(tag, category_key, decision_key, decisions_dir):
    decisions_file = os.path.join(decisions_dir, f"{tag}_decisions.txt")

    decision_inner = f"""    {decision_key} = {{

        #icon = GFX_decision_generic_fundraising
        #priority = 1

        visible = {{}}
        available = {{}}
        on_map_mode = map_and_decisions_view

        #days_re_enable = 60
        #days_remove = 25
        #fire_only_once = yes
        #cost = 45

        complete_effect = {{

        }}

        modifier = {{

        }}

        remove_effect = {{

        }}
    }}"""

    os.makedirs(decisions_dir, exist_ok=True)

    if not os.path.exists(decisions_file):
        with open(decisions_file, "w", encoding="utf-8") as f:
            f.write(f"{category_key} = {{\n{decision_inner}\n}}\n")
        return

    with open(decisions_file, "r", encoding="utf-8") as f:
        content = f.read()

    if re.search(rf"\b{re.escape(decision_key)}\s*=\s*{{", content):
        return

    category_block_regex = re.compile(
        rf"({re.escape(category_key)}\s*=\s*{{)(.*?)(\n}})",
        flags=re.DOTALL
    )
    m = category_block_regex.search(content)
    if m:
        start, middle, end = m.groups()
        new_middle = middle.rstrip() + "\n" + decision_inner + "\n"
        content = content[:m.start()] + start + new_middle + end + content[m.end():]
    else:
        content += f"\n{category_key} = {{\n{decision_inner}\n}}\n"

    with open(decisions_file, "w", encoding="utf-8") as f:
        f.write(content)

def prettify_loc(text: str, tag: str) -> str:
    """
    Convert raw input into pretty localisation:
    - underscores -> spaces
    - replace placeholders (ADJ, NAME, DEF, LEAD) with HOI4 tokens
    - title-case the rest
    """
    # Placeholder replacements
    text = text.replace("ADJ", f"[{tag}.GetAdjectiveCap]")
    text = text.replace("NAME", f"[{tag}.GetNameCap]")
    text = text.replace("DEF", f"[{tag}.GetNameDefCap]")
    text = text.replace("LEAD", f"[{tag}.GetLeader]")

    # Replace underscores with spaces
    text = text.replace("_", " ")

    # Title case while preserving brackets
    pretty_words = []
    for word in text.split():
        if word.startswith("[") and word.endswith("]"):
            pretty_words.append(word)  # don't mess with tokens
        else:
            pretty_words.append(word.capitalize())
    return " ".join(pretty_words)

import os
import codecs

def write_localisation(tag, category_key, decision_key, category_input, decision_input, loc_dir):
    """
    Writes HOI4 localisation entries under #CATEGORIES and #DECISIONS sections,
    avoiding duplicates and preserving order.
    """
    loc_file = os.path.join(loc_dir, f"{tag}_decisions_l_english.yml")
    os.makedirs(loc_dir, exist_ok=True)

    # Prepare new lines
    category_line = f" {category_key}: \"{prettify_loc(category_input, tag)}\""
    decision_line = f" {decision_key}: \"{prettify_loc(decision_input, tag)}\""

    # Ensure the file exists with header and sections
    if not os.path.exists(loc_file):
        with codecs.open(loc_file, "w", encoding="utf-8-sig") as f:
            f.write("l_english:\n")
            f.write(" #CATEGORIES\n")
            f.write(" #DECISIONS\n")

    # Read existing lines
    with codecs.open(loc_file, "r", encoding="utf-8-sig") as f:
        lines = [line.rstrip("\n") for line in f]

    # Ensure sections exist
    if " #CATEGORIES" not in lines:
        lines.append(" #CATEGORIES")
    if " #DECISIONS" not in lines:
        lines.append(" #DECISIONS")

    # Split content into sections
    header_index = 0
    categories_index = lines.index(" #CATEGORIES")
    decisions_index = lines.index(" #DECISIONS")

    # Extract existing entries under each section
    categories = lines[categories_index+1 : decisions_index]
    decisions = lines[decisions_index+1 :]

    # Append new lines if not already present
    if category_line not in categories:
        categories.append(category_line)
    if decision_line not in decisions:
        decisions.append(decision_line)

    # Rebuild file
    with codecs.open(loc_file, "w", encoding="utf-8-sig") as f:
        f.write("l_english:\n")
        f.write(" #CATEGORIES\n")
        for line in categories:
            f.write(line + "\n")
        f.write(" #DECISIONS\n")
        for line in decisions:
            f.write(line + "\n")

def add_decision(tag, category_input, decision_input, root="."):
    tag = tag.upper()
    category_key = f"{tag}_{sanitize_key_component(category_input,tag)}"
    decision_key = f"{tag}_{sanitize_key_component(decision_input,tag)}"

    categories_dir = os.path.join(root, "common", "decisions", "categories")
    decisions_dir = os.path.join(root, "common", "decisions")
    loc_dir = os.path.join(root, "localisation", "english", "decisions")

    write_category(tag, category_key, categories_dir)
    write_decision(tag, category_key, decision_key, decisions_dir)
    write_localisation(tag, category_key, decision_key, category_input, decision_input, loc_dir)

    print(f"Added decision '{decision_key}' under category '{category_key}'.")

def interactive_mode():
    tag = None
    while True:
        if not tag:
            tag = non_blank_input("Enter country tag (e.g., ENG, GER): ").upper()
        category_input = non_blank_input("Enter decision category name: ")
        decision_input = non_blank_input("Enter decision name: ")

        add_decision(tag, category_input, decision_input)

        repeat = input("Add another decision? (y/n, leave tag blank to keep current): ").strip().lower()
        if repeat != "y":
            break
        new_tag = input("Enter new country tag (leave blank to use previous): ").strip()
        if new_tag:
            tag = new_tag.upper()

def csv_mode(path):
    with open(path, newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        required = {"tag", "category", "decision"}
        if not required.issubset({h.strip().lower() for h in reader.fieldnames or []}):
            raise ValueError("CSV must have headers: tag, category, decision")
        for row in reader:
            tag = row["tag"].strip().upper()
            category_input = row["category"].strip()
            decision_input = row["decision"].strip()
            if not tag or not category_input or not decision_input:
                continue
            add_decision(tag, category_input, decision_input)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # File passed via SendTo
        csv_mode(sys.argv[1])
    else:
        # Manual run
        interactive_mode()
