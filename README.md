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
> | A request after a tool result, or a second turn, fails with `A maximum of 4 blocks with cache_control may be provided. Found 5.` | Four in total when a Pi system-prompt update trails the latest query (upstream keeps one per message). | [#10](https://github.com/earendil-works/pi-claude-code/issues/10), [#11](https://github.com/earendil-works/pi-claude-code/pull/11) |
> | One tool name over 50 characters, such as an MCP tool that `tool_search` loads, fails every later turn of the session.           | Tools with names that Claude Code rejects are left out; the other tools stay available.            | Not reported yet                                                                                                                   |
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
- `PI_CLAUDE_CODE_POWERSHELL`: PowerShell executable used to run a `.ps1`
  `PI_CLAUDE_CODE_COMMAND` (default: `pwsh` when installed, otherwise
  `powershell.exe`).

### Windows

npm installs Claude Code as `claude.cmd` (and a `claude.ps1` for PowerShell).
Both forms work as `PI_CLAUDE_CODE_COMMAND`:

- `.cmd` and `.bat` launchers run through `cmd.exe` with their arguments
  escaped once and passed verbatim, so installation paths with spaces and
  arguments containing quotes or `&` reach Claude Code unchanged.
- `.ps1` launchers run in a noninteractive PowerShell session with
  `-NoProfile` and `-ExecutionPolicy Bypass`. The extension prefers `pwsh`
  (PowerShell 7) because Windows PowerShell 5.1 cannot forward every quoted
  argument from a script to a native program.

### Model discovery and privacy

The extension asks Claude Code for the account's model catalog automatically.
The discovery probe allows Claude Code's normal feature-flag and catalog traffic,
including its usage telemetry, because disabling feature flags hides models such
as Mythos and previous-generation models. This is a
[known Claude Code issue](https://github.com/anthropics/claude-code/issues/105923).
The probe sends no conversation history or generation request. Automatic CLI
updates, official marketplace auto-install, feedback uploads, and error reporting
remain disabled.

To opt out of discovery telemetry, set `DISABLE_TELEMETRY=1` before starting Pi.
Discovery also preserves inherited `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`,
`DO_NOT_TRACK`, and `DISABLE_GROWTHBOOK` settings. These can reduce the discovered
catalog; the extension does not remove them to restore missing models. Claude
Code treats any non-empty `DISABLE_TELEMETRY` or
`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` value as enabled, including `0` or
`false`; unset them to allow normal discovery again. See
[Claude Code's environment variables](https://code.claude.com/docs/en/env-vars#features-that-need-feature-flag-fetching).

Conversation workers still disable telemetry and nonessential traffic regardless
of the discovery settings.

## Usage and billing

Requests made through this extension count against your Claude subscription's
usage quota and rate limits, the same as any other Claude Code usage. The
extension does not give you separate or unlimited usage.

The extension ignores `ANTHROPIC_API_KEY` in Claude Code child processes without
changing your environment. To avoid silently changing how you're authenticated
or billed, it still rejects auth-token, proxy, Bedrock, Vertex, or Foundry
overrides for Claude Code.

## Limitations

- The extension is experimental.
- Branching, editing earlier messages, or changing settings mid-conversation
  starts a fresh Claude Code process that replays the conversation. The first
  response after that can be slower and may use more quota.
- Complex tool schemas (nullable types, `oneOf`, `allOf`, `anyOf`) may be
  simplified before Claude sees them.
- On Windows, Windows PowerShell 5.1 mangles quoted arguments (such as the
  inline MCP configuration JSON) when a `.ps1` launcher forwards them to a
  native program. Install PowerShell 7 or use the `claude.cmd` launcher in that
  case.
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
