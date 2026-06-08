# backend/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, engine, Base
from sqlalchemy import Column, Integer, String, DateTime
import datetime

app = FastAPI()

# Enable CORS for local React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SQLAlchemy model matching our Supabase table schema
class DBArticle(Base):
    __tablename__ = "sports_articles"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    source = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)

@app.get("/api/trending")
def get_trending_articles(db: Session = Depends(get_db)):
    # Fetch the 10 newest articles from Supabase
    articles = db.query(DBArticle).order_by(DBArticle.id.desc()).limit(10).all()
    
    # Simple boilerplate if your scraper hasn't run yet
    if not articles:
        return [{"id": 0, "title": "No scraped articles found yet. Run the spider!", "source": "System", "url": "#"}]
        
    return articles