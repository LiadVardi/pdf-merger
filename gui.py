import os
import tkinter as tk
from tkinter import filedialog, messagebox

import utils  # ensures customtkinter is installed
import customtkinter as ctk

from merger import validate_pdfs, merge_pdfs

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


class ReorderWindow:
    def __init__(self, paths):
        self.paths = list(paths)
        self.confirmed = False
        self.go_back = False
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

        ctk.CTkButton(btn_frame, text="Back", width=90, fg_color="grey", hover_color="#555555", command=self._back).pack(side="left", padx=6)
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

    def _back(self):
        self.go_back = True
        self.root.destroy()

    def _merge(self):
        self.confirmed = True
        self.root.destroy()


def pick_output_path(first_input_path):
    root = tk.Tk()
    root.withdraw()
    path = filedialog.asksaveasfilename(
        title="Save merged PDF as",
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        initialfile="Combined_file.pdf",
        initialdir=os.path.dirname(first_input_path),
    )
    root.destroy()
    return path


class SplashScreen:
    def __init__(self):
        root = ctk.CTk()
        root.overrideredirect(True)

        w, h = 380, 220
        x = (root.winfo_screenwidth()  - w) // 2
        y = (root.winfo_screenheight() - h) // 2
        root.geometry(f"{w}x{h}+{x}+{y}")

        ctk.CTkLabel(
            root, text="PDF Merger",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).place(relx=0.5, rely=0.38, anchor="center")

        ctk.CTkLabel(
            root, text="Merge your PDFs easily",
            font=ctk.CTkFont(size=14),
            text_color="gray",
        ).place(relx=0.5, rely=0.58, anchor="center")

        ctk.CTkLabel(
            root, text="v1.0",
            font=ctk.CTkFont(size=11),
            text_color="gray",
        ).place(relx=0.96, rely=0.92, anchor="se")

        root.after(2500, root.destroy)
        root.mainloop()


class SuccessDialog(ctk.CTkToplevel):
    def __init__(self, output_path):
        _root = tk.Tk()
        _root.withdraw()

        super().__init__(_root)
        self.title("Success")
        self.resizable(False, False)

        ctk.CTkLabel(
            self, text="✓",
            font=ctk.CTkFont(size=52, weight="bold"),
            text_color="#2d7d46",
        ).pack(pady=(28, 4))

        ctk.CTkLabel(
            self, text="PDFs merged successfully!",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack()

        ctk.CTkLabel(
            self, text=output_path,
            font=ctk.CTkFont(size=13),
            text_color="gray",
            wraplength=340,
        ).pack(pady=(8, 20), padx=24)

        ctk.CTkButton(self, text="OK", width=100, command=self.destroy).pack(pady=(0, 28))

        self.update_idletasks()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")

        self.grab_set()
        _root.wait_window(self)
        _root.destroy()


def main():
    while True:
        paths = pick_files()

        if not paths:
            return

        if not validate_pdfs(paths):
            return

        window = ReorderWindow(paths)

        if window.go_back:
            continue

        if not window.confirmed:
            return

        break

    output_path = pick_output_path(window.paths[0])
    if not output_path:
        return

    try:
        merge_pdfs(window.paths, output_path)
        SuccessDialog(output_path)
    except Exception as e:
        messagebox.showerror("Merge Error", f"An error occurred during merging:\n{e}")
