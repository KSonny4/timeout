# Standalone build and behaviour

```mermaid
flowchart TD
    A[GNU 9.12 source archive] --> B[Verify pinned SHA-256]
    B --> C[Configure portability and generate BUILT_SOURCES]
    C --> D[Compile unchanged timeout and gnulib]
    D --> E[Six original timeout test scripts]
    E --> F[114 repository tests]
    F --> G[Archive binary plus licence and corresponding source]
    G --> H[Extracted-binary smoke tests and linkage check]
    H --> I[Native verification passes]
    J[Homebrew formula builds same GNU source] --> K[brew test and repository tests]
    I --> L[Release gate]
    K --> L
    L --> M[GitHub release with checksums and evidence]
```

Journey: a Mac user installs the formula, runs `timeout -k 2s 10s command`, and
gets the same GNU option parsing and command exit contract. The timeout monitor
starts the command, sends TERM after ten seconds, and escalates to KILL after
two further seconds only if the monitored command is still running.

```mermaid
flowchart TD
    A[Parse options and duration] --> B{Arguments valid?}
    B -- No --> X[Exit 125]
    B -- Yes --> C[Create process group unless foreground]
    C --> D[Fork and exec command]
    D --> E{Command started?}
    E -- Missing --> Y[Exit 127]
    E -- Cannot invoke --> Z[Exit 126]
    E -- Yes --> F{Child exits or deadline fires}
    F -- Child exits --> G[Return child status]
    F -- Deadline --> H[Send configured signal]
    H --> I{Kill-after deadline required?}
    I -- Yes --> J[Send KILL if still running]
    J --> K[Exit 137]
    I -- No --> L[Wait for child]
    L --> M[Exit 124 or preserved child status]
```

This is a conceptual flow. GNU also handles external signals, races and timer
failures in its unchanged implementation. `--foreground` signals the immediate
child; the default mode signals its process group. This CLI has no service state,
network API, background daemon, deployment controller or runtime telemetry.
