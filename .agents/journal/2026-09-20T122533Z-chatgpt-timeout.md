# Standalone GNU timeout implementation session

- Session recorded from issue creation at 2026-09-20T12:25:33Z; exact earlier session start not captured.
- Agent: ChatGPT implementation session.
- Repository: KSonny4/timeout, initially empty (default branch master).
- Work ledger: https://github.com/KSonny4/timeout/issues/1.
- Shared guidance: KSonny4/engineering-guidance at 119e2093d0723979f5805bdeac5ec1e022c5f7ee.
- Loaded: AGENTS.md, standards/outcome-reporting.md, standards/cognee-memory.md, .agents/skills/cognee-memory/SKILL.md, docs/adoption.md, standards/agent-journal.md.
- Owner explicitly requested proportional adaptation of service-oriented guidance to a CLI.

## Decisions and evidence

- Use GNU coreutils 9.12's unmodified C implementation and upstream timeout tests. Homebrew's current coreutils formula supplies the version and SHA-256. A rewrite creates unnecessary compatibility risk.
- Homebrew coreutils already supplies timeout. This repository's outcome is independently installable timeout, with no other coreutils commands installed.
- Exact cross-OS behaviour has kernel limits: Linux-only parent-death signalling and PID namespaces do not exist on macOS. Preserve GNU's native platform behaviour and report test skips.
- Source checksum, immutable action pins, no silent source patches, safe installer refusal paths and release test receipts protect distribution integrity.
- CLI adaptation omits service deployment, feature-flag infrastructure, Grafana, runtime network metrics and service alerts. CI reports are the verification metrics.

## Environment and checks

The container cannot resolve external hosts; Remote Desktop Commander returned
no connected devices. Local tests initially used the installed GNU 9.7 and
passed all 114 cases. Those results were explicitly distinguished from testing
the GNU 9.12 candidate or a Mac.

Native run https://github.com/KSonny4/timeout/actions/runs/35511874592 at
7668f5aef89b4d20897ccf8087f04dc3755ec4bf completed successfully in all six jobs:
GNU 9.12 source build and upstream/contract/distribution checks on macOS ARM64,
macOS x86_64, Linux x86_64 and Linux ARM64, plus two native Homebrew installation
jobs. Downloaded native evidence confirms 114 repository passes, zero failures,
errors or skips on every target. Linux passed six upstream scripts; Macs passed
five with the explicit Linux PID-namespace skip. Full details: docs/verification.md.

## Struggles, corrections and reflection

1. Direct `make src/timeout` does not prepare Automake BUILT_SOURCES. The first
   Mac CI run failed on missing stdbit.h and gnulib declarations. An external
   Makefile fragment now builds those generated headers first, in the build tree.
   GNU files stay unchanged. Evidence: failed run 35511249347, passing run
   35511874592, and GNU v9.12 Makefile.am. Stable key: timeout-1-built-sources.
2. Oracle tests exposed incorrect assumptions in the initial test expectations:
   foreground SIGKILL still returns 137, and GNU accepts encoded numeric signal
   statuses. Expectations were corrected against GNU v9.12 timeout.c and
   operand2sig.c before native validation. Stable key: timeout-1-signal-contract.
3. macOS lacks setsid as a stock command. A test-only Python helper supplies the
   harness operation while the original upstream test scripts stay unchanged.
   It is neither a runtime wrapper nor installed with timeout.
4. Reusing unchanged upstream code plus original regressions gives a stronger
   compatibility foundation than a new implementation with sampled tests alone.
   Finite tests still cannot prove every race, kernel state or translated message.
5. Keep measured facts separate: implementation commit, native passes, Homebrew
   installation, release publication and adoption by users are different states.

## Cognee

- Recall status: unavailable. No Cognee tool was loaded; Plugin Management search for Cognee returned no plugin.
- Delivery: pending-sync; no write or retrieval is claimed.
- Proposed dataset, not yet authorised: agent-memory-ksonny4-timeout.
- Stable keys: timeout-1-upstream-over-rewrite, timeout-1-built-sources, timeout-1-signal-contract.
- Pending observation: For exact GNU timeout compatibility, build the unchanged pinned GNU source, prepare Automake BUILT_SOURCES before direct targets, and run all timeout-specific upstream tests. Keep native OS differences explicit and verify tricky signal expectations against upstream.
- Source evidence: GNU coreutils v9.12 source/tests; Homebrew coreutils formula; native Actions runs named above.
- Reconciliation remains tracked in issue #1 until an authorised dataset/client is available.

## Publication checkpoint

Implementation and native/Homebrew verification are complete for the recorded
commit. The Release workflow was started on release/9.12.0 at that commit:
https://github.com/KSonny4/timeout/actions/runs/35512205946.
It reruns all six gates before publication. No published release is asserted at
this checkpoint; the final issue update records the actual publication result.
This journal update changes documentation only; it does not alter the tested
implementation, formula, tests or workflows.
