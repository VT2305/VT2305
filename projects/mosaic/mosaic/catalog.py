"""Demonstration catalogue. Every product and price is synthetic."""
import json
from functools import lru_cache
from pathlib import Path

from mosaic.models import Product

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "catalogue.json"


@lru_cache(maxsize=1)
def load_catalogue() -> tuple[Product, ...]:
    raw = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    items = tuple(Product.model_validate(item) for item in raw)
    if len({item.id for item in items}) != len(items):
        raise ValueError("catalogue contains duplicate IDs")
    return items
