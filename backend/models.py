from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class NewsItem(Base):
    __tablename__ = "news_items"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    team = Column(String, nullable=True)
    player_name = Column(String, nullable=True)
    category = Column(String, nullable=True)
    source = Column(String, nullable=True)
    url = Column(String, nullable=True)
    fantasy_relevance = Column(Integer, default=50)
    created_at = Column(DateTime, default=datetime.utcnow)
