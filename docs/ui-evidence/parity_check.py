"""Pembuktian checklist paritas 44 butir PRD (Tahap 6).

Pemeriksaan programatis untuk kelompok P-D / P-E / P-N / P-M / P-X /
P-G; hasil per butir PASS / FAIL / INSPEKSI beserta buktinya. Butir
perilaku UI murni dibuktikan lewat screenshot + journey Tahap 6 dan
di sini ditandai INSPEKSI dengan petunjuk buktinya.

Jalankan dari root repo:  py docs/ui-evidence/parity_check.py
Urutan impor meniru app.py: pandas/numpy sebelum engine (torch).

Adaptasi revisi landing (2026-10-23, branch revisi-landing): app kini
berpintu landing akun demo - dashboard hanya render bila
session_state["active_account"] terisi. run_module() di bawah menyetel
active_account = RESTO (konteks yang memang diasumsikan seluruh skrip
ini sejak awal) sebelum run. TIDAK ADA butir, angka, atau bukti yang
diubah - hanya cara harness masuk ke dashboard yang disesuaikan dengan
alur UI baru.
"""
import ast
import hashlib
import io
import json
import os
import re
import subprocess
import sys

import pandas as pd
import numpy as np  # noqa: F401

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "docs", "ui-evidence"))

RESULTS = []


def report(item, status, evidence):
    RESULTS.append((item, status, evidence))
    print(f"[{status:8s}] {item}: {evidence}", flush=True)


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def git_show(spec):
    return subprocess.run(["git", "show", spec], capture_output=True, text=True,
                          encoding="utf-8").stdout


# ---------------------------------------------------------------- konteks
import record_baseline  # noqa: E402

BASE = json.loads(read("docs/ui-evidence/baseline.json"))
NOW = record_baseline.compute()
ENGINE_OK = NOW["engine_label"] == BASE["engine_label"] and NOW["engine_label"].startswith("IndoBERT")

from src.ui import core, labels, charts  # noqa: E402
from src.config import ASPECT_WEIGHTS, HEALTH_THRESHOLDS  # noqa: E402

pipeline, action_engine, engine_label = core.load_ai_engines()
default_df = core.load_default_dataset()
RESTO = "Ayam Geprek Sambal Korek Barokah"
_fdf = default_df[default_df["restaurant_name"] == RESTO].copy()
CTX = dict(core.compute_context(_fdf, pipeline))
CTX.update({"filtered_df": _fdf, "selected_resto": RESTO})
# Konstruksi plan meniru persis module_rencana.render (urutan aspek +
# maks 3 teks negatif per aspek), karena helper-nya lokal di render().
_sample_complaints = {}
for _asp in ["kemasan", "rasa", "porsi", "harga", "pelayanan"]:
    if _asp in _fdf.columns:
        _negs = _fdf[_fdf[_asp] == "negative"]["review_text"].tolist()
        if _negs:
            _sample_complaints[_asp] = [str(t) for t in _negs[:3]]
PLAN = action_engine.generate_action_plan(
    restaurant_name=RESTO,
    evaluation_results=CTX["eval_results"],
    sample_complaints=_sample_complaints,
)

# ---------------------------------------------------------------- P-D
report("P-D1 engine label IndoBERT", "PASS" if ENGINE_OK else "FAIL",
       f"engine sekarang={NOW['engine_label']} baseline={BASE['engine_label']}")

num_ok, det = True, []
for name, bc in BASE["contexts"].items():
    nc = NOW["contexts"].get(name)
    if nc is None:
        num_ok = False
        det.append(f"{name}: HILANG")
        continue
    same = round(nc["khs"], 2) == bc["khs_2dp"] and nc["n_reviews"] == bc["n_reviews"]
    num_ok = num_ok and same
    det.append(f"{name} KHS {bc['khs_2dp']}->{round(nc['khs'], 2)}")
report("P-D2 KHS 5 konteks identik", "PASS" if num_ok else "FAIL", "; ".join(det))

asp_ok = True
for name, bc in BASE["contexts"].items():
    nc = NOW["contexts"][name]
    for ak, av in bc["aspects"].items():
        nv = nc["aspects"].get(ak, {})
        if round(float(nv.get("satisfaction_score", -1)), 2) != round(av["satisfaction_score"], 2):
            asp_ok = False
report("P-D3 skor per aspek 5 konteks identik", "PASS" if asp_ok else "FAIL",
       "25 skor aspek dibandingkan pada 2 desimal")

brk_ok = True
for name, bc in BASE["contexts"].items():
    nc = NOW["contexts"][name]
    for ak, av in bc["aspects"].items():
        nv = nc["aspects"].get(ak, {})
        for kk in ("total_mentioned", "positive", "neutral", "negative"):
            if nv.get(kk) != av[kk]:
                brk_ok = False
report("P-D4 breakdown counts identik", "PASS" if brk_ok else "FAIL",
       "total/pos/neu/neg per aspek per konteks sama persis")

from src.ui import components  # noqa: E402


def _csv_bytes(rows, header="review_text,restaurant_name"):
    return ("\n".join([header] + rows)).encode("utf-8")


class _U(io.BytesIO):
    def __init__(self, data, name):
        super().__init__(data)
        self.name = name


r_big = components._process_upload(_U(_csv_bytes([f"ulasan ke-{i},Resto Uji" for i in range(201)]), "big.csv"))
r_miss = components._process_upload(_U(_csv_bytes(["satu,Resto Uji"], header="teks,restaurant_name"), "miss.csv"))
r_good = components._process_upload(_U(_csv_bytes(
    ["enak sekali,Resto Uji", "porsi kecil,Resto Uji", "mantap,Resto Uji"]), "good.csv"))
r_weird = components._process_upload(_U(b"apapun", "aneh.xyz"))
d5 = (r_big[0] is None and r_big[2] and "201" in r_big[2][0][1] and "200" in r_big[2][0][1]
      and r_miss[0] is None and "review_text" in r_miss[2][0][1]
      and r_good[0] is not None and len(r_good[0]) == 3 and r_good[1] == "Resto Uji"
      and r_weird[0] is None and labels.DATA_MODES == ["Outlet Bawaan (Preset)",
                                                       "Upload Dataset Real (CSV)"])
report("P-D5 penjaga unggah (201 baris ditolak, kolom wajib, format)", "PASS" if d5 else "FAIL",
       f"201 baris -> {r_big[2][0][1][:40]}...; kolom hilang -> {r_miss[2][0][1]}; "
       f"valid -> resto {r_good[1]}; mode data={labels.DATA_MODES} (sama seperti app lama)")

app_src = read("app.py")
comp_src = read("src/ui/components.py")
d6 = ("BTN_GANTI_DATA" in comp_src and "ui_panel_open" in comp_src
      and "PANEL_DATA_TITLE" in comp_src and "st.file_uploader" in comp_src)
report("P-D6 tombol Ganti Data + PanelData terpasang", "PASS" if d6 else "FAIL",
       "components.py: tombol BTN_GANTI_DATA + panel inline (ui_panel_open, PANEL_DATA_TITLE, file_uploader); "
       "buka panel dibuktikan journey Tahap 6")

ds_diff = subprocess.run(["git", "diff", "461e646", "--", "data/sample_reviews.csv"],
                         capture_output=True, text=True).stdout.strip()
ds_sha = hashlib.sha256(open(os.path.join(ROOT, "data", "sample_reviews.csv"), "rb").read()).hexdigest()
report("P-D7 dataset tidak berubah sejak 461e646", "PASS" if ds_diff == "" else "FAIL",
       f"git diff dataset kosong; sha256 sekarang={ds_sha[:16]}")

restos = sorted(default_df["restaurant_name"].unique().tolist())
d8 = restos == ["Ayam Geprek Sambal Korek Barokah", "Bakso Rusuk Solo Pak Ndut",
                "Bebek Goreng Madura Cak Roni", "Kopi Susu Senja & Toast"] \
    and "st.sidebar" not in app_src
report("P-D8 dataset bawaan 4 resto + tanpa sidebar", "PASS" if d8 else "FAIL",
       f"resto={restos}; st.sidebar di app.py: {'st.sidebar' in app_src}")

core_src = read("src/ui/core.py")
ren_src = read("src/ui/module_rencana.py")
coba_src = read("src/ui/module_coba.py")
d9 = all(k in core_src for k in ("custom_reviews_df", "custom_checklist_items", "active_module_name",
                                 "simulator_text", "rincian_aspect")) \
    and "action_chk_" in ren_src and "sim_input" in coba_src and "sim_res" in coba_src
report("P-D9 kunci sesi dipertahankan", "PASS" if d9 else "FAIL",
       "init_session_state (5 kunci) + pola action_chk_<resto>_<idx> + sim_input/sim_res")

# ---------------------------------------------------------------- P-E
report("P-E1 caption Engine ABSA IndoBERT", "PASS" if engine_label == "IndoBERT (fine-tuned)" else "FAIL",
       f"engine_label app={engine_label}")
e2 = isinstance(PLAN, dict) and "generation_mode" in PLAN and "llm_provider" in PLAN \
    and "Mode rekomendasi:" in ren_src
report("P-E2 mode rekomendasi + cip di modul", "PASS" if e2 else "FAIL",
       f"generation_mode={PLAN.get('generation_mode')} llm_provider={PLAN.get('llm_provider')}")
report("P-E3 jalur pipeline sama (transformer)", "PASS" if pipeline.__class__.__name__ == "TransformerABSAPipeline" else "FAIL",
       f"kelas pipeline={pipeline.__class__.__name__}")

ev_all = pipeline.evaluate_dataframe(default_df)
rank_keys = [k for k in ev_all.keys() if "rank" in k.lower() or "restaurant" in k.lower()]
if rank_keys:
    rk = rank_keys[0]
    seq = ev_all[rk]
    try:
        vals = [float(x.get("weighted_khs_score", x.get("khs", 0))) for x in seq]
        e4 = all(vals[i] >= vals[i + 1] - 1e-9 for i in range(len(vals) - 1))
        ev4 = f"kunci {rk}: { [round(v, 2) for v in vals] }"
    except Exception as ex:
        e4, ev4 = False, f"struktur {rk} tak terduga: {ex}"
else:
    e4, ev4 = "INSPEKSI", f"eval_results tanpa kunci ranking (keys={sorted(ev_all.keys())}); angka ranking = KHS per resto (P-D2)"
report("P-E4 ranking resto terurut skor menurun", "PASS" if e4 is True else ("INSPEKSI" if e4 == "INSPEKSI" else "FAIL"), ev4)

diff = subprocess.run(["git", "diff", "461e646", "--", "src/absa_pipeline.py",
                       "src/models/transformer_engine.py", "src/action_engine.py",
                       "src/config.py", "src/preprocessing.py", "src/utils/exporter.py",
                       "data/sample_reviews.csv"],
                      capture_output=True, text=True).stdout.strip()
report("P-E5 file logika non-UI tidak berubah vs 461e646", "PASS" if diff == "" else "FAIL",
       f"git diff kosong: {diff == ''} ({len(diff)} char)")

# ---------------------------------------------------------------- P-N
ring_src = read("src/ui/module_ringkasan.py")
report("P-N1 KHS tampil 1 desimal + persen", "PASS" if "{khs:.1f}%" in ring_src else "FAIL",
       "KartuKPI + donat memakai format khs:.1f diikuti %")
report("P-N2 label Skor Kesehatan Dapur pada hero donat",
       "PASS" if labels.HERO_TITLE == "Skor Kesehatan Dapur" and "build_khs_donut_figure" in ring_src else "FAIL",
       "HERO_TITLE='Skor Kesehatan Dapur' menjadi judul kartu hero; tengah donat memuat nilai % "
       "(render Fase 1 yang disetujui user)")
thr_ok = True
for name, bc in BASE["contexts"].items():
    khs = bc["khs_2dp"]
    expect = ("PRIMA" if khs >= HEALTH_THRESHOLDS["PRIMA"]
              else "WASPADA" if khs >= HEALTH_THRESHOLDS["WASPADA"] else "KRITIS")
    if not bc["status_label"].startswith(expect):
        thr_ok = False
report("P-N3 ambang status konsisten aturan", "PASS" if thr_ok else "FAIL",
       f"thresholds={HEALTH_THRESHOLDS}; 5 status baseline konsisten")
n4 = ("satisfaction_score', 0.0)):.1f}%" in ring_src) and ("{neg_rate_w:.1f}%" in ring_src)
report("P-N4 format skor aspek + laju negatif 1 desimal", "PASS" if n4 else "FAIL",
       "rel-tabel skor '...:.1f}%' + kalimat keluhan '{neg_rate_w:.1f}%' di module_ringkasan")
recomputed = sum(CTX["breakdown"][a.lower()]["satisfaction_score"] * w
                 for a, w in ASPECT_WEIGHTS.items())
report("P-N5 KHS = rata-rata tertimbang skor aspek", "PASS" if abs(recomputed - CTX["khs"]) < 0.011 else "FAIL",
       f"hitung ulang={recomputed:.4f} ctx={CTX['khs']:.4f}")

# ---------------------------------------------------------------- AppTest
from streamlit.testing.v1 import AppTest  # noqa: E402

MOD_RINGKASAN = "Ringkasan Eksekutif & Health Score"
MOD_RINCIAN = "Deep-Dive Aspek & Sentimen"
MOD_RENCANA = "AI Kitchen Action Checklist"
MOD_COBA = "Single Review Simulator (Live Demo)"


def run_module(module_name, seed=None):
    at = AppTest.from_file(os.path.join(ROOT, "app.py"), default_timeout=600)
    at.session_state["active_module_name"] = module_name
    at.session_state["active_account"] = RESTO  # gerbang landing revisi 2026-10-23
    for k, v in (seed or {}).items():
        at.session_state[k] = v
    at.run(timeout=600)
    md = " ".join(str(getattr(m, "value", "")) for m in at.markdown)
    caps = " ".join(str(getattr(c, "value", "") or getattr(c, "body", "")) for c in at.caption)
    btns = [str(getattr(b, "label", "")) for b in at.button]
    return at, md, caps, btns


at_r, md_r, caps_r, btns_r = run_module(MOD_RINGKASAN)
m1 = (len(at_r.exception) == 0 and "Skor Kesehatan Dapur" in md_r and "Total Ulasan" in md_r
      and "Ulasan Negatif" in md_r and "Aspek Paling Kritis" in md_r
      and "Kepuasan per Aspek" in md_r and "Angka Rincian per Aspek" in md_r
      and any("Lihat di Rincian Aspek" in b for b in btns_r)
      and "Engine ABSA" in md_r and "IndoBERT (fine-tuned)" in md_r)
report("P-M1 Ringkasan utuh + cip engine", "PASS" if m1 else "FAIL",
       f"exception={len(at_r.exception)} tombol_rel={'Lihat di Rincian Aspek' in str(btns_r)} cip_engine={'Engine ABSA' in md_r}")
report("P-M14 sapaan Halo + status", "PASS" if ("Halo," in md_r and "Status saat ini:" in md_r) else "FAIL",
       "header sapaan ter-render di Ringkasan")
try:
    fab = [b for b in at_r.button if getattr(b, "key", "") == "ui_toggle_panel"][0]
    fab.click().run(timeout=600)
    radio = [r for r in at_r.radio if getattr(r, "key", "") == "ui_data_mode"][0]
    radio.set_value(labels.DATA_MODE_UPLOAD).run(timeout=600)
    n_up = len(at_r.file_uploader)
    m15 = n_up >= 1 and len(at_r.exception) == 0
    ev15 = f"klik Ganti Data -> panel terbuka; radio mode=Upload -> file_uploader={n_up}, exception={len(at_r.exception)}"
except Exception as ex:
    m15 = False
    ev15 = f"alur AppTest gagal: {type(ex).__name__}: {ex}"
report("P-M15 widget unggah CSV bisa dibuka", "PASS" if m15 else "FAIL", ev15)

at_i, md_i, caps_i, btns_i = run_module(MOD_RINCIAN)
bd_rasa = CTX["breakdown"]["rasa"]
m2 = (len(at_i.exception) == 0 and "Distribusi Sentimen" in md_i
      and "Komposisi Sentimen" in md_i and "Semua Ulasan" in md_i
      and "Menampilkan" in caps_i)
report("P-M2 Rincian utuh (donat, kata, komposisi, contoh, tabel)", "PASS" if m2 else "FAIL",
       f"exception={len(at_i.exception)} caption hitung={'Menampilkan' in caps_i}")
m3 = (f"<div class='stat-value'>{bd_rasa['total_mentioned']}</div>" in md_i
      and f"<div class='stat-value'>{bd_rasa['negative']}" in md_i)
report("P-M3 AngkaHitungAspek == breakdown rasa (konteks awal)", "PASS" if m3 else "FAIL",
       f"total={bd_rasa['total_mentioned']} pos={bd_rasa['positive']} neu={bd_rasa['neutral']} neg={bd_rasa['negative']}")

fig_c = charts.build_composition_figure(CTX["breakdown"])
order = labels.ASPECT_ORDER
comp_ok = True
for tr in fig_c.data:
    key = {"Positif": "positive", "Netral": "neutral", "Negatif": "negative"}[tr.name]
    if list(tr.y) != [CTX["breakdown"][a][key] for a in order]:
        comp_ok = False
report("P-M4 komposisi bertumpuk == breakdown", "PASS" if comp_ok else "FAIL",
       "3 seri x 5 aspek dibandingkan ke breakdown")


def stop_set_of(src):
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "stop_set" for t in node.targets):
            return {e.value for e in node.value.elts}
    return None


old_rin = git_show("b5ac28b:src/ui/module_rincian.py")
new_rin = read("src/ui/module_rincian.py")
ss_old, ss_new = stop_set_of(old_rin), stop_set_of(new_rin)
m5a = ss_old is not None and ss_old == ss_new
from collections import Counter  # noqa: E402
from src.preprocessing import clean_text  # noqa: E402

neg_texts = _fdf[_fdf["kemasan"] == "negative"]["review_text"].tolist()
words = []
for t in neg_texts:
    words.extend(w for w in clean_text(str(t)).split() if len(w) >= 3 and w not in ss_old)
top6 = Counter(words).most_common(6)
fig_k = charts.build_keyword_figure(top6, "#7C3AED")
m5 = m5a and list(fig_k.data[0].x) == [c for _, c in reversed(top6)]
report("P-M5 kata keluhan: stop_set identik + figur == Counter top-6", "PASS" if m5 else "FAIL",
       f"stop_set sama={m5a}; top6 kemasan={top6[:3]}...")

fig_d = charts.build_distribution_donut_figure(bd_rasa["positive"], bd_rasa["neutral"], bd_rasa["negative"])
m6 = list(fig_d.data[0].values) == [bd_rasa["positive"], bd_rasa["neutral"], bd_rasa["negative"]]
report("P-M6 donat distribusi == breakdown", "PASS" if m6 else "FAIL",
       f"values={list(fig_d.data[0].values)}")

at_a, md_a, caps_a, btns_a = run_module(MOD_RENCANA)
n_down = len(at_a.get("download_button"))
m7 = (len(at_a.exception) == 0 and "Kemajuan Daftar Aksi" in md_a and "aksi selesai" in md_a
      and "Akar Masalah" in md_a and "Daftar Aksi Dapur" in md_a
      and "Mode rekomendasi:" in md_a and n_down >= 3)
report("P-M7 Rencana utuh + progress + cip mode + 3 unduhan", "PASS" if m7 else "FAIL",
       f"exception={len(at_a.exception)} download_button={n_down}")
report("P-M9 SOP tampil", "PASS" if "Rekomendasi SOP Dapur" in md_a else "FAIL",
       "judul SOP ter-render di Rencana")

at_a2, md_a2, _, _ = run_module(MOD_RENCANA, seed={f"action_chk_{RESTO}_0": True})
m8 = "1 dari" in md_a2 and "aksi selesai" in md_a2 and len(at_a2.exception) == 0
report("P-M8 centang persisten -> progress berubah", "PASS" if m8 else "FAIL",
       f"kunci 'action_chk_{RESTO}_0'=True -> garis '1 dari N aksi selesai' ter-render: {m8}")

preset1 = ("Nasi gorengnya sangat wangi dan bumbunya meresap, enak banget! "
           "Sayangnya kemasannya bocor parah, minyak tumpah kemana-mana.")
at_c, md_c, caps_c, btns_c = run_module(MOD_COBA)
m11 = len(at_c.exception) == 0 and "Belum ada hasil" in md_c
report("P-M11 empty state Coba sebelum analisis", "PASS" if m11 else "FAIL",
       f"exception={len(at_c.exception)} empty-state={'Belum ada hasil' in md_c}")
try:
    at_c.session_state["sim_input"] = preset1
    btn = [b for b in at_c.button if getattr(b, "key", "") == "sim_analyze_btn"]
    if not btn:
        btn = [b for b in at_c.button if "Analisis" in str(getattr(b, "label", ""))]
    btn[0].click().run(timeout=600)
    md_c2 = " ".join(str(getattr(m, "value", "")) for m in at_c.markdown)
    m10 = (len(at_c.exception) == 0 and "Hasil Analisis" in md_c2 and "Rasa" in md_c2
           and "Kemasan" in md_c2 and "Tidak disebut:" in md_c2)
    ev10 = f"exception={len(at_c.exception)} hasil={'Hasil Analisis' in md_c2} tidak-disebut={'Tidak disebut:' in md_c2}"
except Exception as ex:
    m10, ev10 = False, f"harness klik gagal: {type(ex).__name__}: {ex}"
report("P-M10 hasil Coba: baris aspek + confidence + tindak lanjut", "PASS" if m10 else "FAIL", ev10)


def dict_literal(src, name):
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    return None


old_app = git_show("461e646:app.py")
m12 = dict_literal(old_app, "preset_texts") == dict_literal(coba_src, "PRESET_TEXTS") \
    and dict_literal(old_app, "preset_texts") is not None
report("P-M12 4 teks preset identik karakter per karakter", "PASS" if m12 else "FAIL",
       "preset_texts (lokal) app.py@461e646 vs PRESET_TEXTS module_coba via AST literal_eval")

old_ren = git_show("b5ac28b:src/ui/module_rencana.py")


def export_calls(src):
    out = {}
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id.startswith("export_action_plan"):
            out[node.func.id] = node
    return out


ec_old, ec_new = export_calls(old_ren), export_calls(ren_src)
txt_same = ast.dump(ec_old["export_action_plan_text"]) == ast.dump(ec_new["export_action_plan_text"])
po, pn = ec_old["export_action_plan_pdf"], ec_new["export_action_plan_pdf"]
kw_o = {k.arg: k.value for k in po.keywords}
kw_n = {k.arg: k.value for k in pn.keywords}
pdf_same = ([ast.dump(a) for a in po.args] == [ast.dump(a) for a in pn.args]
            and sorted(kw_o) == sorted(kw_n)
            and ast.dump(kw_o.get("action_items")) == ast.dump(kw_n.get("action_items")))
m13 = txt_same and pdf_same
report("P-M13 konstruksi argumen exporter identik (AST)", "PASS" if m13 else "FAIL",
       f"TXT dump identik={txt_same}; PDF argumen setara={pdf_same} (critical_alerts dibuktikan di P-X2)")

from src.utils.exporter import export_action_plan_text, export_action_plan_pdf  # noqa: E402

# Konstruksi meniru persis PusatUnduh module_rencana (checked=False).
ITEMS = PLAN.get("kitchen_action_checklist", [])
RCAS = PLAN.get("root_cause_analysis", [])
WEAK = CTX["weakest_aspect"]
items_txt = [{"aspect": "Operasional", "title": it[:35], "target_pic": "Tim Dapur / Kru",
              "deadline": "Shift Berjalan", "instruction": it, "checked": False}
             for it in ITEMS]
crit_txt = [{"title": f"Masalah Aspek {WEAK.capitalize()}", "aspect": WEAK.capitalize(),
             "message": rc} for rc in RCAS[:2]]
txt = export_action_plan_text(overall_score=CTX["khs"], status=CTX["status_label"],
                              action_items=items_txt, critical_alerts=crit_txt)
x1 = all(it in txt for it in ITEMS) and CTX["status_label"] in txt and "Health Score" in txt
report("P-X1 TXT berisi semua butir aksi (instruksi utuh) + status", "PASS" if x1 else "FAIL",
       f"panjang TXT={len(txt)} char; {len(ITEMS)} butir; semua instruksi utuh di dalamnya: {x1}")

items_pdf = [{"id": f"ACT-{i+1}", "aspect": "Dapur",
              "title": it[:35] + ("..." if len(it) > 35 else ""),
              "target_pic": "Kru Dapur", "deadline": "Shift Aktif",
              "instruction": it, "checked": False}
             for i, it in enumerate(ITEMS)]
crit_pdf = [{"title": f"Fokus Perbaikan {WEAK.capitalize()}", "aspect": WEAK.capitalize(),
             "message": rc} for rc in RCAS[:2]]
pdf_bytes = export_action_plan_pdf(overall_score=CTX["khs"], status=CTX["status_label"],
                                   action_items=items_pdf, critical_alerts=crit_pdf)
x2 = isinstance(pdf_bytes, (bytes, bytearray)) and bytes(pdf_bytes[:4]) == b"%PDF" and len(pdf_bytes) > 1000
try:
    import fitz
    _doc = fitz.open(stream=bytes(pdf_bytes), filetype="pdf")
    _ptext = "".join(p.get_text() for p in _doc)
    x2 = x2 and len(_ptext) > 50
    evx2 = f"ukuran={len(pdf_bytes)} byte; teks terekstrak {len(_ptext)} char"
except Exception:
    evx2 = f"ukuran={len(pdf_bytes)} byte (ekstraksi teks tidak tersedia)"
report("P-X2 PDF ter-generate valid (%PDF)", "PASS" if x2 else "FAIL", evx2)

export_df = pd.DataFrame([
    {"No": i + 1, "Tindakan": it, "Status_Selesai": False, "PIC": "Kru Dapur"}
    for i, it in enumerate(ITEMS)
])
csv_txt = export_df.to_csv(index=False)
x3 = csv_txt.splitlines()[0] == "No,Tindakan,Status_Selesai,PIC" \
    and len(csv_txt.splitlines()) == len(ITEMS) + 1
report("P-X3 CSV kolom + baris sesuai", "PASS" if x3 else "FAIL",
       f"header ok; baris data={len(csv_txt.splitlines()) - 1} == jumlah aksi {len(ITEMS)}")

fn_new = sorted(re.findall(r"file_name=f\"([^\"]+)\"", ren_src))
fn_old = sorted(re.findall(r"file_name=f\"([^\"]+)\"", old_ren))
fn_ok = fn_new == fn_old and len(fn_new) == 3
report("P-X4 nama file unduhan sama seperti lama", "PASS" if fn_ok else "FAIL",
       f"template file_name lama={fn_old} baru={fn_new}")

fig_s = charts.build_satisfaction_bar_figure(CTX["breakdown"])
sat_ok = list(fig_s.data[0].x) == [CTX["breakdown"][a]["satisfaction_score"]
                                   for a in reversed(labels.ASPECT_ORDER)] \
    and len(fig_s.layout.shapes) >= 1
report("P-M16 batang kepuasan == skor aspek + garis 70", "PASS" if sat_ok else "FAIL",
       f"x={ [round(v, 1) for v in fig_s.data[0].x] } shapes={len(fig_s.layout.shapes)}")

# ---------------------------------------------------------------- P-G
g1 = labels.APP_TITLE == "UlasRasa - Kesehatan Dapur dari Ulasan" \
    and os.path.exists(os.path.join(ROOT, "assets", "favicon.png")) \
    and "page_title" in app_src
report("P-G1 judul aplikasi + favicon", "PASS" if g1 else "FAIL",
       f"APP_TITLE={labels.APP_TITLE}; favicon ada; page_title di app.py")
theme_src = read("src/ui/theme.py")
g2 = '[data-testid="stSidebar"]' in theme_src and "display: none" in theme_src
report("P-G2 sidebar disembunyikan via CSS", "PASS" if g2 else "FAIL",
       "aturan stSidebar display:none ada di theme.py")
g3 = all(len(x.exception) == 0 for x in (at_r, at_i, at_a, at_c))
report("P-G3 empat modul tanpa exception (AppTest)", "PASS" if g3 else "FAIL",
       f"exceptions ringkasan/rincian/rencana/coba = {[len(x.exception) for x in (at_r, at_i, at_a, at_c)]}")

emoji_re = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F]")
hits = []
for rel in ("src/ui/theme.py", "src/ui/core.py", "src/ui/components.py", "src/ui/charts.py",
            "src/ui/labels.py", "src/ui/module_ringkasan.py", "src/ui/module_rincian.py",
            "src/ui/module_rencana.py", "src/ui/module_coba.py", "src/ui/module_landing.py", "app.py"):
    if emoji_re.search(read(rel)):
        hits.append(rel)
report("P-G5 nol emoji di file UI", "PASS" if not hits else "FAIL",
       f"file ber-emoji: {hits if hits else 'tidak ada'}")

report("P-G4 pytest 13 passed", "INSPEKSI",
       "dijalankan terpisah oleh Executor (py -m pytest tests/ -q) pada pohon yang sama")

fails = [r for r in RESULTS if r[1] == "FAIL"]
print()
print(f"RINGKASAN: {sum(1 for r in RESULTS if r[1] == 'PASS')} PASS, "
      f"{len(fails)} FAIL, {sum(1 for r in RESULTS if r[1] == 'INSPEKSI')} INSPEKSI "
      f"dari {len(RESULTS)} butir terprogram")
sys.exit(1 if fails else 0)
