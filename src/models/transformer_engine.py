"""Engine ABSA berbasis transformer: IndoBERT Base hasil fine-tune lokal.

Kelas TransformerABSAPipeline adalah pengganti drop-in untuk
src.absa_pipeline.ABSAPipeline (lexicon): interface dan bentuk keluaran
analyze_single_review() serta evaluate_dataframe() identik, termasuk
rumus satisfaction_score per aspek dan Kitchen Health Score (KHS),
sehingga angka antar engine selalu dapat dibandingkan.

Format inferensi mereplikasi persis format saat fine-tuning dan evaluasi
hold-out (training/predict_holdout.py):
- segmen pertama = teks ulasan mentah (tanpa cleaning; tokenizer BERT
  menangani teks apa adanya, sama seperti saat training),
- text_pair = nama aspek huruf kecil ("rasa", "porsi", "harga",
  "kemasan", "pelayanan"),
- max_len 128, label id: 0=not_mentioned, 1=positive, 2=neutral,
  3=negative (dibaca dari config model bila tersedia).

confidence adalah probabilitas softmax kelas terpilih dari model
(probabilitas model yang sesungguhnya, bukan heuristik).

Model dimuat secara lazy: mengimpor modul ini tidak memuat model.
Konstruktor melempar FileNotFoundError bila tidak ada sumber model yang
tersedia dan RuntimeError bila pemuatan gagal, agar pemanggil (app.py)
dapat jatuh kembali ke engine lexicon.

Sumber model dipilih dengan urutan prioritas:
(a) argumen model_path / env ULASRASA_MODEL_PATH (folder lokal eksplisit),
(b) folder lokal bawaan models/indobert-base-absa bila ada,
(c) env ULASRASA_MODEL_REPO: repo id Hugging Face Hub (dipakai di
    HF Spaces, tempat folder model lokal tidak ikut ter-deploy),
(d) tidak ada yang tersedia -> FileNotFoundError.
"""

import os
from typing import Dict, List, Any

import pandas as pd

from ..absa_pipeline import DEFAULT_WEIGHTS
from ..preprocessing import clean_text

ASPECTS = ["rasa", "porsi", "harga", "kemasan", "pelayanan"]
FALLBACK_ID2LABEL = {0: "not_mentioned", 1: "positive", 2: "neutral", 3: "negative"}
MAX_LEN = 128

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_MODEL_PATH = os.path.join(_REPO_ROOT, "models", "indobert-base-absa")


def _resolve_model_source(model_path: str = None):
    """Menentukan sumber model: mengembalikan (sumber, is_local_dir).

    Urutan prioritas: (a) argumen / env ULASRASA_MODEL_PATH, (b) folder
    lokal bawaan, (c) env ULASRASA_MODEL_REPO (repo id HF Hub). Melempar
    FileNotFoundError bila tidak ada sumber yang tersedia, atau bila
    path eksplisit pada (a) menunjuk folder yang tidak ada.
    """
    explicit = model_path or os.getenv("ULASRASA_MODEL_PATH")
    if explicit:
        if not os.path.isdir(explicit):
            raise FileNotFoundError(
                f"Folder model IndoBERT fine-tuned tidak ditemukan: {explicit}"
            )
        return explicit, True
    if os.path.isdir(DEFAULT_MODEL_PATH):
        return DEFAULT_MODEL_PATH, True
    repo_id = os.getenv("ULASRASA_MODEL_REPO")
    if repo_id:
        return repo_id, False
    raise FileNotFoundError(
        "Model IndoBERT fine-tuned tidak tersedia: folder lokal "
        f"{DEFAULT_MODEL_PATH} tidak ada, ULASRASA_MODEL_PATH tidak di-set, "
        "dan ULASRASA_MODEL_REPO (repo id HF Hub) juga tidak di-set."
    )


class TransformerABSAPipeline:
    """Mesin inferensi ABSA 5 aspek berbasis IndoBERT fine-tuned."""

    engine_name = "IndoBERT (fine-tuned)"

    def __init__(self, model_path: str = None):
        self.model_path, self.model_is_local = _resolve_model_source(model_path)
        self.aspects = list(ASPECTS)
        self.weights = DEFAULT_WEIGHTS
        self._tokenizer = None
        self._model = None
        self._id2label = dict(FALLBACK_ID2LABEL)
        self._load_model()

    @classmethod
    def is_available(cls, model_path: str = None) -> bool:
        """Cek murah (tanpa memuat model) apakah ada sumber model tersedia."""
        try:
            _resolve_model_source(model_path)
            return True
        except FileNotFoundError:
            return False

    def _load_model(self) -> None:
        try:
            import torch
            from transformers import AutoModelForSequenceClassification, AutoTokenizer
        except Exception as exc:  # pragma: no cover - dependensi hilang
            raise RuntimeError(f"Dependensi transformer tidak tersedia: {exc}") from exc

        try:
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self._model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
            self._model.to("cpu")
            self._model.eval()
        except Exception as exc:
            raise RuntimeError(
                f"Gagal memuat model IndoBERT dari {self.model_path}: {exc}"
            ) from exc

        self._torch = torch
        raw_id2label = getattr(self._model.config, "id2label", None) or {}
        parsed = {}
        for key, value in raw_id2label.items():
            try:
                parsed[int(key)] = str(value)
            except (TypeError, ValueError):
                continue
        if parsed:
            self._id2label = parsed

    # ------------------------------------------------------------------
    # Inferensi inti: satu ulasan x 5 aspek dalam satu batch
    # ------------------------------------------------------------------
    def _predict_aspects(self, raw_text: str) -> Dict[str, Dict[str, Any]]:
        torch = self._torch
        texts = [raw_text] * len(self.aspects)
        enc = self._tokenizer(
            texts,
            self.aspects,
            truncation=True,
            max_length=MAX_LEN,
            padding=True,
            return_tensors="pt",
        )
        with torch.no_grad():
            logits = self._model(**enc).logits
            probs = torch.softmax(logits, dim=-1)

        results: Dict[str, Dict[str, Any]] = {}
        for idx, aspect in enumerate(self.aspects):
            row = probs[idx]
            label_id = int(torch.argmax(row).item())
            sentiment = self._id2label.get(label_id, "not_mentioned")
            results[aspect] = {
                "mentioned": sentiment != "not_mentioned",
                "sentiment": sentiment,
                "confidence": float(row[label_id].item()),
            }
        return results

    # ------------------------------------------------------------------
    # Interface kompatibel ABSAPipeline
    # ------------------------------------------------------------------
    def analyze_single_review(self, raw_text: str) -> Dict[str, Any]:
        """Menganalisis teks ulasan tunggal ke dalam 5 aspek (IndoBERT)."""
        raw_text = "" if raw_text is None else str(raw_text)
        return {
            "original_text": raw_text,
            "cleaned_text": clean_text(raw_text),
            "aspects": self._predict_aspects(raw_text),
        }

    def evaluate_dataframe(self, df: pd.DataFrame, progress_callback=None) -> Dict[str, Any]:
        """
        Menghitung metrik kepuasan dan Kitchen Health Score.

        Logika agregasi identik dengan ABSAPipeline.evaluate_dataframe
        agar KHS antar engine konsisten: dataframe beranotasi lengkap
        dipakai apa adanya; dataframe berisi 'review_text' mentah
        diinferensi on-the-fly per baris.
        """
        eval_df = df.copy()

        aspects_present = all(asp in eval_df.columns for asp in self.aspects)

        if not aspects_present and "review_text" in eval_df.columns:
            total_rows = len(eval_df)
            inferred_aspects = {asp: [] for asp in self.aspects}

            for i, text in enumerate(eval_df["review_text"]):
                res = self.analyze_single_review(str(text))
                for asp in self.aspects:
                    inferred_aspects[asp].append(res["aspects"][asp]["sentiment"])
                if progress_callback:
                    progress_callback((i + 1) / total_rows)

            for asp in self.aspects:
                eval_df[asp] = inferred_aspects[asp]

        aspect_summary = {}
        total_reviews = len(eval_df)

        for aspect in self.aspects:
            if aspect not in eval_df.columns:
                series = pd.Series(["not_mentioned"] * total_reviews)
            else:
                series = eval_df[aspect].astype(str).str.lower()

            pos = int((series == "positive").sum())
            neu = int((series == "neutral").sum())
            neg = int((series == "negative").sum())
            total_mentioned = pos + neu + neg

            if total_mentioned > 0:
                score = (pos + (0.5 * neu)) / total_mentioned * 100.0
            else:
                score = 100.0

            aspect_summary[aspect] = {
                "positive": pos,
                "neutral": neu,
                "negative": neg,
                "total_mentioned": total_mentioned,
                "satisfaction_score": round(float(score), 2),
                "negative_rate": round(float(neg / total_mentioned * 100.0), 2) if total_mentioned > 0 else 0.0,
            }

        khs = 0.0
        for aspect, weight in self.weights.items():
            aspect_score = aspect_summary.get(aspect, {}).get("satisfaction_score", 100.0)
            khs += weight * aspect_score

        return {
            "total_reviews": total_reviews,
            "kitchen_health_score": round(float(khs), 2),
            "aspect_breakdown": aspect_summary,
            "evaluated_df": eval_df,
        }
