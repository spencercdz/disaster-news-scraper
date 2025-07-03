import datetime
import json
from .db import Article

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
            scraped_at=now
        )
        session.add(article)
    session.commit()
    return True 