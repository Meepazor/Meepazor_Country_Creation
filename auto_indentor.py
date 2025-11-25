import os
import tkinter as tk
from tkinter import filedialog

def reformat_file(file_path, create_backup=True, indent_char="\t"):
    with open(file_path, "r", encoding="utf-8") as f:
        raw_lines = f.readlines()

    lines = []
    for raw in raw_lines:
        line = raw.strip()
        if not line:
            continue
        if line.endswith("="):
            lines.append(line + " {")
        else:
            lines.append(line)

    joined_text = "\n".join(lines)
    joined_text = joined_text.replace("= { {", "= {")

    def flush_buffer():
        nonlocal buffer
        if buffer.strip():
            formatted.append(f"{indent_char * indent}{buffer.strip()}")
        buffer = ""

    formatted = []
    indent = 0
    in_quote = False

    for line in joined_text.splitlines():
        stripped = line.strip()

        if stripped.startswith("#"):
            formatted.append(f"{indent_char * indent}{stripped}")
            continue

        buffer = ""
        for ch in line:
            if ch == '"':
                in_quote = not in_quote
                buffer += ch
            elif not in_quote:
                if ch == "{":
                    if buffer.strip().endswith("="):
                        formatted.append(f"{indent_char * indent}{buffer.strip()} {{")
                        buffer = ""
                    else:
                        flush_buffer()
                        formatted.append(f"{indent_char * indent}{{")
                    indent += 1
                elif ch == "}":
                    flush_buffer()
                    indent = max(indent - 1, 0)
                    formatted.append(f"{indent_char * indent}}}")
                    buffer = ""
                else:
                    buffer += ch
            else:
                buffer += ch
        flush_buffer()

    base, ext = os.path.splitext(file_path)
    backup_path = base + ".bak"
    output_path = base + ext

    # Only create backup if allowed
    if create_backup:
        with open(backup_path, "w", encoding="utf-8") as f:
            f.writelines(raw_lines)
        print(f"Backup written to: {backup_path}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(formatted) + "\n")

    print(f"Formatted output written to: {output_path}")
    print(f"Lines written: {len(formatted)}")
    print("--------")


def main():
    root = tk.Tk()
    root.withdraw()

    file_paths = filedialog.askopenfilenames(
        title="Select file(s) to reformat",
        filetypes=[("File", "*.txt *.gui *.gfx *.asset"), ("All files", "*.*")]
    )

    if not file_paths:
        print("No files selected.")
        return

    multiple = len(file_paths) > 1

    for path in file_paths:
        reformat_file(
            path,
            create_backup=not multiple,      # Only back up if one file
            indent_char="\t"
        )

if __name__ == "__main__":
    main()
