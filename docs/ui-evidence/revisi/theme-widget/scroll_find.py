"""Cari elemen scrollable Streamlit 1.57 + uji top bar fixed saat scroll."""
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
    res["scrollables"] = page.evaluate("""() => {
      const out = [];
      for (const el of document.querySelectorAll('*')) {
        if (el.scrollHeight > el.clientHeight + 40) {
          const cs = getComputedStyle(el);
          if (cs.overflowY === 'auto' || cs.overflowY === 'scroll' || el === document.scrollingElement) {
            out.push({tag: el.tagName, testid: el.getAttribute('data-testid') || '',
              cls: (typeof el.className === 'string' ? el.className : '').slice(0, 60),
              scrollHeight: el.scrollHeight, clientHeight: el.clientHeight, overflowY: cs.overflowY});
          }
        }
      }
      return {docScrollH: document.documentElement.scrollHeight,
              bodyScrollH: document.body.scrollHeight,
              scrollingElement: document.scrollingElement ? document.scrollingElement.tagName : null,
              found: out.slice(0, 8)};
    }""")
    res["scroll_test2"] = page.evaluate("""() => {
      const tb = document.querySelector('div.st-key-topbar');
      const before = tb ? tb.getBoundingClientRect().top : null;
      // gulir elemen scrollable terdalam yang memuat konten utama
      let target = null;
      for (const el of document.querySelectorAll('*')) {
        if (el.scrollHeight > el.clientHeight + 40) {
          const cs = getComputedStyle(el);
          if (cs.overflowY === 'auto' || cs.overflowY === 'scroll') target = el;
        }
      }
      if (target) target.scrollTop = 1400;
      if (window.scrollY === 0 && (!target || target.scrollTop === 0)) window.scrollTo(0, 1400);
      return {before, target_desc: target ? (target.getAttribute('data-testid') || target.className || target.tagName) : null,
              target_scrollTop: target ? target.scrollTop : null, windowY: window.scrollY};
    }""")
    page.wait_for_timeout(900)
    res["scroll_test2"]["topbar_top_after"] = page.evaluate("""() => {
      const tb = document.querySelector('div.st-key-topbar');
      return tb ? tb.getBoundingClientRect().top : null;
    }""")
    page.screenshot(path=os.path.join(HERE, "after-dashboard-scrolled.png"))

    # cek ulang hover popover setelah swap urutan aturan
    page.locator('[data-testid="stButtonGroup"] button', has_text="Rincian").first.click()
    page.get_by_text("Pilih aspek", exact=False).first.wait_for(timeout=90000)
    page.wait_for_timeout(2000)
    page.locator('[data-testid="stSelectbox"] [data-baseweb="select"]').first.scroll_into_view_if_needed()
    page.wait_for_timeout(500)
    page.locator('[data-testid="stSelectbox"] [data-baseweb="select"]').first.click()
    page.wait_for_timeout(1500)
    res["selected_resting"] = page.evaluate("""() => {
      const li = document.querySelector('[data-baseweb="popover"] li[role="option"][aria-selected="true"]');
      if (!li) return null;
      const inner = li.querySelector(':scope > div');
      return {text: li.textContent.trim().slice(0, 40),
              inner_bg: inner ? getComputedStyle(inner).backgroundColor : null};
    }""")
    items = page.locator('[data-baseweb="popover"] li[role="option"]')
    idx = None
    for i in range(items.count()):
        items.nth(i).hover()
        page.wait_for_timeout(300)
        break
    res["hover_after_swap"] = page.evaluate("""() => {
      const li = document.querySelector('[data-baseweb="popover"] li[role="option"]:hover')
              || document.querySelectorAll('[data-baseweb="popover"] li[role="option"]')[0];
      const inner = li.querySelector(':scope > div');
      return {text: li.textContent.trim().slice(0, 40),
              ariaSelected_now: li.getAttribute('aria-selected'),
              inner_bg: inner ? getComputedStyle(inner).backgroundColor : null};
    }""")
    page.screenshot(path=os.path.join(HERE, "after-popover-hover-swap.png"))
    ctx.close()
    b.close()
out = os.path.join(HERE, "scroll_find.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
print("JSON ->", out)
