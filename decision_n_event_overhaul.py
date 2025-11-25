import os
import re
import tkinter as tk
from tkinter import filedialog

def find_matching_brace(text, start_index):
    """
    Given text[start_index] == '{', return index of the character AFTER the matching '}'.
    If no match found, return len(text).
    """
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

def patch_decisions(file_path):
    """
    Replace allowed = { ... } blocks only when they are immediate children of a decision
    or decision category block. This avoids touching allowed blocks in triggers/effects.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    n = len(text)
    i = 0
    out = []
    stack = []  # track keys
    changed = False

    key_block_re = re.compile(r'(\s*)([A-Za-z0-9_]+)\s*=\s*\{', flags=re.DOTALL)
    allowed_re = re.compile(r'\s*allowed\s*=', flags=re.DOTALL)

    while i < n:
        m = key_block_re.match(text, i)
        if m:
            matched = m.group(0)
            key = m.group(2)
            out.append(matched)
            stack.append(key)
            i += len(matched)
            continue

        if text[i] == '{':
            out.append('{')
            stack.append(None)
            i += 1
            continue

        if text[i] == '}':
            out.append('}')
            if stack:
                stack.pop()
            i += 1
            continue

        m_allowed = allowed_re.match(text, i)
        if m_allowed:
            abs_allowed_pos = i + m_allowed.start()
            eq_idx = text.find('=', abs_allowed_pos)
            brace_idx = text.find('{', eq_idx if eq_idx != -1 else abs_allowed_pos)
            if brace_idx == -1:
                out.append(text[i:i + m_allowed.end()])
                i += m_allowed.end()
                continue

            # Only replace if parent is decisions or decision_categories
            if len(stack) >= 2 and stack[-2] in ('decisions', 'decision_categories'):
                end_idx = find_matching_brace(text, brace_idx)
                out.append('allowed = { always = no }')
                i = end_idx
                changed = True
                continue
            else:
                out.append(text[i:i + m_allowed.end()])
                i += m_allowed.end()
                continue

        out.append(text[i])
        i += 1

    new_text = "".join(out)
    if changed and new_text != text:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_text)
        print(f"Patched decisions/categories file: {file_path}")

def patch_events(file_path):
    """
    Add is_triggered_only = yes to top-level country_event/news_event definitions only,
    and remove mean_time_to_happen blocks wherever they occur.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    n = len(text)
    i = 0
    out = []
    changed = False
    count_mean_removed = 0
    count_is_added = 0
    count_skipped_nested = 0

    while i < n:
        # Remove mean_time_to_happen blocks wherever found
        if text.startswith("mean_time_to_happen", i):
            eq_idx = text.find("=", i + len("mean_time_to_happen"))
            brace_idx = text.find("{", eq_idx if eq_idx != -1 else i + len("mean_time_to_happen"))
            if brace_idx != -1:
                end_idx = find_matching_brace(text, brace_idx)
                i = end_idx
                changed = True
                count_mean_removed += 1
                continue
            out.append(text[i])
            i += 1
            continue

        # Detect top-level country_event / news_event definitions
        if text.startswith("country_event", i) or text.startswith("news_event", i):
            name = "country_event" if text.startswith("country_event", i) else "news_event"
            j = i + len(name)
            k = j
            while k < n and text[k].isspace():
                k += 1
            if k < n and text[k] == "=":
                brace_idx = text.find("{", k)
                if brace_idx != -1:
                    depth_before = text.count("{", 0, i) - text.count("}", 0, i)
                    block_end = find_matching_brace(text, brace_idx)
                    block_text = text[brace_idx:block_end]
                    if depth_before == 0:
                        if "is_triggered_only" not in block_text:
                            new_block = "{\n    is_triggered_only = yes" + block_text[1:]
                            out.append(text[i:brace_idx] + new_block)
                            i = block_end
                            changed = True
                            count_is_added += 1
                            continue
                        else:
                            out.append(text[i:block_end])
                            i = block_end
                            continue
                    else:
                        out.append(text[i])
                        i += 1
                        count_skipped_nested += 1
                        continue

        out.append(text[i])
        i += 1

    new_text = "".join(out)
    if new_text != text:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_text)
        print(f"Patched events file: {file_path} "
              f"(mean_time_removed={count_mean_removed}, is_triggered_added={count_is_added}, skipped_nested={count_skipped_nested})")

def main():
    root = tk.Tk()
    root.withdraw()
    print("Select the root mod folder...")
    folder = filedialog.askdirectory(title="Select Mod Folder")
    if not folder:
        print("No folder selected. Exiting.")
        return

    # Process decisions and decision categories
    decisions_path = os.path.join(folder, "common", "decisions")
    if os.path.exists(decisions_path):
        for root_dir, _, files in os.walk(decisions_path):
            for file in files:
                if file.endswith(".txt"):
                    patch_decisions(os.path.join(root_dir, file))

    # Process events
    events_path = os.path.join(folder, "events")
    if os.path.exists(events_path):
        for root_dir, _, files in os.walk(events_path):
            for file in files:
                if file.endswith(".txt"):
                    patch_events(os.path.join(root_dir, file))

    print("Finished processing.")

if __name__ == "__main__":
    main()
