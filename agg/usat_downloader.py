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
        # Extract everything after the last tilde (~/) and before the last slash
        parts = url.rstrip('/').split('~/')
        
        if len(parts) >= 2:
            # The last part should be the slug
            slug = parts[-1]
            search_term = slug.replace('-', ' ')
            return slug, search_term
        
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
            
            # Log full response for debugging
            logger.debug(f"API Response: {response.text[:1000]}")
            
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
                if response.status_code == 400:
                    logger.error("Error 400: Request contains an invalid argument")
                    
                    # Check if the API key is included correctly
                    if self.api_key and len(self.api_key) > 5:
                        masked_key = self.api_key[:3] + "..." + self.api_key[-3:]
                        logger.info(f"API key in use: {masked_key}")
                    else:
                        logger.error("API key appears to be missing or invalid")
                        
                elif response.status_code == 403:
                    logger.error("Error 403: API quota exceeded or invalid credentials")
                elif response.status_code == 429:
                    logger.warning("Error 429: Rate limit exceeded, waiting before retry")
                    time.sleep(10)  # Wait longer for rate limit
                    
            # If we get rate limited, wait before continuing
            if response.status_code == 429:
                logger.warning("Rate limit hit. Waiting 10 seconds...")
                time.sleep(10)
                
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
    
    def process_rss_urls(self, urls, max_urls=None):
        """
        Process a list of RSS feed URLs to find and download the actual articles
        
        Args:
            urls: List of RSS feed URLs
            max_urls: Maximum number of URLs to process (None for all)
            
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
        
        for i, url in enumerate(urls):
            logger.info(f"Processing {i+1}/{len(urls)}: {url}")
            
            # Extract the slug
            slug, search_term = self.extract_slug(url)
            if not slug:
                logger.warning(f"Could not extract slug from URL: {url}")
                
                # Add failed entry
                self.results.append({
                    "original_rss_url": url,
                    "slug": None,
                    "search_term": None,
                    "found_url": None,
                    "found_title": None,
                    "success": False,
                    "error": "Could not extract slug"
                })
                continue
            
            logger.info(f"Extracted slug: {slug}")
            logger.info(f"Search term: {search_term}")
            
            # Search for the article - try multiple variations if needed
            found_url, found_title = self.search_for_article(search_term)
            
            # If first search failed, try with the slug directly
            if not found_url:
                logger.info(f"First search attempt failed, trying with the slug directly")
                found_url, found_title = self.search_for_article(slug)
            
            # If still failed, try with a more specific query
            if not found_url:
                logger.info(f"Second search attempt failed, trying with more specific query")
                specific_query = f"usatoday {search_term}"
                found_url, found_title = self.search_for_article(specific_query, site="")
            
            if not found_url:
                logger.warning(f"No article found for slug: {slug}")
                
                # Add failed entry
                self.results.append({
                    "original_rss_url": url,
                    "slug": slug,
                    "search_term": search_term,
                    "found_url": None,
                    "found_title": None,
                    "success": False,
                    "error": "No article found"
                })
                continue
            
            # Download and parse the article
            article_data = self.download_and_parse_article(found_url)
            
            # Add original URL info and search results
            result = {
                "original_rss_url": url,
                "slug": slug,
                "search_term": search_term,
                "found_url": found_url,
                "found_title": found_title
            }
            result.update(article_data)
            
            self.results.append(result)
            
            # Save progress after each article
            self.save_progress(f"progress_{i+1}_of_{len(urls)}.json")
            
            # Be nice to servers
            time.sleep(2)
        
        # Create DataFrame
        df = pd.DataFrame(self.results)
        
        # Save final results
        self.save_results("article_results.csv", df)
        self.save_progress("article_results.json")
        
        return df
    
    def save_progress(self, filename="progress.json"):
        """Save current progress to a JSON file"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"Progress saved to {filename}")
    
    def save_results(self, filename="article_results.csv", df=None):
        """Save results to a CSV file"""
        if df is None:
            df = pd.DataFrame(self.results)
        
        df.to_csv(filename, index=False)
        logger.info(f"Results saved to {filename}")
        
        return df

# Test the API credentials function
def test_api_credentials(api_key, search_engine_id):
    """
    Test if the API credentials are working
    
    Args:
        api_key: Google API key
        search_engine_id: Google Custom Search Engine ID
        
    Returns:
        True if credentials work, False otherwise
    """
    logger.info("Testing API credentials...")
    
    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": search_engine_id,
        "q": "test" 
    }
    
    try:
        response = requests.get(search_url, params=params)
        logger.info(f"Test API response status: {response.status_code}")
        
        if response.status_code == 200:
            logger.info("API credentials are working!")
            return True
        else:
            logger.error(f"API test failed with status {response.status_code}")
            logger.error(f"Error details: {response.text}")
            return False
    except Exception as e:
        logger.error(f"API test exception: {str(e)}")
        return False

# Example usage
if __name__ == "__main__":
    # Your API credentials
    API_KEY = ""
    SEARCH_ENGINE_ID = ""
    
    # Test the API credentials first
    if test_api_credentials(API_KEY, SEARCH_ENGINE_ID):
        # List of URLs (example)
        urls = [
            "http://rssfeeds.usatoday.com/~/701109914/0/usatoday-newstopstories~/Judge-Ketanji-Brown-Jackson-makes-history-as-Supreme-Courts-first-Black-woman-justice/", 
            "http://rssfeeds.usatoday.com/~/701136156/0/usatoday-newstopstories~/Biden-backs-change-to-filibuster-rules-to-codify-abortion-and-privacy-rights-into-law/",
            "http://rssfeeds.usatoday.com/~/701137228/0/usatoday-newstopstories~/Abortions-may-resume-in-Kentucky-after-judge-grants-temporary-suspension-of-trigger-law/"
        ]
        
        # Initialize the article finder
        finder = ArticleFinder(API_KEY, SEARCH_ENGINE_ID)
        
        # Process the URLs
        df = finder.process_rss_urls(urls)
        
        # Display results summary
        print("\nResults Summary:")
        print(f"Total URLs processed: {len(df)}")
        print(f"Successfully retrieved: {df['success'].sum()}")
        print(f"Failed: {len(df) - df['success'].sum()}")
        
        # Show the DataFrame
        print("\nDataFrame Preview:")
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        print(df[['slug', 'found_title', 'found_url', 'success', 'html_saved_path']].head())
    else:
        logger.error("API credentials test failed. Please check your API key and search engine ID.")