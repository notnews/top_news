import json
import feedparser
from urllib.parse import urljoin, urlparse

with open("cbs_urls.json", "r") as cbs_file:
    cbs_json = json.load(cbs_file)

feeds = [
    "https://www.cbsnews.com/latest/rss/main",
    "https://www.cbsnews.com/latest/rss/us",
    "https://www.cbsnews.com/latest/rss/politics",
    "https://www.cbsnews.com/latest/rss/world",
    "https://www.cbsnews.com/latest/rss/health",
    "https://www.cbsnews.com/latest/rss/moneywatch",
    "https://www.cbsnews.com/latest/rss/science",
    "https://www.cbsnews.com/latest/rss/technology",
    "https://www.cbsnews.com/latest/rss/entertainment",
    "https://www.cbsnews.com/latest/rss/evening-news/cbs-news-investigates",
    "https://www.cbsnews.com/latest/rss/60-minutes",
    "https://www.cbsnews.com/latest/rss/evening-news",
    "https://www.cbsnews.com/latest/rss/face-the-nation"
    ]

for url in feeds:
    feed = feedparser.parse(url)
    for article in feed.entries:
        clean_url = urljoin(article['link'], urlparse(article['link']).path)
        if not clean_url in cbs_json:
            cbs_json.append(clean_url)

with open("cbs_urls.json", "w") as f:
    f.write(json.dumps(cbs_json))
