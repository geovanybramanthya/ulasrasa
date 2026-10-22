"""
prepare_pairs.py - Bangun pasangan training (ulasan, aspek) untuk fine-tune ABSA.

Sumber: data/sample_reviews.csv (100 ulasan berlabel 5 aspek).
Hold-out: data/holdout_ids.json (25 ID, FROZEN, seed 42) - TIDAK pernah masuk training.
Output:
  - training/train_pairs.csv        (review_id, aspect, text, label)
  - training/train_pairs_stats.json (distribusi sebelum/sesudah subsample)

Aturan subsample (keputusan terkunci): pasangan not_mentioned dibatasi hingga
maks 1,2 x jumlah pasangan mentioned, dipilih deterministik (seed 42).
Hard assert: tidak ada review_id hold-out di output (gagal keras bila ada).
"""

import json
import os
import sys

import numpy as np
import pandas as pd

ASPECTS = ["rasa", "porsi", "harga", "kemasan", "pelayanan"]
LABELS = ["not_mentioned", "positive", "neutral", "negative"]
SEED = 42
MAX_NOT_MENTIONED_RATIO = 1.2

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_CSV = os.path.join(BASE_DIR, "data", "sample_reviews.csv")
HOLDOUT_JSON = os.path.join(BASE_DIR, "data", "holdout_ids.json")
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_CSV = os.path.join(OUT_DIR, "train_pairs.csv")
OUT_STATS = os.path.join(OUT_DIR, "train_pairs_stats.json")


def load_holdout_ids(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    ids = []
    if isinstance(data, list):
        ids = data
    elif isinstance(data, dict):
        for key in ("holdout_ids", "ids", "holdout", "review_ids"):
            if isinstance(data.get(key), list):
                ids = data[key]
                break
        if not ids and isinstance(data.get("per_restaurant"), dict):
            for entry in data["per_restaurant"].values():
                if isinstance(entry, dict) and isinstance(entry.get("review_ids"), list):
                    ids.extend(entry["review_ids"])
    return [str(x) for x in ids]


def main():
    if not os.path.exists(HOLDOUT_JSON):
        print("ERROR: data/holdout_ids.json tidak ditemukan - hold-out belum dibuat WS-A.")
        sys.exit(2)

    df = pd.read_csv(DATA_CSV)
    df["review_id"] = df["review_id"].astype(str)
    holdout_ids = load_holdout_ids(HOLDOUT_JSON)
    assert len(holdout_ids) == 25, f"holdout harus 25 ID, ditemukan {len(holdout_ids)}"
    assert set(holdout_ids).issubset(set(df["review_id"])), "ada holdout ID yang tidak ada di CSV"

    train_df = df[~df["review_id"].isin(holdout_ids)].copy()
    assert len(train_df) == 75, f"train harus 75 ulasan, ditemukan {len(train_df)}"

    # Bangun pasangan (ulasan x 5 aspek)
    rows = []
    for _, r in train_df.iterrows():
        for asp in ASPECTS:
            rows.append(
                {
                    "review_id": r["review_id"],
                    "aspect": asp,
                    "text": str(r["review_text"]),
                    "label": str(r[asp]).strip(),
                }
            )
    pairs = pd.DataFrame(rows)
    assert set(pairs["label"]).issubset(set(LABELS)), f"label tak dikenal: {set(pairs['label'])}"

    dist_before = pairs["label"].value_counts().to_dict()
    mentioned_n = int((pairs["label"] != "not_mentioned").sum())
    not_mentioned_n = int((pairs["label"] == "not_mentioned").sum())
    max_nm = int(MAX_NOT_MENTIONED_RATIO * mentioned_n)

    rng = np.random.RandomState(SEED)
    nm_idx = pairs.index[pairs["label"] == "not_mentioned"].to_numpy()
    if not_mentioned_n > max_nm:
        keep_nm = rng.choice(nm_idx, size=max_nm, replace=False)
        keep_mask = (pairs["label"] != "not_mentioned") | pairs.index.isin(keep_nm)
        pairs_final = pairs[keep_mask].copy()
    else:
        pairs_final = pairs.copy()

    # Urutan deterministik: shuffle dengan seed tetap
    pairs_final = pairs_final.sample(frac=1.0, random_state=SEED).reset_index(drop=True)

    # HARD ASSERT: tidak ada hold-out yang bocor
    leaked = set(pairs_final["review_id"]).intersection(set(holdout_ids))
    assert not leaked, f"KEBOCORAN HOLD-OUT: {leaked}"
    assert len(set(pairs_final["review_id"])) == 75

    dist_after = pairs_final["label"].value_counts().to_dict()
    per_aspect_after = {
        asp: pairs_final[pairs_final["aspect"] == asp]["label"].value_counts().to_dict()
        for asp in ASPECTS
    }

    pairs_final.to_csv(OUT_CSV, index=False, encoding="utf-8")
    stats = {
        "seed": SEED,
        "n_train_reviews": 75,
        "n_holdout_reviews": 25,
        "pairs_before_subsample": int(len(pairs)),
        "pairs_after_subsample": int(len(pairs_final)),
        "mentioned_pairs": mentioned_n,
        "not_mentioned_before": not_mentioned_n,
        "not_mentioned_cap": max_nm,
        "distribution_before": {k: int(v) for k, v in dist_before.items()},
        "distribution_after": {k: int(v) for k, v in dist_after.items()},
        "distribution_after_per_aspect": per_aspect_after,
    }
    with open(OUT_STATS, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    print(json.dumps(stats, indent=2, ensure_ascii=False))
    print(f"OK: {OUT_CSV}")


if __name__ == "__main__":
    main()
