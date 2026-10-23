"""Uji perjalanan klik Ringkasan (Gerbang 2):
1) CTA hero 'Lihat Rencana Aksi' -> Modul Rencana tampil (caption mode).
2) Kembali lewat pill 'Ringkasan'.
3) Tombol rel keluhan pertama -> Modul Rincian tampil, aspek = aspek item pertama.
"""
import os
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8510"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tahap-2")

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1440, "height": 1000})
    pg.goto(BASE, wait_until="domcontentloaded")
    pg.get_by_text("Halo,", exact=False).first.wait_for(timeout=60000)
    pg.wait_for_timeout(2500)

    # 1) CTA hero
    pg.get_by_role("button", name="Lihat Rencana Aksi").first.click()
    try:
        pg.get_by_text("Mode rekomendasi:", exact=False).first.wait_for(timeout=60000)
        print("STEP1 CTA->Rencana: PASS")
    except Exception as e:
        print("STEP1 CTA->Rencana: FAIL", str(e)[:120])
    pg.wait_for_timeout(1500)
    pg.screenshot(path=os.path.join(OUT, "journey-rencana.png"))

    # 2) kembali ke Ringkasan lewat pill
    pg.get_by_role("button", name="Ringkasan").first.click()
    try:
        pg.get_by_text("Keluhan Terbaru", exact=False).first.wait_for(timeout=60000)
        print("STEP2 pill->Ringkasan: PASS")
    except Exception as e:
        print("STEP2 pill->Ringkasan: FAIL", str(e)[:120])
    pg.wait_for_timeout(2500)

    # 3) klik tombol rel pertama
    pg.get_by_role("button", name="Lihat di Rincian Aspek").first.click()
    try:
        pg.get_by_text("Deep-Dive", exact=False).first.wait_for(timeout=60000)
        print("STEP3 rel->Rincian: PASS")
    except Exception as e:
        print("STEP3 rel->Rincian: FAIL", str(e)[:120])
    pg.wait_for_timeout(2500)
    sel = pg.evaluate("""() => {
        const el = document.querySelector('[data-testid="stSelectbox"] div[data-baseweb="select"]');
        return el ? el.textContent.trim() : 'NO-SELECT';
    }""")
    print("RINCIAN SELECTBOX VALUE:", sel)
    pg.screenshot(path=os.path.join(OUT, "journey-rincian.png"))
    b.close()
