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
platform artefacts, checks individual hashes, publishes SHA256SUMS, retained test
evidence, install.sh, and immutable GitHub release assets. It creates tag v9.12.0
at the tested commit. An existing release causes failure rather than an overwrite.
No GitHub token is needed by an end user installing public releases.

Each binary archive includes GNU's complete unchanged tarball, COPYING and
AUTHORS plus the exact packaging build recipe and lock. This deliberately makes
the archive larger than the executable. Rebuilding from the included source is
possible offline once build dependencies are installed. Only timeout is installed.

The shell installer checks the selected archive against that release's checksum.
This is integrity verification through GitHub HTTPS, not independent code signing.
There is no Apple notarisation, developer certificate, Homebrew bottle or
homebrew/core submission configured. The custom formula builds locally and has
its own native installation tests. Do not claim unpublished assets exist.

## Verification metrics and alerts

`build.json`: GNU version, source pin, OS, architecture, binary SHA-256 and bytes.
`upstream.json`: each original script's status/log and pass/skip/failure counts.
`contract.json`: actual unittest run, failure, error and skip counts.
`linkage.txt`: dynamic-library inspection of the extracted executable.
These are build artefacts, not telemetry. Ordinary GitHub failed-check reporting
is the maintainer alert. No runtime alerts, network collection or dashboards exist.
