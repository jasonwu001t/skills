#!/usr/bin/env bash
# github-sync: commit & push the repos listed in config.json to GitHub.
# Usage: sync.sh ["optional commit message"]
# Safe by design: only add -> commit -> push. Never force-pushes, pulls,
# rebases, merges, or creates branches. Bash 3.2 compatible.
set -o pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG="${GITHUB_SYNC_CONFIG:-$SKILL_DIR/config.json}"
MSG_OVERRIDE="$*"

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 is required to parse $CONFIG" >&2
  exit 1
fi
if [ ! -f "$CONFIG" ]; then
  echo "ERROR: no config at $CONFIG" >&2
  echo "Create it:  cp \"$SKILL_DIR/config.example.json\" \"$CONFIG\"  then edit it." >&2
  exit 1
fi

# One TSV row per repo: name <tab> path <tab> remote <tab> branch <tab> prefix
RAW="$(python3 - "$CONFIG" <<'PY'
import json, os, sys
try:
    cfg = json.load(open(sys.argv[1]))
except Exception as e:
    sys.exit("ERROR: cannot parse config: %s" % e)
repos = cfg.get("repos", [])
if not repos:
    sys.exit("ERROR: config has no 'repos' entries")
for r in repos:
    p = os.path.expanduser(os.path.expandvars(r["path"]))
    print("\t".join([r.get("name", os.path.basename(p)), p,
                      r.get("remote", "origin"), r.get("branch", ""),
                      r.get("commit_prefix", "Sync")]))
PY
)"
if [ $? -ne 0 ]; then
  echo "$RAW" >&2
  exit 1
fi

overall=0
synced=0
while IFS=$'\t' read -r name path remote branch prefix; do
  [ -z "$name" ] && continue
  echo "=== $name ($path) ==="
  if [ ! -d "$path/.git" ]; then
    echo "  SKIP: not a git repository"
    overall=1
    continue
  fi
  [ -z "$branch" ] && branch="$(git -C "$path" rev-parse --abbrev-ref HEAD 2>/dev/null)"

  git -C "$path" add -A
  changes="$(git -C "$path" status --porcelain)"
  committed=0
  if [ -n "$changes" ]; then
    nfiles="$(printf '%s\n' "$changes" | wc -l | tr -d ' ')"
    if [ -n "$MSG_OVERRIDE" ]; then
      msg="$MSG_OVERRIDE"
    else
      msg="$prefix: $nfiles file(s) updated ($(date '+%Y-%m-%d %H:%M'))"
    fi
    if git -C "$path" commit -q -m "$msg"; then
      echo "  committed: $msg"
      committed=1
    else
      echo "  ERROR: commit failed"
      overall=1
      continue
    fi
  fi

  ahead="$(git -C "$path" rev-list --count '@{u}..HEAD' 2>/dev/null || echo '?')"
  if [ "$committed" -eq 0 ] && [ "$ahead" = "0" ]; then
    echo "  up to date — nothing to back up"
    continue
  fi

  if git -C "$path" push -u "$remote" "$branch" 2>&1 | sed 's/^/  /'; then
    echo "  pushed -> $remote/$branch"
    synced=$((synced + 1))
  else
    echo "  ERROR: push failed. Resolve manually, e.g.:"
    echo "         git -C \"$path\" pull --rebase $remote $branch"
    overall=1
  fi
done <<< "$RAW"

echo "---"
if [ "$overall" -eq 0 ]; then
  echo "Done. $synced repo(s) pushed."
else
  echo "Done with errors. $synced repo(s) pushed; see messages above."
fi
exit $overall
