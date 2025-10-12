# Load the PyMuPDF library
import fitz
# Load the PyMuPDF4LLM library
import pymupdf4llm
# Load Pathlib library
import pathlib as path

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
doc.save('storage/cleaned/redacted_v2.pdf', garbage=4, deflate=True)

# Close PDF
doc.close()
          
            
md_text = pymupdf4llm.to_markdown('storage/cleaned/redacted_v2.pdf')
          
md_path = path.Path('storage/cleaned/redacted.md')

   

bytes_written = md_path.write_text(md_text, encoding="utf-8", newline="\n")

print("Markdown saved to redacted.md")

       
       

        
        






