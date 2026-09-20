"""Black-box contract tests. Every child has an independent watchdog and cleanup."""
from __future__ import annotations

import contextlib
import os
from pathlib import Path
import select
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
BINARY = os.environ.get("TIMEOUT_BIN", str(ROOT / ".build/work/src/timeout"))
TRUE = shutil.which("true") or "/usr/bin/true"
ENV = dict(os.environ, LC_ALL="C", LANG="C")
ENV.pop("POSIXLY_CORRECT", None)


def status(returncode: int) -> int:
    return 128 - returncode if returncode < 0 else returncode


def cleanup(process: subprocess.Popen) -> None:
    # Every fixture is in its own session. Never signal the test runner's group.
    with contextlib.suppress(ProcessLookupError):
        os.killpg(process.pid, signal.SIGKILL)
    if process.poll() is None:
        process.kill()
    process.wait(timeout=3)


def invoke(arguments: list, input_data: bytes = b"", deadline: float = 5):
    with tempfile.TemporaryFile() as stdin, tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        stdin.write(input_data)
        stdin.seek(0)
        process = subprocess.Popen([BINARY, *arguments], stdin=stdin, stdout=stdout, stderr=stderr,
                                   start_new_session=True, env=ENV)
        try:
            process.wait(timeout=deadline)
            stdout.seek(0)
            stderr.seek(0)
            return status(process.returncode), stdout.read(), stderr.read()
        finally:
            cleanup(process)


def wait_file(path: Path, deadline: float = 3) -> None:
    end = time.monotonic() + deadline
    while time.monotonic() < end:
        if path.exists():
            return
        time.sleep(0.01)
    raise AssertionError(f"Fixture did not create {path.name}")


class TimeoutContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not Path(BINARY).is_file():
            raise RuntimeError(f"Missing candidate executable {BINARY}; build it or set TIMEOUT_BIN")
        version = os.environ.get("TIMEOUT_REQUIRE_VERSION")
        if version:
            first = invoke(["--version"])[1].splitlines()[0].decode()
            if first != f"timeout (GNU coreutils) {version}":
                raise AssertionError(f"Expected GNU {version}, received {first}")

    def assert_status(self, expected, arguments):
        code, out, err = invoke(arguments)
        self.assertEqual(code, expected, (arguments, out, err))
        return out, err

    def test_command_finishes_before_deadline(self):
        self.assert_status(0, ["2", "/bin/sh", "-c", "exit 0"])

    def test_deadline_returns_124(self):
        self.assert_status(124, [".15", "/bin/sleep", "30"])

    def test_zero_disables_deadline(self):
        self.assert_status(23, ["0", "/bin/sh", "-c", "sleep .1; exit 23"])

    def test_preserve_status_returns_command_status(self):
        self.assert_status(128 + signal.SIGTERM, ["--preserve-status", ".15", "/bin/sleep", "30"])

    def test_stdin_stdout_stderr_are_preserved(self):
        payload = b"\x00binary\xff\n"
        code, out, err = invoke(["2", sys.executable, "-c",
                                "import sys; sys.stdout.buffer.write(sys.stdin.buffer.read()); "
                                "sys.stderr.buffer.write(b'error\\x00')"], payload)
        self.assertEqual((code, out, err), (0, payload, b"error\x00"))

    def test_child_options_are_not_timeout_options(self):
        out, _ = self.assert_status(0, ["2", sys.executable, "-c", "import sys; print(sys.argv[1:])",
                                       "--signal=NOPE", "--help", "-x"])
        self.assertIn(b"--signal=NOPE", out)
        self.assertIn(b"--help", out)

    def test_non_utf8_arguments_are_preserved(self):
        raw = b"\xffarg"
        code, out, _ = invoke([b"2", os.fsencode(sys.executable), b"-c",
                              b"import os,sys;sys.stdout.buffer.write(os.fsencode(sys.argv[1]))", raw])
        self.assertEqual((code, out), (0, raw))

    def test_spaces_and_metacharacters_are_not_shell_interpreted(self):
        value = "a b;$(printf injected) *"
        out, _ = self.assert_status(0, ["2", sys.executable, "-c", "import sys; print(sys.argv[1])", value])
        self.assertEqual(out.decode().strip(), value)

    def test_cwd_and_environment_are_preserved(self):
        out, _ = self.assert_status(0, ["2", sys.executable, "-c", "import os;print(os.getcwd());print(os.getenv('LC_ALL'))"])
        self.assertEqual(out.decode().splitlines(), [os.getcwd(), "C"])

    def test_missing_executable_returns_127(self):
        self.assert_status(127, ["2", "timeout-test-executable-that-does-not-exist-728493"])

    def test_non_executable_returns_126(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "not-executable"
            path.write_text("#!/bin/sh\nexit 0\n")
            path.chmod(0o644)
            self.assert_status(126, ["2", str(path)])
            self.assert_status(126, ["2", directory])

    def test_executable_without_shebang_uses_execvp_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "command"
            path.write_text("exit 37\n")
            path.chmod(0o755)
            self.assert_status(37, ["2", str(path)])

    def test_help_lists_gnu_options(self):
        out, _ = self.assert_status(0, ["--help"])
        for option in (b"--foreground", b"--kill-after", b"--preserve-status", b"--signal", b"--verbose"):
            self.assertIn(option, out)

    def test_version_retains_gnu_identity(self):
        out, _ = self.assert_status(0, ["--version"])
        self.assertIn(b"timeout (GNU coreutils)", out)
        self.assertIn(b"Free Software Foundation", out)

    def test_verbose_diagnostic_goes_to_stderr(self):
        out, err = self.assert_status(124, ["--verbose", ".15", "/bin/sleep", "30"])
        self.assertEqual(out, b"")
        self.assertIn(b"sending signal TERM to command", err)

    def test_default_mode_is_silent(self):
        out, err = self.assert_status(124, [".15", "/bin/sleep", "30"])
        self.assertEqual((out, err), (b"", b""))

    def test_kill_signal_default_group_returns_137(self):
        self.assert_status(137, ["-sKILL", ".15", "/bin/sleep", "30"])

    def test_kill_signal_foreground_returns_137(self):
        self.assert_status(137, ["--foreground", "-sKILL", ".15", "/bin/sleep", "30"])

    def test_kill_after_returns_137_in_both_modes(self):
        for options in ([], ["--foreground"]):
            with self.subTest(options=options):
                self.assert_status(137, [*options, "-s0", "-k.15", ".15", "/bin/sleep", "30"])

    def test_positive_underflow_still_times_out(self):
        self.assert_status(124, ["1e-10000", "/bin/sleep", "30"])

    def signal_fixture(self, options, child_code, received=signal.SIGALRM):
        process = subprocess.Popen([BINARY, *options, "30", sys.executable, "-c", child_code],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   start_new_session=True, env=ENV)
        try:
            ready, _, _ = select.select([process.stdout], [], [], 5)
            self.assertTrue(ready, "Child did not become ready before watchdog")
            self.assertEqual(process.stdout.readline(), b"ready\n")
            os.kill(process.pid, received)
            out, err = process.communicate(timeout=5)
            return status(process.returncode), out, err
        finally:
            cleanup(process)
            process.stdout.close()
            process.stderr.close()

    def test_trapped_signal_preserves_custom_exit(self):
        child = ("import signal,time,sys; signal.signal(signal.SIGTERM,lambda *_:sys.exit(42));"
                 "print('ready',flush=True);time.sleep(30)")
        self.assertEqual(self.signal_fixture(["--preserve-status"], child)[0], 42)
        self.assertEqual(self.signal_fixture([], child)[0], 124)

    def test_external_term_is_forwarded_without_timeout_status(self):
        child = ("import signal,time,sys; signal.signal(signal.SIGTERM,lambda *_:sys.exit(42));"
                 "print('ready',flush=True);time.sleep(30)")
        self.assertEqual(self.signal_fixture([], child, signal.SIGTERM)[0], 42)

    def test_custom_signal_name_is_delivered(self):
        child = ("import signal,time,sys; signal.signal(signal.SIGUSR1,lambda *_:sys.exit(41));"
                 "print('ready',flush=True);time.sleep(30)")
        for sig in ("USR1", "SIGUSR1", "sigusr1", str(signal.SIGUSR1), str(128 + signal.SIGUSR1)):
            with self.subTest(signal=sig):
                self.assertEqual(self.signal_fixture(["-s", sig, "--preserve-status"], child)[0], 41)

    def test_kill_after_terminates_term_ignoring_child(self):
        child = ("import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN);"
                 "print('ready',flush=True);time.sleep(30)")
        self.assertEqual(self.signal_fixture(["-k.15"], child)[0], 137)

    def test_zero_kill_after_is_disabled(self):
        child = ("import signal,time,sys; signal.signal(signal.SIGTERM,signal.SIG_IGN);"
                 "print('ready',flush=True);time.sleep(.2);sys.exit(42)")
        self.assertEqual(self.signal_fixture(["-k0", "--preserve-status"], child)[0], 42)

    def test_stopped_child_is_continued_and_terminated(self):
        child = "import os,signal,time;print('ready',flush=True);os.kill(os.getpid(),signal.SIGSTOP);time.sleep(30)"
        self.assertEqual(self.signal_fixture([], child)[0], 124)

    def process_group(self, foreground):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            child_code = (
                "import signal,time,sys;from pathlib import Path;"
                f"p=Path({str(base)!r});"
                "signal.signal(signal.SIGTERM,lambda *_:(p.joinpath('terminated').touch(),sys.exit(0)));"
                "signal.signal(signal.SIGUSR1,lambda *_:p.joinpath('alive').touch());"
                "p.joinpath('ready').touch();time.sleep(30)"
            )
            parent_code = (
                "import subprocess,sys,time;from pathlib import Path;"
                f"p=Path({str(base)!r});"
                f"c=subprocess.Popen([sys.executable,'-c',{child_code!r}]);"
                "p.joinpath('pid').write_text(str(c.pid));time.sleep(30)"
            )
            options = ["--foreground"] if foreground else []
            process = subprocess.Popen([BINARY, *options, "30", sys.executable, "-c", parent_code],
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                       start_new_session=True, env=ENV)
            try:
                wait_file(base / "ready")
                os.kill(process.pid, signal.SIGALRM)
                process.wait(timeout=5)
                self.assertEqual(status(process.returncode), 124)
                if foreground:
                    os.kill(int((base / "pid").read_text()), signal.SIGUSR1)
                    wait_file(base / "alive")
                    self.assertFalse((base / "terminated").exists())
                else:
                    wait_file(base / "terminated")
            finally:
                cleanup(process)

    def test_default_mode_terminates_process_group(self):
        self.process_group(False)

    def test_foreground_leaves_descendants_running(self):
        self.process_group(True)

    def test_foreground_preserves_tty_access(self):
        import pty
        master, slave = pty.openpty()
        process = subprocess.Popen([BINARY, "--foreground", "2", "/bin/sh", "-c", "test -t 0"],
                                   stdin=slave, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                   start_new_session=True, env=ENV)
        os.close(slave)
        try:
            self.assertEqual(process.wait(timeout=5), 0)
        finally:
            cleanup(process)
            os.close(master)


def add_case(name, arguments, expected):
    def test(self):
        self.assert_status(expected, arguments)
    test.__name__ = name
    setattr(TimeoutContract, name, test)


for number in (0, 1, 2, 42, 123, 124, 125, 126, 127, 137, 255):
    add_case(f"test_propagate_exit_{number}", ["2", "/bin/sh", "-c", f"exit {number}"], number)

for index, duration in enumerate(("0", "0s", "0m", "0h", "0d", "2", "2s", "1m", "1h", "1d",
                                  "1.25", "2e1", "0x1p2", "+2", " 2", "inf", "1e10000")):
    add_case(f"test_valid_duration_{index:02d}", [duration, TRUE], 0)

for index, duration in enumerate(("", "nonsense", "nan", "-1", " -0.1", " -1e-10000", "2ms", "2D",
                                  "2S", "2sX", "2 ", "1m30s", "0x", "--")):
    add_case(f"test_invalid_duration_{index:02d}", [duration, TRUE], 125)

for index, arguments in enumerate(([], ["1"], ["--no-such-option"], ["--signal"], ["-k"],
                                  ["-sNOPE", "1", TRUE], ["-s2147483648", "1", TRUE],
                                  ["-kinvalid", "1", TRUE], ["--foreground=yes", "1", TRUE])):
    add_case(f"test_invalid_invocation_{index:02d}", arguments, 125)

for index, options in enumerate((["--foreground"], ["-f"], ["--preserve-status"], ["-p"],
                                ["-v"], ["--verbose"], ["-sTERM"], ["--signal=TERM"],
                                ["--sig=TERM"], ["--kill-after=1"], ["-k1"], ["-fpv"], ["--"])):
    add_case(f"test_option_form_{index:02d}", [*options, "2", TRUE], 0)

if __name__ == "__main__":
    unittest.main()
