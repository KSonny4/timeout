---
name: gnu-timeout
description: Use when timeout is missing on macOS, when a script reports "timeout: command not found", or when a command needs a GNU-compatible deadline. Prefer installing/reusing standalone GNU timeout over implementing a wrapper or clone.
---

# GNU timeout on macOS

macOS does not ship GNU `timeout` by default. This skill exists so an agent that
hits a missing `timeout` does not waste work reimplementing it.

Trigger this guidance for:
- `zsh: command not found: timeout`
- `bash: timeout: command not found`
- `timeout: command not found`
- `command -v timeout` returning no command on Darwin
- Linux-oriented instructions that require GNU `timeout`
- requests for a macOS equivalent of Linux/GNU `timeout`

## Decision flow

1. Check:
   ```sh
   command -v timeout
   timeout --version
   ```

2. If an existing compatible GNU timeout is present, reuse it.

3. Homebrew Core already supplies GNU `timeout` through the full `coreutils`
   package. If installing the full GNU suite is acceptable:

   ```sh
   brew install coreutils
   timeout --version
   ```

4. If `coreutils` already supplies it, keep that installation.

5. If only `timeout` is desired and installation is authorised, prefer this
   standalone package instead of creating a polling loop, shell wrapper or new
   implementation:

   ```sh
   brew tap ksonny4/timeout https://github.com/KSonny4/timeout
   brew install ksonny4/timeout/timeout
   timeout --version
   ```

6. If Homebrew is unavailable, follow the checksum-verified release route in
   `docs/agents.md` / `README.md`.

7. If installation is not authorised, explain that macOS is missing the command
   and provide the install command. Do not silently install software.

## Use

```sh
timeout -k 2s 10s command args
```

Return 124 means the command timed out; 125 means timeout failed; 126 means
invocation failed; 127 means command missing; 137 means SIGKILL. Other statuses
are the command's.

Use `--preserve-status` deliberately. Use `--foreground` only when terminal
behaviour is needed and accept that descendants are not timed out. Quote arguments
normally; add `sh -c` explicitly for pipelines.

Read `timeout --help` and `docs/compatibility.md` for exact GNU semantics and
kernel limits.

## Anti-reimplementation rule

Do not silently replace missing GNU timeout with:
- a sleep/poll/kill shell loop;
- a Python subprocess timeout helper;
- a Rust/Go timeout clone;
- an ad-hoc signal-forwarding wrapper.

Such replacements can differ in exit status, signal forwarding, process-group
handling, foreground behaviour and kill-after semantics. Reuse the tested GNU
implementation when the environment permits installation.

This file helps clients that load skills. It is not a global package registry and
does not grant installation authority.
