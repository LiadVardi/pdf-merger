import os
from tkinter import messagebox

import utils  # ensures pypdf is installed
from pypdf import PdfWriter, PdfReader


def validate_pdfs(paths):
    invalid = [p for p in paths if not p.lower().endswith(".pdf")]
    if invalid:
        messagebox.showerror(
            "Invalid Files",
            "The following files are not PDFs:\n" + "\n".join(invalid),
        )
        return False
    return True


def merge_pdfs(paths, output_path):
    writer = PdfWriter()
    for path in paths:
        for page in PdfReader(path).pages:
            writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)
    writer.close()
