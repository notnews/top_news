## Top News! URLs from News Feeds of Major National News Sites (2022--)

We automatically pull daily news data from major national news sites: ABC,  CBS, CNN, LA Times, NBC, NPR, NYT, Politico, ProPublica, USA Today, and WaPo using [Github Workflows](https://github.com/notnews/top_news/tree/main/.github/workflows). For the latest version, refer to the respective JSON files.

### Other Scripts + Data

1. The script for [aggregating the URLs](https://github.com/notnews/top_news/blob/main/agg/concat_json.py) and [March-2025 dump of URLs (.zip)](https://github.com/notnews/top_news/blob/main/agg/agg_urls.json.zip)
   
2. The script for downloading the article text and parsing some features using [newspaper3k](https://newspaper.readthedocs.io/en/latest/), e.g., publication date, authors, etc. and putting it in a DB is [here](https://github.com/notnews/top_news/blob/main/agg/create_db.py). The script checks the local db before incrementally processing new data.
  * The June 2023 full-text dump is here: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/ZNAKK6
  * The March-2025 dump is being posted. CNN, LA Times, and NBC are up.

3. Newspaper3k can't parse USAT URLs. I use custom Google search to dig up the URLs and get the data. The script is [here](https://github.com/notnews/top_news/blob/main/agg/usat_downloader.py). 
