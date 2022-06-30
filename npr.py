import json
import feedparser

with open("npr_urls.json", "r") as npr_file:
    npr_json = json.load(npr_file)

feeds = ["https://feeds.npr.org/1014/rss.xml", "https://feeds.npr.org/1001/rss.xml", "https://feeds.npr.org/1003/rss.xml", "https://feeds.npr.org/1004/rss.xml", "https://feeds.npr.org/1006/rss.xml", "https://feeds.npr.org/1007/rss.xml", "https://feeds.npr.org/1008/rss.xml", "https://feeds.npr.org/1009/rss.xml", "https://feeds.npr.org/1015/rss.xml", "https://feeds.npr.org/1016/rss.xml", "https://feeds.npr.org/1017/rss.xml"]

for url in feeds:
    feed = feedparser.parse(url)
    for article in feed.entries:
        if not article['link'] in npr_json:
            npr_json.append(article['link'])

with open("npr_urls.json", "w") as f:
    f.write(json.dumps(npr_json))
