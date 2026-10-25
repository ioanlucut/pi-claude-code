---
name: verify-pi-claude-code
description: Verify the pi-claude-code provider through real Pi CLI requests. Use after transport, cache, tool replay, or session changes; capture live Claude responses and Pi tool execution.
---

# Verify pi-claude-code

Read the [feature map](features/README.md), then select its journeys.
Primary surface: Pi's provider and tools, driven through JSON CLI mode.
The interactive model picker and `/claude-code-status` are secondary surfaces.

## Launch

From this plugin checkout:

```bash
REPO="$(git rev-parse --show-toplevel)"
VERIFY="$REPO/.pi/skills/verify-pi-claude-code/scripts/verify.py"
test -d "$REPO/node_modules" || (cd "$REPO" && npm ci --ignore-scripts)
"$VERIFY" doctor
```

No build or long-lived server is needed: Pi loads `src/index.ts` directly.
Doctor must report this checkout, installed versions, and a valid `claude.ai`
subscription login. If needed, the human runs `claude auth login` first.
Python `3`, Node.js `22.19+`, `pi`, and `claude` must be on `PATH`.
The helper honors `PI_CLAUDE_CODE_COMMAND` and `PI_CLAUDE_CODE_CONFIG_DIR`.

Each drive creates a fresh Pi agent directory, working directory, and session.
Only this extension and the named built-in tools load. The Claude CLI uses its
existing subscription login; credentials are neither copied nor printed.
A completed assistant response and `agent_settled` prove readiness.

## Doctor

```bash
"$VERIFY" doctor
```

Read-only: checks versions, subscription status, checkout revision, and the
transport source hash (which identifies uncommitted patches too).
It does not prove that generation quota or a requested model is available.
Conflicting API-key/backend overrides remain errors; fix the shell environment
rather than silently changing authentication.

## Drive

```bash
"$VERIFY" text --model claude-fable-5-1
"$VERIFY" tools --model claude-fable-5-1
"$VERIFY" tools --model claude-opus-5-5
"$VERIFY" resume --model claude-fable-5-1
```

These are real subscription requests, not mocks. Keep the usage-credit opt-in
`PI_CLAUDE_CODE_ALLOW_USAGE_CREDITS` unset unless the user authorizes charges.
The helper's `--offline` suppresses catalog refresh, not model traffic.
No router is loaded: this isolates the provider, not router integration.
Run journeys serially. Scratch/session state is separate, but account quota and
Claude credential storage are shared with the user's CLI.

## Evidence

Each drive prints its evidence directory under `$PI_CLAUDE_CODE_EVIDENCE_DIR`,
or `pi-claude-code-evidence/` in the system temp directory when it is unset.
It retains commands, JSONL events, stderr, exit codes, doctor metadata, and
`summary.json`. Tool journeys also retain the input and independently read
output file. Treat evidence as private: events contain native replay metadata.

A pass requires the real user path: Pi CLI → provider → official Claude CLI →
upstream model → Pi response. Tool proof also requires Pi's execution events,
model follow-ups after tool results, and the exact output file bytes.
An exit code alone is insufficient; the helper rejects assistant errors,
missing settlement, wrong models, missing tools, and incorrect final text.
No test endpoint, mocked response, or internal setter substitutes for this proof.
Report each unrun model or entry point as unverified.

## Cleanup

The helper waits for its own Pi process and removes its scratch directory in
`finally`, including on assertion failure. Pi closes its Claude workers on exit.
Interrupted commands receive `SIGINT`; timed-out processes are stopped by their
owned PIDs, never by process name. No user session or credential is removed.
Evidence stays outside scratch. Require `scratch_removed: true` in
`summary.json`, then confirm the printed evidence directory still exists.

## Helpers

`scripts/verify.py` is executable. The exact invocations appear above.
It resolves its checkout from its own path, so it can also be called by absolute
path from another directory. Use `/maintain-verification-skill` when commands,
models, or user journeys change.
