"""
train_absa.py - Fine-tune IndoBERT (Lite/Base) untuk ABSA UlasRasa.

Formulasi (keputusan terkunci):
  input  = pasangan (teks ulasan sebagai segmen pertama, nama aspek sebagai text_pair)
  output = 4 kelas: 0=not_mentioned, 1=positive, 2=neutral, 3=negative

Data: training/train_pairs.csv (sudah di-subsample oleh prepare_pairs.py,
      dijamin bebas hold-out).
Validasi internal: 15% dari train_pairs, stratifikasi label, seed 42.
Loss: weighted CrossEntropy (class weight dari distribusi train penuh).
Early stopping pada Macro-F1 validasi (patience 2, maks 5 epoch).

Pakai:
  python train_absa.py --base lite --output ..\\models\\indobert-lite-absa
  python train_absa.py --base base --output ..\\models\\indobert-base-absa
"""

import argparse
import json
import os
import time

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    EarlyStoppingCallback,
    Trainer,
    TrainingArguments,
)

LABEL2ID = {"not_mentioned": 0, "positive": 1, "neutral": 2, "negative": 3}
ID2LABEL = {v: k for k, v in LABEL2ID.items()}
BASE_MODELS = {
    "lite": "indobenchmark/indobert-lite-base-p1",
    "base": "indobenchmark/indobert-base-p1",
}
MAX_LEN = 128
SEED = 42

HERE = os.path.dirname(os.path.abspath(__file__))
PAIRS_CSV = os.path.join(HERE, "train_pairs.csv")


class PairDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {k: torch.tensor(v[idx]) for k, v in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item


class WeightedTrainer(Trainer):
    def __init__(self, *args, class_weights=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_weights = class_weights

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits
        loss_fct = torch.nn.CrossEntropyLoss(
            weight=self.class_weights.to(logits.device) if self.class_weights is not None else None
        )
        loss = loss_fct(logits.view(-1, model.config.num_labels), labels.view(-1))
        return (loss, outputs) if return_outputs else loss


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {"macro_f1": f1_score(labels, preds, average="macro", zero_division=0)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", choices=["lite", "base"], required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    t0 = time.time()
    base_model = BASE_MODELS[args.base]
    is_lite = args.base == "lite"
    lr = 3e-5 if is_lite else 2e-5
    batch = 16 if is_lite else 8

    df = pd.read_csv(PAIRS_CSV)
    df["label_id"] = df["label"].map(LABEL2ID)
    assert df["label_id"].notna().all(), "label tidak dikenal di train_pairs.csv"

    train_df, val_df = train_test_split(
        df, test_size=0.15, random_state=SEED, stratify=df["label_id"]
    )
    print(f"train_pairs total={len(df)} train={len(train_df)} val={len(val_df)}")

    # Class weight dari distribusi train_pairs penuh (sesudah subsample)
    counts = df["label_id"].value_counts().sort_index()
    total = len(df)
    weights = torch.tensor(
        [total / (len(LABEL2ID) * counts.get(i, 1)) for i in range(len(LABEL2ID))],
        dtype=torch.float,
    )
    print("class counts:", counts.to_dict())
    print("class weights:", weights.tolist())

    tokenizer = AutoTokenizer.from_pretrained(base_model)

    def encode(frame):
        return tokenizer(
            frame["text"].astype(str).tolist(),
            frame["aspect"].astype(str).tolist(),
            truncation=True,
            max_length=MAX_LEN,
            padding="max_length",
        )

    train_ds = PairDataset(encode(train_df), train_df["label_id"].tolist())
    val_ds = PairDataset(encode(val_df), val_df["label_id"].tolist())

    model = AutoModelForSequenceClassification.from_pretrained(
        base_model, num_labels=4, id2label=ID2LABEL, label2id=LABEL2ID
    )

    targs = TrainingArguments(
        output_dir=args.output + "_ckpt",
        per_device_train_batch_size=batch,
        per_device_eval_batch_size=batch,
        learning_rate=lr,
        num_train_epochs=5,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="macro_f1",
        greater_is_better=True,
        seed=SEED,
        data_seed=SEED,
        fp16=torch.cuda.is_available(),
        logging_steps=10,
        report_to=[],
        save_total_limit=2,
    )

    trainer = WeightedTrainer(
        model=model,
        args=targs,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        compute_metrics=compute_metrics,
        class_weights=weights,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],
    )
    trainer.train()
    eval_res = trainer.evaluate()
    trainer.save_model(args.output)
    tokenizer.save_pretrained(args.output)

    wall = time.time() - t0
    log = {
        "base_variant": args.base,
        "base_model": base_model,
        "output_dir": args.output,
        "max_len": MAX_LEN,
        "lr": lr,
        "batch": batch,
        "seed": SEED,
        "n_pairs_total": int(len(df)),
        "n_train": int(len(train_df)),
        "n_val": int(len(val_df)),
        "class_counts": {str(k): int(v) for k, v in counts.to_dict().items()},
        "class_weights": weights.tolist(),
        "val_macro_f1_best": float(eval_res.get("eval_macro_f1", 0.0)),
        "epochs_trained": float(trainer.state.epoch or 0),
        "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
        "wall_time_sec": round(wall, 1),
    }
    with open(os.path.join(args.output, "training_log.json"), "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)
    print(json.dumps(log, indent=2))
    print(f"DONE base={args.base} wall={wall:.0f}s")


if __name__ == "__main__":
    main()
