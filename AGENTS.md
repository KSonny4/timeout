# timeout development

Shared guidance: KSonny4/engineering-guidance at
`119e2093d0723979f5805bdeac5ec1e022c5f7ee`. Read that revision's AGENTS.md and
trigger-matching playbooks. Preserve this CLI-specific overlay, authorised by
the owner for first adoption, rather than importing service infrastructure.

## Scope and commands

Package unmodified GNU timeout. Do not implement a second parser, add custom
runtime flags, wrap execution, change exit codes, or claim Linux kernel features
on Darwin. Change `upstream.json` and Formula/timeout.rb together, retaining a
verified source checksum and upstream licensing. GNU source is downloaded into
`.build`, not edited or copied piecemeal. Prepare BUILT_SOURCES before building
a direct Automake program target; otherwise gnulib headers are missing.

- Build: `python3 tools/timeoutctl.py build`
- Full checks: `python3 tools/timeoutctl.py test`
- Local harness against a chosen GNU: `TIMEOUT_BIN=/absolute/path/timeout python3 tools/run_tests.py`
- Install: `python3 tools/timeoutctl.py install --prefix "$HOME/.local"`
- Package after passing checks: `python3 tools/timeoutctl.py package`

The test-only Linux sudo namespace retry is for disposable CI, never silently
run on a user's machine. Every process fixture must be bounded and isolated.
Do not replace native tests with an old system timeout and call that a candidate
pass. Record GNU version, OS, architecture, passes, skips and errors.

## Proportional engineering

Use an outcome-led GitHub Issue before material work, one factual journal per
agent/session in `.agents/journal`, scoped changes, immutable dependency/action
pins, real tests and an honest PR report. Maintain feature scenarios and their
same-named tests. Explain structural changes with inline Mermaid and a journey.

This is a local CLI with no service: no server deployment, Docker/Nomad, feature
flag service, Grafana, network telemetry or runtime alerts. Measurements are CI
verification results, source/binary checksums and binary size. CI failures are
maintainer signals. Do not invent operational dashboards to satisfy a template.
Keep Dependabot (Actions) and Renovate (GNU source pin) scopes non-overlapping.

## Memory workflow

Explicitly load shared standards/cognee-memory.md and
.agents/skills/cognee-memory/SKILL.md at the pin. Recall project lessons at start
and when blocked before asking for troubleshooting help; reflect at meaningful
checkpoints and every session end. Save evidence-backed lessons only through an
authorised Cognee client/dataset, and verify retrieval before claiming it.

Cognee status at onboarding: unavailable in the authoring session. Proposed
project dataset `agent-memory-ksonny4-timeout` is **not yet approved or configured**.
Do not infer permission from this name or write to the ingest-owned guidance
dataset. Keep unsent non-sensitive lessons and stable keys in the journal and
issue #1 as pending-sync. Authoritative commands live in Git; issues are the work
ledger. Never include credentials, personal data or private reasoning in memory.
