# backend/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, engine, Base
from sqlalchemy import Column, Integer, String, DateTime
import datetime
from pydantic import BaseModel
from typing import Optional

# scraper imports
from scraper.crawler import parse_receiving_and_rushing_table
from scraper.ingest import upsert_player_seasons, create_tables_if_missing

app = FastAPI()

# Enable CORS for local React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://stat-spyder.vercel.app"],
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


class ScrapeRequest(BaseModel):
    url: Optional[str] = None
    html: Optional[str] = None
    row_selector: Optional[str] = None


@app.on_event("startup")
def _startup():
    # ensure our tables exist
    try:
        create_tables_if_missing(engine)
    except Exception:
        # don't crash the app on startup if create fails; ingestion will fail later
        pass


def _fetch_html_from_url(url: str) -> str:
    # Try a browser-like requests first (common headers), then fallback to
    # Playwright (for JS-protected pages), and finally urllib as a last resort.
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": url,
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    # 1) Try requests with common browser headers
    req_exc = None
    try:
        import requests

        sess = requests.Session()
        sess.headers.update(headers)
        resp = sess.get(url, timeout=20)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        req_exc = e

    # 2) Try Playwright when requests failed (useful for Cloudflare/JS pages)
    pw_exc = None
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            context = browser.new_context(user_agent=headers["User-Agent"], locale="en-US")
            page = context.new_page()
            page.goto(url, timeout=30000)
            html = page.content()
            browser.close()
            return html
    except Exception as e:
        pw_exc = e

    # 3) Last resort: urllib with the same headers
    try:
        from urllib.request import Request, urlopen

        req = Request(url, headers=headers)
        with urlopen(req, timeout=20) as resp:
            raw = resp.read()
            # try to infer encoding
            encoding = resp.headers.get_content_charset() if hasattr(resp, "headers") else None
            if not encoding:
                encoding = "utf-8"
            return raw.decode(encoding, errors="replace")
    except Exception as e:
        # raise a combined error for easier debugging upstream
        raise Exception(f"requests error: {req_exc}; playwright error: {pw_exc}; urllib error: {e}")



@app.get("/api/trending")
def get_trending_articles(db: Session = Depends(get_db)):
    # Fetch the 10 newest articles from Supabase
    articles = db.query(DBArticle).order_by(DBArticle.id.desc()).limit(10).all()
    
    # Simple boilerplate if your scraper hasn't run yet
    if not articles:
        return [{"id": 0, "title": "No scraped articles found yet. Run the spider!", "source": "System", "url": "#"}]
        
    return articles


@app.post("/api/scrape")
def scrape_and_ingest(payload: ScrapeRequest, db: Session = Depends(get_db)):
    """On-demand scraping endpoint.

    Provide either `url` or raw `html` in the JSON body. The endpoint parses
    receiving_and_rushing rows (or use `row_selector` to target a different
    set of rows) and upserts them into the database.
    """
    html = payload.html
    if not html:
        if not payload.url:
            raise HTTPException(status_code=400, detail="Either 'url' or 'html' is required")
        try:
            html = _fetch_html_from_url(payload.url)
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Failed to fetch url: {exc}")

    rows = parse_receiving_and_rushing_table(html, row_selector=payload.row_selector)
    if not rows:
        return {"processed": 0, "rows_found": 0}

    processed = upsert_player_seasons(db, rows)

    # return a small sample of parsed rows
    sample = []
    for r in rows[:5]:
        try:
            sample.append(r.model_dump())
        except AttributeError:
            sample.append(r.dict())

    return {"processed": processed, "rows_found": len(rows), "sample": sample}


@app.post("/api/preview")
def preview_parsed_rows(payload: ScrapeRequest):
    """Parse provided URL or raw HTML and return parsed rows without inserting."""
    html = payload.html
    if not html:
        if not payload.url:
            raise HTTPException(status_code=400, detail="Either 'url' or 'html' is required")
        try:
            html = _fetch_html_from_url(payload.url)
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Failed to fetch url: {exc}")

    rows = parse_receiving_and_rushing_table(html, row_selector=payload.row_selector)
    result = []
    for r in rows:
        try:
            result.append(r.model_dump())
        except AttributeError:
            result.append(r.dict())

    return {"rows_found": len(rows), "rows": result}


@app.post("/api/db/init")
def init_db():
    """Create database tables for the application models.

    This is intended for development environments where the backend can
    create tables directly. It will call `create_tables_if_missing(engine)`.
    """
    try:
        create_tables_if_missing(engine)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create tables: {exc}")
    return {"created": True}