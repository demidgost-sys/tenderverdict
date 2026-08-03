from __future__ import annotations

import os
import subprocess
import sys
import tomllib
import unittest
from pathlib import Path

from tenderverdict import __version__

ROOT = Path(__file__).resolve().parents[1]


class ProjectMetadataTests(unittest.TestCase):
    def test_versions_entry_points_and_dependency_boundary_match(self) -> None:
        metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        project = metadata["project"]

        self.assertEqual(project["version"], __version__)
        self.assertEqual(project["dependencies"], [])
        self.assertEqual(
            project["scripts"],
            {"tenderverdict": "tenderverdict.cli:main"},
        )
        self.assertEqual(
            project["gui-scripts"],
            {"tenderverdict-desktop": "tenderverdict.desktop:main"},
        )

    def test_desktop_build_tool_is_exact_and_network_adapter_is_excluded(self) -> None:
        requirements = [
            line.strip()
            for line in (ROOT / "requirements-desktop-build.txt")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        spec = (ROOT / "packaging" / "TenderVerdict.spec").read_text(encoding="utf-8")

        self.assertEqual(requirements, ["pyinstaller==6.21.0"])
        self.assertIn('"tenderverdict.cli"', spec)
        self.assertIn('"tenderverdict.ted"', spec)
        self.assertIn("console=False", spec)
        self.assertIn("upx=False", spec)
        self.assertIn("icon=str(ICON_PATH)", spec)
        self.assertIn("ROOT = Path(SPECPATH).parent\n", spec)
        self.assertIn('MACOS_BUNDLE_VERSION = PROJECT_VERSION.split("a", 1)[0]', spec)
        self.assertIn('"CFBundleShortVersionString": MACOS_BUNDLE_VERSION', spec)
        self.assertIn('"CFBundleVersion": MACOS_BUNDLE_VERSION', spec)
        self.assertNotIn("Path(SPECPATH).parent.parent", spec)
        self.assertTrue((ROOT / "packaging" / "tenderverdict-icon.icns").is_file())
        self.assertTrue((ROOT / "packaging" / "tenderverdict-icon.ico").is_file())
        manifest = (ROOT / "tools" / "write_build_manifest.py").read_text(encoding="utf-8")
        self.assertIn('"macos-arm64": ("Darwin", {"arm64", "aarch64"}, "adhoc")', manifest)
        self.assertIn("GITHUB_SHA must be a full lowercase 40-character commit SHA", manifest)

    def test_desktop_module_import_is_headless_and_does_not_load_ted(self) -> None:
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(ROOT / "src")
        command = (
            "import sys; import tenderverdict.desktop; "
            "assert 'tkinter' not in sys.modules; "
            "assert 'tenderverdict.ted' not in sys.modules"
        )

        result = subprocess.run(
            [sys.executable, "-c", command],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_ci_scans_generated_sdist_metadata_without_deleting_it(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

        self.assertIn('tools/check_public_tree.py --root "${sdist_root}" --sdist', workflow)
        self.assertIn('tools/security_scan.py --root "${sdist_root}" --sdist', workflow)
        self.assertNotIn('rm "${sdist_root}/PKG-INFO"', workflow)


if __name__ == "__main__":
    unittest.main()
