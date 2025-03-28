import json
import time
import sys
from sqlite_utils import Database
from newspaper import Article

def create_db(source):
    rows = []
    db_file = f"{source.lower()}.db"
    table_name = f"{source.lower()}_stories"
    db = Database(db_file)
    urls_file = f"{source.lower()}_urls.json"

    try:
        with open(urls_file, "r", encoding="utf-8") as f:
            urls = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load URL list from {urls_file}: {e}")
        return

    for url in urls:
        if (
            '/video/' in url
            or url == 'https://www.comparecards.com/'
            or '/live-news/january-6-hearings' in url
            or 'cnn-underscored' in url
            or (source == 'CNN' and 'cnn.com' not in url)
        ):
            continue

        print(f"📥 {url}")
        row = {}
        article = Article(url)
        article.download()
        try:
            article.parse()
        except Exception:
            print(f"⚠️ Skipped (parse error): {url}")
            continue

        row['source'] = source
        row['url'] = url
        row['publish_date'] = str(article.publish_date)
        row['title'] = article.title
        row['authors'] = article.authors
        row['text'] = article.text
        rows.append(row)
        time.sleep(0.1)

    db[table_name].insert_all(rows, pk="url")
    print(f"✅ Stored {len(rows)} articles in {db_file} [{table_name}]")

def main():
    if len(sys.argv) < 2:
        print("Usage: python create_db.py SOURCE_NAME")
        sys.exit(1)

    source = sys.argv[1]
    create_db(source)

if __name__ == "__main__":
    main()
