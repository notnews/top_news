import json
import feedparser
from urllib.parse import urljoin, urlparse

with open("wapo_urls.json", "r") as wapo_file:
    wapo_json = json.load(wapo_file)

feeds = ["https://feeds.washingtonpost.com/rss/politics", "https://feeds.washingtonpost.com/rss/national", "https://feeds.washingtonpost.com/rss/world", "https://feeds.washingtonpost.com/rss/business", "https://feeds.washingtonpost.com/rss/business/technology", "https://feeds.washingtonpost.com/rss/sports", "https://feeds.washingtonpost.com/rss/lifestyle", "https://feeds.washingtonpost.com/rss/entertainment"]

for url in feeds:
    feed = feedparser.parse(url)
    for article in feed.entries:
        clean_url = urljoin(article['link'], urlparse(article['link']).path)
        if not clean_url in wapo_json:
            wapo_json.append(clean_url)

with open("wapo_urls.json", "w") as f:
    f.write(json.dumps(wapo_json))
