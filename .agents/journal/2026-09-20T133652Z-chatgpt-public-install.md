# Public release installation verification

- Recorded at: 2026-09-20T13:36:52Z (UTC clock observation).
- Agent/session: ChatGPT, continuation after interrupted delivery.
- Repository: KSonny4/timeout; issue: #1.
- Starting master: `126ef10dc1f3334f634862a70c81481b0d7d55dd`.
- Released runtime candidate: `7668f5aef89b4d20897ccf8087f04dc3755ec4bf`, tag `v9.12.0`.
- Outcome: verify that users can install the actual published binary and retain GNU behaviour; close the delivery record with evidence.

## Instructions actually loaded

Local `AGENTS.md`, README, `docs/verification.md`, installer, test runner and CI/release workflows. Shared guidance revision `119e2093d0723979f5805bdeac5ec1e022c5f7ee`: `AGENTS.md`, `standards/cognee-memory.md`, `.agents/skills/cognee-memory/SKILL.md`, `standards/outcome-reporting.md`, and `standards/agent-journal.md`. Preserve the existing owner-authorised local CLI overlay. No service deployment, feature flags, telemetry, Grafana or runtime alert infrastructure is applicable.

## Observations and scope

- GitHub release v9.12.0 is published. Release run 35512205946 completed successfully: four native jobs, two Homebrew jobs, one publish job.
- Existing native evidence is recorded in `docs/verification.md`: 114 repository tests on each target, six upstream scripts on Linux and five plus one Linux-only skip on macOS.
- The verification document explicitly distinguishes packaging fixture tests from live public-download installation. Add a finite native CI check for that remaining gap, with no runtime or published-asset changes.
- The sandbox cannot resolve GitHub; Remote Desktop Commander reports no connected devices. Public download attempts through the browser/download tools did not yield a file. Native execution must use GitHub Actions. A failed local download is not evidence that the public release is broken.

## Intended checks

Download the release installer from GitHub, validate its asset digest, compare it with the tagged source, install without sudo into a temporary prefix containing spaces, run the existing repository tests against the installed executable, and verify a second install refuses to overwrite it. Preserve logs and JSON reports for all four native OS/architecture runners. Keep all commands bounded.

## Reflection and memory delivery

- Recall outcome: `unavailable`; this client has no configured Cognee tool or approved project dataset. Prior conversation context was used only to locate authoritative GitHub records.
- Memory delivery: `pending-sync`, not saved or verified. Proposed destination `agent-memory-ksonny4-timeout` still requires approval/configuration; do not write to the ingest-owned guidance dataset.
- Stable key: `timeout-public-release-installation-evidence-v1`.
- Kind/status: lesson / observed.
- Evidence: issue #1, `docs/verification.md`, release v9.12.0, release run 35512205946.
- Lesson: a successful native package test and a published release establish separate facts; a real downloader/install path needs its own verification against the released executable. On continuation, inspect release state before rebuilding or republishing an existing version.
- Applicability: standalone release packages and interrupted publication hand-offs.
- Reconciliation: issue #1 until a dedicated memory follow-up is linked.

## Current status

In progress. Existing release verified as published; live installer check and final evidence reconciliation are pending. No claim of a new local/native test pass in this session yet.
