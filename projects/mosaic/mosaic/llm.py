"""Optional Anthropic intent parsing; decisions remain deterministic and auditable.

Install with pip install -e '.[llm]' and set ANTHROPIC_API_KEY. An LLM never
selects products, invents catalogue facts, or overrides the filter engine.
"""
import json
import os
import re

from mosaic.models import FEATURES, QueryIntent

SYSTEM = (
    "Extract customer product-search intent. Return ONLY one JSON object matching keys: "
    "category (headphones|laptops|keyboards|mice|null), max_price_usd (number|null), "
    "min_battery_hours (number|null), required_features (array), excluded_features (array), "
    "preferences (array). Hard requirements are mandatory; ordinary adjectives are soft preferences. "
    "Use only tags from: " + ", ".join(sorted(FEATURES)) + ". "
    "Do not add requirements, prices, categories or preferences absent from the user input. "
    "No product recommendations, no markdown, no external knowledge."
)


def parse_with_anthropic(query: str) -> QueryIntent:
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY is not set. Select the rules parser or configure the key.")
    try:
        from anthropic import Anthropic
    except ImportError as exc:
        raise RuntimeError("Install optional LLM support with pip install -e '.[llm]'.") from exc
    client = Anthropic(timeout=12.0)
    result = client.messages.create(
        model=os.getenv("MOSAIC_ANTHROPIC_MODEL", "claude-sonnet-4-5"),
        max_tokens=450,
        temperature=0,
        system=SYSTEM,
        messages=[{"role": "user", "content": query}],
    )
    body = "".join(getattr(block, "text", "") for block in result.content).strip()
    # Accept plaintext JSON or JSON in a fenced block, but nothing else.
    if body.startswith("```"):
        body = re.sub(r"^```(?:json)?\s*|\s*```$", "", body).strip()
    try:
        return QueryIntent.model_validate(json.loads(body))
    except (ValueError, TypeError) as exc:
        raise RuntimeError("LLM returned invalid intent; no products were selected.") from exc
