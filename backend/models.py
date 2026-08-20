from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .db import Base

class NewsItem(Base):
    __tablename__ = "news_items"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    team = Column(String)
    player_name = Column(String)
    category = Column(String)
    source = Column(String)
    url = Column(String)
    fantasy_relevance = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
