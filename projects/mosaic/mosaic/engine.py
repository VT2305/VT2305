"""Deterministic retrieval, ranking and explanations from source attributes."""
from mosaic.models import Product, QueryIntent, RankedProduct, ScoreBreakdown, SearchResponse


def eligible(product: Product, intent: QueryIntent) -> bool:
    if intent.category and product.category != intent.category:
        return False
    if intent.max_price_usd is not None and product.price_usd > intent.max_price_usd:
        return False
    if intent.min_battery_hours is not None and (product.battery_hours is None or product.battery_hours < intent.min_battery_hours):
        return False
    tags = set(product.features)
    return set(intent.required_features).issubset(tags) and not (set(intent.excluded_features) & tags)


def score_product(product: Product, intent: QueryIntent, ceiling: float) -> RankedProduct:
    tags = set(product.features)
    matched = [tag for tag in intent.preferences if tag in tags]
    pref_score = (len(matched) / len(intent.preferences)) if intent.preferences else 0.5
    price_score = max(0.0, 1.0 - product.price_usd / max(ceiling, 1.0))
    rating_score = product.rating / 5.0
    if intent.preferences:
        weights = (0.65, 0.15, 0.20)
    else:
        weights = (0.0, 0.30, 0.70)
    total = 100 * (weights[0] * pref_score + weights[1] * price_score + weights[2] * rating_score)
    evidence = [f"${product.price_usd:,.0f} demo price", f"{product.rating:.1f}/5 demo rating"]
    if matched:
        evidence.insert(0, "matches preferences: " + ", ".join(matched))
    if intent.min_battery_hours is not None and product.battery_hours is not None:
        evidence.append(f"{product.battery_hours:g}h demo battery specification")
    return RankedProduct(
        product=product, score=round(total, 2),
        score_breakdown=ScoreBreakdown(
            preference_match=round(pref_score, 3),
            price_value=round(price_score, 3),
            product_rating=round(rating_score, 3),
        ),
        matched_preferences=matched,
        explanation="; ".join(evidence) + ".",
    )


def search_catalogue(query: str, intent: QueryIntent, products: tuple[Product, ...], top_k: int = 6, parser_used: str = "rules") -> SearchResponse:
    eligible_products = [product for product in products if eligible(product, intent)]
    if intent.max_price_usd is not None:
        ceiling = intent.max_price_usd
    else:
        ceiling = max((product.price_usd for product in products if not intent.category or product.category == intent.category), default=1)
    ranked = sorted(
        (score_product(product, intent, ceiling) for product in eligible_products),
        key=lambda item: (-item.score, item.product.price_usd, item.product.id),
    )
    suggestions = []
    if not eligible_products:
        if intent.max_price_usd is not None:
            suggestions.append("Try increasing the maximum budget.")
        if intent.required_features:
            suggestions.append("Consider relaxing a required feature.")
        if intent.min_battery_hours is not None:
            suggestions.append("Try reducing the minimum battery-hours requirement.")
        if intent.category is None:
            suggestions.append("Mention a category such as headphones or laptops.")
    return SearchResponse(
        query=query, parser_used=parser_used, intent=intent, catalog_size=len(products),
        eligible_count=len(eligible_products), results=ranked[:top_k],
        message=(f"{len(eligible_products)} catalogue products satisfy all hard constraints."
                 if eligible_products else "No catalogue products satisfy every hard constraint."),
        suggestions=suggestions,
    )
