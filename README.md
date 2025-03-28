## Top News! URLs from News Feeds of Major National News Sites (2022--)

We automatically pull daily news data from major national news sites: ABC,  CBS, CNN, LA Times, NBC, NPR, NYT, Politico, ProPublica, USA Today, and WaPo using [Github Workflows](https://github.com/notnews/top_news/tree/main/.github/workflows). For the latest version, refer to the respective JSON files.

### Other Scripts + Data

1. The script for [aggregating the URLs](https://github.com/notnews/top_news/blob/main/agg/concat_json.py) and [March-2025 dump of URLs (.zip](https://github.com/notnews/top_news/blob/main/agg/agg_urls.json.zip)
2. The script for downloading the article text and parsing some features, e.g., publication date, authors, etc. and putting it in a DB is [here](https://github.com/notnews/top_news/blob/main/agg/create_db.py). The June 2023 full-text dump is here: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/ZNAKK6
We will be putting up the March-2025 version shortly.
