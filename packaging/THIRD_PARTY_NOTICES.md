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

## Release boundary

The CI manifest records the exact Python, Tcl/Tk, and PyInstaller versions used for each artifact.
Before any public desktop release, the extracted target bundle and the license files supplied by
that target toolchain must be reviewed again. This notice is not a claim that an unsigned CI
artifact is ready for redistribution.
