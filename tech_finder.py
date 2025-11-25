import os
import re
import tkinter as tk
from tkinter import filedialog

def find_matching_brace(text, start_index):
    """Given text[start_index] == '{', return index after matching '}', or len(text)."""
    n = len(text)
    if start_index >= n or text[start_index] != '{':
        return start_index
    depth = 0
    i = start_index
    while i < n:
        c = text[i]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return n

def extract_technologies_from_file(file_path):
    """
    Extract top-level tech names and their start year that are directly within
    the 'technologies = { ... }' block in the file.
    Returns dict { tech_name: year }.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    results = {}

    # Find the technologies = { ... } block
    m = re.search(r'\btechnologies\s*=\s*\{', text)
    if not m:
        return results

    block_start = m.end() - 1  # index of '{'
    block_end = find_matching_brace(text, block_start)
    block_text = text[block_start+1:block_end-1]  # contents inside technologies { ... }

    # scan through block_text to find direct children: name = { ... }
    i = 0
    n = len(block_text)
    key_re = re.compile(r'\s*([A-Za-z0-9_]+)\s*=\s*\{', re.ASCII)

    while i < n:
        mkey = key_re.match(block_text, i)
        if not mkey:
            i += 1
            continue

        key = mkey.group(1)
        brace_idx = mkey.end() - 1  # index of '{' relative to block_text
        # find matching brace (need to offset by block_start+1 when using find_matching_brace on full text)
        abs_brace_idx = block_start + 1 + brace_idx
        abs_block_end = find_matching_brace(text, abs_brace_idx)
        # extract the block contents (absolute indices)
        block_contents = text[abs_brace_idx+1:abs_block_end-1]

        # search for start_year or starting_year within this block (only inside the tech block)
        m_year = re.search(r'\bstart_year\s*=\s*([0-9]{3,4})\b', block_contents)
        if not m_year:
            m_year = re.search(r'\bstarting_year\s*=\s*([0-9]{3,4})\b', block_contents)
        if m_year:
            year = int(m_year.group(1))
            if year < 1936:
                year = 1935
            results[key] = year
            print(f"    Found tech: {key} ({year}) in {os.path.basename(file_path)}")
        # advance i to after this block (relative to block_text)
        i = (abs_block_end - (block_start + 1))

    return results

def main():
    root = tk.Tk()
    root.withdraw()

    print("Select your technologies folder...")
    tech_folder = filedialog.askdirectory(title="Select technologies folder")
    if not tech_folder:
        print("No folder selected. Exiting.")
        return

    all_techs = {}
    file_count = 0

    for root_dir, _, files in os.walk(tech_folder):
        for file in files:
            if not file.endswith(".txt"):
                continue
            file_count += 1
            file_path = os.path.join(root_dir, file)
            print(f"[{file_count}] Scanning {file_path}")
            try:
                techs = extract_technologies_from_file(file_path)
                # if duplicate tech names across files, keep first seen (or override if desired)
                for k, v in techs.items():
                    if k in all_techs:
                        print(f"      Duplicate tech {k} found; keeping first occurrence.")
                    else:
                        all_techs[k] = v
            except Exception as e:
                print(f"    Error parsing {file}: {e}")

    if not all_techs:
        print("No technologies found. Exiting.")
        return

    # sort by year then name
    sorted_techs = sorted(all_techs.items(), key=lambda x: (x[1], x[0]))

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "yearly_tech_arrays.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        for tech_name, year in sorted_techs:
            f.write(f"add_to_array = {{ tech_{year} = token:{tech_name} }}\n")

    # optional summary
    counts = {}
    for _, y in sorted_techs:
        counts[y] = counts.get(y, 0) + 1

    print("\nSummary:")
    for y in sorted(counts):
        print(f"  {y}: {counts[y]} techs")

    print(f"\nOutput written to: {output_path}")
    print(f"Total technologies: {len(sorted_techs)}")

if __name__ == "__main__":
    main()
