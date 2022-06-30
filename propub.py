import json
import feedparser
from urllib.parse import urljoin, urlparse

with open("propub_urls.json", "r") as propub_file:
    propub_json = json.load(propub_file)

feeds = ["http://feeds.propublica.org/propublica/main"]

for url in feeds:
    feed = feedparser.parse(url)
    for article in feed.entries:
        clean_url = urljoin(article['link'], urlparse(article['link']).path)
        if not clean_url in propub_json:
            propub_json.append(clean_url)

with open("propub_urls.json", "w") as f:
    f.write(json.dumps(propub_json))
