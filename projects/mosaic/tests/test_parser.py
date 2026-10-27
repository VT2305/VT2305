import pytest

from mosaic.parser import parse_query


@pytest.mark.parametrize(
    ("query", "category", "budget"),
    [
        ("Headphones under $180", "headphones", 180),
        ("Laptop up to 1,250", "laptops", 1250),
        ("Mechanical keyboard below $120", "keyboards", 120),
        ("Ergonomic mouse budget of $60", "mice", 60),
        ("Headset within USD 199", "headphones", 199),
        ("Wireless mouse $90 or less", "mice", 90),
    ],
)
def test_budget_category(query, category, budget):
    parsed = parse_query(query)
    assert parsed.category == category
    assert parsed.max_price_usd == budget


def test_required_attribute():
    parsed = parse_query("Headphones under $180 with ANC")
    assert "anc" in parsed.required_features


def test_explicit_negative():
    parsed = parse_query("Keyboard without RGB, ideally quiet")
    assert "rgb" in parsed.excluded_features
    assert "quiet" in parsed.preferences


def test_required_and_excluded_contradiction():
    parsed = parse_query("keyboard with RGB but without RGB")
    assert "rgb" in parsed.excluded_features
    assert "rgb" not in parsed.required_features


def test_minimum_battery_hours():
    parsed = parse_query("headphones at least 30 hours battery")
    assert parsed.min_battery_hours == 30


def test_preference_semantics():
    parsed = parse_query("Laptop ideally lightweight and portable")
    assert "lightweight" in parsed.preferences
    assert "portable" in parsed.preferences


def test_no_keyword_in_longer_word():
    parsed = parse_query("a microcomputer for school")
    assert "microphone" not in parsed.preferences


def test_empty_rejected():
    with pytest.raises(ValueError):
        parse_query(" ")
