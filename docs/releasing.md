# Release procedure

Packaging versions are `GNU_MAJOR.GNU_MINOR.PACKAGING_PATCH`, for example
9.12.0. The executable keeps GNU's original version output. Homebrew tracks the
GNU archive version; bump the formula's `revision` for packaging-only Homebrew
changes after first publication. Never replace a published version's bytes.

Update source URL, mirror, checksum, VERSION and formula together. Validate the
archive checksum against an independent maintained source such as Homebrew's
coreutils formula, and review GNU release notes and test inventory changes.
Renovate opens a version suggestion only; it cannot approve the replacement hash.
Dependabot owns GitHub Actions updates, with no overlapping manager scope.

Run native CI and Homebrew gates. For release, use Actions > Release > Run workflow
against the reviewed commit, or create a release branch pointing at that commit:

```sh
git push origin HEAD:refs/heads/release/9.12.0
```

The release workflow reruns the complete CI at the release commit. Only the
publication job receives contents-write permission. It downloads four verified
platform artefacts, checks individual hashes, and publishes SHA256SUMS, retained
test evidence, install.sh and versioned GitHub release assets. It creates the
version tag at the tested commit. An existing release causes failure rather than
an overwrite. This workflow policy is not a claim that GitHub's immutable-release
setting is enabled. No GitHub token is needed by an end user installing public
releases.

## Verify the published installation

After publication, the release workflow passes its exact version to
`public-install.yml`. That read-only workflow downloads the real public installer,
checks its GitHub asset SHA-256 and equality with the tagged source, and installs
the selected archive into an isolated user prefix containing spaces. It runs the
repository suite against that installed executable, verifies overwrite refusal
and repeats five signal cases 25 times each with no retry-to-pass behaviour.
A failed post-publication check requires investigation; it does not replace or
remove the release automatically. Publish a new version if the shipped bytes need
repair.

The workflow is also available under Actions > Published installation > Run
workflow. Specify `9.12.0` to check that exact release, or leave the field empty
to resolve the latest stable release through the GitHub API. Both the release
source commit and the verification-harness commit are recorded. The two are
checked out separately so a fixture correction can test an existing released
binary without rewriting its tag, source or assets. The expected GNU version
comes from that release's source lock.

The original v9.12.0 release predates this post-publication job. Its subsequent
public-install results are recorded separately in [verification.md](verification.md).
Do not present a configured workflow as an executed or passing check.

## Source and trust

Each binary archive includes GNU's complete unchanged tarball, COPYING and
AUTHORS plus the exact packaging build recipe and lock. This deliberately makes
the archive larger than the executable. Rebuilding from the included source is
possible offline once build dependencies are installed. Only timeout is installed.

The shell installer checks the selected archive against that release's checksum.
This is integrity verification through GitHub HTTPS, not independent code signing.
The public-install check's installer digest comes from the same GitHub publisher.
There is no Apple notarisation, developer certificate, Homebrew bottle or
homebrew/core submission configured. The custom formula builds locally and has
its own native installation tests. Do not claim unpublished assets exist.

## Verification metrics and alerts

`build.json`: GNU version, source pin, OS, architecture, binary SHA-256 and bytes.
`upstream.json`: each original script's status/log and pass/skip/failure counts.
`contract.json`: actual unittest run, failure, error and skip counts.
`linkage.txt`: dynamic-library inspection of the extracted executable.
`public-install.json`: actual release/harness commits, native target, installed
binary size, full suite result and overwrite refusal.
`signal-stress.json`: actual repeated signal-test counts and failures, errors and
skips, with both source identities. The repetition budget is a bounded regression
check, not a measurement of all possible kernel scheduling interleavings.

These are build/test artefacts, not runtime telemetry. Ordinary GitHub failed-check
reporting is the maintainer signal. No runtime alerts, network collection or
dashboards exist. Public-install evidence is retained for 14 days as workflow
artefacts; preserve any longer-lived release record in the verification document
and link the actual run.
