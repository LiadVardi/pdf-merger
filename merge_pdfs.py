import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox


def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Install Error", f"Failed to install {package}:\n{e}")
        sys.exit(1)


try:
    from pypdf import PdfWriter, PdfReader
except ImportError:
    install_package("pypdf")
    from pypdf import PdfWriter, PdfReader


def pick_files():
    root = tk.Tk()
    root.withdraw()
    paths = filedialog.askopenfilenames(
        title="Select PDF files to merge",
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
    )
    root.destroy()
    return list(paths)


def validate_pdfs(paths):
    invalid = [p for p in paths if not p.lower().endswith(".pdf")]
    if invalid:
        messagebox.showerror(
            "Invalid Files",
            "The following files are not PDFs:\n" + "\n".join(invalid),
        )
        return False
    return True


class ReorderWindow:
    def __init__(self, paths):
        self.paths = list(paths)
        self.confirmed = False

        self.root = tk.Tk()
        self.root.title("Set Merge Order")
        self.root.resizable(False, False)

        tk.Label(self.root, text="Use Up / Down to set the merge order, then click Merge.",
                 padx=10, pady=8).pack()

        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=4)

        self.listbox = tk.Listbox(frame, selectmode=tk.SINGLE, width=60, height=12)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH)

        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        self._refresh()
        self.listbox.selection_set(0)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=6)

        tk.Button(btn_frame, text="Up",   width=8, command=self._move_up).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text="Down", width=8, command=self._move_down).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text="Merge", width=10, command=self._merge,
                  bg="#2d7d46", fg="white").pack(side=tk.LEFT, padx=12)

        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.root.mainloop()

    def _refresh(self):
        self.listbox.delete(0, tk.END)
        for p in self.paths:
            self.listbox.insert(tk.END, os.path.basename(p))

    def _selected(self):
        sel = self.listbox.curselection()
        return sel[0] if sel else None

    def _move_up(self):
        idx = self._selected()
        if idx is None or idx == 0:
            return
        self.paths[idx - 1], self.paths[idx] = self.paths[idx], self.paths[idx - 1]
        self._refresh()
        self.listbox.selection_set(idx - 1)

    def _move_down(self):
        idx = self._selected()
        if idx is None or idx == len(self.paths) - 1:
            return
        self.paths[idx + 1], self.paths[idx] = self.paths[idx], self.paths[idx + 1]
        self._refresh()
        self.listbox.selection_set(idx + 1)

    def _merge(self):
        self.confirmed = True
        self.root.destroy()


def merge_pdfs(paths):
    output_dir = os.path.dirname(paths[0])
    output_path = os.path.join(output_dir, "Combined_file.pdf")

    writer = PdfWriter()
    for path in paths:
        reader = PdfReader(path)
        for page in reader.pages:
            writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)

    writer.close()
    return output_path


def main():
    paths = pick_files()

    if not paths:
        return

    if not validate_pdfs(paths):
        return

    window = ReorderWindow(paths)

    if not window.confirmed:
        return

    try:
        output_path = merge_pdfs(window.paths)
        messagebox.showinfo("Success", f"PDFs merged successfully!\n\nSaved to:\n{output_path}")
    except Exception as e:
        messagebox.showerror("Merge Error", f"An error occurred during merging:\n{e}")


if __name__ == "__main__":
    main()
