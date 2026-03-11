# Load the PyMuPDF library
import fitz
# Load the PyMuPDF4LLM library
import pymupdf4llm
# Load Pathlib library
from pathlib import Path
# Load Shutil library
import shutil
# Load os library
import os
# Load re library
import re
# Load counter from collections
from collections import Counter
# Load text splitting library RecursiveTextSplitter from Langchain
from langchain_text_splitters import RecursiveCharacterTextSplitter
#Load hashlib to generate hash SHA256
import hashlib
# Testing Load uuid to generate doc_id
#import uuid
import json


def get_filename(pdf_path: Path) -> str:
    return pdf_path.stem


def get_doc_id(pdf_path: Path) -> str:
    with pdf_path.open("rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:12]


def prepare_pdf(pdf_path: Path, cleaned_pdf_path: Path, profile: str):

    doc = fitz.open(pdf_path)
    if profile == "rbc":
        redact_footer_header(doc)
    doc.save(cleaned_pdf_path, garbage=4, deflate=True)
    doc.close()



def redact_footer_header(doc):

    for page in doc:
        # Get the page height from the pdf
        H = page.rect.height
        x0 = page.rect.x0  # Get the left edge of pdf
        x1 = page.rect.x1 # Get the right edge of pdf


        # Calculate the header and footer band edges
        hdr_y0 = 0.04 * H   # Bottom edge of header band
        hdr_y1 = 0.09 * H   # Top edge of header band
        ftr_y0 = 0.93 * H   # Bottom edge of footer band
        ftr_y1 = 0.97 * H   # Top edge of footer band


         # Add 2pt padding to the rectangle to ensure everything is contained
        P = 2
        hdr_y0_padded = (hdr_y0 - P)
        hdr_y1_padded = (hdr_y1 + P)
        ftr_y0_padded = (ftr_y0 - P)
        ftr_y1_padded = (ftr_y1 + P)

        # Build two full width rectangles for header and footer
        header_rect = (x0, hdr_y0_padded , x1, hdr_y1_padded)
        footer_rect = (x0, ftr_y0_padded, x1, ftr_y1_padded)


         # Add redaction annotation to header and footer rectangles
        page.add_redact_annot(header_rect)
        page.add_redact_annot(footer_rect)

        # Apply redaction
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_REMOVE, graphics=fitz.PDF_REDACT_IMAGE_REMOVE,text=fitz.PDF_REDACT_TEXT_REMOVE)


def pdf_to_markdown(cleaned_pdf_path: Path, md_path: Path)-> Path:

    md_text = pymupdf4llm.to_markdown(cleaned_pdf_path)

    md_path.write_text(md_text, encoding="utf-8", newline="\n")

    return md_path

def text_splitter(md_path: Path) -> list[str]:
    # Creath Path object to show path to file
   
    with open(md_path, "r", encoding = "utf-8" ) as f:
        text = f.read()
    splitter = RecursiveCharacterTextSplitter(
# The default list of split characters is [\n\n, \n, " ", ""]
# Tries to split on them in order until the chunks are small enough
# Keep paragraphs, sentences, words together as long as possible
            separators = ["\n\n", "\n", " ", ""],
            chunk_size = 1200,
            chunk_overlap = 240,
            length_function = len,

        )
    chunks = splitter.split_text(text)
    return chunks



def get_chunk_record(chunks: list[str], doc_id: str, filename: str) -> list[dict]:

    chunk_records = []

    for i, chunk in enumerate(chunks):

            chunk_record = {
            "doc_id": doc_id,
            "chunk_id": (f"{doc_id}-{i + 1:04}"),
            "text": chunk,
            "filename": filename
        }
            chunk_records.append(chunk_record)
    return chunk_records

#next convert to json then save as jsonl

def write_jsonl(chunk_records: list[dict], json_path: Path) -> Path:
    # Create (write) a json file using json_path, encode to utf-8 to avoid errors
    with open (json_path, "w", encoding="utf-8") as json_file:
        for i, chunk_record in enumerate(chunk_records):
        # Convert to JSON string
            json_string = json.dumps(chunk_record)
            json_file.write(json_string + '\n')
        return json_path

def generate_steps(assignment_type, description):
    assignment_type = assignment_type.lower().strip()
    #Create a dictionary of assignment types
    step_templates = {
        "essay": [
        "1.Read the instructions for: {desc}",
        "2.Identify the main argument you want to make",
        "3.Create a quick outline",
        "4.Write the first paragraph"
        ],
        "coding":[
        "1.Understand what the problem '{desc}' is asking",
        "2.Identify the inputs and outputs",
        "3.Write a small pseudocode plan",
        "4.Start implementing the first function"
        ],
        "reading":[
        "1.Skim the material to understand the structure",
        "2.Focus on the sections related to '{desc}'",
        "3.Take brief notes on key ideas",
        "4.Summarize the main points"
        ],
        "other": [
        "1.Read the instructions for: {desc}",
        "2.Identify what the assignment is asking you to produce",
        "3.Break the task into smaller parts",
        "4.Start working on the first small part"
        ]

    }
    steps = []
    template = step_templates.get(assignment_type, step_templates["other"])
    for step in template:
        personalized_step = step.replace("{desc}", description)
        steps.append(personalized_step)
    return steps