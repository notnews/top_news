import json
import feedparser
from urllib.parse import urljoin, urlparse

with open("abc_urls.json", "r") as abc_file:
    abc_json = json.load(abc_file)

feeds = [
    "https://abcnews.go.com/abcnews/topstories"
    ]

for url in feeds:
    feed = feedparser.parse(url)
    for article in feed.entries:
        clean_url = urljoin(article['link'], urlparse(article['link']).path)
        if not clean_url in abc_json:
            abc_json.append(clean_url)

with open("abc_urls.json", "w") as f:
    f.write(json.dumps(abc_json))
