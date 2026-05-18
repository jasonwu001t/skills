#!/usr/bin/env python3
"""
WSJ Article Processor
Handles deduplication, timestamping, and storage of WSJ articles.
"""

import json
import hashlib
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict

DATA_FILE = Path("wsj_articles.json")


def generate_article_id(url: str) -> str:
    """Generate unique ID from article URL."""
    return hashlib.md5(url.encode()).hexdigest()[:12]


def load_existing_data() -> Dict:
    """Load existing article data or create new structure."""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"last_updated": None, "articles": []}


def save_data(data: Dict) -> None:
    """Save article data to JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✓ Saved to {DATA_FILE}")


def process_articles(new_articles: List[Dict]) -> None:
    """
    Process new articles: add new ones, update existing ones.
    
    Args:
        new_articles: List of dicts with 'title' and 'url' keys
    """
    data = load_existing_data()
    now = datetime.now().isoformat()
    
    # Create lookup dict for existing articles
    existing = {article['id']: article for article in data['articles']}
    
    added = 0
    updated = 0
    
    for article in new_articles:
        if not article.get('url') or not article.get('title'):
            print(f"⚠ Skipping invalid article: {article}")
            continue
            
        article_id = generate_article_id(article['url'])
        
        if article_id in existing:
            # Update existing article
            existing[article_id]['last_seen'] = now
            existing[article_id]['scrape_count'] += 1
            updated += 1
        else:
            # Add new article
            existing[article_id] = {
                'id': article_id,
                'title': article['title'],
                'url': article['url'],
                'first_seen': now,
                'last_seen': now,
                'scrape_count': 1
            }
            added += 1
    
    # Update data structure
    data['articles'] = list(existing.values())
    data['last_updated'] = now
    
    # Sort by last_seen (most recent first)
    data['articles'].sort(key=lambda x: x['last_seen'], reverse=True)
    
    save_data(data)
    
    print(f"\n📊 Summary:")
    print(f"  • New articles: {added}")
    print(f"  • Updated articles: {updated}")
    print(f"  • Total articles: {len(data['articles'])}")


def main():
    parser = argparse.ArgumentParser(description='Process WSJ articles')
    parser.add_argument('--articles', type=str, required=True,
                       help='JSON string of articles with title and url')
    
    args = parser.parse_args()
    
    try:
        articles = json.loads(args.articles)
        if not isinstance(articles, list):
            raise ValueError("Articles must be a list")
        process_articles(articles)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)


if __name__ == '__main__':
    main()
