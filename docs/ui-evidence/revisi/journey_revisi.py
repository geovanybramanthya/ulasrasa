"""journey_revisi.py - uji perjalanan pengguna Revisi Mayor UI UlasRasa.

Langkah (masing-masing dicatat PASS/FAIL + alasannya di JSON):
  1 landing_loaded        keadaan awal = landing (bukan dashboard langsung)
  2 enter_ayam            klik kartu Ayam -> dashboard Ayam benar
                          (sapaan memuat nama Ayam + KHS 55.84/KRITIS cocok)
  3 ganti_akun_back       klik "Ganti Akun" di top bar -> kembali ke landing
  4 panel_ganti_data      masuk lagi -> buka panel "Ganti Data"
  5 upload_csv            pilih mode Upload -> unggah test_upload_3.csv
                          (3 baris, hanya kolom review_text) -> sapaan
                          "Outlet Kustom" + total ulasan = 3
  6 back_to_preset        pilih mode Preset lagi -> data akun kembali
                          (sapaan Ayam + KHS Ayam cocok lagi)
  7 add_review            buka expander "Input Ulasan Baru ke Outlet Ini"
                          -> isi ulasan negatif jelas (kemasan bocor)
                          -> klik "Simpan & Perbarui Dashboard"
                          -> total ulasan bertambah tepat 1

KEJUJURAN: bila landing / tombol "Ganti Akun" belum ada, langkah yang
bergantung padanya FAIL dengan alasan eksplisit. Langkah 4-7 yang masih
bisa dicapai dari dashboard langsung tetap dijalankan sebagai bukti
fungsional, tetapi diberi context "entry_bukan_dari_landing" dan journey
keseluruhan tetap FAIL - tidak dipalsukan jadi lulus penuh.

Pemakaian:
  py docs/ui-evidence/revisi/journey_revisi.py [--url http://localhost:8525] [--tag awal]
Output: journey_revisi_<tag>.json + ringkasan stdout. Exit 1 bila ada FAIL.
"""
import argparse
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from _revisi_common import (AYAM, BASELINE, DEFAULT_URL, click_account_card,
                            detect_landing, ensure_server, khs_matches,
                            read_hero, stop_server, wait_initial, write_json)

CSV_PATH = os.path.join(HERE, "test_upload_3.csv")
NEG_REVIEW = ("Kemasan bocor parah, minyak dan kuah tumpah ke kantong "
              "plastik, makanan sampai dalam keadaan dingin dan berantakan.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=DEFAULT_URL)
    ap.add_argument("--tag", default="awal")
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    started, pid = ensure_server(args.url)
    steps = []
    result = {"url": args.url, "tag": args.tag, "steps": steps}
    out_path = os.path.join(HERE, f"journey_revisi_{args.tag}.json")

    def flush():
        write_json(out_path, result)

    def step(name, status, reason, **extra):
        s = {"step": name, "status": status, "reason": reason}
        s.update(extra)
        steps.append(s)
        flush()
        print(f"{status:4s} {name:20s} {reason[:130]}", flush=True)
        return s

    def wait_greeting_contains(page, needle, timeout=90000):
        page.wait_for_function(
            """(n) => { const g = document.querySelector('.greeting');
               return g && g.textContent.includes(n); }""",
            arg=needle, timeout=timeout)
        page.wait_for_timeout(2000)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            ctx = browser.new_context(viewport={"width": 1440, "height": 900})
            page = ctx.new_page()
            page.goto(args.url, wait_until="domcontentloaded")
            wait_initial(page)

            # ---------- 1. landing ----------
            land = detect_landing(page)
            landing_ok = bool(land["landing_likely"])
            if landing_ok:
                step("landing_loaded", "PASS",
                     "keadaan awal adalah landing (tanpa sapaan dashboard, "
                     f"{land['distinct_resto_names_visible']} nama resto terlihat)",
                     detection=land)
            else:
                step("landing_loaded", "FAIL",
                     "keadaan awal BUKAN landing: app langsung membuka "
                     f"dashboard (KPI tampil={land['has_kpi']}, kartu landing={land['landing_card_count']})",
                     detection=land)
            entry_ctx = "dari_landing" if landing_ok else "entry_bukan_dari_landing"

            # ---------- 2. masuk Ayam ----------
            ayam_ok = False
            if landing_ok:
                ok_click, lab, err = click_account_card(page, AYAM)
                if not ok_click:
                    step("enter_ayam", "FAIL", f"klik kartu Ayam gagal: {err}")
                else:
                    try:
                        wait_greeting_contains(page, AYAM)
                        hero = read_hero(page)
                        base = BASELINE[AYAM]
                        good = (khs_matches(hero["khs_display_1dp"], base["khs"])
                                and base["status_word"] in (hero["status_text"] or ""))
                        ayam_ok = good
                        step("enter_ayam", "PASS" if good else "FAIL",
                             f"sapaan={hero['greeting']!r} KHS tampil="
                             f"{hero['khs_display_1dp']} (baseline {base['khs']}) "
                             f"status={hero['status_text']!r}", hero=hero)
                    except Exception as ex:
                        step("enter_ayam", "FAIL",
                             f"dashboard Ayam tidak tampil sesudah klik: {ex}")
            else:
                # diagnostik: apakah dashboard saat ini kebetulan Ayam?
                hero0 = read_hero(page)
                step("enter_ayam", "FAIL",
                     "tidak ada landing untuk mengklik kartu Ayam "
                     f"(dashboard awal: sapaan={hero0['greeting']!r})",
                     hero_initial=hero0)

            # ---------- 3. Ganti Akun -> landing ----------
            if landing_ok and ayam_ok:
                try:
                    ga = page.get_by_role("button", name="Ganti Akun")
                    if ga.count() == 0:
                        ga = page.get_by_text("Ganti Akun", exact=True)
                    ga.first.click(timeout=15000)
                    page.wait_for_timeout(2500)
                    land2 = detect_landing(page)
                    ok3 = bool(land2["landing_likely"])
                    step("ganti_akun_back", "PASS" if ok3 else "FAIL",
                         "klik Ganti Akun mengembalikan tampilan landing"
                         if ok3 else
                         f"sesudah klik Ganti Akun landing tidak terdeteksi "
                         f"(KPI dashboard masih tampil={land2['has_kpi']})",
                         detection=land2)
                except Exception as ex:
                    step("ganti_akun_back", "FAIL",
                         f"tombol 'Ganti Akun' tidak bisa diklik: "
                         f"{type(ex).__name__}: {ex}")
            else:
                has_ga = False
                try:
                    has_ga = "Ganti Akun" in (page.locator("body").inner_text() or "")
                except Exception:
                    pass
                step("ganti_akun_back", "FAIL",
                     "langkah tidak bisa dijalankan penuh (landing/masuk Ayam "
                     f"gagal); teks 'Ganti Akun' di halaman saat ini: {has_ga}")

            # ---------- 4. panel Ganti Data ----------
            # Masuk lagi ke Ayam dulu bila sedang di landing.
            land_now = detect_landing(page)
            if land_now["landing_likely"]:
                ok_click, _, err = click_account_card(page, AYAM)
                if ok_click:
                    try:
                        wait_greeting_contains(page, AYAM)
                    except Exception:
                        pass
            panel_ok = False
            try:
                page.get_by_role("button", name="Ganti Data").first.click(timeout=15000)
                page.get_by_text("Data Ulasan", exact=False).first.wait_for(timeout=30000)
                page.wait_for_timeout(1200)
                panel_ok = True
                step("panel_ganti_data", "PASS",
                     "panel Data Ulasan terbuka dari dashboard Ayam",
                     context=entry_ctx)
            except Exception as ex:
                step("panel_ganti_data", "FAIL",
                     f"panel Ganti Data tidak terbuka: {type(ex).__name__}: {ex}",
                     context=entry_ctx)

            # ---------- 5. upload CSV 3 baris ----------
            upload_ok = False
            if panel_ok:
                try:
                    # radio mode Upload di dalam panel
                    page.get_by_text("Upload Dataset Real (CSV)",
                                     exact=False).first.click(timeout=15000)
                    page.wait_for_timeout(1200)
                    page.locator('input[type="file"]').first.set_input_files(CSV_PATH)
                    wait_greeting_contains(page, "Outlet Kustom", timeout=90000)
                    hero_up = read_hero(page)
                    upload_ok = (hero_up["total_reviews"] == 3)
                    step("upload_csv", "PASS" if upload_ok else "FAIL",
                         f"sapaan={hero_up['greeting']!r} total ulasan tampil="
                         f"{hero_up['total_reviews']} (harap 3 dari CSV uji)",
                         context=entry_ctx, hero=hero_up)
                except Exception as ex:
                    step("upload_csv", "FAIL",
                         f"alur unggah CSV gagal: {type(ex).__name__}: {ex}",
                         context=entry_ctx)
            else:
                step("upload_csv", "FAIL", "dilewati: panel tidak terbuka",
                     context=entry_ctx)

            # ---------- 6. kembali ke Preset ----------
            if panel_ok:
                try:
                    page.get_by_text("Outlet Bawaan (Preset)",
                                     exact=False).first.click(timeout=15000)
                    wait_greeting_contains(page, AYAM, timeout=90000)
                    hero_back = read_hero(page)
                    base = BASELINE[AYAM]
                    good = (khs_matches(hero_back["khs_display_1dp"], base["khs"])
                            and hero_back["total_reviews"] == base["n_reviews"])
                    step("back_to_preset", "PASS" if good else "FAIL",
                         f"sapaan={hero_back['greeting']!r} KHS="
                         f"{hero_back['khs_display_1dp']} (baseline {base['khs']}) "
                         f"total={hero_back['total_reviews']} (harap {base['n_reviews']})",
                         context=entry_ctx, hero=hero_back)
                except Exception as ex:
                    step("back_to_preset", "FAIL",
                         f"kembali ke Preset gagal: {type(ex).__name__}: {ex}",
                         context=entry_ctx)
            else:
                step("back_to_preset", "FAIL", "dilewati: panel tidak terbuka",
                     context=entry_ctx)

            # ---------- 7. tambah ulasan baru ----------
            try:
                hero_before = read_hero(page)
                total_before = hero_before["total_reviews"]
                # panel mungkin tertutup sesudah rerun unggah: buka lagi bila perlu
                if page.get_by_text("Data Ulasan", exact=False).count() == 0:
                    page.get_by_role("button", name="Ganti Data").first.click(timeout=15000)
                    page.get_by_text("Data Ulasan", exact=False).first.wait_for(timeout=30000)
                hdr = page.locator('[data-testid="stExpander"]',
                                   has_text="Input Ulasan Baru ke Outlet Ini").first
                hdr.locator("summary, button, [data-testid='stExpanderHeader']").first.click(timeout=15000)
                ta = page.locator('[data-testid="stTextArea"] textarea').first
                ta.wait_for(state="visible", timeout=30000)
                ta.fill(NEG_REVIEW)
                page.get_by_role("button", name="Simpan & Perbarui Dashboard").first.click(timeout=15000)
                page.wait_for_function(
                    """(prev) => {
                      const els = document.querySelectorAll('.kpi-value');
                      if (els.length < 2) return false;
                      const n = parseInt((els[1].textContent || '').replace(/\\D/g, ''), 10);
                      return !isNaN(n) && n === prev + 1;
                    }""", arg=total_before, timeout=90000)
                page.wait_for_timeout(1500)
                hero_after = read_hero(page)
                good = (hero_after["total_reviews"] == (total_before or 0) + 1)
                step("add_review", "PASS" if good else "FAIL",
                     f"total ulasan {total_before} -> {hero_after['total_reviews']} "
                     f"(harap +1) sesudah simpan ulasan negatif kemasan",
                     context=entry_ctx, hero_before=hero_before, hero_after=hero_after)
            except Exception as ex:
                step("add_review", "FAIL",
                     f"alur tambah ulasan gagal: {type(ex).__name__}: {ex}",
                     context=entry_ctx)

            ctx.close()
            browser.close()
    finally:
        n_pass = sum(1 for s in steps if s["status"] == "PASS")
        result["summary"] = {"pass": n_pass, "fail": len(steps) - n_pass,
                             "total": len(steps),
                             "overall": "PASS" if n_pass == len(steps) and steps else "FAIL"}
        flush()
        if started:
            stop_server(pid)

    print(f"RINGKASAN journey_revisi ({args.tag}): "
          f"{result['summary']['pass']}/{result['summary']['total']} PASS - "
          f"overall {result['summary']['overall']}")
    print(f"JSON -> {out_path}")
    return 0 if result["summary"]["overall"] == "PASS" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(1)
