import time
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from src.utils.clean import clean_text, parse_date
from dateutil import parser as date_parser
import re

logger = logging.getLogger(__name__)

def contains_keywords(text, keywords):
    if not text or not keywords:
        return []
    text = clean_text(text).lower()
    matched = []
    for kw in keywords:
        pattern = r'\b' + re.escape(kw.lower()) + r'\b'
        if re.search(pattern, text):
            matched.append(kw)
    return matched

class GenericScraper:
    def __init__(self, name, homepage_url, link_filter, pubdate_extractor, headline_extractor, author_extractor, content_extractor, tags_extractor, media_extractor, related_extractor, subtitle_extractor=None, keywords=None):
        self.name = name
        self.homepage_url = homepage_url
        self.link_filter = link_filter
        self.pubdate_extractor = pubdate_extractor
        self.headline_extractor = headline_extractor
        self.author_extractor = author_extractor
        self.content_extractor = content_extractor
        self.tags_extractor = tags_extractor
        self.media_extractor = media_extractor
        self.related_extractor = related_extractor
        self.subtitle_extractor = subtitle_extractor or (lambda soup: clean_text(soup.find('h2').text if soup.find('h2') else None))
        self.keywords = keywords or []

    def get_latest_articles(self):
        resp = requests.get(self.homepage_url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        now = datetime.utcnow()
        articles = []
        seen = set()
        for a in soup.find_all('a', href=True):
            link = a['href']
            if not self.link_filter(link):
                continue
            if not link.startswith('http'):
                # Build absolute URL
                base = self.homepage_url.split('/')[0] + '//' + self.homepage_url.split('/')[2]
                link = base + link
            if link in seen:
                continue
            seen.add(link)
            try:
                article_resp = requests.get(link, timeout=5)
                article_soup = BeautifulSoup(article_resp.text, 'html.parser')
                pub_date = self.pubdate_extractor(article_soup)
                if not pub_date:
                    logger.warning(f"{self.name}: No publication date found for {link}, skipping article.")
                    continue
                if isinstance(pub_date, str):
                    pub_dt = date_parser.parse(pub_date)
                else:
                    pub_dt = pub_date
                if pub_dt.tzinfo is not None:
                    pub_dt = pub_dt.replace(tzinfo=None)
                if now - pub_dt > timedelta(hours=24):
                    continue
                # Keyword filter: check headline and content
                headline = self.headline_extractor(article_soup)
                subtitle = self.subtitle_extractor(article_soup)
                matched_headline = contains_keywords(headline, self.keywords)
                matched_subtitle = contains_keywords(subtitle, self.keywords)
                if self.keywords and not (matched_headline or matched_subtitle):
                    logger.info(f"{self.name}: Article at {link} does not match keywords, skipping.")
                    continue
                articles.append((link, pub_dt))
                time.sleep(0.2)
            except Exception as e:
                logger.warning(f"{self.name}: Error fetching {link}: {e}")
                continue
        return articles

    def scrape(self, url):
        try:
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
        except Exception as e:
            logger.warning(f"{self.name}: Failed to load {url}: {e}")
            return {'error': 'Failed to load page', 'article_url': url}
        data = {}
        data['article_url'] = url
        data['headline'] = self.headline_extractor(soup)
        data['subtitle'] = self.subtitle_extractor(soup)
        pub_date = self.pubdate_extractor(soup)
        if not pub_date:
            logger.warning(f"{self.name}: No publication date found for {url}, skipping article.")
            return None
        data['publication_date'] = pub_date
        data['author'] = self.author_extractor(soup)
        data['content'] = self.content_extractor(soup)
        matched_headline = contains_keywords(data['headline'], self.keywords)
        matched_subtitle = contains_keywords(data['subtitle'], self.keywords)
        # Keyword filter: check headline and subtitle
        if self.keywords and not (matched_headline or matched_subtitle):
            logger.info(f"{self.name}: Article at {url} does not match keywords, skipping.")
            return None
        data['keywords'] = list(set(matched_headline + matched_subtitle))
        data['tags'] = self.tags_extractor(soup)
        data['media_urls'] = self.media_extractor(soup)
        data['related_articles'] = self.related_extractor(soup)
        return data 