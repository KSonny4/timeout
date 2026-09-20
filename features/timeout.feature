Feature: GNU timeout command-line compatibility
  The executable uses unmodified GNU coreutils source. Scenario titles map to
  executable tests; the upstream harness supplies additional signal regressions.

  Scenario: test_command_finishes_before_deadline
    When the child finishes before its deadline
    Then timeout propagates the child's exit status

  Scenario: test_deadline_returns_124
    When the deadline expires with the default TERM signal
    Then timeout returns 124

  Scenario: test_preserve_status_returns_command_status
    When preserve-status is selected
    Then the child's status is returned even after expiry

  Scenario: test_default_mode_terminates_process_group
    When the deadline expires in default mode
    Then descendants in the process group receive the signal

  Scenario: test_foreground_leaves_descendants_running
    When foreground mode is selected
    Then timeout signals its immediate child and leaves descendants alone

  Scenario: test_kill_after_terminates_term_ignoring_child
    When the child ignores TERM and the grace period expires
    Then KILL terminates it and status 137 is returned

  Scenario: test_stdin_stdout_stderr_are_preserved
    When binary data flows through the command
    Then timeout leaves its input and output bytes unchanged
