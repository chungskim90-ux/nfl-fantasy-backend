import os
import feedparser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.models import NewsItem
from backend.feeds import RSS_FEEDS
from backend.ingest import (
    parse_feed_entry,
    detect_team,
    extract_player_name,
    classify_category,
    score_fantasy_relevance,
)

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def ingest():
    db = SessionLocal()

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)

        for entry in feed.entries:
            # Use your backend parsing logic
            text, url, created_at, source = parse_feed_entry(entry)

            if not text or not url:
                continue

            # Avoid duplicates
            exists = db.query(NewsItem).filter(NewsItem.url == url).first()
            if exists:
                continue

            team = detect_team(text)
            player_name = extract_player_name(text)
            category = classify_category(text)
            fantasy_relevance = score_fantasy_relevance(text, category)

            item = NewsItem(
                text=text,
                team=team,
                player_name=player_name,
                category=category,
                source=source,
                url=url,
                fantasy_relevance=fantasy_relevance,
                created_at=created_at,
            )

            db.add(item)

    db.commit()
    db.close()

if __name__ == "__main__":
    ingest()

