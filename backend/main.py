from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import feedparser
from fastapi.responses import PlainTextResponse
import httpx

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

    # Seed real RSS data if DB is empty
    from .db import seed_real_data
    seed_real_data()


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
# Sleeper global stats helper
# ----------------------------------------
SLEEPER_BASE = "https://api.sleeper.app/v1"

async def fetch_json(url: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        if r.status_code != 200:
            raise HTTPException(status_code=502, detail=f"Failed to fetch: {url}")
        return r.json()

# ----------------------------------------
# ROUTES
# ----------------------------------------

# Global weekly top performers (no league required)
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

# Feed health checker
@app.get("/debug-feeds")
def debug_feeds():
    results = []

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        results