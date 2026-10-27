"""Offline, inspectable intent extraction. No external model or credentials needed."""
import re

from mosaic.models import FEATURES, QueryIntent

ALIASES = {
    "anc": ["anc", "active noise cancellation", "noise cancelling", "noise canceling"],
    "wireless": ["wireless", "cordless"],
    "over-ear": ["over-ear", "over ear"],
    "bluetooth": ["bluetooth"],
    "comfortable": ["comfortable", "comfort"],
    "lightweight": ["lightweight", "light weight", "light-weight"],
    "foldable": ["foldable", "folding"],
    "water-resistant": ["water-resistant", "waterproof", "water resistant"],
    "multipoint": ["multipoint", "multi-device"],
    "gaming": ["gaming", "gamer"],
    "microphone": ["microphone", "mic"],
    "usb-c": ["usb-c", "usb c"],
    "mechanical": ["mechanical"],
    "quiet": ["quiet", "silent"],
    "ergonomic": ["ergonomic", "ergonomics"],
    "backlit": ["backlit", "backlight"],
    "rgb": ["rgb"],
    "portable": ["portable"],
    "touchscreen": ["touchscreen", "touch screen"],
    "long-battery": ["long battery", "long-lasting battery", "battery life"],
    "fast-charging": ["fast charging", "fast-charging", "quick charging"],
    "compact": ["compact", "small form factor"],
}
CATEGORY_ALIASES = {
    "headphones": ["headphones", "headset", "earphones"],
    "laptops": ["laptop", "laptops", "notebook computer", "notebook"],
    "keyboards": ["keyboard", "keyboards", "keycaps"],
    "mice": ["mouse", "mice", "pointing device"],
}
BUDGET = re.compile(
    r"(?:under|below|less than|up to|maximum(?: of)?|max(?:imum)?|budget(?: of)?|at most|within|≤)\s*(?:usd\s*)?\$?\s*([\d,]+(?:\.\d+)?)"
    r"|(?:\$|usd\s*)([\d,]+(?:\.\d+)?)\s*(?:or less|maximum|max)",
    re.I,
)
BATTERY = re.compile(r"(?:at least|min(?:imum)?|over)\s*(\d+)\s*(?:hours?|hrs?|h)\b", re.I)


def _occurrences(text: str, alias: str):
    """Yield matches with boundaries (so 'mic' does not match 'micro')."""
    pattern = r"(?<!\w)" + re.escape(alias) + r"(?!\w)"
    return list(re.finditer(pattern, text, flags=re.I))


def parse_query(text: str) -> QueryIntent:
    if not text or not text.strip():
        raise ValueError("query cannot be empty")
    clean = " ".join(text.lower().split())
    category = None
    for name, aliases in CATEGORY_ALIASES.items():
        if any(_occurrences(clean, a) for a in aliases):
            category = name
            break

    match = BUDGET.search(clean)
    max_price = float((match.group(1) or match.group(2)).replace(",", "")) if match else None
    match = BATTERY.search(clean)
    min_battery = float(match.group(1)) if match else None

    required, excluded, preferences = [], [], []
    for feature, aliases in ALIASES.items():
        if feature not in FEATURES:
            continue
        matches = sorted((m for alias in aliases for m in _occurrences(clean, alias)), key=lambda m: m.start())
        if not matches:
            continue
        # Interpret the closest phrase, not a blanket keyword match. Negation wins.
        states = []
        for m in matches:
            prefix = clean[max(0, m.start() - 38):m.start()]
            nearest = re.search(
                r"(?:\b(?:without|exclude|excluding|avoid|no|not|must not)\s+|"
                r"\b(?:must have|require|requires|required|need|needs|with)\s+|"
                r"\b(?:prefer|ideally|nice to have|would like|good)\s+)$", prefix
            )
            token = nearest.group(0).strip() if nearest else ""
            if token in {"without", "exclude", "excluding", "avoid", "no", "not", "must not"}:
                states.append("exclude")
            elif token in {"must have", "require", "requires", "required", "need", "needs", "with"}:
                states.append("required")
            else:
                states.append("prefer")
        if "exclude" in states:
            excluded.append(feature)
        elif "required" in states:
            required.append(feature)
        else:
            preferences.append(feature)
    # If contradictory descriptions appear, exclusion is the safer hard constraint.
    required = [x for x in required if x not in excluded]
    preferences = [x for x in preferences if x not in excluded and x not in required]
    return QueryIntent(
        category=category, max_price_usd=max_price, min_battery_hours=min_battery,
        required_features=required, excluded_features=excluded, preferences=preferences,
    )
