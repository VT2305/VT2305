"""FastAPI service and static demo, offline by default."""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from mosaic.catalog import load_catalogue
from mosaic.engine import search_catalogue
from mosaic.llm import parse_with_anthropic
from mosaic.models import FEATURES, SearchRequest, SearchResponse
from mosaic.parser import parse_query

app = FastAPI(title="Mosaic — Catalogue-Grounded Search", version="1.0.0", description="Transparent demo of constraint-first retrieval and preference ranking. Data is entirely synthetic.")
WEB_PATH = Path(__file__).resolve().parents[1] / "web"


class CatalogInfo(BaseModel):
    synthetic: bool
    count: int
    categories: list[str]
    features: list[str]


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(WEB_PATH / "index.html")


@app.get("/styles.css", include_in_schema=False)
def styles():
    return FileResponse(WEB_PATH / "styles.css", media_type="text/css")


@app.get("/app.js", include_in_schema=False)
def browser_script():
    return FileResponse(WEB_PATH / "app.js", media_type="text/javascript")


@app.get("/api/health")
def health():
    return {"status": "ok", "catalogue": "synthetic", "version": "1.0.0"}


@app.get("/api/catalogue", response_model=CatalogInfo)
def catalogue_info():
    items = load_catalogue()
    return CatalogInfo(synthetic=True, count=len(items), categories=sorted(set(p.category for p in items)), features=sorted(FEATURES))


@app.post("/api/search", response_model=SearchResponse)
def search(payload: SearchRequest):
    try:
        intent = parse_query(payload.query) if payload.parser == "rules" else parse_with_anthropic(payload.query)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return search_catalogue(payload.query, intent, load_catalogue(), payload.top_k, payload.parser)
