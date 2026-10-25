#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import uuid

REPO = Path(__file__).resolve().parents[4]


def doctor():
    env = dict(os.environ)
    if env.get("PI_CLAUDE_CODE_CONFIG_DIR"):
        env["CLAUDE_CONFIG_DIR"] = env["PI_CLAUDE_CODE_CONFIG_DIR"]
    claude = env.get("PI_CLAUDE_CODE_COMMAND", "claude")
    status = json.loads(subprocess.check_output([claude, "auth", "status"], env=env))
    result = {
        "repo": str(REPO),
        "revision": subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip(),
        "source_sha256": hashlib.sha256((REPO / "src/claude-cli.ts").read_bytes()).hexdigest(),
        "pi": subprocess.check_output(["pi", "--version"], text=True).strip(),
        "claude": subprocess.check_output([claude, "--version"], env=env, text=True).strip(),
        "loggedIn": status.get("loggedIn"),
        "authMethod": status.get("authMethod"),
        "subscriptionType": status.get("subscriptionType"),
    }
    assert result["loggedIn"] and result["authMethod"] == "claude.ai", "Claude subscription login required"
    return result


def run_pi(args, work, env, evidence, name):
    command = [
        "pi", "--mode", "json", "--offline", "--no-approve", "--no-extensions",
        "-e", str(REPO / "src/index.ts"), "--no-mcp", "--no-skills",
        "--no-prompt-templates", "--no-themes", "--no-context-files",
        "--provider", "claude-code", "--model", args.model, "--thinking", "off",
        "--system-prompt", "Follow the user's exact instructions. Use tools when requested.",
        "--tools", "read,write", "--session-dir", str(work / "sessions"),
        "--session-id", "verification", args.prompt,
    ]
    (evidence / f"{name}.command.json").write_text(json.dumps(command, indent=2) + "\n")
    with (evidence / f"{name}.events.jsonl").open("w") as stdout, (evidence / f"{name}.stderr.txt").open("w") as stderr:
        process = subprocess.Popen(command, cwd=work, env=env, stdin=subprocess.DEVNULL,
                                   stdout=stdout, stderr=stderr, start_new_session=True)
        try:
            code = process.wait(timeout=240)
        except BaseException:
            parents = [tuple(map(int, row.split())) for row in subprocess.check_output(
                ["ps", "-axo", "pid=,ppid="], text=True).splitlines()]
            owned = {process.pid}
            while True:
                children = {pid for pid, parent in parents if parent in owned} - owned
                if not children:
                    break
                owned.update(children)
            process.send_signal(signal.SIGINT)
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            for pid in owned - {process.pid}:
                try:
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            raise
    (evidence / f"{name}.exit.txt").write_text(f"{code}\n")
    records = [json.loads(line) for line in (evidence / f"{name}.events.jsonl").read_text().split("\n") if line.strip()]
    assert code == 0, f"Pi exited {code}; inspect {name}.stderr.txt"
    messages = [r["message"] for r in records if r.get("type") == "message_end" and r["message"].get("role") == "assistant"]
    assert messages, "No completed assistant response"
    assert all(m["provider"] == "claude-code" and m["model"] == args.model for m in messages), "Wrong provider/model"
    assert all(m["stopReason"] not in ("error", "aborted", "pending") for m in messages), "Assistant failed; inspect events"
    assert messages[-1]["stopReason"] == "stop", "No final response after tool use"
    assert any(r.get("type") == "agent_settled" and not r.get("aborted") for r in records), "Run did not settle"
    return records, messages


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("feature", choices=["doctor", "text", "tools", "resume"])
    parser.add_argument("--model", default="claude-fable-5-1")
    args = parser.parse_args()
    if args.feature == "doctor":
        print(json.dumps(doctor(), indent=2))
        return
    # Evidence outlives the scratch directory; PI_CLAUDE_CODE_EVIDENCE_DIR moves it to a lasting place.
    evidence_root = Path(os.environ.get("PI_CLAUDE_CODE_EVIDENCE_DIR") or Path(tempfile.gettempdir()) / "pi-claude-code-evidence")
    evidence_root.mkdir(parents=True, exist_ok=True)
    evidence = Path(tempfile.mkdtemp(prefix=f"{args.feature}-", dir=evidence_root))
    print(f"Evidence: {evidence}", flush=True)
    summary = {"feature": args.feature, "model": args.model, "passed": False}
    work = Path(tempfile.mkdtemp(prefix="verify-pi-claude-code-"))
    try:
        (evidence / "doctor.json").write_text(json.dumps(doctor(), indent=2) + "\n")
        agent = work / "agent"
        agent.mkdir()
        (agent / "settings.json").write_text(json.dumps({"retry": {"enabled": False}, "compaction": {"enabled": False}}))
        env = {**os.environ, "PI_CODING_AGENT_DIR": str(agent), "PI_TELEMETRY": "0"}
        token = uuid.uuid4().hex
        if args.feature == "tools":
            (work / "input.txt").write_text(token + "\n")
            args.prompt = "Use read to read input.txt. Then use write to create output.txt with exactly the same contents, including the newline. Then reply with only VERIFIED."
        elif args.feature == "resume":
            args.prompt = f"Remember this token for my next message: {token}. Reply with only READY."
        else:
            args.prompt = f"Reply with only this token: {token}"
        records, messages = run_pi(args, work, env, evidence, "first")
        if args.feature == "resume":
            args.prompt = "What token did I ask you to remember? Reply with only the token."
            records, messages = run_pi(args, work, env, evidence, "resumed")
        final = "".join(b["text"] for b in messages[-1]["content"] if b["type"] == "text").strip()
        if args.feature == "tools":
            starts = [r for r in records if r.get("type") == "tool_execution_start"]
            ends = [r for r in records if r.get("type") == "tool_execution_end"]
            assert [r["toolName"] for r in starts] == ["read", "write"], "Expected read then write through Pi"
            assert len(ends) == 2 and all(not r.get("isError") for r in ends), "Tools did not complete successfully"
            assert len(messages) >= 3, "Expected model follow-ups after both tool results"
            expected = (token + "\n").encode()
            actual = (work / "output.txt").read_bytes()
            (evidence / "input.txt").write_bytes(expected)
            (evidence / "output.txt").write_bytes(actual)
            assert actual == expected, "Output file differs from input"
            assert final == "VERIFIED", f"Unexpected final response: {final!r}"
        else:
            assert final == token, f"Unexpected final response: {final!r}"
        summary["passed"] = True
    except BaseException as error:
        summary["error"] = str(error)
        raise
    finally:
        shutil.rmtree(work)
        summary["scratch_removed"] = not work.exists()
        (evidence / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        assert (evidence / "summary.json").is_file(), "Cleanup removed evidence"
        print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
