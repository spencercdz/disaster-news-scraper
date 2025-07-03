import re
import dateparser
from .generic_scraper import GenericScraper
from .keywords import KEYWORDS
from src.utils.clean import clean_text, parse_date

# --- Helper for publication date extraction with fallback ---
def extract_pubdate_with_fallback(soup, meta_selector=None, meta_attr=None):
    # Try meta tag first
    if meta_selector and meta_attr:
        meta = soup.find('meta', meta_selector)
        if meta and meta.get(meta_attr):
            return parse_date(meta[meta_attr])
    # Fallback: look for relative time text
    for tag in soup.find_all(['span', 'time']):
        text = tag.get_text(strip=True).lower()
        dt = dateparser.parse(text)
        if dt:
            return dt.isoformat()
    return None

# --- Helper for fallback publication date extraction ---
def fallback_pubdate_extractor(soup, meta_selector=None, meta_attr=None):
    if meta_selector and meta_attr:
        meta = soup.find('meta', meta_selector)
        if meta and meta.get(meta_attr):
            return parse_date(meta[meta_attr])
    for tag in soup.find_all(['span', 'time']):
        text = tag.get_text(strip=True).lower()
        dt = dateparser.parse(text)
        if dt:
            return dt.isoformat()
    return None

# --- BBC ---
def bbc_link_filter(link):
    # Only match /news/articles/ or /news/long-numeric-id
    return ('/news/articles/' in link) or (re.match(r'^/news/\d+$', link) is not None)

def bbc_pubdate_extractor(soup):
    # Try <time datetime=...> first
    time_tag = soup.find('time')
    if time_tag and time_tag.has_attr('datetime'):
        return parse_date(time_tag['datetime'])
    # Fallback to relative
    for tag in soup.find_all(['span', 'time']):
        text = tag.get_text(strip=True).lower()
        dt = dateparser.parse(text)
        if dt:
            return dt.isoformat()
    return None

def bbc_headline_extractor(soup):
    return clean_text(soup.find('h1').text if soup.find('h1') else None)

def bbc_author_extractor(soup):
    return clean_text(soup.find('span', {'class': 'byline__name'}).text if soup.find('span', {'class': 'byline__name'}) else None)

def bbc_content_extractor(soup):
    article = soup.find('article')
    return clean_text(article.text if article else None)

def bbc_tags_extractor(soup):
    return [t.text for t in soup.find_all('li', {'class': 'bbc-1msyfg1 e1hq59l0'})] or []

def bbc_media_extractor(soup):
    return [img['src'] for img in soup.find_all('img') if img.get('src')]

def bbc_related_extractor(soup):
    related = []
    for rel in soup.find_all('a', {'class': 'gs-c-promo-heading'}):
        title = rel.text
        link = rel.get('href')
        if link and not link.startswith('http'):
            link = 'https://www.bbc.com' + link
        related.append({'title': title, 'url': link})
    return related

BBC_SCRAPER = GenericScraper(
    name='BBC',
    homepage_url='https://www.bbc.com/news',
    link_filter=bbc_link_filter,
    pubdate_extractor=bbc_pubdate_extractor,
    headline_extractor=bbc_headline_extractor,
    author_extractor=bbc_author_extractor,
    content_extractor=bbc_content_extractor,
    tags_extractor=bbc_tags_extractor,
    media_extractor=bbc_media_extractor,
    related_extractor=bbc_related_extractor,
    keywords=KEYWORDS
)

# --- CNN ---
def cnn_link_filter(link):
    # Match URLs like /2025/07/03/world/some-article-title.html or .../index.html
    return re.match(r'^/\d{4}/\d{2}/\d{2}/.+\.html$', link) is not None

def cnn_pubdate_extractor(soup):
    # Try <meta itemprop="datePublished"> first
    meta = soup.find('meta', {'itemprop': 'datePublished'})
    if meta and meta.get('content'):
        return parse_date(meta['content'])
    # Fallback to relative
    for tag in soup.find_all(['span', 'time']):
        text = tag.get_text(strip=True).lower()
        dt = dateparser.parse(text)
        if dt:
            return dt.isoformat()
    return None

def cnn_headline_extractor(soup):
    return clean_text(soup.find('h1').text if soup.find('h1') else None)

def cnn_author_extractor(soup):
    return clean_text(soup.find('span', {'class': 'byline__name'}).text if soup.find('span', {'class': 'byline__name'}) else None)

def cnn_content_extractor(soup):
    content = soup.find('div', {'class': 'article__content'})
    if not content:
        content = soup.find('section', {'id': 'body-text'})
    return clean_text(content.text if content else None)

def cnn_tags_extractor(soup):
    return [t.text for t in soup.find_all('meta', {'name': 'section'})] or []

def cnn_media_extractor(soup):
    return [img['src'] for img in soup.find_all('img') if img.get('src')]

def cnn_related_extractor(soup):
    related = []
    for rel in soup.find_all('a', {'class': 'related-article'}):
        title = rel.text
        link = rel.get('href')
        if link and not link.startswith('http'):
            link = 'https://www.cnn.com' + link
        related.append({'title': title, 'url': link})
    return related

CNN_SCRAPER = GenericScraper(
    name='CNN',
    homepage_url='https://www.cnn.com/world',
    link_filter=cnn_link_filter,
    pubdate_extractor=cnn_pubdate_extractor,
    headline_extractor=cnn_headline_extractor,
    author_extractor=cnn_author_extractor,
    content_extractor=cnn_content_extractor,
    tags_extractor=cnn_tags_extractor,
    media_extractor=cnn_media_extractor,
    related_extractor=cnn_related_extractor,
    keywords=KEYWORDS
)

# --- Reuters ---
def reuters_link_filter(link):
    # Match URLs like /world/2025/07/03/some-article-title.html or /article/some-article-title-id.html
    return re.match(r'^/(world|article)/.+\.html$', link) is not None

def reuters_pubdate_extractor(soup):
    # Try <meta property="og:article:published_time"> first
    meta = soup.find('meta', {'property': 'og:article:published_time'})
    if meta and meta.get('content'):
        return parse_date(meta['content'])
    # Fallback to relative
    for tag in soup.find_all(['span', 'time']):
        text = tag.get_text(strip=True).lower()
        dt = dateparser.parse(text)
        if dt:
            return dt.isoformat()
    return None

def reuters_headline_extractor(soup):
    return clean_text(soup.find('h1').text if soup.find('h1') else None)

def reuters_author_extractor(soup):
    return clean_text(soup.find('meta', {'name': 'author'})['content'] if soup.find('meta', {'name': 'author'}) else None)

def reuters_content_extractor(soup):
    content = soup.find('div', {'class': 'article-body__content__17Yit'})
    if not content:
        content = soup.find('div', {'class': 'ArticleBody__content___2gQno'})
    return clean_text(content.text if content else None)

def reuters_tags_extractor(soup):
    return [t.text for t in soup.find_all('a', {'class': 'ArticleHeader_channel_1n4pB'})] or []

def reuters_media_extractor(soup):
    return [img['src'] for img in soup.find_all('img') if img.get('src')]

def reuters_related_extractor(soup):
    related = []
    for rel in soup.find_all('a', {'data-testid': 'related-article-link'}):
        title = rel.text
        link = rel.get('href')
        if link and not link.startswith('http'):
            link = 'https://www.reuters.com' + link
        related.append({'title': title, 'url': link})
    return related

REUTERS_SCRAPER = GenericScraper(
    name='Reuters',
    homepage_url='https://www.reuters.com/news/archive/worldNews',
    link_filter=reuters_link_filter,
    pubdate_extractor=reuters_pubdate_extractor,
    headline_extractor=reuters_headline_extractor,
    author_extractor=reuters_author_extractor,
    content_extractor=reuters_content_extractor,
    tags_extractor=reuters_tags_extractor,
    media_extractor=reuters_media_extractor,
    related_extractor=reuters_related_extractor,
    keywords=KEYWORDS
)

# --- ABC Australia ---
def abc_link_filter(link):
    # Example: /news/2023-07-04/some-article-title/12345678
    return re.match(r'^/news/\d{4}-\d{2}-\d{2}/.+/\d+$', link) is not None

def abc_pubdate_extractor(soup):
    meta = soup.find('meta', {'property': 'article:published'})
    if meta and meta.get('content'):
        return parse_date(meta['content'])
    return fallback_pubdate_extractor(soup)

ABC_SCRAPER = GenericScraper(
    name='ABC Australia',
    homepage_url='https://www.abc.net.au/news/justin',
    link_filter=abc_link_filter,
    pubdate_extractor=abc_pubdate_extractor,
    headline_extractor=lambda soup: clean_text(soup.find('h1').text if soup.find('h1') else None),
    author_extractor=lambda soup: None,
    content_extractor=lambda soup: clean_text(soup.find('article').text if soup.find('article') else None),
    tags_extractor=lambda soup: [],
    media_extractor=lambda soup: [img['src'] for img in soup.find_all('img') if img.get('src')],
    related_extractor=lambda soup: [],
    keywords=KEYWORDS
)

# --- Channel News Asia ---
def cna_link_filter(link):
    return re.match(r'^/news/\d{4}/\d{2}/\d{2}/.+', link) is not None or '/news/' in link

def cna_pubdate_extractor(soup):
    meta = soup.find('meta', {'property': 'article:published_time'})
    if meta and meta.get('content'):
        return parse_date(meta['content'])
    return fallback_pubdate_extractor(soup)

CNA_SCRAPER = GenericScraper(
    name='Channel News Asia',
    homepage_url='https://www.channelnewsasia.com/latest-news',
    link_filter=cna_link_filter,
    pubdate_extractor=cna_pubdate_extractor,
    headline_extractor=lambda soup: clean_text(soup.find('h1').text if soup.find('h1') else None),
    author_extractor=lambda soup: None,
    content_extractor=lambda soup: clean_text(soup.find('article').text if soup.find('article') else None),
    tags_extractor=lambda soup: [],
    media_extractor=lambda soup: [img['src'] for img in soup.find_all('img') if img.get('src')],
    related_extractor=lambda soup: [],
    keywords=KEYWORDS
)

# --- The Star Malaysia ---
def thestar_link_filter(link):
    return re.match(r'^/news/nation/\d{4}/\d{2}/\d{2}/.+', link) is not None or '/news/' in link

def thestar_pubdate_extractor(soup):
    meta = soup.find('meta', {'property': 'article:published_time'})
    if meta and meta.get('content'):
        return parse_date(meta['content'])
    return fallback_pubdate_extractor(soup)

THESTAR_SCRAPER = GenericScraper(
    name='The Star Malaysia',
    homepage_url='https://www.thestar.com.my/news/latest/',
    link_filter=thestar_link_filter,
    pubdate_extractor=thestar_pubdate_extractor,
    headline_extractor=lambda soup: clean_text(soup.find('h1').text if soup.find('h1') else None),
    author_extractor=lambda soup: None,
    content_extractor=lambda soup: clean_text(soup.find('article').text if soup.find('article') else None),
    tags_extractor=lambda soup: [],
    media_extractor=lambda soup: [img['src'] for img in soup.find_all('img') if img.get('src')],
    related_extractor=lambda soup: [],
    keywords=KEYWORDS
)

# --- The Jakarta Post ---
def jakartapost_link_filter(link):
    return re.match(r'^/news/\d{4}/\d{2}/\d{2}/.+', link) is not None or '/news/' in link

def jakartapost_pubdate_extractor(soup):
    meta = soup.find('meta', {'property': 'article:published_time'})
    if meta and meta.get('content'):
        return parse_date(meta['content'])
    return fallback_pubdate_extractor(soup)

JAKARTAPOST_SCRAPER = GenericScraper(
    name='The Jakarta Post',
    homepage_url='https://www.thejakartapost.com/latest',
    link_filter=jakartapost_link_filter,
    pubdate_extractor=jakartapost_pubdate_extractor,
    headline_extractor=lambda soup: clean_text(soup.find('h1').text if soup.find('h1') else None),
    author_extractor=lambda soup: None,
    content_extractor=lambda soup: clean_text(soup.find('article').text if soup.find('article') else None),
    tags_extractor=lambda soup: [],
    media_extractor=lambda soup: [img['src'] for img in soup.find_all('img') if img.get('src')],
    related_extractor=lambda soup: [],
    keywords=KEYWORDS
)

# --- Bangkok Post ---
def bangkokpost_link_filter(link):
    return re.match(r'^/\d{4}/\d{2}/\d{2}/.+', link) is not None or '/news/' in link

def bangkokpost_pubdate_extractor(soup):
    meta = soup.find('meta', {'property': 'article:published_time'})
    if meta and meta.get('content'):
        return parse_date(meta['content'])
    return fallback_pubdate_extractor(soup)

BANGKOKPOST_SCRAPER = GenericScraper(
    name='Bangkok Post',
    homepage_url='https://www.bangkokpost.com/most-recent',
    link_filter=bangkokpost_link_filter,
    pubdate_extractor=bangkokpost_pubdate_extractor,
    headline_extractor=lambda soup: clean_text(soup.find('h1').text if soup.find('h1') else None),
    author_extractor=lambda soup: None,
    content_extractor=lambda soup: clean_text(soup.find('article').text if soup.find('article') else None),
    tags_extractor=lambda soup: [],
    media_extractor=lambda soup: [img['src'] for img in soup.find_all('img') if img.get('src')],
    related_extractor=lambda soup: [],
    keywords=KEYWORDS
)

# --- Xinhua (english.news.cn) ---
def xinhua_link_filter(link):
    return re.match(r'^/\d{4}-\d{2}/\d{2}/c_\d+\.htm$', link) is not None or '/news/' in link

def xinhua_pubdate_extractor(soup):
    meta = soup.find('meta', {'name': 'pubdate'})
    if meta and meta.get('content'):
        return parse_date(meta['content'])
    return fallback_pubdate_extractor(soup)

XINHUA_SCRAPER = GenericScraper(
    name='Xinhua',
    homepage_url='https://english.news.cn/home.htm',
    link_filter=xinhua_link_filter,
    pubdate_extractor=xinhua_pubdate_extractor,
    headline_extractor=lambda soup: clean_text(soup.find('h1').text if soup.find('h1') else None),
    author_extractor=lambda soup: None,
    content_extractor=lambda soup: clean_text(soup.find('article').text if soup.find('article') else None),
    tags_extractor=lambda soup: [],
    media_extractor=lambda soup: [img['src'] for img in soup.find_all('img') if img.get('src')],
    related_extractor=lambda soup: [],
    keywords=KEYWORDS
)

# --- Straits Times (World Latest) ---
def straitstimes_world_link_filter(link):
    return '/world/' in link and link.endswith('.html')

def straitstimes_world_pubdate_extractor(soup):
    meta = soup.find('meta', {'property': 'article:published_time'})
    if meta and meta.get('content'):
        return parse_date(meta['content'])
    return fallback_pubdate_extractor(soup)

STRAITSTIMES_WORLD_SCRAPER = GenericScraper(
    name='Straits Times World',
    homepage_url='https://www.straitstimes.com/world/latest',
    link_filter=straitstimes_world_link_filter,
    pubdate_extractor=straitstimes_world_pubdate_extractor,
    headline_extractor=lambda soup: clean_text(soup.find('h1').text if soup.find('h1') else None),
    author_extractor=lambda soup: None,
    content_extractor=lambda soup: clean_text(soup.find('article').text if soup.find('article') else None),
    tags_extractor=lambda soup: [],
    media_extractor=lambda soup: [img['src'] for img in soup.find_all('img') if img.get('src')],
    related_extractor=lambda soup: [],
    keywords=KEYWORDS
)

# --- Straits Times (Breaking News) ---
def straitstimes_breaking_link_filter(link):
    return '/breaking-news/' in link and link.endswith('.html')

def straitstimes_breaking_pubdate_extractor(soup):
    meta = soup.find('meta', {'property': 'article:published_time'})
    if meta and meta.get('content'):
        return parse_date(meta['content'])
    return fallback_pubdate_extractor(soup)

STRAITSTIMES_BREAKING_SCRAPER = GenericScraper(
    name='Straits Times Breaking',
    homepage_url='https://www.straitstimes.com/breaking-news',
    link_filter=straitstimes_breaking_link_filter,
    pubdate_extractor=straitstimes_breaking_pubdate_extractor,
    headline_extractor=lambda soup: clean_text(soup.find('h1').text if soup.find('h1') else None),
    author_extractor=lambda soup: None,
    content_extractor=lambda soup: clean_text(soup.find('article').text if soup.find('article') else None),
    tags_extractor=lambda soup: [],
    media_extractor=lambda soup: [img['src'] for img in soup.find_all('img') if img.get('src')],
    related_extractor=lambda soup: [],
    keywords=KEYWORDS
)

# --- Reuters Asia-Pacific ---
def reuters_apac_link_filter(link):
    return '/world/asia-pacific/' in link and link.endswith('.html')

def reuters_apac_pubdate_extractor(soup):
    meta = soup.find('meta', {'property': 'og:article:published_time'})
    if meta and meta.get('content'):
        return parse_date(meta['content'])
    return fallback_pubdate_extractor(soup)

REUTERS_APAC_SCRAPER = GenericScraper(
    name='Reuters Asia-Pacific',
    homepage_url='https://www.reuters.com/world/asia-pacific/',
    link_filter=reuters_apac_link_filter,
    pubdate_extractor=reuters_apac_pubdate_extractor,
    headline_extractor=lambda soup: clean_text(soup.find('h1').text if soup.find('h1') else None),
    author_extractor=lambda soup: None,
    content_extractor=lambda soup: clean_text(soup.find('article').text if soup.find('article') else None),
    tags_extractor=lambda soup: [],
    media_extractor=lambda soup: [img['src'] for img in soup.find_all('img') if img.get('src')],
    related_extractor=lambda soup: [],
    keywords=KEYWORDS
)

# --- SCMP Live ---
def scmp_live_link_filter(link):
    return '/live/' in link and link.endswith('.html')

def scmp_live_pubdate_extractor(soup):
    meta = soup.find('meta', {'property': 'article:published_time'})
    if meta and meta.get('content'):
        return parse_date(meta['content'])
    return fallback_pubdate_extractor(soup)

SCMP_LIVE_SCRAPER = GenericScraper(
    name='SCMP Live',
    homepage_url='https://www.scmp.com/live?module=oneline_menu_section_int&pgtype=live',
    link_filter=scmp_live_link_filter,
    pubdate_extractor=scmp_live_pubdate_extractor,
    headline_extractor=lambda soup: clean_text(soup.find('h1').text if soup.find('h1') else None),
    author_extractor=lambda soup: None,
    content_extractor=lambda soup: clean_text(soup.find('article').text if soup.find('article') else None),
    tags_extractor=lambda soup: [],
    media_extractor=lambda soup: [img['src'] for img in soup.find_all('img') if img.get('src')],
    related_extractor=lambda soup: [],
    keywords=KEYWORDS
)

# --- CGTN Asia-Pacific ---
def cgtn_link_filter(link):
    return '/world/asia-pacific/' in link and link.endswith('.html')

def cgtn_pubdate_extractor(soup):
    meta = soup.find('meta', {'property': 'article:published_time'})
    if meta and meta.get('content'):
        return parse_date(meta['content'])
    return fallback_pubdate_extractor(soup)

CGTN_SCRAPER = GenericScraper(
    name='CGTN Asia-Pacific',
    homepage_url='https://www.cgtn.com/world/asia-pacific',
    link_filter=cgtn_link_filter,
    pubdate_extractor=cgtn_pubdate_extractor,
    headline_extractor=lambda soup: clean_text(soup.find('h1').text if soup.find('h1') else None),
    author_extractor=lambda soup: None,
    content_extractor=lambda soup: clean_text(soup.find('article').text if soup.find('article') else None),
    tags_extractor=lambda soup: [],
    media_extractor=lambda soup: [img['src'] for img in soup.find_all('img') if img.get('src')],
    related_extractor=lambda soup: [],
    keywords=KEYWORDS
)

# --- Indian Express (Latest News) ---
def indianexpress_link_filter(link):
    return '/latest-news/' in link and link.endswith('.html')

def indianexpress_pubdate_extractor(soup):
    meta = soup.find('meta', {'property': 'article:published_time'})
    if meta and meta.get('content'):
        return parse_date(meta['content'])
    return fallback_pubdate_extractor(soup)

INDIANEXPRESS_SCRAPER = GenericScraper(
    name='Indian Express',
    homepage_url='https://indianexpress.com/latest-news/?ref=latestnews_hp',
    link_filter=indianexpress_link_filter,
    pubdate_extractor=indianexpress_pubdate_extractor,
    headline_extractor=lambda soup: clean_text(soup.find('h1').text if soup.find('h1') else None),
    author_extractor=lambda soup: None,
    content_extractor=lambda soup: clean_text(soup.find('article').text if soup.find('article') else None),
    tags_extractor=lambda soup: [],
    media_extractor=lambda soup: [img['src'] for img in soup.find_all('img') if img.get('src')],
    related_extractor=lambda soup: [],
    keywords=KEYWORDS
)

# --- The News (Pakistan) ---
def thenews_link_filter(link):
    return '/latest-stories/' in link and link.endswith('.html')

def thenews_pubdate_extractor(soup):
    meta = soup.find('meta', {'property': 'article:published_time'})
    if meta and meta.get('content'):
        return parse_date(meta['content'])
    return fallback_pubdate_extractor(soup)

THENEWS_SCRAPER = GenericScraper(
    name='The News Pakistan',
    homepage_url='https://www.thenews.com.pk/latest-stories',
    link_filter=thenews_link_filter,
    pubdate_extractor=thenews_pubdate_extractor,
    headline_extractor=lambda soup: clean_text(soup.find('h1').text if soup.find('h1') else None),
    author_extractor=lambda soup: None,
    content_extractor=lambda soup: clean_text(soup.find('article').text if soup.find('article') else None),
    tags_extractor=lambda soup: [],
    media_extractor=lambda soup: [img['src'] for img in soup.find_all('img') if img.get('src')],
    related_extractor=lambda soup: [],
    keywords=KEYWORDS
)

# --- Xinhua (Latest News List) ---
def xinhua_list_link_filter(link):
    return '/list/latestnews.htm' in link or link.endswith('.htm')

def xinhua_list_pubdate_extractor(soup):
    meta = soup.find('meta', {'name': 'pubdate'})
    if meta and meta.get('content'):
        return parse_date(meta['content'])
    return fallback_pubdate_extractor(soup)

XINHUA_LIST_SCRAPER = GenericScraper(
    name='Xinhua Latest List',
    homepage_url='https://english.news.cn/list/latestnews.htm',
    link_filter=xinhua_list_link_filter,
    pubdate_extractor=xinhua_list_pubdate_extractor,
    headline_extractor=lambda soup: clean_text(soup.find('h1').text if soup.find('h1') else None),
    author_extractor=lambda soup: None,
    content_extractor=lambda soup: clean_text(soup.find('article').text if soup.find('article') else None),
    tags_extractor=lambda soup: [],
    media_extractor=lambda soup: [img['src'] for img in soup.find_all('img') if img.get('src')],
    related_extractor=lambda soup: [],
    keywords=KEYWORDS
)

# --- Philstar (Homepage) ---
def philstar_home_link_filter(link):
    return '/news/' in link or '/headlines/' in link

def philstar_home_pubdate_extractor(soup):
    meta = soup.find('meta', {'property': 'article:published_time'})
    if meta and meta.get('content'):
        return parse_date(meta['content'])
    return fallback_pubdate_extractor(soup)

PHILSTAR_HOME_SCRAPER = GenericScraper(
    name='Philstar Home',
    homepage_url='https://www.philstar.com/',
    link_filter=philstar_home_link_filter,
    pubdate_extractor=philstar_home_pubdate_extractor,
    headline_extractor=lambda soup: clean_text(soup.find('h1').text if soup.find('h1') else None),
    author_extractor=lambda soup: None,
    content_extractor=lambda soup: clean_text(soup.find('article').text if soup.find('article') else None),
    tags_extractor=lambda soup: [],
    media_extractor=lambda soup: [img['src'] for img in soup.find_all('img') if img.get('src')],
    related_extractor=lambda soup: [],
    keywords=KEYWORDS
)

# --- AP News (Asia-Pacific) ---
def apnews_link_filter(link):
    return '/hub/asia-pacific' in link and link.endswith('.html')

def apnews_pubdate_extractor(soup):
    meta = soup.find('meta', {'property': 'article:published_time'})
    if meta and meta.get('content'):
        return parse_date(meta['content'])
    return fallback_pubdate_extractor(soup)

APNEWS_SCRAPER = GenericScraper(
    name='AP News Asia-Pacific',
    homepage_url='https://apnews.com/hub/asia-pacific',
    link_filter=apnews_link_filter,
    pubdate_extractor=apnews_pubdate_extractor,
    headline_extractor=lambda soup: clean_text(soup.find('h1').text if soup.find('h1') else None),
    author_extractor=lambda soup: None,
    content_extractor=lambda soup: clean_text(soup.find('article').text if soup.find('article') else None),
    tags_extractor=lambda soup: [],
    media_extractor=lambda soup: [img['src'] for img in soup.find_all('img') if img.get('src')],
    related_extractor=lambda soup: [],
    keywords=KEYWORDS
)

# --- SCMP (Asia News) ---
def scmp_asia_link_filter(link):
    return '/news/asia/' in link and link.endswith('.html')

def scmp_asia_pubdate_extractor(soup):
    meta = soup.find('meta', {'property': 'article:published_time'})
    if meta and meta.get('content'):
        return parse_date(meta['content'])
    return fallback_pubdate_extractor(soup)

SCMP_ASIA_SCRAPER = GenericScraper(
    name='SCMP Asia',
    homepage_url='https://www.scmp.com/news/asia',
    link_filter=scmp_asia_link_filter,
    pubdate_extractor=scmp_asia_pubdate_extractor,
    headline_extractor=lambda soup: clean_text(soup.find('h1').text if soup.find('h1') else None),
    author_extractor=lambda soup: None,
    content_extractor=lambda soup: clean_text(soup.find('article').text if soup.find('article') else None),
    tags_extractor=lambda soup: [],
    media_extractor=lambda soup: [img['src'] for img in soup.find_all('img') if img.get('src')],
    related_extractor=lambda soup: [],
    keywords=KEYWORDS
)

# --- Nikkei Asia ---
def nikkei_link_filter(link):
    return '/article/' in link and link.endswith('.html')

def nikkei_pubdate_extractor(soup):
    meta = soup.find('meta', {'property': 'article:published_time'})
    if meta and meta.get('content'):
        return parse_date(meta['content'])
    return fallback_pubdate_extractor(soup)

NIKKEI_SCRAPER = GenericScraper(
    name='Nikkei Asia',
    homepage_url='https://asia.nikkei.com/',
    link_filter=nikkei_link_filter,
    pubdate_extractor=nikkei_pubdate_extractor,
    headline_extractor=lambda soup: clean_text(soup.find('h1').text if soup.find('h1') else None),
    author_extractor=lambda soup: None,
    content_extractor=lambda soup: clean_text(soup.find('article').text if soup.find('article') else None),
    tags_extractor=lambda soup: [],
    media_extractor=lambda soup: [img['src'] for img in soup.find_all('img') if img.get('src')],
    related_extractor=lambda soup: [],
    keywords=KEYWORDS
)

# --- Japan Times (Asia-Pacific) ---
def japantimes_link_filter(link):
    return '/news/asia-pacific/' in link and link.endswith('.html')

def japantimes_pubdate_extractor(soup):
    meta = soup.find('meta', {'property': 'article:published_time'})
    if meta and meta.get('content'):
        return parse_date(meta['content'])
    return fallback_pubdate_extractor(soup)

JAPANTIMES_SCRAPER = GenericScraper(
    name='Japan Times Asia-Pacific',
    homepage_url='https://www.japantimes.co.jp/news/asia-pacific/',
    link_filter=japantimes_link_filter,
    pubdate_extractor=japantimes_pubdate_extractor,
    headline_extractor=lambda soup: clean_text(soup.find('h1').text if soup.find('h1') else None),
    author_extractor=lambda soup: None,
    content_extractor=lambda soup: clean_text(soup.find('article').text if soup.find('article') else None),
    tags_extractor=lambda soup: [],
    media_extractor=lambda soup: [img['src'] for img in soup.find_all('img') if img.get('src')],
    related_extractor=lambda soup: [],
    keywords=KEYWORDS
)

# --- The Guardian (International) ---
def guardian_link_filter(link):
    return '/world/' in link and link.endswith('.html')

def guardian_pubdate_extractor(soup):
    meta = soup.find('meta', {'property': 'article:published_time'})
    if meta and meta.get('content'):
        return parse_date(meta['content'])
    return fallback_pubdate_extractor(soup)

GUARDIAN_SCRAPER = GenericScraper(
    name='The Guardian International',
    homepage_url='https://www.theguardian.com/international',
    link_filter=guardian_link_filter,
    pubdate_extractor=guardian_pubdate_extractor,
    headline_extractor=lambda soup: clean_text(soup.find('h1').text if soup.find('h1') else None),
    author_extractor=lambda soup: None,
    content_extractor=lambda soup: clean_text(soup.find('article').text if soup.find('article') else None),
    tags_extractor=lambda soup: [],
    media_extractor=lambda soup: [img['src'] for img in soup.find_all('img') if img.get('src')],
    related_extractor=lambda soup: [],
    keywords=KEYWORDS
)

# --- Antara News (Indonesia) ---
def antaranews_link_filter(link):
    return '/latest-news/' in link and link.endswith('.html')

def antaranews_pubdate_extractor(soup):
    meta = soup.find('meta', {'property': 'article:published_time'})
    if meta and meta.get('content'):
        return parse_date(meta['content'])
    return fallback_pubdate_extractor(soup)

ANTARANEWS_SCRAPER = GenericScraper(
    name='Antara News',
    homepage_url='https://en.antaranews.com/latest-news',
    link_filter=antaranews_link_filter,
    pubdate_extractor=antaranews_pubdate_extractor,
    headline_extractor=lambda soup: clean_text(soup.find('h1').text if soup.find('h1') else None),
    author_extractor=lambda soup: None,
    content_extractor=lambda soup: clean_text(soup.find('article').text if soup.find('article') else None),
    tags_extractor=lambda soup: [],
    media_extractor=lambda soup: [img['src'] for img in soup.find_all('img') if img.get('src')],
    related_extractor=lambda soup: [],
    keywords=KEYWORDS
)

# --- ABS-CBN (Philippines) ---
def abscbn_link_filter(link):
    return '/news/' in link and link.endswith('.html')

def abscbn_pubdate_extractor(soup):
    meta = soup.find('meta', {'property': 'article:published_time'})
    if meta and meta.get('content'):
        return parse_date(meta['content'])
    return fallback_pubdate_extractor(soup)

ABSCBN_SCRAPER = GenericScraper(
    name='ABS-CBN',
    homepage_url='https://www.abs-cbn.com/news/nation',
    link_filter=abscbn_link_filter,
    pubdate_extractor=abscbn_pubdate_extractor,
    headline_extractor=lambda soup: clean_text(soup.find('h1').text if soup.find('h1') else None),
    author_extractor=lambda soup: None,
    content_extractor=lambda soup: clean_text(soup.find('article').text if soup.find('article') else None),
    tags_extractor=lambda soup: [],
    media_extractor=lambda soup: [img['src'] for img in soup.find_all('img') if img.get('src')],
    related_extractor=lambda soup: [],
    keywords=KEYWORDS
)

ALL_SCRAPERS = {
    "bbc": BBC_SCRAPER,
    "cnn": CNN_SCRAPER,
    "reuters": REUTERS_SCRAPER,
    "abc": ABC_SCRAPER,
    "cna": CNA_SCRAPER,
    "thestar": THESTAR_SCRAPER,
    "jakartapost": JAKARTAPOST_SCRAPER,
    "bangkokpost": BANGKOKPOST_SCRAPER,
    "xinhua": XINHUA_SCRAPER,
    "straitstimes_world": STRAITSTIMES_WORLD_SCRAPER,
    "straitstimes_breaking": STRAITSTIMES_BREAKING_SCRAPER,
    "reuters_apac": REUTERS_APAC_SCRAPER,
    "scmp_live": SCMP_LIVE_SCRAPER,
    "cgtn": CGTN_SCRAPER,
    "indianexpress": INDIANEXPRESS_SCRAPER,
    "thenews": THENEWS_SCRAPER,
    "xinhua_list": XINHUA_LIST_SCRAPER,
    "philstar_home": PHILSTAR_HOME_SCRAPER,
    "apnews": APNEWS_SCRAPER,
    "scmp_asia": SCMP_ASIA_SCRAPER,
    "nikkei": NIKKEI_SCRAPER,
    "japantimes": JAPANTIMES_SCRAPER,
    "guardian": GUARDIAN_SCRAPER,
    "antaranews": ANTARANEWS_SCRAPER,
    "abscbn": ABSCBN_SCRAPER,
}