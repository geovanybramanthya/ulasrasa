"""Dom probe BEFORE - petakan struktur DOM widget Streamlit 1.57 UlasRasa."""
import json, sys
from playwright.sync_api import sync_playwright

URL = "http://localhost:8531"

DUMP_JS = r"""(rootSel) => {
  const root = rootSel ? document.querySelector(rootSel) : document.body;
  if (!root) return {error: 'root not found: ' + rootSel};
  const out = [];
  const els = root.querySelectorAll('*');
  for (const el of els) {
    const cs = getComputedStyle(el);
    let cls = '';
    try { cls = (typeof el.className === 'string') ? el.className : ''; } catch(e) {}
    out.push({
      tag: el.tagName,
      testid: el.getAttribute('data-testid') || '',
      baseweb: el.getAttribute('data-baseweb') || '',
      role: el.getAttribute('role') || '',
      ariaSelected: el.getAttribute('aria-selected') || '',
      cls: cls.slice(0, 120),
      font: cs.fontFamily,
      bg: cs.backgroundColor,
      color: cs.color,
      radius: cs.borderRadius,
      borderColor: cs.borderTopColor,
      text: (el.childNodes.length && [...el.childNodes].some(n=>n.nodeType===3 && n.textContent.trim())) ? el.textContent.trim().slice(0,50) : ''
    });
    if (out.length > 400) break;
  }
  return out;
}"""

def main():
    res = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.goto(URL, wait_until="domcontentloaded")
        page.get_by_text("Halo,", exact=False).first.wait_for(timeout=120000)
        page.wait_for_timeout(2500)

        # --- selectbox resto tertutup ---
        res["select_closed"] = page.evaluate(DUMP_JS, '[data-testid="stSelectbox"]')

        # --- buka popover selectbox resto ---
        page.locator('[data-testid="stSelectbox"] [data-baseweb="select"]').first.click()
        page.wait_for_timeout(1500)
        res["popover_present"] = page.evaluate("() => !!document.querySelector('[data-baseweb=\"popover\"]')")
        res["popover_dump"] = page.evaluate(DUMP_JS, '[data-baseweb="popover"]')
        res["menu_items"] = page.evaluate(r"""() => {
          return Array.from(document.querySelectorAll('[data-baseweb="menu"] li, [role="option"], [data-baseweb="popover"] li')).map(el => {
            const cs = getComputedStyle(el);
            return {tag: el.tagName, role: el.getAttribute('role'), ariaSelected: el.getAttribute('aria-selected'),
                    font: cs.fontFamily, bg: cs.backgroundColor, color: cs.color,
                    padding: cs.padding, text: el.textContent.trim().slice(0,50),
                    cls: (typeof el.className==='string'? el.className:'').slice(0,100)};
          });
        }""")
        # screenshot popover open
        page.screenshot(path=r"C:\Users\geova\Downloads\BOOTCAMP\PROJECTS\ulasrasa\docs\ui-evidence\revisi\theme-widget\before-popover-open.png")
        page.keyboard.press("Escape")
        page.wait_for_timeout(800)

        # --- buka panel Ganti Data ---
        page.locator('button', has_text="Ganti Data").first.click()
        page.wait_for_timeout(2500)
        res["panel_dump"] = page.evaluate(DUMP_JS, '.st-key-paneldata')
        # radio structure
        res["radio_dump"] = page.evaluate(r"""() => {
          const root = document.querySelector('[data-testid="stRadio"]');
          if (!root) return {error: 'no radio'};
          return Array.from(root.querySelectorAll('*')).slice(0, 60).map(el => {
            const cs = getComputedStyle(el);
            let cls=''; try{ cls = (typeof el.className==='string')? el.className:'';}catch(e){}
            return {tag: el.tagName, testid: el.getAttribute('data-testid')||'', baseweb: el.getAttribute('data-baseweb')||'',
              cls: cls.slice(0,120), font: cs.fontFamily, bg: cs.backgroundColor, color: cs.color,
              borderColor: cs.borderTopColor, text: el.textContent.trim().slice(0,40)};
          });
        }""")
        # expander tertutup dulu, lalu buka
        page.locator('[data-testid="stExpander"] summary, [data-testid="stExpander"] [data-testid="stExpanderHeader"]').first.click()
        page.wait_for_timeout(1500)
        res["expander_dump"] = page.evaluate(r"""() => {
          const root = document.querySelector('[data-testid="stExpander"]');
          if (!root) return {error: 'no expander'};
          return Array.from(root.querySelectorAll('*')).slice(0, 80).map(el => {
            const cs = getComputedStyle(el);
            let cls=''; try{ cls = (typeof el.className==='string')? el.className:'';}catch(e){}
            return {tag: el.tagName, testid: el.getAttribute('data-testid')||'',
              cls: cls.slice(0,120), font: cs.fontFamily, text: el.textContent.trim().slice(0,40)};
          });
        }""")
        page.screenshot(path=r"C:\Users\geova\Downloads\BOOTCAMP\PROJECTS\ulasrasa\docs\ui-evidence\revisi\theme-widget\before-panel-expander-open.png")

        # --- mode unggah: klik radio unggah ---
        try:
            page.locator('[data-testid="stRadio"] label', has_text="Unggah").first.click()
            page.wait_for_timeout(2000)
            res["uploader_dump"] = page.evaluate(r"""() => {
              const root = document.querySelector('[data-testid="stFileUploader"]');
              if (!root) return {error: 'no uploader'};
              return Array.from(root.querySelectorAll('*')).slice(0, 80).map(el => {
                const cs = getComputedStyle(el);
                let cls=''; try{ cls = (typeof el.className==='string')? el.className:'';}catch(e){}
                return {tag: el.tagName, testid: el.getAttribute('data-testid')||'', baseweb: el.getAttribute('data-baseweb')||'',
                  cls: cls.slice(0,120), font: cs.fontFamily, bg: cs.backgroundColor, text: el.textContent.trim().slice(0,40)};
              });
            }""")
            res["alert_dump"] = page.evaluate(r"""() => {
              const root = document.querySelector('[data-testid="stAlert"]');
              if (!root) return {error: 'no alert'};
              const cs = getComputedStyle(root);
              return {font: cs.fontFamily, bg: cs.backgroundColor, radius: cs.borderRadius, text: root.textContent.trim().slice(0,80),
                      children: Array.from(root.querySelectorAll('*')).slice(0,20).map(el=>{const c=getComputedStyle(el); return {tag: el.tagName, testid: el.getAttribute('data-testid')||'', font: c.fontFamily, text: el.textContent.trim().slice(0,40)};})};
            }""")
            page.screenshot(path=r"C:\Users\geova\Downloads\BOOTCAMP\PROJECTS\ulasrasa\docs\ui-evidence\revisi\theme-widget\before-panel-upload-mode.png")
        except Exception as ex:
            res["upload_mode_error"] = f"{type(ex).__name__}: {ex}"
        b.close()
    out = r"C:\Users\geova\Downloads\BOOTCAMP\PROJECTS\ulasrasa\docs\ui-evidence\revisi\theme-widget\dom_before.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print("popover_present:", res.get("popover_present"))
    print("menu_items:", json.dumps(res.get("menu_items"), ensure_ascii=False)[:1500])
    print("radio sample:", json.dumps(res.get("radio_dump"), ensure_ascii=False)[:1200])
    print("alert:", json.dumps(res.get("alert_dump"), ensure_ascii=False)[:800])
    print("JSON ->", out)

if __name__ == "__main__":
    main()
