# Public release installation verification

- Started: 2026-09-20T13:36:52Z (UTC clock observation).
- Agent/session: ChatGPT, continuation after interrupted delivery.
- Repository/outcome: KSonny4/timeout, issue #1. Verify actual public installation and GNU behaviour.
- Starting master: `126ef10dc1f3334f634862a70c81481b0d7d55dd`.
- Released runtime: `7668f5aef89b4d20897ccf8087f04dc3755ec4bf`, tag `v9.12.0`.
- Final tested harness: `cad0d0052b56b902a8d2c371d06c15876f341065`.
- Final status: implementation and verification complete; Cognee delivery pending separately in #5.

## Instructions actually loaded

Local AGENTS.md, README, compatibility/verification/release documents, installer,
test runner and CI/release workflows. Shared guidance revision
`119e2093d0723979f5805bdeac5ec1e022c5f7ee`: AGENTS.md,
standards/cognee-memory.md, .agents/skills/cognee-memory/SKILL.md,
standards/outcome-reporting.md and standards/agent-journal.md.
Preserved the owner-authorised local CLI overlay. No service deployment, feature
flags, runtime telemetry, Grafana or runtime alert infrastructure applies.

## Work and observations

The repository already contained the implementation and published v9.12.0.
Release run 35512205946 passed four native, two Homebrew and publication jobs.
Recovered that state rather than rebuilding or republishing an existing release.
The environment had no connected Remote Desktop device and could not resolve
GitHub from the container. Native execution used GitHub Actions. GitHub's artifact
download action supplied ZIPs that could be inspected locally.

Added a read-only four-platform public installer workflow, plus an exact-version
post-publication hook for future releases. It verifies the real released script
and archive, installs into a user prefix containing spaces, exercises the installed
executable, checks overwrite refusal and retains measured reports. Released source
and current harness are checked out and recorded separately. No published GNU
source, tag, installer or binary asset was changed.

Two actual harness failures were investigated and retained in docs/verification.md:

1. Run 35514156386: Apple Silicon numeric SIGUSR1 produced 158 instead of requested
   fixture exit 41. GNU sends to both PID and group; CPython finalisation resets
   handlers. This supports a shutdown-race explanation, without proving an exact
   kernel interleaving. Disposable signal fixtures now use os._exit; a deterministic
   atexit regression distinguishes old status 99 from immediate status 41.
2. Run 35514608769: all applicable GNU scripts passed, but post-exit fixture killpg
   raised PermissionError. No snapshot established the exact kernel cause. The new
   test-only cleanup helper accepts this only after an exited leader and a bounded,
   successful ps snapshot showing no live group members. Live groups and ambiguous
   or failed inspections still fail. Ten guard tests cover the branches.

Expected GNU assertions were preserved. No skip, xfail, blanket permission-error
suppression or retry-until-green was used. The kill-after case was added to stress
coverage. Runtime and upstream tests remain unchanged.

## Executed verification

- Final native run 35515616455: all six jobs passed, including both Homebrew targets.
- Final public run 35515616466: all four jobs passed. Each reports 125 repository
  tests and 125 repeated signal tests, zero failures/errors/skips, public install
  success and overwrite refusal. Five methods are repeated 25 times; this is not
  125 additional unique requirements.
- Downloaded all four final public evidence ZIPs, verified their GitHub digests and
  inspected contract.json, public-install.json and signal-stress.json.
- Downloaded final native Apple Silicon evidence, verified its digest and inspected
  125 successful repository tests plus five GNU script passes and one Linux-only
  PID-namespace skip. Other final native/Homebrew job/step conclusions were read
  from GitHub. Historical full four-platform source evidence remains documented.
- Historical 115/100 passing public run 35514608768 retained separately.
- Local cleanup guard tests: ten passed. Local old/new signal diagnostic: ten each
  passed against GNU 9.7, so no reproduction of the intermittent native issue.
  A larger local attempt hit its tool watchdog and yielded no useful conclusion.
- Local deterministic atexit experiment: sys.exit returned 99; os._exit returned 41.
  Local results were not counted as native GNU 9.12 compatibility proof.

Durable evidence: docs/verification.md and
`docs/evidence/public-install-v9.12.0-cleanup.json`. Historical evidence is preserved
rather than relabelled. Documentation-only closing commits do not change the tested
harness. Public workflow artifacts have 14-day retention.

## Reflection and memory delivery

Recall: unavailable. No configured Cognee client or approved project dataset was
available. Proposed `agent-memory-ksonny4-timeout` remains unapproved; no write was
made to it or the ingest-owned guidance dataset. Delivery is **pending-sync**, not
saved or retrieved. Reconciliation owner is existing issue #5.

Pending evidence-backed lesson records:

- `timeout-public-release-installation-evidence-v1`: package tests, publication and
  actual public download installation establish different facts. Preserve distinct
  source/harness identities when verifying an existing release after fixture fixes.
- `timeout-signal-fixture-shutdown-v1`: a disposable Python signal fixture using
  sys.exit can include interpreter finalisation in the observed behaviour. Use an
  explicit fixture exit contract and deterministic regression; do not change GNU
  semantics to accommodate a test fixture. Exact native race remains inferred.
- `timeout-test-cleanup-state-v1`: process cleanup errors require evidence-sensitive
  handling. Reap the owned child, inspect group state with a bound, and keep live
  groups or unavailable inspections as failures. Do not blanket-ignore EPERM.

Kind/status: lessons / observed with causal limitations above. Evidence links are
issue #1, the verification document, the failed and passing runs, and the recorded
GNU/CPython source references. No secrets or private reasoning are included.

## Metrics, review and remaining limits

Added public-install and signal-stress JSON outcomes. Existing native build,
upstream, contract and linkage reports remain. GitHub failed checks are the
maintainer signal; no runtime alerts or telemetry were created. CLI behaviour has
no new UI, so UI screenshots are not applicable. Source-preservation, exact source
identities, bounded tests and failed-case regression review supplied the checks.

Publication is a custom Homebrew tap and GitHub release, not Homebrew core or an
automatic model registry. macOS kernel facilities and untranslated diagnostics
remain explicit compatibility boundaries. Cognee sync is the only pending
administrative follow-up from this continuation, tracked in #5.
