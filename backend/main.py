from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import feedparser
from fastapi.responses import PlainTextResponse

from .db import Base, engine, SessionLocal
from .models import NewsItem



# ----------------------------------------
# Initialize FastAPI FIRST
# ----------------------------------------
app = FastAPI()

# ----------------------------------------
# CORS
# ----------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.api_route("/", methods=["GET", "HEAD"])
def root():
    return {"status": "ok"}

@app.get("/robots.txt")
def robots():
    return PlainTextResponse("User-agent: *\nDisallow: /")

# ----------------------------------------
# Database setup
# ----------------------------------------

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------------------------
# Models
# ----------------------------------------
class NewsItemResponse(BaseModel):
    id: int
    text: str
    team: str | None
    player_name: str | None
    category: str | None
    source: str | None
    url: str | None
    fantasy_relevance: int
    created_at: datetime

    class Config:
        from_attributes = True


# ----------------------------------------
# ROUTES
# ----------------------------------------





# Feed health checker
@app.get("/debug-feeds")
def debug_feeds():
    results = []

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        results.append({
            "url": url,
            "entries": len(feed.entries),
            "bozo": bool(feed.bozo),
            "error": str(feed.bozo_exception) if feed.bozo else None
        })

    return results


# Per-team filtering
@app.get("/team/{team_abbr}")
def get_team_news(team_abbr: str):
    db = SessionLocal()
    items = (
        db.query(NewsItem)
        .filter(NewsItem.team == team_abbr.upper())
        .order_by(NewsItem.created_at.desc())
        .all()
    )
    db.close()

    return [
        {
            "id": i.id,
            "text": i.text,
            "team": i.team,
            "player_name": i.player_name,
            "category": i.category,
            "source": i.source,
            "url": i.url,
            "fantasy_relevance": i.fantasy_relevance,
            "created_at": i.created_at.isoformat(),
        }
        for i in items
    ]


# Main items endpoint
@app.get("/items")
def get_items(
    team: Optional[str] = None,
    min_relevance: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(NewsItem).filter(NewsItem.fantasy_relevance >= min_relevance)
    if team:
        query = query.filter(NewsItem.team == team.upper())

    items = query.order_by(NewsItem.created_at.desc()).all()

    return [
        {
            "id": i.id,
            "source": i.source,
            "created_at": i.created_at.isoformat(),
            "text": i.text,
            "url": i.url,
            "team": i.team,
            "player_name": i.player_name,
            "category": i.category,
            "fantasy_relevance": i.fantasy_relevance,
        }
        for i in items
    ]
