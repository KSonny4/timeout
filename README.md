# timeout for macOS

**The GNU `timeout` command, installed on its own.** Apple Silicon, Intel Mac,
and Linux builds. The runtime is the unchanged C implementation from GNU
coreutils 9.12, including its gnulib portability code. This repository maintains
standalone packaging, installation and compatibility tests. It does not claim
that the GNU implementation was written here.

## Install with Homebrew

```sh
brew tap ksonny4/timeout https://github.com/KSonny4/timeout
brew install ksonny4/timeout/timeout
timeout --version
```

This custom tap uses the repository URL explicitly because its name is `timeout`,
not `homebrew-timeout`. Review and approve the formula if Homebrew requests trust.
The formula builds from checksum-pinned GNU source and installs only `timeout`.
It needs Apple's Command Line Tools, which Homebrew normally checks for.

**Already have coreutils? Keep it.** `brew install coreutils` also provides GNU
`timeout`. These packages conflict because both install the same command.
There is no reason to remove a working GNU installation just to use this one.
Check `command -v timeout` and `timeout --version` first.

## Use

```sh
timeout 10s command arg1 arg2
timeout -k 2s 10s command       # TERM after 10s; KILL 2s later if needed
timeout --preserve-status 10s command
timeout --foreground 10s interactive-command
timeout -s INT -v 30s command
```

The interface is `timeout [OPTION]... DURATION COMMAND [ARG]...`. Durations accept
GNU floating-point syntax and `s`, `m`, `h`, `d` suffixes. Zero disables the
associated timer. Arguments are passed directly to the command, without adding
a shell. Explicitly use `sh -c '...'` for a shell pipeline.

| Status | Meaning |
| --- | --- |
| Child's status | Command finishes normally, or `--preserve-status` applies |
| 124 | Deadline expires without `--preserve-status` |
| 125 | `timeout` itself fails, including invalid arguments |
| 126 | Command exists but cannot be invoked |
| 127 | Command cannot be found |
| 137 | Command or monitor is killed with SIGKILL |

## Other installation routes

Source installation requires Python 3.12+, a C compiler, make and curl. The
installed executable has **no Python, Rust, Homebrew or daemon requirement**.

```sh
git clone https://github.com/KSonny4/timeout.git
cd timeout
python3 tools/timeoutctl.py build
python3 tools/timeoutctl.py test
python3 tools/timeoutctl.py install --prefix "$HOME/.local"
export PATH="$HOME/.local/bin:$PATH"
```

Prebuilt binaries are published in
[release v9.12.0](https://github.com/KSonny4/timeout/releases/tag/v9.12.0).
Download the versioned installer:

```sh
curl --fail --location --proto '=https' --proto-redir '=https' \
  --output timeout-install-9.12.0.sh \
  https://github.com/KSonny4/timeout/releases/download/v9.12.0/install.sh
```

Inspect that script before executing it, then run:

```sh
sh timeout-install-9.12.0.sh --version 9.12.0 --prefix "$HOME/.local"
export PATH="$HOME/.local/bin:$PATH"
timeout --version
```

The installer requires that version's release assets and SHA256SUMS to exist.
It never uses `sudo`, edits shell configuration, or overwrites another executable.
Checksums protect transfer integrity; they are not independent publisher signatures.
Manual extraction of the release archive also works. Native release binaries are
built and tested on macOS 15.7.9 and Ubuntu 24.04/glibc 2.39, each for ARM64 and
x86_64. Other OS versions may build locally through Homebrew or the source recipe;
compatibility of prebuilt archives with older releases is not established.

## Compatibility and verification

`upstream.json` pins GNU's release archive and SHA-256. Source files and all
upstream timeout tests are checked against that archive after building and testing.
The build prepares GNU's generated headers before compiling only `src/timeout`.
Additional GNU commands built by the test harness are never installed.

CI runs all **six GNU 9.12 timeout test scripts**, plus **125 repository tests**
covering the executable, packaging, installer and fixture/cleanup regressions, on
four native OS/architecture runners. Homebrew installation and `brew test` have
their own Mac jobs. A separate public-install workflow downloads the published
installer and binaries, runs the current suite against the installed executable,
checks overwrite refusal and runs 125 repeated signal tests per target.

Actual results and skips are retained as JSON and upstream logs. The
[verification record](docs/verification.md) distinguishes the released binary,
verification-harness revision, historical 114/115-test results and final 125-test
checks. See [Actions](https://github.com/KSonny4/timeout/actions) for later
candidates; workflow configuration alone is not a passing result.

The contract is GNU 9.12's native platform behaviour. Linux-only parent-death
signals and PID namespaces cannot be reproduced identically on macOS. English
messages are used (`--disable-nls`); translated GNU message catalogues are not
shipped. Signal numbers, system error wording and timer resolution can differ
between kernels. See [the exact compatibility boundary](docs/compatibility.md).
No finite test suite proves every possible timing race or kernel state.

## Agents and maintainers

[llms.txt](llms.txt) provides install/usage pointers. [AGENTS.md](AGENTS.md) supplies
repository development instructions. The install/use skill lives at
[.agents/skills/gnu-timeout/SKILL.md](.agents/skills/gnu-timeout/SKILL.md).
These files help clients that read them; they do not automatically teach ChatGPT
or register the package with every agent. Public documentation, a working tap
and release assets are the distribution paths.

See [release procedure](docs/releasing.md) and [contribution rules](CONTRIBUTING.md).
GNU's executable and source are GPL-3.0-or-later. Original packaging/test code in
this repository is MIT-licensed. Release archives include GNU's COPYING, AUTHORS
and complete corresponding source with the build recipe.
