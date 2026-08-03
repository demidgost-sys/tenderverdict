# Desktop preview

TenderVerdict `0.2.0a1` adds an unreleased desktop preview for macOS and Windows. It is a native,
local interface over the same deterministic qualification workflow used by the CLI.

The preview is intended for evaluation. It is not a signed consumer release or a replacement for
procurement, eligibility, or legal review.

## What the desktop preview does

1. Enter a supplier name, CPV codes, countries, and a minimum lead time.
2. Choose a local normalized notices CSV or JSON file, save an editable CSV example, or use the
   bundled synthetic demo.
3. Enter an explicit review date.
4. Review the `open_documents`, `watch`, and `reject` results with their reasons, unknowns, and
   human next step.
5. Export a complete HTML, Markdown, or JSON report to a location you choose.

The file chooser validates notice data before accepting it and reports the failing CSV row when it
can. The editable example contains only fictional `SYN-` rows and uses `|` between multiple CPV or
country values. You can also load and save the small supplier profile as JSON. Changing any input
invalidates the visible result and disables export until the review is run again.

The preview uses a two-pane review workspace: setup stays on the left, while verdict totals, the
notice queue, and a structured explanation stay visible on the right. The visual system follows the
operating system's light or dark appearance and uses one primary action for each review cycle.

Keyboard shortcuts use Command on macOS and Control on Windows: `D` runs the demo, `R` runs the
current review, `O` chooses notices, and `S` exports. Latin and Russian keyboard layouts are handled
by the preview. The same actions are discoverable in the native File and Review menus.

## Privacy and network boundary

- Profile and notice qualification stays in the local process.
- The desktop preview does not call the TED adapter or make another intentional network request.
- Nothing is uploaded automatically.
- Reports and profiles are written only after you choose a destination.
- Saving the CSV example is explicit and atomic; it never overwrites a file after a failed write.
- Failed validation or export does not intentionally replace an existing output with a partial
  file.

The preview still consumes untrusted metadata. Keep confidential material outside this alpha and
read [LIMITATIONS.md](LIMITATIONS.md) before evaluating real workflows.

## Run from source

Use Python 3.11 or newer with Tk included. Confirm Tk is available before installing:

```bash
python3 -c "import tkinter; print(tkinter.TkVersion)"
```

Then create an isolated environment and launch the preview:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/tenderverdict desktop
```

On Windows PowerShell, use `py -m venv .venv` and
`.venv\Scripts\tenderverdict.exe desktop`.

The CLI remains available when Tk is not installed.

## Developer builds

Desktop bundles use a version-pinned PyInstaller build dependency and `--onedir --windowed`. Each
target is built on its own operating system; PyInstaller is not used as a cross-compiler.

```bash
python3 -m pip install -r requirements-desktop-build.txt
python3 -m pip install --no-build-isolation --no-deps .
python3 tools/build_desktop.py
```

GitHub Actions builds separate developer artifacts for macOS arm64, macOS Intel, and Windows x64.
They are short-lived CI artifacts, not GitHub Releases.

The direct build tool and Python version are pinned, and every archive gets a checksum and build
manifest. Transitive build wheels and hosted-runner images are not hash-locked in this preview, so
the artifacts are source-pinned and traceable, not claimed to be byte-for-byte reproducible.

## Trust and accessibility limits

- The macOS previews do not have Developer ID signing or Apple notarization. PyInstaller may apply
  an ad-hoc signature during assembly, which is not the same trust level.
- The Windows preview is not code-signed and may trigger reputation-based warnings.
- Do not redistribute a CI artifact as a trusted installer.
- The interface uses styled Tk controls with system fonts, visible status text, keyboard traversal,
  clear focus treatment, and common open/save shortcuts. Packaged keyboard behaviour still
  requires hands-on verification on each target platform.
- Screen-reader support is not confirmed. In one source-runtime check on macOS, the Tk controls
  were not exposed reliably in the accessibility tree. Do not rely on this preview for a
  screen-reader workflow until packaged builds pass VoiceOver and NVDA testing.
- This preview does not include automatic updates, an installer, drag and drop, arbitrary TED CSV
  mapping, full-document parsing, or TED fetching.
