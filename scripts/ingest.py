import os
import feedparser
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.models import NewsItem
from backend.feeds import RSS_FEEDS
from backend.ingest import (
    extract_team,
    extract_player_name,
    extract_category,
    extract_timestamp,
)

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def ingest():
    db = SessionLocal()

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)

        for entry in feed.entries:
            item = NewsItem(
                text=entry.get("title", ""),
                team=extract_team(entry),
                player_name=extract_player_name(entry),
                category=extract_category(entry),
                source=entry.get("source", "RSS"),
                url=entry.get("link", ""),
                fantasy_relevance=50,
                created_at=extract_timestamp(entry),
            )
            db.add(item)

    db.commit()
    db.close()

if __name__ == "__main__":
    ingest()
