import os
import re
import tkinter as tk
from tkinter import filedialog

def main():
    # Hide Tk window
    root = tk.Tk()
    root.withdraw()

    print("Select your mod's history folder (e.g. .../mod/MODNAME/history)")
    history_path = filedialog.askdirectory(title="Select history folder")

    if not history_path:
        print("No folder selected.")
        return

    if not os.path.isdir(history_path):
        print("Invalid history folder.")
        return

    script_dir = os.path.abspath(os.getcwd())
    log_path = os.path.join(script_dir, "comment_log.txt")

    # Resolve HOI4 path relative structure
    mod_root = os.path.abspath(os.path.join(history_path, "..", ".."))
    hoi4_root = os.path.abspath(os.path.join(mod_root, ".."))
    error_log = os.path.join(hoi4_root, "logs", "error.log")

    if not os.path.isfile(error_log):
        print("Could not locate error.log at:", error_log)
        return

    print("Reading error.log ...")

    # Pattern for "invalid database object for effect/trigger: X"
    pattern = r"invalid database object for effect/trigger:\s*([A-Za-z0-9_\-\.]+)"
    invalid_objects = set()

    with open(error_log, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = re.search(pattern, line)
            if m:
                tech = m.group(1)
                tech = tech.rstrip(".,;:")  # strip punctuation
                invalid_objects.add(tech)

    # Start writing the log immediately
    with open(log_path, "w", encoding="utf-8") as log:

        log.write("Commented Out Entries Log\n")
        log.write("=========================\n\n")

        log.write("Invalid tech/object names detected in error.log:\n")
        if invalid_objects:
            for obj in sorted(invalid_objects):
                log.write(f" - {obj}\n")
        else:
            log.write(" (None found)\n")

        log.write("\n--------------------------------------------\n\n")

        if not invalid_objects:
            print("No invalid objects found.")
            return

        print("Found invalid objects:")
        for obj in invalid_objects:
            print(" -", obj)

        countries_path = os.path.join(history_path, "countries")
        if not os.path.isdir(countries_path):
            print("No countries folder found inside history/.")
            return

        print("\nScanning country history files...")

        files_changed = 0
        entries_changed = 0

        for rootdir, dirs, files in os.walk(countries_path):
            for filename in files:
                if not filename.endswith(".txt"):
                    continue

                file_path = os.path.join(rootdir, filename)

                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()

                modified = False
                new_lines = []

                for line in lines:
                    stripped = line.strip()

                    # Match patterns like: trench_warfare = 1
                    for invalid_obj in invalid_objects:
                        if re.match(rf"{re.escape(invalid_obj)}\s*=", stripped):
                            new_lines.append("# " + line)

                            # Log what was found and where
                            log.write(f"[{file_path}]\n")
                            log.write(f"    {line}")
                            log.write("\n")

                            modified = True
                            entries_changed += 1
                            break
                    else:
                        new_lines.append(line)

                if modified:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.writelines(new_lines)

                    files_changed += 1
                    print("Edited:", file_path)

        # Summary
        log.write("\n=== Summary ===\n")
        log.write(f"Files modified: {files_changed}\n")
        log.write(f"Entries commented out: {entries_changed}\n")

    print("\nFinished.")
    print("Files modified:", files_changed)
    print("Entries commented out:", entries_changed)
    print("Log written to:", log_path)

    # If nothing was edited, make this extremely clear in console
    if files_changed == 0:
        print("\nWarning: No matching entries found in any history/countries files.")
        print("All detected tech names were written to comment_log.txt for inspection.")


if __name__ == "__main__":
    main()
