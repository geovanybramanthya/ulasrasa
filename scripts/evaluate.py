"""Evaluate ABSA predictions on the frozen UlasRasa hold-out set.

Modes:
  Default            Run src.absa_pipeline.ABSAPipeline on the hold-out reviews
                     and score it as model "lexicon_baseline".
  --predictions FILE CSV with columns review_id + rasa/porsi/harga/kemasan/
                     pelayanan containing predicted labels; scored under
                     --model-name (default: the CSV file stem).

Metrics, per aspect, over the 4 classes
[positive, neutral, negative, not_mentioned]:
precision / recall / F1 per class, Macro-F1 per aspect, a 4x4 confusion
matrix (rows = gold, columns = predicted), plus an overall Macro-F1
(mean of the per-aspect Macro-F1 values).

Output is merged into evaluation/evaluation_results.json: sections for other
models already present in the file are preserved.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

ASPECTS = ["rasa", "porsi", "harga", "kemasan", "pelayanan"]
CLASSES = ["positive", "neutral", "negative", "not_mentioned"]
CSV_PATH = ROOT / "data" / "sample_reviews.csv"
HOLDOUT_PATH = ROOT / "data" / "holdout_ids.json"
OUT_PATH = ROOT / "evaluation" / "evaluation_results.json"

LEXICON_CAVEAT = (
    "Lexicon dikembangkan terhadap keseluruhan dataset sebelum hold-out dibekukan; "
    "angka ini perbandingan internal, bukan estimasi generalisasi murni."
)


def per_aspect_metrics(gold: list, pred: list) -> dict:
    idx = {c: i for i, c in enumerate(CLASSES)}
    cm = [[0] * len(CLASSES) for _ in CLASSES]
    for g, p in zip(gold, pred):
        cm[idx[g]][idx[p]] += 1

    precision, recall, f1 = {}, {}, {}
    support_gold, support_pred = {}, {}
    for c in CLASSES:
        i = idx[c]
        tp = cm[i][i]
        fp = sum(cm[r][i] for r in range(len(CLASSES))) - tp
        fn = sum(cm[i][r] for r in range(len(CLASSES))) - tp
        p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
        precision[c] = round(p, 4)
        recall[c] = round(r, 4)
        f1[c] = round(f, 4)
        support_gold[c] = int(sum(cm[i]))
        support_pred[c] = int(sum(cm[r][i] for r in range(len(CLASSES))))

    # Macro-F1 follows the scikit-learn convention: averaged over the classes
    # that occur in gold and/or predictions. A class absent from both (e.g.
    # 'neutral' for harga/kemasan/pelayanan in this hold-out) is undefined,
    # not zero - otherwise even a perfect predictor could not reach 1.0.
    included = [c for c in CLASSES if support_gold[c] > 0 or support_pred[c] > 0]
    macro_f1 = round(sum(f1[c] for c in included) / len(included), 4) if included else 0.0
    return {
        "precision_per_class": precision,
        "recall_per_class": recall,
        "f1_per_class": f1,
        "macro_f1": macro_f1,
        "macro_f1_classes": included,
        "macro_f1_note": (
            "Macro-F1 averaged over classes present in gold and/or predictions "
            "(scikit-learn convention); classes absent from both are excluded."
        ),
        "confusion_matrix": cm,
        "class_order": CLASSES,
        "support_gold": support_gold,
        "support_pred": support_pred,
    }


def evaluate(gold_by_id: dict, pred_by_id: dict, holdout_ids: list) -> dict:
    per_aspect = {}
    for aspect in ASPECTS:
        gold = [gold_by_id[i][aspect] for i in holdout_ids]
        pred = [pred_by_id[i][aspect] for i in holdout_ids]
        per_aspect[aspect] = per_aspect_metrics(gold, pred)
    overall = round(sum(per_aspect[a]["macro_f1"] for a in ASPECTS) / len(ASPECTS), 4)
    return {"per_aspect": per_aspect, "overall_macro_f1": overall}


def lexicon_predictions(df_holdout: pd.DataFrame) -> dict:
    from src.absa_pipeline import ABSAPipeline

    pipe = ABSAPipeline()
    preds = {}
    for row in df_holdout.itertuples():
        res = pipe.analyze_single_review(str(row.review_text))
        preds[int(row.review_id)] = {
            a: res["aspects"][a]["sentiment"] for a in ASPECTS
        }
    return preds


def csv_predictions(path: Path, holdout_ids: list) -> dict:
    df = pd.read_csv(path)
    missing_cols = [c for c in ["review_id"] + ASPECTS if c not in df.columns]
    if missing_cols:
        raise SystemExit(f"ERROR: predictions file missing columns: {missing_cols}")
    preds = {}
    for row in df.itertuples():
        rid = int(row.review_id)
        vals = {}
        for a in ASPECTS:
            v = str(getattr(row, a)).strip().lower()
            if v not in CLASSES:
                raise SystemExit(f"ERROR: invalid label '{v}' for review {rid}, aspect {a}.")
            vals[a] = v
        preds[rid] = vals
    missing_ids = [i for i in holdout_ids if i not in preds]
    if missing_ids:
        raise SystemExit(f"ERROR: predictions file lacks hold-out ids: {missing_ids}")
    return preds


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--predictions", type=str, default=None,
                    help="CSV of predictions (review_id + 5 aspect columns).")
    ap.add_argument("--model-name", type=str, default=None,
                    help="Name for the results section (predictions mode).")
    args = ap.parse_args()

    holdout = json.loads(HOLDOUT_PATH.read_text(encoding="utf-8"))
    holdout_ids = [int(i) for i in holdout["review_ids"]]

    df = pd.read_csv(CSV_PATH)
    df_holdout = df[df["review_id"].isin(holdout_ids)].copy()
    if len(df_holdout) != len(holdout_ids):
        raise SystemExit("ERROR: some hold-out ids are missing from the dataset CSV.")
    gold_by_id = {
        int(r.review_id): {a: str(getattr(r, a)).strip().lower() for a in ASPECTS}
        for r in df_holdout.itertuples()
    }

    if args.predictions:
        pred_path = Path(args.predictions)
        model_name = args.model_name or pred_path.stem
        pred_by_id = csv_predictions(pred_path, holdout_ids)
        section = evaluate(gold_by_id, pred_by_id, holdout_ids)
        section["source"] = f"predictions file: {pred_path.name}"
    else:
        model_name = "lexicon_baseline"
        pred_by_id = lexicon_predictions(df_holdout)
        section = evaluate(gold_by_id, pred_by_id, holdout_ids)
        section["source"] = "src.absa_pipeline.ABSAPipeline (lexicon/keyword)"
        section["caveat"] = LEXICON_CAVEAT

    if OUT_PATH.exists():
        out = json.loads(OUT_PATH.read_text(encoding="utf-8"))
        out.setdefault("results", {})
    else:
        out = {"results": {}}
    out["generated_at"] = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    out["holdout"] = {
        "n": len(holdout_ids),
        "seed": holdout.get("seed"),
        "ids_file": "data/holdout_ids.json",
    }
    out["results"][model_name] = section
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Model: {model_name}")
    for a in ASPECTS:
        print(f"  {a:<10} Macro-F1 = {section['per_aspect'][a]['macro_f1']:.4f}")
    print(f"  OVERALL Macro-F1 = {section['overall_macro_f1']:.4f}")
    print(f"Wrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
