import os
import re
import tkinter as tk
from tkinter import filedialog

def swap_tags_in_folder(folder_path, tag1, tag2):
    if not os.path.isdir(folder_path):
        print("Error: Provided path is not a valid folder.")
        return

    pattern_tag1 = re.compile(rf"\b{re.escape(tag1)}\b")
    pattern_tag2 = re.compile(rf"\b{re.escape(tag2)}\b")

    placeholder = "__TEMP_TAG_PLACEHOLDER__"
    files_changed = 0
    modified_files = []

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".txt"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()

                new_content = content
                new_content = pattern_tag1.sub(placeholder, new_content)
                new_content = pattern_tag2.sub(tag1, new_content)
                new_content = new_content.replace(placeholder, tag2)

                if new_content != content:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    files_changed += 1
                    modified_files.append(file)

    print(f"\nCompleted. {files_changed} file(s) modified.")
    if modified_files:
        print("Modified files:")
        for f in modified_files:
            print(f" - {f}")

if __name__ == "__main__":
    print("HOI4 Tag Swap Utility")

    # Folder selection dialog
    root = tk.Tk()
    root.withdraw()  # hide main window
    folder = filedialog.askdirectory(title="Select your 'history/states' folder")

    if not folder:
        print("No folder selected. Exiting.")
    else:
        tag1 = input("Enter first tag (e.g. GER): ").strip().upper()
        tag2 = input("Enter second tag (e.g. FRA): ").strip().upper()

        swap_tags_in_folder(folder, tag1, tag2)

    input("\nPress Enter to exit...")
