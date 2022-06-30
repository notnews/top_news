import json
import feedparser
from urllib.parse import urljoin, urlparse

with open("lat_urls.json", "r") as lat_file:
    lat_json = json.load(lat_file)

feeds = ["https://www.latimes.com/business/rss2.0.xml", "https://www.latimes.com/california/rss2.0.xml", "https://www.latimes.com/environment/rss2.0.xml", "https://www.latimes.com/entertainment-arts/rss2.0.xml", "https://www.latimes.com/food/rss2.0.xml", "https://www.latimes.com/lifestyle/rss2.0.xml", "https://www.latimes.com/politics/rss2.0.xml", "https://www.latimes.com/science/rss2.0.xml", "https://www.latimes.com/sports/rss2.0.xml", "https://www.latimes.com/travel/rss2.0.xml", "https://www.latimes.com/world-nation/rss2.0.xml"]

for url in feeds:
    feed = feedparser.parse(url)
    for article in feed.entries:
        clean_url = urljoin(article['link'], urlparse(article['link']).path)
        if not clean_url in lat_json:
            lat_json.append(clean_url)

with open("lat_urls.json", "w") as f:
    f.write(json.dumps(lat_json))
