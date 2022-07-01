import json
import feedparser
from urllib.parse import urljoin, urlparse

with open("abc_urls.json", "r") as abc_file:
    abc_json = json.load(abc_file)

feeds = [
    "https://abcnews.go.com/abcnews/topstories",
    "https://abcnews.go.com/abcnews/internationalheadlines",
    "https://abcnews.go.com/abcnews/usheadlines",
    "https://abcnews.go.com/abcnews/moneyheadlines",
    "https://abcnews.go.com/abcnews/healthheadlines",
    "https://abcnews.go.com/abcnews/sportsheadlines",
    "https://abcnews.go.com/abcnews/entertainmentheadlines",
    "https://abcnews.go.com/abcnews/technologyheadlines",
    "https://abcnews.go.com/abcnews/travelheadlines"
    ]

for url in feeds:
    feed = feedparser.parse(url)
    for article in feed.entries:
        clean_url = urljoin(article['link'], urlparse(article['link']).path)
        if not clean_url in abc_json:
            abc_json.append(clean_url)

with open("abc_urls.json", "w") as f:
    f.write(json.dumps(abc_json))
