"""verify_fix.py - verifikasi perbaikan D1 (font Inter elemen bawaan) + D2 (top bar lengket).
Gaya probe sama seperti Auditor: computed style sungguhan + uji gulir roda Playwright.
Server target: http://localhost:8514 (kode branch ui-overhaul sesudah perbaikan).
Screenshot bukti ditulis ke folder yang sama dengan script ini.
"""
import json
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "http://localhost:8514"
R = {"d1": {}, "d2": {}}

FONT_JS = """(sel) => { const el = document.querySelector(sel); if (!el) return null;
  return {font: getComputedStyle(el).fontFamily, text: (el.textContent||'').trim().slice(0,60)}; }"""

FIRST_P_JS = """() => { const ps = Array.from(document.querySelectorAll('[data-testid="stMarkdownContainer"] p'))
  .filter(p => p.textContent.trim().length > 3);
  if (!ps.length) return null; const p = ps[0];
  return {font: getComputedStyle(p).fontFamily, text: p.textContent.trim().slice(0,60)}; }"""


def is_inter(f):
    return bool(f) and "Inter" in f["font"] and "Source Sans" not in f["font"]


def topbar_rect(page):
    return page.evaluate(
        """() => { const tb = document.querySelector('div.st-key-topbar');
        if (!tb) return null; const r = tb.getBoundingClientRect();
        return {top: r.top, bottom: r.bottom, left: r.left, width: r.width, height: r.height,
                position: getComputedStyle(tb).position}; }"""
    )


def greeting_top(page):
    return page.evaluate(
        """() => { const g = document.querySelector('.greeting');
        return g ? g.getBoundingClientRect().top : null; }"""
    )


def goto_module(page, name, marker, timeout=60000):
    page.locator('[data-testid="stButtonGroup"] button', has_text=name).first.click()
    page.get_by_text(marker, exact=False).first.wait_for(timeout=timeout)
    page.wait_for_timeout(1500)


def main():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        # ---------------- desktop ----------------
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.goto(BASE, wait_until="domcontentloaded")
        page.get_by_text("Halo,", exact=False).first.wait_for(timeout=90000)
        page.wait_for_timeout(3000)

        # D2 desktop: posisi awal + sesudah gulir roda >= 800px
        tb0 = topbar_rect(page)
        gt0 = greeting_top(page)
        R["d2"]["desktop_before"] = {"topbar": tb0, "greeting_top": gt0}
        page.screenshot(path=os.path.join(HERE, "fix-desktop-top.png"))
        page.mouse.move(720, 500)
        page.mouse.wheel(0, 1400)
        page.wait_for_timeout(900)
        tb1 = topbar_rect(page)
        st = page.evaluate("() => document.querySelector('section[data-testid=\"stMain\"]').scrollTop")
        R["d2"]["desktop_after_wheel1400"] = {"topbar": tb1, "main_scrollTop": st}
        page.screenshot(path=os.path.join(HERE, "fix-desktop-scrolled.png"))
        page.evaluate("() => document.querySelector('section[data-testid=\"stMain\"]').scrollTo(0,0)")
        page.wait_for_timeout(600)

        # D1 ringkasan: paragraf markdown pertama + nilai selectbox + label widget
        R["d1"]["ringkasan_paragraph"] = page.evaluate(FIRST_P_JS)
        R["d1"]["select_value"] = page.evaluate(
            """() => { const s = document.querySelector('[data-baseweb="select"]');
            if (!s) return null; const val = s.querySelector('div');
            return {root_font: getComputedStyle(s).fontFamily,
                    inner_font: val ? getComputedStyle(val).fontFamily : null,
                    text: s.textContent.trim().slice(0,60)}; }"""
        )
        R["d1"]["widget_label"] = page.evaluate(FONT_JS % "[data-testid='stWidgetLabel'] p") \
            if False else page.evaluate(
            """() => { const el = document.querySelector('[data-testid="stWidgetLabel"] p');
            return el ? {font: getComputedStyle(el).fontFamily, text: el.textContent.trim().slice(0,60)} : null; }""")
        page.screenshot(path=os.path.join(HERE, "fix-ringkasan.png"))

        # D1 rincian: paragraf persis sampel Auditor
        goto_module(page, "Rincian Aspek", "Pilih aspek")
        R["d1"]["rincian_paragraph"] = page.evaluate(
            """() => { const ps = Array.from(document.querySelectorAll('[data-testid="stMarkdownContainer"] p'));
            const p = ps.find(x => x.textContent.includes('Pilih aspek')) || ps[0];
            return p ? {font: getComputedStyle(p).fontFamily, text: p.textContent.trim().slice(0,60)} : null; }"""
        )
        page.screenshot(path=os.path.join(HERE, "fix-rincian.png"))

        # D1 rencana: teks aksi (checkbox/markdown) persis gaya sampel Auditor
        goto_module(page, "Rencana Aksi", "Akar Masalah")
        page.wait_for_timeout(2500)
        R["d1"]["rencana_paragraph"] = page.evaluate(FIRST_P_JS)
        R["d1"]["rencana_checkbox_label"] = page.evaluate(
            """() => { const el = document.querySelector('[data-testid="stCheckbox"] [data-testid="stMarkdownContainer"] p');
            return el ? {font: getComputedStyle(el).fontFamily, text: el.textContent.trim().slice(0,60)} : null; }"""
        )
        page.screenshot(path=os.path.join(HERE, "fix-rencana.png"))

        # D1 coba: textarea
        goto_module(page, "Coba Ulasan", "Coba")
        R["d1"]["coba_textarea"] = page.evaluate(
            """() => { const t = document.querySelector('[data-testid="stTextArea"] textarea');
            return t ? {font: getComputedStyle(t).fontFamily} : null; }"""
        )
        page.screenshot(path=os.path.join(HERE, "fix-coba.png"))

        # peran font lain tidak rusak: judul Jakarta + angka mono + tombol Jakarta
        R["font_roles"] = {
            "greeting": page.evaluate(
                """() => { const g = document.querySelector('.greeting');
                return g ? getComputedStyle(g).fontFamily : null; }"""),
            "button_label_p": page.evaluate(
                """() => { const el = document.querySelector('.stButton [data-testid="stMarkdownContainer"] p');
                return el ? {font: getComputedStyle(el).fontFamily, text: el.textContent.trim().slice(0,40)} : null; }"""),
        }
        ctx.close()

        # ---------------- mobile ----------------
        ctx = browser.new_context(viewport={"width": 390, "height": 844})
        page = ctx.new_page()
        page.goto(BASE, wait_until="domcontentloaded")
        page.get_by_text("Halo,", exact=False).first.wait_for(timeout=90000)
        page.wait_for_timeout(3000)
        mb0 = topbar_rect(page)
        mg0 = greeting_top(page)
        R["d2"]["mobile_before"] = {"topbar": mb0, "greeting_top": mg0}
        page.screenshot(path=os.path.join(HERE, "fix-mobile-top.png"))
        page.mouse.move(195, 420)
        page.mouse.wheel(0, 1400)
        page.wait_for_timeout(900)
        mb1 = topbar_rect(page)
        mst = page.evaluate("() => document.querySelector('section[data-testid=\"stMain\"]').scrollTop")
        R["d2"]["mobile_after_wheel1400"] = {"topbar": mb1, "main_scrollTop": mst}
        page.screenshot(path=os.path.join(HERE, "fix-mobile-scrolled.png"))
        ctx.close()
        browser.close()

    # vonis ringkas
    d1keys = ["ringkasan_paragraph", "select_value", "rincian_paragraph",
              "rencana_paragraph", "rencana_checkbox_label", "coba_textarea"]
    R["d1_pass"] = {}
    for k in d1keys:
        v = R["d1"].get(k)
        if k == "select_value":
            R["d1_pass"][k] = bool(v) and "Inter" in (v.get("inner_font") or "") and "Source Sans" not in (v.get("inner_font") or "")
        elif k == "coba_textarea":
            R["d1_pass"][k] = bool(v) and "Inter" in v["font"] and "Source Sans" not in v["font"]
        else:
            R["d1_pass"][k] = is_inter(v)
    for vp in ["desktop", "mobile"]:
        b = R["d2"][vp + "_before"]["topbar"]
        a = R["d2"][vp + "_after_wheel1400"]["topbar"]
        R["d2"][vp + "_pass"] = bool(b and a) and abs(a["top"] - b["top"]) <= 2 and a["position"] == "fixed"
        R["d2"][vp + "_no_overlap_at_rest"] = bool(b) and R["d2"][vp + "_before"]["greeting_top"] >= b["bottom"] - 1
    print(json.dumps(R, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
