import pdfplumber
from itertools import groupby

# === SETTINGS ===
pdf_path = "your_roster.pdf"  # <-- change this to your file path
column = "left"  # or 'right'

# === EXTRACT WORDS FROM HALF PAGE ===
lines = []

with pdfplumber.open(pdf_path) as pdf:
    first_page = pdf.pages[0]
    split_x = first_page.width / 2

    for page in pdf.pages:
        words = page.extract_words()
        selected_words = [w for w in words if (w["x0"] < split_x if column == "left" else w["x0"] >= split_x)]

        # Group into lines by Y position
        for _, group in groupby(sorted(selected_words, key=lambda w: (int(w['top']), w['x0'])), key=lambda w: int(w['top'])):
            line = " ".join(word["text"] for word in group)
            lines.append(line)

# === CLEAN: keep only block between start and next "Individual duty plan for" ===
def clean_roster_text(lines):
    # Find start (first appearance of the header)
    try:
        start_idx = next(i for i, line in enumerate(lines) if line.strip() == "date H duty R dep arr AC info")
    except StopIteration:
        start_idx = 0

    # Find next occurrence of the "Individual duty plan" after that
    try:
        end_idx = next(i for i in range(start_idx + 1, len(lines)) if "Individual duty plan for" in lines[i])
    except StopIteration:
        end_idx = len(lines)

    return lines[start_idx + 1:end_idx]

cleaned_lines = clean_roster_text(lines)

# === OUTPUT ===
# Print to terminal
for line in cleaned_lines:
    print(line)

# Save to file
with open(f"{column}_column_cleaned.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(cleaned_lines))

print(f"\n✅ Extracted and cleaned text saved to: {column}_column_cleaned.txt")
