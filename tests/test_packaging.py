"""Offline checks for supply-chain pins, package gates and safe installation."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import timeoutctl as ctl


class PackagingContract(unittest.TestCase):
    def test_formula_matches_source_lock(self):
        formula = (ROOT / "Formula/timeout.rb").read_text()
        for key in ("url", "mirror", "sha256"):
            self.assertIn(ctl.LOCK[key], formula)
        for argument in ctl.LOCK["configure"]:
            self.assertIn(f'"{argument}"', formula)
        self.assertIn('"src/timeout"', formula)
        self.assertNotIn('"make", "install"', formula)

    def test_version_tracks_upstream(self):
        self.assertRegex((ROOT / "VERSION").read_text().strip(), r"^" + ctl.LOCK["version"].replace(".", r"\.") + r"\.\d+$")
        self.assertRegex(ctl.LOCK["sha256"], r"^[a-f0-9]{64}$")

    def test_checksum_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "archive"
            path.write_bytes(b"wrong source")
            with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                ctl.verify_archive(path)

    def test_checksum_accepts_exact_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "archive"
            path.write_bytes(b"fixture")
            with mock.patch.dict(ctl.LOCK, sha256=hashlib.sha256(b"fixture").hexdigest()):
                ctl.verify_archive(path)

    def test_offline_fetch_validates_before_copying(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            archive = base / "input"
            archive.write_bytes(b"fixture")
            with mock.patch.multiple(ctl, BUILD=base / "build", ARCHIVE=base / "build/source"), \
                    mock.patch.dict(ctl.LOCK, sha256=hashlib.sha256(b"fixture").hexdigest()):
                result = ctl.fetch(archive)
                self.assertEqual(result.read_bytes(), b"fixture")

    def test_package_requires_verification_receipt(self):
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(ctl, "require_build"), \
                mock.patch.object(ctl, "REPORTS", Path(directory)):
            with self.assertRaisesRegex(RuntimeError, "complete test gate"):
                ctl.package()

    def test_package_rejects_changed_binary(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / "verified.json").write_text('{"binary_sha256": "old"}')
            (base / "timeout").write_bytes(b"new")
            with mock.patch.object(ctl, "require_build"), \
                    mock.patch.multiple(ctl, REPORTS=base, BIN=base / "timeout"):
                with self.assertRaisesRegex(RuntimeError, "complete test gate"):
                    ctl.package()

    def test_upstream_source_modification_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = base / "coreutils-9.12"
            source.mkdir()
            file = source / "timeout.c"
            file.write_text("original")
            archive = base / "source.tar"
            with tarfile.open(archive, "w") as tar:
                tar.add(file, arcname="coreutils-9.12/timeout.c")
            with mock.patch.multiple(ctl, BUILD=base, ARCHIVE=archive), \
                    mock.patch.dict(ctl.LOCK, sha256=ctl.digest(archive)):
                ctl.assert_unmodified()
                file.write_text("modified")
                with self.assertRaisesRegex(ValueError, "Modified upstream source"):
                    ctl.assert_unmodified()

    def test_unsupported_platform_has_no_fallback(self):
        with mock.patch("platform.system", return_value="Windows"):
            with self.assertRaises(ValueError):
                ctl.target()

    def test_target_maps_apple_silicon(self):
        with mock.patch("platform.system", return_value="Darwin"), \
                mock.patch("platform.machine", return_value="arm64"):
            self.assertEqual(ctl.target(), "aarch64-apple-darwin")

    def test_living_spec_names_exist(self):
        text = (ROOT / "tests/test_timeout.py").read_text()
        for line in (ROOT / "features/timeout.feature").read_text().splitlines():
            if line.strip().startswith("Scenario:"):
                self.assertIn("def " + line.split(":", 1)[1].strip() + "(", text)

    def test_installer_shell_syntax(self):
        subprocess.run(["sh", "-n", str(ROOT / "install.sh")], check=True, timeout=5)


class InstallerContract(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.prefix = self.base / "prefix with spaces"
        self.fakebin = self.base / "fakebin"
        self.fakebin.mkdir()
        self.release = self.base / "release"
        self.release.mkdir()
        self.name = "timeout-9.12.0-aarch64-apple-darwin"
        stage = self.base / self.name
        (stage / "bin").mkdir(parents=True)
        binary = stage / "bin/timeout"
        binary.write_text("#!/bin/sh\nprintf 'installed fixture\\n'\n")
        binary.chmod(0o755)
        (stage / "share/doc/timeout").mkdir(parents=True)
        (stage / "share/doc/timeout/COPYING").write_text("fixture licence")
        archive = self.release / (self.name + ".tar.gz")
        with tarfile.open(archive, "w:gz") as tar:
            tar.add(stage, arcname=self.name)
        (self.release / "SHA256SUMS").write_text(f"{ctl.digest(archive)}  {archive.name}\n")
        self.write_command("uname", 'case "$1" in -s) echo Darwin;; -m) echo arm64;; esac\n')
        self.write_command("curl", 'destination=\nwhile [ "$#" -gt 1 ]; do\n'
                           '  if [ "$1" = --output ]; then destination=$2; shift; fi\nshift\ndone\n'
                           'case "$1" in https://github.com/KSonny4/timeout/releases/download/v9.12.0/*) ;; *) exit 91;; esac\n'
                           'cp "$FIXTURE_RELEASE/${1##*/}" "$destination"\n')
        self.env = dict(os.environ, PATH=str(self.fakebin) + os.pathsep + os.environ["PATH"],
                        FIXTURE_RELEASE=str(self.release))

    def write_command(self, name, body):
        path = self.fakebin / name
        path.write_text("#!/bin/sh\nset -eu\n" + body)
        path.chmod(0o755)

    def install(self, *args):
        return subprocess.run(["sh", str(ROOT / "install.sh"), "--version", "9.12.0", "--prefix", str(self.prefix), *args],
                              env=self.env, capture_output=True, text=True, timeout=10)

    def test_install_verified_release_without_root(self):
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(subprocess.check_output([str(self.prefix / "bin/timeout")], text=True), "installed fixture\n")
        self.assertEqual((self.prefix / "share/doc/timeout/COPYING").read_text(), "fixture licence")
        self.assertEqual(list((self.prefix / "bin").glob(".timeout-install.*")), [])

    def test_reinstall_refuses_overwrite(self):
        self.assertEqual(self.install().returncode, 0)
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing to overwrite", result.stderr)

    def test_dangling_symlink_is_not_overwritten(self):
        (self.prefix / "bin").mkdir(parents=True)
        link = self.prefix / "bin/timeout"
        link.symlink_to(self.base / "missing")
        self.assertNotEqual(self.install().returncode, 0)
        self.assertTrue(link.is_symlink())

    def test_bad_checksum_installs_nothing(self):
        (self.release / "SHA256SUMS").write_text(f"{'0' * 64}  {self.name}.tar.gz\n")
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("checksum mismatch", result.stderr)
        self.assertFalse((self.prefix / "bin/timeout").exists())

    def test_missing_checksum_installs_nothing(self):
        (self.release / "SHA256SUMS").write_text("")
        self.assertNotEqual(self.install().returncode, 0)
        self.assertFalse((self.prefix / "bin/timeout").exists())

    def test_invalid_version_is_rejected(self):
        result = self.install("--version", "../../bad")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("explicit numeric", result.stderr)

    def test_unknown_option_is_rejected(self):
        self.assertNotEqual(self.install("--force").returncode, 0)

    def test_relative_prefix_is_rejected(self):
        self.assertNotEqual(self.install("--prefix", "relative").returncode, 0)

    def test_unsupported_architecture_is_rejected(self):
        self.write_command("uname", 'case "$1" in -s) echo Darwin;; -m) echo unknown;; esac\n')
        self.assertNotEqual(self.install().returncode, 0)


if __name__ == "__main__":
    unittest.main()
