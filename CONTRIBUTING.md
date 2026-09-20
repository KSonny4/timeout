# Contributing

Open an issue describing an observable CLI or installation failure, including
OS/architecture, GNU version, exact arguments, expected result and actual result.
Do not include credentials or command output containing private data.

Use the pinned source; add a bounded failing test before a fix. Runtime changes
belong upstream unless a narrowly documented patch is unavoidable. Never fork
GNU behaviour accidentally for convenience. Source changes invalidate the
unmodified-source contract and require a new reviewed compatibility decision.

Run the commands in AGENTS.md. The native CI matrix and Homebrew checks must pass
before a release. Inspect unexpected skips. Pin action revisions, keep source
checksums verified, and retain GNU licence/source distribution. API-authored
changes need the same evidence as hand-written PRs.
