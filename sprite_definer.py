import os
import re

def define_and_replace_sprites(root_dir="."):
    characters_dir = os.path.join(root_dir, "common", "characters")
    gfx_file = os.path.join(root_dir, "interface", "mod_characters.gfx")

    # Regex to find portrait assignments like: small="gfx/leaders/AMR/AMR_Huey_Long.png"
    # Captures the field (small/large/etc.), the relative path, and the filename (without .png)
    path_pattern = re.compile(
        r'(\w+)\s*=\s*"(gfx/leaders/(?:[\w\d]+/)*([\w\d]+))\.png"'
    )

    all_matches = set()

    # Process every file in common/characters
    for filename in os.listdir(characters_dir):
        if not filename.endswith(".txt"):
            continue

        file_path = os.path.join(characters_dir, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            data = f.read()

        # Collect matches
        matches = path_pattern.findall(data)
        for _, rel_path, tag in matches:
            all_matches.add((rel_path, tag))

        # Replace with GFX references
        def replacer(match):
            field, rel_path, tag = match.groups()
            return f'{field}="GFX_{tag}"'

        new_data = path_pattern.sub(replacer, data)

        # Save updated file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_data)

        print(f"Updated {filename}, replaced {len(matches)} entries.")

    # Sort unique sprite tags alphabetically by tag (the filename part, not folder)
    unique_entries = sorted(all_matches, key=lambda x: (x[1], x[0]))

    # Prepare spriteType definitions
    sprite_defs = [
        f'    spriteType = {{ name = "GFX_{tag}" texturefile = "{rel_path}.png" }}'
        for rel_path, tag in unique_entries
    ]

    # Ensure gfx file exists
    os.makedirs(os.path.dirname(gfx_file), exist_ok=True)
    if not os.path.exists(gfx_file):
        with open(gfx_file, "w", encoding="utf-8") as f:
            f.write("spriteTypes = {\n}\n")

    # Read current gfx file
    with open(gfx_file, "r", encoding="utf-8") as f:
        gfx_data = f.read()

    # Extract existing sprite names
    existing = set(re.findall(r'name\s*=\s*"([^"]+)"', gfx_data))
    new_entries = [line for line in sprite_defs if re.search(r'name\s*=\s*"([^"]+)"', line).group(1) not in existing]

    # Insert before the last }
    if "spriteTypes" not in gfx_data:
        new_gfx_data = "spriteTypes = {\n" + "\n".join(sprite_defs) + "\n}\n"
    else:
        new_gfx_data = gfx_data.strip()[:-1] + "\n" + "\n".join(new_entries) + "\n}\n"

    # Write updated gfx file
    with open(gfx_file, "w", encoding="utf-8") as f:
        f.write(new_gfx_data)

    print(f"\nProcessed {len(unique_entries)} unique sprites.")
    print(f"Updated all .txt files in {characters_dir} and {gfx_file}.")


# Example usage
if __name__ == "__main__":
    define_and_replace_sprites(root_dir=".")
