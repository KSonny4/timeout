# Standalone GNU timeout implementation session

- Session recorded from issue creation at 2026-09-20T12:25:33Z; exact earlier session start not captured.
- Agent: ChatGPT implementation session.
- Repository: KSonny4/timeout, initially empty (default branch master).
- Work ledger: https://github.com/KSonny4/timeout/issues/1.
- Shared guidance: KSonny4/engineering-guidance at 119e2093d0723979f5805bdeac5ec1e022c5f7ee.
- Loaded: AGENTS.md, standards/outcome-reporting.md, standards/cognee-memory.md, .agents/skills/cognee-memory/SKILL.md, docs/adoption.md, standards/agent-journal.md. Additional applied sources are recorded as they are loaded.
- Owner explicitly requested proportional adaptation of service-oriented guidance to a CLI.

## Decisions and evidence

- Use GNU coreutils 9.12's unmodified C implementation and upstream timeout tests. Homebrew's current coreutils formula supplies the version and SHA-256. A rewrite creates unnecessary compatibility risk.
- Homebrew coreutils already supplies timeout. This repository's outcome is independently installable timeout, with no other coreutils commands installed.
- Exact cross-OS behaviour has kernel limits: Linux-only parent-death signalling and PID namespaces do not exist on macOS. Preserve GNU's native platform behaviour and report test skips.
- Native build/test validation will use GitHub Actions. The container cannot resolve external hosts; Remote Desktop Commander returned no connected devices. These are environment limitations, not code test passes.

## Cognee

- Recall status: unavailable. No Cognee tool is loaded; Plugin Management search for Cognee returned no plugin.
- Delivery: pending-sync; no write or retrieval is claimed.
- Proposed dataset, not yet authorised: agent-memory-ksonny4-timeout.
- Stable key: timeout-1-upstream-over-rewrite.
- Pending observation: For exact GNU timeout compatibility, build the unchanged pinned GNU source and run all timeout-specific upstream tests. Keep native OS differences explicit. GNU 9.12 has six timeout-specific test scripts, including a Linux PID-namespace regression for coreutils 9.10. Evidence: coreutils/coreutils v9.12 src/timeout.c and tests/timeout/; Homebrew/homebrew-core Formula/c/coreutils.rb inspected 2026-09-20.
- Reconciliation remains tracked in issue #1 until an authorised dataset/client is available.

## Current state

Implementation in progress. No build, macOS test, release or Homebrew installation has yet been reported as passing.
