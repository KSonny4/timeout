# Verification record: 20 September 2026

## Released implementation and original native builds

The released runtime is implementation commit
`7668f5aef89b4d20897ccf8087f04dc3755ec4bf`, tag `v9.12.0`.
GNU reference: coreutils 9.12, unchanged source.

[Native compatibility run 35511874592](https://github.com/KSonny4/timeout/actions/runs/35511874592)
completed successfully across all six jobs. The four native artefact archives
were downloaded and their build.json, upstream.json, contract.json and linkage
reports inspected. Homebrew job results were read from GitHub Actions; the ARM
Homebrew job log explicitly reports `Ran 114 tests` and `OK`.

| Native target | GNU timeout scripts | Repository tests at release | Executable bytes | Distribution and linkage checks |
| --- | --- | --- | --- | --- |
| macOS 15.7.9 ARM64 | 5 passed, 1 expected skip | 114 passed, 0 skipped | 130,872 | Passed |
| macOS 15.7.9 x86_64 | 5 passed, 1 expected skip | 114 passed, 0 skipped | 113,472 | Passed |
| Ubuntu 24.04 x86_64, glibc 2.39 | 6 passed, 0 skipped | 114 passed, 0 skipped | 207,488 | Passed |
| Ubuntu 24.04 ARM64, glibc 2.39 | 6 passed, 0 skipped | 114 passed, 0 skipped | 229,040 | Passed |

Both Homebrew jobs built the exact candidate formula from source, ran `brew test`
and passed all 114 repository tests against the installed executable. All tests
reported zero failures/errors. The Mac skip is `tests/timeout/init-parent.sh`,
which depends on Linux PID namespaces. No other upstream skip was accepted.

The original 114 repository tests comprise 93 executable contract tests and 21
packaging/installer tests. The six upstream scripts each contain their own
assertions; script counts must not be presented as individual assertion counts.
Native jobs also reran the repository suite against the executable extracted from
the final archive. Packaging fixture tests alone do not prove that public-release
download installation works.

The Apple Silicon binary links only to `/usr/lib/libSystem.B.dylib`. Binary
archives are larger than the executable because complete GNU source, licensing
and the build recipe are deliberately included.

## Publication and actual public installation

[Release run 35512205946](https://github.com/KSonny4/timeout/actions/runs/35512205946)
completed successfully with four native jobs, two Homebrew jobs and publication.
[Release v9.12.0](https://github.com/KSonny4/timeout/releases/tag/v9.12.0) was published
at 2026-09-20T13:20:25Z. Its four platform archives, checksums, installer and original
verification evidence are public. No v9.12.0 source, tag or asset was replaced by
the continuation described below.

[Public installation run 35514608768](https://github.com/KSonny4/timeout/actions/runs/35514608768)
subsequently passed on all four native targets. It tested the actual downloaded
v9.12.0 binaries using verification harness
`2411db902cab04acafa04a99aa52eda9d7d49078`. This harness includes one additional
fixture regression, bringing the repository suite to 115 tests.

| Public installer target | Current suite | Repeated signal tests | Public install and overwrite refusal |
| --- | --- | --- | --- |
| macOS ARM64 | 115 passed, 0 skipped | 100 passed, 0 skipped | Passed |
| macOS x86_64 | 115 passed, 0 skipped | 100 passed, 0 skipped | Passed |
| Linux x86_64 | 115 passed, 0 skipped | 100 passed, 0 skipped | Passed |
| Linux ARM64 | 115 passed, 0 skipped | 100 passed, 0 skipped | Passed |

Every row has zero failures and errors. The installer was downloaded from its
public release URL, checked against GitHub's asset SHA-256, and compared with the
tagged installer source before execution. The binary archive's own checksum was
checked by that installer. Installation used a temporary user prefix containing
spaces, without sudo. A second installation refused to overwrite the executable,
and before/after binary hashes matched.

The 100 repeated tests are four existing signal-related methods repeated 25 times,
not 100 additional unique contract requirements. All four evidence ZIPs were
downloaded, their GitHub archive digests checked, and public-install.json,
contract.json and signal-stress.json inspected. Their durable measured summary
and artifact identities are in
[evidence/public-install-v9.12.0.json](evidence/public-install-v9.12.0.json).
The workflow's downloadable artefacts expire after 14 days.

## Failure retained and fixture correction

The first live check,
[run 35514156386](https://github.com/KSonny4/timeout/actions/runs/35514156386),
installed successfully on all four targets. Its Apple Silicon suite failed one
subtest: numeric SIGUSR1 returned 158 instead of the fixture's requested 41.
The other three targets passed their complete suite and overwrite checks.

The fixture already waited for the child to print readiness after installing its
handler. GNU's unchanged `src/timeout.c:cleanup` signals the child PID and then its
process group. CPython 3.13.15 `Modules/signalmodule.c:_PySignal_Fini` resets custom
handlers to SIG_DFL during `sys.exit` finalisation. A second signal arriving in
that shutdown interval is a source-supported explanation of the observed status;
no kernel trace was taken, so the exact interleaving is not claimed as proven.

Commit `76d880b7e1fbcfc114d9752a9a18231129f6cbd9` makes the disposable signal/exit
fixtures use `os._exit` instead. Expected statuses, signal aliases, readiness,
watchdogs and cleanup remain enforced. The new
`test_signal_exit_fixture_avoids_interpreter_shutdown` installs an atexit hook
that would produce status 99 with `sys.exit`, making the fixture regression
deterministic without relying on a particular scheduling race. No GNU code,
upstream script, installer or release binary changed; no failure was skipped,
marked expected or retried until green. The passing run above also repeats the
affected methods on every target.

This preserves GNU behaviour for real commands, including any duplicate signal
delivery; the fixture now deliberately exits immediately with its requested status.
A local diagnostic against GNU 9.7 passed ten old and ten corrected invocations,
which did not reproduce the intermittent race and is not native GNU 9.12 proof.

Source references:
- https://github.com/coreutils/coreutils/blob/v9.12/src/timeout.c
- https://github.com/python/cpython/blob/v3.13.15/Modules/signalmodule.c

## Reproduction

```sh
python3 tools/timeoutctl.py build
python3 tools/timeoutctl.py test
python3 tools/timeoutctl.py package
```

To repeat real download/installation verification, run Actions > Published
installation with version `9.12.0`. The workflow records the released binary source
commit separately from the current test-harness commit. See
[releasing.md](releasing.md) for the post-publication job used by future releases.

Linux CI explicitly enables the test-only root PID-namespace retry on disposable
runners. Normal local testing does not silently use sudo.

An earlier local harness run passed 114 tests against the container's GNU 9.7.
That established the harness worked; it was not counted as native GNU 9.12 proof.
The first native attempt exposed missing Automake BUILT_SOURCES preparation.
The passing release commit fixes build order without editing GNU's implementation.

## Platform and publication limits

These native results cover the exact platforms above. They do not prove every
older macOS point release, every Linux libc or every possible signal timing race.
Use the Homebrew/source build on a different compatible platform rather than
assuming a prebuilt archive supports it. Source builds use the local compiler's
normal deployment target; no oldest-supported-macOS claim has been validated.

Messages are English because translated GNU catalogues are not shipped. Kernel
limitations and all intentional differences are in [compatibility.md](compatibility.md).
All timeout-specific GNU scripts are selected; suites for unrelated coreutils
programs and every shared GNU helper are outside this standalone test claim.

The original source-build results and subsequent public-install results refer to
different explicit commits. They are not a claim that every later branch or
workflow run passed. Check the exact candidate in Actions for subsequent changes.
No Homebrew core acceptance, bottles, code-signing/notarisation, immutable-release
setting or model-registry registration is claimed. Cognee memory reconciliation
is tracked separately in issue #5 and is not claimed complete.
