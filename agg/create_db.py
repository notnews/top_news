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

def create_db(source, batch_size=100):
    current_batch = []
    db_file = f"{source.lower()}.db"
    table_name = f"{source.lower()}_stories"
    urls_file = f"{source.lower()}_urls.json"
    
    logger.info(f"Starting extraction for {source} with batch size {batch_size}")
    logger.info(f"Database: {db_file}")
    logger.info(f"URL source: {urls_file}")
    
    # Create database
    try:
        db = Database(db_file)
        logger.info(f"Successfully connected to database {db_file}")
        
        # Create table if it doesn't exist
        if table_name not in db.table_names():
            logger.info(f"Creating new table: {table_name}")
            db[table_name].create({
                "url": str,
                "source": str,
                "publish_date": str,
                "title": str,
                "authors": str,
                "text": str,
                "extraction_date": str,
                "domain": str
            }, pk="url")
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
    
    # Get existing URLs from database
    existing_urls = set()
    try:
        for row in db[table_name].rows:
            existing_urls.add(row["url"])
        logger.info(f"Found {len(existing_urls)} existing URLs in database")
    except Exception as e:
        logger.error(f"Failed to retrieve existing URLs from database: {e}")
        existing_urls = set()  # Reset to empty set if there was an error
    
    # Filter out URLs that are already in the database
    new_urls = [url for url in urls if url not in existing_urls]
    logger.info(f"Found {len(new_urls)} new URLs to process")
    
    # Stats tracking
    total_urls = len(new_urls)
    successful = 0
    skipped = 0
    errors = 0
    
    if total_urls == 0:
        logger.info("No new URLs to process. Exiting.")
        return
    
    # Process each URL
    for index, url in enumerate(new_urls):
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
        row['authors'] = json.dumps(article.authors)  # Store authors as JSON string
        row['text'] = article.text
        row['extraction_date'] = datetime.now().isoformat()
        
        # Domain for additional categorization
        domain = urlparse(url).netloc
        row['domain'] = domain
        
        # Log article details for debugging
        logger.debug(f"Article details: Title: {article.title}, Date: {article.publish_date}, Authors: {article.authors}")
        logger.debug(f"Text length: {len(article.text)} characters")
        
        # Add to current batch
        current_batch.append(row)
        successful += 1
        
        # If batch is full, insert into database
        if len(current_batch) >= batch_size:
            _insert_batch(db, table_name, current_batch)
            logger.info(f"Inserted batch of {len(current_batch)} articles ({successful} of {total_urls} processed)")
            current_batch = []  # Reset batch
        
        # Rate limiting
        time.sleep(0.1)
    
    # Insert any remaining articles
    if current_batch:
        _insert_batch(db, table_name, current_batch)
        logger.info(f"Inserted final batch of {len(current_batch)} articles")
    
    # Log final statistics
    logger.info(f"Processing complete for {source}")
    logger.info(f"Total new URLs: {total_urls}")
    logger.info(f"Successfully processed: {successful}")
    logger.info(f"Skipped: {skipped}")
    logger.info(f"Errors: {errors}")

def _insert_batch(db, table_name, batch):
    """Helper function to insert a batch of articles into the database"""
    try:
        db[table_name].insert_all(batch, pk="url")
        return True
    except Exception as e:
        logger.error(f"Failed to insert batch into database: {e}")
        # If batch insert fails, try inserting one by one
        logger.info("Attempting to insert articles individually")
        successful = 0
        for row in batch:
            try:
                db[table_name].insert(row, pk="url", replace=True)
                successful += 1
            except Exception as article_e:
                logger.error(f"Failed to insert article {row['url']}: {article_e}")
        
        logger.info(f"Individual insertion: {successful}/{len(batch)} articles inserted")
        return successful > 0

def get_db_schema(source):
    """Function to print the database schema"""
    db_file = f"{source.lower()}.db"
    table_name = f"{source.lower()}_stories"
    
    try:
        db = Database(db_file)
        if table_name in db.table_names():
            schema = db[table_name].schema
            print(f"\nSchema for {table_name}:")
            print(json.dumps(schema, indent=2))
            
            # Count records
            count = db[table_name].count
            print(f"\nTotal records: {count}")
            
            # Show sample data (first row)
            try:
                first_row = next(db[table_name].rows)
                print("\nSample record (first row):")
                for key, value in first_row.items():
                    if key == 'text':
                        # Truncate text to avoid excessive output
                        print(f"  {key}: {value[:100]}...")
                    else:
                        print(f"  {key}: {value}")
            except StopIteration:
                print("No records found in the database.")
        else:
            print(f"Table {table_name} does not exist in the database.")
    except Exception as e:
        print(f"Error accessing database: {e}")

def main():
    if len(sys.argv) < 2:
        logger.error("Usage: python create_db.py SOURCE_NAME [--schema]")
        sys.exit(1)
    
    source = sys.argv[1]
    
    # Check if we should just print the schema
    if len(sys.argv) > 2 and sys.argv[2] == "--schema":
        get_db_schema(source)
        return
    
    logger.info(f"Starting extraction for source: {source}")
    
    try:
        create_db(source)
    except Exception as e:
        logger.error(f"Unhandled exception in create_db: {e}", exc_info=True)
    
    logger.info("Script execution complete")

if __name__ == "__main__":
    main()