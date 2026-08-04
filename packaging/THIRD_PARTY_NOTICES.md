# Third-party notices for desktop developer artifacts

The source package itself remains licensed under Apache-2.0. A frozen desktop artifact also
contains components supplied by its platform Python and build toolchain.

## CPython and the Python standard library

The embedded Python runtime and standard library are distributed under the Python Software
Foundation License Version 2 and the additional historical notices shipped with that runtime.

## Tcl/Tk

The native interface uses Tkinter and therefore packages Tcl/Tk components from the selected
Python distribution. Tcl/Tk is distributed under its upstream permissive license terms.

## PyInstaller bootloader

Developer artifacts are assembled with PyInstaller. PyInstaller is distributed under
GPL-2.0-or-later with a special exception that permits the distribution of bundled applications.

## EU vocabulary snapshots

The frozen application contains bounded CPV and country authority-code snapshots retrieved from
the Publications Office of the European Union. Their exact endpoint, queries, retrieval date,
record counts, and SHA-256 digests are recorded in
`tenderverdict/data/VOCABULARY_SOURCES.json`. TenderVerdict uses them for offline membership
validation. The Apache-2.0 license for TenderVerdict code does not relicense those data, provider
names, or trademarks.

## Release boundary

The CI manifest records the exact Python, Tcl/Tk, and PyInstaller versions used for each artifact.
A workflow-dispatch build intended for a public prerelease records `public_release=true`; ordinary
pull-request artifacts record `public_release=false`. This field records distribution intent, not
code-signing, notarization, support, or security status. Before each public desktop prerelease, the
extracted target bundle and the license files supplied by that target toolchain must be reviewed
again.
