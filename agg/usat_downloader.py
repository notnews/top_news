import pandas as pd
import newspaper
import re
import time
import requests
import json
import os
from datetime import datetime
from urllib.parse import quote, urlparse
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("article_search.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ArticleFinder:
    def __init__(self, api_key, search_engine_id, output_dir="downloaded_articles"):
        """
        Initialize the ArticleFinder with required credentials and settings
        
        Args:
            api_key: Google API key
            search_engine_id: Google Custom Search Engine ID
            output_dir: Directory to save HTML files
        """
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"HTML files will be saved to {output_dir}")
        
        # Track API usage to avoid exceeding limits
        self.search_count = 0
        self.results = []
    
    def extract_slug(self, url):
        """Extract the article slug from RSS feed URLs"""
        # Try multiple patterns to extract slugs from different URL formats

        # Pattern for specific sections (newstopstories, techtopstories, etc.)
        match = re.search(r'usatoday-(\w+)~(.*?)(?:/|$)', url)
        if match:
            slug = match.group(2)
            search_term = slug.replace('-', ' ')
            return slug, search_term

        # Pattern for nation-topstories format
        match = re.search(r'usatodaycom(\w+)-topstories~(.*?)(?:/|$)', url)
        if match:
            slug = match.group(2)
            search_term = slug.replace('-', ' ')
            return slug, search_term

        # Last resort: Extract the last segment of the URL path
        parts = url.rstrip('/').split('/')
        if parts and len(parts) > 0:
            last_segment = parts[-1]
            # Check if it looks like a slug (contains dashes)
            if '-' in last_segment and not last_segment.startswith('~'):
                search_term = last_segment.replace('-', ' ')
                return last_segment, search_term

        return None, None
    
    def search_for_article(self, search_term, site="usatoday.com"):
        """
        Search for an article using Google's Custom Search API
        
        Args:
            search_term: The term to search for
            site: The site to restrict search to
            
        Returns:
            The URL of the first search result, or None if no results
        """
        # Properly format the search query with site restriction
        query = f"site:{site} {search_term}"
        logger.info(f"Searching for: {query}")
        
        # Track API usage (Google CSE has limits)
        self.search_count += 1
        if self.search_count % 10 == 0:
            logger.info(f"Search API count: {self.search_count}")
        
        # Custom Search API URL
        search_url = "https://www.googleapis.com/customsearch/v1"
        
        # Parameters for the API request
        params = {
            "key": self.api_key,
            "cx": self.search_engine_id,
            "q": query,
            "num": 5  # Request 5 results
        }
        
        try:
            # Make the API request with proper error handling
            response = requests.get(search_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if we have search items
                if "items" in data and len(data["items"]) > 0:
                    # Get the first result URL
                    result_url = data["items"][0]["link"]
                    result_title = data["items"][0]["title"]
                    logger.info(f"Found article: {result_title} at {result_url}")
                    return result_url, result_title
                else:
                    logger.warning(f"No search results found for '{query}'")
                    if "searchInformation" in data:
                        logger.info(f"Total results: {data['searchInformation'].get('totalResults', 0)}")
            else:
                # Detailed error logging
                logger.error(f"Search API error: {response.status_code}")
                logger.error(f"Error details: {response.text}")
                
                # Handle specific error codes
                if response.status_code == 403:
                    logger.error("Error 403: API quota exceeded or invalid credentials")
                elif response.status_code == 429:
                    logger.warning("Error 429: Rate limit exceeded, waiting before retry")
                    time.sleep(10)  # Wait longer for rate limit
                    
        except Exception as e:
            logger.error(f"Search API exception: {str(e)}")
        
        return None, None
    
    def download_and_parse_article(self, url):
        """
        Download and parse an article using newspaper3k
        
        Args:
            url: URL of the article to download
            
        Returns:
            Dictionary with article data and success status
        """
        logger.info(f"Downloading article from: {url}")
        
        try:
            article = newspaper.Article(url)
            article.download()
            
            # Save the HTML content
            html_content = article.html
            
            # Create a filename based on the URL
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.replace(".", "_")
            path = parsed_url.path.strip("/").replace("/", "_")
            if not path:
                path = "index"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{domain}_{path}_{timestamp}.html"
            filepath = os.path.join(self.output_dir, filename)
            
            # Save the HTML
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            # Parse the article
            article.parse()
            
            return {
                "url": url,
                "title": article.title,
                "text": article.text[:500] + "..." if len(article.text) > 500 else article.text,
                "publish_date": str(article.publish_date),
                "authors": article.authors,
                "html_saved_path": filepath,
                "html_size": len(html_content),
                "text_size": len(article.text),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error downloading/parsing {url}: {str(e)}")
            return {
                "url": url,
                "error": str(e),
                "success": False
            }
    
    def process_rss_urls(self, urls, max_urls=None, results_file="article_results.jsonl"):
        """
        Process a list of RSS feed URLs to find and download the actual articles

        Args:
            urls: List of RSS feed URLs
            max_urls: Maximum number of URLs to process (None for all)
            results_file: JSONL file to save results to incrementally

        Returns:
            Pandas DataFrame with article data
        """
        self.results = []
        total_urls = len(urls)

        if max_urls:
            urls = urls[:max_urls]
            logger.info(f"Processing {len(urls)} of {total_urls} URLs")
        else:
            logger.info(f"Processing all {total_urls} URLs")

        # Create or truncate the JSONL file at the start
        with open(results_file, 'w') as f:
            f.write('')  # Just create/truncate the file

        for i, url in enumerate(urls):
            logger.info(f"Processing {i+1}/{len(urls)}: {url}")

            # Extract the slug
            slug, search_term = self.extract_slug(url)
            if not slug:
                logger.warning(f"Could not extract slug from URL: {url}")

                # Create failed entry
                result = {
                    "original_rss_url": url,
                    "slug": None,
                    "search_term": None,
                    "found_url": None,
                    "found_title": None,
                    "success": False,
                    "error": "Could not extract slug",
                    "timestamp": datetime.now().isoformat()
                }

                # Append to JSONL file
                self._append_to_jsonl(result, results_file)

                # Also keep in memory
                self.results.append(result)
                continue

            logger.info(f"Extracted slug: {slug}")
            logger.info(f"Search term: {search_term}")

            # Search for the article - just one simple search approach
            found_url, found_title = self.search_for_article(search_term)

            if not found_url:
                logger.warning(f"No article found for slug: {slug}")
                
                # Create failed entry
                result = {
                    "original_rss_url": url,
                    "slug": slug,
                    "search_term": search_term,
                    "found_url": None,
                    "found_title": None,
                    "success": False,
                    "error": "No article found",
                    "timestamp": datetime.now().isoformat()
                }
                
                # Append to JSONL file
                self._append_to_jsonl(result, results_file)
                
                # Also keep in memory
                self.results.append(result)
                continue

            # Download and parse the article
            article_data = self.download_and_parse_article(found_url)

            # Add original URL info and search results
            result = {
                "original_rss_url": url,
                "slug": slug,
                "search_term": search_term,
                "found_url": found_url,
                "found_title": found_title,
                "timestamp": datetime.now().isoformat()
            }
            result.update(article_data)

            # Append to JSONL file
            self._append_to_jsonl(result, results_file)

            # Also keep in memory
            self.results.append(result)

            # Be nice to servers
            time.sleep(2)

        # Create DataFrame from final results
        df = pd.DataFrame(self.results)

        # Save final results as CSV as well
        self.save_results("article_results.csv", df)

        return df

    def _append_to_jsonl(self, result, jsonl_file):
        """
        Append a single result to a JSONL file

        Args:
            result: Result dictionary to append
            jsonl_file: Path to JSONL file
        """
        # Create a copy of the result to avoid modifying the original
        result_copy = result.copy()

        # If the result contains HTML content, truncate it to save space
        if "html_content" in result_copy:
            result_copy["html_content"] = f"[HTML content truncated, {len(result_copy['html_content'])} bytes]"

        # If the result contains article text, truncate it if it's too long
        if "text" in result_copy and len(result_copy["text"]) > 1000:
            result_copy["text"] = result_copy["text"][:1000] + "..."

        # Append to the JSONL file
        with open(jsonl_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(result_copy) + '\n')

        logger.debug(f"Appended result for {result_copy.get('slug', 'unknown')} to {jsonl_file}")
    
    def save_results(self, filename="article_results.csv", df=None):
        """
        Save results to a CSV file using append mode

        Args:
            filename: Name of the CSV file
            df: DataFrame to save (uses self.results if None)

        Returns:
            The DataFrame that was saved
        """
        if df is None:
            df = pd.DataFrame(self.results)

        # Check if file exists to determine if header should be written
        file_exists = os.path.isfile(filename)

        # Append to file if it exists, create new file if it doesn't
        df.to_csv(filename, mode='a', header=not file_exists, index=False)

        logger.info(f"Results {'appended to' if file_exists else 'saved to'} {filename}")

        return df

# Example usage
if __name__ == "__main__":
    API_KEY = ""
    SEARCH_ENGINE_ID = ""

    with open('usat_urls.json', 'r', encoding='utf-8') as f:
        urls = json.load(f)[501:9000]
        
    finder = ArticleFinder(API_KEY, SEARCH_ENGINE_ID)
        
    df = finder.process_rss_urls(urls)
        
    print("\nResults Summary:")
    print(f"Total URLs processed: {len(df)}")
    print(f"Successfully retrieved: {df['success'].sum()}")
    print(f"Failed: {len(df) - df['success'].sum()}")
        
    # Show the DataFrame
    print("\nDataFrame Preview:")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(df[['slug', 'found_title', 'found_url', 'success', 'html_saved_path']].head())