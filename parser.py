import pdfplumber
from itertools import groupby

# === SETTINGS ===
pdf_path = "your_roster.pdf"  # <-- update with your actual path

# === FUNCTION: Extract lines from one half ===
def extract_column_lines(pdf, column):
    lines = []
    split_x = pdf.pages[0].width / 2

    for page in pdf.pages:
        words = page.extract_words()
        selected_words = [w for w in words if (w["x0"] < split_x if column == "left" else w["x0"] >= split_x)]

        for _, group in groupby(sorted(selected_words, key=lambda w: (int(w['top']), w['x0'])), key=lambda w: int(w['top'])):
            line = " ".join(word["text"] for word in group)
            lines.append(line)

    return lines

# === FUNCTION: Clean out headers and footers ===
def clean_roster_text(lines, column):
    cleaned = []
    capturing = False

    for line in lines:
        if line.strip() == "date H duty R dep arr AC info":
            capturing = True
            continue  # skip header

        # Stop at footers
        if "Individual duty plan for" in line or "NetLine/Crew" in line:
            capturing = False
            continue

        # Column-specific cutoff points
        if column == "left" and line.strip().lower().startswith("hotels"):
            break  # stop collecting when hotel list begins
        if column == "right" and line.strip().lower().startswith("flight time"):
            break  # stop collecting when summary begins

        if capturing:
            cleaned.append(line)

    return cleaned



# === MAIN PROCESS ===
with pdfplumber.open(pdf_path) as pdf:
    left_raw = extract_column_lines(pdf, "left")
    right_raw = extract_column_lines(pdf, "right")

# Clean both
left_cleaned = clean_roster_text(left_raw, "left")
right_cleaned = clean_roster_text(right_raw, "right")

# Save separately
with open("left_column_cleaned.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(left_cleaned))

with open("right_column_cleaned.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(right_cleaned))

# Combine and save
import re
from collections import OrderedDict

# Combine both
combined_all = left_cleaned + right_cleaned

# Group by lines that start with a weekday + day number
day_start_pattern = re.compile(r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\d{2}")
blocks = []
current_block = []
current_day = None

for line in combined_all:
    if day_start_pattern.match(line):
        if current_block:
            blocks.append((current_day, current_block))
        current_day = line
        current_block = [line]
    else:
        current_block.append(line)

# Add final block
if current_block:
    blocks.append((current_day, current_block))

# Define real calendar order for sorting
weekday_order = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
def block_sort_key(block):
    day_str = block[0][:3]
    date_num = int(block[0][3:5])
    return date_num + weekday_order[day_str] / 10  # small offset for tie-breaking

# Sort blocks
sorted_blocks = sorted(blocks, key=block_sort_key)

# Flatten back into lines
sorted_lines = [line for _, block in sorted_blocks for line in block]

# Save
with open("combined_cleaned_roster.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(sorted_lines))

print("✅ Combined file now sorted by day!")


print("✅ Left, right, and combined cleaned rosters saved.")
