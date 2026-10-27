"""Evaluate the offline search system using labelled, synthetic search queries.

Prints real measured metrics. Benchmark cases are hand-authored, not external user logs.
Metrics are diagnostic only; no claim of production search relevance.
"""
import json
import statistics
import time
from pathlib import Path

from mosaic.catalog import load_catalogue
from mosaic.engine import eligible, search_catalogue
from mosaic.parser import parse_query

ROOT = Path(__file__).resolve().parent


def percentile(values: list[float], fraction: float) -> float:
    values = sorted(values)
    if not values:
        return 0.0
    position = (len(values) - 1) * fraction
    lo = int(position)
    hi = min(lo + 1, len(values) - 1)
    return values[lo] + (values[hi] - values[lo]) * (position - lo)


def run() -> dict:
    cases = json.loads((ROOT / "benchmark_queries.json").read_text(encoding="utf-8"))
    products = load_catalogue()
    timings, correct_categories, correct_budgets, constraint_violations = [], 0, 0, 0
    result_count = 0
    topk_valid = 0
    topk_total = 0
    for case in cases:
        start = time.perf_counter()
        intent = parse_query(case["query"])
        results = search_catalogue(case["query"], intent, products, top_k=5)
        timings.append((time.perf_counter() - start) * 1000)
        correct_categories += int(intent.category == case["expected_category"])
        correct_budgets += int(intent.max_price_usd == case["expected_max_price_usd"])
        for p in results.results:
            result_count += 1
            constraint_violations += int(not eligible(p.product, intent))
            # Verify expected category and expected labelled budget too, independently
            valid = ((case["expected_category"] is None or p.product.category == case["expected_category"])
                     and (case["expected_max_price_usd"] is None or p.product.price_usd <= case["expected_max_price_usd"]))
            topk_valid += int(valid)
            topk_total += 1
    return {
        "dataset": "synthetic catalogue and hand-authored queries",
        "query_count": len(cases),
        "catalogue_size": len(products),
        "category_extraction_accuracy": round(correct_categories / len(cases), 4),
        "budget_extraction_accuracy": round(correct_budgets / len(cases), 4),
        "hard_constraint_violation_rate": round(constraint_violations / max(result_count, 1), 4),
        "top_k_category_budget_validity": round(topk_valid / max(topk_total, 1), 4),
        "median_local_ms": round(statistics.median(timings), 2),
        "p95_local_ms": round(percentile(timings, 0.95), 2),
        "no_external_model_calls": True,
        "warning": "Results describe only this synthetic diagnostic benchmark; no user relevance judgments or ranking ground truth.",
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
