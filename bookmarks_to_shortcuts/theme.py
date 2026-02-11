"""Dark and light theme definitions for the Tkinter GUI."""
from __future__ import annotations

from dataclasses import dataclass
from tkinter import ttk
import tkinter as tk


@dataclass(frozen=True)
class ThemeColors:
    """Color palette for a single theme."""

    bg: str
    fg: str
    entry_bg: str
    entry_fg: str
    button_bg: str
    button_fg: str
    select_bg: str
    select_fg: str
    tree_bg: str
    tree_fg: str
    border: str
    warning: str
    status_fg: str
    checkbox_bg: str
    checkbox_border: str
    checkbox_check: str


DARK = ThemeColors(
    bg="#2b2b2b",
    fg="#e0e0e0",
    entry_bg="#3c3c3c",
    entry_fg="#e0e0e0",
    button_bg="#404040",
    button_fg="#e0e0e0",
    select_bg="#4a6fa5",
    select_fg="#ffffff",
    tree_bg="#333333",
    tree_fg="#e0e0e0",
    border="#555555",
    warning="#ff9933",
    status_fg="#aaaaaa",
    checkbox_bg="#3c3c3c",
    checkbox_border="#888888",
    checkbox_check="#5cb85c",
)

LIGHT = ThemeColors(
    bg="#f0f0f0",
    fg="#1a1a1a",
    entry_bg="#ffffff",
    entry_fg="#1a1a1a",
    button_bg="#e0e0e0",
    button_fg="#1a1a1a",
    select_bg="#0078d4",
    select_fg="#ffffff",
    tree_bg="#ffffff",
    tree_fg="#1a1a1a",
    border="#cccccc",
    warning="#cc6600",
    status_fg="#555555",
    checkbox_bg="#ffffff",
    checkbox_border="#4a4a4a",
    checkbox_check="#1d6f42",
)

THEMES = {"dark": DARK, "light": LIGHT}


def apply_theme(root: tk.Tk, colors: ThemeColors) -> None:
    """Apply the given color palette to all ttk widgets and the root window."""
    style = ttk.Style(root)
    style.theme_use("clam")

    # Root window
    root.configure(bg=colors.bg)

    # TFrame
    style.configure("TFrame", background=colors.bg)

    # TLabel
    style.configure("TLabel", background=colors.bg, foreground=colors.fg)

    # TButton
    style.configure(
        "TButton",
        background=colors.button_bg,
        foreground=colors.button_fg,
        bordercolor=colors.border,
    )
    style.map(
        "TButton",
        background=[("active", colors.select_bg)],
        foreground=[("active", colors.select_fg)],
    )

    # TCheckbutton
    style.configure(
        "TCheckbutton",
        background=colors.bg,
        foreground=colors.fg,
        indicatorbackground=colors.entry_bg,
        indicatorforeground=colors.checkbox_check,
    )
    style.map(
        "TCheckbutton",
        background=[("active", colors.bg)],
    )

    # TEntry
    style.configure(
        "TEntry",
        fieldbackground=colors.entry_bg,
        foreground=colors.entry_fg,
        bordercolor=colors.border,
    )

    # TCombobox
    style.configure(
        "TCombobox",
        fieldbackground=colors.entry_bg,
        foreground=colors.entry_fg,
        background=colors.button_bg,
        bordercolor=colors.border,
        arrowcolor=colors.fg,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", colors.entry_bg)],
        foreground=[("readonly", colors.entry_fg)],
    )

    # TLabelframe
    style.configure(
        "TLabelframe",
        background=colors.bg,
        foreground=colors.fg,
        bordercolor=colors.border,
    )
    style.configure("TLabelframe.Label", background=colors.bg, foreground=colors.fg)

    # Treeview
    style.configure(
        "Treeview",
        background=colors.tree_bg,
        foreground=colors.tree_fg,
        fieldbackground=colors.tree_bg,
        bordercolor=colors.border,
    )
    style.map(
        "Treeview",
        background=[("selected", colors.select_bg)],
        foreground=[("selected", colors.select_fg)],
    )

    # Scrollbar
    style.configure(
        "Vertical.TScrollbar",
        background=colors.button_bg,
        troughcolor=colors.bg,
        bordercolor=colors.border,
        arrowcolor=colors.fg,
    )

    # Warning label style
    style.configure("Warning.TLabel", background=colors.bg, foreground=colors.warning)
