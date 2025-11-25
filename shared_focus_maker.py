#!/usr/bin/env python3
import pandas as pd
import re
import os
import tkinter as tk
from tkinter import filedialog

def make_safe_id(title):
    safe = str(title or "").lower()
    safe = re.sub(r'[^a-z0-9 ]', '', safe)
    safe = re.sub(r'\s+', '_', safe.strip())
    return f"SHARED_{safe}" if safe else "SHARED_focus"

def find_available_filename(folder, base_name, ext):
    counter = 0
    while True:
        suffix = f"_{counter}" if counter > 0 else ""
        candidate = os.path.join(folder, f"{base_name}{suffix}.{ext}")
        if not os.path.exists(candidate):
            return candidate
        counter += 1

def normalize_indices(df, prereq_col, mutual_col):
    df_copy = df.copy()
    for col in [prereq_col, mutual_col]:
        new_values = []
        for val in df_copy[col]:
            if pd.isna(val):
                new_values.append(-1)  # -1 means no reference
                continue
            try:
                ival = int(float(val))
            except Exception:
                new_values.append(-1)
                continue
            new_values.append(ival - 1 if ival > 0 else -1)
        df_copy[col] = new_values
    return df_copy

def main():
    root = tk.Tk()
    root.withdraw()

    csv_path = filedialog.askopenfilename(
        title="Select Shared Focus CSV", filetypes=[("CSV Files", "*.csv")]
    )
    if not csv_path:
        print("No CSV selected.")
        return

    df = pd.read_csv(csv_path)
    col_map = {c.strip().lower(): c for c in df.columns}
    required = {"title", "cost", "x", "y", "prerequisite", "mutual"}
    if not required.issubset(col_map.keys()):
        print("CSV must have columns:", ", ".join(required))
        print("Found columns:", ", ".join(df.columns))
        return

    title_col = col_map["title"]
    cost_col = col_map["cost"]
    x_col = col_map["x"]
    y_col = col_map["y"]
    prereq_col = col_map["prerequisite"]
    mutual_col = col_map["mutual"]

    df = normalize_indices(df, prereq_col, mutual_col)

    normalized_path = os.path.splitext(csv_path)[0] + "_normalized.csv"
    df.to_csv(normalized_path, index=False)
    print(f"Normalized CSV written: {normalized_path}")

    total_rows = len(df)
    ids = [make_safe_id(t) for t in df[title_col].fillna("").astype(str)]

    mod_folder = filedialog.askdirectory(title="Select Mod Root Folder")
    if not mod_folder:
        print("No mod folder selected.")
        return

    focus_folder = os.path.join(mod_folder, "common", "national_focus")
    loc_folder = os.path.join(mod_folder, "localisation", "english")
    os.makedirs(focus_folder, exist_ok=True)
    os.makedirs(loc_folder, exist_ok=True)

    focus_file = find_available_filename(focus_folder, "shared_focuses", "txt")
    loc_file = find_available_filename(loc_folder, "shared_focuses_l_english", "yml")

    with open(focus_file, "w", encoding="utf-8") as f:
        for idx, row in df.iterrows():
            fid = ids[idx]
            f.write("shared_focus = {\n")
            f.write(f"\tid = {fid}\n")
            f.write("\ticon = GFX_goal_generic\n")
            f.write(f"\tx = {row[x_col]}\n")
            f.write(f"\ty = {row[y_col]}\n")
            f.write(f"\tcost = {row[cost_col]}\n\n")

            # FIXED: allow 0 as valid reference and skip self-references
            prereq_idx = int(row[prereq_col])
            if prereq_idx >= 0 and prereq_idx < total_rows and prereq_idx != idx:
                prereq_id = ids[prereq_idx]
                f.write(f"\trelative_position_id = {prereq_id}\n")
                f.write(f"\tprerequisite = {{ focus = {prereq_id} }}\n")

            mutual_idx = int(row[mutual_col])
            if mutual_idx >= 0 and mutual_idx < total_rows and mutual_idx != idx:
                mutual_id = ids[mutual_idx]
                f.write(f"\tmutually_exclusive = {{ focus = {mutual_id} }}\n")

            f.write("\n\tavailable_if_capitulated = yes\n\n")
            f.write("\tcompletion_reward = {\n\n\t}\n")
            f.write("}\n")

    with open(loc_file, "w", encoding="utf-8") as loc:
        loc.write("l_english:\n")
        for idx, row in df.iterrows():
            fid = ids[idx]
            title_text = str(row[title_col]).replace('"', "'")
            loc.write(f" {fid}:0 \"{title_text}\"\n")

    print(f"Focus file written: {focus_file}")
    print(f"Localisation file written: {loc_file}")

if __name__ == "__main__":
    main()
