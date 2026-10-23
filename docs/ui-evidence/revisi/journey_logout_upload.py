"""Journey tambahan koordinator: Ganti Akun SAAT unggahan CSV sedang aktif.

Kasus yang tidak tersimulasikan AppTest Pekerja L: user mengunggah CSV
(dataset aktif = "Outlet Kustom"), lalu klik "Ganti Akun" di top bar.
Harapan: tidak ada exception, kembali ke landing, dan saat masuk lagi
ke akun yang sama dataset sudah murni bawaan (unggahan sesi hilang).

Pola mengikuti journey_revisi.py; memakai _revisi_common.
Jalankan: py docs/ui-evidence/revisi/journey_logout_upload.py
"""
import json
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from _revisi_common import (AYAM, BASELINE, DEFAULT_URL, click_account_card,
                            detect_landing, ensure_server, read_hero,
                            stop_server, wait_initial, write_json)

CSV_PATH = os.path.join(HERE, "test_upload_3.csv")
OUT = os.path.join(HERE, "journey_logout_upload_result.json")

steps = []
result = {"url": DEFAULT_URL, "steps": steps}


def step(name, status, evidence, **kw):
    steps.append({"name": name, "status": status, "evidence": evidence, **kw})
    print(f"[{status}] {name}: {evidence}", flush=True)


def wait_greeting_contains(page, needle, timeout=90000):
    page.wait_for_function(
        """(n) => {
          const g = document.querySelector('.greeting');
          return g && (g.textContent || '').includes(n);
        }""", arg=needle, timeout=timeout)


def main():
    started, pid = ensure_server(DEFAULT_URL)
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto(DEFAULT_URL)
            wait_initial(page)

            land = detect_landing(page)
            step("landing_awal", "PASS" if land["landing_likely"] else "FAIL",
                 f"deteksi landing: {land}")

            ok, lab, err = click_account_card(page, AYAM)
            if ok:
                wait_greeting_contains(page, AYAM)
                hero = read_hero(page)
                step("masuk_ayam", "PASS" if hero["total_reviews"] == 25 else "FAIL",
                     f"sapaan={hero['greeting']!r} total={hero['total_reviews']} (harap 25)",
                     hero=hero)
            else:
                step("masuk_ayam", "FAIL", f"klik kartu gagal: {err}")

            # unggah CSV -> Outlet Kustom
            try:
                page.get_by_role("button", name="Ganti Data").first.click(timeout=15000)
                page.get_by_text("Data Ulasan", exact=False).first.wait_for(timeout=30000)
                page.get_by_text("Upload Dataset Real (CSV)", exact=False).first.click(timeout=15000)
                page.wait_for_timeout(1200)
                page.locator('input[type="file"]').first.set_input_files(CSV_PATH)
                wait_greeting_contains(page, "Outlet Kustom", timeout=90000)
                hero_up = read_hero(page)
                step("upload_aktif", "PASS" if hero_up["total_reviews"] == 3 else "FAIL",
                     f"sapaan={hero_up['greeting']!r} total={hero_up['total_reviews']} (harap 3)",
                     hero=hero_up)
            except Exception as ex:
                step("upload_aktif", "FAIL", f"{type(ex).__name__}: {ex}")

            # Ganti Akun SELAGI unggahan aktif
            try:
                ga = page.get_by_role("button", name="Ganti Akun")
                if ga.count() == 0:
                    ga = page.get_by_text("Ganti Akun", exact=True)
                ga.first.click(timeout=15000)
                # tunggu berbasis KONDISI (bukan waktu tetap): render landing
                # pasca-logout menghitung ulang KHS 5 akun, bisa > 3 detik.
                try:
                    page.wait_for_function(
                        """() => document.body && document.body.innerText
                           .includes('Pilih restoran untuk masuk ke dashboard')""",
                        timeout=90000)
                except Exception:
                    pass
                page.wait_for_timeout(1000)
                land2 = detect_landing(page)
                body = page.locator("body").inner_text() or ""
                has_exc = "Traceback" in body or "StreamlitAPIException" in body
                good = bool(land2["landing_likely"]) and not has_exc
                step("ganti_akun_saat_upload", "PASS" if good else "FAIL",
                     f"landing lagi={land2['landing_likely']} exception-di-halaman={has_exc}",
                     detection=land2)
            except Exception as ex:
                step("ganti_akun_saat_upload", "FAIL", f"{type(ex).__name__}: {ex}")

            # masuk lagi -> dataset harus murni
            try:
                ok2, _, err2 = click_account_card(page, AYAM)
                if not ok2:
                    raise RuntimeError(f"klik kartu kedua gagal: {err2}")
                wait_greeting_contains(page, AYAM)
                hero2 = read_hero(page)
                base = BASELINE[AYAM]
                good = (hero2["total_reviews"] == base["n_reviews"]
                        and hero2["khs_display_1dp"] is not None
                        and abs(hero2["khs_display_1dp"] - round(base["khs"], 1)) < 0.051)
                step("masuk_lagi_dataset_murni", "PASS" if good else "FAIL",
                     f"sapaan={hero2['greeting']!r} total={hero2['total_reviews']} "
                     f"(harap {base['n_reviews']}) KHS={hero2['khs_display_1dp']} "
                     f"(baseline {base['khs']})", hero=hero2)
            except Exception as ex:
                step("masuk_lagi_dataset_murni", "FAIL", f"{type(ex).__name__}: {ex}")

            browser.close()
    finally:
        n_pass = sum(1 for s in steps if s["status"] == "PASS")
        result["summary"] = {"pass": n_pass, "total": len(steps),
                             "overall": "PASS" if n_pass == len(steps) and steps else "FAIL"}
        write_json(OUT, result)
        if started:
            stop_server(pid)
    print(f"RINGKASAN journey_logout_upload: {result['summary']['pass']}/{result['summary']['total']} PASS - {result['summary']['overall']}")
    print(f"JSON -> {OUT}")
    return 0 if result["summary"]["overall"] == "PASS" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(1)
