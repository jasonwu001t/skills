# WSJ News Scraper — skill

Captures the top articles from The Wall Street Journal homepage into a
deduplicated, timestamped JSON dataset, suitable for repeated runs that build a
history of what WSJ featured over time.

## Files

- `SKILL.md` — skill definition (workflow + when it triggers)
- `scripts/process_articles.py` — stdlib-only processor: dedup, timestamps, storage
- `wsj_articles.json` — dataset, created next to this skill on first run (gitignored)

## Behavior

- **Deduplication** by article URL (won't add the same story twice)
- **Timestamping** — `first_seen` / `last_seen` per article
- **Incremental** — re-running updates existing entries and adds new ones
- **Scrape tracking** — `scrape_count` = times the article reappeared

## Manual test

```bash
python3 ~/.claude/skills/wsj-news/scripts/process_articles.py --articles '[
  {"title": "Test Article 1", "url": "https://www.wsj.com/test1"},
  {"title": "Test Article 2", "url": "https://www.wsj.com/test2"}
]'
```

Writes/updates `~/.claude/skills/wsj-news/wsj_articles.json` regardless of the
directory you run it from.

## Requirements

- Python 3.6+ (standard library only — nothing to install)
- Any browser-automation capability available in the host (used to load wsj.com)

## Scheduling

For continuous monitoring, drive the skill on a recurring basis from your agent
of choice (e.g. Claude Code's `/schedule` or `/loop`, or an OS cron job that
invokes the agent). The dataset accumulates across runs.
