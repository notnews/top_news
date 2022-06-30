import json
import feedparser

with open("npr_urls.json", "r") as npr_file:
    npr_json = json.load(npr_file)

feed = feedparser.parse("https://feeds.npr.org/1001/rss.xml")

for article in feed.entries:
    if not article['link'] in npr_json:
        npr_json.append(article['link'])

with open("npr_urls.json", "w") as f:
    f.write(json.dumps(npr_json))
