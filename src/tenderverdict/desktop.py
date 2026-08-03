"""Cross-platform local desktop interface for TenderVerdict."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import stat
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .demo_data import demo_notices
from .models import (
    Profile,
    QualificationResult,
    SchemaValidationError,
    notices_from_data,
    notices_from_json_bytes,
    parse_iso_date,
    profile_from_dict,
    profile_from_json_bytes,
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

MAX_PROFILE_FILE_BYTES = 256 * 1024
MAX_NOTICES_FILE_BYTES = 10 * 1024 * 1024
DEMO_NOTICE_LABEL = "Bundled synthetic notices (offline)"
_TOKEN_SEPARATOR = re.compile(r"[,;\s]+")
_VERDICT_LABELS = {
    "open_documents": "Open documents",
    "watch": "Watch",
    "reject": "Reject",
}
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
class LocalJsonSnapshot:
    """One bounded local-file snapshot and its export provenance."""

    path: Path
    payload: bytes
    sha256: str


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


def read_local_json_snapshot(
    raw_path: str,
    *,
    label: str,
    maximum_bytes: int,
) -> LocalJsonSnapshot:
    """Read one regular local file once, within the desktop input budget."""

    if not raw_path.strip():
        raise SchemaValidationError(f"Choose a {label} JSON file.")
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
    return LocalJsonSnapshot(
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
        f"Notice: {safe(notice.publication_number)}",
        f"Title: {safe(notice.title)}",
        f"Buyer: {safe(notice.buyer)}",
        f"Deadline: {notice.deadline.isoformat() if notice.deadline else '(missing)'}",
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

        root.title("TenderVerdict — desktop preview")
        root.geometry("1020x800")
        root.minsize(780, 720)
        root.option_add("*tearOff", False)

        self.style = ttk.Style(root)
        self.style.configure("Action.TButton", padding=(12, 8))
        self.style.configure("Section.TLabelframe", padding=(12, 10))

        default_font = tkfont.nametofont("TkDefaultFont")
        title_font = default_font.copy()
        title_font.configure(size=max(default_font.cget("size") + 6, 17), weight="bold")
        subtitle_font = default_font.copy()
        subtitle_font.configure(size=max(default_font.cget("size") + 1, 11))
        summary_font = default_font.copy()
        summary_font.configure(weight="bold")
        self.style.configure("Title.TLabel", font=title_font)
        self.style.configure("Subtitle.TLabel", font=subtitle_font)
        self.style.configure("Summary.TLabel", font=summary_font)

        self.name_var = tk.StringVar()
        self.cpv_var = tk.StringVar()
        self.countries_var = tk.StringVar()
        self.minimum_days_var = tk.StringVar(value="14")
        self.notices_path_var = tk.StringVar()
        self.as_of_var = tk.StringVar()
        self.status_var = tk.StringVar(
            value="Enter a supplier profile and choose normalized notices, or try the demo."
        )
        self.total_var = tk.StringVar(value="Total —")
        self.open_var = tk.StringVar(value="Open documents —")
        self.watch_var = tk.StringVar(value="Watch —")
        self.reject_var = tk.StringVar(value="Reject —")

        root.columnconfigure(0, weight=1)
        root.rowconfigure(4, weight=1)
        self._build_header()
        self._build_profile_section()
        self._build_notice_section()
        self._build_actions()
        self._build_results()
        self._bind_shortcuts()

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

    def _build_header(self) -> None:
        header = self.ttk.Frame(self.root, padding=(18, 16, 18, 8))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        self.ttk.Label(header, text="TenderVerdict", style="Title.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        self.ttk.Label(
            header,
            text=(
                "Review notice metadata locally. No uploads, no AI, and no automatic "
                "participation decision."
            ),
            style="Subtitle.TLabel",
            wraplength=900,
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

    def _build_profile_section(self) -> None:
        frame = self.ttk.LabelFrame(
            self.root,
            text="1. Supplier profile",
            style="Section.TLabelframe",
        )
        frame.grid(row=1, column=0, sticky="ew", padx=18, pady=(8, 6))
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(3, weight=1)

        self.ttk.Label(frame, text="Company name").grid(row=0, column=0, sticky="w")
        self.name_entry = self.ttk.Entry(frame, textvariable=self.name_var)
        self.name_entry.grid(row=0, column=1, columnspan=3, sticky="ew", padx=(10, 0))

        self.ttk.Label(frame, text="CPV codes").grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.cpv_entry = self.ttk.Entry(frame, textvariable=self.cpv_var)
        self.cpv_entry.grid(row=1, column=1, sticky="ew", padx=(10, 16), pady=(10, 0))
        self.ttk.Label(frame, text="Countries").grid(row=1, column=2, sticky="w", pady=(10, 0))
        self.countries_entry = self.ttk.Entry(frame, textvariable=self.countries_var)
        self.countries_entry.grid(row=1, column=3, sticky="ew", padx=(10, 0), pady=(10, 0))

        self.ttk.Label(
            frame,
            text="Separate codes with commas; use 8-digit CPV and 3-letter country codes.",
        ).grid(row=2, column=1, columnspan=3, sticky="w", pady=(4, 0))

        self.ttk.Label(frame, text="Minimum days to deadline").grid(
            row=3, column=0, sticky="w", pady=(10, 0)
        )
        self.minimum_days_entry = self.ttk.Spinbox(
            frame,
            from_=0,
            to=3650,
            textvariable=self.minimum_days_var,
            width=8,
        )
        self.minimum_days_entry.grid(row=3, column=1, sticky="w", padx=(10, 0), pady=(10, 0))

        profile_actions = self.ttk.Frame(frame)
        profile_actions.grid(row=3, column=2, columnspan=2, sticky="e", pady=(10, 0))
        self.ttk.Button(
            profile_actions,
            text="Load profile…",
            command=self._load_profile,
            style="Action.TButton",
        ).grid(row=0, column=0, padx=(0, 8))
        self.ttk.Button(
            profile_actions,
            text="Save profile…",
            command=self._save_profile,
            style="Action.TButton",
        ).grid(row=0, column=1)

    def _build_notice_section(self) -> None:
        frame = self.ttk.LabelFrame(
            self.root,
            text="2. Notice metadata",
            style="Section.TLabelframe",
        )
        frame.grid(row=2, column=0, sticky="ew", padx=18, pady=6)
        frame.columnconfigure(1, weight=1)

        self.ttk.Label(frame, text="Notices JSON").grid(row=0, column=0, sticky="w")
        self.notices_entry = self.ttk.Entry(
            frame,
            textvariable=self.notices_path_var,
            state="readonly",
        )
        self.notices_entry.grid(row=0, column=1, sticky="ew", padx=(10, 10))
        self.choose_notices_button = self.ttk.Button(
            frame,
            text="Choose notices…",
            command=self._choose_notices,
            style="Action.TButton",
        )
        self.choose_notices_button.grid(row=0, column=2)
        self.ttk.Label(
            frame,
            text=("Use TenderVerdict notice JSON. New here? Try the synthetic demo first."),
        ).grid(row=1, column=1, columnspan=2, sticky="w", pady=(4, 0))

    def _build_actions(self) -> None:
        frame = self.ttk.Frame(self.root, padding=(18, 6, 18, 8))
        frame.grid(row=3, column=0, sticky="ew")
        frame.columnconfigure(3, weight=1)

        self.ttk.Label(frame, text="Review date").grid(row=0, column=0, sticky="w")
        self.as_of_entry = self.ttk.Entry(frame, textvariable=self.as_of_var, width=14)
        self.as_of_entry.grid(row=0, column=1, sticky="w", padx=(10, 6))
        self.ttk.Label(frame, text="YYYY-MM-DD (required)").grid(row=0, column=2, sticky="w")
        self.ttk.Button(
            frame,
            text="Try synthetic demo",
            command=self._run_demo,
            style="Action.TButton",
        ).grid(row=0, column=4, padx=(12, 8))
        self.run_button = self.ttk.Button(
            frame,
            text="Run review",
            command=self._run_review,
            style="Action.TButton",
        )
        self.run_button.grid(row=0, column=5)
        self.ttk.Label(
            frame,
            textvariable=self.status_var,
            wraplength=900,
        ).grid(row=1, column=0, columnspan=6, sticky="w", pady=(8, 0))

    def _build_results(self) -> None:
        outer = self.ttk.LabelFrame(
            self.root,
            text="3. Review results",
            style="Section.TLabelframe",
        )
        outer.grid(row=4, column=0, sticky="nsew", padx=18, pady=(6, 18))
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(1, weight=1)

        summary = self.ttk.Frame(outer)
        summary.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        for column, variable in enumerate(
            (self.total_var, self.open_var, self.watch_var, self.reject_var)
        ):
            summary.columnconfigure(column, weight=1)
            self.ttk.Label(summary, textvariable=variable, style="Summary.TLabel").grid(
                row=0, column=column, sticky="w", padx=(0, 14)
            )
        self.export_button = self.ttk.Button(
            summary,
            text="Export report…",
            command=self._export_report,
            state="disabled",
            style="Action.TButton",
        )
        self.export_button.grid(row=0, column=4, sticky="e")

        panes = self.ttk.Panedwindow(outer, orient=self.tk.HORIZONTAL)
        panes.grid(row=1, column=0, sticky="nsew")

        list_frame = self.ttk.Frame(panes)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        self.results_tree = self.ttk.Treeview(
            list_frame,
            columns=("verdict", "notice", "title"),
            show="headings",
            selectmode="browse",
        )
        self.results_tree.heading("verdict", text="Verdict")
        self.results_tree.heading("notice", text="Notice")
        self.results_tree.heading("title", text="Title")
        self.results_tree.column("verdict", width=120, minwidth=105, stretch=False)
        self.results_tree.column("notice", width=135, minwidth=105, stretch=False)
        self.results_tree.column("title", width=220, minwidth=150, stretch=True)
        tree_scroll = self.ttk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.results_tree.yview,
        )
        tree_x_scroll = self.ttk.Scrollbar(
            list_frame,
            orient="horizontal",
            command=self.results_tree.xview,
        )
        self.results_tree.configure(
            yscrollcommand=tree_scroll.set,
            xscrollcommand=tree_x_scroll.set,
        )
        self.results_tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll.grid(row=0, column=1, sticky="ns")
        tree_x_scroll.grid(row=1, column=0, sticky="ew")
        self.results_tree.bind("<<TreeviewSelect>>", self._show_selected_result)

        detail_frame = self.ttk.Frame(panes)
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(1, weight=1)
        self.ttk.Label(detail_frame, text="Selected notice details").grid(
            row=0, column=0, sticky="w", pady=(0, 6)
        )
        self.details_text = self.tk.Text(
            detail_frame,
            wrap="word",
            state="disabled",
            takefocus=True,
            borderwidth=1,
            relief="solid",
            highlightthickness=1,
            padx=10,
            pady=10,
        )
        detail_scroll = self.ttk.Scrollbar(
            detail_frame,
            orient="vertical",
            command=self.details_text.yview,
        )
        self.details_text.configure(yscrollcommand=detail_scroll.set)
        self.details_text.grid(row=1, column=0, sticky="nsew")
        detail_scroll.grid(row=1, column=1, sticky="ns")
        self._set_details(
            "Run a review, then select a notice to read its reasons, unknowns, and next step."
        )

        panes.add(list_frame, weight=3)
        panes.add(detail_frame, weight=2)

    def _bind_shortcuts(self) -> None:
        self._windowing_system = str(self.root.tk.call("tk", "windowingsystem"))
        modifier = "Command" if self._windowing_system == "aqua" else "Control"
        self.root.bind_all(f"<{modifier}-KeyPress>", self._handle_shortcut)

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
        if self._suspend_stale or self._current_run is None:
            return
        if self._input_signature() != self._current_signature:
            self._clear_results("Inputs changed. Run the review again before exporting.")

    def _choose_notices(self) -> None:
        selected = self.filedialog.askopenfilename(
            title="Choose normalized notices JSON",
            filetypes=(("JSON files", "*.json"), ("All files", "*")),
        )
        if selected:
            self._using_demo_notices = False
            self.notices_path_var.set(selected)
            self.status_var.set("Notices selected. Confirm the review date, then run the review.")
            self.as_of_entry.focus_set()

    def _load_profile(self) -> None:
        selected = self.filedialog.askopenfilename(
            title="Load supplier profile",
            filetypes=(("JSON files", "*.json"), ("All files", "*")),
        )
        if not selected:
            return
        try:
            snapshot = read_local_json_snapshot(
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
            self.status_var.set(f"Loaded profile {snapshot.path.name}.")
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
        self.status_var.set(f"Saved profile as {Path(selected).name}.")

    def _run_demo(self) -> None:
        run = demo_run()
        self._suspend_stale = True
        try:
            self._set_profile_fields(run.profile)
            self._using_demo_notices = True
            self.notices_path_var.set(DEMO_NOTICE_LABEL)
            self.as_of_var.set(run.as_of.isoformat())
        finally:
            self._suspend_stale = False
        self._display_run(run, notices_sha256=None)
        self.status_var.set("Synthetic demo complete. No network request was made.")

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
            as_of = parse_iso_date(self.as_of_var.get().strip(), "Review date")
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
                snapshot = read_local_json_snapshot(
                    self.notices_path_var.get(),
                    label="notices",
                    maximum_bytes=MAX_NOTICES_FILE_BYTES,
                )
                notices_sha256 = snapshot.sha256
                run = qualify_inputs(
                    profile,
                    notices_from_json_bytes(snapshot.payload, snapshot.path),
                    as_of=as_of,
                )
        except (SchemaValidationError, OSError, ValueError) as exc:
            self._show_error("Review not created", exc, self.choose_notices_button)
            return
        self._display_run(run, notices_sha256=notices_sha256)
        self.status_var.set(f"Review complete: {len(run.results)} notices. No files were uploaded.")

    def _display_run(self, run: QualificationRun, *, notices_sha256: str | None) -> None:
        self._current_run = run
        self._current_signature = self._input_signature()
        self._current_notices_sha256 = notices_sha256
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        for index, result in enumerate(run.results):
            notice = result.notice
            self.results_tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    _VERDICT_LABELS[result.verdict.value],
                    normalize_display_text(notice.publication_number),
                    normalize_display_text(notice.title or "(title missing)"),
                ),
            )
        summary = run.summary
        self.total_var.set(f"Total {summary['total']}")
        self.open_var.set(f"Open documents {summary['open_documents']}")
        self.watch_var.set(f"Watch {summary['watch']}")
        self.reject_var.set(f"Reject {summary['reject']}")
        self.export_button.configure(state="normal")
        if run.results:
            first = self.results_tree.get_children()[0]
            self.results_tree.selection_set(first)
            self.results_tree.focus(first)
            self.results_tree.see(first)
            self._show_selected_result()
            self.results_tree.focus_set()
        else:
            self._set_details(
                "No notices were supplied. Choose another notices file and run again."
            )

    def _show_selected_result(self, _event: object | None = None) -> None:
        if self._current_run is None:
            return
        selection = self.results_tree.selection()
        if not selection:
            return
        index = int(selection[0])
        self._set_details(format_result_details(self._current_run.results[index]))

    def _export_report(self) -> None:
        if self._current_run is None or self._input_signature() != self._current_signature:
            self.status_var.set("Run the current inputs before exporting a report.")
            return
        if not self._notices_are_current():
            return
        initialfile = f"tenderverdict-report-{self._current_run.as_of.isoformat()}.html"
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
        self.status_var.set(f"Exported report as {Path(selected).name}.")

    def _notices_are_current(self) -> bool:
        if self._current_notices_sha256 is None:
            return True
        try:
            snapshot = read_local_json_snapshot(
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
        self.total_var.set("Total —")
        self.open_var.set("Open documents —")
        self.watch_var.set("Watch —")
        self.reject_var.set("Reject —")
        self.export_button.configure(state="disabled")
        self._set_details("Run the current inputs to create a new review.")
        self.status_var.set(status)

    def _set_details(self, content: str) -> None:
        self.details_text.configure(state="normal")
        self.details_text.delete("1.0", "end")
        self.details_text.insert("1.0", content)
        self.details_text.configure(state="disabled")

    def _show_error(self, title: str, error: Exception, focus_widget: Any) -> None:
        message = normalize_display_text(str(error))
        self.status_var.set(f"Error: {message}")
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
        root.update()
        app.name_entry.focus_force()
        root.update()
        modifier = "Command" if root.tk.call("tk", "windowingsystem") == "aqua" else "Control"
        app.name_entry.event_generate(f"<{modifier}-KeyPress-d>")
        root.update()
        if app._current_run is None:
            raise RuntimeError("desktop demo shortcut did not run")
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
