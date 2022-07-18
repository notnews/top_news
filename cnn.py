import json
import feedparser
from urllib.parse import urljoin, urlparse

with open("cnn_urls.json", "r") as abc_file:
    cnn_json = json.load(abc_file)

feeds = [
    "http://rss.cnn.com/rss/cnn_topstories.rss",
    "http://rss.cnn.com/rss/cnn_world.rss",
    "http://rss.cnn.com/rss/cnn_us.rss",
    "http://rss.cnn.com/rss/cnn_allpolitics.rss",
    "http://rss.cnn.com/rss/cnn_tech.rss",
    "http://rss.cnn.com/rss/cnn_health.rss",
    "http://rss.cnn.com/rss/cnn_showbiz.rss",
    "http://rss.cnn.com/rss/cnn_travel.rss"
    ]

for url in feeds:
    feed = feedparser.parse(url)
    for article in feed.entries:
        clean_url = urljoin(article['link'], urlparse(article['link']).path)
        if not clean_url in cnn_json:
            cnn_json.append(clean_url)

with open("cnn_urls.json", "w") as f:
    f.write(json.dumps(cnn_json))
