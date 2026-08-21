import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
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
