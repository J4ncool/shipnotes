"""Generate release notes from Conventional Commits in a Git repository."""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

COMMIT_RE = re.compile(r"^(?P<type>[a-zA-Z][a-zA-Z0-9_-]*)(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?: (?P<subject>.+)$")
SECTIONS = {
    "feat": "Features",
    "fix": "Fixes",
    "perf": "Performance",
    "docs": "Documentation",
    "refactor": "Refactoring",
    "build": "Build",
    "ci": "CI",
    "test": "Tests",
    "chore": "Maintenance",
}


@dataclass
class Commit:
    subject: str
    body: str
    hash: str


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True)
    if result.returncode:
        message = result.stderr.strip() or "Git command failed"
        raise RuntimeError(message)
    return result.stdout.strip()


def collect(repo: Path, since: str | None, until: str | None) -> list[Commit]:
    revision = f"{since}..{until}" if since and until else (f"{since}..HEAD" if since else (until or "HEAD"))
    raw = git(repo, "log", revision, "--no-merges", "--format=%H%x1f%s%x1f%b%x1e")
    commits = []
    for item in raw.split("\x1e"):
        fields = item.strip().split("\x1f", 2)
        if len(fields) == 3 and fields[1]:
            commits.append(Commit(fields[1], fields[2].strip(), fields[0][:8]))
    return commits


def render(commits: list[Commit], title: str) -> str:
    groups: dict[str, list[str]] = {name: [] for name in SECTIONS.values()}
    other: list[str] = []
    breaking: list[str] = []
    for commit in reversed(commits):
        match = COMMIT_RE.match(commit.subject)
        if not match:
            other.append(f"- {commit.subject} (`{commit.hash}`)")
            continue
        kind = match.group("type").lower()
        scope = f"**{match.group('scope')}:** " if match.group("scope") else ""
        line = f"- {scope}{match.group('subject')} (`{commit.hash}`)"
        section = SECTIONS.get(kind)
        if section:
            groups[section].append(line)
        elif kind != "revert":
            other.append(line)
        if match.group("breaking") or re.search(r"^BREAKING CHANGE:", commit.body, re.MULTILINE):
            breaking.append(line)

    lines = [f"# {title}", ""]
    if breaking:
        lines += ["## Breaking changes", "", *breaking, ""]
    for section, entries in groups.items():
        if entries:
            lines += [f"## {section}", "", *entries, ""]
    if other:
        lines += ["## Other changes", "", *other, ""]
    if not commits:
        lines += ["No commits found in this range.", ""]
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create Markdown release notes from Git history.")
    parser.add_argument("repo", nargs="?", default=".", help="Git repository path (default: current directory)")
    parser.add_argument("--since", help="Starting tag or commit (exclusive)")
    parser.add_argument("--until", help="Ending tag or commit (default: HEAD)")
    parser.add_argument("--title", help="Release heading (default: based on --until or Unreleased)")
    parser.add_argument("-o", "--output", help="Write to a file instead of standard output")
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    try:
        commits = collect(repo, args.since, args.until)
        title = args.title or (args.until if args.until else "Unreleased")
        result = render(commits, title)
        if args.output:
            Path(args.output).write_text(result, encoding="utf-8")
        else:
            sys.stdout.write(result)
    except (RuntimeError, OSError) as exc:
        print(f"shipnotes: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
