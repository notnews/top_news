import json
import feedparser
from urllib.parse import urljoin, urlparse

with open("usat_urls.json", "r") as usat_file:
    usat_json = json.load(usat_file)

feeds = [
    "http://rssfeeds.usatoday.com/usatoday-NewsTopStories",
    "http://rssfeeds.usatoday.com/UsatodaycomNation-TopStories",
    "http://rssfeeds.usatoday.com/UsatodaycomWashington-TopStories",
    "http://rssfeeds.usatoday.com/UsatodaycomWorld-TopStories",
    "http://rssfeeds.usatoday.com/usatoday-LifeTopStories",
    "http://rssfeeds.usatoday.com/usatoday-TechTopStories"
    ]

for url in feeds:
    feed = feedparser.parse(url)
    for article in feed.entries:
        clean_url = urljoin(article['link'], urlparse(article['link']).path)
        if not clean_url in usat_json:
            usat_json.append(clean_url)

with open("usat_urls.json", "w") as f:
    f.write(json.dumps(usat_json))
