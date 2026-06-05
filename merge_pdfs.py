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

try:
    import customtkinter as ctk
except ImportError:
    install_package("customtkinter")
    import customtkinter as ctk


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


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
        self.selected_idx = 0

        self.root = ctk.CTk()
        self.root.title("PDF Merger — Set Merge Order")
        self.root.resizable(False, False)

        ctk.CTkLabel(
            self.root,
            text="Select a file, then use Up / Down to reorder. Click Merge when ready.",
            font=ctk.CTkFont(size=13),
        ).pack(padx=20, pady=(16, 8))

        self.scroll_frame = ctk.CTkScrollableFrame(self.root, width=500, height=240)
        self.scroll_frame.pack(padx=20, pady=4, fill="both")

        self._refresh()

        btn_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        btn_frame.pack(pady=14)

        ctk.CTkButton(btn_frame, text="Up",   width=90, command=self._move_up).pack(side="left", padx=6)
        ctk.CTkButton(btn_frame, text="Down", width=90, command=self._move_down).pack(side="left", padx=6)
        ctk.CTkButton(
            btn_frame, text="Merge", width=110,
            fg_color="#2d7d46", hover_color="#235e34",
            command=self._merge,
        ).pack(side="left", padx=14)

        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.root.mainloop()

    def _refresh(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        for i, path in enumerate(self.paths):
            is_selected = (i == self.selected_idx)
            row = ctk.CTkFrame(
                self.scroll_frame,
                fg_color=("#c9daf8" if is_selected else "transparent"),
                corner_radius=6,
            )
            row.pack(fill="x", pady=2, padx=4)

            index_label = ctk.CTkLabel(
                row,
                text=f"{i + 1}.",
                width=28,
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="e",
            )
            index_label.pack(side="left", padx=(8, 4), pady=6)

            name_label = ctk.CTkLabel(
                row,
                text=os.path.basename(path),
                font=ctk.CTkFont(size=13),
                anchor="w",
            )
            name_label.pack(side="left", padx=(0, 8), pady=6, fill="x", expand=True)

            # Capture i in the closure
            for widget in (row, index_label, name_label):
                widget.bind("<Button-1>", lambda _, idx=i: self._select(idx))

    def _select(self, idx):
        self.selected_idx = idx
        self._refresh()

    def _move_up(self):
        idx = self.selected_idx
        if idx == 0:
            return
        self.paths[idx - 1], self.paths[idx] = self.paths[idx], self.paths[idx - 1]
        self.selected_idx = idx - 1
        self._refresh()

    def _move_down(self):
        idx = self.selected_idx
        if idx == len(self.paths) - 1:
            return
        self.paths[idx + 1], self.paths[idx] = self.paths[idx], self.paths[idx + 1]
        self.selected_idx = idx + 1
        self._refresh()

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
