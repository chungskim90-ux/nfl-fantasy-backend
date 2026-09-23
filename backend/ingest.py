import feedparser
import re
from datetime import datetime
from zoneinfo import ZoneInfo

from .db import SessionLocal
from .models import NewsItem
from .feeds import RSS_FEEDS  # <-- use relative import, single source of truth


TEAM_MAP = {
    "ARI": ["cardinals", "arizona"],
    "ATL": ["falcons", "atlanta"],
    "BAL": ["ravens", "baltimore"],
    "BUF": ["bills", "buffalo"],
    "CAR": ["panthers", "carolina"],
    "CHI": ["bears", "chicago"],
    "CIN": ["bengals", "cincinnati"],
    "CLE": ["browns", "cleveland"],
    "DAL": ["cowboys", "dallas"],
    "DEN": ["broncos", "denver"],
    "DET": ["lions", "detroit"],
    "GB":  ["packers", "green bay"],
    "HOU": ["texans", "houston"],
    "IND": ["colts", "indianapolis"],
    "JAX": ["jaguars", "jacksonville"],
    "KC":  ["chiefs", "kansas city"],
    "LV":  ["raiders", "las vegas", "oakland"],
    "LAC": ["chargers", "los angeles chargers", "san diego"],
    "LAR": ["rams", "los angeles rams"],
    "MIA": ["dolphins", "miami"],
    "MIN": ["vikings", "minnesota"],
    "NE":  ["patriots", "new england"],
    "NO":  ["saints", "new orleans"],
    "NYG": ["giants", "new york giants"],
    "NYJ": ["jets", "new york jets"],
    "PHI": ["eagles", "philadelphia"],
    "PIT": ["steelers", "pittsburgh"],
    "SEA": ["seahawks", "seattle"],
    "SF":  ["49ers", "san francisco"],
    "TB":  ["buccaneers", "tampa bay", "bucs"],
    "TEN": ["titans", "tennessee"],
    "WAS": ["commanders", "washington"],
}


def parse_feed_entry(entry):
    text = entry.get("title", "") or entry.get("summary", "")
    url = entry.get("link", "")

    if entry.get("published_parsed"):
        dt = datetime(*entry.published_parsed[:6])
        dt = dt.replace(tzinfo=ZoneInfo("America/New_York"))
    else:
        dt = datetime.now(ZoneInfo("America/New_York"))

    created_at = dt
    source = entry.get("source", {}).get("title", "RSS") if entry.get("source") else "RSS"

    return text, url, created_at, source


def detect_team(text: str) -> str | None:
    t = text.lower()
    for abbr, keywords in TEAM_MAP.items():
        for kw in keywords:
            if kw in t:
                return abbr
    return None


def extract_player_name(text: str) -> str | None:
    matches = re.findall(r"\b([A-Z][a-z]+ [A-Z][a-z]+)\b", text)
    return matches[0] if matches else None


def classify_category(text: str) -> str | None:
    t = text.lower()

    if any(w in t for w in ["out for", "out with", "questionable", "doubtful", "injury", "ruled out", "inactive"]):
        return "injury"
    if any(w in t for w in ["first-team", "starter", "starting role", "depth chart", "backup", "rb1", "wr1", "te1"]):
        return "depth_chart"
    if any(w in t for w in ["trade", "traded", "acquired", "sent to", "deal with"]):
        return "trade"
    if any(w in t for w in ["signed", "extension", "contract", "restructured"]):
        return "contract"
    if any(w in t for w in ["suspended", "discipline", "ban"]):
        return "suspension"

    return "news"


def score_fantasy_relevance(text: str, category: str | None) -> int:
    t = text.lower()
    score = 40

    if category == "injury":
        score += 40
    elif category == "depth_chart":
        score += 30
    elif category == "trade":
        score += 35
    elif category == "contract":
        score += 15
    elif category == "suspension":
        score += 35

    if any(w in t for w in ["out for season", "torn acl", "achilles", "season-ending"]):
        score += 20
    if any(w in t for w in ["limited", "did not practice", "dnp", "questionable", "doubtful"]):
        score += 10
    if any(w in t for w in ["starting", "starter", "rb1", "wr1", "feature back"]):
        score += 15
    if any(w in t for w in ["targets", "touches", "snap share", "workload"]):
        score += 10

    return max(0, min(score, 100))


def ingest_news():
    db = SessionLocal()

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)

        if not hasattr(feed, "entries"):
            continue

        for entry in feed.entries:
            text, url, created_at, source = parse_feed_entry(entry)

            if not text or not url:
                continue

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
