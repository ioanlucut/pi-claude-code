# Tool round trip

Claude requests tools, Pi executes them, and Claude continues from their real results.

## Sub-features

- `tools-read`: Pi reads an unpredictable token from a scratch file.
- `tools-write`: Pi writes that exact content into a second file.
- `tools-follow-up`: the model responds after both tool results without a cache-marker rejection.

## How to get to it (user POV)

Ask Pi to read a file, write a copy, and report completion. This works in interactive
Pi and through the `--mode json` CLI.

## Driving it with verify.py

Preconditions: launch and doctor pass; each selected model is available on the subscription.

- **Fable.** Run `"$VERIFY" tools --model claude-fable-5-1`.
- **Opus.** Run `"$VERIFY" tools --model claude-opus-5-5`.
- **Observe actions.** Each `first.events.jsonl` must show `tool_execution_start` for `read`, then `write`, with successful matching completion events and at least three completed assistant messages.
- **Verify state.** The helper independently reads the output before cleanup. Retained `input.txt` and `output.txt` must match exactly, including the newline. Final assistant text must be `VERIFIED`.
- **Verify cleanup.** Require both summary booleans to be `true` and retained evidence files to exist.

## Gotchas

- No tool execution event means the model did not exercise the tool path, even if it claims success.
- A failure after a successful tool call is still a failed journey; do not stop proof at the tool result.
- This reproduces the user path affected by cache-marker errors. Unit regression tests separately prove the exact marker count.
- Interactive execution and tools beyond `read`/`write` are not covered.
