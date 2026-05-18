---
name: github-sync
description: Commit and push one or more local Git repositories to their GitHub remotes. Use whenever the user wants to back up, sync, save, or push their work to GitHub — triggered by phrases like "github sync", "back up", "back up skills", "sync to github", "push to github", "save to my repo". Which repositories to sync is read from a separate config.json (not hardcoded), so the skill is generic and shareable.
when_to_use: User asks to back up / sync / push local work to GitHub (e.g. "back up", "github sync", "sync to github", "back up my skills"). Reads target repos from config.json. Not for cloning, pulling, branching, force-pushing, or resolving merge conflicts.
---

# GitHub Sync

Commits and pushes the repositories listed in `config.json` to their GitHub
remotes. The repo list is **config-driven** so this skill stays generic — no
repo paths are hardcoded in the skill itself.

## Setup (first run / new user)

1. Copy the example config and edit it:
   ```bash
   cp ~/.claude/skills/github-sync/config.example.json ~/.claude/skills/github-sync/config.json
   ```
2. Set the repo(s) to sync in `config.json`. `config.json` is gitignored, so
   each user keeps their own private list; the skill ships only with
   `config.example.json`.

## What to do when invoked

1. Run the sync script:
   ```bash
   bash ~/.claude/skills/github-sync/scripts/sync.sh ["optional commit message"]
   ```
   - If the user supplied a commit message (e.g. *"back up: finished the wsj
     skill"*), pass that message as a single quoted argument.
   - Otherwise run with no arguments — the script generates a default message
     with a file count and timestamp.
2. Read the script's per-repo output and report it back concisely: for each
   repo say whether it was **pushed** (with the commit message), **already up
   to date**, or **failed** (with the reason).
3. If the script reports a push failure (e.g. the remote is ahead), surface
   the suggested manual fix — do **not** auto-pull, rebase, merge, or
   force-push. This skill only ever does `add` → `commit` → `push`.

## Example

**Input:** "back up: finished the wsj-news fixes"
**Action:** `bash ~/.claude/skills/github-sync/scripts/sync.sh "back up: finished the wsj-news fixes"`
**Output (reported back to the user):**
```
skills — pushed to origin/main
  commit: back up: finished the wsj-news fixes
Done. 1 repo(s) pushed.
```
If nothing changed, report it plainly instead: `skills — already up to date, nothing to back up.`

## Notes / constraints

- Never force-push, create branches, or modify repos not listed in
  `config.json`.
- If `config.json` is missing, tell the user to create it from
  `config.example.json` and stop.
- Requires `python3` (used only to parse the JSON config).
- "Already up to date" is a success, not an error — report it plainly.
