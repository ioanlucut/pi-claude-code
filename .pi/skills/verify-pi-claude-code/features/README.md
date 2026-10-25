# pi-claude-code verification map

Start with `../SKILL.md` for launch, doctor, and evidence rules.
Use `VERIFY` from its launch block. Each journey gets a new isolated Pi session;
`resume` reopens only the session created by that same journey.
A subscription login is required. Failed or unavailable model requests remain
failures, not successful skips.

| Feature | Automated entry | Other user entry |
|---|---|---|
| [Subscription response](response.md) | `verify.py text` | Interactive provider/model picker |
| [Tool round trip](tools.md) | `verify.py tools` | Interactive prompts using Pi tools |
| [Saved-session replay](resume.md) | `verify.py resume` | Pi `--continue` and `--resume` |

For each proof, retain the action command, resulting events, exit code, and
`summary.json`. File mutations require an independent file read.
The automated journey verifies only the listed JSON CLI entry. Interactive
picker/status commands, alternate session selectors, images, abort, billing
rejections, and cross-provider switching need separate evidence.
