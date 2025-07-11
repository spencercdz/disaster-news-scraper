import logging
from fastapi import FastAPI, Query
from src.scraper.scraper_config import ALL_SCRAPERS
from src.db import SessionLocal, Article
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import json
from src.db_utils import upsert_article

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

# Use ALL_SCRAPERS from scraper_config
SCRAPERS = ALL_SCRAPERS

# In-memory cache: {url: publication_date}
article_cache = {}
CACHE_WINDOW_HOURS = 24

def load_cache_from_db():
    session = SessionLocal()
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(hours=CACHE_WINDOW_HOURS)
    articles = session.query(Article).filter(Article.scraped_at >= cutoff).all()
    cache = {}
    for a in articles:
        if a.publication_date:
            cache[a.url] = a.publication_date
    session.close()
    logger.info(f"Loaded {len(cache)} articles into cache from DB.")
    return cache

def prune_cache_and_db():
    now = datetime.datetime.utcnow()
    to_remove = []
    for url, pub_date in article_cache.items():
        # Make pub_date naive if it's aware
        if hasattr(pub_date, 'tzinfo') and pub_date.tzinfo is not None:
            pub_date_naive = pub_date.replace(tzinfo=None)
        else:
            pub_date_naive = pub_date
        if (now - pub_date_naive).total_seconds() > CACHE_WINDOW_HOURS * 3600:
            to_remove.append(url)
    for url in to_remove:
        del article_cache[url]
    if to_remove:
        logger.info(f"Pruned {len(to_remove)} articles from cache.")
    # Also prune DB
    session = SessionLocal()
    cutoff = now - datetime.timedelta(hours=CACHE_WINDOW_HOURS)
    deleted = session.query(Article).filter(Article.publication_date < cutoff).delete()
    session.commit()
    session.close()
    if deleted:
        logger.info(f"Pruned {deleted} articles from DB (older than {CACHE_WINDOW_HOURS}h).")

def scrape_all():
    logger.info("Starting scheduled scraping job...")
    session = SessionLocal()
    total_new = 0
    prune_cache_and_db()
    for name, scraper in SCRAPERS.items():
        logger.info(f"Visiting {name} for latest articles...")
        articles = scraper.get_latest_articles()
        logger.info(f"Found {len(articles)} candidate articles on {name}.")
        new_count = 0
        for url, pub_date in articles:
            # Check cache before scraping
            if url in article_cache and (datetime.datetime.utcnow() - article_cache[url]).total_seconds() < CACHE_WINDOW_HOURS * 3600:
                continue
            article = session.query(Article).filter_by(url=url).first()
            now = datetime.datetime.utcnow()
            if article and (now - article.scraped_at).total_seconds() < CACHE_WINDOW_HOURS * 3600:
                # Update cache if missing
                if url not in article_cache and article.publication_date:
                    article_cache[url] = article.publication_date
                continue
            data = scraper.scrape(url)
            if data and upsert_article(session, data):
                # Update cache
                if data.get('publication_date'):
                    try:
                        pub_dt = datetime.datetime.fromisoformat(data['publication_date'])
                        article_cache[url] = pub_dt
                    except Exception:
                        pass
                new_count += 1
        logger.info(f"{new_count} new articles scraped and stored for {name}.")
        total_new += new_count
    # Cleanup: remove articles older than 24h from DB
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(hours=CACHE_WINDOW_HOURS)
    deleted = session.query(Article).filter(Article.scraped_at < cutoff).delete()
    session.commit()
    total_articles = session.query(Article).count()
    logger.info(f"Scraping job complete. {total_new} new articles scraped. {deleted} old articles deleted. Total articles in DB: {total_articles}.")
    session.close()
    prune_cache_and_db()

@app.on_event("startup")
def startup_event():
    global article_cache
    article_cache = load_cache_from_db()
    # Do not run scrape_all() on startup

scheduler = BackgroundScheduler()
scheduler.add_job(scrape_all, 'interval', minutes=10)
scheduler.start()

@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()

@app.get("/articles")
def get_articles():
    session = SessionLocal()
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(hours=CACHE_WINDOW_HOURS)
    articles = session.query(Article).filter(Article.scraped_at >= cutoff).all()
    session.close()
    return [a.to_dict() for a in articles]

@app.get("/scrape-now")
def scrape_now():
    scrape_all()
    return {"status": "Scraping triggered"}

@app.post("/clear-db")
def clear_db():
    session = SessionLocal()
    deleted = session.query(Article).delete()
    session.commit()
    session.close()
    article_cache.clear()
    logger.info(f"Cleared DB and cache. {deleted} articles deleted.")
    return {"status": f"Cleared DB and cache. {deleted} articles deleted."}

def upsert_article(session, data):
    url = data['article_url']
    now = datetime.datetime.utcnow()
    article = session.query(Article).filter_by(url=url).first()
    if article:
        # Only update if scraped_at is older than 24h
        if (now - article.scraped_at).total_seconds() < 24*3600:
            return False  # Already fresh
        # Update fields
        article.headline = data.get('headline')
        article.subtitle = data.get('subtitle')
        article.publication_date = datetime.datetime.fromisoformat(data['publication_date']) if data.get('publication_date') else None
        article.author = data.get('author')
        article.content = data.get('content')
        article.tags = json.dumps(data.get('tags', []))
        article.media_urls = json.dumps(data.get('media_urls', []))
        article.related_articles = json.dumps(data.get('related_articles', []))
        article.keywords = json.dumps(data.get('keywords', []))
        article.scraped_at = now
    else:
        article = Article(
            url=url,
            headline=data.get('headline'),
            subtitle=data.get('subtitle'),
            publication_date=datetime.datetime.fromisoformat(data['publication_date']) if data.get('publication_date') else None,
            author=data.get('author'),
            content=data.get('content'),
            tags=json.dumps(data.get('tags', [])),
            media_urls=json.dumps(data.get('media_urls', [])),
            related_articles=json.dumps(data.get('related_articles', [])),
            keywords=json.dumps(data.get('keywords', [])),
            scraped_at=now
        )
        session.add(article)
    session.commit()
    return True 