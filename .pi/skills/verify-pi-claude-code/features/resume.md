# Saved-session replay

A user reopens an existing Pi conversation and Claude remembers prior conversation content.

## Sub-features

- `resume-save`: a first process records a unique token in its isolated session.
- `resume-reopen`: a second Pi process opens the same session.
- `resume-recall`: Claude returns the prior token without receiving it in the second prompt.

## How to get to it (user POV)

- Start or reopen a session with `--session-id`.
- Continue a previous session with `--continue`.
- Choose an older session with `--resume` or `--session`.

## Driving it with verify.py

Preconditions: launch and doctor pass.

- **Save and reopen.** Run `"$VERIFY" resume --model claude-fable-5-1`. The helper starts two separate Pi processes using its private session directory and `--session-id verification`.
- **Inspect actions.** Compare `first.command.json` with `resumed.command.json`: only the first prompt contains the token.
- **Observe recall.** The second process's final assistant response must equal the token in the first prompt.
- **Inspect cleanup.** Require `passed: true` and `scratch_removed: true`. Both commands, event streams, exit codes, and stderr files must survive.

## Gotchas

- This checks fresh-process replay, not warm-process reuse.
- The private session directory prevents collision with another run using the same session ID.
- Alternate session selectors and the interactive selector remain unverified by this journey.
