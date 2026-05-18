# WSJ News Scraper Agent Skill

An agent skill for continuously monitoring and collecting top articles from The Wall Street Journal.

## Files

- `SKILL.md` - Agent skill definition with workflow instructions
- `process_articles.py` - Python script for data processing and storage
- `wsj_articles.json` - Data file (created automatically on first run)

## Features

- **Deduplication**: Automatically prevents duplicate articles
- **Timestamping**: Tracks when articles first appeared and last seen
- **Incremental updates**: Designed for repeated runs throughout the day
- **Scrape tracking**: Counts how many times each article appeared

## Data Schema

```json
{
  "last_updated": "ISO 8601 timestamp",
  "articles": [
    {
      "id": "unique-hash",
      "title": "Article Title",
      "url": "https://wsj.com/article-url",
      "first_seen": "ISO 8601 timestamp",
      "last_seen": "ISO 8601 timestamp",
      "scrape_count": 3
    }
  ]
}
```

## Usage with Agent

The agent will:
1. Use browser tools to navigate to wsj.com
2. Extract article titles and URLs from the page
3. Call the Python script to process and store the data

Example agent command:
```
"Go to wsj.com and collect the top 10 articles"
```

## Manual Testing

Test the script directly:

```bash
python process_articles.py --articles '[
  {"title": "Test Article 1", "url": "https://wsj.com/test1"},
  {"title": "Test Article 2", "url": "https://wsj.com/test2"}
]'
```

## Scheduling

For continuous monitoring, set up a cron job or scheduled task:

```bash
# Run every 2 hours
0 */2 * * * cd ~/wsj-news-scraper && /path/to/agent "scrape wsj news"
```

## Requirements

- Python 3.6+
- Browser automation tools (for agent)
- No external Python dependencies (uses stdlib only)
