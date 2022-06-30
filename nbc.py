import json
import feedparser
from urllib.parse import urljoin, urlparse

with open("nbc_urls.json", "r") as nbc_file:
    nbc_json = json.load(nbc_file)

feeds = [
    "http://feeds.nbcnews.com/nbcnews/public/news",
    "http://feeds.nbcnews.com/nbcnews/public/world",
    "http://feeds.nbcnews.com/nbcnews/public/politics",
    "http://feeds.nbcnews.com/nbcnews/public/health",
    ]

for url in feeds:
    feed = feedparser.parse(url)
    for article in feed.entries:
        clean_url = urljoin(article['link'], urlparse(article['link']).path)
        if not clean_url in nbc_json:
            nbc_json.append(clean_url)

with open("nbc_urls.json", "w") as f:
    f.write(json.dumps(nbc_json))
