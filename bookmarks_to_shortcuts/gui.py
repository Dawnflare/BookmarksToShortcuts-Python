"""Simple Tkinter GUI for exporting Brave bookmarks on Windows."""
from __future__ import annotations

import os
import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .exporter import BookmarkExporter, DuplicateStrategy
from .raw import RawBookmarkFile
from .tree import BookmarkTreeBuilder


class BookmarkExporterGUI(tk.Tk):
    """Lightweight window that wraps the CLI behavior in Tkinter widgets."""

    ROOT_KEYS = ("bookmark_bar", "other", "synced", "mobile")
    DEFAULT_BOOKMARKS_PATH = Path(
        os.environ.get("USERPROFILE", str(Path.home()))
    ) / "AppData" / "Local" / "BraveSoftware" / "Brave-Browser" / "User Data" / "Default" / "Bookmarks"
    DEFAULT_OUTPUT_PATH = Path("F:/Temp")

    def __init__(self) -> None:
        super().__init__()
        self.title("Bookmarks to Shortcuts")
        self.resizable(False, False)

        self.bookmarks_var = tk.StringVar(value=str(self.DEFAULT_BOOKMARKS_PATH))
        self.output_var = tk.StringVar(value=str(self.DEFAULT_OUTPUT_PATH))
        self.include_full_path_var = tk.BooleanVar(value=False)
        self.duplicate_strategy_var = tk.StringVar(value=DuplicateStrategy.UNIQUE.value)
        self.root_vars = {key: tk.BooleanVar(value=True) for key in self.ROOT_KEYS}
        self.status_var = tk.StringVar(value="Select your Bookmarks file and destination.")

        self._build_layout()

    def _build_layout(self) -> None:
        padding = dict(padx=10, pady=5)
        frame = ttk.Frame(self, padding=10)
        frame.grid(column=0, row=0, sticky="nsew")

        # Bookmarks file input
        ttk.Label(frame, text="Brave Bookmarks file:").grid(column=0, row=0, sticky="w")
        bookmarks_entry = ttk.Entry(frame, textvariable=self.bookmarks_var, width=50)
        bookmarks_entry.grid(column=0, row=1, sticky="we", **padding)
        ttk.Button(frame, text="Browse…", command=self._choose_bookmarks).grid(
            column=1, row=1, **padding
        )

        # Output directory input
        ttk.Label(frame, text="Destination folder for shortcuts:").grid(
            column=0, row=2, sticky="w"
        )
        output_entry = ttk.Entry(frame, textvariable=self.output_var, width=50)
        output_entry.grid(column=0, row=3, sticky="we", **padding)
        ttk.Button(frame, text="Browse…", command=self._choose_output).grid(
            column=1, row=3, **padding
        )

        # Include roots section
        roots_frame = ttk.LabelFrame(frame, text="Roots to export")
        roots_frame.grid(column=0, row=4, columnspan=2, sticky="we", **padding)
        for idx, key in enumerate(self.ROOT_KEYS):
            ttk.Checkbutton(
                roots_frame,
                text=key.replace("_", " ").title(),
                variable=self.root_vars[key],
            ).grid(column=idx % 2, row=idx // 2, sticky="w", padx=6, pady=3)

        # Options
        options_frame = ttk.Frame(frame)
        options_frame.grid(column=0, row=5, columnspan=2, sticky="we", **padding)
        ttk.Checkbutton(
            options_frame,
            text="Include root name in exported paths",
            variable=self.include_full_path_var,
        ).grid(column=0, row=0, sticky="w")

        ttk.Label(options_frame, text="Duplicate handling:").grid(column=0, row=1, sticky="w", pady=(10, 0))
        duplicate_combo = ttk.Combobox(
            options_frame,
            textvariable=self.duplicate_strategy_var,
            values=[d.value for d in DuplicateStrategy],
            state="readonly",
            width=12,
        )
        duplicate_combo.grid(column=0, row=2, sticky="w")
        duplicate_combo.current(0)

        ttk.Button(frame, text="Export Shortcuts", command=self._export).grid(
            column=0, row=6, columnspan=2, sticky="we", **padding
        )

        status_label = ttk.Label(frame, textvariable=self.status_var, foreground="#555555")
        status_label.grid(column=0, row=7, columnspan=2, sticky="w", pady=(0, 5))

    def _choose_bookmarks(self) -> None:
        path = filedialog.askopenfilename(title="Select Brave Bookmarks file", filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
        if path:
            self.bookmarks_var.set(path)

    def _choose_output(self) -> None:
        path = filedialog.askdirectory(title="Select destination folder")
        if path:
            self.output_var.set(path)

    def _export(self) -> None:
        bookmarks_path = Path(self.bookmarks_var.get()).expanduser()
        output_path = Path(self.output_var.get()).expanduser()

        if not bookmarks_path.exists():
            messagebox.showerror("Invalid path", "Please select a valid Brave Bookmarks file.")
            return
        if not output_path.exists():
            try:
                output_path.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                messagebox.showerror("Invalid destination", str(exc))
                return

        include_roots = [name for name, var in self.root_vars.items() if var.get()]
        include_roots = include_roots or None

        try:
            raw = RawBookmarkFile.load(bookmarks_path)
            tree = BookmarkTreeBuilder(raw)
            nodes = tree.build(include_roots=include_roots)
            exporter = BookmarkExporter(
                output_root=output_path,
                include_full_path=self.include_full_path_var.get(),
                duplicate_strategy=DuplicateStrategy(self.duplicate_strategy_var.get()),
            )
            result = exporter.export(nodes)
        except Exception as exc:  # pragma: no cover - GUI-only
            messagebox.showerror("Export failed", str(exc))
            self.status_var.set("Export failed. See error message above.")
            return

        message = f"Created {len(result.created_files)} shortcuts; skipped {len(result.skipped)}"
        self.status_var.set(message)
        messagebox.showinfo("Export finished", message)


def hide_console_window() -> None:
    """Hide the console window on Windows after the GUI launches."""

    if not sys.platform.startswith("win"):
        return

    try:
        import ctypes

        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
    except Exception:
        # Failing to hide the console shouldn't break the GUI.
        pass


def main() -> None:
    hide_console_window()
    app = BookmarkExporterGUI()
    app.mainloop()


if __name__ == "__main__":  # pragma: no cover - GUI-only
    main()
