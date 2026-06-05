import os

import utils  # ensures pypdf is installed
from pypdf import PdfWriter, PdfReader


def validate_pdfs(paths):
    """Return a list of invalid paths. Empty list means all files are valid."""
    return [p for p in paths if not p.lower().endswith(".pdf")]


def merge_pdfs(paths, output_path):
    writer = PdfWriter()
    for path in paths:
        for page in PdfReader(path).pages:
            writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)
    writer.close()
