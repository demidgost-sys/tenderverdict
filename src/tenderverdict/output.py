"""Safe output helpers shared by the CLI and desktop application."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


def write_text_atomically(destination: str | Path, content: str) -> None:
    """Replace ``destination`` only after a complete, flushed UTF-8 write."""

    destination = Path(destination).expanduser()
    parent = destination.parent
    if not parent.is_dir():
        raise OSError(f"output directory does not exist: {parent}")

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            prefix=f".{destination.name}.",
            suffix=".tmp",
            dir=parent,
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, destination)
    except BaseException:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
        raise
