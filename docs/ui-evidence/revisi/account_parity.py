"""account_parity.py - paritas KHS per akun lewat journey klik landing.

Untuk SETIAP akun (4 resto + Benchmark): muat app dari keadaan awal,
klik kartu akunnya di landing, tunggu dashboard, baca KHS + status dari
hero Ringkasan (.kpi-value pertama + .hero-status), bandingkan ke
baseline teraudit (docs/ui-evidence/baseline.json, disalin di
_revisi_common.BASELINE):

  Semua Outlet 67.27 WASPADA | Ayam 55.84 KRITIS | Bakso 68.24 WASPADA
  Bebek 83.00 PRIMA           | Kopi 59.55 KRITIS

Tampilan app hanya 1 desimal, jadi kecocokan angka = pembulatan 1
desimal sama + kata status sama + sapaan menyebut nama akun yang benar.

KEJUJURAN: bila klik kartu gagal, akun itu FAIL dengan alasan eksplisit -
tidak dipalsukan jadi PASS. Sebagai diagnostik tambahan (TIDAK dihitung
PASS), script membaca angka KHS yang tercetak di kartu landing itu
sendiri (format Indonesia 2 desimal, mis. "55,84", dari
.landing-khs-num) dan melaporkannya di "diagnostic_via_landing_card".

Pemakaian:
  py docs/ui-evidence/revisi/account_parity.py [--url http://localhost:8525] [--tag awal]
Output: account_parity_<tag>.json + ringkasan stdout. Exit 1 bila ada FAIL.
"""
import argparse
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from _revisi_common import (ACCOUNT_ORDER, BASELINE, DEFAULT_URL,
                            click_account_card, detect_landing, ensure_server,
                            khs_matches, read_hero, stop_server, wait_initial,
                            write_json)


def check_hero(page, greeting_name):
    """Bandingkan hero saat ini ke baseline akun. -> (ok, detail dict)."""
    hero = read_hero(page)
    base = BASELINE[greeting_name]
    greet_ok = bool(hero["greeting"]) and greeting_name in hero["greeting"]
    khs_ok = khs_matches(hero["khs_display_1dp"], base["khs"])
    status_ok = base["status_word"] in (hero["status_text"] or "")
    ok = greet_ok and khs_ok and status_ok
    detail = {"greeting": hero["greeting"],
              "khs_display_1dp": hero["khs_display_1dp"],
              "khs_expected_2dp": base["khs"],
              "status_text": hero["status_text"],
              "status_expected": base["status_label"],
              "total_reviews_shown": hero["total_reviews"],
              "total_expected": base["n_reviews"],
              "greeting_ok": greet_ok, "khs_ok": khs_ok, "status_ok": status_ok}
    return ok, detail


def diagnostic_via_landing_card(page, greeting_name):
    """Diagnostik SAJA (bukan PASS journey): baca KHS + cip status yang
    tercetak di kartu landing akun ini (.landing-khs-num, format "55,84")."""
    base = BASELINE[greeting_name]
    label = base["card_labels"][0]
    try:
        d = page.evaluate("""(label) => {
          const cards = Array.from(
            document.querySelectorAll('[class*="st-key-landing_acct"]'));
          const card = cards.find(c => (c.textContent || '').includes(label));
          if (!card) return null;
          const num = card.querySelector('.landing-khs-num');
          return {card_text: (card.textContent || '').trim().slice(0, 200),
                  khs_text: num ? (num.textContent || '').trim() : null};
        }""", label)
        if not d:
            return {"numbers_match_baseline": False,
                    "error": "kartu landing akun tidak ditemukan"}
        khs_card = None
        if d["khs_text"]:
            try:
                khs_card = float(d["khs_text"].replace(".", "").replace(",", ".")
                                 if d["khs_text"].count(",") == 1 and
                                 len(d["khs_text"].split(",")[1]) == 2
                                 else d["khs_text"].replace(",", "."))
            except Exception:
                khs_card = None
        match = (khs_card is not None
                 and abs(khs_card - base["khs"]) < 0.011
                 and base["status_word"] in (d["card_text"] or ""))
        return {"khs_on_card": khs_card, "khs_expected_2dp": base["khs"],
                "card_text_excerpt": d["card_text"],
                "numbers_match_baseline": bool(match)}
    except Exception as ex:
        return {"numbers_match_baseline": False,
                "error": f"{type(ex).__name__}: {ex}"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=DEFAULT_URL)
    ap.add_argument("--tag", default="awal")
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    started, pid = ensure_server(args.url)
    result = {"url": args.url, "tag": args.tag,
              "accounts": [], "summary": {}}
    out_path = os.path.join(HERE, f"account_parity_{args.tag}.json")

    def flush():
        write_json(out_path, result)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for name in ACCOUNT_ORDER:
                entry = {"account": name, "journey_status": "FAIL",
                         "reason": "", "hero": None,
                         "diagnostic_via_landing_card": None}
                ctx = browser.new_context(viewport={"width": 1440, "height": 900})
                page = ctx.new_page()
                try:
                    page.goto(args.url, wait_until="domcontentloaded")
                    wait_initial(page)
                    land = detect_landing(page)
                    entry["landing_detection"] = land
                    # diagnostik kartu selalu dibaca selagi masih di landing
                    if land["landing_likely"]:
                        entry["diagnostic_via_landing_card"] = \
                            diagnostic_via_landing_card(page, name)
                    if not land["landing_likely"]:
                        entry["reason"] = (
                            "landing tidak terdeteksi pada keadaan awal "
                            f"(kartu landing={land['has_landing_cards']}, "
                            f"KPI dashboard tampil={land['has_kpi']}, "
                            f"nama resto terlihat="
                            f"{land['distinct_resto_names_visible']}) - "
                            "langkah klik kartu tidak bisa dijalankan")
                    else:
                        ok_click, lab, err = click_account_card(page, name)
                        if not ok_click:
                            entry["reason"] = f"klik kartu gagal: {err}"
                        else:
                            entry["clicked_label"] = lab
                            try:
                                page.wait_for_function(
                                    """(n) => { const g = document.querySelector('.greeting');
                                       return g && g.textContent.includes(n); }""",
                                    arg=name, timeout=90000)
                                page.wait_for_timeout(2500)
                                ok, detail = check_hero(page, name)
                                entry["hero"] = detail
                                if ok:
                                    entry["journey_status"] = "PASS"
                                    entry["reason"] = "KHS + status + sapaan cocok baseline"
                                else:
                                    entry["reason"] = (
                                        "hero tidak cocok baseline: "
                                        f"greeting_ok={detail['greeting_ok']} "
                                        f"khs_ok={detail['khs_ok']} "
                                        f"status_ok={detail['status_ok']}")
                            except Exception as ex:
                                entry["reason"] = (f"dashboard akun tidak tampil "
                                                    f"sesudah klik kartu: {ex}")
                except Exception as ex:
                    entry["reason"] = f"pengecualian journey: {type(ex).__name__}: {ex}"
                result["accounts"].append(entry)
                flush()
                diag = entry["diagnostic_via_landing_card"] or {}
                print(f"{entry['journey_status']:4s} {name:38s} "
                      f"khs_hero={ (entry['hero'] or {}).get('khs_display_1dp') } "
                      f"khs_card={diag.get('khs_on_card')} "
                      f"diag_card_match={diag.get('numbers_match_baseline')} "
                      f"| {entry['reason'][:110]}", flush=True)
                ctx.close()
            browser.close()
    finally:
        n_pass = sum(1 for a in result["accounts"] if a["journey_status"] == "PASS")
        result["summary"] = {"pass": n_pass,
                             "fail": len(result["accounts"]) - n_pass,
                             "total": len(result["accounts"])}
        flush()
        if started:
            stop_server(pid)

    print(f"RINGKASAN account_parity ({args.tag}): "
          f"{result['summary']['pass']} PASS, {result['summary']['fail']} FAIL")
    print(f"JSON -> {out_path}")
    return 0 if result["summary"]["fail"] == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(1)
