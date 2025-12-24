# Load the PyMuPDF library
import fitz
# Load the PyMuPDF4LLM library
import pymupdf4llm
# Load Pathlib library
import pathlib as path
# Load Shutil library
import shutil
# Load os library
import os
# Load re library
import re
# Load counter from collections
from collections import Counter

doc = fitz.open('storage/originals/RBC_Scholarship.pdf')
#For every page in the document
for page in doc:
    text = page.get_text() #  Get all the text from the pdf
    print(text) # Print the text


# Total pages of pdf, covers creating the footers that match the same pattern for all 6 pages (Page 1 of 6, etc)
total_pages = 6

# For each number, starting at 1 and counting up by one until you reach the total number of pages (including page 6)
# Create the exact text of the footer for each page number, like "page 1 of 6",
footer_phrases = [f"page {i} of {total_pages}" for i in range(1, total_pages + 1)]

# Specify the texts to search for
search_words = ("RBC Future Launch Scholarship", "Universities Canada", "Foundation", "Scholarship Partners Canada", "2025 Program Guidelines") + tuple(footer_phrases)

# Save search_words into a blank dictionary called results
results = {}

# Iterate through each page in the PDF
for page in doc:

    words = page.get_text("words")
    # Use the `search_for` method to find instances of the search text on the page
    # text_instances = page.search_for(search_words)
    for w in words:
    # w is like: [x0, y0, x1, y1, "word_text", block_no, line_no, word_no]
    # bounding box coordinates
        x0, y0, x1, y1 = w[0], w[1], w[2], w[3]
    # the actual word
        word_text = w[4]
        block_no = w[5]
        line_no = w[6]
        word_no = w[7]
        print(f"Word '{word_text}' found at coordinates: ({x0}, {y0}), ({x1}, {y1})")
        print(f"Located in block {block_no}, line {line_no}, word number {word_no}\n")

    for sword in search_words:

        if sword in words:

            pages = results.get(sword, set())

            pages.add(page.number)

            results[sword] = pages

    for word in results:

        result = list(map(str, results[word]))

        page_list = ", ".join(result)

        print("Word '%s' occurs on pages %s." % (word, page_list))

    for page in doc:
        # Get the page height from the pdf
        H = page.rect.height
        x0 = page.rect.x0  # Get the left edge of pdf
        x1 = page.rect.x1 # Get the right edge of pdf

        # Sanity check
        print(f"Page height in points: {H}")
        print(f"Left Edge in points: {x0}")
        print(f"Right Edge in points: {x1}")

        # Calculate the header and footer band edges
        hdr_y0 = 0.04 * H   # Bottom edge of header band
        hdr_y1 = 0.09 * H   # Top edge of header band
        ftr_y0 = 0.93 * H   # Bottom edge of footer band
        ftr_y1 = 0.97 * H   # Top edge of footer band

        #Sanity check
        print(f"Header Bottom Edge in points: {hdr_y0}")
        print(f"Header Top Edge in points: {hdr_y1}")
        print(f"Footer Bottom Edge in points: {ftr_y0}")
        print(f"Footer Bottom Edge in points: {ftr_y1}")

        # Add 2pt padding to the rectangle to ensure everything is contained
        P = 2
        hdr_y0_padded = (hdr_y0 - P)
        hdr_y1_padded = (hdr_y1 + P)
        ftr_y0_padded = (ftr_y0 - P)
        ftr_y1_padded = (ftr_y1 + P)

        # Build two full width rectangles for header and footer
        header_rect = (x0, hdr_y0_padded , x1, hdr_y1_padded)
        footer_rect = (x0, ftr_y0_padded, x1, ftr_y1_padded)

        # Sanity check
        print(f"Header Rectangle in points: {header_rect}")
        print(f"Footer Rectangle in points: {footer_rect}")

        # Add redaction annotation to header and footer rectangles
        page.add_redact_annot(header_rect)
        page.add_redact_annot(footer_rect)

        # Apply redaction
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_REMOVE, graphics=fitz.PDF_REDACT_IMAGE_REMOVE,text=fitz.PDF_REDACT_TEXT_REMOVE)

        # Sanity check
        print("Successfully redacted")

# Save to new pdf
doc.save('storage/cleaned/redacted.pdf', garbage=4, deflate=True)

# Close PDF
doc.close()


md_text = pymupdf4llm.to_markdown('storage/cleaned/redacted.pdf')

md_path = path.Path('storage/cleaned/redacted.md')



bytes_written = md_path.write_text(md_text, encoding="utf-8", newline="\n")

print("Markdown saved to redacted.md")



# Copy and rename redacted.md for chunking
source_file = "storage/cleaned/redacted.md"
destination_folder = "storage/cleaned"
new_file_name = "copy_redacted.md"
new_path = os.path.join(destination_folder, new_file_name)



# Use the shutil.copy2() method to copy the file to the destination directory
shutil.copy2(source_file, new_path)

print("Successfully Created File and Renamed Redacted.md")

# Create a Path object for a file
file_path = path.Path('storage/cleaned/copy_redacted.md')

# Read the contents of the file
contents = file_path.read_text(encoding="utf-8")

# Sanity check if file is read, prints number of characters in file
print(len(contents))

# Split string into a list of lines and preserve format
lines = contents.splitlines(keepends=False)

match_lines = lines.copy()

sub_pattern = r'(\*\*)(.*?\bnumber\b)(.*?\band\b)(.*?\bvalue\b)(.*?\bof\b)(.*?\bscholarships\b)(\*\*)'
pattern = r'(\*\*)(.*?)(\*\*)'


# ^\s*\*\*([^*]+?)\*\*\s*:\s+(.+)$
sub_text = re.compile(sub_pattern, re.IGNORECASE)
bold_text = re.compile(pattern)


# Create empty list called matches to store results that match the pattern
matches = []

# Create separate counters for each category of results if the string is empty, has whitespaces, etc

empty = 0

whitespace_only = 0

whitespace_nbsp = 0

content_nbsp = 0

other_content = 0

# Count how many lines match the subtext and bold text pattern

bold_hits = 0

sub_hits = 0


for i, line in enumerate(lines):

    mline = line.replace('\u00A0', ' ')

    # Precompute booleans first, to make code more readable
    is_empty = len(line) == 0
    is_ws_only = line.strip() == ""
    has_nbsp = "\u00A0" in line


    sub_match = sub_text.search(mline)
    match = bold_text.search(mline)

    if sub_match:

        record = {
            "line_no": i + 1,
            "pattern_type": "bold_label_phrase",
            "raw_line": line,
            "match0": sub_match.group(0),
            "groups": sub_match.groups(),
            "span": sub_match.span()
        }
        sub_hits += 1
        matches.append(record)
        print(f"String matches the regex pattern: {record}")



    elif match:
        record = {
            "line_no": i + 1,
            "pattern_type": "any_bold_span",
            "raw_line": line,
            "match0": match.group(0),
            "groups": match.groups(),
            "span": match.span()
        }
        bold_hits += 1
        matches.append(record)
        print(f"String matches the regex pattern: {record}")


    else:
        print("String does not match regex pattern")

    if is_empty:
        empty += 1


    elif is_ws_only and has_nbsp:
        whitespace_nbsp += 1
        print("Line contains whitespace and NBSP:", repr(line))

    elif is_ws_only:
        whitespace_only += 1
        print("Lines contains whitespace only")



    elif has_nbsp:
        content_nbsp += 1
        print("Line contains NBSP:", repr(line))

    else:
        other_content += 1
        print("Line contains other content")



counts = Counter({'empty': empty, 'whitespace_nbsp': whitespace_nbsp, 'whitespace_only': whitespace_only, 'content_nbsp': content_nbsp, 'other_content': other_content})

print(counts)

# Sanity check
total_lines = len(lines)
bucket_sum = empty + whitespace_only + whitespace_nbsp + content_nbsp + other_content

print(f"Total lines: {total_lines}")
print(f"Sum of buckets: {bucket_sum}")

if total_lines != bucket_sum:
    print("Warning! Buckets don't add up correctly.")

print(f"Sub text pattern matches: {sub_hits}")
print(f"Bold text pattern matches: {bold_hits}")
print(f"Non-matching lines: {total_lines - (sub_hits + bold_hits)}")

