"""Probe tambalan: (a) scroll test pada kontainer scroll Streamlit 1.57,
(b) tombol Upload asli (stBaseButton-secondary) di dropzone,
(c) klarifikasi hover popover: aria-selected item yang di-hover."""
import json, os
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
URL = "http://localhost:8531"
res = {}

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 1440, "height": 900})
    page = ctx.new_page()
    page.goto(URL, wait_until="domcontentloaded")
    page.get_by_text("Pilih restoran", exact=False).first.wait_for(timeout=120000)
    page.wait_for_timeout(2500)
    page.locator('button', has_text="Masuk Dashboard").first.click()
    page.get_by_text("Halo,", exact=False).first.wait_for(timeout=120000)
    page.wait_for_timeout(2500)

    # (a) scroll kontainer aplikasi
    res["scroll_container"] = page.evaluate("""() => {
      const tb = document.querySelector('div.st-key-topbar');
      const before = tb ? tb.getBoundingClientRect().top : null;
      const cand = document.querySelector('[data-testid="stAppViewContainer"]');
      let used = null;
      if (cand && cand.scrollHeight > cand.clientHeight) { cand.scrollTop = 1400; used = 'stAppViewContainer'; }
      return {before, used,
              scrollTop: cand ? cand.scrollTop : null,
              scrollHeight: cand ? cand.scrollHeight : null,
              clientHeight: cand ? cand.clientHeight : null};
    }""")
    page.wait_for_timeout(900)
    res["scroll_container"]["topbar_top_after"] = page.evaluate("""() => {
      const tb = document.querySelector('div.st-key-topbar');
      return tb ? tb.getBoundingClientRect().top : null;
    }""")
    res["scroll_container"]["topbar_position_after"] = page.evaluate("""() => {
      const tb = document.querySelector('div.st-key-topbar');
      return tb ? getComputedStyle(tb).position : null;
    }""")
    page.evaluate("() => { const c = document.querySelector('[data-testid=\"stAppViewContainer\"]'); if (c) c.scrollTop = 0; }")
    page.wait_for_timeout(600)

    # (b) panel -> mode unggah -> tombol Upload asli
    page.locator('button', has_text="Ganti Data").first.click()
    page.wait_for_timeout(2500)
    page.locator('[data-testid="stRadio"] label', has_text="Upload Dataset").first.click()
    page.wait_for_timeout(2500)
    res["upload_btn_real"] = page.evaluate("""() => {
      const ub = document.querySelector('[data-testid="stFileUploader"] button[data-testid="stBaseButton-secondary"]')
              || document.querySelector('[data-testid="stFileUploaderDropzone"] button');
      if (!ub) return {found: false};
      const cs = getComputedStyle(ub);
      const pp = ub.querySelector('[data-testid="stMarkdownContainer"] p');
      return {found: true, testid: ub.getAttribute('data-testid'), kind: ub.getAttribute('kind'),
        bg: cs.backgroundColor, bgImage: cs.backgroundImage, radius: cs.borderRadius, color: cs.color,
        border: cs.borderTopWidth + ' ' + cs.borderTopStyle + ' ' + cs.borderTopColor,
        label_font: pp ? getComputedStyle(pp).fontFamily : null,
        text: ub.textContent.trim().slice(0, 30)};
    }""")

    # (c) hover popover di Rincian
    page.locator('[data-testid="stButtonGroup"] button', has_text="Rincian").first.click()
    page.get_by_text("Pilih aspek", exact=False).first.wait_for(timeout=90000)
    page.wait_for_timeout(2000)
    page.locator('[data-testid="stSelectbox"] [data-baseweb="select"]').first.scroll_into_view_if_needed()
    page.wait_for_timeout(500)
    page.locator('[data-testid="stSelectbox"] [data-baseweb="select"]').first.click()
    page.wait_for_timeout(1500)
    items = page.locator('[data-baseweb="popover"] li[role="option"]')
    idx = None
    for i in range(items.count()):
        if items.nth(i).get_attribute("aria-selected") != "true":
            idx = i
            break
    if idx is not None:
        items.nth(idx).hover()
        page.wait_for_timeout(700)
        res["hover_clarify"] = page.evaluate("""(i) => {
          const li = document.querySelectorAll('[data-baseweb="popover"] li[role="option"]')[i];
          const inner = li.querySelector(':scope > div');
          return {text: li.textContent.trim().slice(0, 40),
                  ariaSelected_now: li.getAttribute('aria-selected'),
                  matches_hover: li.matches(':hover'),
                  inner_bg: inner ? getComputedStyle(inner).backgroundColor : null};
        }""", idx)
    ctx.close()
    b.close()

out = os.path.join(HERE, "scroll_upload.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
print("JSON ->", out)
