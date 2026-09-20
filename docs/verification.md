# Verification snapshot: 20 September 2026

This records actual results for implementation commit
`7668f5aef89b4d20897ccf8087f04dc3755ec4bf`, rather than a claim about an
untested future revision. GNU reference: coreutils 9.12, unchanged source.

[Native compatibility run 35511874592](https://github.com/KSonny4/timeout/actions/runs/35511874592)
completed successfully across all six jobs. The four native artefact archives
were downloaded and their build.json, upstream.json, contract.json and linkage
reports inspected. Homebrew job results were read from GitHub Actions; the ARM
Homebrew job log explicitly reports `Ran 114 tests` and `OK`.

| Native target | GNU timeout scripts | Repository tests | Executable bytes | Distribution and linkage checks |
| --- | --- | --- | --- | --- |
| macOS 15.7.9 ARM64 | 5 passed, 1 expected skip | 114 passed, 0 skipped | 130,872 | Passed |
| macOS 15.7.9 x86_64 | 5 passed, 1 expected skip | 114 passed, 0 skipped | 113,472 | Passed |
| Ubuntu 24.04 x86_64, glibc 2.39 | 6 passed, 0 skipped | 114 passed, 0 skipped | 207,488 | Passed |
| Ubuntu 24.04 ARM64, glibc 2.39 | 6 passed, 0 skipped | 114 passed, 0 skipped | 229,040 | Passed |

Both Homebrew jobs built the exact candidate formula from source, ran `brew test`
and passed all 114 repository tests against the installed executable. All tests
reported zero failures/errors. The Mac skip is `tests/timeout/init-parent.sh`,
which depends on Linux PID namespaces. No other upstream skip was accepted.

The 114 repository tests comprise 93 executable contract tests and 21 packaging/
installer tests. The six upstream scripts each contain their own assertions;
script counts must not be presented as individual assertion counts. Native jobs
also reran the repository suite against the executable extracted from the final
archive. Packaging fixture tests alone do not constitute a live public-release
installer download test.

The Apple Silicon binary links only to `/usr/lib/libSystem.B.dylib`. Binary
archives are larger than the executable because complete GNU source, licensing
and the build recipe are deliberately included.

## Reproduction

```sh
python3 tools/timeoutctl.py build
python3 tools/timeoutctl.py test
python3 tools/timeoutctl.py package
```

The Linux CI jobs explicitly enable the test-only root PID-namespace retry on
disposable runners. Normal local testing does not silently use sudo.

An earlier local harness run passed 114 tests against the container's GNU 9.7.
That established the harness worked; it was not counted as native GNU 9.12 proof.
The first native attempt exposed missing Automake BUILT_SOURCES preparation.
The passing commit fixes build order without editing GNU's implementation.

## Platform and publication limits

These native results cover the exact platforms above. They do not prove every
older macOS point release, every Linux libc or every possible signal timing race.
Use the Homebrew/source build on a different compatible platform rather than
assuming a prebuilt archive supports it. Source builds use the local compiler's
normal deployment target; no oldest-supported-macOS claim has been validated.

Messages are English because translated GNU catalogues are not shipped. Kernel
limitations and all intentional differences are in [compatibility.md](compatibility.md).

[Release run 35512205946](https://github.com/KSonny4/timeout/actions/runs/35512205946)
was started from this passing implementation commit. Publication is a separate
state: check that run and the repository's Releases page for the actual result.
No Homebrew core acceptance, bottles, code-signing/notarisation or model-registry
registration is claimed.
