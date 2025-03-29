import json
import time
import sys
import os
import logging
from datetime import datetime
from urllib.parse import urlparse
from newspaper import Article
from sqlite_utils import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"article_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_db(source):
    rows = []
    db_file = f"{source.lower()}.db"
    table_name = f"{source.lower()}_stories"
    urls_file = f"{source.lower()}_urls.json"
    
    logger.info(f"Starting extraction for {source}")
    logger.info(f"Database: {db_file}")
    logger.info(f"URL source: {urls_file}")
    
    # Create database
    try:
        db = Database(db_file)
        logger.info(f"Successfully connected to database {db_file}")
    except Exception as e:
        logger.error(f"Failed to create/connect to database {db_file}: {e}")
        return
    
    # Load URLs
    try:
        with open(urls_file, "r", encoding="utf-8") as f:
            urls = json.load(f)
        logger.info(f"Loaded {len(urls)} URLs from {urls_file}")
    except Exception as e:
        logger.error(f"Failed to load URL list from {urls_file}: {e}")
        return
    
    # Stats tracking
    total_urls = len(urls)
    successful = 0
    skipped = 0
    errors = 0
    
    # Process each URL
    for index, url in enumerate(urls):
        logger.info(f"Processing URL {index+1}/{total_urls}: {url}")
        
        # Filter out unwanted URLs
        if (
            '/video/' in url
            or url == 'https://www.comparecards.com/'
            or '/live-news/january-6-hearings' in url
            or 'cnn-underscored' in url
            or (source == 'CNN' and 'cnn.com' not in url)
        ):
            logger.info(f"Skipped (filtered): {url}")
            skipped += 1
            continue
        
        # Extract article
        row = {}
        article = Article(url)
        
        try:
            article.download()
            logger.debug(f"Downloaded: {url}")
        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            errors += 1
            continue
        
        try:
            article.parse()
            logger.debug(f"Parsed: {url}")
        except Exception as e:
            logger.error(f"Failed to parse {url}: {e}")
            errors += 1
            continue
        
        # Store article data
        row['source'] = source
        row['url'] = url
        row['publish_date'] = str(article.publish_date)
        row['title'] = article.title
        row['authors'] = article.authors
        row['text'] = article.text
        row['extraction_date'] = datetime.now().isoformat()
        
        # Domain for additional categorization
        domain = urlparse(url).netloc
        row['domain'] = domain
        
        # Log article details for debugging
        logger.debug(f"Article details: Title: {article.title}, Date: {article.publish_date}, Authors: {article.authors}")
        logger.debug(f"Text length: {len(article.text)} characters")
        
        # Add to results
        rows.append(row)
        successful += 1
        
        # Rate limiting
        time.sleep(0.1)
    
    # Save to database
    if rows:
        try:
            db[table_name].insert_all(rows, pk="url")
            logger.info(f"Successfully stored {len(rows)} articles in {db_file} [{table_name}]")
        except Exception as e:
            logger.error(f"Failed to insert articles into database: {e}")
    
    # Log final statistics
    logger.info(f"Processing complete for {source}")
    logger.info(f"Total URLs: {total_urls}")
    logger.info(f"Successfully processed: {successful}")
    logger.info(f"Skipped: {skipped}")
    logger.info(f"Errors: {errors}")

def main():
    if len(sys.argv) < 2:
        logger.error("Usage: python create_db.py SOURCE_NAME")
        sys.exit(1)
    
    source = sys.argv[1]
    logger.info(f"Starting extraction for source: {source}")
    
    try:
        create_db(source)
    except Exception as e:
        logger.error(f"Unhandled exception in create_db: {e}", exc_info=True)
    
    logger.info("Script execution complete")

if __name__ == "__main__":
    main()