import sys
import json
from scraper.cnn_scraper import CNNScraper
from scraper.reuters_scraper import ReutersScraper
from scraper.bbc_scraper import BBCScraper
from utils.export import export_to_json

SCRAPER_MAP = {
    'cnn.com': CNNScraper(),
    'reuters.com': ReutersScraper(),
    'bbc.com': BBCScraper(),
}

def get_scraper(url):
    for domain, scraper in SCRAPER_MAP.items():
        if domain in url:
            return scraper
    raise ValueError(f"No scraper available for URL: {url}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <urls.json>")
        sys.exit(1)
    with open(sys.argv[1], 'r') as f:
        urls = json.load(f)
    results = []
    for url in urls:
        try:
            scraper = get_scraper(url)
            data = scraper.scrape(url)
            results.append(data)
        except Exception as e:
            print(f"Error scraping {url}: {e}")
    export_to_json(results, 'scraped_articles.json')

if __name__ == "__main__":
    main() 