import os
import re
import tkinter as tk
from tkinter import filedialog

# Regex patterns
STATE_ID_PATTERN = re.compile(r"id\s*=\s*(\d+)")
COAL_PATTERN = re.compile(r"coal\s*=\s*(\d+)", re.IGNORECASE)
RESOURCES_BLOCK_PATTERN = re.compile(r"resources\s*=\s*\{", re.IGNORECASE)


def select_folder(title):
    root = tk.Tk()
    root.withdraw()
    return filedialog.askdirectory(title=title)


def parse_base_states(base_folder):
    """
    Reads base-game state files and extracts:
      - state ID
      - total coal amount
    Returns dict: { state_id: coal_amount }
    """
    state_coal = {}

    for fname in os.listdir(base_folder):
        if not fname.endswith(".txt"):
            continue

        fpath = os.path.join(base_folder, fname)
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Find state id
        id_match = STATE_ID_PATTERN.search(content)
        if not id_match:
            continue
        sid = int(id_match.group(1))

        # Extract all resources blocks
        blocks = re.findall(r"resources\s*=\s*\{([^}]*)\}", content,
                            flags=re.IGNORECASE | re.DOTALL)

        coal_total = 0
        for block in blocks:
            m = COAL_PATTERN.search(block)
            if m:
                coal_total += int(m.group(1))

        if coal_total > 0:
            state_coal[sid] = coal_total

    return state_coal


def find_state_block_end(lines, state_start_idx):
    """
    Given the index where 'state = {' occurs,
    return the index of the correct matching closing brace.
    Uses brace-depth tracking to avoid nested block mistakes.
    """
    brace_depth = 0
    found_open = False

    for idx in range(state_start_idx, len(lines)):
        line = lines[idx]

        # Count braces
        brace_depth += line.count("{")
        brace_depth -= line.count("}")

        # First time we see a '{' after "state ="
        if not found_open and "{" in line:
            found_open = True
            continue

        # When brace depth returns to zero, block closes
        if found_open and brace_depth == 0:
            return idx

    return None


def find_state_block_start(lines):
    """
    Find the line index where the state block begins.
    Returns the index of the line containing "state = {".
    """
    for i, line in enumerate(lines):
        if "state" in line and "=" in line and "{" in line:
            return i
    return None


def apply_to_mod_states(mod_folder, base_coal_dict, log):
    """
    For each mod state file:
      - match by state ID
      - insert or update coal inside resources block
      - ensure insertion occurs ONLY inside the correct state block
    """

    # Build index of mod state files by state ID
    mod_index = {}

    for fname in os.listdir(mod_folder):
        if not fname.endswith(".txt"):
            continue
        fpath = os.path.join(mod_folder, fname)
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        m = STATE_ID_PATTERN.search(content)
        if m:
            sid = int(m.group(1))
            mod_index[sid] = fpath

    total_modified = 0

    for sid, coal in base_coal_dict.items():
        if sid not in mod_index:
            continue

        path = mod_index[sid]

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        state_start_idx = find_state_block_start(lines)
        if state_start_idx is None:
            log.write(f"WARNING: State {sid} in {path} has no state block.\n")
            continue

        state_end_idx = find_state_block_end(lines, state_start_idx)
        if state_end_idx is None:
            log.write(f"WARNING: Could not find end of state block for state {sid} in {path}.\n")
            continue

        # Determine if resources block exists in this state
        resources_start = None
        resources_end = None
        inside = False
        brace_depth = 0

        for i in range(state_start_idx, state_end_idx + 1):
            line = lines[i]

            if RESOURCES_BLOCK_PATTERN.search(line):
                resources_start = i
                # Find the end of this block
                brace_depth = line.count("{") - line.count("}")
                for j in range(i + 1, len(lines)):
                    brace_depth += lines[j].count("{")
                    brace_depth -= lines[j].count("}")
                    if brace_depth == 0:
                        resources_end = j
                        break
                break

        # Case 1: No resources block — insert one just before end of state block
        if resources_start is None:
            new_block = [
                "    resources = {\n",
                f"        coal = {coal}\n",
                "    }\n"
            ]

            new_lines = (
                lines[:state_end_idx] +
                new_block +
                lines[state_end_idx:]
            )

            with open(path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

            total_modified += 1
            log.write(f"Added new resources block with coal={coal} to state {sid} in {path}\n")

        else:
            # Case 2: Resources block exists — update or insert coal
            block_content = "".join(lines[resources_start:resources_end + 1])

            if COAL_PATTERN.search(block_content):
                updated_block = COAL_PATTERN.sub(f"coal = {coal}", block_content)
                log.write(f"Updated coal in state {sid} to {coal} in {path}\n")
            else:
                # Insert coal before closing brace
                updated_block = block_content.replace("}", f"    coal = {coal}\n}}")
                log.write(f"Inserted coal={coal} into existing resources block in state {sid} ({path})\n")

            new_lines = (
                lines[:resources_start] +
                updated_block.splitlines(keepends=True) +
                lines[resources_end + 1:]
            )

            with open(path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

            total_modified += 1

    return total_modified


def main():
    print("Select BASE GAME history/states folder")
    base_folder = select_folder("Select base game's history/states folder")

    print("Select MOD history/states folder")
    mod_folder = select_folder("Select mod's history/states folder")

    log_path = os.path.join(os.getcwd(), "coal_merge_log.txt")

    base_data = parse_base_states(base_folder)

    with open(log_path, "w", encoding="utf-8") as log:
        log.write("Coal Merge Operation Log\n")
        log.write("========================\n\n")
        log.write("Detected base-game coal values:\n")
        for sid, coal in sorted(base_data.items()):
            log.write(f"  State {sid}: coal={coal}\n")
        log.write("\n-----------------------------------\n")

        modified = apply_to_mod_states(mod_folder, base_data, log)

        log.write(f"\nTotal states modified: {modified}\n")

    print("Done. Log written to:", log_path)


if __name__ == "__main__":
    main()
