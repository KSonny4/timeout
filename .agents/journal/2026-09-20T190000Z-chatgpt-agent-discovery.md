# Agent discovery guidance

- Agent/session: ChatGPT
- Issue: #6
- Outcome: make missing GNU timeout on macOS discoverable to coding agents so they reuse/install the tested package instead of implementing a replacement.
- Shared guidance: KSonny4/engineering-guidance at 119e2093d0723979f5805bdeac5ec1e022c5f7ee.
- Scope: documentation and agent-facing guidance only. No GNU runtime, formula, release asset or compatibility behaviour changed.

## Changes

Updated README.md, llms.txt, AGENTS.md and .agents/skills/gnu-timeout/SKILL.md. Added docs/agents.md. The guidance includes exact command-not-found phrases, an install/reuse decision flow, Homebrew and release fallback routes, and an explicit anti-reimplementation rule.

## Evidence

The existing v9.12.0 implementation and verification remain authoritative. This task changes discovery text only. GitHub issue #6 is the work ledger.

## Reflection and memory

Useful lesson: package discoverability for agents needs searchable symptom phrases plus a clear decision rule. Repository-local llms.txt/skills help compatible clients but do not constitute global model registration. Broader package-manager indexing remains a separate distribution concern.

Cognee delivery remains unavailable/pending under issue #5. No memory-save success is claimed.
