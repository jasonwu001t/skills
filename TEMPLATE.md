# Skill template

Copy this into a new folder to create a skill:

```
mkdir my-new-skill
# create my-new-skill/SKILL.md using the structure below
```

A skill is any top-level folder here that contains a `SKILL.md`. The folder
name and the `name:` in the frontmatter should match (lowercase, hyphens).

---

```markdown
---
name: my-new-skill
description: One or two sentences on WHAT this skill does and WHEN to use it. This text is what the model matches against to decide whether to load the skill, so be specific and include trigger phrases / example requests.
when_to_use: (optional, Claude Code) Short note on the situations that should trigger this skill, and what it is NOT for.
---

# Human-Readable Skill Title

One-line summary of what the skill produces.

## Workflow

1. Step one
2. Step two
3. Step three

## Notes / constraints

- Requirements, defaults, gotchas.
```

Supporting files (scripts, data) live alongside `SKILL.md` in the same folder
and are referenced from it by relative path.
