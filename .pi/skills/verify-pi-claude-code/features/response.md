# Subscription response

A user selects a Claude Code subscription model and receives a model response in Pi.

## Sub-features

- `response-auth`: the CLI has a subscription login.
- `response-text`: the selected model returns the requested text.
- `response-stream`: Pi emits completed messages and settles.

## How to get to it (user POV)

- Run Pi with `--provider claude-code --model claude-fable-5-1`.
- In interactive Pi, choose the `Claude Code Subscription (Experimental)` provider and a model.
- Run `/claude-code-status` in interactive Pi to check installation/login.

## Driving it with verify.py

Preconditions: launch and doctor in `../SKILL.md` pass.

- **Check auth.** Run `"$VERIFY" doctor`. Require `loggedIn: true` and `authMethod: "claude.ai"`.
- **Request text.** Run `"$VERIFY" text --model claude-fable-5-1`. The recorded command requests a unique token. Completed assistant text must equal it, with provider `claude-code` and the selected model.
- **Inspect proof.** Require `passed: true` and `scratch_removed: true` in the printed directory's `summary.json`. Confirm `first.events.jsonl` and `first.exit.txt` survive cleanup.

## Gotchas

- Doctor proves login, not available quota or successful generation.
- The status command and picker are interactive entry points, not covered by this JSON CLI journey.
- `--offline` still permits live model requests.
