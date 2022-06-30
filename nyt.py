import json
import feedparser

with open("nyt_urls.json", "r") as nyt_file:
    nyt_json = json.load(nyt_file)

feeds = ["https://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/section/politics/rss.xml", "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml", "https://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/section/us/rss.xml", "https://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/section/world/rss.xml", "https://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/section/business/rss.xml", "https://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/section/technology/rss.xml"]

for url in feeds:
    feed = feedparser.parse(url)
    for article in feed.entries:
        if not article['link'] in nyt_json:
            nyt_json.append(article['link'])

with open("nyt_urls.json", "w") as f:
    f.write(json.dumps(nyt_json))
