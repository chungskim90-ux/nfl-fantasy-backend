import feedparser
import re
from datetime import datetime
from .db import SessionLocal
from .models import NewsItem
from zoneinfo import ZoneInfo
from backend.models import NewsItem
from backend.ingest import RSS_FEEDS


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


RSS_FEEDS = [
    # Fantasy news
    "https://www.fantasypros.com/rss/nfl-news.xml",
    "https://www.rotowire.com/rss/news.php?sport=nfl",

    # National news
    "https://profootballtalk.nbcsports.com/feed/",
    "https://www.nbcsports.com/rss/nfl",
    "https://www.nfl.com/rss/rsslanding?searchString=news",

    # AFC East — SB Nation
    "https://www.buffalorumblings.com/rss/index.xml",
    "https://www.thephinsider.com/rss/index.xml",
    "https://www.patspulpit.com/rss/index.xml",
    "https://www.ganggreennation.com/rss/index.xml",

    # AFC North — SB Nation
    "https://www.baltimorebeatdown.com/rss/index.xml",
    "https://www.behindthesteelcurtain.com/rss/index.xml",


    # AFC South — SB Nation
    "https://www.battleredblog.com/rss/index.xml",
    "https://www.stampedeblue.com/rss/index.xml",
    "https://www.bigcatcountry.com/rss/index.xml",
    "https://www.musiccitymiracles.com/rss/index.xml",


    # AFC West — SB Nation
    "https://www.milehighreport.com/rss/index.xml",
    "https://www.arrowheadpride.com/rss/index.xml",
    "https://www.silverandblackpride.com/rss/index.xml",
    "https://www.boltsfromtheblue.com/rss/index.xml",

    # AFC West — Beat Writers
    "https://nitter.net/MikeKlis/rss",
    "https://nitter.net/ryanohalloran/rss",
    "https://nitter.net/SamWarrenNFL/rss",
    "https://nitter.net/VinnyBonsignore/rss",
    "https://nitter.net/DanielPopper/rss",

    # NFC East — SB Nation
    "https://www.bloggingtheboys.com/rss/index.xml",
    "https://www.bigblueview.com/rss/index.xml",
    "https://www.bleedinggreennation.com/rss/index.xml",
    "https://www.hogshaven.com/rss/index.xml",

    # NFC North — SB Nation
    "https://www.windycitygridiron.com/rss/index.xml",
    "https://www.prideofdetroit.com/rss/index.xml",
    "https://www.acmepackingcompany.com/rss/index.xml",
    "https://www.dailynorseman.com/rss/index.xml",


    # NFC South — SB Nation
    "https://www.thefalcoholic.com/rss/index.xml",
    "https://www.catscratchreader.com/rss/index.xml",
    "https://www.canalstreetchronicles.com/rss/index.xml",
    "https://www.bucsnation.com/rss/index.xml",

    # NFC South — Beat Writers
    "https://nitter.net/JeffSchultzATL/rss",
    "https://nitter.net/joebucsfan/rss",

    # NFC West — SB Nation
    "https://www.revengeofthebirds.com/rss/index.xml",
    "https://www.turfshowtimes.com/rss/index.xml",
    "https://www.ninersnation.com/rss/index.xml",
    "https://www.fieldgulls.com/rss/index.xml",

    # Insiders
    "https://nitter.net/AdamSchefter/rss",
    "https://nitter.net/RapSheet/rss",
    "https://nitter.net/TomPelissero/rss",
    "https://nitter.net/FieldYates/rss",
    "https://nitter.net/Schultz_Report/rss",
    "https://nitter.net/AllbrightNFL/rss",
    "https://nitter.net/ProFootballTalk/rss",
    "https://nitter.net/ESPNNFL/rss",
    "https://nitter.net/NFLNetwork/rss",
]


def parse_feed_entry(entry):
    text = entry.get("title", "") or entry.get("summary", "")
    url = entry.get("link", "")

    # Handle RSS timestamps
    if entry.get("published_parsed"):
        dt = datetime(*entry.published_parsed[:6])
        # Treat naive RSS timestamps as Eastern Time
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
    # Look for "Firstname Lastname" patterns
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
    score = 40  # base

    # Category weight
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

    # Keywords
    if any(w in t for w in ["out for season", "torn acl", "achilles", "season-ending"]):
        score += 20
    if any(w in t for w in ["limited", "did not practice", "dnp", "questionable", "doubtful"]):
        score += 10
    if any(w in t for w in ["starting", "starter", "rb1", "wr1", "feature back"]):
        score += 15
    if any(w in t for w in ["targets", "touches", "snap share", "workload"]):
        score += 10

    # Clamp
    if score > 100:
        score = 100
    if score < 0:
        score = 0

    return score

def ingest_news():
    db = SessionLocal()

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries:
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


