# pi-claude-code

This Pi extension lets you use your Claude Pro or Max subscription in Pi by
routing all Claude model requests through the official Claude Code CLI.

Pi still handles conversation history, approvals, compaction, and tool
execution. Claude Code only talks to the model. It never runs tools itself.

> [!NOTE]
> **This is a fork.** The original is
> [earendil-works/pi-claude-code](https://github.com/earendil-works/pi-claude-code)
> by [Armin Ronacher](https://github.com/mitsuhiko) at
> [Earendil Works](https://earendil.com/). This fork,
> [ioanlucut/pi-claude-code](https://github.com/ioanlucut/pi-claude-code), keeps
> fixes that upstream has not merged yet. Each one has a test:
>
> | Problem upstream                                                                                                                 | Here                                                                                               | Upstream                                                                                                                           |
> | -------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
> | A switch from Codex to Claude in one conversation fails with HTTP 400: Codex tool-call IDs such as `call_…\|fc_…` contain `\|`.  | IDs that Claude rejects get stable valid replacements.                                             | [#6](https://github.com/earendil-works/pi-claude-code/pull/6), [#3](https://github.com/earendil-works/pi-claude-code/pull/3)       |
> | A request after a tool result, or a second turn, fails with `A maximum of 4 blocks with cache_control may be provided. Found 5.` | One cache breakpoint per message, four in total.                                                   | [#10](https://github.com/earendil-works/pi-claude-code/issues/10), [#11](https://github.com/earendil-works/pi-claude-code/pull/11) |
> | A lost connection to Anthropic ends the turn: Pi does not retry it, and the error shows only `AggregateError`.                   | The error names the network codes (`ETIMEDOUT`, …) and ends with `connection lost`, so Pi retries. | [#8](https://github.com/earendil-works/pi-claude-code/issues/8), [#4](https://github.com/earendil-works/pi-claude-code/pull/4)     |
>
> Install the fork with
> `pi install https://github.com/ioanlucut/pi-claude-code`. See
> [Fork](#fork) to take upstream changes.

> [!WARNING]
> **The future of this extension is uncertain.** Right now it works by running
> Pi's requests through the official Claude Code CLI in non-interactive mode
> (`claude -p`), and that usage counts against your normal Claude subscription
> limits. In May 2026 Anthropic
> [announced](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan)
> that `claude -p`, Agent SDK, and third-party usage would move to a separate,
> smaller "Agent SDK credit" billed at API rates. Anthropic has since put that
> change on hold and says it will give advance notice before any future change.
>
> Until then the extension keeps working as described here, but that could
> change at any time. If Anthropic changes how `claude -p` usage is billed, this
> extension may cost more, stop drawing from your subscription, or stop working
> altogether. See Zed's
> [write-up](https://zed.dev/blog/anthropic-subscription-changes) for more
> background.

## Requirements

- Pi
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code), installed and
  on your `PATH`:

  ```sh
  npm install -g @anthropic-ai/claude-code
  ```

- A Claude subscription that you are logged into with Claude Code

## Installation

```sh
pi install https://github.com/earendil-works/pi-claude-code
```

Then pick a model from the **Claude Code Subscription (Experimental)** provider
in Pi.

## Login and logout

Claude Code handles authentication. Log in and out with the Claude Code CLI:

```sh
claude auth login
claude auth logout
```

The extension uses whatever login Claude Code currently has. You don't need
Pi's `/login` or `/logout` for this provider. The extension doesn't read, copy,
or store your Claude Code credentials.

Run `/claude-code-status` in Pi to check that Claude Code is installed and
logged in.

## Configuration

These environment variables are optional:

- `PI_CLAUDE_CODE_COMMAND`: path or name of the Claude Code executable
  (default: `claude`).
- `PI_CLAUDE_CODE_CONFIG_DIR`: Claude Code config directory to use. The
  extension passes it to Claude Code as `CLAUDE_CONFIG_DIR`.

## Usage and billing

Requests made through this extension count against your Claude subscription's
usage quota and rate limits, the same as any other Claude Code usage. The
extension does not give you separate or unlimited usage.

To avoid silently changing how you're authenticated or billed, the extension
refuses to run if your environment sets an API key, proxy, Bedrock, Vertex, or
Foundry override for Claude Code.

## Limitations

- The extension is experimental.
- Branching, editing earlier messages, or changing settings mid-conversation
  starts a fresh Claude Code process that replays the conversation. The first
  response after that can be slower and may use more quota.
- Complex tool schemas (nullable types, `oneOf`, `allOf`, `anyOf`) may be
  simplified before Claude sees them.
- Adding or removing tools in the middle of a conversation keeps the prompt
  cache only on supported models. On other models it may use more quota.

For details on how the extension works internally, see
[ARCHITECTURE.md](ARCHITECTURE.md).

## Fork

Take upstream changes:

```sh
git remote add upstream git@github.com:earendil-works/pi-claude-code.git  # once
git fetch upstream && git rebase upstream/main
npm test && npm run check
```

When upstream merges a fix, drop its commit here. When upstream has all of
them, go back to `pi install https://github.com/earendil-works/pi-claude-code`.

The license stays the upstream [MIT License](LICENSE), copyright Armin
Ronacher.

## Credits

pi-claude-code is the work of [Armin Ronacher](https://github.com/mitsuhiko)
and [Earendil Works](https://github.com/earendil-works). The design is theirs:
Pi keeps the conversation and runs the tools, and Claude Code only talks to the
model through a turn relay. This fork adds only the fixes above and their
tests. The fixes follow reports and pull requests from
[@adstastic](https://github.com/adstastic) (#6),
[@injaneity](https://github.com/injaneity) (#3),
[@jdbrew88](https://github.com/jdbrew88) (#10, #11),
[@B0und](https://github.com/B0und) (#8) and
[@series-phil](https://github.com/series-phil) (#4). Thank you all.
