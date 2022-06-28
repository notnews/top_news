import json
import newspaper

nyt_data = []

nyt_stories = newspaper.build("https://www.nytimes.com/")

for article in nyt_stories.articles[1:-1]:
    article.download()
    article.parse()
    # skip Chinese versions
    if 'cn.nytimes.com' in article.url:
        continue
    data = {}
    if article.publish_date:
        data['year'] = article.publish_date.year
        data['month'] = article.publish_date.month
        data['date'] = article.publish_date.day
    data['url'] = article.url
    data['headline'] = article.title
    data['byline'] = article.authors
    data['subhead'] = article.meta_data['description']
    data['text'] = article.text
    nyt_data.append(data)

with open("nyt_stories.json", "w") as f:
    f.write(json.dumps(nyt_data))
