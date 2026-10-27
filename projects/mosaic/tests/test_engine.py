from mosaic.catalog import load_catalogue
from mosaic.engine import eligible, score_product, search_catalogue
from mosaic.models import Product, QueryIntent
from mosaic.parser import parse_query


def test_catalogue_count_ids_and_features():
    items = load_catalogue()
    assert len(items) == 48
    assert len({p.id for p in items}) == len(items)


def test_hard_budget_never_violated():
    intent = parse_query("Headphones under $100")
    response = search_catalogue("Headphones under $100", intent, load_catalogue())
    assert response.eligible_count > 0
    assert all(x.product.price_usd <= 100 for x in response.results)


def test_required_features_never_violated():
    intent = parse_query("headphones with ANC")
    response = search_catalogue("headphones with ANC", intent, load_catalogue())
    assert all("anc" in p.product.features for p in response.results)


def test_exclusion_never_violated():
    intent = parse_query("keyboard without RGB")
    response = search_catalogue("keyboard without RGB", intent, load_catalogue())
    assert all("rgb" not in p.product.features for p in response.results)


def test_battery_never_violated():
    intent = parse_query("headphones at least 35 hours")
    response = search_catalogue("headphones at least 35 hours", intent, load_catalogue())
    assert all(p.product.battery_hours is not None and p.product.battery_hours >= 35 for p in response.results)


def test_no_match_does_not_relax_constraints():
    intent = parse_query("headphones under $10 with ANC")
    response = search_catalogue("headphones under $10 with ANC", intent, load_catalogue())
    assert response.results == []
    assert response.eligible_count == 0
    assert response.suggestions


def test_sort_is_descending_and_deterministic():
    intent = QueryIntent(category="headphones", preferences=["comfortable"])
    first = search_catalogue("comfort", intent, load_catalogue(), top_k=5)
    second = search_catalogue("comfort", intent, load_catalogue(), top_k=5)
    assert [p.product.id for p in first.results] == [p.product.id for p in second.results]
    assert [p.score for p in first.results] == sorted((p.score for p in first.results), reverse=True)


def test_price_breaks_ties():
    p1 = Product(id="aa", name="Item A", category="mice", price_usd=20, rating=4, features=[], description="Synthetic item A")
    p2 = Product(id="bb", name="Item B", category="mice", price_usd=20, rating=4, features=[], description="Synthetic item B")
    intent = QueryIntent(category="mice")
    response = search_catalogue("mice", intent, (p2, p1))
    assert [x.product.id for x in response.results] == ["aa", "bb"]


def test_explanation_grounded_in_product_attributes():
    intent = QueryIntent(category="headphones", preferences=["comfortable"])
    product = load_catalogue()[0]
    result = score_product(product, intent, 200)
    assert result.product.price_usd == 129
    assert "comfortable" in result.explanation
    assert "129" in result.explanation
    assert "demo rating" in result.explanation


def test_zero_category_price_handled():
    intent = QueryIntent(category="mice", max_price_usd=1)
    response = search_catalogue("mice under 1", intent, load_catalogue())
    assert response.eligible_count == 0


def test_invalid_schemas_rejected():
    from pydantic import ValidationError
    try:
        Product(id="id", name="Bad Product", category="mice", price_usd=4, rating=3, features=["made-up"], description="bogus details")
    except ValidationError:
        pass
    else:
        raise AssertionError("unknown product tags should fail validation")


def test_eligible_works_with_exact_constraints():
    product = load_catalogue()[0]
    assert eligible(product, QueryIntent(category="headphones", max_price_usd=129, required_features=["anc"]))
    assert not eligible(product, QueryIntent(category="headphones", max_price_usd=128, required_features=["anc"]))
