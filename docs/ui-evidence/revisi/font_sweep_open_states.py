"""font_sweep_open_states.py - sapuan font keadaan TERBUKA Revisi Mayor UI.

Melanjutkan pola audit-fix2/font_sweep.py + audit-fix3/font_sweep_svg.py
(computed style SEMUA elemen teks terlihat, termasuk SVG <text> Plotly),
tetapi pada keadaan-keadaan yang dulu tidak pernah tersapu karena panel /
expander / popover-nya tertutup:

  (a) LANDING            keadaan awal app sesudah revisi. Bila landing
                         belum jadi, keadaan awal = dashboard langsung;
                         itu dicatat apa adanya (landing_detected=false).
  (b) PANEL TERBUKA      sesudah klik tombol "Ganti Data".
  (c) EXPANDER TERBUKA   expander "Input Ulasan Baru ke Outlet Ini"
                         dibuka di dalam panel.
  (d) POPOVER TERBUKA    satu selectbox dibuka (filter polaritas di modul
                         Rincian Aspek; fallback selectbox restoran di
                         header) - elemen di dalam popover ikut tersapu
                         (popover BaseWeb adalah portal di akhir <body>).
  (e) EMPAT MODUL        Ringkasan / Rincian / Rencana / Coba, normal.

Target akhir: 0 elemen teks berisi font "Source Sans" di SEMUA keadaan;
peran lain benar (sapaan/judul Plus Jakarta Sans, angka JetBrains Mono,
isi Inter) - peran dilaporkan lewat role_samples + role_verdicts.

Pemakaian (di PC, dari root repo atau folder mana pun):
  py docs/ui-evidence/revisi/font_sweep_open_states.py [--url http://localhost:8525] [--tag awal]
Server: bila --url tidak menjawab health-check, script menyalakan server
Streamlit detached di port itu sendiri dan mematikannya di akhir
(kecuali --keep-server). Output: font_sweep_open_states_<tag>.json di
folder ini + ringkasan stdout. Exit 1 bila ada Source Sans / langkah gagal.
"""
import argparse
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from _revisi_common import (DEFAULT_URL, detect_landing, ensure_server,
                            goto_module, role_verdicts, stop_server, sweep,
                            wait_initial, write_json)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=DEFAULT_URL)
    ap.add_argument("--tag", default="awal")
    ap.add_argument("--keep-server", action="store_true")
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    started, pid = ensure_server(args.url)
    result = {"url": args.url, "tag": args.tag, "server_started_by_script": started,
              "states": [], "errors": []}
    out_path = os.path.join(HERE, f"font_sweep_open_states_{args.tag}.json")

    def flush():
        write_json(out_path, result)

    def add_state(page, label, note="", extra=None):
        s = sweep(page, label)
        s["note"] = note
        if extra:
            s.update(extra)
        s["role_verdicts"] = role_verdicts(s.get("role_samples"))
        result["states"].append(s)
        flush()
        print(f"{label:28s} total={s['total_text_elements']:4d} "
              f"chart_text={s['chart_text_elements']:3d} "
              f"source_sans={s['source_sans_count']:3d} fonts={s['by_primary_font']}",
              flush=True)
        return s

    def expander_state(page):
        """Keadaan expander Input Ulasan yang teramati di DOM (details.open
        adalah sinyal benar; konten expander tertutup TETAP ada di DOM
        Streamlit dan lolos cek visibilitas sapuan - tercatat apa adanya)."""
        try:
            return page.evaluate("""() => {
              const exps = Array.from(document.querySelectorAll('[data-testid="stExpander"]'));
              const hit = exps.find(e => (e.textContent || '').includes('Input Ulasan Baru'));
              if (!hit) return null;
              const det = hit.querySelector('details');
              const summ = hit.querySelector('summary');
              return {details_open: det ? det.open : null,
                      summary_aria_expanded: summ ? summ.getAttribute('aria-expanded') : null,
                      has_textarea: !!hit.querySelector('textarea')};
            }""")
        except Exception as ex:
            return {"error": f"{type(ex).__name__}: {ex}"}

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            ctx = browser.new_context(viewport={"width": 1440, "height": 900})
            page = ctx.new_page()
            page.goto(args.url, wait_until="domcontentloaded")
            wait_initial(page)

            # ---------------- (a) LANDING / keadaan awal ----------------
            land = detect_landing(page)
            result["landing_detection_initial"] = land
            print(f"LANDING detected={land['landing_likely']} "
                  f"kpi={land['has_kpi']} cards={land['landing_card_count']} "
                  f"distinct_resto={land['distinct_resto_names_visible']}",
                  flush=True)
            add_state(page, "a_landing_or_initial",
                      note=("landing terdeteksi" if land["landing_likely"] else
                            "landing TIDAK terdeteksi: app membuka dashboard "
                            "langsung (KPI tampil, tanpa kartu landing) - "
                            "keadaan awal apa adanya yang tersapu"))

            # Bila ada landing, masuk ke dashboard akun pertama agar
            # keadaan (b)-(e) bisa diuji; kegagalan dicatat, bukan disembunyikan.
            if land["landing_likely"]:
                from _revisi_common import AYAM, click_account_card
                ok, lab, err = click_account_card(page, AYAM)
                result["landing_enter_ayam"] = {"ok": ok, "label": lab, "error": err}
                if ok:
                    try:
                        page.get_by_text("Halo,", exact=False).first.wait_for(timeout=90000)
                    except Exception as ex:
                        result["errors"].append(f"sesudah klik kartu Ayam, sapaan tidak tampil: {ex}")
                page.wait_for_timeout(2500)
            else:
                result["landing_enter_ayam"] = {
                    "ok": False, "label": None,
                    "error": "dilewati: tidak ada landing untuk diklik"}

            # ---------------- (b) PANEL GANTI DATA TERBUKA ----------------
            try:
                page.get_by_role("button", name="Ganti Data").first.click(timeout=15000)
                page.get_by_text("Data Ulasan", exact=False).first.wait_for(timeout=30000)
                page.wait_for_timeout(1500)
                add_state(page, "b_panel_ganti_data_open",
                          extra={"expander_state_observed": expander_state(page)})
            except Exception as ex:
                result["errors"].append(f"(b) panel Ganti Data: {type(ex).__name__}: {ex}")
                print("ERROR (b):", ex, flush=True)

            # ---------------- (c) EXPANDER INPUT ULASAN TERBUKA ----------------
            try:
                hdr = page.locator('[data-testid="stExpander"]',
                                   has_text="Input Ulasan Baru ke Outlet Ini").first
                hdr.locator("summary, button, [data-testid='stExpanderHeader']").first.click(timeout=15000)
                page.locator('[data-testid="stTextArea"] textarea').first.wait_for(
                    state="visible", timeout=30000)
                page.wait_for_timeout(1200)
                es = expander_state(page)
                add_state(page, "c_expander_input_ulasan_open",
                          note=(f"expander teramati: {es}"),
                          extra={"expander_state_observed": es})
            except Exception as ex:
                result["errors"].append(f"(c) expander Input Ulasan: {type(ex).__name__}: {ex}")
                print("ERROR (c):", ex, flush=True)

            # tutup panel lagi agar keadaan modul bersih - DIVERIFIKASI:
            # judul panel harus hilang dari DOM; hasil dicatat di JSON.
            closed = False
            for _attempt in range(2):
                try:
                    page.get_by_role("button", name="Tutup Panel").first.click(timeout=10000)
                    page.wait_for_function(
                        """() => !(document.body.innerText || '').includes('Data Ulasan')""",
                        timeout=20000)
                    closed = True
                    break
                except Exception:
                    page.wait_for_timeout(1500)
            result["panel_close_after_c"] = {"closed": closed}
            flush()
            print(f"PANEL CLOSE after (c): closed={closed}", flush=True)
            page.wait_for_timeout(1000)

            # ---------------- (e) EMPAT MODUL NORMAL ----------------
            # (dikerjakan sebelum (d) karena (d) hidup di dalam modul Rincian)
            try:
                page.get_by_text("Halo,", exact=False).first.wait_for(timeout=30000)
                add_state(page, "e_module_ringkasan")
            except Exception as ex:
                result["errors"].append(f"(e) Ringkasan: {type(ex).__name__}: {ex}")
            for label, marker, state in [
                    ("Rincian Aspek", "Pilih aspek", "e_module_rincian"),
                    ("Rencana Aksi", "Akar Masalah", "e_module_rencana"),
                    ("Coba Ulasan", "Tulis Ulasan Pelanggan", "e_module_coba")]:
                try:
                    goto_module(page, label, marker)
                    add_state(page, state)
                except Exception as ex:
                    result["errors"].append(f"(e) {state}: {type(ex).__name__}: {ex}")
                    print(f"ERROR (e) {state}:", ex, flush=True)

            # ---------------- (d) POPOVER SELECTBOX TERBUKA ----------------
            try:
                goto_module(page, "Rincian Aspek", "Pilih aspek")
                # selectbox filter polaritas = stSelectbox pertama yang
                # labelnya "Saring polaritas:"; klik kontrol BaseWeb-nya.
                boxes = page.locator('[data-testid="stSelectbox"]')
                target = None
                for i in range(boxes.count()):
                    if "Saring polaritas" in (boxes.nth(i).inner_text() or ""):
                        target = boxes.nth(i)
                        break
                if target is None:
                    target = boxes.first
                target.locator('[data-baseweb="select"]').first.click(timeout=15000)
                page.locator('[data-baseweb="popover"] [role="option"], '
                             '[data-baseweb="popover"] li, '
                             '[role="listbox"]').first.wait_for(
                                 state="visible", timeout=30000)
                page.wait_for_timeout(1200)
                s = add_state(page, "d_popover_selectbox_open",
                              note="popover BaseWeb (portal di akhir body) ikut tersapu")
                pop_els = [e for e in s["elements"]
                           if e["testid"] in ("stSelectbox",) or e["plot_idx"] >= 0]
                s["popover_option_elements_seen"] = len(
                    [e for e in s["elements"] if e["text"] in (
                        "Semua Sentimen", "Hanya Negatif (Komplain)",
                        "Hanya Positif", "Hanya Netral")])
                page.keyboard.press("Escape")
            except Exception as ex:
                result["errors"].append(f"(d) popover selectbox: {type(ex).__name__}: {ex}")
                print("ERROR (d):", ex, flush=True)

            ctx.close()
            browser.close()
    finally:
        flush()
        if started and not args.keep_server:
            stop_server(pid)

    total_ss = sum(s["source_sans_count"] for s in result["states"])
    result["total_source_sans"] = total_ss
    result["target_met"] = (total_ss == 0 and not result["errors"]
                            and len(result["states"]) >= 7)
    flush()
    print(f"TOTAL Source Sans ({args.tag}): {total_ss} "
          f"dari {len(result['states'])} keadaan; errors={len(result['errors'])}")
    for e in result["errors"]:
        print("ERROR:", e)
    print(f"JSON -> {out_path}")
    return 0 if result["target_met"] else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(1)
