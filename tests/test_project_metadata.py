from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tomllib
import unittest
from pathlib import Path

from tenderverdict import __version__

ROOT = Path(__file__).resolve().parents[1]


class ProjectMetadataTests(unittest.TestCase):
    def test_repository_text_checkout_is_cross_platform_deterministic(self) -> None:
        attributes = (ROOT / ".gitattributes").read_text(encoding="ascii").splitlines()
        self.assertIn("* text=auto eol=lf", attributes)
        for pattern in ("*.icns binary", "*.ico binary", "*.png binary"):
            self.assertIn(pattern, attributes)

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
        requirements = (ROOT / "requirements-desktop-build.txt").read_text(encoding="utf-8")
        spec = (ROOT / "packaging" / "TenderVerdict.spec").read_text(encoding="utf-8")

        self.assertIn("pyinstaller==6.21.0", requirements)
        self.assertIn("hatchling==1.27.0", requirements)
        self.assertIn("--hash=sha256:", requirements)
        self.assertNotIn(">=", requirements)
        self.assertIn('"tenderverdict.cli"', spec)
        self.assertIn('"tenderverdict.ted"', spec)
        self.assertIn("console=False", spec)
        self.assertIn("upx=False", spec)
        self.assertIn("icon=str(ICON_PATH)", spec)
        self.assertIn('"tenderverdict/data"', spec)
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
        self.assertIn("desktop_build_lock_sha256=", manifest)
        self.assertIn("build_tools=", manifest)
        self.assertIn('f"public_release={str(args.public_release).lower()}"', manifest)
        self.assertIn("--public-release requires --ci provenance", manifest)
        workflow = (ROOT / ".github" / "workflows" / "desktop.yml").read_text(encoding="utf-8")
        self.assertIn("release_args+=(--public-release)", workflow)
        self.assertIn('$releaseArgs += "--public-release"', workflow)
        self.assertIn('github.event_name }}" == "workflow_dispatch"', workflow)

    def test_bundled_vocabularies_match_source_metadata(self) -> None:
        data = ROOT / "src" / "tenderverdict" / "data"
        metadata = json.loads((data / "VOCABULARY_SOURCES.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["retrieved_on"], "2026-08-04")
        for key, filename in (("cpv", "cpv_codes.txt"), ("countries", "country_codes.txt")):
            payload = (data / filename).read_bytes()
            self.assertEqual(metadata[key]["records"], len(payload.splitlines()))
            self.assertEqual(metadata[key]["sha256"], hashlib.sha256(payload).hexdigest())

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

    def test_next_gen_sdk_pin_and_ci_are_explicit(self) -> None:
        package_root = ROOT / "macos" / "TenderVerdictNextGen"
        package = (package_root / "Package.swift").read_text(encoding="utf-8")
        resolved = json.loads((package_root / "Package.resolved").read_text(encoding="utf-8"))
        workflow = (ROOT / ".github" / "workflows" / "desktop.yml").read_text(encoding="utf-8")
        metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

        self.assertIn('exact: "5.83.0"', package)
        self.assertEqual(len(resolved["pins"]), 1)
        pin = resolved["pins"][0]
        self.assertEqual(pin["identity"], "purchases-ios")
        self.assertEqual(pin["state"]["version"], "5.83.0")
        self.assertEqual(
            pin["state"]["revision"],
            "c69a23f56c63bdfe96096fa64a1c65334d2592db",
        )
        self.assertIn("swift build --package-path macos/TenderVerdictNextGen", workflow)
        self.assertIn("TenderVerdictNextGenChecks", workflow)
        self.assertIn("TenderVerdictNextGen --smoke-test", workflow)
        self.assertIn("python tools/build_next_gen.py", workflow)
        self.assertIn("TenderVerdictNextGen-macos-${{ github.sha }}", workflow)
        self.assertNotIn("REVENUECAT_TEST_STORE_API_KEY", workflow)
        self.assertIn("/macos", metadata["tool"]["hatch"]["build"]["targets"]["sdist"]["include"])
        self.assertIn(
            "/submission",
            metadata["tool"]["hatch"]["build"]["targets"]["sdist"]["include"],
        )
        self.assertIn(
            "/AGENTS.md",
            metadata["tool"]["hatch"]["build"]["targets"]["sdist"]["include"],
        )

        core_spec = (ROOT / "packaging" / "TenderVerdictNextGenCore.spec").read_text(
            encoding="utf-8"
        )
        next_gen_builder = (ROOT / "tools" / "build_next_gen.py").read_text(encoding="utf-8")
        self.assertIn('"tenderverdict.ted"', core_spec)
        self.assertIn("console=True", core_spec)
        self.assertIn("--smoke-test", next_gen_builder)
        self.assertIn('"normalize-workspace"', next_gen_builder)
        self.assertIn('"inspect-notices"', next_gen_builder)
        self.assertIn("_verify_embedded_core", next_gen_builder)
        self.assertIn('"codesign", "--verify"', next_gen_builder)
        self.assertIn("api_key_included=false", next_gen_builder)
        self.assertIn('choices=("debug", "release")', next_gen_builder)
        self.assertIn('f"build_configuration={configuration}"', next_gen_builder)
        self.assertIn(
            "f\"test_store_enabled={str(configuration == 'debug').lower()}\"",
            next_gen_builder,
        )
        self.assertIn('project_version = metadata["project"]["version"]', next_gen_builder)
        self.assertIn('swift_checks = swift_bin_path / f"{APP_NAME}Checks"', next_gen_builder)
        self.assertIn(
            "swift format lint --recursive --strict macos/TenderVerdictNextGen",
            workflow,
        )
        self.assertIn(
            "swift run -c release --package-path macos/TenderVerdictNextGen",
            workflow,
        )

    def test_local_markdown_links_resolve_inside_the_public_tree(self) -> None:
        allowlist = (ROOT / "PUBLIC_TREE_ALLOWLIST.txt").read_text(encoding="utf-8").splitlines()
        local_link = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
        html_fragment = re.compile(r'href="#([^"]+)"')
        heading = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)

        def heading_slug(value: str) -> str:
            plain = value.replace("`", "").lower()
            plain = re.sub(r"[^\w\- ]", "", plain)
            return re.sub(r" +", "-", plain.strip())

        for relative in allowlist:
            if not relative.endswith(".md"):
                continue
            document = ROOT / relative
            content = document.read_text(encoding="utf-8")
            for raw_target in local_link.findall(content):
                target = raw_target.strip().strip("<>")
                if target.startswith(("#", "https://", "http://", "mailto:")):
                    continue
                path_text = target.split("#", 1)[0]
                resolved = document.parent / path_text
                self.assertTrue(
                    resolved.exists(),
                    f"{relative} contains a broken local link: {raw_target}",
                )

            fragments = {heading_slug(value) for value in heading.findall(content)}
            for fragment in html_fragment.findall(content):
                self.assertIn(
                    fragment,
                    fragments,
                    f"{relative} contains a broken local fragment: #{fragment}",
                )

        documentation_index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
        for required in ("DEVELOPMENT.md", "DOCUMENTATION.md", "TECHNICAL_AUDIT.md"):
            self.assertIn(required, documentation_index)

        agent_guide = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        for required in (
            "docs/README.md",
            "docs/PROJECT_STATUS.md",
            "docs/ARCHITECTURE.md",
            "docs/DEVELOPMENT.md",
            "docs/DOCUMENTATION.md",
        ):
            self.assertIn(required, agent_guide)


if __name__ == "__main__":
    unittest.main()
