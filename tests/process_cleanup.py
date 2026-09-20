"""Test-only process cleanup. Never installed with the timeout executable."""
from __future__ import annotations

import contextlib
import os
import signal
import subprocess


def group_has_live_members(pgid: int) -> bool:
    """Inspect native process state; an unavailable or malformed view is an error."""
    result = subprocess.run(
        ["ps", "-A", "-o", "pgid=", "-o", "stat="],
        check=True, capture_output=True, text=True, timeout=3,
        env=dict(os.environ, LC_ALL="C", LANG="C"),
    )
    rows = [line.split() for line in result.stdout.splitlines() if line.strip()]
    if not rows or any(len(row) != 2 or not row[0].isdigit() for row in rows):
        raise RuntimeError("Cannot verify process-group cleanup from ps output")
    return any(int(group) == pgid and not state.startswith("Z") for group, state in rows)


def cleanup(process: subprocess.Popen) -> None:
    """Kill an isolated fixture group and always reap its direct child."""
    try:
        # Fixtures use start_new_session=True; never signal our own process group.
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    except PermissionError:
        # A native Mac run reported EPERM after the command had exited. Accept
        # this only with an exited leader AND observed absence of live members.
        # Live groups, denied inspections and ambiguous snapshots remain errors.
        if process.poll() is None or group_has_live_members(process.pid):
            raise
    finally:
        if process.poll() is None:
            with contextlib.suppress(ProcessLookupError):
                process.kill()
        process.wait(timeout=3)
