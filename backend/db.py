from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ----------------------------------------
# SQLite database (local file)
# ----------------------------------------

DATABASE_URL = "sqlite:///./news.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def seed_mock_data():
    from .models import NewsItem   # <-- import here, NOT at top

    db = SessionLocal()

    if db.query(NewsItem).count() == 0:
        from datetime import datetime
        items = [
            NewsItem(
                text="Justin Jefferson expected to play Week 1.",
                team="MIN",
                player_name="Justin Jefferson",
                category="injury",
                source="Schefter",
                url="https://example.com",
                fantasy_relevance=90,
                created_at=datetime.utcnow()
            ),
            NewsItem(
                text="Tony Pollard getting first-team reps.",
                team="DAL",
                player_name="Tony Pollard",
                category="depth_chart",
                source="RapSheet",
                url="https://example.com",
                fantasy_relevance=75,
                created_at=datetime.utcnow()
            ),
        ]
        db.add_all(items)
        db.commit()

    db.close()

def seed_real_data():
    import feedparser
    from datetime import datetime
    from .models import NewsItem
    from .feed import RSS_FEEDS   # <-- your feed.py file

    db = SessionLocal()

    # Only seed if DB is empty
    if db.query(NewsItem).count() == 0:
        for url in RSS_FEEDS:
            feed = feedparser.parse(url)

            for entry in feed.entries:
                item = NewsItem(
                    text=entry.get("title", "No title"),
                    team=None,  # You can enhance this later
                    player_name=None,
                    category=None,
                    source=feed.feed.get("title", "Unknown"),
                    url=entry.get("link"),
                    fantasy_relevance=50,  # Default relevance
                    created_at=datetime.utcnow()
                )
                db.add(item)

        db.commit()

    db.close()

