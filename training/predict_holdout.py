"""
predict_holdout.py - Prediksi model fine-tune ABSA pada HOLD-OUT FROZEN.

Membangun pasangan hold-out (25 ulasan x 5 aspek, TANPA subsample), memprediksi
dengan model fine-tune, dan menulis file prediksi:
  evaluation/predictions_<name>.csv  (review_id + 5 kolom aspek berisi label string)

Metrik resmi dihitung oleh scripts/evaluate.py (WS-A):
  python scripts/evaluate.py --predictions evaluation/predictions_<name>.csv --model-name <name>

Pakai:
  python predict_holdout.py --model ..\\models\\indobert-lite-absa --name indobert_lite
"""

import argparse
import json
import os

import pandas as pd
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

ASPECTS = ["rasa", "porsi", "harga", "kemasan", "pelayanan"]
ID2LABEL = {0: "not_mentioned", 1: "positive", 2: "neutral", 3: "negative"}
MAX_LEN = 128

HERE = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(HERE)
DATA_CSV = os.path.join(BASE_DIR, "data", "sample_reviews.csv")
HOLDOUT_JSON = os.path.join(BASE_DIR, "data", "holdout_ids.json")
EVAL_DIR = os.path.join(BASE_DIR, "evaluation")


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
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--name", required=True, choices=["indobert_lite", "indobert_base"])
    args = ap.parse_args()

    os.makedirs(EVAL_DIR, exist_ok=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("device:", device)

    df = pd.read_csv(DATA_CSV)
    df["review_id"] = df["review_id"].astype(str)
    holdout_ids = load_holdout_ids(HOLDOUT_JSON)
    assert len(holdout_ids) == 25, f"holdout harus 25, ditemukan {len(holdout_ids)}"
    hold_df = df[df["review_id"].isin(holdout_ids)].copy()
    assert len(hold_df) == 25, f"hold-out rows harus 25, ditemukan {len(hold_df)}"

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForSequenceClassification.from_pretrained(args.model).to(device)
    model.eval()

    texts, meta = [], []
    for _, r in hold_df.iterrows():
        for asp in ASPECTS:
            texts.append((str(r["review_text"]), asp))
            meta.append((r["review_id"], asp))

    pred_map = {}
    batch = 32
    with torch.no_grad():
        for i in range(0, len(texts), batch):
            chunk = texts[i : i + batch]
            enc = tokenizer(
                [c[0] for c in chunk],
                [c[1] for c in chunk],
                truncation=True,
                max_length=MAX_LEN,
                padding=True,
                return_tensors="pt",
            ).to(device)
            preds = torch.argmax(model(**enc).logits, dim=-1).cpu().numpy()
            for j, p in enumerate(preds):
                pred_map[meta[i + j]] = ID2LABEL[int(p)]

    rows = []
    for _, r in hold_df.iterrows():
        row = {"review_id": r["review_id"]}
        for asp in ASPECTS:
            row[asp] = pred_map[(r["review_id"], asp)]
        rows.append(row)
    out = os.path.join(EVAL_DIR, f"predictions_{args.name}.csv")
    pd.DataFrame(rows, columns=["review_id"] + ASPECTS).to_csv(out, index=False, encoding="utf-8")
    print(f"predictions -> {out} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
