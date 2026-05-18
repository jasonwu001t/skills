---
name: scraping-wsj-news
description: Scrapes top articles from wsj.com and stores them in JSON format. Use when the user asks to collect, scrape, or monitor WSJ news articles, headlines, or top stories.
---

# WSJ News Scraper

Collects top articles from The Wall Street Journal homepage and stores them in a structured JSON format.

## Workflow

1. **Open browser and navigate**: Use browser tools to go to wsj.com
2. **Extract articles**: Read the page DOM to find article titles and links
3. **Process data**: Run the Python script to store articles
4. **Verify**: Check that data was saved correctly

## Step 1: Navigate to WSJ

Use browser:launch_chrome to open Chrome, then browser:navigate to go to https://wsj.com

## Step 2: Extract article data

Use browser:read_dom to get page content. Look for article elements in the DOM. Extract:
- Article title
- Article URL
- Timestamp (current time when scraped)

Collect the top 10 articles from the homepage.

## Step 3: Store data

Run the processing script:

```bash
python process_articles.py --articles '[article_data_json]'
```

The script handles:
- Deduplication (won't add duplicate URLs)
- Timestamping (adds scrape time)
- Data validation
- Incremental updates throughout the day

## Data schema

Articles are stored in `wsj_articles.json`:

```json
{
  "last_updated": "2026-03-08T08:00:00",
  "articles": [
    {
      "id": "unique-hash",
      "title": "Article Title",
      "url": "https://wsj.com/article-url",
      "first_seen": "2026-03-08T08:00:00",
      "last_seen": "2026-03-08T12:00:00",
      "scrape_count": 3
    }
  ]
}
```

## Repeatable process

This skill is designed for continuous monitoring:
- Run multiple times per day
- New articles are added automatically
- Existing articles update their `last_seen` timestamp
- `scrape_count` tracks how many times an article appeared

## Error handling

If the script fails:
1. Check that article data is valid JSON
2. Verify the data file is writable
3. Ensure Python dependencies are installed: `pip install hashlib json datetime`
