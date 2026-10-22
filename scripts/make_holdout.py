"""Freeze a deterministic stratified hold-out set for UlasRasa evaluation.

Splits 25 of 100 reviews from data/sample_reviews.csv into a hold-out set:
- Stratified proportionally per restaurant_name.
- Within each restaurant, reviews are chosen greedily so the hold-out label
  distribution (5 aspects x 4 classes) tracks the restaurant's own label
  distribution as closely as possible.
- Deterministic with seed 42 (seeded tie-breaking + greedy deviation minimisation).

Writes data/holdout_ids.json. The hold-out is FROZEN: this script refuses to
overwrite an existing holdout_ids.json.
"""

import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

SEED = 42
HOLDOUT_N = 25
ASPECTS = ["rasa", "porsi", "harga", "kemasan", "pelayanan"]
CLASSES = ["positive", "neutral", "negative", "not_mentioned"]

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "sample_reviews.csv"
OUT_PATH = ROOT / "data" / "holdout_ids.json"


def proportional_quotas(group_sizes: dict, total: int) -> dict:
    """Largest-remainder proportional allocation, deterministic on ties
    (ties broken by sorted group name)."""
    n_all = sum(group_sizes.values())
    raw = {g: total * s / n_all for g, s in group_sizes.items()}
    quotas = {g: int(v) for g, v in raw.items()}
    remainder = total - sum(quotas.values())
    order = sorted(group_sizes, key=lambda g: (-(raw[g] - quotas[g]), g))
    for g in order[:remainder]:
        quotas[g] += 1
    return quotas


def deviation(selected_labels: list, group_labels: list, quota: int, group_n: int) -> float:
    """Sum of absolute deviations between the selected subset's per-class
    counts and the proportionally expected counts, across all aspects."""
    dev = 0.0
    for j in range(len(ASPECTS)):
        for cls in CLASSES:
            expected = quota * sum(1 for row in group_labels if row[j] == cls) / group_n
            actual = sum(1 for row in selected_labels if row[j] == cls)
            dev += abs(actual - expected)
    return dev


def pick_for_group(df_group: pd.DataFrame, quota: int, rng: random.Random) -> list:
    """Greedy pick: repeatedly add the review that minimises label-distribution
    deviation. Candidate order is a seeded shuffle, so ties are deterministic."""
    labels = {
        int(r.review_id): tuple(getattr(r, a) for a in ASPECTS)
        for r in df_group.itertuples()
    }
    group_labels = list(labels.values())
    candidates = list(labels.keys())
    rng.shuffle(candidates)

    selected: list = []
    selected_labels: list = []
    while len(selected) < quota:
        best_id, best_dev = None, None
        for cid in candidates:
            if cid in selected:
                continue
            d = deviation(selected_labels + [labels[cid]], group_labels, quota, len(group_labels))
            if best_dev is None or d < best_dev - 1e-12:
                best_id, best_dev = cid, d
        selected.append(best_id)
        selected_labels.append(labels[best_id])
    return selected


def main() -> int:
    if OUT_PATH.exists():
        print(f"ERROR: {OUT_PATH} already exists. Hold-out is FROZEN; refusing to overwrite.", file=sys.stderr)
        return 1

    df = pd.read_csv(CSV_PATH)
    if len(df) != 100:
        print(f"ERROR: expected 100 rows in dataset, found {len(df)}.", file=sys.stderr)
        return 1

    rng = random.Random(SEED)
    group_sizes = df["restaurant_name"].value_counts().to_dict()
    quotas = proportional_quotas(group_sizes, HOLDOUT_N)

    holdout_ids: list = []
    per_restaurant: dict = {}
    for resto in sorted(group_sizes):
        picked = pick_for_group(df[df["restaurant_name"] == resto], quotas[resto], rng)
        holdout_ids.extend(picked)
        per_restaurant[resto] = {"quota": quotas[resto], "review_ids": sorted(picked)}

    holdout_ids = sorted(int(i) for i in holdout_ids)
    assert len(holdout_ids) == HOLDOUT_N and len(set(holdout_ids)) == HOLDOUT_N
    assert set(holdout_ids).issubset(set(int(i) for i in df["review_id"]))

    payload = {
        "seed": SEED,
        "created_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "n": HOLDOUT_N,
        "dataset": "data/sample_reviews.csv",
        "method": (
            "Deterministic split, seed 42. Quota per restaurant allocated proportionally "
            "by largest remainder (25 hold-out of 100 reviews, 4 restaurants x 25). Within "
            "each restaurant, reviews were picked greedily to minimise the absolute deviation "
            "between the hold-out label distribution (5 aspects x 4 classes) and the "
            "restaurant's own label distribution; ties broken by a seed-42 shuffle. "
            "This file is FROZEN: make_holdout.py refuses to overwrite it."
        ),
        "per_restaurant": per_restaurant,
        "review_ids": holdout_ids,
    }
    OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUT_PATH} with {len(holdout_ids)} hold-out ids.")
    for resto, info in per_restaurant.items():
        print(f"  {resto}: {info['quota']} -> {info['review_ids']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
