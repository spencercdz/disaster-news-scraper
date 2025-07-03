import os
import json
import datetime
from sqlalchemy import create_engine, Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///articles.db')
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'
    url = Column(String, primary_key=True, index=True)
    headline = Column(String)
    subtitle = Column(String)
    publication_date = Column(DateTime)
    author = Column(String)
    content = Column(Text)
    tags = Column(Text)  # JSON string
    media_urls = Column(Text)  # JSON string
    related_articles = Column(Text)  # JSON string
    scraped_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "url": self.url,
            "headline": self.headline,
            "subtitle": self.subtitle,
            "publication_date": self.publication_date.isoformat() if self.publication_date else None,
            "author": self.author,
            "content": self.content,
            "tags": json.loads(self.tags) if self.tags else [],
            "media_urls": json.loads(self.media_urls) if self.media_urls else [],
            "related_articles": json.loads(self.related_articles) if self.related_articles else [],
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
        }

# Create tables
Base.metadata.create_all(bind=engine) 