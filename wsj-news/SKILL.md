---
name: wsj-news
description: Scrape the current top headlines/articles from the Wall Street Journal homepage (wsj.com) and store them in a deduplicated, timestamped JSON dataset that tracks when each article first and last appeared and how often it resurfaced. Use whenever the user wants to collect, scrape, snapshot, track, or monitor WSJ news, headlines, top stories, or front-page articles — including recurring checks throughout the day (e.g. "grab the top WSJ stories right now", "snapshot the WSJ front page", "what is the WSJ leading with", "keep a running log of WSJ headlines every couple of hours"). Make sure to use this skill even when the user doesn't say the word "scrape" — any request to capture or watch WSJ's top stories over time should trigger it.
when_to_use: User wants the WSJ homepage's current top articles captured into, or monitored over time in, a JSON dataset. Triggers on collect/scrape/snapshot/track/monitor WSJ headlines or top stories. NOT for other news outlets, extracting full paywalled article body text, or a one-off read of a single already-known URL.
---

# WSJ News Scraper

Collects the top articles from The Wall Street Journal homepage into a
structured, deduplicated JSON dataset. Designed to be run repeatedly — each run
adds genuinely new articles and updates `last_seen` / `scrape_count` on ones
already captured, so the file becomes a history of what WSJ featured over time.

## Workflow

1. **Open wsj.com.** Use whatever browser-automation capability the current
   environment provides — a built-in browser/computer-use tool, Chrome driven
   via `osascript`, an MCP browser server, etc. This skill deliberately does not
   hard-code a tool: it just needs the homepage loaded and its rendered DOM/HTML
   readable. (Tool names differ between hosts; capability is what matters.)
2. **Extract the top ~10 articles.** From the homepage DOM, collect each
   article's **title** and **absolute URL**. If the page yields relative links,
   prefix them with `https://www.wsj.com`. Do not scrape article bodies — only
   the headline + link from the front page (timestamps are added by the script).
3. **Store the data** by passing the articles to the processor script (below).
4. **Verify** the summary the script prints (new vs. updated vs. total).

## Storing the data

Run the processor, passing a JSON array of `{title, url}` objects:

```bash
python3 ~/.claude/skills/wsj-news/scripts/process_articles.py --articles '[
  {"title": "Headline one", "url": "https://www.wsj.com/..."},
  {"title": "Headline two", "url": "https://www.wsj.com/..."}
]'
```

The script writes/updates `~/.claude/skills/wsj-news/wsj_articles.json` — a
fixed location next to the skill, independent of your current directory. It
dedupes by URL, sets `first_seen`/`last_seen`, increments `scrape_count`, sorts
by most-recently-seen, and prints a summary. It uses **only the Python standard
library** — there is nothing to `pip install`.

## Data schema (output)

```json
{
  "last_updated": "2026-03-08T08:00:00",
  "articles": [
    {
      "id": "unique-hash",
      "title": "Article Title",
      "url": "https://www.wsj.com/article-url",
      "first_seen": "2026-03-08T08:00:00",
      "last_seen": "2026-03-08T12:00:00",
      "scrape_count": 3
    }
  ]
}
```

## Recurring monitoring

Re-running accumulates history rather than overwriting: a returning headline
keeps its `first_seen` and gets a bumped `scrape_count` and fresh `last_seen`,
so you can later see which stories WSJ kept on the front page longest.

## Example

**Input:** "Snapshot the WSJ front page and add it to my tracker."
**Output:** Chrome opened to wsj.com, top ~10 headlines + URLs extracted, script
run; it reports e.g. `New: 4 · Updated: 6 · Total: 38` and updates
`wsj_articles.json`.

## Notes / troubleshooting

- Pure stdlib; no dependencies. If the script errors, the usual causes are: the
  `--articles` value isn't valid JSON, an article is missing `title` or `url`
  (those are skipped with a warning), or `wsj_articles.json` isn't writable.
- Keep URLs absolute so dedup-by-URL stays consistent across runs.
