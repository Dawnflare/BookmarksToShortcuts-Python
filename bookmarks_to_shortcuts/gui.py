"""Simple Tkinter GUI for exporting Brave bookmarks on Windows."""
from __future__ import annotations

import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Dict, Iterable, List, Optional

from .exporter import BookmarkExporter, DuplicateStrategy, StructureMode
from .model import BookmarkNode
from .raw import RawBookmarkFile
from .tree import BookmarkTreeBuilder


@dataclass
class ExportContext:
    exporter: BookmarkExporter
    nodes: list
    base_output: Path
    timestamp_suffix: str


class BookmarkExporterGUI(tk.Tk):
    """Lightweight window that wraps the CLI behavior in Tkinter widgets."""

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
        self.structure_mode_var = tk.StringVar(value=StructureMode.PRESERVE.label)
        self.export_shortcuts_var = tk.BooleanVar(value=True)
        self.export_html_var = tk.BooleanVar(value=False)
        self.export_text_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="Select your Bookmarks file and destination.")

        self._tree_roots: List[BookmarkNode] = []
        self._folder_selection: Dict[str, bool] = {}
        self._node_lookup: Dict[str, BookmarkNode] = {}
        self._node_to_item: Dict[str, str] = {}
        self._item_to_node: Dict[str, str] = {}
        self._checkbox_images: Dict[str, tk.PhotoImage] = {}
        self.folder_tree: Optional[ttk.Treeview] = None

        self._build_layout()
        self._load_folder_tree(initial=True)

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
        ttk.Label(frame, text="Destination folder for exports:").grid(
            column=0, row=2, sticky="w"
        )
        output_entry = ttk.Entry(frame, textvariable=self.output_var, width=50)
        output_entry.grid(column=0, row=3, sticky="we", **padding)
        ttk.Button(frame, text="Browse…", command=self._choose_output).grid(
            column=1, row=3, **padding
        )

        # Options
        options_frame = ttk.Frame(frame)
        options_frame.grid(column=0, row=4, columnspan=2, sticky="we", **padding)
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

        ttk.Label(options_frame, text="Bookmark layout:").grid(column=0, row=3, sticky="w", pady=(10, 0))
        structure_combo = ttk.Combobox(
            options_frame,
            textvariable=self.structure_mode_var,
            values=[mode.label for mode in StructureMode],
            state="readonly",
            width=32,
        )
        structure_combo.grid(column=0, row=4, sticky="w")
        structure_combo.current(0)

        self._build_folder_explorer(frame, start_row=5, padding=padding)

        export_frame = ttk.LabelFrame(frame, text="Export formats")
        export_frame.grid(column=0, row=8, columnspan=2, sticky="we", **padding)
        ttk.Checkbutton(
            export_frame, text="Export Shortcuts", variable=self.export_shortcuts_var
        ).grid(column=0, row=0, sticky="w", padx=5, pady=2)
        ttk.Checkbutton(
            export_frame, text="Export as HTML", variable=self.export_html_var
        ).grid(column=0, row=1, sticky="w", padx=5, pady=2)
        ttk.Checkbutton(
            export_frame, text="Export as text document", variable=self.export_text_var
        ).grid(column=0, row=2, sticky="w", padx=5, pady=2)

        ttk.Button(frame, text="Export", command=self._export_selected).grid(
            column=0, row=9, columnspan=2, sticky="we", **padding
        )

        status_label = ttk.Label(frame, textvariable=self.status_var, foreground="#555555")
        status_label.grid(column=0, row=10, columnspan=2, sticky="w", pady=(0, 5))

    def _build_folder_explorer(self, parent: ttk.Frame, start_row: int, padding: dict) -> None:
        if not self._checkbox_images:
            self._create_checkbox_images()

        explorer = ttk.LabelFrame(parent, text="Folders to include in export")
        explorer.grid(column=0, row=start_row, columnspan=2, sticky="nsew", **padding)
        explorer.columnconfigure(0, weight=1)
        explorer.rowconfigure(0, weight=1)

        tree = ttk.Treeview(explorer, show="tree", selectmode="none", height=30)
        tree.grid(column=0, row=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(explorer, orient="vertical", command=tree.yview)
        scrollbar.grid(column=1, row=0, sticky="ns")
        tree.configure(yscrollcommand=scrollbar.set)
        tree.tag_configure("placeholder", foreground="#666666")
        tree.bind("<Button-1>", self._on_tree_click)

        self.folder_tree = tree

        ttk.Button(explorer, text="Refresh folders", command=self._load_folder_tree).grid(
            column=0, row=1, sticky="w", pady=(6, 0)
        )

        self._show_tree_placeholder("Load a Brave Bookmarks file to preview folders.")

    def _create_checkbox_images(self) -> None:
        if self._checkbox_images:
            return

        def draw_box(mark: str | None) -> tk.PhotoImage:
            size = 14
            img = tk.PhotoImage(width=size, height=size)
            bg = "#ffffff"
            border = "#4a4a4a"
            img.put(bg, to=(0, 0, size, size))
            for idx in range(size):
                img.put(border, to=(idx, 0))
                img.put(border, to=(idx, size - 1))
                img.put(border, to=(0, idx))
                img.put(border, to=(size - 1, idx))
            if mark == "check":
                color = "#1d6f42"
                points = [
                    (3, 7),
                    (4, 8),
                    (5, 9),
                    (6, 8),
                    (7, 7),
                    (8, 6),
                    (9, 5),
                    (10, 4),
                ]
                for x, y in points:
                    img.put(color, to=(x, y))
                    img.put(color, to=(x, y - 1))
            elif mark == "mixed":
                img.put("#1d6f42", to=(3, 6, size - 3, 8))
            return img

        self._checkbox_images["checked"] = draw_box("check")
        self._checkbox_images["unchecked"] = draw_box(None)
        self._checkbox_images["mixed"] = draw_box("mixed")

    def _show_tree_placeholder(self, message: str) -> None:
        if not self.folder_tree:
            return
        self.folder_tree.delete(*self.folder_tree.get_children())
        self.folder_tree.insert("", "end", text=message, tags=("placeholder",))
        self._tree_roots = []
        self._node_lookup.clear()
        self._node_to_item.clear()
        self._item_to_node.clear()

    def _on_tree_click(self, event):  # pragma: no cover - GUI-only
        if not self.folder_tree:
            return
        item_id = self.folder_tree.identify_row(event.y)
        element = self.folder_tree.identify("element", event.x, event.y)
        if element != "image":
            return
        if not item_id:
            return
        if self.folder_tree.tag_has("placeholder", item_id):
            return
        node_id = self._item_to_node.get(item_id)
        if not node_id:
            return
        new_value = not self._folder_selection.get(node_id, True)
        self._apply_folder_state(node_id, new_value)
        self._refresh_checkbox_icons()
        return "break"

    def _apply_folder_state(self, node_id: str, value: bool) -> None:
        node = self._node_lookup.get(node_id)
        if node is None:
            return
        self._folder_selection[node_id] = value
        for child in node.children:
            if child.is_folder:
                self._apply_folder_state(child.id, value)

    def _refresh_checkbox_icons(self) -> None:
        for node in self._tree_roots:
            if node.is_folder:
                self._update_branch_icon(node)

    def _update_branch_icon(self, node: BookmarkNode) -> str:
        child_states: List[str] = []
        for child in node.children:
            if child.is_folder:
                child_states.append(self._update_branch_icon(child))
        current_state = "checked" if self._folder_selection.get(node.id, True) else "unchecked"
        if child_states:
            if all(state == "checked" for state in child_states) and current_state == "checked":
                display = "checked"
            elif all(state == "unchecked" for state in child_states) and current_state == "unchecked":
                display = "unchecked"
            else:
                display = "mixed"
        else:
            display = current_state
        item_id = self._node_to_item.get(node.id)
        if item_id and self.folder_tree is not None:
            image = self._checkbox_images.get(display)
            if image is not None:
                self.folder_tree.item(item_id, image=image)
        return display

    def _iter_folder_nodes(self, nodes: Iterable[BookmarkNode]) -> Iterable[BookmarkNode]:
        for node in nodes:
            if not node.is_folder:
                continue
            yield node
            yield from self._iter_folder_nodes(node.children)

    def _load_folder_tree(self, initial: bool = False, *, silent: bool = False) -> None:
        if not self.folder_tree:
            return
        bookmarks_path = Path(self.bookmarks_var.get()).expanduser()
        if not bookmarks_path.exists():
            self._show_tree_placeholder("Select a valid Bookmarks file to choose folders.")
            if not (initial or silent):
                messagebox.showerror(
                    "Bookmarks file missing",
                    "Please pick a valid Brave Bookmarks file.",
                )
            return
        try:
            raw = RawBookmarkFile.load(bookmarks_path)
            tree = BookmarkTreeBuilder(raw)
            nodes = tree.build()
        except Exception as exc:  # pragma: no cover - GUI-only
            self._show_tree_placeholder("Unable to load folders from the selected file.")
            if not (initial or silent):
                messagebox.showerror("Failed to load bookmarks", str(exc))
            return

        self._tree_roots = nodes
        lookup = {node.id: node for node in self._iter_folder_nodes(nodes)}
        self._node_lookup = lookup
        new_selection: Dict[str, bool] = {}
        for node_id in lookup:
            new_selection[node_id] = self._folder_selection.get(node_id, True)
        self._folder_selection = new_selection
        self._populate_folder_tree(nodes)

    def _populate_folder_tree(self, nodes: List[BookmarkNode]) -> None:
        if not self.folder_tree:
            return
        self.folder_tree.delete(*self.folder_tree.get_children())
        self._node_to_item.clear()
        self._item_to_node.clear()
        inserted = False
        for node in nodes:
            if not node.is_folder:
                continue
            self._insert_tree_node("", node)
            inserted = True
        if not inserted:
            self._show_tree_placeholder("No folders found in the selected file.")
        else:
            self._refresh_checkbox_icons()

    def _insert_tree_node(self, parent_item: str, node: BookmarkNode) -> None:
        if not self.folder_tree:
            return
        display_name = node.name or "(Unnamed folder)"
        image = self._checkbox_images.get("checked")
        item_id = self.folder_tree.insert(parent_item, "end", text=display_name, open=True, image=image)
        self._node_to_item[node.id] = item_id
        self._item_to_node[item_id] = node.id
        for child in node.children:
            if child.is_folder:
                self._insert_tree_node(item_id, child)

    def _filter_nodes_for_export(self, nodes: List[BookmarkNode]) -> List[BookmarkNode]:
        filtered: List[BookmarkNode] = []
        for node in nodes:
            clone = self._clone_node(node)
            if clone is not None:
                filtered.append(clone)
        return filtered

    def _clone_node(self, node: BookmarkNode) -> Optional[BookmarkNode]:
        folder_selected = not node.is_folder or self._folder_selection.get(node.id, True)
        clone = BookmarkNode(id=node.id, name=node.name, type=node.type, url=node.url)
        for child in node.children:
            if child.is_folder:
                child_clone = self._clone_node(child)
                if child_clone is not None:
                    clone.add_child(child_clone)
            elif folder_selected:
                # Only include direct bookmarks when the folder itself is selected
                bookmark = BookmarkNode(
                    id=child.id,
                    name=child.name,
                    type=child.type,
                    url=child.url,
                )
                clone.add_child(bookmark)
        # Include this folder if it's selected, or if it has any surviving children
        # (i.e., a descendant folder was selected even though this one wasn't)
        if not folder_selected and not clone.children:
            return None
        return clone

    def _choose_bookmarks(self) -> None:
        path = filedialog.askopenfilename(title="Select Brave Bookmarks file", filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
        if path:
            self.bookmarks_var.set(path)
            self._load_folder_tree()

    def _choose_output(self) -> None:
        path = filedialog.askdirectory(title="Select destination folder")
        if path:
            self.output_var.set(path)

    def _export_selected(self) -> None:
        do_shortcuts = self.export_shortcuts_var.get()
        do_html = self.export_html_var.get()
        do_text = self.export_text_var.get()

        if not (do_shortcuts or do_html or do_text):
            messagebox.showwarning(
                "No export format selected",
                "Please select at least one export format before exporting.",
            )
            return

        context = self._prepare_export_context(create_destination=do_shortcuts)
        if context is None:
            return

        exporter = context.exporter
        nodes = context.nodes
        messages: List[str] = []
        errors: List[str] = []

        def run_shortcuts():
            result = exporter.export(nodes)
            return f"Created {len(result.created_files)} shortcuts; skipped {len(result.skipped)}"

        def run_html():
            html_path = context.base_output / f"{context.timestamp_suffix}_Bookmarks.html"
            count = exporter.export_html(nodes, html_path)
            return f"Exported {count} bookmarks to {html_path.name}"

        def run_text():
            text_path = context.base_output / f"{context.timestamp_suffix}_Bookmarks.txt"
            count = exporter.export_text(nodes, text_path)
            return f"Exported {count} bookmarks to {text_path.name}"

        tasks = []
        if do_shortcuts:
            tasks.append(("Shortcuts", run_shortcuts))
        if do_html:
            tasks.append(("HTML", run_html))
        if do_text:
            tasks.append(("Text", run_text))

        with ThreadPoolExecutor(max_workers=len(tasks)) as pool:
            futures = {pool.submit(fn): label for label, fn in tasks}
            for future in as_completed(futures):
                label = futures[future]
                try:
                    messages.append(future.result())
                except Exception as exc:
                    errors.append(f"{label}: {exc}")

        if errors:
            messagebox.showerror("Export failed", "\n".join(errors))
            self.status_var.set("Export failed. See error message above.")
        else:
            self.status_var.set("; ".join(messages))

    def _export(self) -> None:
        context = self._prepare_export_context(create_destination=True)
        if context is None:
            return

        exporter = context.exporter
        nodes = context.nodes
        try:
            result = exporter.export(nodes)
        except Exception as exc:  # pragma: no cover - GUI-only
            messagebox.showerror("Export failed", str(exc))
            self.status_var.set("Export failed. See error message above.")
            return

        message = f"Created {len(result.created_files)} shortcuts; skipped {len(result.skipped)}"
        self.status_var.set(message)

    def _export_html(self) -> None:
        context = self._prepare_export_context(create_destination=False)
        if context is None:
            return

        exporter = context.exporter
        nodes = context.nodes
        html_path = context.base_output / f"{context.timestamp_suffix}_Bookmarks.html"
        try:
            count = exporter.export_html(nodes, html_path)
        except Exception as exc:  # pragma: no cover - GUI-only
            messagebox.showerror("Export failed", str(exc))
            self.status_var.set("Export failed. See error message above.")
            return

        message = f"Exported {count} bookmarks to {html_path.name}"
        self.status_var.set(message)

    def _export_text(self) -> None:
        context = self._prepare_export_context(create_destination=False)
        if context is None:
            return

        exporter = context.exporter
        nodes = context.nodes
        text_path = context.base_output / f"{context.timestamp_suffix}_Bookmarks.txt"
        try:
            count = exporter.export_text(nodes, text_path)
        except Exception as exc:  # pragma: no cover - GUI-only
            messagebox.showerror("Export failed", str(exc))
            self.status_var.set("Export failed. See error message above.")
            return

        message = f"Exported {count} bookmarks to {text_path.name}"
        self.status_var.set(message)

    def _prepare_export_context(self, create_destination: bool):
        bookmarks_path = Path(self.bookmarks_var.get()).expanduser()
        output_path = Path(self.output_var.get()).expanduser()

        if not bookmarks_path.exists():
            messagebox.showerror("Invalid path", "Please select a valid Brave Bookmarks file.")
            return None
        if not output_path.exists():
            try:
                output_path.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                messagebox.showerror("Invalid destination", str(exc))
                return None

        try:
            raw = RawBookmarkFile.load(bookmarks_path)
            tree = BookmarkTreeBuilder(raw)
            nodes = tree.build()
        except Exception as exc:  # pragma: no cover - GUI-only
            messagebox.showerror("Export failed", str(exc))
            self.status_var.set("Export failed. See error message above.")
            return None

        filtered_nodes = self._filter_nodes_for_export(nodes)
        if not filtered_nodes:
            messagebox.showwarning(
                "No folders selected",
                "Please select at least one folder in the folder explorer before exporting.",
            )
            return None

        try:
            if create_destination:
                destination, timestamp_suffix = self._create_destination_folder(output_path)
            else:
                destination = output_path
                timestamp_suffix = self._next_timestamp_suffix(output_path)
        except OSError as exc:
            messagebox.showerror("Invalid destination", str(exc))
            return None

        exporter = BookmarkExporter(
            output_root=destination,
            include_full_path=self.include_full_path_var.get(),
            duplicate_strategy=DuplicateStrategy(self.duplicate_strategy_var.get()),
            structure_mode=StructureMode.from_label(self.structure_mode_var.get()),
        )
        return ExportContext(
            exporter=exporter,
            nodes=filtered_nodes,
            base_output=output_path,
            timestamp_suffix=timestamp_suffix,
        )

    def _create_destination_folder(self, base_path: Path) -> tuple[Path, str]:
        """Create a timestamped folder for the current export session."""

        candidate, label = self._next_destination_folder(base_path)
        candidate.mkdir(parents=True, exist_ok=False)
        return candidate, label

    def _next_timestamp_suffix(self, base_path: Path) -> str:
        """Generate a timestamp label unique among exported files."""

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        suffix = timestamp
        counter = 2
        while any(
            (base_path / f"{suffix}_Bookmarks{extension}").exists()
            for extension in (".html", ".txt")
        ):
            suffix = f"{timestamp}_{counter}"
            counter += 1
        return suffix

    def _next_destination_folder(self, base_path: Path) -> tuple[Path, str]:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        base_name = f"{timestamp}_Bookmarks"
        candidate = base_path / base_name
        suffix = 2
        while candidate.exists():
            candidate = base_path / f"{base_name}_{suffix}"
            suffix += 1
        label = (
            candidate.name.replace("_Bookmarks", "", 1)
            if "_Bookmarks" in candidate.name
            else candidate.name
        )
        return candidate, label


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
