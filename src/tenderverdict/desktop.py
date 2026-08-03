"""Cross-platform local desktop interface for TenderVerdict."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import stat
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

from .demo_data import demo_notices
from .models import (
    MAX_NOTICES_FILE_BYTES,
    MAX_PROFILE_FILE_BYTES,
    Profile,
    QualificationResult,
    SchemaValidationError,
    notice_collection_from_file_bytes,
    notices_from_data,
    parse_review_point,
    profile_from_dict,
    profile_from_json_bytes,
    render_notices_csv,
)
from .output import write_text_atomically
from .report import normalize_display_text
from .workflow import (
    QualificationRun,
    demo_run,
    dump_json,
    qualify_inputs,
    write_run,
)

DEMO_NOTICE_LABEL = "Bundled synthetic notices (offline)"
_TOKEN_SEPARATOR = re.compile(r"[,;\s]+")
_VERDICT_LABELS = {
    "open_documents": "Open documents",
    "watch": "Watch",
    "reject": "Reject",
}
_VERDICT_FILTERS = ("All verdicts", "Open documents", "Watch", "Reject")
_FILTER_TO_VERDICT = {
    "Open documents": "open_documents",
    "Watch": "watch",
    "Reject": "reject",
}
_VERDICT_SORT_ORDER = {"open_documents": 0, "watch": 1, "reject": 2}
_MACOS_SHORTCUT_KEYCODES = {1: "export", 2: "demo", 15: "review", 31: "open"}
_WINDOWS_SHORTCUT_KEYCODES = {68: "demo", 79: "open", 82: "review", 83: "export"}
_KEYSYM_SHORTCUTS = {
    "cyrillic_ka": "review",
    "cyrillic_shcha": "open",
    "cyrillic_ve": "demo",
    "cyrillic_yeru": "export",
    "d": "demo",
    "o": "open",
    "r": "review",
    "s": "export",
}


class DesktopUnavailableError(RuntimeError):
    """Raised when this Python installation does not include Tk."""


@dataclass(frozen=True, slots=True)
class LocalFileSnapshot:
    """One bounded local-file snapshot and its export provenance."""

    path: Path
    payload: bytes
    sha256: str


@dataclass(frozen=True, slots=True)
class DesktopPalette:
    """Semantic desktop colours for one light or dark appearance."""

    background: str
    surface: str
    surface_alt: str
    field: str
    text: str
    muted: str
    subtle: str
    border: str
    accent: str
    accent_hover: str
    accent_text: str
    focus: str
    selection: str
    selection_text: str
    success: str
    warning: str
    danger: str


def desktop_palette(is_dark: bool) -> DesktopPalette:
    """Return the restrained, high-contrast palette used by the desktop preview."""

    if is_dark:
        return DesktopPalette(
            background="#0c111d",
            surface="#161b26",
            surface_alt="#1d2939",
            field="#101828",
            text="#f9fafb",
            muted="#d0d5dd",
            subtle="#98a2b3",
            border="#344054",
            accent="#84adff",
            accent_hover="#b2ccff",
            accent_text="#101828",
            focus="#84adff",
            selection="#2e5aac",
            selection_text="#ffffff",
            success="#75e0a7",
            warning="#fec84b",
            danger="#fda29b",
        )
    return DesktopPalette(
        background="#f4f6f8",
        surface="#ffffff",
        surface_alt="#f8fafc",
        field="#ffffff",
        text="#101828",
        muted="#475467",
        subtle="#667085",
        border="#d0d5dd",
        accent="#155eef",
        accent_hover="#004eeb",
        accent_text="#ffffff",
        focus="#528bff",
        selection="#d1e0ff",
        selection_text="#101828",
        success="#067647",
        warning="#93370d",
        danger="#b42318",
    )


def _colour_is_dark(root: Any, colour: str) -> bool:
    try:
        red, green, blue = (channel / 65535 for channel in root.winfo_rgb(colour))
    except (ValueError, TypeError):
        return False
    luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue
    return luminance < 0.45


def profile_from_fields(
    name: str,
    cpv_codes: str,
    countries: str,
    minimum_days: str,
) -> Profile:
    """Validate the visible desktop profile fields through the public schema."""

    minimum_days = minimum_days.strip()
    if not minimum_days or not minimum_days.isascii() or not minimum_days.isdecimal():
        raise SchemaValidationError("Minimum days must be a whole number of 0 or more.")

    cpv_values = _split_tokens(cpv_codes)
    if not cpv_values:
        raise SchemaValidationError("Add at least one 8-digit CPV code.")
    country_values = _split_tokens(countries)
    if not country_values:
        raise SchemaValidationError("Add at least one 3-letter country code.")

    return profile_from_dict(
        {
            "schema_version": 1,
            "name": name,
            "cpv_codes": cpv_values,
            "countries": country_values,
            "minimum_days_to_deadline": int(minimum_days),
        }
    )


def read_local_snapshot(
    raw_path: str,
    *,
    label: str,
    maximum_bytes: int,
) -> LocalFileSnapshot:
    """Read one regular local file once, within the desktop input budget."""

    if not raw_path.strip():
        raise SchemaValidationError(f"Choose a {label} file.")
    path = Path(raw_path).expanduser()
    try:
        with path.open("rb") as handle:
            before = os.fstat(handle.fileno())
            if not stat.S_ISREG(before.st_mode):
                raise SchemaValidationError(f"The selected {label} path is not a file.")
            payload = handle.read(maximum_bytes + 1)
            after = os.fstat(handle.fileno())
    except OSError as exc:
        raise SchemaValidationError(f"Unable to read the selected {label} file.") from exc
    if (
        before.st_size != after.st_size
        or before.st_mtime_ns != after.st_mtime_ns
        or before.st_ino != after.st_ino
    ):
        raise SchemaValidationError(f"The selected {label} file changed while it was read.")
    if before.st_size > maximum_bytes or len(payload) > maximum_bytes:
        maximum_mib = maximum_bytes // (1024 * 1024)
        if maximum_mib:
            limit = f"{maximum_mib} MiB"
        else:
            limit = f"{maximum_bytes // 1024} KiB"
        raise SchemaValidationError(f"Choose a {label} file no larger than {limit}.")
    return LocalFileSnapshot(
        path=path,
        payload=payload,
        sha256=hashlib.sha256(payload).hexdigest(),
    )


def format_result_details(result: QualificationResult) -> str:
    """Render one result safely for a native read-only text widget."""

    notice = result.notice

    def safe(value: str | None, fallback: str = "(missing)") -> str:
        return normalize_display_text(value) if value else fallback

    lines = [
        f"Verdict: {_VERDICT_LABELS[result.verdict.value]}",
        f"Notice: {safe(notice_identity(notice.publication_number, notice.lot_id))}",
        f"Title: {safe(notice.title)}",
        f"Buyer: {safe(notice.buyer)}",
        f"Deadline: {deadline_display(notice.deadline, notice.deadline_at)}",
        "Published: "
        f"{notice.publication_date.isoformat() if notice.publication_date else '(missing)'}",
        f"Supplied source URL: {safe(notice.source_url)}",
        "",
        "Reasons",
    ]
    lines.extend(f"• {normalize_display_text(reason)}" for reason in result.reasons)
    lines.extend(["", "Unknowns"])
    if result.unknowns:
        lines.extend(f"• {normalize_display_text(unknown)}" for unknown in result.unknowns)
    else:
        lines.append("• None from the supplied metadata.")
    lines.extend(
        [
            "",
            "Human next step",
            normalize_display_text(result.human_next_step),
        ]
    )
    return "\n".join(lines)


def export_format_for_path(path: str | Path) -> str:
    """Map a user-selected filename to one supported report format."""

    suffix = Path(path).suffix.casefold()
    if suffix in {".htm", ".html"}:
        return "html"
    if suffix in {".md", ".markdown"}:
        return "markdown"
    if suffix == ".json":
        return "json"
    raise SchemaValidationError("Save the report as .html, .md, or .json.")


def shortcut_action(windowing_system: str, keycode: int, keysym: str) -> str | None:
    """Map one shortcut event without depending on the active keyboard layout."""

    if windowing_system == "aqua":
        return _MACOS_SHORTCUT_KEYCODES.get(keycode) or _KEYSYM_SHORTCUTS.get(keysym.casefold())
    if windowing_system == "win32":
        return _WINDOWS_SHORTCUT_KEYCODES.get(keycode) or _KEYSYM_SHORTCUTS.get(keysym.casefold())
    return _KEYSYM_SHORTCUTS.get(keysym.casefold())


def _split_tokens(value: str) -> list[str]:
    return [token for token in _TOKEN_SEPARATOR.split(value.strip()) if token]


def notice_count_label(count: int) -> str:
    return f"{count} notice" if count == 1 else f"{count} notices"


def notice_identity(publication_number: str, lot_id: str | None) -> str:
    return f"{publication_number} / {lot_id}" if lot_id else publication_number


def deadline_display(deadline: date | None, deadline_at: datetime | None) -> str:
    if deadline_at is not None:
        return deadline_at.isoformat()
    if deadline is not None:
        return deadline.isoformat()
    return "(missing)"


def visible_result_indices(
    results: Sequence[QualificationResult],
    verdict_filter: str,
    sort_column: str,
    descending: bool,
) -> list[int]:
    """Return stable result indices for the desktop queue view."""

    wanted_verdict = _FILTER_TO_VERDICT.get(verdict_filter)
    indices = [
        index
        for index, result in enumerate(results)
        if wanted_verdict is None or result.verdict.value == wanted_verdict
    ]
    if sort_column == "input":
        return indices

    if sort_column == "verdict":
        return sorted(
            indices,
            key=lambda index: _VERDICT_SORT_ORDER[results[index].verdict.value],
            reverse=descending,
        )
    if sort_column == "notice":
        return sorted(
            indices,
            key=lambda index: notice_identity(
                results[index].notice.publication_number,
                results[index].notice.lot_id,
            ).casefold(),
            reverse=descending,
        )
    if sort_column == "title":
        return sorted(
            indices,
            key=lambda index: (results[index].notice.title or "").casefold(),
            reverse=descending,
        )
    raise ValueError(f"unsupported desktop sort column: {sort_column}")


def _load_tkinter() -> tuple[Any, Any, Any, Any, Any]:
    try:
        import tkinter as tk
        import tkinter.font as tkfont
        from tkinter import filedialog, messagebox, ttk
    except ImportError as exc:
        raise DesktopUnavailableError(
            "Tk is unavailable in this Python installation. Use a Python 3.11+ build "
            "that includes Tk, or continue with the TenderVerdict CLI."
        ) from exc
    return tk, ttk, filedialog, messagebox, tkfont


class TenderVerdictApp:
    """A small native adapter around the deterministic offline workflow."""

    def __init__(
        self,
        root: Any,
        tk: Any,
        ttk: Any,
        filedialog: Any,
        messagebox: Any,
        tkfont: Any,
    ) -> None:
        self.root = root
        self.tk = tk
        self.ttk = ttk
        self.filedialog = filedialog
        self.messagebox = messagebox
        self._current_run: QualificationRun | None = None
        self._current_signature: tuple[str, ...] | None = None
        self._current_notices_sha256: str | None = None
        self._using_demo_notices = False
        self._suspend_stale = False
        self._sort_column = "input"
        self._sort_descending = False

        root.title("TenderVerdict")
        root.geometry("1120x780")
        root.minsize(860, 680)
        root.option_add("*tearOff", False)

        self.style = ttk.Style(root)
        self._configure_appearance(tkfont)

        self.name_var = tk.StringVar()
        self.cpv_var = tk.StringVar()
        self.countries_var = tk.StringVar()
        self.minimum_days_var = tk.StringVar(value="14")
        self.notices_path_var = tk.StringVar()
        self.notices_display_var = tk.StringVar(value="No notice file selected")
        self.as_of_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready. Add inputs or run the synthetic demo.")
        self.total_var = tk.StringVar(value="—")
        self.open_var = tk.StringVar(value="—")
        self.watch_var = tk.StringVar(value="—")
        self.reject_var = tk.StringVar(value="—")
        self.verdict_filter_var = tk.StringVar(value=_VERDICT_FILTERS[0])
        self.filter_summary_var = tk.StringVar(value="No reviewed notices")

        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)
        self._build_header()
        self._build_workspace()
        self._bind_shortcuts()
        self._build_menu()

        for variable in (
            self.name_var,
            self.cpv_var,
            self.countries_var,
            self.minimum_days_var,
            self.notices_path_var,
            self.as_of_var,
        ):
            variable.trace_add("write", self._mark_result_stale)
        self.name_entry.focus_set()

    def _configure_appearance(self, tkfont: Any) -> None:
        native_background = self.style.lookup("TFrame", "background") or self.root.cget(
            "background"
        )
        self.palette = desktop_palette(_colour_is_dark(self.root, native_background))
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")

        palette = self.palette
        self.root.configure(background=palette.background)

        default_font = tkfont.nametofont("TkDefaultFont")
        configured_size = int(default_font.cget("size"))
        base_size = configured_size if configured_size > 0 else 13
        self.body_font = default_font.copy()
        self.body_font.configure(size=max(base_size, 12))
        self.small_font = default_font.copy()
        self.small_font.configure(size=max(base_size - 1, 11))
        self.eyebrow_font = self.small_font.copy()
        self.eyebrow_font.configure(weight="bold")
        self.label_font = self.body_font.copy()
        self.label_font.configure(weight="bold")
        self.title_font = default_font.copy()
        self.title_font.configure(size=max(base_size + 9, 22), weight="bold")
        self.heading_font = default_font.copy()
        self.heading_font.configure(size=max(base_size + 3, 16), weight="bold")
        self.metric_font = default_font.copy()
        self.metric_font.configure(size=max(base_size + 7, 20), weight="bold")
        self.button_font = self.body_font.copy()
        self.button_font.configure(weight="bold")

        self.style.configure(".", font=self.body_font)
        self.style.configure("App.TFrame", background=palette.background)
        self.style.configure("Surface.TFrame", background=palette.surface)
        self.style.configure(
            "Card.TFrame",
            background=palette.surface,
            relief="solid",
            borderwidth=1,
            bordercolor=palette.border,
        )
        self.style.configure(
            "Metric.TFrame",
            background=palette.surface_alt,
            relief="solid",
            borderwidth=1,
            bordercolor=palette.border,
        )
        self.style.configure(
            "Title.TLabel",
            background=palette.background,
            foreground=palette.text,
            font=self.title_font,
        )
        self.style.configure(
            "Subtitle.TLabel",
            background=palette.background,
            foreground=palette.muted,
            font=self.body_font,
        )
        self.style.configure(
            "HeaderEyebrow.TLabel",
            background=palette.background,
            foreground=palette.accent,
            font=self.eyebrow_font,
        )
        self.style.configure(
            "Trust.TLabel",
            background=palette.surface_alt,
            foreground=palette.text,
            font=self.eyebrow_font,
            padding=(12, 7),
            relief="solid",
            borderwidth=1,
            bordercolor=palette.border,
            lightcolor=palette.border,
            darkcolor=palette.border,
        )
        self.style.configure(
            "CardTitle.TLabel",
            background=palette.surface,
            foreground=palette.text,
            font=self.heading_font,
        )
        self.style.configure(
            "CardDescription.TLabel",
            background=palette.surface,
            foreground=palette.muted,
            font=self.body_font,
        )
        self.style.configure(
            "CardEyebrow.TLabel",
            background=palette.surface,
            foreground=palette.accent,
            font=self.eyebrow_font,
        )
        self.style.configure(
            "FieldLabel.TLabel",
            background=palette.surface,
            foreground=palette.text,
            font=self.label_font,
        )
        self.style.configure(
            "Helper.TLabel",
            background=palette.surface,
            foreground=palette.subtle,
            font=self.small_font,
        )
        self.style.configure(
            "MetricLabel.TLabel",
            background=palette.surface_alt,
            foreground=palette.muted,
            font=self.small_font,
        )
        self.style.configure(
            "MetricValue.TLabel",
            background=palette.surface_alt,
            foreground=palette.text,
            font=self.metric_font,
        )
        for tone, colour in (
            ("Open", palette.success),
            ("Watch", palette.warning),
            ("Reject", palette.danger),
        ):
            self.style.configure(
                f"{tone}.MetricValue.TLabel",
                background=palette.surface_alt,
                foreground=colour,
                font=self.metric_font,
            )
        for tone, colour in (
            ("Status", palette.muted),
            ("Success.Status", palette.success),
            ("Warning.Status", palette.warning),
            ("Error.Status", palette.danger),
        ):
            self.style.configure(
                f"{tone}.TLabel",
                background=palette.surface,
                foreground=colour,
                font=self.small_font,
            )

        entry_options = {
            "padding": (10, 6),
            "fieldbackground": palette.field,
            "foreground": palette.text,
            "bordercolor": palette.border,
            "lightcolor": palette.border,
            "darkcolor": palette.border,
            "insertcolor": palette.text,
        }
        self.style.configure("Field.TEntry", **entry_options)
        self.style.configure("Field.TSpinbox", **entry_options)
        for style_name in ("Field.TEntry", "Field.TSpinbox"):
            self.style.map(
                style_name,
                bordercolor=[("focus", palette.focus)],
                lightcolor=[("focus", palette.focus)],
                darkcolor=[("focus", palette.focus)],
                fieldbackground=[("readonly", palette.surface_alt)],
                foreground=[("readonly", palette.text)],
            )

        self.style.configure(
            "Primary.TButton",
            background=palette.accent,
            foreground=palette.accent_text,
            borderwidth=0,
            focusthickness=2,
            focuscolor=palette.focus,
            font=self.button_font,
            padding=(16, 9),
        )
        self.style.map(
            "Primary.TButton",
            background=[
                ("disabled", palette.border),
                ("pressed", palette.accent_hover),
                ("active", palette.accent_hover),
            ],
            foreground=[("disabled", palette.subtle)],
        )
        self.style.configure(
            "Secondary.TButton",
            background=palette.surface_alt,
            foreground=palette.text,
            bordercolor=palette.border,
            lightcolor=palette.border,
            darkcolor=palette.border,
            font=self.button_font,
            padding=(13, 7),
        )
        self.style.map(
            "Secondary.TButton",
            background=[("pressed", palette.field), ("active", palette.field)],
            bordercolor=[("focus", palette.focus)],
            foreground=[("disabled", palette.subtle)],
        )
        self.style.configure(
            "Quiet.TButton",
            background=palette.surface,
            foreground=palette.muted,
            bordercolor=palette.border,
            lightcolor=palette.border,
            darkcolor=palette.border,
            font=self.small_font,
            padding=(11, 6),
        )
        self.style.map(
            "Quiet.TButton",
            background=[("pressed", palette.surface_alt), ("active", palette.surface_alt)],
            foreground=[("active", palette.text), ("disabled", palette.subtle)],
            bordercolor=[("focus", palette.focus)],
        )
        self.style.configure(
            "Quiet.TMenubutton",
            background=palette.surface,
            foreground=palette.muted,
            bordercolor=palette.border,
            lightcolor=palette.border,
            darkcolor=palette.border,
            font=self.small_font,
            padding=(10, 5),
        )
        self.style.map(
            "Quiet.TMenubutton",
            background=[("pressed", palette.surface_alt), ("active", palette.surface_alt)],
            foreground=[("active", palette.text)],
            bordercolor=[("focus", palette.focus)],
        )
        self.style.configure(
            "Review.Treeview",
            background=palette.surface,
            fieldbackground=palette.surface,
            foreground=palette.text,
            borderwidth=1,
            bordercolor=palette.border,
            lightcolor=palette.border,
            darkcolor=palette.border,
            relief="solid",
            rowheight=34,
        )
        self.style.map(
            "Review.Treeview",
            background=[("selected", palette.selection)],
            foreground=[("selected", palette.selection_text)],
        )
        self.style.configure(
            "Review.Treeview.Heading",
            background=palette.surface_alt,
            foreground=palette.muted,
            bordercolor=palette.border,
            relief="flat",
            font=self.eyebrow_font,
            padding=(10, 8),
        )
        self.style.map(
            "Review.Treeview.Heading",
            background=[("active", palette.surface_alt)],
        )

    def _build_header(self) -> None:
        header = self.ttk.Frame(
            self.root,
            padding=(24, 18, 24, 10),
            style="App.TFrame",
        )
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        self.ttk.Label(
            header,
            text="LOCAL PROCUREMENT REVIEW",
            style="HeaderEyebrow.TLabel",
        ).grid(row=0, column=0, sticky="w")
        self.ttk.Label(header, text="TenderVerdict", style="Title.TLabel").grid(
            row=1, column=0, sticky="w", pady=(3, 0)
        )
        self.ttk.Label(
            header,
            text="Turn supplier criteria and notice metadata into an explainable review queue.",
            style="Subtitle.TLabel",
            wraplength=680,
        ).grid(row=2, column=0, sticky="w", pady=(4, 0))
        self.ttk.Label(
            header,
            text="LOCAL / NO UPLOADS",
            style="Trust.TLabel",
        ).grid(row=0, column=1, rowspan=2, sticky="e", padx=(20, 0))
        self.ttk.Label(
            header,
            text="Developer preview",
            style="Subtitle.TLabel",
        ).grid(row=2, column=1, sticky="e", padx=(20, 0), pady=(4, 0))

    def _build_workspace(self) -> None:
        workspace = self.ttk.Frame(
            self.root,
            padding=(20, 8, 20, 16),
            style="App.TFrame",
        )
        workspace.grid(row=1, column=0, sticky="nsew")
        workspace.columnconfigure(0, weight=2, minsize=315)
        workspace.columnconfigure(1, weight=3, minsize=455)
        workspace.rowconfigure(0, weight=1)

        setup = self.ttk.Frame(
            workspace,
            padding=(20, 14),
            style="Card.TFrame",
        )
        setup.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        results = self.ttk.Frame(
            workspace,
            padding=(20, 14),
            style="Card.TFrame",
        )
        results.grid(row=0, column=1, sticky="nsew")
        self._build_setup(setup)
        self._build_results(results)

    def _build_setup(self, frame: Any) -> None:
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        self.ttk.Label(frame, text="SETUP", style="CardEyebrow.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        self.ttk.Label(
            frame,
            text="Supplier criteria",
            style="CardTitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(3, 0))
        profile_menu = self.tk.Menu(frame)
        profile_menu.add_command(label="Load Profile…", command=self._load_profile)
        profile_menu.add_command(label="Save Profile…", command=self._save_profile)
        self.profile_menu_button = self.ttk.Menubutton(
            frame,
            text="Profile…",
            menu=profile_menu,
            style="Quiet.TMenubutton",
        )
        self.profile_menu_button.grid(row=1, column=1, sticky="e", padx=(10, 0))

        self.ttk.Label(frame, text="Supplier name", style="FieldLabel.TLabel").grid(
            row=4, column=0, columnspan=2, sticky="w"
        )
        self.name_entry = self.ttk.Entry(
            frame,
            textvariable=self.name_var,
            style="Field.TEntry",
        )
        self.name_entry.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(5, 10))

        self.ttk.Label(frame, text="CPV codes", style="FieldLabel.TLabel").grid(
            row=6, column=0, sticky="w", padx=(0, 6)
        )
        self.ttk.Label(frame, text="Countries", style="FieldLabel.TLabel").grid(
            row=6, column=1, sticky="w", padx=(6, 0)
        )
        self.cpv_entry = self.ttk.Entry(
            frame,
            textvariable=self.cpv_var,
            style="Field.TEntry",
        )
        self.cpv_entry.grid(row=7, column=0, sticky="ew", padx=(0, 6), pady=(5, 0))
        self.countries_entry = self.ttk.Entry(
            frame,
            textvariable=self.countries_var,
            style="Field.TEntry",
        )
        self.countries_entry.grid(row=7, column=1, sticky="ew", padx=(6, 0), pady=(5, 0))
        self.ttk.Label(
            frame,
            text="8-digit CPV · 3-letter country · comma-separated",
            style="Helper.TLabel",
            wraplength=330,
        ).grid(row=8, column=0, columnspan=2, sticky="w", pady=(5, 10))

        self.ttk.Label(
            frame,
            text="Lead time (days)",
            style="FieldLabel.TLabel",
        ).grid(row=9, column=0, sticky="w", padx=(0, 6))
        self.ttk.Label(
            frame,
            text="Review point",
            style="FieldLabel.TLabel",
        ).grid(row=9, column=1, sticky="w", padx=(6, 0))
        self.minimum_days_entry = self.ttk.Spinbox(
            frame,
            from_=0,
            to=3650,
            textvariable=self.minimum_days_var,
            style="Field.TSpinbox",
        )
        self.minimum_days_entry.grid(row=10, column=0, sticky="ew", padx=(0, 6), pady=(5, 0))
        self.as_of_entry = self.ttk.Entry(
            frame,
            textvariable=self.as_of_var,
            style="Field.TEntry",
        )
        self.as_of_entry.grid(row=10, column=1, sticky="ew", padx=(6, 0), pady=(5, 0))
        self.ttk.Label(
            frame,
            text="Date or RFC 3339 timestamp with UTC offset",
            style="Helper.TLabel",
            wraplength=330,
        ).grid(row=11, column=0, columnspan=2, sticky="w", pady=(5, 0))

        self.ttk.Label(frame, text="NOTICE DATA", style="CardEyebrow.TLabel").grid(
            row=12, column=0, columnspan=2, sticky="w", pady=(16, 0)
        )
        self.ttk.Label(
            frame,
            text="Use CSV, JSON, or the offline demo.",
            style="CardDescription.TLabel",
            wraplength=330,
        ).grid(row=13, column=0, columnspan=2, sticky="w", pady=(4, 8))
        self.notices_entry = self.ttk.Entry(
            frame,
            textvariable=self.notices_display_var,
            state="readonly",
            takefocus=False,
            style="Field.TEntry",
        )
        self.notices_entry.grid(row=14, column=0, columnspan=2, sticky="ew")

        notice_actions = self.ttk.Frame(frame, style="Surface.TFrame")
        notice_actions.grid(row=15, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        notice_actions.columnconfigure(0, weight=1)
        notice_actions.columnconfigure(1, weight=1)
        self.choose_notices_button = self.ttk.Button(
            notice_actions,
            text="Choose file…",
            command=self._choose_notices,
            style="Secondary.TButton",
        )
        self.choose_notices_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.ttk.Button(
            notice_actions,
            text="Run demo",
            command=self._run_demo,
            style="Secondary.TButton",
        ).grid(row=0, column=1, sticky="ew", padx=(5, 0))

        frame.rowconfigure(16, weight=1)
        self.run_button = self.ttk.Button(
            frame,
            text="Run review",
            command=self._run_review,
            style="Primary.TButton",
        )
        self.run_button.grid(row=17, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        self.status_label = self.ttk.Label(
            frame,
            textvariable=self.status_var,
            style="Status.TLabel",
            wraplength=330,
            takefocus=True,
        )
        self.status_label.grid(row=18, column=0, columnspan=2, sticky="w", pady=(4, 0))

    def _set_status(self, message: str, tone: str = "neutral") -> None:
        styles = {
            "neutral": "Status.TLabel",
            "success": "Success.Status.TLabel",
            "warning": "Warning.Status.TLabel",
            "error": "Error.Status.TLabel",
        }
        self.status_var.set(message)
        self.status_label.configure(style=styles.get(tone, "Status.TLabel"))

    def _build_results(self, outer: Any) -> None:
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(3, weight=2)
        outer.rowconfigure(4, weight=3)

        header = self.ttk.Frame(outer, style="Surface.TFrame")
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        self.ttk.Label(header, text="RESULTS", style="CardEyebrow.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        self.ttk.Label(header, text="Review queue", style="CardTitle.TLabel").grid(
            row=1, column=0, sticky="w", pady=(3, 0)
        )
        self.ttk.Label(
            header,
            text="Reasons, unknowns, and next steps stay attached to every verdict.",
            style="CardDescription.TLabel",
            wraplength=520,
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(4, 0))
        self.export_button = self.ttk.Button(
            header,
            text="Export report…",
            command=self._export_report,
            state="disabled",
            style="Secondary.TButton",
        )
        self.export_button.grid(row=0, column=1, rowspan=3, sticky="e", padx=(16, 0))

        summary = self.ttk.Frame(outer, style="Surface.TFrame")
        summary.grid(row=1, column=0, sticky="ew", pady=(18, 16))
        for column in range(4):
            summary.columnconfigure(column, weight=1)
        metrics = (
            ("Notices", self.total_var, "MetricValue.TLabel"),
            ("Open", self.open_var, "Open.MetricValue.TLabel"),
            ("Watch", self.watch_var, "Watch.MetricValue.TLabel"),
            ("Reject", self.reject_var, "Reject.MetricValue.TLabel"),
        )
        for column, (label, variable, value_style) in enumerate(metrics):
            card = self.ttk.Frame(summary, padding=(12, 10), style="Metric.TFrame")
            card.grid(
                row=0,
                column=column,
                sticky="ew",
                padx=(0 if column == 0 else 4, 0 if column == 3 else 4),
            )
            self.ttk.Label(
                card,
                textvariable=variable,
                style=value_style,
            ).grid(row=0, column=0, sticky="w")
            self.ttk.Label(card, text=label, style="MetricLabel.TLabel").grid(
                row=1, column=0, sticky="w", pady=(2, 0)
            )

        queue_toolbar = self.ttk.Frame(outer, style="Surface.TFrame")
        queue_toolbar.grid(row=2, column=0, sticky="ew", pady=(0, 7))
        queue_toolbar.columnconfigure(1, weight=1)
        self.ttk.Label(queue_toolbar, text="Notices", style="FieldLabel.TLabel").grid(
            row=0, column=0, sticky="w", padx=(0, 10)
        )
        self.verdict_filter = self.ttk.Combobox(
            queue_toolbar,
            textvariable=self.verdict_filter_var,
            values=_VERDICT_FILTERS,
            state="readonly",
            width=16,
            takefocus=True,
        )
        self.verdict_filter.grid(row=0, column=1, sticky="w")
        self.verdict_filter.bind("<<ComboboxSelected>>", self._refresh_results)
        self.ttk.Label(
            queue_toolbar,
            textvariable=self.filter_summary_var,
            style="Helper.TLabel",
        ).grid(row=0, column=2, sticky="e", padx=(10, 8))
        self.copy_button = self.ttk.Button(
            queue_toolbar,
            text="Copy selected",
            command=self._copy_selected_result,
            state="disabled",
            style="Quiet.TButton",
        )
        self.copy_button.grid(row=0, column=3, sticky="e")
        list_frame = self.ttk.Frame(outer, style="Surface.TFrame")
        list_frame.grid(row=3, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        self.results_tree = self.ttk.Treeview(
            list_frame,
            columns=("verdict", "notice", "title"),
            show="headings",
            selectmode="browse",
            style="Review.Treeview",
            height=7,
            takefocus=True,
        )
        self.results_tree.heading(
            "verdict",
            text="Verdict",
            command=lambda: self._sort_results("verdict"),
        )
        self.results_tree.heading(
            "notice",
            text="Notice / lot",
            command=lambda: self._sort_results("notice"),
        )
        self.results_tree.heading(
            "title",
            text="Notice title",
            command=lambda: self._sort_results("title"),
        )
        self.results_tree.column("verdict", width=118, minwidth=100, stretch=False)
        self.results_tree.column("notice", width=135, minwidth=110, stretch=False)
        self.results_tree.column("title", width=340, minwidth=160, stretch=True)
        tree_scroll = self.ttk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.results_tree.yview,
        )
        self.results_tree.configure(yscrollcommand=tree_scroll.set)
        self.results_tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll.grid(row=0, column=1, sticky="ns")
        self.results_tree.bind("<<TreeviewSelect>>", self._show_selected_result)
        self.results_tree.tag_configure("open_documents", foreground=self.palette.success)
        self.results_tree.tag_configure("watch", foreground=self.palette.warning)
        self.results_tree.tag_configure("reject", foreground=self.palette.danger)

        detail_frame = self.ttk.Frame(outer, style="Surface.TFrame")
        detail_frame.grid(row=4, column=0, sticky="nsew", pady=(16, 0))
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(1, weight=1)
        self.ttk.Label(
            detail_frame,
            text="Selected notice",
            style="FieldLabel.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))
        self.details_text = self.tk.Text(
            detail_frame,
            wrap="word",
            state="disabled",
            takefocus=True,
            borderwidth=1,
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.palette.border,
            highlightcolor=self.palette.focus,
            background=self.palette.surface_alt,
            foreground=self.palette.text,
            selectbackground=self.palette.selection,
            selectforeground=self.palette.selection_text,
            font=self.body_font,
            padx=14,
            pady=12,
        )
        self.details_text.tag_configure(
            "detail_title",
            font=self.heading_font,
            foreground=self.palette.text,
            spacing3=7,
        )
        self.details_text.tag_configure(
            "detail_meta",
            font=self.small_font,
            foreground=self.palette.muted,
            spacing3=9,
        )
        self.details_text.tag_configure(
            "detail_section",
            font=self.label_font,
            foreground=self.palette.text,
            spacing1=10,
            spacing3=4,
        )
        self.details_text.tag_configure(
            "detail_body",
            font=self.body_font,
            foreground=self.palette.muted,
            lmargin2=12,
            spacing3=3,
        )
        for verdict, colour in (
            ("open_documents", self.palette.success),
            ("watch", self.palette.warning),
            ("reject", self.palette.danger),
        ):
            self.details_text.tag_configure(
                f"verdict_{verdict}",
                font=self.label_font,
                foreground=colour,
                spacing3=4,
            )
        detail_scroll = self.ttk.Scrollbar(
            detail_frame,
            orient="vertical",
            command=self.details_text.yview,
        )
        self.details_text.configure(yscrollcommand=detail_scroll.set)
        self.details_text.grid(row=1, column=0, sticky="nsew")
        detail_scroll.grid(row=1, column=1, sticky="ns")
        self._set_empty_details(
            "Ready for a local review",
            "Run the synthetic demo or add a normalized CSV or JSON file. "
            "Results will appear here.",
        )

    def _bind_shortcuts(self) -> None:
        self._windowing_system = str(self.root.tk.call("tk", "windowingsystem"))
        modifier = "Command" if self._windowing_system == "aqua" else "Control"
        self.root.bind_all(f"<{modifier}-KeyPress>", self._handle_shortcut)
        self.root.bind_all(f"<{modifier}-Shift-KeyPress-c>", self._copy_selected_result)

    def _build_menu(self) -> None:
        accelerator = "⌘" if self._windowing_system == "aqua" else "Ctrl+"
        menu = self.tk.Menu(self.root)

        file_menu = self.tk.Menu(menu)
        file_menu.add_command(
            label="Choose Notice Data…",
            accelerator=f"{accelerator}O",
            command=self._choose_notices,
        )
        file_menu.add_command(label="Save CSV Example…", command=self._save_csv_example)
        self.save_csv_example_menu_index = file_menu.index("end")
        file_menu.add_separator()
        file_menu.add_command(label="Load Profile…", command=self._load_profile)
        file_menu.add_command(label="Save Profile…", command=self._save_profile)
        file_menu.add_separator()
        file_menu.add_command(
            label="Export Report…",
            accelerator=f"{accelerator}S",
            command=self._export_report,
            state="disabled",
        )
        self.file_menu = file_menu
        self.export_menu_index = file_menu.index("end")
        menu.add_cascade(label="File", menu=file_menu)

        edit_menu = self.tk.Menu(menu)
        edit_menu.add_command(
            label="Copy Selected Result",
            accelerator=f"{accelerator}Shift+C",
            command=self._copy_selected_result,
            state="disabled",
        )
        self.edit_menu = edit_menu
        self.copy_menu_index = edit_menu.index("end")
        menu.add_cascade(label="Edit", menu=edit_menu)

        review_menu = self.tk.Menu(menu)
        review_menu.add_command(
            label="Run Demo",
            accelerator=f"{accelerator}D",
            command=self._run_demo,
        )
        review_menu.add_command(
            label="Run Review",
            accelerator=f"{accelerator}R",
            command=self._run_review,
        )
        menu.add_cascade(label="Review", menu=review_menu)
        self.root.configure(menu=menu)

    def _handle_shortcut(self, event: Any) -> str | None:
        action = shortcut_action(self._windowing_system, int(event.keycode), str(event.keysym))
        if action is None:
            return None
        commands = {
            "demo": self._run_demo,
            "export": self._export_report,
            "open": self._choose_notices,
            "review": self._run_review,
        }
        command = commands[action]
        command()
        return "break"

    def _profile_from_form(self) -> Profile:
        return profile_from_fields(
            self.name_var.get(),
            self.cpv_var.get(),
            self.countries_var.get(),
            self.minimum_days_var.get(),
        )

    def _input_signature(self) -> tuple[str, ...]:
        return (
            self.name_var.get(),
            self.cpv_var.get(),
            self.countries_var.get(),
            self.minimum_days_var.get(),
            self.notices_path_var.get(),
            self.as_of_var.get(),
            str(self._using_demo_notices),
        )

    def _mark_result_stale(self, *_args: object) -> None:
        if self._suspend_stale:
            return
        if self._current_run is None:
            self._set_status("Input changed. Run the review to validate it.")
            return
        if self._input_signature() != self._current_signature:
            self._clear_results("Inputs changed. Run the review again before exporting.")

    def _choose_notices(self) -> None:
        selected = self.filedialog.askopenfilename(
            title="Choose normalized notice data",
            filetypes=(
                ("Notice data", "*.csv *.json"),
                ("CSV files", "*.csv"),
                ("JSON files", "*.json"),
                ("All files", "*"),
            ),
        )
        if not selected:
            return
        try:
            snapshot = read_local_snapshot(
                selected,
                label="notices",
                maximum_bytes=MAX_NOTICES_FILE_BYTES,
            )
            notices = notice_collection_from_file_bytes(snapshot.payload, snapshot.path).notices
        except (SchemaValidationError, OSError, ValueError) as exc:
            self._show_error("Unable to use notice data", exc, self.choose_notices_button)
            return
        self._using_demo_notices = False
        self.notices_path_var.set(selected)
        self.notices_display_var.set(selected)
        self._set_status(
            f"{notice_count_label(len(notices))} ready · confirm the review date, "
            "then run the review.",
            "success",
        )
        self.as_of_entry.focus_set()

    def _load_profile(self) -> None:
        selected = self.filedialog.askopenfilename(
            title="Load supplier profile",
            filetypes=(("JSON files", "*.json"), ("All files", "*")),
        )
        if not selected:
            return
        try:
            snapshot = read_local_snapshot(
                selected,
                label="profile",
                maximum_bytes=MAX_PROFILE_FILE_BYTES,
            )
            profile = profile_from_json_bytes(snapshot.payload, snapshot.path)
        except (SchemaValidationError, OSError, ValueError) as exc:
            self._show_error("Unable to load profile", exc, self.name_entry)
            return
        had_current_run = self._current_run is not None
        self._set_profile_fields(profile)
        if had_current_run:
            self._clear_results(f"Loaded profile {snapshot.path.name}. Run the review again.")
        else:
            self._set_status(f"Loaded profile {snapshot.path.name}.", "success")
        self.name_entry.focus_set()

    def _save_profile(self) -> None:
        try:
            profile = self._profile_from_form()
        except (SchemaValidationError, ValueError) as exc:
            self._show_error("Unable to save profile", exc, self.name_entry)
            return
        selected = self.filedialog.asksaveasfilename(
            title="Save supplier profile",
            defaultextension=".json",
            initialfile="tenderverdict-profile.json",
            filetypes=(("JSON files", "*.json"),),
        )
        if not selected:
            return
        try:
            write_text_atomically(selected, dump_json(profile.to_dict()))
        except OSError as exc:
            self._show_error("Unable to save profile", exc, self.name_entry)
            return
        self._set_status(f"Saved profile as {Path(selected).name}.", "success")

    def _save_csv_example(self) -> None:
        selected = self.filedialog.asksaveasfilename(
            title="Save editable CSV example",
            defaultextension=".csv",
            initialfile="tenderverdict-notices-example.csv",
            filetypes=(("CSV files", "*.csv"),),
        )
        if not selected:
            return
        notices = notices_from_data(demo_notices())
        try:
            write_text_atomically(selected, render_notices_csv(notices))
        except OSError as exc:
            self._show_error("Unable to save CSV example", exc, self.choose_notices_button)
            return
        self._set_status(
            f"Saved {Path(selected).name}. Replace the synthetic rows, then choose that file.",
            "success",
        )

    def _run_demo(self) -> None:
        run = demo_run()
        self._suspend_stale = True
        try:
            self._set_profile_fields(run.profile)
            self._using_demo_notices = True
            self.notices_path_var.set(DEMO_NOTICE_LABEL)
            self.notices_display_var.set(DEMO_NOTICE_LABEL)
            self.as_of_var.set(run.as_of.isoformat())
        finally:
            self._suspend_stale = False
        self._display_run(run, notices_sha256=None)
        self._set_status("Demo complete · offline · no uploads.", "success")

    def _run_review(self) -> None:
        if self._current_run is not None:
            self._clear_results("Validating the current inputs…")
        try:
            profile = self._profile_from_form()
        except (SchemaValidationError, ValueError) as exc:
            message = str(exc).casefold()
            if "cpv" in message:
                focus_widget = self.cpv_entry
            elif "countr" in message:
                focus_widget = self.countries_entry
            elif "minimum" in message:
                focus_widget = self.minimum_days_entry
            else:
                focus_widget = self.name_entry
            self._show_error("Review not created", exc, focus_widget)
            return
        try:
            as_of = parse_review_point(self.as_of_var.get().strip(), "Review point")
        except (SchemaValidationError, ValueError) as exc:
            self._show_error("Review not created", exc, self.as_of_entry)
            return
        try:
            if self._using_demo_notices:
                notices_sha256 = None
                run = qualify_inputs(
                    profile,
                    notices_from_data(demo_notices()),
                    as_of=as_of,
                )
            else:
                snapshot = read_local_snapshot(
                    self.notices_path_var.get(),
                    label="notices",
                    maximum_bytes=MAX_NOTICES_FILE_BYTES,
                )
                notices_sha256 = snapshot.sha256
                collection = notice_collection_from_file_bytes(snapshot.payload, snapshot.path)
                run = qualify_inputs(
                    profile,
                    collection.notices,
                    as_of=as_of,
                    source_kind=collection.source_kind,
                    notices_sha256=snapshot.sha256,
                    ted_query=collection.ted_query,
                    retrieved_at=collection.retrieved_at,
                    lot_policy=collection.lot_policy,
                )
        except (SchemaValidationError, OSError, ValueError) as exc:
            self._show_error("Review not created", exc, self.choose_notices_button)
            return
        self._display_run(run, notices_sha256=notices_sha256)
        self._set_status(
            f"Review complete · {notice_count_label(len(run.results))} · no uploads.",
            "success",
        )

    def _display_run(self, run: QualificationRun, *, notices_sha256: str | None) -> None:
        self._current_run = run
        self._current_signature = self._input_signature()
        self._current_notices_sha256 = notices_sha256
        summary = run.summary
        self.total_var.set(str(summary["total"]))
        self.open_var.set(str(summary["open_documents"]))
        self.watch_var.set(str(summary["watch"]))
        self.reject_var.set(str(summary["reject"]))
        self.export_button.configure(state="normal")
        self.file_menu.entryconfigure(self.export_menu_index, state="normal")
        self._sort_column = "input"
        self._sort_descending = False
        self.verdict_filter_var.set(_VERDICT_FILTERS[0])
        self._refresh_results()

    def _sort_results(self, column: str) -> None:
        if self._current_run is None:
            return
        if self._sort_column == column:
            self._sort_descending = not self._sort_descending
        else:
            self._sort_column = column
            self._sort_descending = False
        self._refresh_results()

    def _refresh_results(self, _event: object | None = None) -> None:
        selected_index: int | None = None
        selection = self.results_tree.selection()
        if selection:
            selected_index = int(selection[0])
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        if self._current_run is None:
            self.filter_summary_var.set("No reviewed notices")
            self._set_copy_state(False)
            return

        indices = visible_result_indices(
            self._current_run.results,
            self.verdict_filter_var.get(),
            self._sort_column,
            self._sort_descending,
        )
        for index in indices:
            result = self._current_run.results[index]
            notice = result.notice
            self.results_tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    _VERDICT_LABELS[result.verdict.value],
                    normalize_display_text(
                        notice_identity(notice.publication_number, notice.lot_id)
                    ),
                    normalize_display_text(notice.title or "(title missing)"),
                ),
                tags=(result.verdict.value,),
            )
        self.filter_summary_var.set(f"Showing {len(indices)} of {len(self._current_run.results)}")
        if not indices:
            self._set_copy_state(False)
            self._set_empty_details(
                "No notices match this filter",
                "Choose another verdict filter to continue reviewing results.",
            )
            return
        target = selected_index if selected_index in indices else indices[0]
        iid = str(target)
        self.results_tree.selection_set(iid)
        self.results_tree.focus(iid)
        self.results_tree.see(iid)
        self._show_selected_result()
        self.results_tree.focus_set()

    def _set_copy_state(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        self.copy_button.configure(state=state)
        self.edit_menu.entryconfigure(self.copy_menu_index, state=state)

    def _copy_selected_result(self, _event: object | None = None) -> str | None:
        if self._current_run is None:
            return None
        selection = self.results_tree.selection()
        if not selection:
            return None
        result = self._current_run.results[int(selection[0])]
        self.root.clipboard_clear()
        self.root.clipboard_append(format_result_details(result))
        self.root.update_idletasks()
        self._set_status(
            "Copied the selected result as plain text. No data was uploaded.",
            "success",
        )
        return "break"

    def _show_selected_result(self, _event: object | None = None) -> None:
        if self._current_run is None:
            return
        selection = self.results_tree.selection()
        if not selection:
            return
        index = int(selection[0])
        self._set_result_details(self._current_run.results[index])
        self._set_copy_state(True)

    def _export_report(self) -> None:
        if self._current_run is None or self._input_signature() != self._current_signature:
            self._set_status(
                "Run the current inputs before exporting a report.",
                "warning",
            )
            return
        if not self._notices_are_current():
            return
        review_date = (
            self._current_run.as_of.date()
            if type(self._current_run.as_of) is datetime
            else self._current_run.as_of
        )
        initialfile = f"tenderverdict-report-{review_date.isoformat()}.html"
        selected = self.filedialog.asksaveasfilename(
            title="Export review report",
            defaultextension=".html",
            initialfile=initialfile,
            filetypes=(
                ("HTML report", "*.html"),
                ("Markdown report", "*.md"),
                ("JSON report", "*.json"),
            ),
        )
        if not selected:
            return
        if not self._notices_are_current():
            return
        try:
            format_name = export_format_for_path(selected)
            write_run(self._current_run, selected, format_name)
        except (SchemaValidationError, OSError, ValueError) as exc:
            self._show_error("Unable to export report", exc, self.export_button)
            return
        self._set_status(f"Exported report as {Path(selected).name}.", "success")

    def _notices_are_current(self) -> bool:
        if self._current_notices_sha256 is None:
            return True
        try:
            snapshot = read_local_snapshot(
                self.notices_path_var.get(),
                label="notices",
                maximum_bytes=MAX_NOTICES_FILE_BYTES,
            )
        except (SchemaValidationError, OSError, ValueError) as exc:
            self._clear_results("Notices could not be rechecked. Run the review again.")
            self._show_error("Report is stale", exc, self.run_button)
            return False
        if snapshot.sha256 == self._current_notices_sha256:
            return True
        self._clear_results("Notices changed on disk. Run the review again before export.")
        self._show_error(
            "Report is stale",
            SchemaValidationError("The selected notices file changed after the review."),
            self.run_button,
        )
        return False

    def _set_profile_fields(self, profile: Profile) -> None:
        previous_suspend_state = self._suspend_stale
        self._suspend_stale = True
        try:
            self.name_var.set(profile.name)
            self.cpv_var.set(", ".join(profile.cpv_codes))
            self.countries_var.set(", ".join(profile.countries))
            self.minimum_days_var.set(str(profile.minimum_days_to_deadline))
        finally:
            self._suspend_stale = previous_suspend_state

    def _clear_results(self, status: str) -> None:
        self._current_run = None
        self._current_signature = None
        self._current_notices_sha256 = None
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.total_var.set("—")
        self.open_var.set("—")
        self.watch_var.set("—")
        self.reject_var.set("—")
        self.filter_summary_var.set("No reviewed notices")
        self.verdict_filter_var.set(_VERDICT_FILTERS[0])
        self.export_button.configure(state="disabled")
        self.file_menu.entryconfigure(self.export_menu_index, state="disabled")
        self._set_copy_state(False)
        self._set_empty_details(
            "Results need a refresh",
            "Run the current inputs to create a new review.",
        )
        self._set_status(status, "warning")

    def _replace_details(self, sections: list[tuple[str, str]]) -> None:
        self.details_text.configure(state="normal")
        self.details_text.delete("1.0", "end")
        for content, tag in sections:
            self.details_text.insert("end", content, tag)
        self.details_text.yview_moveto(0)
        self.details_text.configure(state="disabled")

    def _set_empty_details(self, title: str, body: str) -> None:
        self._replace_details(
            [
                (f"{normalize_display_text(title)}\n", "detail_title"),
                (normalize_display_text(body), "detail_body"),
            ]
        )

    def _set_result_details(self, result: QualificationResult) -> None:
        notice = result.notice

        def safe(value: str | None, fallback: str = "(missing)") -> str:
            return normalize_display_text(value) if value else fallback

        deadline = deadline_display(notice.deadline, notice.deadline_at)
        publication_date = (
            notice.publication_date.isoformat() if notice.publication_date else "(missing)"
        )
        metadata = (
            f"Notice / lot  {safe(notice_identity(notice.publication_number, notice.lot_id))}\n"
            f"Buyer  {safe(notice.buyer)}\n"
            f"Deadline  {deadline}\n"
            f"Published  {publication_date}\n"
            f"Supplied source  {safe(notice.source_url)}\n"
        )
        reasons = "".join(f"• {normalize_display_text(reason)}\n" for reason in result.reasons)
        if result.unknowns:
            unknowns = "".join(
                f"• {normalize_display_text(unknown)}\n" for unknown in result.unknowns
            )
        else:
            unknowns = "No unresolved fields in the supplied metadata.\n"
        self._replace_details(
            [
                (
                    f"{_VERDICT_LABELS[result.verdict.value].upper()}\n",
                    f"verdict_{result.verdict.value}",
                ),
                (f"{safe(notice.title, '(title missing)')}\n", "detail_title"),
                (metadata, "detail_meta"),
                ("Why this result\n", "detail_section"),
                (reasons, "detail_body"),
                ("Unknowns\n", "detail_section"),
                (unknowns, "detail_body"),
                ("Human next step\n", "detail_section"),
                (
                    normalize_display_text(result.human_next_step),
                    "detail_body",
                ),
            ]
        )

    def _show_error(self, title: str, error: Exception, focus_widget: Any) -> None:
        message = normalize_display_text(str(error))
        self._set_status(f"Error: {message}", "error")
        self.root.bell()
        self.messagebox.showerror(title, message, parent=self.root)
        focus_widget.focus_set()


def _desktop_smoke_test(
    tk: Any,
    ttk: Any,
    filedialog: Any,
    messagebox: Any,
    tkfont: Any,
) -> None:
    interpreter = tk.Tcl()
    if not interpreter.eval("info patch"):
        raise RuntimeError("Tcl runtime is unavailable")
    root = tk.Tk()
    try:
        app = TenderVerdictApp(root, tk, ttk, filedialog, messagebox, tkfont)
        root.geometry("860x680")
        root.update()
        if not str(root.cget("menu")):
            raise RuntimeError("desktop menu is not configured")
        if str(app.file_menu.entrycget(app.export_menu_index, "state")) != "disabled":
            raise RuntimeError("desktop export menu must start disabled")
        if str(app.edit_menu.entrycget(app.copy_menu_index, "state")) != "disabled":
            raise RuntimeError("desktop copy menu must start disabled")
        if (
            str(app.file_menu.entrycget(app.save_csv_example_menu_index, "label"))
            != "Save CSV Example…"
        ):
            raise RuntimeError("desktop CSV example action is not configured")
        modifier = "Command" if app._windowing_system == "aqua" else "Control"
        if not root.bind_all(f"<{modifier}-KeyPress>"):
            raise RuntimeError("desktop keyboard shortcuts are not registered")
        keycode = 2 if app._windowing_system == "aqua" else 68
        event = argparse.Namespace(keycode=keycode, keysym="d")
        if app._handle_shortcut(event) != "break":
            raise RuntimeError("desktop demo shortcut was not handled")
        root.update()
        if app._current_run is None:
            raise RuntimeError("desktop demo shortcut did not run")
        if str(app.file_menu.entrycget(app.export_menu_index, "state")) != "normal":
            raise RuntimeError("desktop export menu was not enabled after a review")
        if str(app.edit_menu.entrycget(app.copy_menu_index, "state")) != "normal":
            raise RuntimeError("desktop copy menu was not enabled after a review")
        app.verdict_filter_var.set("Watch")
        app._refresh_results()
        root.update()
        if len(app.results_tree.get_children()) != 1:
            raise RuntimeError("desktop verdict filter did not preserve exactly one watch result")

        def bottom_in_root(widget: Any) -> int:
            bottom = int(widget.winfo_height())
            current = widget
            while current is not root:
                bottom += int(current.winfo_y())
                current = current.master
            return bottom

        def right_in_root(widget: Any) -> int:
            right = int(widget.winfo_width())
            current = widget
            while current is not root:
                right += int(current.winfo_x())
                current = current.master
            return right

        for name, widget in (
            ("primary review action", app.run_button),
            ("review status", app.status_label),
            ("result queue", app.results_tree),
            ("selected notice detail", app.details_text),
        ):
            has_layout = widget.winfo_width() > 1 and widget.winfo_height() > 1
            widget_bottom = bottom_in_root(widget)
            widget_right = right_in_root(widget)
            if (
                not has_layout
                or widget_bottom > root.winfo_height()
                or widget_right > root.winfo_width()
            ):
                widget_size = f"{widget.winfo_width()}x{widget.winfo_height()}"
                root_size = f"{root.winfo_width()}x{root.winfo_height()}"
                raise RuntimeError(
                    f"{name} is not laid out within the minimum window size "
                    f"(widget={widget_size}, right={widget_right}, bottom={widget_bottom}, "
                    f"root={root_size})"
                )
    finally:
        root.destroy()
    summary = demo_run().summary
    expected = {"total": 3, "open_documents": 1, "watch": 1, "reject": 1}
    if summary != expected:
        raise RuntimeError("bundled desktop demo does not match the expected verdicts")
    if getattr(sys, "frozen", False):
        import importlib.util

        for excluded_module in ("tenderverdict.cli", "tenderverdict.ted"):
            if importlib.util.find_spec(excluded_module) is not None:
                raise RuntimeError(f"desktop bundle unexpectedly contains {excluded_module}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Launch the local TenderVerdict desktop preview.")
    parser.add_argument("--smoke-test", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    try:
        tk, ttk, filedialog, messagebox, tkfont = _load_tkinter()
    except DesktopUnavailableError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.smoke_test:
        try:
            _desktop_smoke_test(tk, ttk, filedialog, messagebox, tkfont)
        except (RuntimeError, OSError, tk.TclError) as exc:
            print(f"error: desktop smoke test failed: {exc}", file=sys.stderr)
            return 2
        return 0
    try:
        root = tk.Tk()
    except tk.TclError as exc:
        print(f"error: unable to start the desktop interface: {exc}", file=sys.stderr)
        return 2

    TenderVerdictApp(root, tk, ttk, filedialog, messagebox, tkfont)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
