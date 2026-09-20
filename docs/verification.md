# Verification record: 20 September 2026

## Final verified outcome

Released GNU runtime: `7668f5aef89b4d20897ccf8087f04dc3755ec4bf`, tag **v9.12.0**.
Final verification harness: `cad0d0052b56b902a8d2c371d06c15876f341065`.
GNU reference: unchanged coreutils **9.12** source and timeout-specific tests.
Later documentation-only commits do not change these tested identities.

[Native compatibility run 35515616455](https://github.com/KSonny4/timeout/actions/runs/35515616455)
passed all six jobs: four native source build/test/package jobs and both Homebrew
installation jobs. [Public installation run 35515616466](https://github.com/KSonny4/timeout/actions/runs/35515616466)
passed all four native jobs against the actual downloaded v9.12.0 executables.

| Native target | GNU timeout scripts | Current repository suite | Repeated signal tests against public binary | Public installation and overwrite refusal |
| --- | --- | --- | --- | --- |
| macOS 15.7.9 ARM64 | 5 passed, 1 expected skip | 125 passed | 125 passed | Passed |
| macOS 15.7.9 x86_64 | 5 passed, 1 expected skip | 125 passed | 125 passed | Passed |
| Ubuntu 24.04 x86_64, glibc 2.39 | 6 passed | 125 passed | 125 passed | Passed |
| Ubuntu 24.04 ARM64, glibc 2.39 | 6 passed | 125 passed | 125 passed | Passed |

The repository and repeated-test suites report zero failures, errors and skips.
The sole accepted upstream skip on each Mac is `tests/timeout/init-parent.sh`,
which requires Linux PID namespaces. The six upstream entries are scripts with
multiple assertions, not six individual assertions. Shared tests for unrelated
coreutils programs are outside this standalone test claim.

The current 125 repository tests comprise 94 executable/signal-fixture cases,
21 packaging/installer cases and 10 cleanup guard cases. The separate repeated
suite runs five signal methods 25 times each; it adds no new unique requirements.
Native jobs also test the executable extracted from the final archive. Both
Homebrew jobs install the exact candidate formula, run `brew test` and the
repository suite against the installed binary.

### Evidence inspected

All four final public evidence ZIPs were downloaded. Their SHA-256 values were
checked against GitHub metadata, and public-install.json, contract.json and
signal-stress.json were inspected. The final native Apple Silicon evidence ZIP
was also downloaded and its digest, contract and upstream reports inspected.
Other final native/Homebrew conclusions were read from GitHub job/step results.
The durable measured summary, identities and digests are in
[evidence/public-install-v9.12.0-cleanup.json](evidence/public-install-v9.12.0-cleanup.json).
Workflow artefacts expire after 14 days; this checked-in summary preserves the
measured outcome, not the complete raw logs or a cryptographic attestation.

Public installation downloads the versioned installer, checks its GitHub asset
SHA-256 and compares it with tagged source. The installer verifies the downloaded
binary archive checksum. Installation uses an isolated user prefix containing
spaces, without sudo. A second installation must refuse to overwrite the existing
executable, and its before/after hashes must match. Release and harness source
identities are recorded separately. These checks passed on every target above.

## Original release and historical evidence

[Native run 35511874592](https://github.com/KSonny4/timeout/actions/runs/35511874592)
passed all six jobs for the released implementation. All four original native
artefact archives were downloaded and their build, upstream, contract and linkage
reports inspected. Both Homebrew jobs passed; the ARM Homebrew log explicitly
reported 114 tests and OK.

| Released target | Original repository tests | Executable bytes | Original GNU scripts |
| --- | --- | --- | --- |
| macOS ARM64 | 114 passed | 130,872 | 5 passed, 1 expected skip |
| macOS x86_64 | 114 passed | 113,472 | 5 passed, 1 expected skip |
| Linux x86_64 | 114 passed | 207,488 | 6 passed |
| Linux ARM64 | 114 passed | 229,040 | 6 passed |

The original suite had 93 executable cases and 21 packaging/installer cases.
The Apple Silicon binary links only to `/usr/lib/libSystem.B.dylib`.
Archives are larger because they include complete GNU source, licences and the
build recipe. The final public-install reports confirm the same executable sizes.

[Release run 35512205946](https://github.com/KSonny4/timeout/actions/runs/35512205946)
passed four native jobs, two Homebrew jobs and publication.
[Release v9.12.0](https://github.com/KSonny4/timeout/releases/tag/v9.12.0)
was published at **2026-09-20T13:20:25Z**, with four platform archives, checksums,
installer and original verification evidence. No v9.12.0 source, tag or asset
was replaced during subsequent fixture corrections.

[Intermediate public run 35514608768](https://github.com/KSonny4/timeout/actions/runs/35514608768)
passed on all four platforms with harness
`2411db902cab04acafa04a99aa52eda9d7d49078`: 115 repository tests and 100 repeated
signal tests each. All four ZIP digests and reports were inspected. Its historical
summary remains in [evidence/public-install-v9.12.0.json](evidence/public-install-v9.12.0.json).
Those counts are historical and are not silently relabelled as the final 125-test
harness result.

## Retained failures and harness corrections

### Signal fixture interpreter shutdown

[First live run 35514156386](https://github.com/KSonny4/timeout/actions/runs/35514156386)
installed successfully on all four targets. Apple Silicon failed one subtest:
numeric SIGUSR1 returned 158 instead of the fixture's requested 41. The other
three targets passed their entire suite and overwrite checks.

The fixture already waited for readiness after the handler was installed.
GNU `src/timeout.c:cleanup` signals the child PID and then its group. CPython
3.13.15 `Modules/signalmodule.c:_PySignal_Fini` resets custom handlers to SIG_DFL
during `sys.exit` finalisation. A second delivery during that interval is a
source-supported explanation; no kernel trace established the exact interleaving.

Commit `76d880b7e1fbcfc114d9752a9a18231129f6cbd9` changes disposable signal/exit
fixtures to `os._exit`. Expected statuses, aliases, readiness, watchdogs and
cleanup remain enforced. The added deterministic regression installs an atexit
hook that would return 99 with `sys.exit`, while immediate exit returns 41.
This was checked locally and included in native tests. GNU's behaviour for real
commands, including duplicate signal delivery, is unchanged.

A bounded local diagnostic against GNU 9.7 passed ten old and ten corrected
invocations. It did not reproduce the intermittent race and is not GNU 9.12
native evidence. A larger local attempt hit its execution watchdog and produced
no useful conclusion.

### Post-exit process-group cleanup

[Fresh native run 35514608769](https://github.com/KSonny4/timeout/actions/runs/35514608769)
passed both Homebrew jobs, both Linux native jobs and Intel macOS. Apple Silicon
passed the five applicable unchanged GNU scripts and skipped the Linux-only one,
then reported zero assertion failures and one repository cleanup error:

```text
test_kill_after_terminates_term_ignoring_child
signal_fixture -> finally -> cleanup -> os.killpg(..., SIGKILL)
PermissionError: [Errno 1] Operation not permitted
```

This occurred after `communicate` had collected the monitored process. The
failure archive, ID 10605394903, was downloaded and inspected; SHA-256:
`727258357df497ac98c956380abc73697d64b71fd6171f9cc9216311bc1bf63b`.
No process snapshot or kernel trace established why that specific killpg failed.

The test-only `process_cleanup.py` helper still signals the isolated group and
always reaps the direct child. PermissionError is accepted only when the leader
has exited and a bounded successful native `ps` snapshot shows no live group
members. A live leader/member, unknown state, failed inspection, or malformed
snapshot remains an error. Ten guard tests cover those branches and native ps
format; they passed locally and in the final native/public suites. The affected
kill-after case was also added to repeated tests on all four targets.

No GNU implementation, original upstream test, formula, installer or released
binary changed for either correction. No failed test was skipped or marked
expected, and no unchanged failed run was retried until green.

Source references:
- https://github.com/coreutils/coreutils/blob/v9.12/src/timeout.c
- https://github.com/python/cpython/blob/v3.13.15/Modules/signalmodule.c

## Reproduction and boundaries

```sh
python3 tools/timeoutctl.py build
python3 tools/timeoutctl.py test
python3 tools/timeoutctl.py package
```

Use Actions > Published installation with version `9.12.0` for live download
verification. See [releasing.md](releasing.md) for future releases' post-publication
job; the original v9.12.0 publication predates that job.

Linux CI enables its test-only root PID-namespace retry on disposable runners.
Normal local testing does not silently use sudo. An early local harness pass
against GNU 9.7 was not counted as native 9.12 proof. The first build attempt
exposed missing Automake BUILT_SOURCES preparation, corrected without editing GNU.

Results cover the exact native platforms above. They do not establish every older
macOS release, Linux libc, scheduling race or shared GNU helper. Source builds use
the local compiler's normal deployment target; no oldest macOS version is claimed.
Messages are English because translated catalogues are not shipped. OS signal
numbers, error wording, timer precision and Linux-only kernel facilities retain
their platform-specific behaviour. See [compatibility.md](compatibility.md).

No Homebrew core acceptance, bottles, Apple signing/notarisation, enabled GitHub
immutable-release setting or automatic model registration is claimed. Factual
Cognee memory reconciliation remains pending in issue #5; CLI delivery is verified.
