import json
import feedparser
from urllib.parse import urljoin, urlparse

# Load existing URLs from JSON file
with open("politico_urls.json", "r") as politico_file:
    politico_json = json.load(politico_file)

# List of RSS feeds
feeds = [
    "https://rss.politico.com/congress.xml",
    "https://rss.politico.com/healthcare.xml",
    "https://rss.politico.com/defense.xml",
    "https://rss.politico.com/economy.xml",
    "https://rss.politico.com/energy.xml",
    "https://rss.politico.com/politics-news.xml"
]

# Parse each feed and extract URLs
for url in feeds:
    try:
        # Parse the feed
        feed = feedparser.parse(url)
        
        # Check for parsing errors
        if feed.bozo:
            print(f"Warning: Failed to parse feed {url}")
            continue
        
        # Process each article in the feed
        for article in feed.entries:
            # Check if 'link' key exists
            if 'link' in article:
                raw_link = article['link']
                clean_url = urljoin(raw_link, urlparse(raw_link).path)
                
                # Add the URL to politico_json if it's not already present
                if clean_url not in politico_json:
                    politico_json.append(clean_url)
            else:
                print(f"Warning: Missing 'link' key in article from feed {url}")

    except Exception as e:
        print(f"Error processing feed {url}: {e}")

# Save updated URLs back to JSON file
with open("politico_urls.json", "w") as f:
    json.dump(politico_json, f, indent=4)

