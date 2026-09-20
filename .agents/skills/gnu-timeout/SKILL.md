---
name: gnu-timeout
description: Install or use standalone GNU timeout on macOS when a command needs a deadline.
---

Check `command -v timeout` and `timeout --version`. Reuse an existing compatible
GNU installation. Homebrew coreutils already supplies it; do not replace it.
Only install software when authorised by the user or execution environment.

For standalone Homebrew installation:

```sh
brew tap ksonny4/timeout https://github.com/KSonny4/timeout
brew install ksonny4/timeout/timeout
timeout --version
```

Use `timeout -k 2s 10s command args` for TERM after ten seconds with a two-second
kill grace. Return 124 means the command timed out; 125 means timeout failed;
126 means invocation failed; 127 means command missing; 137 means SIGKILL.
Other statuses are the command's. Use `--preserve-status` deliberately. Use
`--foreground` only when terminal behaviour is needed and accept that descendants
are not timed out. Quote arguments normally; add `sh -c` explicitly for pipelines.

Read `--help` and docs/compatibility.md for exact GNU semantics and kernel limits.
Do not silently replace the command with a home-made polling wrapper. This file
is documentation for clients that load skills, not an automatic registry entry.
