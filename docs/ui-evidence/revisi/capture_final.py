"""Tangkapan penutup koordinator dari kode final revisi-landing.

Menghasilkan (di folder ini): shot-landing-desktop.png,
shot-landing-mobile.png, shot-dashboard-ayam.png.
Panel terbuka + popover terbuka memakai tangkapan Pekerja T dari kode
aplikasi yang sama (theme-widget/after-*.png).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from _revisi_common import (AYAM, DEFAULT_URL, click_account_card,
                            ensure_server, stop_server, wait_initial)


def main():
    started, pid = ensure_server(DEFAULT_URL)
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            # desktop landing + dashboard
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto(DEFAULT_URL)
            wait_initial(page)
            page.wait_for_timeout(1500)
            page.screenshot(path=os.path.join(HERE, "shot-landing-desktop.png"))
            ok, lab, err = click_account_card(page, AYAM)
            if not ok:
                raise RuntimeError(f"klik Ayam gagal: {err}")
            page.wait_for_function(
                """() => { const g = document.querySelector('.greeting');
                    return g && g.textContent.includes('Ayam Geprek'); }""",
                timeout=90000)
            page.wait_for_timeout(2500)
            page.screenshot(path=os.path.join(HERE, "shot-dashboard-ayam.png"))
            page.close()
            # mobile landing (konteks baru = sesi baru = landing)
            ctx = browser.new_context(viewport={"width": 390, "height": 844})
            mp = ctx.new_page()
            mp.goto(DEFAULT_URL)
            wait_initial(mp)
            mp.wait_for_timeout(1500)
            mp.screenshot(path=os.path.join(HERE, "shot-landing-mobile.png"))
            ctx.close()
            browser.close()
        print("CAPTURE OK")
    finally:
        if started:
            stop_server(pid)


if __name__ == "__main__":
    main()
