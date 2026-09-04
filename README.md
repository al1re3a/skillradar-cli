# SkillRadar

[![CI](https://github.com/al1re3a/skillradar-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/al1re3a/skillradar-cli/actions/workflows/ci.yml) [![MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Find the right agent skill without stuffing every description into context.**

SkillRadar discovers local `SKILL.md` files and ranks them with a small BM25 search index. It is fast, private, dependency-free, and compatible with skills stored for Codex, Claude Code, Cursor, or a custom agent.

```bash
skillradar "validate a PDF form"
```

## Why

Skill libraries are growing faster than context windows should. Injecting every skill description into every turn wastes tokens and still makes selection harder. SkillRadar retrieves a focused top-k list when it is needed.

## Usage

```bash
python -m pip install -e .

# Search common user and project skill directories
skillradar "analyze spreadsheet formulas"

# Search explicit libraries
skillradar "inspect PDF layout" --root ~/.agents/skills --root ./team-skills

# Agent-friendly output
skillradar "deploy site" --format json --top 5
skillradar "deploy site" --format compact

# Inventory
skillradar --list --root examples/skills
```

## Ranking

The index uses BM25 over names, descriptions, headings, and folder names, with an exact-name boost. No embedding model, API key, database, or background daemon is required. Results are recomputed from files, so they never go stale.

## Token-saving pattern

1. Keep only skill names in the base agent prompt.
2. Search SkillRadar using the current user request.
3. Inject descriptions for the top three to eight candidates.
4. Let the agent read only the selected `SKILL.md` files.

## Development

```bash
python -m unittest discover -s tests -v
```

## License

MIT
