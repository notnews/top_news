## Top News! URLs from News Feeds of Major National News Sites (2022-)

We automatically pull daily news data from major national news sites: ABC,  CBS, CNN, LA Times, NBC, NPR, NYT, Politico, ProPublica, USA Today, and WaPo using [Github Workflows](https://github.com/notnews/top_news/tree/main/.github/workflows). For the latest version, please take a look at the respective JSON files.

As of March 2025, we have about 700k unique URLs.

### Other Scripts + Data

1. The script for [aggregating the URLs](https://github.com/notnews/top_news/blob/main/agg/concat_json.py) and [March-2025 dump of URLs (.zip)](https://github.com/notnews/top_news/blob/main/agg/agg_urls.json.zip)
   
2. The script for downloading the article text and parsing some features using [newspaper3k](https://newspaper.readthedocs.io/en/latest/), e.g., publication date, authors, etc. and putting it in a DB is [here](https://github.com/notnews/top_news/blob/main/agg/create_db.py). The script checks the local DB before incrementally processing new data.
  * The June 2023 full-text dump is here: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/ZNAKK6
  * The March 2025 dump (minus the exceptions listed below) is in the same place.

3. Newspaper3k can't parse USAT, Politico, and ABC URLs. I use custom Google search to dig up the URLs and get the data. The script is [here](https://github.com/notnews/top_news/blob/main/agg/usat_downloader.py). 

### Get Started With Exploring the Data

To explore the DB, some code ([Jupyter NB](https://github.com/notnews/top_news/blob/main/agg/tester.ipynb)) ...

```python

from sqlite_utils import Database
from itertools import islice

db = Database("../cbs.db")
print("Tables:", db.table_names())
```

```
Tables: ['../cbs_stories']
```

#### Table Schema

```python
schema = db[table_name].schema
print("Schema:\n")
print(schema)
```

```
Schema:

CREATE TABLE [../cbs_stories] (
   [url] TEXT PRIMARY KEY,
   [source] TEXT,
   [publish_date] TEXT,
   [title] TEXT,
   [authors] TEXT,
   [text] TEXT,
   [extraction_date] TEXT,
   [domain] TEXT
)
```

```python
db_file = "../cbs.db"
table_name = "../cbs_stories" # yup! it has the ../

db = Database(db_file)

for row in islice(db[table_name].rows, 5):
    print(f"URL: {row['url']}")
    print(f"Title: {row['title']}")
    print(f"Date: {row['publish_date']}")
    print(f"Text preview: {row['text'][:100]}...\n")
```

#### Exporting to Pandas

```python

# Option 1: Convert all data to a DataFrame
df = pd.DataFrame(list(db[table_name].rows))

# Option 2: If the table is very large, you might want to limit rows
# df = pd.DataFrame(list(islice(db[table_name].rows, 1000)))  # first 1000 rows

# Print info about the DataFrame
print(f"DataFrame shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
print(df.head())
```
