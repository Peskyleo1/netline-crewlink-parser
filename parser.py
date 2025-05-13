import pdfplumber

# Path to your PDF file
pdf_path = "your_roster.pdf"  # <-- replace with actual path

# Choose which half to extract: 'left' or 'right'
column = "left"

# Open the PDF and extract based on x0 position
split_x = None
lines = []

with pdfplumber.open(pdf_path) as pdf:
    first_page = pdf.pages[0]
    page_width = first_page.width
    split_x = page_width / 2  # vertical midpoint, typically around 420

    for page in pdf.pages:
        words = page.extract_words()
        selected_words = [w for w in words if (w["x0"] < split_x if column == "left" else w["x0"] >= split_x)]

        # Group words into lines by Y-coordinate (approximate line height)
        from itertools import groupby

        for _, group in groupby(sorted(selected_words, key=lambda w: (int(w["top"]), w["x0"])), key=lambda w: int(w["top"])):
            line = " ".join(word["text"] for word in group)
            lines.append(line)

# Output the text
text_output = "\n".join(lines)
print(text_output)
