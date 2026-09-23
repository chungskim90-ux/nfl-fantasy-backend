from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, NewsItem
from datetime import datetime
import feedparser
from .feeds import RSS_FEEDS

DATABASE_URL = "sqlite:///./news.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def seed_real_data():
    db = SessionLocal()

    # Only seed if empty
    if db.query(NewsItem).count() > 0:
        db.close()
        return

    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)

            if not hasattr(feed, "entries"):
                continue

            for entry in feed.entries:
                title = entry.get("title")
                link = entry.get("link")

                if not title:
                    continue

                # Prevent duplicates
                exists = db.query(NewsItem).filter(NewsItem.text == title).first()
                if exists:
                    continue

                item = NewsItem(
                    text=title,
                    team=None,
                    player_name=None,
                    category=None,
                    source=getattr(feed.feed, "title", "Unknown"),
                    url=link,
                    fantasy_relevance=50,
                    created_at=datetime.utcnow()
                )

                db.add(item)

        except Exception:
            continue

    db.commit()
    db.close()
