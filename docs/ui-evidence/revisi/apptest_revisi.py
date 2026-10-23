"""apptest_revisi.py - AppTest untuk keadaan landing + dashboard revisi.

Mengikuti pola docs/ui-evidence/apptest_check.py + blok AppTest di
parity_check.py (AppTest.from_file app.py, default_timeout=600).

Keadaan yang diuji:
  1. LANDING  - run segar TANPA state akun apa pun. Harapan final: app
     berhenti di landing dan 0 exception. KEADAAN SAAT INI (dicatat apa
     adanya): belum ada gerbang landing, jadi run segar langsung merender
     dashboard - exception tetap harus 0, tetapi temuan
     "landing_gate_absent" dilaporkan dan verdict landing = FAIL.
  2. DASHBOARD AYAM - state akun disetel ke Ayam, modul Ringkasan:
     0 exception + sapaan Ayam + KHS tampil 55.8% (baseline 55.84).
  3. DASHBOARD BENCHMARK - state akun = Semua Outlet (Benchmark):
     0 exception + sapaan "Halo, Semua Outlet" + KHS 67.3% (baseline 67.27).

=====================================================================
KUNCI SESSION_STATE AKUN - SUDAH FINAL (diperbarui 2026-10-23 malam)
=====================================================================
Implementasi landing final (commit 77749d5 + 7515e77) memakai kunci:

    "active_account"  (src/ui/core.py init_session_state)
      None            -> belum masuk, app merender landing saja
      nama resto      -> dashboard akun resto itu
      labels.BENCHMARK_LABEL ("Semua Outlet (Benchmark Industri)")
                      -> dashboard Benchmark (sapaan "Halo, Semua Outlet")

core.enter_account() juga menyetel cermin "ui_resto_select" ke nilai
yang sama; seeding dashboard di bawah meniru persis enter_account untuk
bagian yang relevan (active_account + ui_resto_select + ui_data_mode
Preset + active_module_name Ringkasan + panel tertutup).
=====================================================================

Pemakaian:  py docs/ui-evidence/revisi/apptest_revisi.py [timeout_detik]
Output: ringkasan stdout + apptest_revisi_result.json di folder ini.
Exit 1 bila ada exception atau verdict FAIL.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

# --- kunci akun final: active_account (lihat blok dokumentasi di atas) ---
ACCOUNT_KEY = "active_account"
ACCOUNT_SEED = {
    # greeting_name -> nilai active_account (nama resto / label Benchmark)
    "Ayam Geprek Sambal Korek Barokah": "Ayam Geprek Sambal Korek Barokah",
    "Semua Outlet": "Semua Outlet (Benchmark Industri)",
}

from _revisi_common import BASELINE, khs_matches  # noqa: E402

MOD_RINGKASAN = "Ringkasan Eksekutif & Health Score"
TIMEOUT = int(sys.argv[1]) if len(sys.argv) > 1 else 600

RESULTS = []


def report(name, status, evidence):
    RESULTS.append({"check": name, "status": status, "evidence": evidence})
    print(f"[{status:4s}] {name}: {evidence}", flush=True)


def run_app(seed=None, timeout=TIMEOUT):
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(os.path.join(ROOT, "app.py"),
                           default_timeout=timeout)
    for k, v in (seed or {}).items():
        try:
            at.session_state[k] = v
        except Exception:
            pass
    at.run(timeout=timeout)
    md = " ".join(str(getattr(m, "value", "")) for m in at.markdown)
    return at, md


def dashboard_seed(greeting_name):
    """Seed dashboard meniru core.enter_account() untuk akun ini."""
    from src.ui import labels
    resto_value = (labels.BENCHMARK_LABEL if greeting_name == "Semua Outlet"
                   else greeting_name)
    return {"active_module_name": MOD_RINGKASAN,
            "ui_data_mode": labels.DATA_MODE_PRESET,
            "ui_resto_select": resto_value,
            "ui_panel_open": False,
            ACCOUNT_KEY: ACCOUNT_SEED.get(greeting_name, resto_value)}


def main():
    # ---------------- 1. keadaan landing (tanpa state akun) ----------------
    at0, md0 = run_app(seed=None)
    exc0 = len(at0.exception)
    has_greeting = "Halo," in md0
    # Penanda landing implementasi final: judul landing + nama-nama resto
    # kartu tampil bersamaan TANPA sapaan dashboard "Halo,".
    resto_names = [n for n in BASELINE if n != "Semua Outlet"]
    names_shown = [n for n in resto_names if n in md0]
    has_title = "Pilih restoran untuk masuk ke dashboard" in md0
    has_enter_btn = False
    try:
        has_enter_btn = any("Masuk Dashboard" in str(getattr(b, "label", ""))
                            for b in at0.button)
    except Exception:
        pass
    landing_shown = (not has_greeting) and (has_title or len(names_shown) >= 3)
    report("landing_no_exception", "PASS" if exc0 == 0 else "FAIL",
           f"run segar tanpa state akun (active_account=None): exception={exc0}")
    report("landing_gate_present", "PASS" if landing_shown else "FAIL",
           f"landing tampil: judul={has_title} nama resto di markdown="
           f"{len(names_shown)} tombol 'Masuk Dashboard' ada={has_enter_btn} "
           f"sapaan dashboard ada={has_greeting}"
           if landing_shown else
           "landing_gate_absent: run segar TIDAK berhenti di landing "
           f"(judul={has_title}; sapaan 'Halo,' ada={has_greeting}; "
           f"nama resto di markdown={len(names_shown)})")
    for e in at0.exception:
        print("  EXCEPTION(landing):", getattr(e, "value", e), flush=True)

    # ---------------- 2 & 3. dashboard per akun ----------------
    for name in ("Ayam Geprek Sambal Korek Barokah", "Semua Outlet"):
        base = BASELINE[name]
        at, md = run_app(seed=dashboard_seed(name))
        exc = len(at.exception)
        greet_ok = f"Halo, {name}" in md
        khs_txt = f"{base['khs']:.1f}%"
        khs_ok = khs_txt in md and khs_matches(base["khs"], base["khs"])
        status_ok = base["status_label"] in md
        ok = exc == 0 and greet_ok and khs_txt in md and status_ok
        report(f"dashboard_{name[:18]}", "PASS" if ok else "FAIL",
               f"exception={exc} sapaan_ok={greet_ok} "
               f"KHS '{khs_txt}' tampil={khs_txt in md} "
               f"status '{base['status_label']}' tampil={status_ok} "
               f"(seed {ACCOUNT_KEY}={ACCOUNT_SEED.get(name)!r})")
        for e in at.exception:
            print(f"  EXCEPTION({name}):", getattr(e, "value", e), flush=True)

    out = {"checks": RESULTS,
           "account_key": ACCOUNT_KEY,
           "summary": {
               "pass": sum(1 for r in RESULTS if r["status"] == "PASS"),
               "fail": sum(1 for r in RESULTS if r["status"] == "FAIL"),
               "total": len(RESULTS)}}
    out_path = os.path.join(HERE, "apptest_revisi_result.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"RINGKASAN apptest_revisi: {out['summary']['pass']} PASS, "
          f"{out['summary']['fail']} FAIL dari {out['summary']['total']}")
    print(f"JSON -> {out_path}")
    return 0 if out["summary"]["fail"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
