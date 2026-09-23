from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from datetime import datetime
import httpx

from .db import SessionLocal
from .models import Base, engine, NewsItem
from .ingest import ingest_news   # <-- your full ingestion pipeline

# ----------------------------------------
# Initialize FastAPI
# ----------------------------------------
app = FastAPI()

# ----------------------------------------
# CORS
# ----------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Netlify, Render, localhost — everything works
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------
# Root + robots.txt
# ----------------------------------------
@app.api_route("/", methods=["GET", "HEAD"])
def root():
    return {"status": "ok"}

@app.get("/robots.txt")
def robots():
    return PlainTextResponse("User-agent: *\nDisallow: /")

# ----------------------------------------
# Startup: create DB + ingest if empty
# ----------------------------------------
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    has_data = db.query(NewsItem).count() > 0
    db.close()

    if not has_data:
        ingest_news()   # <-- your full ingestion logic runs here


# ----------------------------------------
# DB dependency
# ----------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------------------------
# Response Model
# ----------------------------------------
from pydantic import BaseModel

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

# Main feed
@app.get("/items", response_model=list[NewsItemResponse])
def get_items(
    team: str | None = None,
    min_relevance: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(NewsItem).filter(NewsItem.fantasy_relevance >= min_relevance)

    if team:
        query = query.filter(NewsItem.team == team.upper())

    return query.order_by(NewsItem.created_at.desc()).all()


# Per-team feed
@app.get("/team/{team_abbr}", response_model=list[NewsItemResponse])
def get_team_news(team_abbr: str, db: Session = Depends(get_db)):
    items = (
        db.query(NewsItem)
        .filter(NewsItem.team == team_abbr.upper())
        .order_by(NewsItem.created_at.desc())
        .all()
    )
    return items


# Manual refresh endpoint (optional)
@app.post("/refresh-news")
def refresh_news():
    ingest_news()
    return {"status": "refreshed"}


# ----------------------------------------
# Sleeper API: Top Performers
# ----------------------------------------
SLEEPER_BASE = "https://api.sleeper.app/v1"

async def fetch_json(url: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        if r.status_code != 200:
            raise HTTPException(status_code=502, detail=f"Failed to fetch: {url}")
        return r.json()

@app.get("/top-performers")
async def top_performers(week: int, limit: int = 25):
    stats_url = f"{SLEEPER_BASE}/stats/nfl/2024/{week}"
    stats = await fetch_json(stats_url)

    players = []
    for p in stats:
        points = p.get("fantasy_points_ppr", 0)
        if points and points > 0:
            players.append({
                "player_id": p.get("player_id"),
                "name": p.get("player", "Unknown"),
                "team": p.get("team"),
                "position": p.get("position"),
                "points": points,
            })

    players_sorted = sorted(players, key=lambda x: x["points"], reverse=True)
    return players_sorted[:limit]
