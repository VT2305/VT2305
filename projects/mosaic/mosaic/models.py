"""Typed contracts for a transparent catalogue-grounded recommender."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Category = Literal["headphones", "laptops", "keyboards", "mice"]
FEATURES = frozenset({
    "wireless", "anc", "over-ear", "bluetooth", "comfortable", "lightweight",
    "foldable", "water-resistant", "multipoint", "gaming", "microphone",
    "usb-c", "mechanical", "quiet", "ergonomic", "backlit", "rgb",
    "portable", "touchscreen", "long-battery", "fast-charging", "compact",
})


class Product(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(min_length=2)
    name: str = Field(min_length=2)
    category: Category
    price_usd: float = Field(gt=0)
    rating: float = Field(ge=0, le=5)
    battery_hours: float | None = Field(default=None, ge=0)
    features: list[str] = Field(default_factory=list)
    description: str = Field(min_length=8)

    @field_validator("features")
    @classmethod
    def valid_features(cls, features: list[str]) -> list[str]:
        if any(x not in FEATURES for x in features):
            raise ValueError("product includes unsupported feature tags")
        return list(dict.fromkeys(features))


class QueryIntent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    category: Category | None = None
    max_price_usd: float | None = Field(default=None, gt=0)
    min_battery_hours: float | None = Field(default=None, gt=0)
    required_features: list[str] = Field(default_factory=list)
    excluded_features: list[str] = Field(default_factory=list)
    preferences: list[str] = Field(default_factory=list)

    @field_validator("required_features", "excluded_features", "preferences")
    @classmethod
    def valid_tags(cls, tags: list[str]) -> list[str]:
        if any(tag not in FEATURES for tag in tags):
            raise ValueError("query includes unsupported feature tags")
        return list(dict.fromkeys(tags))


class SearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=500)
    top_k: int = Field(default=6, ge=1, le=10)
    parser: Literal["rules", "anthropic"] = "rules"


class ScoreBreakdown(BaseModel):
    preference_match: float
    price_value: float
    product_rating: float


class RankedProduct(BaseModel):
    product: Product
    score: float
    score_breakdown: ScoreBreakdown
    matched_preferences: list[str]
    explanation: str


class SearchResponse(BaseModel):
    query: str
    parser_used: str
    intent: QueryIntent
    catalog_size: int
    eligible_count: int
    results: list[RankedProduct]
    message: str
    suggestions: list[str] = Field(default_factory=list)
