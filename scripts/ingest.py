import os
import feedparser
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import NewsItem
from backend.ingest import RSS_FEEDS

engine = create_engine(os.getenv("DATABASE_URL"))
SessionLocal = sessionmaker(bind=engine)


def ingest():
    db = SessionLocal()

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)

        for entry in feed.entries:
            item = NewsItem(
                text=entry.get("title", ""),
                team=None,
                player_name=None,
                category=None,
                source=entry.get("source", "unknown"),
                url=entry.get("link", ""),
                fantasy_relevance=50,
                created_at=datetime.utcnow(),
            )
            db.add(item)

    db.commit()
    db.close()

if __name__ == "__main__":
    ingest()
