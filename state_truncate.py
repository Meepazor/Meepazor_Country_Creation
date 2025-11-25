import os
import re
import tkinter as tk
from tkinter import filedialog

def trim_last_digit_from_manpower(file_path):
    """Read a file and trim the last digit from 'manpower =' lines."""
    changed = False
    lines_out = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if "manpower =" in line:
                match = re.search(r"(manpower\s*=\s*)(\d+)", line)
                if match:
                    prefix, number = match.groups()
                    if len(number) > 1:  # Only trim if there's more than one digit
                        new_number = number[:-1]  # Remove last digit
                        line = f"{prefix}{new_number}\n"
                        changed = True
            lines_out.append(line)

    if changed:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines_out)
        print(f"Updated: {file_path}")
    else:
        print(f"No change: {file_path}")

def main():
    root = tk.Tk()
    root.withdraw()
    print("Select the folder containing your state files...")
    folder = filedialog.askdirectory(title="Select state files folder")
    if not folder:
        print("No folder selected. Exiting...")
        return

    for root_dir, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root_dir, file)
                trim_last_digit_from_manpower(file_path)

    print("\nAll state files processed.")

if __name__ == "__main__":
    main()
