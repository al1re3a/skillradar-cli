from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

TOKEN = re.compile(r"[\w-]{2,}", re.UNICODE)


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    path: str
    headings: tuple[str, ...]
    tokens: tuple[str, ...]

    def to_dict(self, score: float | None = None):
        result = asdict(self)
        result.pop("tokens")
        if score is not None:
            result["score"] = round(score, 4)
        return result


def _tokens(text: str) -> tuple[str, ...]:
    return tuple(match.group(0).lower().replace("_", "-") for match in TOKEN.finditer(text))


def _frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    values: dict[str, str] = {}
    for line in parts[1].splitlines():
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            values[key.strip().lower()] = value.strip().strip("'\"")
    return values, parts[2]


def parse_skill(path: str | Path) -> Skill:
    source = Path(path)
    text = source.read_text(encoding="utf-8", errors="replace")
    meta, body = _frontmatter(text)
    headings = tuple(match.group(1).strip() for match in re.finditer(r"^#{1,3}\s+(.+)$", body, re.MULTILINE))
    name = meta.get("name") or (headings[0] if headings else source.parent.name)
    description = meta.get("description") or next((line.strip() for line in body.splitlines() if line.strip() and not line.startswith("#")), "No description")
    searchable = " ".join((name, description, " ".join(headings), source.parent.name))
    return Skill(name, description, str(source.resolve()), headings, _tokens(searchable))


def discover(roots: Iterable[str | Path]) -> list[Skill]:
    paths: set[Path] = set()
    for raw_root in roots:
        root = Path(raw_root).expanduser()
        if root.is_file() and root.name.lower() == "skill.md":
            paths.add(root.resolve())
        elif root.exists():
            paths.update(path.resolve() for path in root.rglob("SKILL.md") if ".git" not in path.parts)
    skills = []
    for path in sorted(paths):
        try:
            skills.append(parse_skill(path))
        except OSError:
            continue
    return skills


def search(skills: list[Skill], query: str, limit: int = 8) -> list[tuple[Skill, float]]:
    query_terms = _tokens(query)
    if not query_terms or not skills:
        return []
    document_frequency = Counter(term for term in set(query_terms) for skill in skills if term in skill.tokens)
    average_length = sum(len(skill.tokens) for skill in skills) / len(skills)
    results = []
    for skill in skills:
        frequencies = Counter(skill.tokens)
        score = 0.0
        for term in query_terms:
            frequency = frequencies[term]
            if not frequency:
                continue
            count = document_frequency[term]
            inverse = math.log(1 + (len(skills) - count + 0.5) / (count + 0.5))
            denominator = frequency + 1.5 * (1 - 0.75 + 0.75 * len(skill.tokens) / max(average_length, 1))
            score += inverse * frequency * 2.5 / denominator
            if term in _tokens(skill.name):
                score += 1.5
        if score > 0:
            results.append((skill, score))
    return sorted(results, key=lambda item: (-item[1], item[0].name.lower()))[: max(1, limit)]
