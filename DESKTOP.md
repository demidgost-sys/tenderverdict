# Desktop preview

TenderVerdict `0.2.0a1` adds a desktop developer alpha for macOS and Windows. It is a native,
local interface over the same deterministic qualification workflow used by the CLI.

The preview is intended for evaluation. It is not a signed consumer release or a replacement for
procurement, eligibility, or legal review.

## Release status

The source UI and unsigned native archives are published in the `v0.2.0-alpha.1` prerelease. Each
archive has a matching checksum and an embedded `BUILD_INFO.txt`. The macOS arm64 packaged flow has
completed hands-on evaluation. macOS Intel and Windows x64 pass native automated builds and frozen
smoke tests; the Windows archive has not yet completed a hands-on run.

The exact release and follow-on evidence gates are listed in [ROADMAP.md](ROADMAP.md). Do not advise
evaluators to disable Gatekeeper, SmartScreen, antivirus, or another operating-system security
control to run an unsigned artifact.

## What the desktop preview does

1. Enter a supplier name, CPV codes, countries, and a minimum lead time.
2. Choose a local normalized notices CSV or JSON file, save an editable CSV example, or use the
   bundled synthetic demo.
3. Enter an explicit review date or RFC 3339 instant with a UTC offset.
4. Filter by verdict, sort the queue by a column heading, inspect reasons and unknowns, and copy a
   selected result as plain text when useful.
5. Export a complete HTML, Markdown, or JSON report to a location you choose.

The file chooser validates notice data before accepting it and reports the failing CSV row when it
can. The editable example contains only fictional `SYN-` rows and uses `|` between multiple CPV or
country values. You can also load and save the small supplier profile as JSON. Changing any input
invalidates the visible result and disables export until the review is run again.

The desktop accepts at most 1,000 rows in a 10 MiB file. Duplicate notice identities and overlong
fields fail validation; separate verified `lot_id` values may share a publication number. CPV and
country codes are checked against the source-traceable EU snapshots bundled with the application.
Header-only CSV and empty JSON are treated consistently as a valid zero-notice review. Exported
reports include the TenderVerdict version and SHA-256 digests of the profile and notice inputs; a
saved TED snapshot also preserves its query and retrieval time.

The preview uses a two-pane review workspace: setup stays on the left, while verdict totals, the
notice queue, and a structured explanation stay visible on the right. The visual system follows the
operating system's light or dark appearance and uses one primary action for each review cycle.

Keyboard shortcuts use Command on macOS and Control on Windows: `D` runs the demo, `R` runs the
current review, `O` chooses notices, and `S` exports. Command/Control+Shift+C copies the selected
result. Latin and Russian keyboard layouts are handled for the main shortcuts. The same actions are
discoverable in the native File, Edit, and Review menus.

## Privacy and network boundary

- Profile and notice qualification stays in the local process.
- The desktop preview does not call the TED adapter or make another intentional network request.
- Nothing is uploaded automatically.
- Reports and profiles are written only after you choose a destination.
- Saving the CSV example is explicit and atomic; it never overwrites a file after a failed write.
- Failed validation or export does not intentionally replace an existing output with a partial
  file.
- A changed notice file cannot export the result created from its previous bytes.

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
python3 -m pip install --require-hashes --only-binary=:all: --no-deps \
  -r requirements-desktop-build.txt
python3 -m pip check
python3 -m pip install --no-build-isolation --no-deps .
python3 tools/build_desktop.py
```

GitHub Actions builds separate developer artifacts for macOS arm64, macOS Intel, and Windows x64.
The artifacts attached to `v0.2.0-alpha.1` are copied from the successful workflow for the tagged
commit; ordinary branch and pull-request artifacts remain short-lived.

Each archive is accompanied by a SHA-256 checksum and `BUILD_INFO.txt`, plus `START_HERE.txt` and
synthetic example data inside the archive. Verify the checksum and manifest before a manual test,
then record the commit, target, operating system, and completed workflow. An automated smoke test
is evidence that the application starts and its synthetic flow is intact; it is not a substitute
for a person completing the packaged workflow.

On macOS or Linux, verify a downloaded archive before extracting it:

```bash
shasum -a 256 -c TenderVerdict-macos-arm64.sha256
unzip -l TenderVerdict-macos-arm64.zip
```

On Windows PowerShell, compare the expected and calculated values explicitly:

```powershell
$expected = (Get-Content .\TenderVerdict-windows-x64.sha256).Split()[0].ToLowerInvariant()
$actual = (Get-FileHash .\TenderVerdict-windows-x64.zip -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $expected) { throw "TenderVerdict archive checksum mismatch" }
```

After extraction, inspect `BUILD_INFO.txt` and confirm that its commit and target match the workflow
run you intended to test.

The Python version and the complete Python build dependency set are pinned. CI accepts only
hash-verified wheels from the lock file, runs `pip check`, and records the lock digest, installed
tool versions, source commit, target, and hosted-runner image version in every archive. Hosted
runner images, system libraries, archive metadata, and platform toolchains are not immutable, so
artifacts remain source-pinned and traceable rather than claimed to be byte-for-byte reproducible.

## Trust and accessibility limits

- The macOS previews do not have Developer ID signing or Apple notarization. PyInstaller may apply
  an ad-hoc signature during assembly, which is not the same trust level.
- The Windows preview is not code-signed and may trigger reputation-based warnings.
- Do not represent a prerelease or CI artifact as a trusted installer.
- The interface uses labelled native controls, visible and focusable status text, keyboard
  traversal, clear focus treatment, filters, sortable headings, and explicit copy/open/save
  actions. Packaged keyboard behaviour still requires hands-on verification on each target.
- Screen-reader support is not confirmed. In one source-runtime check on macOS, the Tk controls
  were not exposed reliably in the accessibility tree. Do not rely on this preview for a
  screen-reader workflow until packaged builds pass VoiceOver and NVDA testing.
- This preview deliberately has no automatic updater or installer until there is a signed trust
  channel. It also does not include drag and drop, arbitrary TED CSV mapping, full-document
  parsing, or TED fetching. Network collection remains an explicit CLI-only action.
