# skills

Central store of my personal [Agent Skills](https://github.com/anthropics/skills),
shared by **Claude Code** and **Kiro CLI**, version-controlled and synced to
[github.com/jasonwu001t/skills](https://github.com/jasonwu001t/skills).

## How it's wired

This repository **is** `~/.claude/skills` — the directory Claude Code loads
personal skills from. Kiro CLI loads skills from `~/.kiro/skills`, which is a
symlink to this same directory:

```
~/.claude/skills        <- this git repo (source of truth)
~/.kiro/skills  ->  ~/.claude/skills   (symlink)
```

So every skill here is automatically available in **both** tools. There is no
copy or sync step between tools — they read the same files.

## Layout

Flat: every top-level folder containing a `SKILL.md` is a skill.

```
.
├── README.md
├── TEMPLATE.md            # starter for new skills (not a skill itself)
├── .gitignore
├── va-reward-search/
│   ├── SKILL.md
│   └── scripts/
└── wsj-news/
    ├── SKILL.md
    ├── README.md
    └── process_articles.py
```

> Note: skills are kept at the top level (not nested under a `skills/`
> subfolder like `anthropics/skills`) because Claude Code discovers personal
> skills at `~/.claude/skills/<name>/SKILL.md`. Nesting them would hide them
> from the tools.

## Add a new skill

```bash
cd ~/.claude/skills
mkdir my-new-skill
$EDITOR my-new-skill/SKILL.md      # see TEMPLATE.md for the structure
```

It becomes available in Claude Code and Kiro on the next session — no install
step.

## Sync to GitHub

Skills are live as soon as the files exist locally. Backing them up / sharing
is a normal Git push:

```bash
cd ~/.claude/skills
git add -A
git commit -m "Update skills"
git push
```
