"""Deterministic cleanup guard tests plus a native ps-format integration check."""
import os
import signal
import subprocess
import unittest
from unittest.mock import Mock, patch

from process_cleanup import cleanup, group_has_live_members


class CleanupContract(unittest.TestCase):
    def process(self):
        process = Mock(spec=subprocess.Popen)
        process.pid = 31001
        process.poll.return_value = -signal.SIGKILL
        process.wait.return_value = -signal.SIGKILL
        return process

    def snapshot(self, output):
        return subprocess.CompletedProcess(["ps"], 0, stdout=output, stderr="")

    def test_successful_cleanup_does_not_inspect(self):
        process = self.process()
        with patch("process_cleanup.os.killpg") as killpg, patch("process_cleanup.subprocess.run") as inspect:
            cleanup(process)
        killpg.assert_called_once_with(process.pid, signal.SIGKILL)
        inspect.assert_not_called()
        process.wait.assert_called_once_with(timeout=3)

    def test_missing_group_reaps_child(self):
        process = self.process()
        with patch("process_cleanup.os.killpg", side_effect=ProcessLookupError):
            cleanup(process)
        process.wait.assert_called_once_with(timeout=3)

    def test_denied_absent_group_with_exited_leader_is_complete(self):
        process = self.process()
        with patch("process_cleanup.os.killpg", side_effect=PermissionError), \
             patch("process_cleanup.subprocess.run", return_value=self.snapshot("42 Ss\n43 R\n")):
            cleanup(process)
        process.wait.assert_called_once_with(timeout=3)

    def test_denied_zombie_only_group_with_exited_leader_is_complete(self):
        process = self.process()
        with patch("process_cleanup.os.killpg", side_effect=PermissionError), \
             patch("process_cleanup.subprocess.run", return_value=self.snapshot("42 Ss\n31001 Z\n31001 Z+\n")):
            cleanup(process)
        process.wait.assert_called_once_with(timeout=3)

    def test_denied_live_group_is_an_error(self):
        process = self.process()
        with patch("process_cleanup.os.killpg", side_effect=PermissionError), \
             patch("process_cleanup.subprocess.run", return_value=self.snapshot("31001 S\n")):
            with self.assertRaises(PermissionError):
                cleanup(process)
        process.wait.assert_called_once_with(timeout=3)

    def test_denied_live_leader_is_killed_reaped_and_reported(self):
        process = self.process()
        process.poll.return_value = None
        with patch("process_cleanup.os.killpg", side_effect=PermissionError), \
             patch("process_cleanup.subprocess.run") as inspect:
            with self.assertRaises(PermissionError):
                cleanup(process)
        inspect.assert_not_called()
        process.kill.assert_called_once_with()
        process.wait.assert_called_once_with(timeout=3)

    def test_failed_inspection_is_an_error(self):
        process = self.process()
        with patch("process_cleanup.os.killpg", side_effect=PermissionError), \
             patch("process_cleanup.subprocess.run", side_effect=subprocess.CalledProcessError(1, ["ps"])):
            with self.assertRaises(subprocess.CalledProcessError):
                cleanup(process)
        process.wait.assert_called_once_with(timeout=3)

    def test_ambiguous_snapshot_is_an_error(self):
        for output in ("", "pgid stat\n", "31001\n", "31001 S extra\n"):
            with self.subTest(output=output), patch("process_cleanup.subprocess.run", return_value=self.snapshot(output)):
                with self.assertRaises(RuntimeError):
                    group_has_live_members(31001)

    def test_unknown_state_counts_as_live(self):
        with patch("process_cleanup.subprocess.run", return_value=self.snapshot("31001 ?\n")):
            self.assertTrue(group_has_live_members(31001))

    def test_native_ps_can_observe_our_live_group(self):
        self.assertTrue(group_has_live_members(os.getpgrp()))


if __name__ == "__main__":
    unittest.main()
