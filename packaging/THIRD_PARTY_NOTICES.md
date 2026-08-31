# Third-party notices for developer artifacts

TenderVerdict source remains licensed under Apache-2.0. Frozen Python desktop artifacts and the
unreleased SwiftUI target also use components supplied by their platform toolchains and declared
dependencies.

## CPython and the Python standard library

The embedded Python runtime and standard library are distributed under the Python Software
Foundation License Version 2 and the additional historical notices shipped with that runtime.

## Tcl/Tk

The native interface uses Tkinter and therefore packages Tcl/Tk components from the selected
Python distribution. Tcl/Tk is distributed under its upstream permissive license terms.

## PyInstaller bootloader

Developer artifacts are assembled with PyInstaller. PyInstaller is distributed under
GPL-2.0-or-later with a special exception that permits the distribution of bundled applications.

## RevenueCat Purchases Apple SDK

The unreleased Next Gen Swift package declares RevenueCat `purchases-ios` `5.83.0`. The dependency
is distributed under the MIT License:

Copyright (c) 2024 RevenueCat, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT
OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

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
