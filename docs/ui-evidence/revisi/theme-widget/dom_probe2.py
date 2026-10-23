"""Dom probe 2 - struktur uploader + alert + radio circle + select control border (BEFORE)."""
import json
from playwright.sync_api import sync_playwright

URL = "http://localhost:8531"
OUT = r"C:\Users\geova\Downloads\BOOTCAMP\PROJECTS\ulasrasa\docs\ui-evidence\revisi\theme-widget\dom_before2.json"

def dump(page, sel, limit=90):
    return page.evaluate("""([sel, limit]) => {
      const root = document.querySelector(sel);
      if (!root) return {error: 'not found ' + sel};
      const self = {tag: root.tagName, testid: root.getAttribute('data-testid')||'', cls: (typeof root.className==='string'?root.className:'').slice(0,100),
        font: getComputedStyle(root).fontFamily, bg: getComputedStyle(root).backgroundColor, radius: getComputedStyle(root).borderRadius};
      const kids = Array.from(root.querySelectorAll('*')).slice(0, limit).map(el => {
        const cs = getComputedStyle(el);
        let cls=''; try{ cls = (typeof el.className==='string')? el.className:'';}catch(e){}
        return {tag: el.tagName, testid: el.getAttribute('data-testid')||'', baseweb: el.getAttribute('data-baseweb')||'',
          kind: el.getAttribute('kind')||'', cls: cls.slice(0,90), font: cs.fontFamily, bg: cs.backgroundColor,
          color: cs.color, radius: cs.borderRadius, border: cs.borderTopWidth+' '+cs.borderTopStyle+' '+cs.borderTopColor,
          shadow: cs.boxShadow, text: el.textContent.trim().slice(0,44)};
      });
      return {self, kids};
    }""", [sel, limit])

def main():
    res = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.goto(URL, wait_until="domcontentloaded")
        page.get_by_text("Halo,", exact=False).first.wait_for(timeout=120000)
        page.wait_for_timeout(2500)
        # select control chain: border of each div in [data-baseweb=select]
        res["select_chain"] = page.evaluate("""() => {
          const root = document.querySelector('[data-testid="stSelectbox"] [data-baseweb="select"]');
          if (!root) return {error:'no select'};
          const chain = [root, ...Array.from(root.querySelectorAll('div')).slice(0,6)];
          return chain.map(el => { const cs = getComputedStyle(el);
            return {cls:(typeof el.className==='string'?el.className:'').slice(0,80), bg: cs.backgroundColor, radius: cs.borderRadius,
              border: cs.borderTopWidth+' '+cs.borderTopStyle+' '+cs.borderTopColor, shadow: cs.boxShadow}; });
        }""")
        # panel
        page.locator('button', has_text="Ganti Data").first.click()
        page.wait_for_timeout(2500)
        # radio: detailed circle chain per label
        res["radio_labels"] = page.evaluate("""() => {
          return Array.from(document.querySelectorAll('[data-testid="stRadio"] label')).map(lab => {
            const input = lab.querySelector('input');
            const divs = Array.from(lab.querySelectorAll('div')).slice(0,3).map(dv => { const cs = getComputedStyle(dv);
              return {bg: cs.backgroundColor, border: cs.borderTopWidth+' '+cs.borderTopStyle+' '+cs.borderTopColor, radius: cs.borderRadius, w: cs.width, h: cs.height}; });
            return {checked: input ? input.checked : null, text: lab.textContent.trim().slice(0,30), divs};
          });
        }""")
        # switch to upload mode
        page.locator('[data-testid="stRadio"] label', has_text="Upload Dataset").first.click()
        page.wait_for_timeout(2500)
        res["uploader"] = dump(page, '[data-testid="stFileUploader"]')
        res["alert"] = dump(page, '[data-testid="stAlert"]')
        res["expander_root"] = dump(page, '[data-testid="stExpander"]', 12)
        # primary button bg
        page.locator('[data-testid="stExpander"] summary').first.click()
        page.wait_for_timeout(1200)
        res["primary_btn"] = page.evaluate("""() => {
          const btn = document.querySelector('[data-testid="stExpander"] button');
          if (!btn) return {error:'no btn in expander'};
          const cs = getComputedStyle(btn);
          return {testid: btn.getAttribute('data-testid'), kind: btn.getAttribute('kind'), bg: cs.backgroundColor, bgImage: cs.backgroundImage, color: cs.color, font: cs.fontFamily, radius: cs.borderRadius, text: btn.textContent.trim().slice(0,40)};
        }""")
        # textarea / textinput container chain borders
        res["input_chains"] = page.evaluate("""() => {
          const grab = (sel) => { const r = document.querySelector(sel); if (!r) return {error: sel};
            const els = [r, ...Array.from(r.querySelectorAll('div')).slice(0,5)];
            return els.map(el => { const cs = getComputedStyle(el);
              return {testid: el.getAttribute('data-testid')||'', baseweb: el.getAttribute('data-baseweb')||'', bg: cs.backgroundColor, radius: cs.borderRadius, border: cs.borderTopWidth+' '+cs.borderTopStyle+' '+cs.borderTopColor, shadow: cs.boxShadow}; }); };
          return {textarea: grab('[data-testid="stTextArea"]'), textinput: grab('[data-testid="stTextInput"]')};
        }""")
        b.close()
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: (v if not isinstance(v, dict) or 'kids' not in v else {'self': v['self'], 'nkids': len(v['kids'])}) for k, v in res.items()}, ensure_ascii=False)[:3000])
    print("JSON ->", OUT)

if __name__ == "__main__":
    main()
