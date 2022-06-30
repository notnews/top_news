import json
import feedparser
from urllib.parse import urljoin, urlparse

with open("politico_urls.json", "r") as politico_file:
    politico_json = json.load(politico_file)

feeds = [
    "https://rss.politico.com/congress.xml",
    "https://rss.politico.com/healthcare.xml",
    "https://rss.politico.com/defense.xml",
    "https://rss.politico.com/economy.xml",
    "https://rss.politico.com/energy.xml",
    "https://rss.politico.com/politics-news.xml"
    ]

for url in feeds:
    feed = feedparser.parse(url)
    for article in feed.entries:
        clean_url = urljoin(article['link'], urlparse(article['link']).path)
        if not clean_url in politico_json:
            politico_json.append(clean_url)

with open("politico_urls.json", "w") as f:
    f.write(json.dumps(politico_json))
