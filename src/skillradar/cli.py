from __future__ import annotations

import argparse
import json
from pathlib import Path

from .index import discover, search


def default_roots() -> list[Path]:
    home = Path.home()
    current = Path.cwd()
    return [current / ".agents" / "skills", current / ".codex" / "skills", current / ".cursor" / "skills", home / ".agents" / "skills", home / ".codex" / "skills"]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="skillradar", description="Find the right coding-agent skill locally")
    parser.add_argument("query", nargs="?", default="")
    parser.add_argument("--root", action="append", help="Skill root (repeatable)")
    parser.add_argument("--top", type=int, default=8)
    parser.add_argument("--format", choices=("text", "json", "markdown", "compact"), default="text")
    parser.add_argument("--list", action="store_true", help="List every discovered skill")
    args = parser.parse_args(argv)
    skills = discover(args.root or default_roots())
    ranked = [(skill, 0.0) for skill in skills] if args.list else search(skills, args.query, args.top)
    if args.format == "json":
        print(json.dumps({"query": args.query, "discovered": len(skills), "results": [skill.to_dict(score) for skill, score in ranked]}, indent=2))
    elif args.format == "markdown":
        print(f"## SkillRadar: {args.query or 'all skills'}\n")
        for skill, score in ranked:
            print(f"- **{skill.name}** ({score:.3f}) — {skill.description}  \n  `{skill.path}`")
    elif args.format == "compact":
        for skill, _ in ranked:
            print(skill.name)
    else:
        print(f"SkillRadar: {len(skills)} discovered, {len(ranked)} matches")
        for skill, score in ranked:
            print(f"{score:6.3f}  {skill.name}\n        {skill.description}\n        {skill.path}")
    return 0 if ranked or args.list else 1


if __name__ == "__main__":
    raise SystemExit(main())
