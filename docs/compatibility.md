# Compatibility contract

## Reference

GNU coreutils **9.12**, archived and SHA-256 pinned in `upstream.json`.
`src/timeout.c`, its helpers, gnulib and the upstream test scripts are unmodified.
Packaging version 9.12.0 does not replace GNU's `--version` output.
GNU is the reference, rather than BusyBox timeout or every distribution patch.

| Area | Contract and evidence |
| --- | --- |
| Options | `-f/--foreground`, `-k/--kill-after`, `-p/--preserve-status`, `-s/--signal`, `-v/--verbose`, `--help`, `--version`; unchanged GNU getopt parsing |
| Durations | GNU cl_strtod parsing, floating point, exponents, suffixes, zero, overflow and positive underflow; invalid forms rejected |
| Execution | Direct fork/execvp, original argv bytes, stdin/stdout/stderr, environment and working directory |
| Exit status | Propagate child status; GNU 124,125,126,127 and signal exits; SIGKILL yields 137 even in foreground mode |
| Signals | GNU signal names, case handling and encoded numeric statuses; forwarding and grace deadline |
| Process groups | Default group signalling, foreground immediate-child behaviour, stopped-child continuation |
| Diagnostics | GNU diagnostics under the C locale; no rebranded help or version |
| Licensing | Upstream attribution retained; complete GNU source included with binary releases |

## Platform boundaries

On Linux GNU can use `prctl(PR_SET_PDEATHSIG)` to signal a child if its monitor
dies. Darwin does not provide that facility. This package follows GNU's Darwin
implementation; it cannot promise Linux parent-death behaviour. Similarly,
`unshare --pid` tests concern Linux namespaces and are an explicit macOS skip.

Use signal names in portable scripts. Numeric signal assignments and system
error text are platform-specific. GNU uses available platform timers: typically
POSIX timers on Linux and setitimer on Darwin. Scheduling and resolution are
not hard real-time guarantees. GNU timeout does not promise to kill descendants
that escaped its process group, and foreground mode deliberately leaves children
of the monitored command outside timeout's group signalling.

Builds use `--disable-nls`, with English messages rather than translated GNU
catalogues, to avoid a separate runtime gettext dependency. This is a deliberate
packaging difference from an NLS-enabled GNU installation. Locale-aware numeric
parsing remains GNU's own code. Exact byte comparisons should use `LC_ALL=C`.

## Tests and gates

`python3 tools/timeoutctl.py test` invokes GNU's actual Automake/Perl harness,
selecting every `.sh` and `.pl` file in the pinned `tests/timeout` directory:
`init-parent`, `timeout-blocked`, `timeout-group`, `timeout-large-parameters`,
`timeout-parameters` and `timeout`. These are six scripts with multiple assertions,
not six individual behaviour assertions. Other coreutils commands' suites are
outside this standalone product. GNU shared-helper tests are not all run here.

Test helpers are built from the same source: env, sleep, kill, getlimits, true,
false, printf and yes. On macOS only, a test-only Python setsid command supplies
the missing group-creation harness dependency. Upstream test files stay intact.
The helper is never installed or included in binary distributions.

The CI gate permits only the Linux PID-namespace script to skip on macOS.
Linux CI explicitly permits a sudo retry of this test on its disposable runner
and requires it to pass. Local tests may report this one skip if namespaces are
unavailable. Unexpected skips, absent logs, failures and errors fail the gate.
JSON reports preserve exact outcomes rather than counting skips as passes.

The additional Python suite isolates child process groups, applies independent
watchdogs, and cleans up children on failures. It covers CLI forms, byte handling,
signal/exit rules, descendants, basic PTY access and installer failure paths.
The PTY test checks terminal file descriptors; it is not a full interactive-shell
job-control proof. Timing races and resource-exhaustion fault injection are not
exhaustively tested. Source identity provides assurance beyond sampled scenarios.

## Sources

- https://github.com/coreutils/coreutils/blob/v9.12/src/timeout.c
- https://github.com/coreutils/coreutils/blob/v9.12/src/operand2sig.c
- https://github.com/coreutils/coreutils/tree/v9.12/tests/timeout
- https://www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html
- https://github.com/Homebrew/homebrew-core/blob/main/Formula/c/coreutils.rb
