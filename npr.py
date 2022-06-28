import json
import newspaper

npr_data = []

npr_stories = newspaper.build("https://www.npr.org/")

for article in npr_stories.articles[1:-1]:
    article.download()
    article.parse()
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
    npr_data.append(data)

with open("npr_stories.json", "w") as f:
    f.write(json.dumps(npr_data))
