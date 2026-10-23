"""Rekam / verifikasi baseline angka UlasRasa (Tahap 0 PRD Implementasi UI).

Menghitung KHS + skor per aspek untuk 5 konteks (4 resto + benchmark) lewat
jalur yang sama seperti aplikasi: dataset bawaan -> filter per resto ->
pipeline.evaluate_dataframe(). Engine dimuat dengan urutan yang sama persis
seperti load_ai_engines() di app (lexicon dulu, transformer dicoba).

CATATAN KONTEKS (terverifikasi 2026-10-23): pipeline transformer memakai
torch; di shell non-interaktif Windows, impor torch bisa gagal dengan
OSError WinError 1114 (c10.dll) bila torch dimuat SEBELUM pandas/numpy
menyentuh runtime MSVC lebih dulu. Di aplikasi nyata urutannya aman karena
app.py mengimpor pandas lebih dulu. Script ini meniru urutan impor app.py:
pandas/numpy lebih dulu, baru engine. Kegagalan muat transformer kini
DICATAT (bukan ditelan) dan mode `record` MENOLAK menulis baseline bila
engine aktif bukan engine yang sama seperti aplikasi (IndoBERT).

Mode:
  py record_baseline.py record   -> tulis baseline.json
  py record_baseline.py verify   -> hitung ulang, bandingkan ke baseline.json
"""
import json
import os
import sys
import hashlib

# Urutan impor meniru app.py: pandas/numpy SEBELUM engine/torch.
import pandas as pd
import numpy as np  # noqa: F401  (memuat runtime lebih dulu, seperti app.py)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from src.absa_pipeline import ABSAPipeline
from src.config import HEALTH_THRESHOLDS

OUT = os.path.join(ROOT, "docs", "ui-evidence", "baseline.json")
EXPECTED_ENGINE_PREFIX = "IndoBERT"


def load_engine():
    engine = ABSAPipeline()
    label = "Lexicon (fallback)"
    load_error = None
    try:
        from src.models.transformer_engine import TransformerABSAPipeline
        engine = TransformerABSAPipeline()
        label = getattr(engine, "engine_name", "IndoBERT (fine-tuned)")
    except Exception as e:  # dicatat, tidak ditelan
        load_error = f"{type(e).__name__}: {e}"
    return engine, label, load_error


def status_of(khs):
    if khs >= HEALTH_THRESHOLDS["PRIMA"]:
        return "PRIMA (Optimal)"
    if khs >= HEALTH_THRESHOLDS["WASPADA"]:
        return "WASPADA (Perhatian)"
    return "KRITIS (Audit Segera)"


def compute():
    engine, label, load_error = load_engine()
    df = pd.read_csv(os.path.join(ROOT, "data", "sample_reviews.csv"))
    restos = sorted(df["restaurant_name"].unique().tolist())
    contexts = {}
    plan = [("benchmark_semua_outlet", df.copy())]
    for r in restos:
        plan.append((r, df[df["restaurant_name"] == r].copy()))
    for name, sub in plan:
        ev = engine.evaluate_dataframe(sub)
        khs = float(ev.get("kitchen_health_score", 0.0))
        breakdown = ev.get("aspect_breakdown", {})
        weakest = min(breakdown.items(), key=lambda x: x[1].get("satisfaction_score", 100.0))[0] if breakdown else None
        contexts[name] = {
            "n_reviews": int(len(sub)),
            "khs": khs,
            "khs_2dp": round(khs, 2),
            "status_label": status_of(khs),
            "weakest_aspect": weakest,
            "weakest_score": float(breakdown[weakest]["satisfaction_score"]) if weakest else None,
            "aspects": {
                k: {
                    "satisfaction_score": float(v["satisfaction_score"]),
                    "total_mentioned": int(v["total_mentioned"]),
                    "positive": int(v["positive"]),
                    "neutral": int(v["neutral"]),
                    "negative": int(v["negative"]),
                    "negative_rate": float(v["negative_rate"]),
                }
                for k, v in breakdown.items()
            },
        }
    with open(os.path.join(ROOT, "app.py"), "rb") as f:
        app_hash = hashlib.sha256(f.read()).hexdigest()
    return {"engine_label": label, "engine_load_error": load_error,
            "app_py_sha256": app_hash, "contexts": contexts}


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "record"
    data = compute()
    if mode == "record":
        if not data["engine_label"].startswith(EXPECTED_ENGINE_PREFIX):
            print(f"RECORD DITOLAK: engine aktif '{data['engine_label']}' bukan engine aplikasi "
                  f"({EXPECTED_ENGINE_PREFIX}...). load_error={data['engine_load_error']}")
            sys.exit(2)
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"BASELINE RECORDED engine={data['engine_label']} sha={data['app_py_sha256'][:12]}")
        for name, c in data["contexts"].items():
            print(f"  {name}: n={c['n_reviews']} KHS={c['khs_2dp']} status={c['status_label']} weakest={c['weakest_aspect']} {c['weakest_score']}")
        return
    # verify
    with open(OUT, encoding="utf-8") as f:
        base = json.load(f)
    if data["engine_label"] != base["engine_label"]:
        print(f"PARITAS: GAGAL - engine beda: baseline={base['engine_label']} now={data['engine_label']} load_error={data['engine_load_error']}")
        sys.exit(1)
    ok = True
    for name, bc in base["contexts"].items():
        nc = data["contexts"].get(name)
        if nc is None:
            print(f"MISSING CONTEXT {name}"); ok = False; continue
        same = (round(nc["khs"], 2) == bc["khs_2dp"] and nc["status_label"] == bc["status_label"]
                and nc["weakest_aspect"] == bc["weakest_aspect"] and nc["n_reviews"] == bc["n_reviews"])
        for ak, av in bc["aspects"].items():
            nv = nc["aspects"].get(ak, {})
            if round(float(nv.get("satisfaction_score", -1)), 2) != round(av["satisfaction_score"], 2):
                same = False
            for kk in ("total_mentioned", "positive", "neutral", "negative"):
                if nv.get(kk) != av[kk]:
                    same = False
        print(f"  {name}: KHS base={bc['khs_2dp']} now={round(nc['khs'],2)} -> {'IDENTIK' if same else 'BEDA!'}")
        ok = ok and same
    print("PARITAS: LULUS" if ok else "PARITAS: GAGAL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
