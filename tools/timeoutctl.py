#!/usr/bin/env python3
"""Build, test and package unmodified GNU timeout. Python is build-time only."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / ".build"
DIST = ROOT / "dist"
LOCK = json.loads((ROOT / "upstream.json").read_text())
ARCHIVE = BUILD / f"coreutils-{LOCK['version']}.tar.xz"
SOURCE = BUILD / f"coreutils-{LOCK['version']}"
WORK = BUILD / "work"
BIN = WORK / "src" / "timeout"
REPORTS = BUILD / "reports"
JOBS = str(min(os.cpu_count() or 2, 8))


def digest(path: Path) -> str:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def run(args: list[str], *, cwd: Path = ROOT, env: dict | None = None,
        seconds: int = 900, check: bool = True) -> subprocess.CompletedProcess:
    print("+", " ".join(map(str, args)), flush=True)
    return subprocess.run(args, cwd=cwd, env=env, check=check, timeout=seconds)


def verify_archive(path: Path) -> None:
    actual = digest(path)
    if actual != LOCK["sha256"]:
        raise ValueError(f"Source checksum mismatch: expected {LOCK['sha256']}, got {actual}")


def fetch(archive: Path | None = None) -> Path:
    BUILD.mkdir(exist_ok=True)
    if archive is not None:
        verify_archive(archive)
        if archive.resolve() != ARCHIVE.resolve():
            shutil.copyfile(archive, ARCHIVE)
    if ARCHIVE.exists():
        verify_archive(ARCHIVE)
        return ARCHIVE
    errors = []
    for url in (LOCK["url"], LOCK["mirror"]):
        partial = ARCHIVE.with_suffix(".part")
        try:
            run(["curl", "--fail", "--location", "--proto", "=https", "--proto-redir", "=https",
                 "--connect-timeout", "20", "--max-time", "180", "--retry", "2",
                 "--output", str(partial), url], seconds=600)
            verify_archive(partial)
            partial.replace(ARCHIVE)
            return ARCHIVE
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            errors.append(f"{url}: {exc}")
        finally:
            partial.unlink(missing_ok=True)
    raise RuntimeError("Verified source download failed:\n" + "\n".join(errors))


def extract() -> None:
    verify_archive(ARCHIVE)
    if SOURCE.exists():
        shutil.rmtree(SOURCE)
    with tarfile.open(ARCHIVE) as tar:
        expected = f"coreutils-{LOCK['version']}"
        if any(Path(m.name).parts[0] != expected for m in tar.getmembers()):
            raise ValueError("Unexpected source archive layout")
        tar.extractall(BUILD, filter="data")


def assert_unmodified() -> None:
    """Check every shipped source file, including gnulib and all upstream tests."""
    verify_archive(ARCHIVE)
    with tarfile.open(ARCHIVE) as tar:
        for member in tar:
            if member.isfile():
                path = BUILD / member.name
                data = tar.extractfile(member)
                if data is None or not path.is_file():
                    raise ValueError(f"Missing upstream source: {member.name}")
                if digest(path) != hashlib.sha256(data.read()).hexdigest():
                    raise ValueError(f"Modified upstream source: {member.name}")
            elif member.issym():
                path = BUILD / member.name
                if not path.is_symlink() or os.readlink(path) != member.linkname:
                    raise ValueError(f"Modified upstream link: {member.name}")


def build(archive: Path | None = None) -> None:
    fetch(archive)
    extract()
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir()
    REPORTS.mkdir(exist_ok=True)
    env = os.environ.copy()
    if os.geteuid() == 0:
        env["FORCE_UNSAFE_CONFIGURE"] = "1"
    run([str(SOURCE / "configure"), *LOCK["configure"]], cwd=WORK, env=env)
    run(["make", f"-j{JOBS}", "src/timeout"], cwd=WORK, env=env)
    assert_unmodified()
    result = subprocess.check_output([str(BIN), "--version"], text=True).splitlines()[0]
    if result != f"timeout (GNU coreutils) {LOCK['version']}":
        raise ValueError(f"Unexpected executable version: {result}")
    record = {"upstream": LOCK, "platform": platform.platform(), "machine": platform.machine(),
              "binary_sha256": digest(BIN), "binary_bytes": BIN.stat().st_size, "version": result}
    (REPORTS / "build.json").write_text(json.dumps(record, indent=2) + "\n")


def require_build() -> None:
    if not BIN.is_file():
        raise RuntimeError("Build first: python3 tools/timeoutctl.py build")
    assert_unmodified()


def test_upstream(*, root_pid_namespace: bool = False) -> dict:
    require_build()
    helpers = ["env", "sleep", "kill", "getlimits", "true", "false", "printf", "yes"]
    run(["make", f"-j{JOBS}", *[f"src/{x}" for x in helpers]], cwd=WORK)
    env = os.environ.copy()
    if platform.system() == "Darwin" and shutil.which("setsid") is None:
        testbin = BUILD / "test-bin"
        testbin.mkdir(exist_ok=True)
        helper = testbin / "setsid"
        helper.write_text(f"#!{sys.executable}\nimport os, sys\nos.setsid()\nos.execvp(sys.argv[1], sys.argv[1:])\n")
        helper.chmod(0o755)
        env["PATH"] = str(testbin) + os.pathsep + env["PATH"]
    tests = sorted(p.relative_to(SOURCE).as_posix() for p in (SOURCE / "tests/timeout").iterdir()
                   if p.suffix in {".sh", ".pl"})
    if not tests:
        raise ValueError("Upstream timeout test inventory is empty")
    command = ["make", f"-j{JOBS}", "check-TESTS", "TESTS=" + " ".join(tests)]
    result = run(command, cwd=WORK, env=env, seconds=600, check=False)
    records = []
    for name in tests:
        trs = (WORK / name).with_suffix(".trs")
        log = (WORK / name).with_suffix(".log")
        if (root_pid_namespace and platform.system() == "Linux" and name.endswith("init-parent.sh")
                and trs.exists() and ":test-result: SKIP" in trs.read_text()):
            trs.unlink()
            log.unlink(missing_ok=True)
            run(["sudo", "-n", "make", "check-TESTS", "TESTS=" + name],
                cwd=WORK, env=env, seconds=120)
        text = trs.read_text() if trs.exists() else ""
        status = re.search(r"^:test-result: (\S+)", text, re.M)
        status = status.group(1) if status else "MISSING"
        records.append({"test": name, "result": status,
                        "log": str(log.relative_to(ROOT)),
                        "detail": log.read_text(errors="replace")[-4000:] if log.exists() else "No log"})
    report = {"platform": platform.platform(), "upstream": LOCK["version"], "tests": records,
              "counts": {s: sum(r["result"] == s for r in records)
                         for s in ("PASS", "SKIP", "FAIL", "ERROR", "MISSING", "XFAIL", "XPASS")}}
    (REPORTS / "upstream.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report["counts"], indent=2))
    assert_unmodified()
    bad = [r for r in records if r["result"] != "PASS"
           and not (r["result"] == "SKIP" and r["test"] == "tests/timeout/init-parent.sh")]
    if result.returncode or bad:
        raise RuntimeError(f"Upstream suite failed (make status {result.returncode}): {bad}")
    if root_pid_namespace and platform.system() == "Linux" and report["counts"]["SKIP"]:
        raise RuntimeError("Linux release gate requires the PID-namespace test to pass")
    return report


def test(*, root_pid_namespace: bool = False) -> None:
    test_upstream(root_pid_namespace=root_pid_namespace)
    env = dict(os.environ, TIMEOUT_BIN=str(BIN), TIMEOUT_REQUIRE_VERSION=LOCK["version"])
    run([sys.executable, "tools/run_tests.py"], env=env, seconds=600)
    (REPORTS / "verified.json").write_text(json.dumps({"binary_sha256": digest(BIN)}) + "\n")


def target() -> str:
    system = platform.system().lower()
    machine = {"arm64": "aarch64", "aarch64": "aarch64", "x86_64": "x86_64"}.get(platform.machine())
    if system not in {"darwin", "linux"} or machine is None:
        raise ValueError(f"Unsupported target: {platform.platform()}")
    return f"{machine}-{'apple-darwin' if system == 'darwin' else 'unknown-linux-gnu'}"


def package() -> Path:
    require_build()
    receipt = REPORTS / "verified.json"
    if not receipt.exists() or json.loads(receipt.read_text()).get("binary_sha256") != digest(BIN):
        raise RuntimeError("Run the complete test gate for this binary before packaging")
    version = (ROOT / "VERSION").read_text().strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("VERSION must be a numeric semantic version")
    DIST.mkdir(exist_ok=True)
    name = f"timeout-{version}-{target()}"
    with tempfile.TemporaryDirectory(dir=BUILD) as temporary:
        stage = Path(temporary) / name
        (stage / "bin").mkdir(parents=True)
        shutil.copy2(BIN, stage / "bin/timeout")
        docs = stage / "share/doc/timeout"
        docs.mkdir(parents=True)
        for src in (SOURCE / "COPYING", SOURCE / "AUTHORS", ROOT / "README.md", ROOT / "upstream.json"):
            shutil.copy2(src, docs / src.name)
        shutil.copy2(ROOT / "docs/compatibility.md", docs / "compatibility.md")
        shutil.copy2(REPORTS / "build.json", docs / "build.json")
        sources = docs / "source"
        sources.mkdir()
        shutil.copy2(ARCHIVE, sources / ARCHIVE.name)
        (sources / "tools").mkdir()
        for src, dst in ((ROOT / "tools/timeoutctl.py", sources / "tools/timeoutctl.py"),
                         (ROOT / "upstream.json", sources / "upstream.json"),
                         (ROOT / "VERSION", sources / "VERSION"),
                         (ROOT / "LICENSE", sources / "LICENSE")):
            shutil.copy2(src, dst)
        (sources / "README").write_text(
            "GNU coreutils is unchanged. Rebuild using Python >=3.12, C compiler, make, curl:\n"
            "python3 tools/timeoutctl.py build --archive " + ARCHIVE.name + "\n"
            "The resulting executable is .build/work/src/timeout. See COPYING for GPLv3+.\n")
        output = DIST / f"{name}.tar.gz"
        with tarfile.open(output, "w:gz") as tar:
            tar.add(stage, arcname=name)
    (output.with_name(output.name + ".sha256")).write_text(f"{digest(output)}  {output.name}\n")
    print(output)
    return output


def install(prefix: Path) -> None:
    require_build()
    destination = prefix.expanduser().resolve() / "bin/timeout"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as output, BIN.open("rb") as source:
        shutil.copyfileobj(source, output)
    destination.chmod(0o755)
    doc = prefix.expanduser().resolve() / "share/doc/timeout"
    doc.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE / "COPYING", doc / "COPYING")
    print(f"Installed {destination}; ensure {destination.parent} is on PATH")


def main() -> None:
    if sys.version_info < (3, 12):
        raise SystemExit("Build tooling requires Python 3.12+; the installed timeout needs no Python.")
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("fetch", "build", "test", "package", "install"):
        p = sub.add_parser(name)
        if name in {"fetch", "build"}:
            p.add_argument("--archive", type=Path, help="Offline, checksum-verified upstream archive")
        if name == "test":
            p.add_argument("--root-pid-namespace", action="store_true",
                           help="Permit sudo retry of the Linux PID-namespace test (ephemeral CI only)")
        if name == "install":
            p.add_argument("--prefix", type=Path, default=Path.home() / ".local")
    args = parser.parse_args()
    try:
        if args.command == "fetch":
            fetch(args.archive)
        elif args.command == "build":
            build(args.archive)
        elif args.command == "test":
            test(root_pid_namespace=args.root_pid_namespace)
        elif args.command == "package":
            package()
        elif args.command == "install":
            install(args.prefix)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError, tarfile.TarError) as exc:
        raise SystemExit(f"timeout build: {exc}") from exc


if __name__ == "__main__":
    main()
