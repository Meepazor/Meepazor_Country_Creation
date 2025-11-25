import os
import re
import codecs
import sys
import csv

# Characters to strip from IDs but keep for localisation
IGNORED_CHARS = [" ", "-", "'", "!", "?", ",", ".", ":", ";", "’", '"', "(", ")", "[", "]"]

def sanitize_namespace(prefix: str, tag: str) -> str:
    """Make a safe namespace/ID by removing IGNORED_CHARS and collapsing underscores."""
    base = f"{prefix}_{tag}".lower()
    for ch in IGNORED_CHARS:
        base = base.replace(ch, "_")
    base = re.sub(r"_+", "_", base).strip("_")
    return base

def get_next_id(events_file: str, loc_file: str) -> int:
    """Find the next valid numeric ID by scanning existing files."""
    ids = set()
    if os.path.exists(events_file):
        with open(events_file, "r", encoding="utf-8") as f:
            ids.update(int(n) for n in re.findall(r"\.(\d+)", f.read()) if n.isdigit())
    if os.path.exists(loc_file):
        with open(loc_file, "r", encoding="utf-8-sig") as f:
            ids.update(int(n) for n in re.findall(r"\.(\d+)", f.read()) if n.isdigit())
    return max(ids, default=0) + 1

def non_blank_input(prompt):
    while True:
        s = input(prompt).strip()
        if s:
            return s

def prettify_loc(text: str, tag: str) -> str:
    """
    Replace placeholders in localisation text:
    ADJ, NAME, DEF, LEAD -> HOI4 dynamic tokens
    Then title-case words except tokens.
    """
    text = text.replace("ADJ", f"[{tag.upper()}.GetAdjectiveCap]")
    text = text.replace("NAME", f"[{tag.upper()}.GetNameCap]")
    text = text.replace("DEF", f"[{tag.upper()}.GetNameDefCap]")
    text = text.replace("LEAD", f"[{tag.upper()}.GetLeader]")

    # Replace underscores with spaces (useful for CSV input)
    text = text.replace("_", " ")

    pretty_words = []
    for word in text.split():
        if word.startswith("[") and word.endswith("]"):
            pretty_words.append(word)  # don’t title-case HOI4 tokens
        else:
            pretty_words.append(word.capitalize())
    return " ".join(pretty_words).strip()

def write_event(country, eid, title, desc, include_news, events_file, loc_file, capitalise=True):
    ns_country = sanitize_namespace("eot", country)
    ns_news = sanitize_namespace("eot", f"{country}_news")

    ev_block = f"""# {title}
country_event = {{
    id = {ns_country}.{eid}
    title = {ns_country}.{eid}.t
    desc = {ns_country}.{eid}.d
    picture = GFX_todo

    is_triggered_only = yes

    immediate = {{}}

    option = {{
        name = {ns_country}.{eid}.a
        trigger = {{}}
        ai_chance = {{
            base = 10
        }}
    }}
"""
    if include_news:
        ev_block += f"""
    after = {{
        news_event = {ns_news}.{eid}
    }}
"""
    ev_block += "}\n"

    if include_news:
        ev_block += f"""
# NEWS — {title}
news_event = {{
    id = {ns_news}.{eid}
    title = {ns_news}.{eid}.t
    desc = {ns_news}.{eid}.d
    picture = GFX_todo

    major = yes
    minor_flavor = yes
    fire_for_sender = no

    is_triggered_only = yes

    option = {{
        name = {ns_news}.{eid}.a
    }}
}}
"""

    # Apply capitalisation choice
    loc_title = prettify_loc(title, country) if capitalise else title
    loc_desc = prettify_loc(desc, country) if (capitalise and desc) else desc

    loc_blocks = [
        f" {ns_country}.{eid}.t: \"{loc_title}\"",
        f" {ns_country}.{eid}.d: \"{loc_desc}\"",
        f" {ns_country}.{eid}.a: \"OK\"",
    ]
    if include_news:
        loc_blocks.extend([
            f" {ns_news}.{eid}.t: \"{loc_title}\"",
            f" {ns_news}.{eid}.d: \"{loc_desc}\"",
            f" {ns_news}.{eid}.a: \"The world reacts.\"",
        ])

    with open(events_file, "a", encoding="utf-8") as f:
        f.write("\n\n" + ev_block)

    if not os.path.exists(loc_file):
        with codecs.open(loc_file, "w", encoding="utf-8-sig") as f:
            f.write("l_english:\n")
    with codecs.open(loc_file, "a", encoding="utf-8-sig") as f:
        f.write("\n".join(loc_blocks) + "\n")  # no extra blank line between events

    print(f"Added event {eid} to {events_file} and {loc_file}")

def interactive_mode():
    country = None
    include_news = None

    while True:
        if not country:
            country = non_blank_input("Enter country name: ").lower()
        else:
            country = country.lower()

        events_dir = os.path.join("events")
        loc_dir = os.path.join("localisation", "english", "events")
        os.makedirs(events_dir, exist_ok=True)
        os.makedirs(loc_dir, exist_ok=True)

        events_file = os.path.join(events_dir, f"{country}_events.txt")
        loc_file = os.path.join(loc_dir, f"{country}_events_l_english.yml")

        if include_news is None:
            yn = input("Do you want to include news events? (y/n): ").strip().lower()
            include_news = (yn == "y")

        title_input = non_blank_input("Enter event title: ")
        title = title_input.title()
        desc = input("Enter event description (can be blank): ").strip()

        eid = get_next_id(events_file, loc_file)
        write_event(country, eid, title, desc, include_news, events_file, loc_file)

        repeat = input("Add another event? (y/n, leave country blank to keep current): ").strip().lower()
        if repeat != "y":
            break
        new_country = input("Enter new country name (leave blank to use previous): ").strip()
        if new_country:
            country = new_country.lower()

def csv_mode(csv_path, include_news=True):
    with open(csv_path, newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        required = {"country", "title", "description"}
        headers = {h.strip().lower() for h in reader.fieldnames or []}
        if not required.issubset(headers):
            raise ValueError("CSV must have headers: country,title,description")

        for row in reader:
            country = row["country"].strip().lower()
            title_raw = row["title"].strip()
            desc = row.get("description", "").strip()

            # Decide per-row news inclusion
            row_news = include_news
            if "include_news" in row:
                val = row["include_news"].strip().lower()
                if val in {"y", "yes", "true", "1"}:
                    row_news = True
                elif val in {"n", "no", "false", "0"}:
                    row_news = False

            # Decide per-row localisation capitalisation
            row_cap = True
            if "capitalise_loc" in row:
                val = row["capitalise_loc"].strip().lower()
                if val in {"n", "no", "false", "0"}:
                    row_cap = False

            # Apply capitalisation to title only if chosen
            title = title_raw.title() if row_cap else title_raw

            events_dir = os.path.join("events")
            loc_dir = os.path.join("localisation", "english", "events")
            os.makedirs(events_dir, exist_ok=True)
            os.makedirs(loc_dir, exist_ok=True)

            events_file = os.path.join(events_dir, f"{country}_events.txt")
            loc_file = os.path.join(loc_dir, f"{country}_events_l_english.yml")

            eid = get_next_id(events_file, loc_file)
            write_event(country, eid, title, desc, row_news, events_file, loc_file, capitalise=row_cap)

if __name__ == "__main__":
    args = sys.argv[1:]
    include_news = True
    if "--no-news" in args:
        include_news = False
        args.remove("--no-news")

    if args:
        csv_mode(args[0], include_news=include_news)
    else:
        interactive_mode()
